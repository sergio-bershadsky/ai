# Presenter reel: AI talking-head PiP over tutorial slides

Use this path when the video is a **tutorial with a presenter**: a photoreal talking head in a PiP
over animated terminal or UI slides, voiced in the owner's cloned voice. `promo.py` covers the
capture-and-TTS promo. This file covers what `promo.py` doesn't: the presenter, speech-to-speech,
sound effects, the QA loop and the production storyboard. Everything here was learned on real
deliveries; the dates mark when each figure was measured.

**Owner-specific values never go in this file.** Read them from the consuming project's
`.claude/promo-video.local.md`, the *local card*; the template is at the end of this file. That
covers voice ids, the identity model id, the approved base keyframe, the real-photo folder and the
owner's style rules. If the card is missing, ask for those values. Never substitute a stock voice
or face.

## 0. Pipeline at a glance

```
script (EN/RU, per beat) ─▶ storyboard artifact (canvas) ─▶ owner locks hook, beats, CTA
        │
        ├─▶ slides  : PIL frames inside the safe box ─▶ slides.mp4
        ├─▶ presenter: identity keyframe ─▶ N gesture keyframes on flat green ─▶ owner approves face
        │             ─▶ 1 test clip ─▶ owner OK ─▶ remaining clips (one per beat)
        ├─▶ voice   : clips' own speech, laid on the beat timeline ─▶ ONE whole-track STS ─▶ gate
        ├─▶ sfx     : cue list on the same timeline (never through STS)
        └─▶ picture : slides + keyed PiP ─▶ mix ─▶ master ─▶ QA loop ─▶ deliver + captions + post text
```

Keep the plan in one build script with steps (`plan | voice | mix | qa | all`). Each step reads the
previous step's files, so a late fix re-runs only what changed. Beat lengths come from the clip
durations rounded to whole frames (`beats.json`); every layer reads that one file.

## 1. Sizing: revalidated 2026-11-03

On a 1080×1920 frame, the platform UI covers:

| Zone | Instagram Reels | Pixels |
|---|---|---|
| Top: header, "Reels", camera | 14 % | y < 270 |
| Bottom: caption, username, audio | 35 % | y > 1248 |
| Left | 6 % | x < 65 |
| Right: like / comment / share rail | 120 px | x > 960 |

These come from the most-cited Meta ad guidance, as quoted by third-party guides (hopperhq,
admanage.ai, firstpier). Meta publishes nothing for organic Reels. Older templates use
108/320/60/120 px. **Use the conservative set above for every vertical delivery, Telegram
included**, so one file posts to both platforms.

- **Content box:** design slides for x 65–960, y 270–1248 from the start. Inset the layout further
  by the outline stroke widths and by the push-in zoom. A 1.2 % push-in around the centre moves an
  edge at x 74 out to x 68. Practical slide margins are therefore x 92–930, with the first line at
  y≈290.
- **Faces and hands are content.** Flush bottom-right puts a PiP under the caption and the button
  rail. If the owner still chooses it, record the choice as accepted on the storyboard. Do not
  report it as "safe".
- **Measure, don't eyeball:** `scripts/pv_safezone.py VIDEO` grabs a frame every 0.5 s, takes the
  bounding box of everything that differs from the background, and exits 1 on any frame outside
  the box. Wire it into the build's QA so a violation fails the build. Then render an overlay of
  the four zones on 6 frames and *look* at it. The overlay is how the missing-glyph spinner (an
  empty box) was caught.
- **Captions:** a caption pill must sit inside the box too (its bottom edge ≤ 1248). The engine's
  Instagram 9:16 layout centres captions at 0.62 H for this reason.
- **Encode:** H.264 High, yuv420p, 30 fps, `+faststart`, AAC 256k. The master was 20 MB for 52 s.
  For a preview inside an artifact (16 MB cap), re-encode at CRF 24 with AAC 160k, which gave 7 MB.

## 2. Storyboard artifact (the "canvas")

The owner reviews and decides everything on one storyboard artifact. It is a single HTML page
published with the Artifact tool.

- **Content:** a header (topic, length per language, voices, aspect, end card, presenter), a
  proportional timeline per language, then one row per beat. Each row has a 9:16 frame mock, the
  EN and RU lines with word counts, and the direction notes. Production cards come after: open
  decisions, captures, and a **ledger** of every generation and credit spent. Once a draft exists,
  add a draft card at the top with the playable preview and a cost card.
- **Republish after every change**: a generation, a take, a decision, a spend, a fix. Always publish
  the same `file_path`, so the URL stays the same. From a new session (after compaction), pass the
  existing `url`; publishing without it silently creates a second artifact. First `read` the live
  version and every file you overwrite; a publish over an unread file is refused.
- **Remove rejected material** (frames, takes) from the canvas when the owner rejects it. The page
  shows the current truth, not history. History goes in the ledger as a line.
