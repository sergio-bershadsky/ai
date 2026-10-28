"""Frame compositor: spec + timing + captures → MP4. PIL draws every frame, ffmpeg encodes.

Cuts sit in the silence between narration lines; every shot fades out to the background and the
next fades in, so two shots are never on screen together. Captions are clipped to their own shot.
"""

from __future__ import annotations

import glob
import json
import multiprocessing as mp
import os
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import pv_spec as S

FADE_IN, FADE_OUT = .30, .22
THEMES = {
    "dark": {"bg": "#11151c", "panel": "#181e27", "ink": "#e5e9f0", "muted": "#98a2b3", "line": "#2a3240",
             "accent": "#7d9cff", "ok": "#5fd39a", "code_bg": "#0b0e13", "caption_bg": "#090c11"},
    "light": {"bg": "#f5f6f8", "panel": "#ffffff", "ink": "#1b2230", "muted": "#5d6676", "line": "#dde1e8",
              "accent": "#2f5bd3", "ok": "#1d7a4d", "code_bg": "#1b2230", "caption_bg": "#ffffff"},
}
FONT_DIRS = ["~/Library/Fonts", "/Library/Fonts", "/System/Library/Fonts", "/usr/share/fonts", "/usr/local/share/fonts",
             "~/.local/share/fonts", "~/.fonts", "C:/Windows/Fonts"]
WEIGHTS = {400: ("Regular", "400", "Text"), 500: ("Medium", "500"), 600: ("SemiBold", "Semibold", "600"), 700: ("Bold", "700")}


# ---------------------------------------------------------------- small helpers
def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def rgba(c: str, a: float = 1.0) -> tuple:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (int(255 * max(0.0, min(1.0, a))),)


@lru_cache(maxsize=None)
def font_file(family: str, weight: int) -> str:
    if Path(family).expanduser().is_file():
        return str(Path(family).expanduser())
    compact = family.replace(" ", "")
    names = {f"{compact}-{w}" for w in WEIGHTS[weight]}
    for d in FONT_DIRS:
        root = Path(d).expanduser()
        if root.exists():
            for f in root.rglob(f"{compact}-*"):
                if f.suffix.lower() in (".ttf", ".otf") and f.stem in names:
                    return str(f)
    raise FileNotFoundError(f"font {family} {weight} not found; install it (macOS: brew install --cask "
                            f"font-{family.lower().replace(' ', '-')}) or set theme.fonts to a .ttf path")


def fade_alpha(img: Image.Image, a: float) -> Image.Image:
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * max(0.0, a)))); return img


def put(dst: Image.Image, src: Image.Image, x: float, y: float, a: float = 1.0) -> None:
    """alpha_composite with clipping to the frame."""
    if a <= 0: return
    x, y = int(round(x)), int(round(y))
    l, t = max(0, -x), max(0, -y)
    r, b = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if r <= l or b <= t: return
    dst.alpha_composite(fade_alpha(src.crop((l, t, r, b)), a), (x + l, y + t))


def rounded(img: Image.Image, r: int) -> Image.Image:
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    out = img.convert("RGBA"); out.putalpha(Image.composite(out.getchannel("A"), m, m)); return out


def shadow(w: int, h: int, r: int = 26, blur: int = 36, off: int = 18, alpha: float = .55) -> tuple[Image.Image, int]:
    pad = blur * 2
    sh = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + off, pad + w, pad + h + off), r, fill=(0, 0, 0, int(255 * alpha)))
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad


def card(img: Image.Image, line: str, r: int = 26) -> tuple[Image.Image, int]:
    """Image as a rounded card with border and soft shadow; returns (image, padding)."""
    sh, pad = shadow(img.width, img.height, r)
    c = rounded(img, r)
    ImageDraw.Draw(c).rounded_rectangle((0, 0, c.width - 1, c.height - 1), r, outline=rgba(line), width=2)
    sh.alpha_composite(c, (pad, pad))
    return sh, pad


