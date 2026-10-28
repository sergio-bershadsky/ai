# Example: Epic Observation promo (EN, Telegram + Instagram 9:16)

The spec captures `page.html`, the static export of the epic-observation plugin's sample epic.
Generate it first (from the repo root):

```bash
S=plugins/epic-observation/skills/epic-observation
python3 $S/scripts/observe.py export $S/assets/sample-seed.json \
  plugins/promo-video/skills/promo-video/examples/epic-observation/page.html --profile $S/assets/profiles/jira.json
python3 plugins/promo-video/skills/promo-video/scripts/promo.py all \
  plugins/promo-video/skills/promo-video/examples/epic-observation/video.json
```

The forecast in the burn-up runs from today's date, so dates in the frames change with the day you render.
