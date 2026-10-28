"""Video spec: load, resolve paths, validate, platform layouts. Standard library only.

A spec is one JSON file (see references/spec.md). Everything the pipeline writes goes to
<spec dir>/build/<spec stem>/: captures/, takes/, vo.mp3, timing.json, <stem>-<platform>-<format>.mp4.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

FORMATS = {"9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080)}
PLATFORMS = ("telegram", "instagram")
SCENE_TYPES = ("reveal", "title", "screen", "spotlight", "cards", "mapping")
CAPTIONS_DEFAULT = {"reveal": False, "title": False}  # their big on-screen text already says the line
STT_LANG = {"en": "eng", "ru": "rus"}

# Content box and caption band as fractions of the frame: (left, top, right, bottom), caption centre y.
# WHY Instagram 9:16 differs: the Reels UI covers the top ~13 %, the bottom ~25 % (caption, audio,
# username) and a ~17 % rail of buttons on the right. Figures follow third-party creator guides
# (Meta publishes safe zones for ads only) — preview on a phone before posting.
LAYOUTS = {
    ("instagram", "9:16"): {"box": (.06, .13, .83, .63), "caption_y": .685, "caption_x": (.06, .83)},
    ("telegram", "9:16"): {"box": (.046, .10, .954, .84), "caption_y": .91, "caption_x": (.06, .94)},
}
DEFAULT_LAYOUT = {"box": (.06, .07, .94, .80), "caption_y": .875, "caption_x": (.06, .94)}

PUNCT = ".,:;!?…\"'«»“”„()[]—–"

FADE_IN, FADE_OUT = .30, .22  # every shot fades in from / out to the background
END_FADE = .5                 # the whole film fades out over its last half second

# Reading-time floor for on-screen text, from the reading-time rule of the it-reelsmaker skill:
# a short line needs 0.8 s, a phrase 0.3 s per word. Captions follow the speech and are exempt.
READ_MIN, READ_PER_WORD = .8, .3


def layout(platform: str, fmt: str) -> dict:
    return LAYOUTS.get((platform, fmt), DEFAULT_LAYOUT)


def norm_word(w: str) -> str:
    return w.strip(PUNCT).casefold()


def words(text: str) -> list[str]:
    return text.split()


def find_word(say: str, ref: str) -> int:
    """Index of the word `ref` ("word" or "word#2" for the 2nd occurrence) in `say`."""
    m = re.fullmatch(r"(.+?)(?:#(\d+))?", ref.strip())
    if not m:
        raise KeyError(f"empty word reference in: {say!r}")
    target, nth = norm_word(m.group(1)), int(m.group(2) or 1)
    hits = [i for i, w in enumerate(words(say)) if norm_word(w) == target]
    if len(hits) < nth:
        raise KeyError(f"word {ref!r} not found in: {say!r}")
    return hits[nth - 1]


def load(path: str | Path) -> dict:
    path = Path(path).resolve()
    spec = json.loads(path.read_text())
    spec["_path"], spec["_dir"] = path, path.parent
    spec["_build"] = path.parent / "build" / path.stem
    spec.setdefault("lang", "en")
    spec.setdefault("targets", [{"platform": "telegram", "format": "9:16"}])
    spec.setdefault("voice", {})
    spec.setdefault("captures", [])
    spec.setdefault("tail", 1.8)
    for sc in spec.get("scenes", []):
        sc.setdefault("captions", CAPTIONS_DEFAULT.get(sc.get("type"), True))
    return spec


def resolve(spec: dict, ref: str) -> Path:
    """'@name' -> build/captures/name.png; anything else is relative to the spec file."""
    if ref.startswith("@"):
        return spec["_build"] / "captures" / f"{ref[1:]}.png"
    return (spec["_dir"] / ref).resolve()


def at_refs(scene: dict) -> list[str]:
    """Every word reference a scene uses, for validation."""
    refs = []
    def add(v):
        if isinstance(v, str): refs.append(v)
    for key in ("punch", "media", "code", "footer", "tap"):
        if isinstance(scene.get(key), dict): add(scene[key].get("at"))
    for it in scene.get("items", []):
        if isinstance(it, dict): add(it.get("at"))
    if isinstance(scene.get("sequence"), dict): add(scene["sequence"].get("from"))
    return refs


def validate(spec: dict) -> list[str]:
    problems = []
    scenes = spec.get("scenes") or []
    if not scenes:
        problems.append("spec has no scenes")
    seen = set()
    for i, sc in enumerate(scenes):
        where = f"scene {i} ({sc.get('id', '?')})"
        if not sc.get("id"): problems.append(f"{where}: missing id")
        elif sc["id"] in seen: problems.append(f"{where}: duplicate id")
        seen.add(sc.get("id"))
        if sc.get("type") not in SCENE_TYPES:
            problems.append(f"{where}: type must be one of {', '.join(SCENE_TYPES)}")
        if not (sc.get("say") or "").strip():
            problems.append(f"{where}: missing 'say' (the voice-over line)")
            continue
        for ref in at_refs(sc):
            try: find_word(sc["say"], ref)
            except KeyError as e: problems.append(f"{where}: {e.args[0]}")
    for t in spec["targets"]:
        if t.get("platform") not in PLATFORMS: problems.append(f"target {t}: platform must be one of {PLATFORMS}")
        if t.get("format") not in FORMATS: problems.append(f"target {t}: format must be one of {tuple(FORMATS)}")
    names = [c.get("name") for c in spec["captures"]]
    if len(names) != len(set(names)): problems.append("capture names must be unique")
    if spec["lang"] not in STT_LANG: problems.append(f"lang must be one of {tuple(STT_LANG)}")
    return problems


def script_text(spec: dict) -> str:
    return " ".join(sc["say"].strip() for sc in spec["scenes"])


def bounds(spec: dict, timing: list[dict]) -> list[float]:
    """Shot boundaries in seconds: 0, a cut in the silence between every two lines, the end of the film."""
    tm = {t["id"]: t for t in timing}
    order = [sc["id"] for sc in spec["scenes"]]
    cuts = [min(tm[b]["start"] - .1, (tm[a]["end"] + tm[b]["start"]) / 2) for a, b in zip(order, order[1:])]
    return [0.0] + cuts + [timing[-1]["end"] + spec["tail"]]


def reading_need(text: str) -> float:
    n = sum(1 for w in words(text) if any(ch.isalnum() for ch in w))  # "·", "…", "→" are not read as words
    return max(READ_MIN, READ_PER_WORD * n) if n else 0.0


def _on_screen(sc: dict, b0: float, word_t) -> list[tuple[str, str, float, float | None]]:
    """(label, text, appears, dimmed_at) for every piece of text a scene shows; mirrors pv_render's scenes."""
    t, out = sc.get("type"), []
    def static(*keys):
        for k in keys:
            if sc.get(k): out.append((k, sc[k], b0, None))
    if t == "reveal":
        static("lead")
        punch = sc.get("punch")
        tp = word_t(punch.get("at")) if punch else None
        for i, it in enumerate(sc.get("items", [])):
            out.append((f"items[{i}]", it["text"], word_t(it.get("at")), tp))  # the punch dims the items
        if punch: out.append(("punch", punch["text"], tp, None))
    elif t == "title":
        static("kicker")
        for i, s in enumerate(sc.get("lines", [])): out.append((f"lines[{i}]", s, b0, None))
        static("sub")
        for k in ("code", "footer"):
            if sc.get(k): out.append((k, " ".join(sc[k].get("lines", [])), word_t(sc[k].get("at")), None))
    elif t in ("spotlight", "cards", "mapping"):
        static("kicker", "title", "sub")
        for i, r in enumerate(sc.get("rows", [])):  # rows slide in .45 s apart after .4 s
            out.append((f"rows[{i}]", " ".join(r.get(k, "") for k in ("tag", "left", "right")), b0 + .4 + i * .45, None))
    return out


