"""Measure a vertical video's content against the Instagram/Telegram UI safe box.

usage: python3 pv_safezone.py VIDEO [--step 0.5] [--box 65,270,960,1248] [--bg auto|#rrggbb] [--tol 40]

Grabs a frame every --step seconds, takes the bounding box of every pixel that differs from the
background by more than --tol (sum of RGB deltas), and prints each frame whose box leaves the safe
box. Exit 1 on any violation. Run it on the slide/background layer when a corner PiP is accepted in
the UI zone; on the full picture otherwise.

WHY these defaults: on 1080x1920 the Reels UI covers the top 14 % (y < 270), the bottom 35 %
(y > 1248), the left 6 % (x < 65) and a 120 px button rail on the right (x > 960) — the most-cited
Meta ad figures; Meta publishes none for organic Reels, so the conservative set is used for both
platforms.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

import numpy as np

SAFE_BOX = (65, 270, 960, 1248)  # x0, y0, x1, y1 on 1080x1920


def probe(video: str) -> tuple[int, int, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "default=nw=1", video],
                         capture_output=True, text=True, check=True).stdout
    kv = dict(l.split("=", 1) for l in out.split() if "=" in l)
    return int(kv["width"]), int(kv["height"]), float(kv["duration"])


def frame(video: str, t: float, w: int, h: int) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(int)


def content_box(img: np.ndarray, bg: np.ndarray, tol: int) -> tuple[int, int, int, int] | None:
    ys, xs = np.nonzero(np.abs(img - bg).sum(2) > tol)
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(ys) else None


def outside(box: tuple[int, int, int, int], safe: tuple[int, int, int, int]) -> bool:
    return box[0] < safe[0] or box[1] < safe[1] or box[2] > safe[2] or box[3] > safe[3]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Measure a vertical video against the Reels safe box.")
    ap.add_argument("video"); ap.add_argument("--step", type=float, default=.5)
    ap.add_argument("--box", default=",".join(map(str, SAFE_BOX)))
    ap.add_argument("--bg", default="auto", help="background colour; auto = pixel (5,5) of each frame")
    ap.add_argument("--tol", type=int, default=40)
    a = ap.parse_args(argv)
    w, h, dur = probe(a.video)
    sx, sy = w / 1080, h / 1920
    x0, y0, x1, y1 = (int(v) for v in a.box.split(","))
    safe = (round(x0 * sx), round(y0 * sy), round(x1 * sx), round(y1 * sy))
    bad = 0
    for t in np.arange(a.step, dur - .05, a.step):
        img = frame(a.video, float(t), w, h)
        bg = img[5, 5] if a.bg == "auto" else np.array([int(a.bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)])
        box = content_box(img, bg, a.tol)
        if box and outside(box, safe):
            bad += 1; print(f"t={t:6.2f}s OUT  content x {box[0]}-{box[2]} y {box[1]}-{box[3]}  safe {safe}")
    print("safe-zone check:", "PASS" if not bad else f"FAIL ({bad} frames)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
