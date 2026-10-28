"""Voice-over: ElevenLabs takes with word timings, and an objective comparison of takes.

The API key comes from ELEVENLABS_API_KEY or an env file (KEY=VALUE lines); it is never printed.
"""

from __future__ import annotations

import base64
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

import pv_spec as S

API = "https://api.elevenlabs.io"


class VoiceError(RuntimeError):
    pass


def api_key(spec: dict, env_file: str | None = None) -> str:
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"].strip()
    path = env_file or spec["voice"].get("env_file")
    if path:
        p = Path(path).expanduser()
        p = p if p.is_absolute() else spec["_dir"] / p
        for line in p.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip().removeprefix("export ").strip() == "ELEVENLABS_API_KEY":
                return v.strip().strip("\"'")
    raise VoiceError("no ElevenLabs key: set ELEVENLABS_API_KEY or voice.env_file in the spec")


def _call(key: str, path: str, body: dict | None = None, raw: bytes | None = None, ctype: str = "application/json"):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(API + path, data=data, headers={"xi-api-key": key, "Content-Type": ctype})
    try:
        return json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:  # body explains quota / voice / model errors; it never echoes the key
        raise VoiceError(f"{path.split('?')[0]}: HTTP {e.code} {e.read()[:400].decode(errors='replace')}") from None


def list_voices(key: str) -> list[dict]:
    return _call(key, "/v1/voices")["voices"]


def resolve_voice(key: str, want: str) -> tuple[str, str]:
    voices = list_voices(key)
    for v in voices:
        if v["voice_id"] == want:
            return v["voice_id"], v["name"]
    for v in voices:
        if v["name"].casefold().startswith(want.casefold()):
            return v["voice_id"], v["name"]
    raise VoiceError(f"voice {want!r} not in this account; run `promo.py voices` to list them")


def settings(model: str, voice: dict) -> dict:
    # v3/v4 take stability only (lower = more expressive); older models take the full set.
    if re.match(r"eleven_v\d", model):
        return {"stability": voice.get("stability", 0.4)}
    s = {"stability": voice.get("stability", 0.35), "similarity_boost": voice.get("similarity", 0.75),
         "style": voice.get("style", 0.3), "use_speaker_boost": True}
    if "speed" in voice:
        s["speed"] = voice["speed"]
    return s


def scene_timing(spec: dict, alignment: dict) -> list[dict]:
    """Per-scene start/end and per-word times from ElevenLabs character alignment."""
    chars = alignment["characters"]
    starts, ends = alignment["character_start_times_seconds"], alignment["character_end_times_seconds"]
    text = "".join(chars)
    out, pos = [], 0
    for sc in spec["scenes"]:
        say = sc["say"].strip()
        i = text.index(say, pos)
        pos = i + len(say)
        ws, k = [], i
        for w in S.words(say):
            k = text.index(w, k)
            ws.append([w, round(starts[k], 3), round(ends[k + len(w) - 1], 3)])
            k += len(w)
        out.append({"id": sc["id"], "start": ws[0][1], "end": ws[-1][2], "words": ws})
    return out


def take(spec: dict, model: str, key: str) -> Path:
    """Synthesize the whole script in one request (one take keeps prosody continuous across scenes)."""
    v = spec["voice"]
    voice_id, name = resolve_voice(key, v.get("voice", "Daniel"))
    fmt = v.get("output_format", "mp3_44100_128")
    body = {"text": S.script_text(spec), "model_id": model, "voice_settings": settings(model, v)}
    r = _call(key, f"/v1/text-to-speech/{voice_id}/with-timestamps?output_format={fmt}", body)
    takes = spec["_build"] / "takes"
    takes.mkdir(parents=True, exist_ok=True)
    short = re.split(r"\s+[-–—]\s+", name)[0]  # "Daniel - Steady Broadcaster" -> "Daniel"
    tag = f"{model}__{re.sub(r'[^a-z0-9]+', '-', short.casefold()).strip('-')[:24] or 'voice'}"
    mp3 = takes / f"{tag}.mp3"
    mp3.write_bytes(base64.b64decode(r["audio_base64"]))
    timing = scene_timing(spec, r["alignment"])
    (takes / f"{tag}.json").write_text(json.dumps({"model": model, "voice": name, "scenes": timing}, indent=1, ensure_ascii=False))
    print(f"take {tag}: {timing[-1]['end']:.1f}s")
    return mp3


