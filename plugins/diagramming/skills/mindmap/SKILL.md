---
name: mindmap
description: Use when the user asks for a mindmap, mind-map, concept map, idea tree, brainstorm diagram, or any radial topic explosion ("draw a mindmap of X", "map out the themes around Y", "mindmap the differentiators of Z"). Produces dark-themed self-contained HTML+SVG with a central root, branches radiating in all directions, halo text, Q-curved Bezier connectors, and geometry-audit gating.
---

# Mindmap Skill

Generate radial mindmaps as self-contained HTML files with inline SVG, sharing the blueprint aesthetic of the sibling `architecture-diagram` skill: dark `#020617` background, JetBrains Mono, halo text, semantic palette, Q-curved Bezier connectors, deterministic geometry-audit gate.

## What triggers this skill

- "Draw a mindmap of X"
- "Map out themes / dimensions / ideas around Y"
- "Brainstorm a tree of Z"
- "Concept map for …"
- Any request producing a radial, single-root, branching diagram (≠ system architecture)

When in doubt: if the topic has **one focal point and N parallel themes** (a brainstorm, a taxonomy, a feature wheel), this skill. If it has **components, data flow, edges that mean traffic/calls/dependencies**, use `architecture-diagram` instead.

## Output contract

Same as `architecture-diagram`:
- Single self-contained `.html` file with inline SVG, JetBrains Mono via Google Fonts, dark `#020617` background, halo text via `paint-order: stroke fill`, built-in export toolbar (PNG / PDF / Copy).
- Use `../architecture-diagram/resources/template.html` as the starting point — same header, same toolbar, same capture script.
- Geometry-audit (`../architecture-diagram/resources/geometry-audit.py`) must exit 0 before the diagram is done.

## Workflow

1. **Parse the brief into a tree.** The user writes a freeform prose request. Extract:
   - **Root** (1 node): the topic the user named. If the user said "mindmap Socket0", root = "Socket0". Wrap in 1–3 words; this is the headline.
   - **Branches** (3–8 nodes): main themes/dimensions/axes. Pick from the user's words first; only invent labels when the user gave a topic without structure.
   - **Leaves** (2–4 per branch typically, max 6): concrete sub-points under each branch.
   - Depth > 3 is a smell — collapse or split into multiple mindmaps.

2. **Assign semantic colors per branch.** Each branch + its subtree share one of the palette colors (cyan / emerald / violet / amber / rose / orange / slate). Use the meaning matrix below; if no semantic match, cycle through the palette.

3. **Compute radial layout** (algorithm below).

4. **Draw**: root rect at center, branch rects + edges in their sector, leaf rects + edges fanning from each branch.

5. **Run the geometry audit** — `python3 ../architecture-diagram/resources/geometry-audit.py <file>.html` — and iterate until clean.

## Radial layout algorithm

The mindmap lives in a canvas (default `viewBox="0 0 1400 1000"`) with the root at the center `(Cx, Cy) = (700, 500)`. Default radii: `R1 = 260` (branch ring), `R2 = 440` (leaf ring). Adjust these together if N branches > 6 or labels are unusually long — see *Sizing tradeoffs* at the bottom.

### Step 1 — root box

- `root.w = max(content_w + 28, 240)`, `root.h = 76`, centered on `(Cx, Cy)`.
- Title font: 16 px bold, with optional 10 px subtitle line.

### Step 2 — branch ring (depth 1)

Let N = number of branches. Distribute around 360°, **starting at the top** (`θ_0 = -π/2`, north), going clockwise:

```
θ_i = -π/2 + i * (2π / N)        # i = 0..N-1
```

Place each branch with its **center** at radius `R1` from `(Cx, Cy)`:

```
branch_i.cx = Cx + R1 * cos(θ_i)
branch_i.cy = Cy + R1 * sin(θ_i)
```

- `branch.w = max(content_w + 16, 160)`, `branch.h = 56`. Keep boxes horizontal — never rotate the rect or its text.
- Each branch owns the **angular sector** `[θ_i − π/N, θ_i + π/N]` for its descendants.

**Avoid overlap.** With N = 5 and `R1 = 260`, neighbouring branch centers sit ≈ 305 px apart on the circle — fits comfortably. For N > 6, bump `R1` to `260 + 30 * (N − 6)`. For N ≤ 4, the canvas can shrink to `1100 × 800` and `R1 = 230`.

### Step 3 — leaves (depth 2)

For each branch with M leaves, fan them out **across most of the branch's angular sector** at radius `R2`:

```
sector_half  = π / N                                          # half-angle of branch's sector
leaf_spread  = sector_half * 0.85                             # use 85 % of the sector
φ_j          = θ_i + (j − (M − 1)/2) * (2 * leaf_spread / max(M, 1))
leaf_j.cx    = Cx + R2 * cos(φ_j)
leaf_j.cy    = Cy + R2 * sin(φ_j)
```

- `leaf.w = max(content_w + 14, 140)`, `leaf.h = 44`. Font: 11 px name, 9 px sub-label.
- **If a label produces `content_w + 14 > 170 px`, shorten it.** Long leaf labels are the #1 cause of overlap with neighbours. Trim adverbs ("Plaintext in RAM only" → "Plaintext in RAM"), use symbols ("Free → enterprise"), or split into two leaves.
- If M > 4 in a single branch, stack leaves in **two arcs**: half at `R2`, half at `R2 + 80`, interleaved by index parity. Don't try to cram 8 leaves on one arc.

