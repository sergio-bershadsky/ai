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
