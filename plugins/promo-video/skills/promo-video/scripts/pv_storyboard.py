"""Validate long-form storyboards against the promo-video mandatory rules.

Usage: python3 pv_storyboard.py <storyboard.json> [...] [--forbid TEXT ...]
Exit 1 when any storyboard breaks a rule. Schema: references/youtube-tutorial.md.
"""
import json, pathlib, re, sys

MODES = {"cover", "full", "pip", "vo", "end"}
MAX_S, MAX_FULL, MAX_WPS = 300.0, 45.0, 2.9


def check(s: dict, forbid: list[str]) -> list[str]:
    errs, beats = [], s.get("beats", [])
    if not beats or beats[0].get("mode") != "cover" or beats[0].get("start") != 0 \
            or abs(beats[0].get("end", 0) - 2.0) > 0.01:
        errs.append("rule 1: beat 0 must be the cover, 0.0–2.0 s")
    if not beats or beats[-1].get("mode") != "end":
        errs.append("rule 2: last beat must be the QR end card (mode 'end')")
    elif not (7.9 <= beats[-1]["end"] - beats[-1]["start"] <= 12.1):
        errs.append("rule 2: end card must last 8–12 s")
    if not s.get("end_card", {}).get("qr_url"):
        errs.append("rule 2: end_card.qr_url missing")
    t = words = full = pip = 0.0
    for b in beats:
        bid, mode = b.get("id"), b.get("mode")
        if mode not in MODES: errs.append(f"{bid}: unknown mode {mode}")
        if abs(b.get("start", -1) - t) > 0.01: errs.append(f"{bid}: starts at {b.get('start')}, expected {t:.1f}")
        d = b.get("end", 0) - b.get("start", 0)
        if mode not in ("cover", "end") and not (3.9 <= d <= 25.1): errs.append(f"{bid}: {d:.1f} s (beats are 4–25 s)")
        w = len(re.findall(r"[\w'’-]+", b.get("line", "")))
        words += w
        if mode == "cover" and w: errs.append("rule 1: no narration under the cover")
        if d > 0 and w / d > MAX_WPS: errs.append(f"{bid}: {w} words in {d:.1f} s is too fast")
        full += d if mode == "full" else 0
        pip += d if mode == "pip" else 0
        for f in forbid:
            if f in json.dumps(b): errs.append(f"{bid}: mentions forbidden '{f}'")
        t = b.get("end", t)
    if t > MAX_S: errs.append(f"rule 7: {t:.1f} s is over 5:00")
    if full > MAX_FULL + 1: errs.append(f"full-frame presenter {full:.0f} s > {MAX_FULL:.0f} s")
    if abs(s.get("duration_s", 0) - t) > 0.5: errs.append(f"duration_s {s.get('duration_s')} != {t:.1f}")
    if s.get("words") != words: errs.append(f"words {s.get('words')} != counted {words:.0f}")
    ps = s.get("presenter_seconds", {})
    if abs(ps.get("full", -1) - full) > 0.5 or abs(ps.get("pip", -1) - pip) > 0.5:
        errs.append(f"presenter_seconds should be full={full:.1f} pip={pip:.1f}")
    if not s.get("article", {}).get("url"): errs.append("rule 7: article.url missing")
    for k in ("title", "youtube_title", "cover", "chapters", "description", "thumbnail"):
        if not s.get(k): errs.append(f"missing {k}")
    if len(s.get("youtube_title", "")) > 70: errs.append("youtube_title > 70 chars")
    return errs


def main(argv: list[str]) -> int:
    forbid, paths, i = [], [], 0
    while i < len(argv):
        if argv[i] == "--forbid": forbid.append(argv[i + 1]); i += 2
        else: paths.append(argv[i]); i += 1
    bad = 0
    for p in paths:
        s = json.loads(pathlib.Path(p).read_text())
        errs = check(s, forbid)
        print(f"{p}: {'OK' if not errs else 'FAIL'}")
        for e in errs: print("   -", e)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