def pick(spec: dict, tag: str) -> None:
    takes = spec["_build"] / "takes"
    shutil.copy(takes / f"{tag}.mp3", spec["_build"] / "vo.mp3")
    shutil.copy(takes / f"{tag}.json", spec["_build"] / "timing.json")
    print(f"voice-over: {tag}")


# ---------------------------------------------------------------- analysis
def _norm_tokens(s: str) -> list[str]:
    return re.sub(r"[^\w ]", " ", s.casefold().replace("-", " ")).split()


def misheard(ref: str, hyp: str) -> tuple[float, list[str]]:
    """Word error rate and the reference phrases the recogniser heard differently."""
    r, h = _norm_tokens(ref), _norm_tokens(hyp)
    sm = difflib.SequenceMatcher(a=r, b=h, autojunk=False)
    errors, diffs = 0, []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op != "equal":
            errors += max(a1 - a0, b1 - b0)
            diffs.append(f"{' '.join(r[a0:a1]) or '∅'} → {' '.join(h[b0:b1]) or '∅'}")
    return errors / max(len(r), 1), diffs


def transcribe(key: str, mp3: Path, lang: str) -> str:
    b = uuid.uuid4().hex
    head = "".join(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n"
                   for k, v in {"model_id": "scribe_v1", "language_code": S.STT_LANG[lang]}.items())
    body = (head + f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"take.mp3\"\r\n"
            "Content-Type: audio/mpeg\r\n\r\n").encode() + mp3.read_bytes() + f"\r\n--{b}--\r\n".encode()
    return _call(key, "/v1/speech-to-text", raw=body, ctype=f"multipart/form-data; boundary={b}")["text"]


def prosody(mp3: Path) -> dict:
    """Pitch spread (semitones) and pauses — a flat contour is what reads as 'robotic'."""
    import numpy as np
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    n, hop, lo, hi = int(.04 * sr), int(.01 * sr), sr // 300, sr // 70
    f0, rms = [], []
    for s in range(0, len(x) - n - hi, hop):  # YIN cumulative-mean-normalised difference
        fr = x[s:s + n + hi]
        rms.append(float(np.sqrt(np.mean(fr[:n] ** 2))))
        d = np.array([np.sum((fr[:n] - fr[t:t + n]) ** 2) for t in range(lo, hi)])
        cm = d / (np.cumsum(d) / np.arange(1, len(d) + 1) + 1e-12)
        k = int(np.argmin(cm))
        f0.append(sr / (k + lo) if cm[k] < .15 else np.nan)
    f0, rms = np.array(f0), np.array(rms)
    v = f0[~np.isnan(f0)]
    st = 12 * np.log2(v / np.median(v)) if len(v) else np.zeros(1)
    silent, runs, c = rms < .02 * rms.max(), [], 0
    for s_ in silent:
        if s_: c += 1
        elif c: runs.append(c / 100); c = 0
    pauses = [p for p in runs if p >= .15]
    return {"seconds": round(len(x) / sr, 1), "pitch_range_st": round(float(np.percentile(st, 95) - np.percentile(st, 5)), 1),
            "pauses": len(pauses), "mean_pause_s": round(float(np.mean(pauses)), 2) if pauses else 0.0}


def analyze(spec: dict, key: str) -> list[dict]:
    rows = []
    ref = S.script_text(spec)
    for mp3 in sorted((spec["_build"] / "takes").glob("*.mp3")):
        hyp = transcribe(key, mp3, spec["lang"])
        wer, diffs = misheard(ref, hyp)
        row = {"take": mp3.stem, "wer": round(wer, 3), "misheard": diffs, **prosody(mp3)}
        rows.append(row)
        print(f"{mp3.stem:24} {row['seconds']:5.1f}s  WER {wer:5.1%}  pitch range {row['pitch_range_st']:4.1f} st  "
              f"pauses {row['pauses']} (avg {row['mean_pause_s']}s)")
        for d in diffs:
            print(f"{'':26}heard: {d}")
    (spec["_build"] / "takes" / "report.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    return rows


def best(rows: list[dict]) -> str:
    """Fewest recognition errors first (a misread brand name sinks a promo), then the livelier contour."""
    return min(rows, key=lambda r: (round(r["wer"], 2), -r["pitch_range_st"]))["take"]


if __name__ == "__main__":
    sys.exit("use promo.py")
