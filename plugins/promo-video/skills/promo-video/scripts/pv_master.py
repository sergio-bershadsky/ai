"""Audio mastering and the acceptance check for a finished MP4. Standard library + ffmpeg.

The voice-over and the optional music are mixed into a float WAV, brought to −14 LUFS integrated
with a true peak of at most −1 dBTP by two-pass loudnorm, and only then encoded to AAC once.
`check` measures the delivered file; a non-empty list of problems means: do not post it.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

TARGET_I, TARGET_TP, LRA = -14.0, -1.0, 11.0
TOL_I = .7      # integrated loudness window around the target
TP_AIM = -1.5   # WHY below TARGET_TP: the AAC encode after mastering can lift true peak a little
DUR_TOL = .05   # audio vs video track length, seconds (AAC priming and frame padding)


def _ffmpeg_stderr(args: list[str]) -> str:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()[-400:]}")
    return r.stderr


def _loudnorm_json(stderr: str) -> dict:
    blocks = re.findall(r"\{[^{}]*\}", stderr)
    if not blocks:
        raise RuntimeError("loudnorm printed no measurement")
    return json.loads(blocks[-1])


def measure(path: Path) -> dict:
    """Integrated loudness (LUFS), true peak (dBTP), loudness range and loudnorm's pass-1 values."""
    raw = _loudnorm_json(_ffmpeg_stderr(["-i", str(path), "-map", "0:a:0",
                                         "-af", f"loudnorm=I={TARGET_I}:TP={TP_AIM}:LRA={LRA}:print_format=json",
                                         "-f", "null", "-"]))
    return {"I": float(raw["input_i"]), "TP": float(raw["input_tp"]), "LRA": float(raw["input_lra"]),
            "thresh": float(raw["input_thresh"]), "offset": float(raw["target_offset"])}


def master_wav(src: Path, dst: Path) -> dict:
    """Two-pass loudnorm (single pass drifts off target). Returns the pass-1 measurement."""
    m = measure(src)
    af = (f"loudnorm=I={TARGET_I}:TP={TP_AIM}:LRA={LRA}:measured_I={m['I']}:measured_TP={m['TP']}"
          f":measured_LRA={m['LRA']}:measured_thresh={m['thresh']}:offset={m['offset']}:linear=true")
    # loudnorm works at 192 kHz internally; set the output rate explicitly
    _ffmpeg_stderr(["-y", "-i", str(src), "-af", af, "-ar", "48000", "-c:a", "pcm_f32le", str(dst)])
    return m


def durations(path: Path) -> tuple[float, float]:
    """(video track, audio track) duration in seconds."""
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration:stream_disposition=attached_pic",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    dur = {}
    for s in json.loads(out)["streams"]:
        if s.get("disposition", {}).get("attached_pic"): continue  # the cover picture has no duration
        dur.setdefault(s["codec_type"], float(s.get("duration", 0)))
    return dur.get("video", 0.0), dur.get("audio", 0.0)


def accept(m: dict, dur_v: float, dur_a: float) -> list[str]:
    problems = []
    if abs(m["I"] - TARGET_I) > TOL_I:
        problems.append(f"loudness {m['I']:.1f} LUFS, want {TARGET_I:.0f} ±{TOL_I}")
    if m["TP"] > TARGET_TP:
        problems.append(f"true peak {m['TP']:.1f} dBTP, want ≤ {TARGET_TP:.0f}")
    if abs(dur_a - dur_v) > DUR_TOL:
        problems.append(f"duration: audio {dur_a:.2f}s vs video {dur_v:.2f}s")
    return problems


def check(path: Path) -> list[str]:
    return accept(measure(path), *durations(path))