- **Video previews** go in `files` next to the page and must stay under the 16 MB size cap.
- **Cost card:** take the amounts from the provider's transaction log, never from estimates. Group
  them by phase using the timestamps, and check that they sum to the balance delta. Show the money
  as a range from the plan rate to the top-up rate when you can't tell which credits were used, and
  name the FX rate and its date. Validate the chart palette with the dataviz validator.

## 3. Presenter PiP

### 3.1 Identity first, then keyframes
1. Start from the owner's **approved base keyframe** (local card) and **real photos** (local card,
   2–3 of them, face clearly visible). Never build keyframes from a fresh, unapproved render. A
   batch of 20 was rejected ("It's not my face") because it was edited from one. Keyframes that are
   consistent with each other still aren't proven to match the real face.
2. Edit the pose and gesture onto the base with an image-edit model (2026-11:
   `nano_banana_pro`, 2 credits per edit). Refs: the base keyframe plus the real photos. Prompt: the
   pose, hands at chest height, a positive face, and wardrobe and accessories from the local card.
3. **Test 1–2 frames and get the owner's face approval before the batch.** Only then run the batch;
   for a 50 s reel that's about 20 gesture keyframes.
4. **Green screen:** do not prompt a chroma background, which comes out as an uneven gradient.
   Instead, run the provider's background remover (about 1 credit each) on the normal render, then
   composite locally onto flat `#00B140`. Local rembg failed: isnet left the coat and hands
   see-through, and u2net_human_seg kept the furniture.
5. **Background look:** the owner's call, from the local card. For the PiP it was an "amateur real"
   look: home room, phone on a tripod, ordinary light. It still gets keyed out.

### 3.2 Clips
- **Model, 2026-11:** Seedance 2.0 Mini at 720p (834×1112) is billed **per second, 1 credit/s**.
  Seedance 2.5 costs 3 credits/s for a 480p draft, 7 at 720p and 16 at 1080p. Prices change, so run
  `models_explore` before quoting them. Mini clips held the face and the flat green, and spoke the
  quoted line correctly without an audio reference.
- **Inputs per clip:** the green gesture keyframe as the start image, 2 real photos as image
  references, and a prompt with the exact line in quotes. The prompt also describes a positive,
  smiling delivery, gestures at chest height that point at the slide area (up-left for a
  bottom-right PiP), and a locked-off camera.
- **One test clip first.** Check the transcript against the script, the green flatness, the face
  and the hands. Report what's weak, for example "smile faint, point held the whole clip".
- **Hands:** check finger count, morphing and size in every clip. Gestures aimed at the lens make
  the near hand huge.

### 3.3 Keying and placement
- **Use `chromakey`, never `colorkey`.** The RGB colorkey at a 0.32 similarity also removed dark
  pixels (beard, shirt, coat shadows), and the page background showed through. The owner called it
  "burned". `chromakey` works on chroma only:
  `chromakey=0x00A440:0.14:0.06,despill=type=green:mix=0.5:expand=0,scale=560:-2`.
  Sample the real green from a frame first; the Mini clips measured about (0,164,64).
- **Check against the source:** place the keyed PiP side by side with the same source frame and
  compare skin, beard and shadows. Pixel statistics alone missed it.
- **Placement:** PiP width ≈ 560 px for chest-up. Put it flush to the frame bottom; floating
  110 px above the bottom shows a hard torso cut. Check that it doesn't cover slide text. For
  Instagram, see §1.

## 4. Voice: whole-track speech-to-speech

The clip generator re-voices each line with its own voice, and the lips are synced to that audio.
So keep the clips' timing and convert the voice.

1. **Voice track:** lay each clip's audio at its beat start, apply 10 ms fades, and **peak-normalise
   to −3 dBFS before encoding**. A track summed at +2.7 dBFS clipped in the mp3 sent to STS.
2. **One STS pass over the whole track:** ElevenLabs `eleven_multilingual_sts_v2`, the owner's voice
   id from the local card, `remove_background_noise=true`. One pass means one consistent voice with
   no seams at the cuts.
3. **Seed loop:** STS output varies per run. Transcribe it (`scribe_v1`, word timestamps), diff it
   against the script, and if any word differs, re-run with the next seed (37, 11, 23, 51, 64,
   7, 91, …). Normalise before diffing: lowercase, "/" → "slash", strip "+", and keep an alias map
   for spellings the transcriber picks (`ctrl` → `control`).
4. **Gate:** mute the STS output wherever the source track is silent for ≥ 150 ms, with a 40 ms
   pre-roll and 30 ms fades. STS invents breaths and tails, and a compressor later lifts them into
   phantom words. 15 % of the track was gated on the context reel.
5. **Retries:** the ElevenLabs API drops connections (`RemoteDisconnected`). Wrap every POST in 4
   retries with backoff.
