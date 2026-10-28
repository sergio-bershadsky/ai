# Spec reference — `video.json`

One JSON file per video. Relative paths resolve against the spec's folder; everything generated
goes to `build/<spec stem>/` next to it.

## Top level

| Field | Default | Meaning |
|---|---|---|
| `title` | — | Free text, for humans. |
| `lang` | `en` | `en` or `ru`. Sets Scribe's language in `analyze` and the capture locale. |
| `targets` | `[{"platform":"telegram","format":"9:16"}]` | One MP4 per entry. `platform`: `telegram`, `instagram`. `format`: `9:16` (1080×1920), `4:5` (1080×1350), `1:1` (1080×1080). |
| `voice.voice` | `Daniel` | Voice name prefix or voice id from `promo.py voices`. |
| `voice.models` | `["eleven_v4","eleven_multilingual_v2"]` | One take per model. |
| `voice.stability` | `0.4` (v3/v4), `0.35` (older) | Lower = more expressive. v3/v4 accept only this setting. |
| `voice.similarity`, `voice.style`, `voice.speed` | `0.75`, `0.3`, — | Older models only. Leave `speed` unset (speed-ups sound robotic). |
| `voice.output_format` | `mp3_44100_128` | `mp3_44100_192` needs a Creator plan or higher. |
| `voice.env_file` | — | File with `ELEVENLABS_API_KEY=…` if the variable is not in the environment. Never put the key itself in the spec. |
| `theme.preset` | `dark` | `dark` or `light` (colours of the background, cards, captions). |
| `theme.colors` | — | Override any of `bg panel ink muted line accent ok code_bg caption_bg` (hex). |
| `theme.fonts` | IBM Plex Sans / Mono | `{"sans": "Family", "mono": "Family"}` or `.ttf` paths. Needs Cyrillic for `ru`. |
| `music` | — | `{"file": "track.mp3", "volume": 0.15}` — loops, ducks under the voice, fades out. |
| `tail` | `1.8` | Seconds after the last word (the final card holds, then fades). |
| `fps` | `30` | Frame rate. |

## `captures[]` — real UI with Playwright

| Field | Default | Meaning |
|---|---|---|
| `name` | required | Output `captures/<name>.png` (or `<name>_00.png…` for a sequence). Reference as `@name`. |
| `url` | required | `https://…` or a local file relative to the spec. |
| `viewport` | `[540, 960]` | CSS pixels. |
| `scale` | `2` | Device scale factor (540 × 2 = 1080). Use 3 for images that get panned or enlarged. |
| `theme` | `dark` | `prefers-color-scheme`. |
| `steps` | `[]` | Run in order before the shot: `{"click": sel}`, `{"check": sel}`, `{"hover": sel}`, `{"fill": [sel, text]}`, `{"press": key}`, `{"scroll": sel}`, `{"eval": js}`, `{"wait": ms}`. |
| `selector` | — | Screenshot this element only; omit for the viewport. |
| `full_page` | `false` | Whole scroll height (for a `screen` that scrolls). |
| `sequence` | — | `{"count": N or "js expression", "eval": "js with {i}", "wait_ms": 150}` → one shot per `i`. |
| `measure` | — | `{"key": "js expression"}` → numbers saved as `<name>.<key>` for `scroll` / `tap`. |

## Scenes — common fields

| Field | Meaning |
|---|---|
| `id` | Unique. |
| `type` | `reveal`, `title`, `screen`, `spotlight`, `cards`, `mapping`. |
| `say` | The narration line. All scenes are voiced in one take, in order. |
| `captions` | Word-highlighted captions. Default `true`, except `reveal` and `title`. |

**Word references** (`at`, `sequence.from`): `"play"`, `"нажмите#2"` (second occurrence) — matched
case-insensitively, ignoring punctuation, within the scene's own `say`. A number means seconds
after the line starts. `promo.py check` fails on a word that is not in the line.

**Images:** `"@name"` (a capture), `"@name_12"` (a sequence frame) or a path relative to the spec.

**Measured numbers** (in `screen.scroll`, `screen.tap.x/y`): a number in output pixels, or
`{"measure": "capture.key", "scale": 2, "offset": -60}` → value × scale + offset.

## Scene types

### `reveal` — hook
`lead` (small line), `items: [{"text", "at"}]` (big lines that pop in on their words),
`punch: {"text", "at"}` (accent line; the items dim when it lands).

### `title` — intro, call to action
`kicker` (small caps), `lines` (big name, one entry per line, sized to fit), `sub`,
`code: {"lines": [...], "at"}` (terminal block, `$` prompt), `footer: {"lines": [...], "at"}`
(first line accent mono, rest muted), `media: {"image", "at", "width"}` (card below, kept above
the caption band).

### `screen` — full-frame UI
`image` or `frames` (`"@name"` = all `name_NN.png`). With frames: `sequence: {"from": word}` —
frame 0 until that word, then the frames play out to the end of the scene. `scroll: [from, to]`
(top of the window in output pixels, eased). `tap: {"x", "y", "at"}` — ripple on the word.

### `spotlight` — one feature, close up
`kicker`, `title`, `sub`, `image`, `fit`: `"width"` (default, fill the content width) or a pixel
height (for wide charts). If the image is larger than the panel it pans; `pan: [from, to]` as
fractions of the overflow (default `[0, 1]`).

### `cards` — several captures side by side
`kicker`, `title`, `sub`, `images: [...]` stacked as cards, sliding in `stagger` seconds apart
(default 0.35). Scaled down together if they don't fit.

### `mapping` — "your words → one model"
`kicker`, `title`, `sub`, `rows: [{"tag", "left", "right"}]` (tool name, its wording, the neutral
value), optional `media: {"image", "at"}` below when there is room above the captions.

## Layout safe areas

| Target | Content box (x0, y0, x1, y1 as fractions) | Caption centre |
|---|---|---|
| Instagram 9:16 | .06, .13, .83, .63 — clear of the Reels header, caption/audio block and the right button rail | .685 |
| Telegram 9:16 | .046, .10, .954, .84 | .91 |
| Any 4:5 / 1:1 | .06, .07, .94, .80 | .875 |

Instagram figures follow third-party creator guides; Meta publishes safe zones only for ads.
Preview the export on a phone.
