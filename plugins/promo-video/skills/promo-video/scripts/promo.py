#!/usr/bin/env python3
"""promo.py — narrated promo videos from real UI captures (Telegram / Instagram, RU / EN).

    promo.py doctor   [SPEC]                   check ffmpeg, Python deps, Chromium, fonts, API key
    promo.py voices   SPEC [--lang ru]         list the account's voices (name, accent, languages)
    promo.py check    SPEC                     validate the spec
    promo.py capture  SPEC [NAME ...]          screenshots / sequences → build/<stem>/captures/
    promo.py voice    SPEC [--models a,b] [--voice NAME]   one take per model → build/<stem>/takes/
    promo.py analyze  SPEC [--pick]            STT error rate + pitch range per take; --pick selects the best
    promo.py pick     SPEC TAKE                use that take (file stem in takes/) as the voice-over
    promo.py stills   SPEC                     contact sheets (scenes + cuts), cut-overlap and reading-time checks
    promo.py render   SPEC [--full] [--force]  one mastered MP4 + cover JPEG per target; redraws only changed chunks
                                               (--full: redraw everything; --force: render despite reading problems)
    promo.py all      SPEC [--models a,b]      capture → voice → analyze/pick → stills → render

Everything lands in <spec dir>/build/<spec stem>/. See references/spec.md for the spec format.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pv_spec as S  # noqa: E402

DEFAULT_MODELS = ["eleven_v4", "eleven_multilingual_v2"]


def doctor(spec: dict | None) -> int:
    ok = True
    def row(good: bool, what: str, fix: str = ""):
        nonlocal ok
        ok &= good
        print(f"{'ok ' if good else 'MISSING'}  {what}" + (f"  → {fix}" if not good and fix else ""))
    row(bool(shutil.which("ffmpeg")), "ffmpeg", "brew install ffmpeg / apt install ffmpeg")
    if shutil.which("ffmpeg"):
        enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        row("libx264" in enc, "ffmpeg libx264 encoder")
    for mod, pip in [("PIL", "pillow"), ("numpy", "numpy"), ("playwright", "playwright")]:
        row(importlib.util.find_spec(mod) is not None, f"python: {mod}", f"pip install {pip}")
    if importlib.util.find_spec("playwright"):
        try:
            from playwright.sync_api import sync_playwright
            import pv_capture
            with sync_playwright() as p:
                pv_capture._chromium(p).close()
            row(True, "Chromium for Playwright")
        except Exception as e:
            row(False, "Chromium for Playwright", f"python3 -m playwright install chromium ({e.__class__.__name__})")
    try:
        import pv_render
        th = (spec or {}).get("theme", {}).get("fonts", {})
        for fam, w in [(th.get("sans", "IBM Plex Sans"), 400), (th.get("sans", "IBM Plex Sans"), 600), (th.get("mono", "IBM Plex Mono"), 500)]:
            path = pv_render.font_file(fam, w)
            cyr = _has_cyrillic(path)
            row(cyr is not False, f"font {fam} {w}" + (" (Cyrillic ok)" if cyr else ""), "font has no Cyrillic glyphs")
    except FileNotFoundError as e:
        row(False, "fonts", str(e))
    if spec:
        import pv_voice
        try:
            pv_voice.api_key(spec); row(True, "ElevenLabs key (value not shown)")
        except Exception as e:
            row(False, "ElevenLabs key", str(e))
    return 0 if ok else 1


def _has_cyrillic(path: str):
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return None
    cmap = TTFont(path, lazy=True).getBestCmap()
    return all(c in cmap for c in range(0x410, 0x450))


def need(spec: dict) -> dict:
    problems = S.validate(spec)
    if problems:
        sys.exit("spec problems:\n- " + "\n- ".join(problems))
    return spec


def timing(spec: dict) -> list[dict]:
    p = spec["_build"] / "timing.json"
    if not p.exists():
        sys.exit("no voice-over yet: run `promo.py voice SPEC` then `promo.py analyze SPEC --pick`")
    return json.loads(p.read_text())["scenes"]


def reading(spec: dict) -> list[str]:
    problems = S.reading_problems(spec, timing(spec))
    for p in problems:
        print(f"reading: {p}")
    return problems


def stills(spec: dict) -> None:
    import pv_render
    reading(spec)
    for t in spec["targets"]:
        film = pv_render.Film(spec, timing(spec), t["platform"], t["format"])
        tag = f"{t['platform']}-{t['format'].replace(':', 'x')}"
        b = film.ctx.bounds
        mids = [(b[i] + b[i + 1]) / 2 + .4 for i in range(len(b) - 1)]
        film.sheet(mids, spec["_build"] / f"scenes-{tag}.png")
        cuts = [c + dt for c in b[1:-1] for dt in (-.25, -.1, 0, .12, .3)]
        film.sheet(cuts, spec["_build"] / f"cuts-{tag}.png", cols=5, w=180)
        worst = max(film.cut_check(), default=0)
        print(f"{tag}: scenes-{tag}.png, cuts-{tag}.png; max |frame−background| at cuts = {worst:.2f} (0 = clean)")


def render(spec: dict, full: bool = False, force: bool = False) -> list[Path]:
    import pv_master
    import pv_render
    if reading(spec) and not force:
        sys.exit("on-screen text above is not up long enough to read: shorten it, move its word earlier, "
                 "or raise `tail`; --force renders anyway")
    outs = []
    for t in spec["targets"]:
        film = pv_render.Film(spec, timing(spec), t["platform"], t["format"])
        out = spec["_build"] / f"{spec['_path'].stem}-{t['platform']}-{t['format'].replace(':', 'x')}.mp4"
        fps = spec.get("fps", 30)
        try:
            film.encode(spec["_build"] / "vo.mp3", out, fps, full=full)
        except pv_render.MasterRejected as e:
            sys.exit(str(e) + "\ndo not post it; fix the mix (music volume, voice take) and render again")
        m = pv_master.measure(out)
        print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB): {m['I']:.1f} LUFS, true peak {m['TP']:.1f} dBTP, "
              f"redrew {len(film.rendered)}/{len(film.chunks(fps))} chunks"
              + (f", cover {out.with_suffix('.cover.jpg').name} from {film.cover_t:.2f}s" if film.cover_t is not None else ""))
        outs.append(out)
    return outs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["doctor", "voices", "check", "capture", "voice", "analyze", "pick", "stills", "render", "all"])
    ap.add_argument("spec", nargs="?")
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--models", default=None, help="comma-separated ElevenLabs model ids")
    ap.add_argument("--pick", action="store_true")
    ap.add_argument("--full", action="store_true", help="render: redraw every chunk, ignore the cache")
    ap.add_argument("--force", action="store_true", help="render: go ahead despite reading-time problems")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--env-file", default=None)
    ap.add_argument("--voice", default=None, help="voice name or id (overrides the spec)")
    a = ap.parse_args(argv)
    spec = S.load(a.spec) if a.spec else None
    if a.cmd == "doctor":
        return doctor(spec)
    if spec is None:
        sys.exit("SPEC is required")
    if a.voice:
        spec["voice"]["voice"] = a.voice
    if a.env_file:
        spec["voice"]["env_file"] = os.path.abspath(a.env_file)
    models = a.models.split(",") if a.models else spec["voice"].get("models") or DEFAULT_MODELS

    if a.cmd == "check":
        problems = S.validate(spec)
        if not problems and (spec["_build"] / "timing.json").exists():
            problems = S.reading_problems(spec, timing(spec))  # needs the voice-over's word timing
        print("ok" if not problems else "problems:\n- " + "\n- ".join(problems))
        return 1 if problems else 0
    if a.cmd == "voices":
        import pv_voice
        for v in pv_voice.list_voices(pv_voice.api_key(spec)):
            lab = v.get("labels", {})
            langs = ",".join(sorted({l.get("language", "") for l in v.get("verified_languages", []) if l.get("language")}))
            if a.lang and a.lang not in langs and lab.get("language") != a.lang:
                continue
            print(f"{v['voice_id']}  {v['name'][:44]:44} {lab.get('gender', ''):7} {lab.get('accent', ''):12} {langs}")
        return 0
    need(spec)
    if a.cmd in ("capture", "all") and spec["captures"]:
        import pv_capture
        pv_capture.capture(spec, a.rest or None)
    if a.cmd in ("voice", "all"):
        import pv_voice
        key = pv_voice.api_key(spec)
        made = [pv_voice.take(spec, m, key).stem for m in models]
        if len(made) == 1 and not (spec["_build"] / "vo.mp3").exists():
            pv_voice.pick(spec, made[0])
    if a.cmd in ("analyze", "all"):
        import pv_voice
        rows = pv_voice.analyze(spec, pv_voice.api_key(spec))
        if a.pick or a.cmd == "all":
            pv_voice.pick(spec, pv_voice.best(rows))
    if a.cmd == "pick":
        import pv_voice
        pv_voice.pick(spec, a.rest[0])
    if a.cmd in ("stills", "all"):
        stills(spec)
    if a.cmd in ("render", "all"):
        render(spec, full=a.full, force=a.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