6. Re-run STS whenever the timeline changes. Picture-only fixes (keying, layout) don't need it.

## 5. Sound effects

- Keep a reusable cue folder and lay the cues on the beat timeline from a cue list.
  - **Typing:** under typed commands.
  - **Click:** on Enter or a key press, such as Ctrl+O.
  - **Soft glass tick:** when statuses light up.
  - **Room tone:** a faint bed at about −42 dB.
- **SFX never go through STS.** Mix them after it.
- Keep broadband beds faint (they mask plosives), and duck foley under the voice.

## 6. Mastering

voice (STS, gated) + sfx → `acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2`
→ `alimiter=limit=0.6:attack=4:release=60:level=false` → **two-pass** `loudnorm=I=-14:TP=-1.5:LRA=7`
(linear mode, measured values fed back) → AAC 256k.

Linear loudnorm alone came in at −15.6, then −15.2 LUFS, because it won't raise peaks over the true
peak limit. The limiter in front of it fixed that, giving −14.8.

## 7. QA loop: repeat until clean

Run it on the delivered file, fix the cause of each finding, and rebuild the affected step.

| Check | Pass |
|---|---|
| Clicks | 0 second-difference spikes above the local RMS envelope. A naive sample-jump threshold flags loud sibilants after compression (it reported 1205 false clicks). |
| Dropouts | no unexpected silence inside speech |
| Transcript | STT of the final file matches the script word for word, after normalisation and aliases |
| Onset drift | each beat's first word lands within ±120 ms of the plan |
| Garble | per-beat envelope correlation of the STS output against the source ≥ 0.8 |
| Loudness | −14 ± 1 LUFS integrated, peak ≤ −1 dBFS |
| Safe zone | `pv_safezone.py` exits 0, plus the overlay looked at |
| Picture | keyed PiP compared side by side with the source, no missing glyphs (render each glyph you use and compare it to the font's missing-glyph box; Menlo has no braille spinner characters) |

You cannot hear the result, so say so and ask the owner to listen on headphones.

## 8. Captions and post text

- **SRT from the final master:** transcribe it (word timestamps) and align the script's cue lines
  to the transcript on the concatenated **letter stream**, not on word tokens. The transcriber
  splits words differently ("auto-compact" comes back as "auto" + "compact"). The on-screen text
  can differ from the spoken text, for example `/context` for "slash context" and `Ctrl+O` for
  "control O". End each cue 0.25 s after its last word, and clamp it to 20 ms before the next cue
  so cues never overlap.
- **Post text:**
  - **Telegram:** ≤ 1024 characters, with the link.
  - **Instagram:** links in the caption are not clickable, so name the handle instead, and add 3–5
    hashtags.
- Include any copy-paste prompt the video demonstrates.

## 9. Cost and reporting

- **Ledger:** take credits from the provider's transaction log, grouped by phase. On the context
  reel that came to 157.24 credits:
  - rejected batch: 41.24
  - keyframes and cutouts: 64
  - clips: 52
  - final cut: 116 of the total, or 3.01 credits per second of video
- **Money:** the plan rate (€70 / 3,000 credits) to the top-up rate (€29.41 / 500), converted at a
  named, dated FX rate. That gave $4.11–10.36 for the reel.
- **Before any paid batch,** quote its cost with retakes. Mini at 1 credit/s × the script seconds
  × about 1.3 for retakes.

## 10. Failure log → rules

| What happened | Rule |
|---|---|
| Keyframes edited from an unapproved render ("not my face") | Base keyframe + real photos only; test 1–2 frames and get approval before any batch |
| Chroma green prompted directly came out as a gradient | Background remover, then local flat green |
| RGB colorkey "burned" the face | `chromakey`, plus a side-by-side check against the source |
| PiP floating above the bottom edge | Flush to the bottom |
| Step labels under the IG header, text under the button rail | Safe box from the start, `pv_safezone.py` gating QA |
| Spinner rendered as empty boxes | Test every glyph against the missing-glyph box |
| Loudness short of target | Limiter before two-pass loudnorm |
| False clicks | Second-difference spike detector |
| Published to a new URL after compaction | Pass the storyboard `url` explicitly; read before publishing |

## Local card template: `.claude/promo-video.local.md`

```markdown
# promo-video local card (gitignored, owner-specific)
voice_en: <ElevenLabs voice id>        # narration + STS target, EN
voice_ru: <ElevenLabs voice id>        # RU
identity_model: <provider soul / character id>
base_keyframe: <approved job id>       # every keyframe is edited from this
real_photos: <folder of real photos>   # 2–3 used as references per edit/clip
wardrobe: <coat, glasses, rings, necklaces …>
pip: {position: bottom-right, width_px: 560, background: "amateur real"}
storyboard_url: <artifact url>          # per video, republish after every change
end_card: <handles / QR rule>
rules: <owner's style rules or links to them>
```
