# Long-form tutorial (YouTube, 16:9)

A ≤ 5-minute tutorial video that matches one published article, presented by the owner's AI
talking head over real footage. The mandatory rules in `SKILL.md` apply in full; this file adds the
long-form specifics.

## Shape
- 1920×1080, ≤ 5:00 (target 4:00–4:50). Narration ≈ 2.2 words/s, so ≤ 650 spoken words.
- Beat 0: **cover**, 0.0–2.0 s, no narration, fading out at 1.6–2.0 s.
- Last beat: **end**, 8–12 s, with the QR code to the article and the next video's title.
- One idea per beat; beats are 4–25 s and contiguous.

## Presenter modes (hybrid)
| Mode | On screen | Use |
|---|---|---|
| `full` | presenter full-frame | intro (15–25 s) and outro (10–20 s); ≤ 45 s per video in total |
| `pip` | real footage + presenter in a corner, speaking | the body of the video |
| `vo` | real footage, voice only | sparingly, e.g. dense screen detail |
| `cover`, `end` | designed cards | first 2 s, last 8–12 s |

Presenter clips are generated per beat (per-second billing: cost ≈ seconds of `full` + `pip` at the
model's rate). Each clip starts from an identity-approved keyframe; run a 1–2-frame face test for
any new framing (16:9 full-frame differs from the 9:16 PiP) before generating a batch. Voice: one
whole-track speech-to-speech pass into the owner's voice, then the silence gate and mastering from
`presenter-reel.md`.

## Footage
Real only: the product's live pages recorded with Playwright (name the URL and the camera move:
scroll, zoom to a region, click), terminal runs recorded with vhs (exact command, real output),
source files shown in an editor, and the article's own screenshot tours. Never record a private
instance; record a public sample.

## Storyboard schema (`<video>/storyboard.json`)
```json
{
  "n": 1, "slug": "", "title": "", "youtube_title": "≤ 70 chars", "module": "",
  "article": {"id": 0, "title": "", "url": ""},
  "cover": {"headline": "2–5 WORDS", "kicker": "SERIES · 01", "visual": ""},
  "beats": [{"id": "b0", "start": 0.0, "end": 2.0, "mode": "cover", "line": "", "visual": "", "source": ""}],
  "end_card": {"qr_url": "", "next": ""},
  "chapters": [{"t": "0:00", "label": ""}],
  "description": "", "thumbnail": "",
  "words": 0, "duration_s": 0, "presenter_seconds": {"full": 0, "pip": 0},
  "open_checks": []
}
```
Validate with `python3 scripts/pv_storyboard.py <dir>/storyboard.json [...]`. Optional
`--forbid <text>` (repeatable) fails any beat that mentions the text, e.g. a private host or port.

## Review page
Render each storyboard as a review page (cover mock, beat table with timings, mode, line and
footage source, chapters, description, cost) and republish it after every change.
