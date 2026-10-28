---
name: promo-video
description: Author a narrated promo / feature-announcement video for Telegram or Instagram (Reels, feed, stories) in Russian or English from one prompt — real UI captured with Playwright, an ElevenLabs voice-over with word-level timing, scenes cut on the narration, word-highlighted captions, platform-safe layouts (9:16, 4:5, 1:1), fade-through transitions, MP4 ready to post plus the post text. Use it whenever someone wants a video, reel, teaser, demo clip, launch video or "advertisement" for a feature, plugin, PR, release, product page or artifact — "сделай видео / ролик / рилс / промо / анонс фичи для телеграма или инстаграма", "make a reel about this PR", "feature promo with voice-over" — even if they don't say "promo-video".
---

# Promo Video

One prompt → a narrated vertical video about a feature, built from the **real UI**, voiced by
ElevenLabs and cut on the narration. The engine is `scripts/promo.py`; you write one JSON spec.

```
subject (PR, page, app)          spec  video.json  (scenes: what is said + what is shown)
   │ read, pick 4–6 features        │
   ▼                                ▼
captures (Playwright) ──▶ build/<stem>/captures/*.png
voice (ElevenLabs, 1 take/model) ──▶ takes/*.mp3 + word timing ──analyze──▶ best take → vo.mp3
render (PIL frames → ffmpeg) ──▶ <stem>-<platform>-<format>.mp4 + contact sheets
```