def scale_to(img: Image.Image, w: int | None = None, h: int | None = None) -> Image.Image:
    if w: return img.resize((w, max(1, round(img.height * w / img.width))), Image.Resampling.LANCZOS)
    assert h, "scale_to needs w or h"
    return img.resize((max(1, round(img.width * h / img.height)), h), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------- context
class Ctx:
    def __init__(self, spec: dict, timing: list[dict], platform: str, fmt: str):
        self.spec, self.platform, self.fmt = spec, platform, fmt
        self.W, self.H = S.FORMATS[fmt]
        th = spec.get("theme", {})
        self.c = {**THEMES[th.get("preset", "dark")], **th.get("colors", {})}
        self.fonts = {"sans": "IBM Plex Sans", "mono": "IBM Plex Mono", **th.get("fonts", {})}
        lay = S.layout(platform, fmt)
        bx = lay["box"]
        self.box = (bx[0] * self.W, bx[1] * self.H, bx[2] * self.W, bx[3] * self.H)
        self.cap_y = lay["caption_y"] * self.H
        self.cap_x = (lay["caption_x"][0] * self.W, lay["caption_x"][1] * self.W)
        self.timing = {t["id"]: t for t in timing}
        order = [sc["id"] for sc in spec["scenes"]]
        self.end = timing[-1]["end"] + spec["tail"]
        self.bounds = [0.0] + [min(self.timing[b]["start"] - .1, (self.timing[a]["end"] + self.timing[b]["start"]) / 2)
                               for a, b in zip(order, order[1:])] + [self.end]
        self.bg = self._background()
        self.measure = {}
        mf = spec["_build"] / "captures" / "measure.json"
        if mf.exists():
            self.measure = json.loads(mf.read_text())

    def font(self, size: float, weight: int = 600, mono: bool = False) -> ImageFont.FreeTypeFont:
        return _font(font_file(self.fonts["mono" if mono else "sans"], min(weight, 600) if mono else weight), int(size))

    def _background(self) -> Image.Image:
        bg = Image.new("RGBA", (self.W, self.H), rgba(self.c["bg"]))
        d = ImageDraw.Draw(bg)
        for y in range(40, self.H, 60):
            for x in range(30, self.W, 60):
                d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=rgba(self.c["line"], .9))
        glow = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((-300, -500, self.W + 300, int(self.H * .36)), fill=rgba(self.c["accent"], .10))
        return Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(160)))

    def image(self, ref: str) -> Image.Image:
        return Image.open(S.resolve(self.spec, ref)).convert("RGBA")

    def number(self, v) -> float:
        """A number, or {"measure": "capture.key", "scale": 2, "offset": -60} from capture measurements."""
        if isinstance(v, dict):
            return self.measure[v["measure"]] * v.get("scale", 1) + v.get("offset", 0)
        return float(v)


