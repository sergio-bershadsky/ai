"""Capture real UI with Playwright: screenshots, element shots and replayable sequences."""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path


def _chromium(p):
    """Bundled Chromium if this Playwright has it, else the newest Chromium already in the cache."""
    try:
        return p.chromium.launch()
    except Exception as first:
        cache = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", Path.home() / "Library/Caches/ms-playwright"))
        if not cache.exists():
            cache = Path.home() / ".cache/ms-playwright"
        pats = ["chromium-*/chrome-mac*/*.app/Contents/MacOS/*", "chromium-*/chrome-linux*/chrome", "chromium-*/chrome-win*/chrome.exe"]
        found = sorted((f for pat in pats for f in glob.glob(str(cache / pat))), reverse=True)
        if not found:
            raise RuntimeError("no Chromium for Playwright: run `python3 -m playwright install chromium`") from first
        return p.chromium.launch(executable_path=found[0])


def _url(spec: dict, cap: dict) -> str:
    u = cap["url"]
    return u if "://" in u else (spec["_dir"] / u).resolve().as_uri()


def _step(pg, step: dict) -> None:
    (kind, arg), = step.items()
    if kind == "click": pg.click(arg)
    elif kind == "check": pg.check(arg)
    elif kind == "hover": pg.hover(arg)
    elif kind == "fill": pg.fill(arg[0], arg[1])
    elif kind == "press": pg.keyboard.press(arg)
    elif kind == "scroll": pg.locator(arg).scroll_into_view_if_needed()
    elif kind == "eval": pg.evaluate(arg)
    elif kind == "wait": pg.wait_for_timeout(arg)
    else: raise ValueError(f"unknown capture step {kind!r}")
    pg.wait_for_timeout(120)


def _shot(pg, cap: dict, path: Path) -> None:
    sel = cap.get("selector")
    if sel:
        pg.locator(sel).first.screenshot(path=str(path))
    else:
        pg.screenshot(path=str(path), full_page=cap.get("full_page", False))


def capture(spec: dict, only: list[str] | None = None) -> list[Path]:
    from playwright.sync_api import sync_playwright
    out_dir = spec["_build"] / "captures"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    with sync_playwright() as p:
        browser = _chromium(p)
        for cap in spec["captures"]:
            if only and cap["name"] not in only:
                continue
            w, h = cap.get("viewport", [540, 960])
            pg = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=cap.get("scale", 2),
                                  color_scheme=cap.get("theme", "dark"), locale=cap.get("locale", spec["lang"]))
            pg.goto(_url(spec, cap))
            pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(cap.get("settle_ms", 400))
            for step in cap.get("steps", []):
                _step(pg, step)
            seq = cap.get("sequence")
            if seq:
                # sequence: run `eval` with {i} replaced, for i in 0..count-1 → name_00.png, name_01.png…
                count = seq["count"] if isinstance(seq["count"], int) else int(pg.evaluate(seq["count"]))
                for i in range(count):
                    pg.evaluate(seq["eval"].replace("{i}", str(i)))
                    pg.wait_for_timeout(seq.get("wait_ms", 150))
                    path = out_dir / f"{cap['name']}_{i:02d}.png"
                    _shot(pg, cap, path); written.append(path)
            else:
                path = out_dir / f"{cap['name']}.png"
                _shot(pg, cap, path); written.append(path)
            for name, js in cap.get("measure", {}).items():  # numbers the spec can reference, e.g. a section's y
                spec.setdefault("_measure", {})[f"{cap['name']}.{name}"] = pg.evaluate(js)
            pg.close()
        browser.close()
    if spec.get("_measure"):
        (out_dir / "measure.json").write_text(json.dumps(spec["_measure"], indent=1))
    print(f"captured {len(written)} image(s) → {out_dir}")
    return written