def reading_problems(spec: dict, timing: list[dict]) -> list[str]:
    """On-screen text that is not up long enough to read, given the narration's word timing."""
    tm = {x["id"]: x for x in timing}
    b = bounds(spec, timing)
    last = len(spec["scenes"]) - 1
    problems = []
    for i, sc in enumerate(spec["scenes"]):
        words_t = tm[sc["id"]]["words"]
        def word_t(ref, _sc=sc, _w=words_t):
            if ref is None: return b[i]
            if isinstance(ref, (int, float)): return _w[0][1] + ref
            return _w[find_word(_sc["say"], ref)][1]
        gone = b[i + 1] - (END_FADE if i == last else FADE_OUT)
        pieces = _on_screen(sc, b[i], word_t)
        # text that is there from the first frame is read one piece after another
        upfront = [p for p in pieces if p[2] <= b[i] + 1e-6 and p[3] is None]
        need = sum(reading_need(p[1]) for p in upfront)
        if upfront and gone - b[i] < need:
            problems.append(f"{sc['id']}: {', '.join(p[0] for p in upfront)} need {need:.1f}s to read, "
                            f"on screen {gone - b[i]:.1f}s")
        for label, text, t0, dimmed in pieces:
            if (label, text, t0, dimmed) in upfront: continue
            have = min(gone, dimmed if dimmed is not None else gone) - t0
            if have < reading_need(text):
                problems.append(f"{sc['id']}: {label} {text!r} needs {reading_need(text):.1f}s to read, "
                                f"on screen {max(0.0, have):.1f}s")
    return problems