@lru_cache(maxsize=None)
def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_tile(s: str, f: ImageFont.FreeTypeFont, color: tuple) -> tuple[Image.Image, int, int]:
    l, t, r, b = (int(v) for v in f.getbbox(s))
    tile = Image.new("RGBA", (max(1, r - l + 4), max(1, b - t + 4)), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((2 - l, 2 - t), s, font=f, fill=color)
    return tile, l - 2, t - 2


def draw_text(img, x, y, s, f, color, a=1.0):
    if a <= 0 or not s: return
    tile, dx, dy = text_tile(s, f, color)
    put(img, tile, x + dx, y + dy, a)


def wrap(s: str, f: ImageFont.FreeTypeFont, maxw: float) -> list[str]:
    lines, cur = [], ""
    for w in s.split():
        nxt = f"{cur} {w}".strip()
        if cur and f.getlength(nxt) > maxw:
            lines.append(cur); cur = w
        else:
            cur = nxt
    return lines + ([cur] if cur else [])


def fit(ctx: Ctx, s: str, maxw: float, max_lines: int, big: float, small: float, weight=600, mono=False):
    """Largest font size in [small, big] that wraps `s` into ≤ max_lines lines within maxw."""
    size = big
    while True:
        f = ctx.font(size, weight, mono)
        lines = wrap(s, f, maxw)
        if (len(lines) <= max_lines and all(f.getlength(l) <= maxw for l in lines)) or size <= small:
            return f, lines
        size = max(small, size * .92)


# ---------------------------------------------------------------- scenes
class Scene:
    def __init__(self, ctx: Ctx, sc: dict, b0: float, b1: float):
        self.ctx, self.sc, self.b0, self.b1 = ctx, sc, b0, b1
        self.tm = ctx.timing[sc["id"]]
        self.x0, self.y0, self.x1, self.y1 = ctx.box
        self.w = self.x1 - self.x0
        self.prepare()

    def at(self, ref, default: float | None = None) -> float:
        """Absolute time of a word in this scene's line ('word', 'word#2'), or seconds after the scene starts."""
        if ref is None:
            return self.b0 + (default or 0)
        if isinstance(ref, (int, float)):
            return self.tm["start"] + ref
        return self.tm["words"][S.find_word(self.sc["say"], ref)][1]

    def heading(self, y: float) -> float:
        """Lay out kicker / title / sub from y; returns the bottom."""
        c, sc, self.head = self.ctx.c, self.sc, []
        if sc.get("kicker"):
            f, lines = fit(self.ctx, sc["kicker"].upper(), self.w, 1, 30, 22, 500, mono=True)
            self.head.append((lines[0], f, c["accent"], y)); y += f.size * 1.65
        if sc.get("title"):
            f, lines = fit(self.ctx, sc["title"], self.w, 2, 76, 52)
            for ln in lines:
                self.head.append((ln, f, c["ink"], y)); y += f.size * 1.18
            y += 12
        if sc.get("sub"):
            f, lines = fit(self.ctx, sc["sub"], self.w, 2, 40, 30, 400)
            for ln in lines:
                self.head.append((ln, f, c["muted"], y)); y += f.size * 1.3
        return y

    def draw_heading(self, img, lt):
        a = ease_out(lt / .35)
        for s, f, col, y in self.head:
            draw_text(img, self.x0, y + (1 - a) * 24, s, f, rgba(col), a)

    def media_box(self, top: float) -> tuple[float, float, float, float]:
        return self.x0, top + 40, self.x1, self.y1

    def prepare(self): ...
    def draw(self, img, lt, d, t): ...


class Reveal(Scene):
    """Lead line, items that pop in on their words, then a punch line (hook)."""
    def prepare(self):
        c, sc = self.ctx.c, self.sc
        self.lead_f, self.lead = fit(self.ctx, sc.get("lead", ""), self.w, 2, 60, 40, 500)
        self.punch_f, self.punch = fit(self.ctx, sc["punch"]["text"], self.w, 3, 132, 72) if sc.get("punch") else (self.ctx.font(132), [])
        items = [it["text"] for it in sc.get("items", [])]
        avail = (self.y1 - self.y0) - len(self.lead) * self.lead_f.size * 1.3 - 60 \
            - (len(self.punch) * self.punch_f.size * 1.12 + 70 if self.punch else 0)
        size = min(110, avail / max(1, len(items)) / 1.18)
        while items and size > 40 and max(self.ctx.font(size).getlength(s) for s in items) > self.w:
            size *= .94
        self.item_f = self.ctx.font(size)

    def draw(self, img, lt, d, t):
        c, sc = self.ctx.c, self.sc
        y = self.y0
        a0 = ease_out(lt / .4)
        for ln in self.lead:
            draw_text(img, self.x0, y - (1 - a0) * 20, ln, self.lead_f, rgba(c["muted"]), a0); y += self.lead_f.size * 1.3
        y += 40
        tp = self.at(sc["punch"].get("at")) if sc.get("punch") else 1e9
        dim = 1 - .7 * ease_out((t - tp) / .4)
        for it in sc.get("items", []):
            a = ease_out((t - self.at(it.get("at")) + .05) / .3)
            draw_text(img, self.x0, y + (1 - a) * 40, it["text"], self.item_f, rgba(c["ink"]), a * dim)
            y += self.item_f.size * 1.18
        if self.punch:
            a = ease_out((t - tp + .05) / .35)
            y += 50
            for ln in self.punch:
                draw_text(img, self.x0, y + (1 - a) * 30, ln, self.punch_f, rgba(c["accent"]), a)
                y += self.punch_f.size * 1.12


class Title(Scene):
    """Big name, optional sub, code block, footer lines and an image (intro / call to action)."""
    def prepare(self):
        c, sc, ctx = self.ctx.c, self.sc, self.ctx
        y, self.parts = self.y0, []
        if sc.get("kicker"):
            f, ln = fit(ctx, sc["kicker"].upper(), self.w, 1, 32, 22, 500, mono=True)
            self.parts.append(("text", ln[0], f, c["accent"], y, None)); y += f.size * 1.6
        lines = sc.get("lines", [])
        size = min([150] + [150 * self.w / max(1, ctx.font(150).getlength(s)) for s in lines])
        f = ctx.font(max(56, size))
        for s in lines:
            self.parts.append(("text", s, f, c["ink"], y, None)); y += f.size * 1.08
        if sc.get("sub"):
            f, ln = fit(ctx, sc["sub"], self.w, 2, 44, 32, 400)
            y += 18
            for s in ln:
                self.parts.append(("text", s, f, c["muted"], y, None)); y += f.size * 1.3
        if sc.get("code"):
            y += 50
            code = sc["code"]["lines"]
            f = ctx.font(28, 500, mono=True)
            while f.size > 16 and max(f.getlength("$ " + s) for s in code) > self.w - 70:
                f = ctx.font(f.size - 1, 500, mono=True)
            h = len(code) * f.size * 2.2 + 50
            self.parts.append(("code", code, f, None, y, self.at(sc["code"].get("at")))); y += h + 40
        for i, s in enumerate((sc.get("footer") or {}).get("lines", [])):
            f, ln = fit(ctx, s, self.w, 1, 40 if i == 0 else 36, 22, 500 if i == 0 else 400, mono=i == 0)
            self.parts.append(("text", ln[0], f, c["accent"] if i == 0 else c["muted"], y, self.at(sc["footer"].get("at"))))
            y += f.size * 1.75
        self.media = None
        if sc.get("media"):
            m = sc["media"]
            img = ctx.image(m["image"])
            room_h = ctx.cap_y - 100 - y - 40  # stop above the caption band
            w = min(m.get("width", 700), self.w, img.width * room_h / img.height) if room_h > 100 else 0
            if w > 120:
                im = scale_to(img, w=int(w))
                self.media = (*card(im, c["line"], 30), y + 40, self.at(m.get("at"), .35))

    def draw(self, img, lt, d, t):
        c = self.ctx.c
        base = ease_out(lt / .5)
        for kind, s, f, col, y, t_at in self.parts:
            a = base if t_at is None else ease_out((t - t_at) / .5)
            if kind == "text":
                draw_text(img, self.x0, y + (1 - a) * 30, s, f, rgba(col), a)
            elif a > 0:
                h = len(s) * f.size * 2.2 + 50
                box = Image.new("RGBA", (int(self.w), int(h)), (0, 0, 0, 0))
                bd = ImageDraw.Draw(box)
                bd.rounded_rectangle((0, 0, box.width - 1, box.height - 1), 22, fill=rgba(c["code_bg"]), outline=rgba(c["line"]), width=2)
                for i, ln in enumerate(s):
                    yy = 25 + i * f.size * 2.2 + f.size * .45
                    bd.text((34, yy), "$", font=f, fill=rgba(c["ok"]))
                    bd.text((34 + f.getlength("$ "), yy), ln, font=f, fill=rgba(c["ink"]))
                put(img, box, self.x0, y + (1 - a) * 40, a)
        if self.media:
            im, pad, y, t_at = self.media
            b = ease_out((t - t_at) / .7) if t_at > self.b0 else ease_out((lt - .35) / .7)
            put(img, im, (self.ctx.W - im.width) / 2, y - pad + (1 - b) * 160, b)


class Screen(Scene):
    """A full-frame capture (or a replayed sequence of captures), optionally scrolling, with a tap ripple."""
    def prepare(self):
        sc, ctx = self.sc, self.ctx
        if sc.get("frames"):
            ref = sc["frames"]
            pattern = ctx.spec["_build"] / "captures" / f"{ref[1:]}_*.png" if ref.startswith("@") else ctx.spec["_dir"] / ref
            paths = sorted(glob.glob(str(pattern)))
            if not paths: raise FileNotFoundError(f"scene {sc['id']}: no frames for {ref}")
            self.frames = [Image.open(p).convert("RGBA") for p in paths]
        else:
            self.frames = [ctx.image(sc["image"])]
        self.frames = [f if f.width == ctx.W else scale_to(f, w=ctx.W) for f in self.frames]
        self.k = self.frames[0].width / ctx.W
        scroll = sc.get("scroll", [0, 0])
        self.scroll = [ctx.number(v) for v in scroll]

    def draw(self, img, lt, d, t):
        sc, ctx = self.sc, self.ctx
        k = 0
        if len(self.frames) > 1:
            t0 = self.at((sc.get("sequence") or {}).get("from"), 0) + .15
            t1 = self.b1 - FADE_OUT - .1
            k = 0 if t < t0 else min(len(self.frames) - 1, int((t - t0) / max(.1, t1 - t0) * len(self.frames)))
        fr = self.frames[k]
        y = self.scroll[0] + (self.scroll[1] - self.scroll[0]) * ease(lt / max(d, .1))
        y = max(0, min(fr.height - ctx.H, y))
        img.alpha_composite(fr.crop((0, int(y), ctx.W, int(y) + ctx.H)) if fr.height >= ctx.H else fr, (0, 0))
        tap = sc.get("tap")
        if tap:
            r = (t - self.at(tap.get("at"))) / .7
            if 0 <= r <= 1:
                x, yy = ctx.number(tap["x"]), ctx.number(tap["y"]) - y
                R = 40 + 90 * r
                ImageDraw.Draw(img).ellipse((x - R, yy - R, x + R, yy + R), outline=rgba("#ffffff", .9 * (1 - r)), width=6)


class Spotlight(Scene):
    """Heading plus one capture in a panel; pans across it when it is larger than the panel."""
    def prepare(self):
        sc, ctx = self.sc, self.ctx
        top = self.heading(self.y0)
        x0, y0, x1, y1 = self.media_box(top)
        img = ctx.image(sc["image"])
        fit_ = sc.get("fit", "width")
        img = scale_to(img, h=int(fit_)) if isinstance(fit_, (int, float)) else scale_to(img, w=int(x1 - x0))
        self.src = img
        self.pw, self.ph = int(min(img.width, x1 - x0)), int(min(img.height, y1 - y0))
        self.px = x0 + ((x1 - x0) - self.pw) / 2
        self.py = y0 + max(0, ((y1 - y0) - self.ph) / 2.5)
        self.sh, self.pad = shadow(self.pw, self.ph)
        self.pan = sc.get("pan", [0, 1])

    def draw(self, img, lt, d, t):
        self.draw_heading(img, lt)
        p = self.pan[0] + (self.pan[1] - self.pan[0]) * ease(lt / max(d, .1))
        sx, sy = p * (self.src.width - self.pw), p * (self.src.height - self.ph)
        crop = self.src.crop((int(sx), int(sy), int(sx) + self.pw, int(sy) + self.ph))
        a = ease_out((lt - .1) / .4)
        put(img, self.sh, self.px - self.pad, self.py - self.pad + (1 - a) * 40, a)
        c = rounded(crop, 26)
        ImageDraw.Draw(c).rounded_rectangle((0, 0, c.width - 1, c.height - 1), 26, outline=rgba(self.ctx.c["line"]), width=2)
        put(img, c, self.px, self.py + (1 - a) * 40, a)


class Cards(Scene):
    """Heading plus captures stacked as cards, sliding in one after another."""
    def prepare(self):
        sc, ctx = self.sc, self.ctx
        x0, y0, x1, y1 = self.media_box(self.heading(self.y0))
        imgs = [scale_to(ctx.image(r), w=int(x1 - x0)) for r in sc["images"]]
        gap = 40
        total = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
        if total > y1 - y0:
            k = (y1 - y0 - gap * (len(imgs) - 1)) / sum(i.height for i in imgs)
            imgs = [scale_to(i, w=int(i.width * k)) for i in imgs]
        self.cards, y = [], y0
        for im in imgs:
            cimg, pad = card(im, ctx.c["line"])
            self.cards.append((cimg, pad, x0 + ((x1 - x0) - im.width) / 2, y)); y += im.height + gap

    def draw(self, img, lt, d, t):
        self.draw_heading(img, lt)
        for i, (cimg, pad, x, y) in enumerate(self.cards):
            a = ease_out((lt - .15 - i * self.sc.get("stagger", .35)) / .45)
            put(img, cimg, x - pad + (1 - a) * 120, y - pad, a)


class Mapping(Scene):
    """Rows 'TOOL  “their word” → neutral', then an optional image (bring-your-own-X)."""
    def prepare(self):
        sc, ctx, c = self.sc, self.ctx, self.ctx.c
        top = self.heading(self.y0) + 40
        rows = sc.get("rows", [])
        self.rh = min(108, (self.y1 - top) / max(1, len(rows)) - 24)
        self.rows, y = [], top
        for r in rows:
            tile = Image.new("RGBA", (int(self.w), int(self.rh)), (0, 0, 0, 0))
            d = ImageDraw.Draw(tile)
            d.rounded_rectangle((0, 0, tile.width - 1, tile.height - 1), 20, fill=rgba(c["panel"]), outline=rgba(c["line"]), width=2)
            s = self.rh / 108
            d.text((30, 16 * s), r.get("tag", "").upper(), font=ctx.font(24 * s, 500, mono=True), fill=rgba(c["muted"]))
            lf, _ = fit(ctx, f"“{r['left']}”", self.w * .55, 1, 38 * s, 22, 500)
            d.text((30, 48 * s), f"“{r['left']}”", font=lf, fill=rgba(c["ink"]))
            d.text((self.w * .64, self.rh / 2), "→", font=ctx.font(44 * s), fill=rgba(c["muted"]), anchor="mm")
            pf = ctx.font(32 * s, 500, mono=True)
            tw = pf.getlength(r["right"])
            d.rounded_rectangle((self.w - 25 - tw - 36, self.rh / 2 - 25 * s, self.w - 25, self.rh / 2 + 25 * s), 14, fill=rgba(c["accent"], .18))
            d.text((self.w - 25 - 18, self.rh / 2), r["right"], font=pf, fill=rgba(c["accent"]), anchor="rm")
            self.rows.append((tile, y)); y += self.rh + 24
        self.media = None
        m = sc.get("media")
        room = ctx.cap_y - 100 - y - 20  # stop above the caption band
        if m and room > 360:  # a thumbnail smaller than this reads as noise
            im = ctx.image(m["image"])
            w = min(m.get("width", 560), self.w, im.width * room / im.height)
            cimg, pad = card(scale_to(im, w=int(w)), c["line"], 22)
            self.media = (cimg, pad, (ctx.W - cimg.width) / 2, y + 10, self.at(m.get("at"), .35))

    def draw(self, img, lt, d, t):
        self.draw_heading(img, lt)
        for i, (tile, y) in enumerate(self.rows):
            a = ease_out((lt - .4 - i * .45) / .4)
            put(img, tile, self.x0, y + (1 - a) * 30, a)
        if self.media:
            cimg, pad, x, y, t_at = self.media
            b = ease_out((t - t_at + .1) / .6)
            put(img, cimg, x, y - pad + (1 - b) * 80, b)


KINDS = {"reveal": Reveal, "title": Title, "screen": Screen, "spotlight": Spotlight, "cards": Cards, "mapping": Mapping}


# ---------------------------------------------------------------- captions
class Captions:
    def __init__(self, ctx: Ctx):
        self.ctx, self.f = ctx, ctx.font(54)
        self.maxw = ctx.cap_x[1] - ctx.cap_x[0] - 68
        self.chunks = []
        for i, sc in enumerate(ctx.spec["scenes"]):
            if not sc["captions"]: continue
            shot_end = ctx.bounds[i + 1] - FADE_OUT
            cur = []
            for w in ctx.timing[sc["id"]]["words"]:
                trial = cur + [w]
                if cur and self.f.getlength(" ".join(x[0] for x in trial)) > self.maxw:
                    self.chunks.append((cur, shot_end)); cur = [w]
                else:
                    cur = trial
                if w[0][-1] in ".,:;!?…" and len(cur) >= 2:
                    self.chunks.append((cur, shot_end)); cur = []
            if cur: self.chunks.append((cur, shot_end))
        out = []
        for i, (ws, shot_end) in enumerate(self.chunks):
            nxt = self.chunks[i + 1][0][0][1] if i + 1 < len(self.chunks) else ws[-1][2] + .5
            out.append((max(0.0, ws[0][1] - .05), min(nxt, ws[-1][2] + .6, shot_end), ws))
        self.chunks = out

    def draw(self, img, t):
        cur = next((c for c in self.chunks if c[0] <= t < c[1]), None)
        if not cur: return
        ctx, f = self.ctx, self.f
        words = cur[2]
        sp = f.getlength(" ")
        widths = [f.getlength(w[0]) for w in words]
        total = sum(widths) + sp * (len(words) - 1)
        cx = (ctx.cap_x[0] + ctx.cap_x[1]) / 2
        x0, y = cx - total / 2, ctx.cap_y - 40
        pill = Image.new("RGBA", (int(total + 68), 106), (0, 0, 0, 0))
        ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, 105), 26, fill=rgba(ctx.c["caption_bg"], .88))
        put(img, pill, x0 - 34, y - 22)
        x = x0
        for (w, ws, we), wd in zip(words, widths):
            draw_text(img, x, y, w, f, rgba(ctx.c["accent"] if ws <= t < we + .08 else ctx.c["ink"]))
            x += wd + sp


