---
name: architecture-diagram
description: Use when the user asks for a system, infrastructure, cloud, security, network topology, or architecture diagram. Produces polished dark-themed self-contained HTML+SVG files with mathematically-correct label placement, clean-background priority, text halos, and leader lines.
---

# Architecture Diagram Skill

Generate professional technical architecture diagrams as self-contained HTML files with inline SVG graphics, CSS styling, and a built-in export toolbar (PNG / PDF / Copy-to-clipboard).

Blueprint aesthetic: dashed cluster boundaries, halo text, semantic palette, Q-filleted orthogonal edges, and a deterministic geometry-audit linter that gates release.

## What triggers this skill

- "Draw an architecture diagram"
- "Show me how X system is structured"
- "Make a diagram of the data flow"
- "Visualize the network topology"
- Any request producing a system / infrastructure / network / security diagram

## Core output contract

Always produce **a single self-contained `.html` file** that:
- Renders correctly when opened directly in any modern browser
- Has embedded CSS (no external stylesheets except Google Fonts)
- Has inline SVG (no external images)
- Has the export toolbar with PNG / PDF / Copy buttons (uses html2canvas + jsPDF from CDN with SRI hashes)
- Captures the entire `#report-container` div via `getBoundingClientRect()` + 32 px padding
- Renders to `#020617` (slate-950) dark background even in PDF
- Has working halos on ALL text labels for cross-element readability

See `resources/template.html` for the canonical starting point.

## How this skill is used (no generator scripts)

This skill is **self-contained markdown**. Every algorithm needed to produce a correct blueprint diagram lives in `resources/design-system.md` and the rule list below. When the user asks for a diagram, the model applies those algorithms inline in the conversation and emits HTML+SVG directly — there is no build step, no Python generator, no `make` target. The maintainer never writes per-diagram code.

The only Python in `resources/` is genuinely-generic post-production tooling: `geometry-audit.py` deterministically detects intersections/overlaps/overflows (blocking — must pass before a diagram is done), `audit-labels.py` lints label placement vs arrow midpoints, `coordinate-shifter.py` bulk-shifts y-coordinates in any HTML+SVG file. None produce diagrams; all operate on already-rendered output.

Examples under `examples/` are hand-committed SVG artifacts that demonstrate the rules in their current form. They are evidence, not infrastructure.

## The blueprint rules (read in order)

These rules describe the v2 (blueprint) aesthetic. They are inspired by **ISO 128** (technical drawings — line grammar, weight series, terminator shape) and **ISO/IEC 19505** (UML 2.x — relationship notation). Every rule below is an algorithm the model applies at generation time — no external tool needed.

1. **Layout first, content second.** Before emitting any SVG, compute and validate the bounding-box geometry of every component, cluster, and floating label. No two boxes may intersect; every component must fit inside its parent cluster; same-role boxes share width; row/column centrelines align across the diagram. Only after this validation passes do you draw rects, place icons, place labels, and route edges. See `resources/design-system.md` § *Workflow — layout first, content second*.
2. **Label placement: clean background beats geometric midpoint.** Don't put labels at the Bezier/edge midpoint just because the math says so. Find empty visual space the size of the label and put the label there. Use leader lines if needed.
3. **Knockout text-border for labels — no chip rects.** Every text element gets a wide solid canvas-colour stroke via `paint-order: stroke fill` (4 px for body, 6 px for titles, 3 px for sublabels). This masks underlying lines cleanly through each glyph; the universal halo IS the background. Never wrap labels in rounded-corner rect "chips".
4. **Reserve icon space before placing text.** When a component box has an icon in the left padding, the label must NOT centre on the full box — it will slide under the icon. Centre the text in the space *right of the icon* (`text_x = (icon_right + 8 + box_right) / 2`) or left-align at `icon_right + 8`. Required guard: `icon_size + 16 px` of horizontal clearance.
5. **Distribute attach points across a box side when multiple arrows share it.** Group edges by `(box, side)`. For N edges in a group, give each a distinct attach point at fraction `(k+1)/(N+1)` of the side length (`k = 0..N-1`, sorted by direction toward target). Single-arrow case lands at the midpoint — backward-compatible. See `resources/design-system.md` § *Edge endpoint distribution*.
6. **Orthogonal routing with rounded corners.** Edges are horizontal or vertical only, with `r = 12` rounded turns. Route horizontal legs in CLEAR corridors between rows of components — never through a row of components. For cross-band edges use a `Z`-shape via an intermediate y (V-H-V) or x (H-V-H). Diagonals are forbidden.
7. **Open-V chevron arrowhead; UML endings semantic.** Default arrowhead is an open V chevron (ISO 128). For real UML relationships use the semantic endings: open triangle (inheritance), dashed + open triangle (realization), filled diamond (composition), open diamond (aggregation), dashed + open V (dependency). Never use a filled triangle as the default arrowhead.
8. **Quiet geometry.** Stroke widths from `{0.5, 1, 1.5, 2}` only. Corner radii from `{0, 2, 4}` only. Same width / rx for the same role across the whole diagram.
9. **Gaps must fit the label between them.** For every edge sitting between two adjacent boxes (same row or same column), measure `label_w = len * font_size * 0.6` and ensure the gap is `≥ label_w + 24 px`. If not, widen the gap (default), shorten the label, or promote to a callout. Done in Phase 1 layout, not after.
10. **Labels are text-only with the knockout halo.** No underline beneath text by default — the halo does the line-masking. Underlines + diagonal leaders are reserved for **callouts** (text in clear space pointing at a distant referent, ISO 128-24).
11. **Icon discs are opt-in.** Only emit a corner-anchored coloured disc with a stencil glyph when the user explicitly asks for an icon on a specific box. Default position is top-left (`center = (box.x + 20, box.y)`, `r = 12`, fill = box stroke colour). The disc straddles the top border (half outside, half inside). Apply the icon-space rule to the box's label. See `resources/design-system.md` § *Icon disc (corner-anchored, opt-in)*.
12. **3× spacing between root-level blocks.** Generous padding around every cluster. Default gap between major bands is 100–200 px, not 30 px. Visual hierarchy depends on whitespace.
13. **Sub-group clusters within larger clusters.** When a logical group has more than ~4 components, partition them into 2–4 named sub-groups with their own dashed boundaries.