Paths below are relative to this skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/promo-video`).

## Workflow

### 0. Settle the brief — ask only what the prompt leaves open
Infer first, ask once (one `AskUserQuestion` call) only for what you cannot infer:

| Decision | Default when unstated |
|---|---|
| Language | Language of the user's prompt (`ru` / `en`) |
| Platforms → targets | Telegram 9:16 **and** Instagram 9:16 (Reels). Feed post → 4:5; square → 1:1 |
| Length | 40–55 s (≈ 90–110 words; see the word budget) |
| Voice | Stock voice from the account; for `ru` prefer a voice whose `voices --lang ru` row lists `ru` |
| Footage | Real UI of the subject. Never mock a UI, never use third-party logos (tool names as text are fine) |

### 1. Check the machine
`python3 scripts/promo.py doctor SPEC` — ffmpeg + libx264, Pillow, numpy, Playwright + Chromium,
fonts (IBM Plex Sans/Mono by default, Cyrillic checked), the ElevenLabs key (never printed).
Key: `ELEVENLABS_API_KEY` in the environment, or `voice.env_file` in the spec / `--env-file`.
Never copy the key into the spec, the repo or any output.

### 2. Study the subject
Read the PR / README / page. List what it does for a user, pick 4–6 things worth *seeing*, and
find where each is visible in the real UI (live URL, local HTML, an exported artifact, a running
app). Each feature becomes one scene with one line of narration and one visual.

### 3. Write the script for the ear
- **Arc:** hook (the pain, ≤ 10 s) → name it (intro) → 3–5 feature scenes → why it's different →
  call to action. One idea per scene.
- **Word budget:** both examples measured ≈ 2.0–2.2 words/s on `eleven_v4` (EN 118 words → 53 s,
  RU 38 words → 18.8 s). Target seconds × 2 = words.
- **Sound natural:** full phrases with commas and "…" for breath (`"Jira... or Linear, or GitHub"`),
  not staccato fragments (`"Or Linear. Or GitHub."` reads robotic). No speed-up.
- **Names the voice may misread** (surnames, brand words, abbreviations): keep them on screen and out
  of the narration unless `analyze` shows they are heard correctly. Rephrase rather than respell —
  phonetic spellings tested worse.
- Every `at` word a scene uses must appear in that scene's `say`.

### 4. Plan captures
`references/spec.md` → *captures*. Rules of thumb (1080-wide output):
- full-frame `screen` scenes: viewport 540×960, scale 2 (→ 1080×1920);
- `spotlight` / `cards` images: element `selector`, viewport ~520–720 wide, scale 3 (crisp when panned);
- a replay of states: `sequence` (`eval` with `{i}`) → `@name` frames; coordinates for a tap
  ripple via `measure`;
- dark theme by default (`theme: "dark"` in the capture and the spec).

### 5. Write the spec and validate
Start from `examples/epic-observation/video.json` (EN, 9 scenes, 2 targets) or
`examples/minimal-ru/video.json` (RU, 4 scenes, Instagram 9:16 + Telegram 1:1). Put it next to
the material, e.g. `promo/<topic>/video.json`. Then `promo.py check SPEC`.

### 6. Capture, voice, choose the take
```bash
python3 scripts/promo.py capture SPEC
python3 scripts/promo.py voice   SPEC                    # one take per model in voice.models
python3 scripts/promo.py analyze SPEC --pick             # Scribe STT error rate + pitch range
```
`analyze` transcribes each take (ElevenLabs Scribe) and prints the word error rate, every phrase
heard differently (`bershadsky → bachinski`), the pitch range in semitones (a flat contour is what
sounds robotic) and pauses. `--pick` takes the fewest errors, then the livelier contour. If a
brand word is misheard in every take, rephrase that line and re-voice — don't ship it.
Compare voices with `voice SPEC --voice NAME` (takes are named `<model>__<voice>`).
Defaults: models `eleven_v4` (most expressive) and `eleven_multilingual_v2` (fallback).
Cost ≈ script characters × takes (+ the same for Scribe); report it.

### 7. Review stills before the full render
`promo.py stills SPEC` writes `scenes-<target>.png` (mid-point of every scene) and
`cuts-<target>.png` (frames around every cut), and prints the overlap check at the cuts
(`0.00` = no two shots on screen). **Read both PNGs** and fix before rendering:
text cut off, captions covering the key number, an image too small to read, Instagram content
in the bottom quarter or under the right-hand button rail.

`stills` also prints the **reading-time check**: every piece of on-screen text (heading, reveal
item, punch, code block, footer, mapping row) must stay up for 0.8 s, or 0.3 s per word for a
phrase, from the moment it appears until its shot fades (a reveal item only until the punch dims
it). Captions are exempt. `render` refuses while any line fails; fix by shortening the text,
anchoring it to an earlier word, or raising `tail` for the last scene. `--force` is for a
deliberate flash.

### 8. Render, verify, deliver
`promo.py render SPEC` → one MP4 per target (H.264 + AAC, `+faststart`, 30 fps) plus
`<name>.cover.jpg`. After drawing, the render does three things:
- **Mastering, always.** Voice (+ music) is mixed to a float WAV, brought to −14 LUFS
  integrated / true peak ≤ −1 dBTP by two-pass loudnorm, then encoded to AAC once. The
  acceptance check measures the delivered file (−14 ±0.7 LUFS, peak ≤ −1 dBTP, audio and video
  the same length). A failure leaves `<name>.rejected.mp4` and exits non-zero. **Never post it.**
- **Cover in frame 0.** The first shot starts from an empty background, so frame 0 (the preview
  a feed shows before playback) is replaced by a settled frame of the first scene. Pick another
  moment with `cover: {"scene": id, "at": word}` or `{"t": s}`; `cover: false` turns it off.
  The same frame is saved as `cover.jpg` for the platform's cover upload. `"embed": true` also
  stores it as cover art inside the MP4 (an `attached_pic` stream). How each platform treats that
  stream is not verified, so it is off by default.
- **Incremental.** Frames are encoded in 2-second chunks under `build/<stem>/chunks/`, each with
  a fingerprint of everything it depends on (its scenes, word timing, theme, captures, renderer
  source). A re-render redraws only chunks whose fingerprint changed, so a late text fix costs
  its own scene, not the whole film. A new take retimes everything and redraws every chunk.
  `--full` ignores the cache.

The render prints loudness, peak and how many chunks it redrew. Send the files, then give post text in the
video's language: Telegram caption ≤ 1024 characters with the install command / link; Instagram
caption + 3–5 hashtags. Say what you could not verify (you cannot hear the voice — ask the user to
listen).

`promo.py all SPEC` runs capture → voice → analyze/pick → stills → render in one go; use it
after the spec is stable.

## Judgment calls
- **Telegram vs Instagram:** layouts differ only in safe areas. Instagram 9:16 keeps text inside
  13–63 % of the height and clear of the right rail; captions sit at ~68 %. Telegram 9:16 uses the
  whole frame, captions at ~91 %. Figures follow third-party guides (Meta publishes ad safe zones
  only) — tell the user to preview on a phone.
- **Captions:** on for `screen` / `spotlight` / `cards` / `mapping` (muted autoplay), off for
  `reveal` / `title` where the big text already says the line.
- **Render time:** frames draw in parallel worker processes. Measured: the RU example (21 s,
  2 targets) rendered in 11 s on a plugged-in M4 Max; the EN example (55 s, 2 targets) took 26 min
  on battery in Low Power Mode. Check `pmset -g` when it crawls and say so instead of waiting silently.
- **Music:** optional `music: {file, volume}` loops under the voice and ducks while it speaks. Use
  only tracks the user owns or that are licensed for this use.
- **Privacy:** never put the owner's personal email or the API key in a spec, caption, frame or post.

## Files
- `scripts/promo.py` — CLI. `pv_spec.py` spec, layouts, cut points, reading-time check,
  `pv_capture.py` Playwright, `pv_voice.py` ElevenLabs takes + analysis, `pv_render.py` scenes,
  captions, transitions, cover, chunked encode, `pv_master.py` loudness mastering + acceptance.
- `references/spec.md` — every spec field and scene type.
- `examples/` — two working specs. `tests/` — `python3 -m unittest discover -s tests`.