# ---------------------------------------------------------------- frames and encoding
class Film:
    def __init__(self, spec: dict, timing: list[dict], platform: str, fmt: str):
        self.ctx = ctx = Ctx(spec, timing, platform, fmt)
        self.shots = [KINDS[sc["type"]](ctx, sc, ctx.bounds[i], ctx.bounds[i + 1]) for i, sc in enumerate(spec["scenes"])]
        self.captions = Captions(ctx)
        self.bg_rgb = ctx.bg.convert("RGB")
        self.timing = timing

    def frame(self, t: float) -> Image.Image:
        ctx = self.ctx
        i = max(j for j in range(len(self.shots)) if ctx.bounds[j] <= t)
        shot = self.shots[i]
        lt, d = t - shot.b0, shot.b1 - shot.b0
        img = ctx.bg.copy()
        shot.draw(img, lt, d, t)
        self.captions.draw(img, t)
        vis = min(1.0 if i == 0 else ease_out(lt / FADE_IN),
                  1.0 if i == len(self.shots) - 1 else 1 - ease((lt - (d - FADE_OUT)) / FADE_OUT),
                  1 - max(0.0, (t - (ctx.end - .5)) / .5))
        rgb = img.convert("RGB")
        return rgb if vis >= 1 else Image.blend(self.bg_rgb, rgb, vis)

    def cut_check(self) -> list[float]:
        """Mean |frame − background| at every cut: 0 means no two shots overlap."""
        import numpy as np
        bg = np.asarray(self.bg_rgb, np.float32)
        return [float(np.abs(np.asarray(self.frame(b - 1e-6), np.float32) - bg).mean()) for b in self.ctx.bounds[1:-1]]

    def sheet(self, times: list[float], path: Path, cols: int = 5, w: int = 270) -> Path:
        h = int(w * self.ctx.H / self.ctx.W)
        rows = (len(times) + cols - 1) // cols
        out = Image.new("RGB", (cols * (w + 8), rows * (h + 8)), "white")
        for k, t in enumerate(times):
            out.paste(self.frame(t).resize((w, h)), ((k % cols) * (w + 8), (k // cols) * (h + 8)))
        out.save(path)
        return path

    def encode(self, vo: Path, out: Path, fps: int = 30, crf: int = 18, workers: int | None = None) -> Path:
        ctx, spec = self.ctx, self.ctx.spec
        W, H, end = ctx.W, ctx.H, ctx.end
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
               "-i", str(vo)]
        music = spec.get("music")
        if music:
            # music loops under the voice and ducks while it speaks (sidechain), fading out at the end
            cmd += ["-stream_loop", "-1", "-i", str(S.resolve(spec, music["file"]))]
            fl = (f"[1:a]apad,asplit=2[v1][v2];[2:a]volume={music.get('volume', .15)},"
                  f"afade=t=out:st={max(0, end - 1.5):.2f}:d=1.5[m];"
                  f"[m][v1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];"
                  f"[v2][md]amix=inputs=2:normalize=0[a]")
        else:
            fl = "[1:a]apad[a]"
        cmd += ["-filter_complex", fl, "-map", "0:v", "-map", "[a]", "-t", f"{end:.3f}", "-c:v", "libx264", "-preset", "medium",
                "-crf", str(crf), "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(out)]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        assert ff.stdin is not None
        n = int(end * fps)
        workers = workers or max(1, min(8, (os.cpu_count() or 2) - 1))
        if workers == 1:
            for k in range(n):
                ff.stdin.write(self.frame(k / fps).tobytes())
        else:
            # frames are independent: draw them in worker processes, write them in order
            args = (ctx.spec["_path"], self.timing, ctx.platform, ctx.fmt)
            with mp.get_context("spawn").Pool(workers, _worker_init, args) as pool:
                for buf in pool.imap(_worker_frame, (k / fps for k in range(n)), chunksize=8):
                    ff.stdin.write(buf)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        return out


_FILM: Film | None = None


def _worker_init(spec_path, timing, platform, fmt):
    global _FILM
    _FILM = Film(S.load(spec_path), timing, platform, fmt)


def _worker_frame(t: float) -> bytes:
    assert _FILM is not None
    return _FILM.frame(t).tobytes()