### Step 4 — depth 3 (rare)

Only if the brief genuinely needs it. Same recursion: each leaf gets a narrower sector (`leaf_spread / max(K, 1)`) and a new radius (`R3 = R2 + 200`). If you reach depth 3 with more than 2–3 nodes, refactor: the diagram is becoming an outline, not a mindmap.

### Step 5 — connectors

Every edge is a Q-curved Bezier from **parent's outer side** to **child's inner side**:

```
P  = (parent.cx + (child.cx − parent.cx) * (parent_radius_x / d),
      parent.cy + (child.cy − parent.cy) * (parent_radius_y / d))

C  = (child.cx  − (child.cx  − parent.cx) * (child_radius_x  / d),
      child.cy  − (child.cy  − parent.cy) * (child_radius_y  / d))

control = midpoint(P, C) + perpendicular(P → C) * curve_amount
        where curve_amount = 0.18 * |P − C|        # gentle curve
        and perpendicular rotates the P→C vector 90° clockwise

path = M P.x,P.y Q control.x,control.y C.x,C.y
```

- `parent_radius_x` = `parent.w / 2`, `parent_radius_y` = `parent.h / 2`. (Approximate the rect as an ellipse for attachment — exact rect-side calculation is fine too, but the ellipse approximation reads as smoother in practice.)
- Stroke: 1 px solid for branch lines, 1 px solid for leaf lines, all in the **branch's semantic colour**. No arrowheads on mindmaps — they aren't directional.

### Step 6 — labels on edges (optional)

Mindmaps usually don't need edge labels. If a connection carries a verb worth saying (e.g., "requires", "blocks"), drop it at the curve midpoint with a halo. Don't add labels just to fill space.

## Visual rules (reuse from architecture-diagram)

- **Halo text**: every `text` element has `paint-order: stroke fill; stroke: #020617; stroke-width: 4` (6 for the root, 3 for sub-labels).
- **Semantic palette**: cyan / emerald / violet / amber / rose / slate / orange — see `../architecture-diagram/resources/design-system.md` for fills, strokes, glow values.
- **Typography**: JetBrains Mono. Sizes: 16 px (root), 12 px (branches), 11 px (leaves), 9 px (sub-labels).
- **No rotation**: every text and rect stays horizontal. Mindmaps that rotate labels read worse, not better.
- **No icons by default** (mindmaps are textual). If the user explicitly asks for icons, use the same corner-disc rule as architecture-diagram (`circle r=12` at the rect's top-left, half outside / half inside).

## Color assignment guide

When the brief carries domain hints, match them to the palette:

| Branch theme | Color |
|---|---|
| Performance / speed / latency | amber |
| Security / compliance / trust | rose |
| Architecture / data / storage | violet |
| Engineering / build / process | emerald |
| Frontend / UX / interface | cyan |
| Operations / runtime / SRE | orange |
| External / generic / "other" | slate |

When no semantic match exists, cycle through `[cyan, emerald, violet, amber, rose, orange, slate]` in branch order so adjacent branches don't share a colour.

## Audit workflow

Same script as architecture-diagram, run from any cwd:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/architecture-diagram/resources/geometry-audit.py <file>.html
```

The audit checks the same six classes — `component-overlap`, `edge-crosses-component`, `edge-crosses-edge`, `label-overlaps-component`, `edge-crosses-label`, `arrowhead-reversed`. For mindmaps, **only `component-overlap` and `edge-crosses-component` are blocking** — radial diagrams routinely have edge-edge crossings near the center, and that's fine. Pass `--ignore-edge-edge` after the audit's first pass if you've already confirmed the structure.

## What you must not do

- ❌ Don't rotate text to follow the radial angle. Keep all labels horizontal.
- ❌ Don't use arrowheads on connectors. Mindmaps are non-directional.
- ❌ Don't pack more than 8 branches at depth 1. Split into multiple mindmaps if needed.
- ❌ Don't go past depth 3. It stops being a mindmap and becomes an outline.
- ❌ Don't write a per-mindmap Python or Node script. The model emits the SVG directly, applying the algorithm above inline.
- ❌ Don't omit the export toolbar — it's the same boilerplate as architecture-diagram.

## Example brief → output

> "Mindmap the core concerns of an outbound API proxy."

Extract:
- Root: **Outbound proxy** (subtitle: "third-party API gateway")
- 5 branches covering the canonical engineering dimensions: **Credentials**, **Egress control**, **Observability**, **Reliability**, **Provider quirks**
- 3 leaves each (concrete sub-concerns)

Layout: 5 branches → `θ_i = -π/2 + i * 72°` (N, NE, SE, SW, NW). Colors picked by theme: rose (credentials/security), amber (egress/edge), violet (observability/data), emerald (reliability/engineering), cyan (provider/interface). See [`../../examples/12-mindmap-outbound-proxy.svg`](../../examples/12-mindmap-outbound-proxy.svg) for the rendered output.

## Sizing tradeoffs

When the audit flags `component-overlap`, before tweaking radii, check the data:

1. **Too many leaves per branch?** > 4 → stack in two arcs (see Step 3) or split a branch.
2. **A long label?** > 170 px box width → shorten. Shortening one label fixes the whole arc.
3. **Too many branches?** N > 6 → bump `R1` by `30 * (N − 6)` and `R2` proportionally.
4. **Branch labels touching their leaves?** Increase `R2 − R1` from 180 → 220.

Only after exhausting (1) and (2) should you grow the canvas.