## Workflow

1. **Read the design system** — `resources/design-system.md` for colors, fonts, spacing, component patterns.
2. **Read the label-placement rules** — `resources/label-placement.md` for the math + clean-background principle.
3. **Sketch the layout** in 3 horizontal bands minimum: top context (customer/external), middle (your system), bottom (downstream/integrations or detail). Estimate width per box, decide on viewBox dimensions.
4. **Build from `template.html`** — copy and customise. Always preserve the header, toolbar, capture script, halo CSS.
5. **Place components** with adequate padding (40 px between boxes, 80 px between sub-groups).
6. **Place arrows** with proper labels: compute Bezier midpoint first, then look for clean background nearby. If clean space is far from midpoint, use leader line.
7. **Run the geometry audit (REQUIRED, blocking)** — `resources/geometry-audit.py <file>.html` must exit `0` before the diagram is considered done. It deterministically reports component-overlap, component-outside-cluster, edge-crosses-component, edge-crosses-edge, label-overlaps-component, and edge-crosses-label. Iterate fixes and re-run until clean. Only pass `--ignore-edge-edge` when the diagram is an intentional mesh.
8. **Run the label audit** — `resources/audit-labels.py <file>.html` reports any label > 50 px from its arrow's midpoint and lacking a leader line.
9. **Render in browser** to verify visually. Iterate on placements.
10. **Output the final file** as `<name>-architecture.html` in the user's docs directory.

## Design system summary (see `resources/design-system.md` for full)

### Semantic colors

| Component Type | Fill | Stroke |
|---|---|---|
| Frontend | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| Backend / service | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| Database / store | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| Cloud edge / LB | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| Security / IDP / KMS | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| External / generic | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |
| Message bus | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |

### Typography

- Font: JetBrains Mono everywhere (loaded from Google Fonts)
- Sizes: 12 px component names · 9 px sublabels · 8 px annotations · 7 px tiny labels · 13–16 px headings

### Boundaries

- Component boxes: `rx="6"`, 1.5 px stroke, semi-transparent fill
- Security groups: dashed `stroke-dasharray="4,4"`, transparent fill, rose stroke
- Region / large boundaries: dashed `stroke-dasharray="8,4"`, `rx="12"`, amber stroke

### Arrow line styles (semantic)

| Style | Meaning |
|---|---|
| Solid | Data plane traffic (HTTPS, mTLS) |
| Dashed cyan/emerald | Control plane (xDS, gRPC) |
| Dashed rose | Auth / key / rotation flow |
| Dashed amber | Egress to upstream / external |
| Dotted violet (`1,3`) | Audit log stream |
| Bold (no dash) | Key / secret flow |

## Label placement algorithm

See `resources/label-placement.md` for the formal version. Summary:

```
def place_label(arrow_path, label_text, occupied_regions):
    # Compute Bezier midpoint as initial candidate
    if arrow_path.type == 'quadratic':
        # P = 0.25·P0 + 0.5·P1 + 0.25·P2
        midpoint = bezier_midpoint(arrow_path)
    elif arrow_path.type == 'line':
        midpoint = ((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

    # Compute label bounding box
    label_width = len(label_text) * font_size * 0.6
    label_height = font_size * 1.2
    margin = font_size

    # Search for clean space, starting at midpoint and spiraling outward
    for candidate in spiral_search(midpoint, max_distance=300):
        bbox = (candidate.x - label_width/2, candidate.y - label_height,
                label_width + 2*margin, label_height + 2*margin)
        if not overlaps_any(bbox, occupied_regions):
            # Place label here
            distance = euclidean(candidate, midpoint)
            return {
                'x': candidate.x,
                'y': candidate.y,
                'anchor': 'middle',
                'needs_leader_line': distance > 30
            }

    # Fallback: place at midpoint, rely on halo
    return {'x': midpoint.x, 'y': midpoint.y, 'anchor': 'middle', 'needs_leader_line': False}
```

The principle: **fight for clean visual space**. Geometric midpoint accuracy is the lowest-priority criterion.

## Audit workflow

Two audit scripts. **Both must be run.** The geometry audit is **blocking** — a diagram is not done until it exits 0.

### 1. Geometry audit (blocking, required)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/architecture-diagram/resources/geometry-audit.py <file>.html
```

Deterministically reports six classes of collision, each with SVG line numbers:

| Kind | Meaning | Typical fix |
|---|---|---|
| `component-overlap` | Two component rects overlap | Move one box; widen row spacing |
| `component-overflow-cluster` | Component pokes outside its parent cluster | Resize cluster or move box inward |
| `edge-crosses-component` | Path segment passes through a box that is not its endpoint | Re-route via clear corridor (V-H-V or H-V-H) |
| `edge-crosses-edge` | Two paths cross outside their shared endpoints | Re-route the shorter/less-important one; or use `--ignore-edge-edge` for intentional meshes |
| `label-overlaps-component` | Text bbox sits on a box it does not label | Shorten label, move it, or promote to a callout with a leader line |
| `edge-crosses-label` | Path runs through a foreign label's bbox | Shift label off the corridor, or shift the corridor |
| `arrowhead-reversed` | Path ends on a rect edge but the tangent at the endpoint points *away* from the rect interior, so `orient="auto"` rotates the arrowhead 180° | Make the path's last segment travel **into** the rect (e.g. for top-edge entry, end the path with a downward V or a Q whose endpoint is at the target y). Common bug: ending with `Q X,via X,via+12 V target` where `target < via+12` — the final V draws upward. |
| `edge-on-cluster-border` | A path's H/V segment runs within ~2 px of a cluster's dashed boundary for ≥8 px, so the two lines visually merge into one cluttered band | Move the path's via_y / via_x further inside the cluster (≥10 px from the border) |

Iterate: fix one class, re-run, repeat until "clean — no geometry issues".

### 2. Label distance audit

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/architecture-diagram/resources/audit-labels.py <file>.html
```

Flags any arrow label > 50 px from its curve midpoint without a leader line. Each flag is either fixable (move label closer or add a leader line) or by design (endpoint annotation — add the leader line and move on).

## Coordinate shifter (for fixing spacing)

When the diagram needs more breathing room between root-level blocks, use:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/architecture-diagram/resources/coordinate-shifter.py <file>.html
```

The script shifts y-coordinates in tiers by editing the SVG directly: top row stays, control plane shifts +N, region shifts +2N, etc. Handles `y=` attributes and `d="..."` path commands correctly.

## What you must not do

- ❌ Don't place labels at Bezier midpoints without checking for collisions.
- ❌ Don't use bright primary colors; stick to the semantic palette.
- ❌ Don't use serif fonts or proportional fonts; JetBrains Mono only.
- ❌ Don't omit the export toolbar; it's a feature, not optional.
- ❌ Don't use foreignObject in SVG (renders inconsistently in html2canvas).
- ❌ Don't load external images or stylesheets except Google Fonts and the two CDN scripts (with SRI hashes preserved).
- ❌ Don't pack components without gaps. The default minimum gap is 40 px.

## Example invocations

> "Create an architecture diagram for our payment processing pipeline: Stripe webhook → API gateway → queue → workers → Postgres."

→ Use semantic colors (Stripe is external/slate, API gateway is cloud-edge/amber, queue is message-bus/orange, workers are backend/emerald, Postgres is database/violet). Place in left-to-right horizontal flow. Add halos. Run audit.

> "Diagram our auth flow: user → CloudFront → ALB → API → Cognito → Postgres."

→ Top-down flow. Cognito is security/rose. Annotate the JWT verification arrow with a dashed rose line. Run audit.

> "Show me a diagram of our multi-region setup with global control plane and regional data planes."

→ This is the Socket0 Connect shape. Two-band layout: global CP cluster (sub-grouped: compute services, identity, storage, audit) at top; regional fan-out below. Generous spacing. Halos and leader lines as needed.

## Attribution

Original work.
