# Architecture Diagram Design System — v2 (Blueprint)

Dark-theme, monospace-typography, **engineering-blueprint** diagrams. The reference is a classic structural drawing or PCB layout: aggressive alignment, quiet geometry, computed coordinates, no decoration. Use this as the canonical reference for every diagram produced by this skill.

## Layout pre-check — gaps must fit edge labels (non-negotiable)

**Edge labels affect layout, not the other way round.** Before fixing component coordinates, enumerate every edge that will sit between two adjacent boxes (same row or same column) and measure the label that will go on it:

```
label_width_px  = len(label_text) * font_size * 0.6     (JetBrains Mono)
label_height_px = font_size * 1.2
required_gap    = label_width + 2 * pad                 (pad = 12 px each side, default)
```

If the current planned gap between the two boxes is less than `required_gap`, you have three options. In priority order:

1. **Widen the gap.** Push the right-hand (or lower) box further along its axis until the label fits comfortably. This is the default fix — the diagram width grows by `required_gap - current_gap`. Then re-align downstream columns / rows.
2. **Shorten the label.** If the label is verbose (`"introspect token via /jwks"` → `introspect`), trim it. Verbose only counts if it carries meaning the diagram doesn't already convey.
3. **Promote to callout.** Move the label off the edge into clear space and connect via a leader (see *Labels — default and leader-line*). Use sparingly — see the callout rule above.

**Worked example.** Row of four boxes (each 140 px wide) at y=200, edge labels "Bearer JWT" (10 chars), "introspect" (10 chars), "JWKS" (4 chars). At 11 px font size:

| Edge | Label | label_w | required_gap | current gap (60) | required gap | verdict |
|---|---|---|---|---|---|---|
| 1→2 | Bearer JWT | 66 | 90 | 60 | 90 | widen +30 |
| 2→3 | introspect | 66 | 90 | 60 | 90 | widen +30 |
| 3→4 | JWKS | 26 | 50 | 60 | 50 | OK |

Result: re-plan box positions with the new gaps before drawing anything. Same algorithm for vertically stacked boxes — `required_gap` becomes `label_height + 2 * pad`.

**Cluster boundaries must also be re-checked.** When you widen a gap, the parent cluster's width grows; re-derive `cluster.right` and `cluster.width` from `max(child.right) + pad` before validation.

## Workflow — layout first, content second (foundational)

Drawing a diagram in two phases prevents almost every class of mistake the earlier versions of this plugin produced (text overlapping icons, edges cutting through boxes, labels colliding, cluster borders intersecting components).

**Phase 1 — Layout.** Before emitting a single visual element, compute the bounding box for every entity:

1. Enumerate every component, cluster, sub-group, and free-floating label the diagram needs.
2. Assign `(x, y, width, height)` to each on the planned grid. Components that share a role share a width. Components in the same row share a y. Same-role columns share an x.
3. Lay out clusters around their child components: cluster `x = min(child.x) − pad`, `y = min(child.y) − pad − header`, `right = max(child.right) + pad`, `bottom = max(child.bottom) + pad`.
4. **Validation pass — required:**
   - No two component bounding boxes intersect.
   - No component extends beyond its parent cluster.
   - Edge routing channels have ≥ 20 px clearance from neighbouring boxes.
   - Same-role boxes have identical widths (alignment check).
   - Row centrelines and column centrelines align across the diagram (no fractional offsets).
5. If validation fails, **fix the layout numbers**. Do not "draw around" the bug — re-derive the geometry.

**Phase 2 — Content.** Only after Phase 1 validates: draw the rects, place the icons (apply icon-space formula), place the labels (apply text-border halo + underline), route the edges (orthogonal with `r=12` corners), attach markers.

Treat Phase 1 as the engineering drawing's grid pencilling and Phase 2 as the ink-over. Skipping Phase 1 is the source of every visual-chaos complaint historically reported on this plugin.

## Blueprint priorities (read this first)

1. **Aggressive alignment.** Components that share a role share a column or row. Same-role boxes get the same width. Centerlines line up across bands. If two things almost line up, make them line up exactly.
2. **Quiet geometry.** Stroke widths come from the fixed set `{0.5, 1, 1.5, 2}` — never an ad-hoc value. Corner radii from `{0, 2, 4}` — never 6/8/10. Same rx for the same role across the whole diagram.
3. **Computed coordinates.** Every position is derived from the box geometry. Never eyeball. The icon-space and label-routing rules in this document are formulas — compute them.
4. **No visual chaos.** No decoration that doesn't encode something. No drop-shadow except on hover. No bezier curves except for leader-lines. No diagonal edges. No off-grid placement.

## Canvas

- Background: `#020617` (slate-950)
- Subtle grid pattern:
  ```svg
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
  </pattern>
  ```
- The grid is rendered first; everything else sits on top.

## Typography

- Family: **JetBrains Mono** loaded from Google Fonts (`?family=JetBrains+Mono:wght@400;500;600;700`)
- Sizes:
  - 12 px — component box name
  - 9 px — sub-label / property line
  - 8 px — annotation / hint
  - 7 px — tiny labels (use sparingly)
  - 13–16 px — cluster headings
- All text gets the halo treatment (see below)

## Text-border (knockout halo, universal)

Every `<text>` element in the SVG renders with a wide **solid canvas-colour** stroke behind its fill. The stroke acts as a knockout — wherever the text sits on top of an edge or another shape, the underlying line is masked cleanly around the glyphs. This is what makes "labels just sit on the line" work without any chip rect.

```css
svg text {
  paint-order: stroke fill;
  stroke: #020617;            /* solid canvas colour — knockout */
  stroke-width: 4;            /* 4 px masks 1–1.5 px edges */
  stroke-linejoin: round;
  stroke-linecap: round;
}
svg text.title { stroke-width: 6; }   /* 16 px headings */
svg text.sub   { stroke-width: 3; }   /* 9–10 px sub-labels */
```

The width is sized to **cover the widest edge line in the diagram plus 2 px of headroom**. For 1.5 px stroke edges the 4 px halo gives roughly 1.25 px of clean canvas on either side of each glyph — enough to feel deliberate without looking pillowy.

No chip rects. No rounded boxes around text. The text-border is the only label background mechanism.

## Icon + text layout (component boxes)

When a component box has an icon in its left padding, the box's label **must not centre on the full box width** — the centred text slides under the icon and intersects it. Two correct patterns:

**A. Right-shifted centre — preferred for short labels:**
```
icon_left  = box_x + 16            # 16 px left padding
icon_right = icon_left + icon_size # `size` attr on the icon
text_x     = (icon_right + 8 + box_right) / 2     # centre the *available* space
text-anchor= "middle"
```

**B. Left-aligned — preferred for long or multi-line labels:**
```
text_x     = icon_right + 8        # 8 px gap between icon and first glyph
text-anchor= "start"
```

**Wrong pattern (causes visible icon/text intersection):**
```
text_x     = box_cx                # centres across whole box, overlays the icon
text-anchor= "middle"
```

Minimum reserved horizontal space on the icon side: `icon_size + 16 px`. For a 20 px icon that's a 36 px guard before any text starts. Same rule mirrored when icons sit on the right edge; vertical guard for top-positioned icons is `icon_size + 8 px`.

## Hover interactivity (optional but recommended)

The canonical `template.html` ships hover CSS so each component box gains a subtle coloured glow when the cursor enters it. To opt in, add the `component` class plus one semantic color class to every component `<rect>`:

```svg
<rect class="component emerald" x="..." y="..." width="..." height="..." rx="2"
      fill="rgba(6,78,59,0.4)" stroke="#34d399" stroke-width="1.5"/>
```

Hover effect (already in the template's `<style>`):

```css
svg rect.component {
  transition: filter 220ms ease;
  cursor: pointer;
}
svg rect.component:hover {
  filter: drop-shadow(0 0 12px var(--glow, rgba(255,255,255,0.3))) brightness(1.15);
}
svg rect.cyan    { --glow: rgba( 34, 211, 238, 0.65); }
svg rect.emerald { --glow: rgba( 52, 211, 153, 0.65); }
svg rect.violet  { --glow: rgba(167, 139, 250, 0.65); }
svg rect.rose    { --glow: rgba(251, 113, 133, 0.65); }
svg rect.amber   { --glow: rgba(251, 191, 36, 0.65); }
svg rect.slate   { --glow: rgba(148, 163, 184, 0.50); }
```

**Where hover works:**
- Diagrams generated by the `architecture-diagram` skill (standalone HTML) — works always.
- The `architecture-diagram-react` skill output, when the host site renders inline `<svg>` — works.
- Example SVGs opened directly in a browser — works.
- Example SVGs displayed via `<img src="...svg">` (e.g. on the GitHub README) — **does not work**, browsers strip CSS interactivity from `<img>` SVGs. This is expected; the README is preview, the interactive copy lives at the file URL.

<!-- (former "Label chip backgrounds" section removed in v2 — labels are
text-only with knockout halo; no chip rects anywhere. See Text-border above
and Labels — default and leader-line below.) -->

## Semantic component colors

Pick the color by what the component *is*, not by visual aesthetic:

| Component type | Fill (rgba) | Stroke (hex) | Examples |
|---|---|---|---|
| Frontend | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) | React app, mobile client, web dashboard |
| Backend / service | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) | API server, worker, gRPC service |
| Database / store | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) | Postgres, Redis, S3, SIEM |
| Cloud edge / LB | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) | Cloudflare, AWS CloudFront, ALB, NAT |
| Security / IDP / KMS | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) | Keycloak, KMS, HSM, OAuth provider |
| External / generic | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) | User, third-party API, unknown |
| Message bus | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) | Kafka, NATS, RabbitMQ, SQS |

To mask arrows passing behind a semi-transparent box, draw an opaque background rect first:

```svg
<!-- Opaque background so arrows don't show through -->
<rect x="X" y="Y" width="W" height="H" rx="2" fill="#0f172a"/>
<!-- Styled component on top -->
<rect x="X" y="Y" width="W" height="H" rx="2"
      fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
```

## Shapes

- Component boxes: `rect rx="2"` rounded corners, 1.5 px stroke
- Storage / database: `shape=cylinder` (or rect with note label)
- KMS / HSM: hexagon (`<polygon>`) for distinction
- User / actor: oval (`rx="38"` for pill shape)
- Note / file: `shape=note` style — small flag corner

## Geometry constants (the small fixed sets)

| Property | Allowed values | Notes |
|---|---|---|
| Stroke width | `0.5` / `1` / `1.5` / `2` | 0.5 = grid; 1 = default edge & component border; 1.5 = emphasized edge & cluster border; 2 = critical / key material |
| Corner radius `rx` | `0` / `2` / `4` | 0 = technical raw boxes; **2 = components (default)**; 4 = clusters / regions |
| Stroke linecap / linejoin | `round` everywhere | Soft turn-joins read as engineered, not jagged |
| Arrowhead size | `8` px | Single canonical size across the diagram |
| Orthogonal edge corner radius | `12` px | Constant across the whole drawing |

If you find yourself reaching for a value outside these sets, the impulse is wrong — re-derive from geometry, don't add a new constant.

## Boundaries (clusters / regions / security groups)

| Boundary type | Stroke style | `rx` | Fill |
|---|---|---|---|
| Region / cluster (largest) | `stroke-width="1.5"`, `stroke-dasharray="8,4"` | `4` | Subtle tint of zone color (0.05 opacity) |
| Sub-group within cluster | `stroke-width="1"`, `stroke-dasharray="6,3"` | `4` | Very subtle tint (0.04) |
| Security group | `stroke-width="1"`, `stroke-dasharray="4,3"` | `4` | Transparent, rose stroke `#fb7185` |
| Process group / node-pair | `stroke-width="1"`, `stroke-dasharray="4,3"` | `4` | Transparent, slate stroke `#475569` |

Cluster labels are placed *on* the dashed boundary at top-left. The universal text-border halo masks the dashed stroke cleanly around the label glyphs — no separate chip needed.

## Edge endpoint distribution — fan attachments across the side

When a single box has **N arrows entering or leaving on the same side**, every arrow must get its own attach point on that side. Stacking N arrows on a single midpoint is illegible — the eye cannot follow any one of them back to its origin.

**Algorithm (apply at generation time, no tool needed):**

1. For every edge, decide which **side** of each endpoint box it attaches to (`t` / `r` / `b` / `l`). If you can pick, choose the side facing the other endpoint:
   - if `|target.cx - box.cx| ≥ |target.cy - box.cy|` → `r` if the target is to the right else `l`
   - else → `b` if the target is below else `t`
2. **Group edges by `(box, side)`.** Count `N` = number of edges in each group.
3. For each group, **sort edges by the direction they head toward** so neighbouring slots stay in natural reading order:
   - sides `l` / `r` → sort by target's `y` (ascending = top-down)
   - sides `t` / `b` → sort by target's `x` (ascending = left-to-right)
4. Assign each edge in the group a **slot index** `k = 0..N-1`. The attach point is:

   ```
   side = l      → (box.x,            box.y + box.h * (k+1) / (N+1))
   side = r      → (box.right,        box.y + box.h * (k+1) / (N+1))
   side = t      → (box.x + box.w * (k+1) / (N+1), box.y)
   side = b      → (box.x + box.w * (k+1) / (N+1), box.bottom)
   ```

5. For `N = 1` the slot lands exactly at the side midpoint — same as the simple case. For `N = 3` the slots are at `1/4`, `2/4`, `3/4` of the side length; for `N = 4` at `1/5`, `2/5`, `3/5`, `4/5`; and so on.

**Worked example.** A `KAFKA` box at `x=300, y=200, w=180, h=64` has three outbound arrows on its right side (to PROJECTOR, NOTIFIER, AUDIT SINK). Without distribution they'd all leave at `(480, 232)`. With the algorithm:

| edge | target y | k | attach point |
|---|---|---|---|
| → PROJECTOR (y=132) | 132 | 0 | (480, 216) |
| → NOTIFIER  (y=332) | 332 | 1 | (480, 232) |
| → AUDIT SINK (y=412) | 412 | 2 | (480, 248) |

Three distinct departure points, sorted top-down to match the destinations.

**When you also pass `via_y` / `via_x` (Z-shape routing)**, distribution still uses the side slots — the intermediate waypoint comes from the path generator, not from the attach point.

**Failure mode to watch for.** Two parallel edges to the *same target side* — e.g., two "READ" arrows into a DB's left side. The slot algorithm gives them distinct points, but if their source x-columns differ they may still cross visually. In that case prefer a *single bundled* edge labelled with a multiplicity (`2..*`) over two parallel lines.

## Departure and arrival are perpendicular to the box side (non-negotiable)

**An edge's first segment must move perpendicular to the side it attaches from. The last segment must arrive perpendicular to the side it attaches to.** This prevents the visually-broken case where an arrow leaves a vertical edge by moving vertically, which makes the first 10–20 px of the arrow line up on top of the box's own border.

The rule maps the two attach sides to the required shape:

| src side | dst side | Path shape | Waypoint |
|---|---|---|---|
| `r` or `l` | `r` or `l` | **H-V-H** (Z, two turns) | `via_x = (src.x + dst.x) / 2` |
| `t` or `b` | `t` or `b` | **V-H-V** (Z, two turns) | `via_y = (src.y + dst.y) / 2` |
| `r` or `l` | `t` or `b` | H-V (single turn) | none — H first, then V |
| `t` or `b` | `r` or `l` | V-H (single turn) | none — V first, then H |
| equal x or y | (any) | straight line | — |

For the two same-orientation Z-shape cases, the auto-chosen waypoint is the midpoint of the corresponding coordinate. Override only when the midpoint would cross a cluster boundary or a row of components — see the next section.

## Z-shape waypoints must clear cluster boundaries

The horizontal leg (in V-H-V) or vertical leg (in H-V-H) must **not** coincide with any cluster boundary line — if it does, the edge merges visually with the dashed cluster border and becomes unreadable.

**Rule:** `via_y` must be ≥ 12 px away from every horizontal cluster edge it would otherwise sit on. Same for `via_x` vs. every vertical cluster edge.

Procedure when picking `via_y`:

1. Start with the midpoint candidate.
2. List every horizontal cluster boundary on the canvas (each cluster contributes two: `c.y` and `c.bottom`).
3. If the candidate is within 12 px of any of them, shift the candidate to the nearer of `boundary − 12` (above) or `boundary + 12` (below), choosing whichever stays in the gap between the source and destination rows.
4. If neither shift fits, pick a different cluster boundary to bypass (route via a different corridor entirely).

Same algorithm for `via_x` vs. vertical cluster boundaries.

For diagrams where multiple cross-band edges share the same horizontal corridor, fix `via_y` per-edge with explicit offsets (`via_y = corridor_y + 4 * k` for the k-th edge), so the horizontal legs stack as visually distinct rails instead of overlapping.

## Edge routing — orthogonal only

Default routing is **orthogonal**: edges run horizontal or vertical, never diagonal. Turns are rounded with `r = 12`. The only exceptions are leader lines for displaced labels (see *Labels*).

Path templates:

```
# straight (no turn)
M x1 y1 H x2          (when y1 == y2)
M x1 y1 V y2          (when x1 == x2)

# single turn, H first then V (most common)
M x1 y1 H (x2 - r·sx) Q x2 y1, x2 (y1 + r·sy) V y2
# where sx = sign(x2 - x1), sy = sign(y2 - y1), r = 12

# single turn, V first then H
M x1 y1 V (y2 - r·sy) Q x1 y2, (x1 + r·sx) y2 H x2

# Z-shape (two turns) — split into two single-turn segments at midpoint
```

Pick H-first when the source is closer to its row neighbour, V-first when closer to its column neighbour. The goal is to keep parallel edges parallel and on shared centrelines so the eye reads them as a bus.

## Arrowhead — open V (chevron), one canonical shape

Every edge ends in an **open V chevron**: two strokes forming a 60° angle. The chevron inherits the edge's stroke colour. Filled-triangle arrowheads are explicitly rejected — too informal for a blueprint.

```svg
<marker id="ah-cyan" viewBox="0 0 10 10" markerWidth="8" markerHeight="8"
        refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
  <path d="M0,0 L9,5 L0,10" fill="none" stroke="#22d3ee"
        stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
```

Define one marker per stroke colour (`ah-cyan`, `ah-emerald`, `ah-violet`, `ah-rose`, `ah-amber`, `ah-slate`). Use `marker-end="url(#ah-X)"` matching the edge's stroke colour.

## UML line endings — opt-in when the relationship is real

Use a semantic ending **only when it carries meaning**. Default to the open-V chevron. The semantic endings:

| Ending | UML meaning | When to use |
|---|---|---|
| Open V chevron | simple association / data flow | default |
| Open triangle | generalization / inheritance | "is-a" hierarchy |
| Dashed + open triangle | realization | interface implementation |
| Filled diamond | composition | child cannot exist without parent (lifecycle owned) |
| Open diamond | aggregation | parent references child but child can outlive it |
| Dashed + open V | dependency | "uses" without owning |
| Filled circle | flow start / terminus | activity / state diagrams |

Marker definitions (defined once in `<defs>`, sized 8×8):

```svg
<marker id="end-tri-open"     viewBox="0 0 10 10" markerWidth="8" markerHeight="8" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
  <path d="M0,0 L9,5 L0,10 Z" fill="#020617" stroke="#94a3b8" stroke-width="1.2"/>
</marker>
<marker id="end-diamond-filled" viewBox="0 0 10 10" markerWidth="10" markerHeight="8" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
  <path d="M0,5 L5,0 L10,5 L5,10 Z" fill="#94a3b8" stroke="#94a3b8" stroke-width="1"/>
</marker>
<marker id="end-diamond-open"   viewBox="0 0 10 10" markerWidth="10" markerHeight="8" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
  <path d="M0,5 L5,0 L10,5 L5,10 Z" fill="#020617" stroke="#94a3b8" stroke-width="1"/>
</marker>
<marker id="end-dot-filled"     viewBox="0 0 10 10" markerWidth="6" markerHeight="6" refX="5" refY="5" orient="auto" markerUnits="strokeWidth">
  <circle cx="5" cy="5" r="3" fill="#94a3b8"/>
</marker>
```

The `fill="#020617"` on open shapes is the canvas colour, so the marker reads as outline-only against the dark background.

## Edge dash semantics

| Dash | Semantic | `stroke-dasharray` | `stroke-width` |
|---|---|---|---|
| Solid | data plane / synchronous call | none | 1 |
| Dashed (5,3) | control plane (config push, xDS, gRPC config) | `5,3` | 1 |
| Dashed (3,3) | auth / token / credential flow | `3,3` | 1 |
| Dashed (2,3) | egress / external API call | `2,3` | 1 |
| Dotted (1,3) | audit / observability log | `1,3` | 0.5 |
| Bold solid | key / secret material flow | none | 2 |
| Dashed (4,3) | internal store I/O | `4,3` | 1 |

Colour the line by destination role (cyan to a frontend, emerald to a service, etc.) unless the semantic dash already implies a colour (rose for auth/key, violet for audit).

## Labels — default and leader-line

Two styles. Pick by whether the label can fit *on* the line it labels.

**No chip rects, no rounded boxes around text — ever.** The universal text-border halo (solid canvas-colour stroke, 4 px wide) is what creates the visible background. Two styles below use the same halo and differ only in how they associate the label with its referent.

### Default — text only

The label sits directly ON or NEAR its edge. The text-border knockout halo masks the underlying line through the glyphs cleanly — no underline, no chip, no leader. Visual association comes from proximity to the edge (or to the box, for component labels).

```svg
<!-- centred label on a horizontal edge at y=190 -->
<text x="cx" y="y - 1" text-anchor="middle" fill="#cbd5e1" font-size="11">HTTPS</text>
```

No `<rect>`, no `<line>` underline. The halo IS the background.

### Callout — when the label needs to point at a distant referent

In engineering drawing parlance this is a *callout* or *footnote*. Use it **only** when the label cannot sit on or adjacent to its referent: the referent is across the diagram, the local edge is too crowded, or several adjacent edges would all want a label in the same place.

A callout is text + a horizontal "shelf" + a diagonal leader stroke ending in a small dot, oblique tick, or open chevron at the referent (ISO 128-24, leader-line terminator):

```svg
<!-- "LABEL" sitting in clear space, pointing at target (tx, ty) -->
<text x="lx" y="ly" font-size="11">LABEL</text>
<line x1="lx"      y1="ly + 3" x2="lx + w"  y2="ly + 3"
      stroke="#94a3b8" stroke-width="0.75"/>           <!-- shelf -->
<line x1="lx + w"  y1="ly + 3" x2="tx"      y2="ty"
      stroke="#94a3b8" stroke-width="0.75"/>           <!-- leader -->
<circle cx="tx" cy="ty" r="1.2" fill="#94a3b8"/>      <!-- terminator -->
<!-- where w = len(text) × font-size × 0.6 -->
```

Use callouts sparingly. **If more than ~3 callouts appear in a diagram, the layout is wrong, not the labelling** — put the labels back on the edges and re-route the edges so labels fit.

### Titles, legends, zone headings — same rule

Top-of-diagram titles, subtitles, and zone headings are text-only with the knockout halo. No chips, no underlines. Use `class="title"` for the heading-weight halo (6 px stroke) and `class="sub"` for the smaller subtitle (3 px).

## Spacing rules (the most violated, the most important)

### Between root-level blocks

**3× minimum** the default gap of a typical diagram tool. Root-level blocks include: customer zone, edge / CDN zone, control plane, region(s), external dependencies.

Recommended vertical gaps:
- Top context band → control plane: 100 px
- Control plane → fan-out indicator: 80 px
- Fan-out → region detail: 80 px
- Region detail → legend: 100 px

If the diagram looks "crowded," the answer is almost always more whitespace.

### Within clusters

- 40 px between adjacent component boxes
- 60–80 px between adjacent sub-group clusters
- 20–30 px from cluster border to first component inside

### Component box internals

- 20–30 px top padding for cluster title
- Component name (12 px font) goes at `y = top + 22`
- First sub-label at `y = top + 42`
- Each subsequent sub-label adds 16 px
- Last line should have 14+ px of bottom padding inside the box

## Layout patterns

### Three-band layout

Default starting layout for system architecture:
1. **Top band** — context (users, external services, edge)
2. **Middle band** — your system (control plane, application services)
3. **Bottom band** — detail (regional data plane, per-tenant zoom, or downstream integrations)

Bands are stacked vertically with big gaps. Each band can be subdivided horizontally.

### Sub-group quadrants

When a cluster has more than ~4 components, partition into 2×2 sub-groups. Example for a control plane:
- Top-left: API services (Admin API, xDS server, OAuth worker)
- Top-right: Identity & security (IDP, KMS)
- Bottom-left: Storage (Postgres, Redis behind DAL)
- Bottom-right: Audit & observability (SIEM)

Each sub-group has its own dashed boundary and title.

### Blue/green pair pattern

For showing rolling deployments or migration mechanics, draw two equal-sized sub-clusters side-by-side, one in cyan-tinted background, one in emerald-tinted. Show one tenant on each to convey concurrent state.

## Cards under the diagram

Below the SVG, render 2–3 information cards in a CSS grid. Each card has:
- A colored dot indicating which part of the diagram it relates to
- A short H3 title
- A 4–6 item bulleted list

Cards explain things that don't fit on the diagram itself: trade-offs, constraints, design rationale.

## Toolbar (always present)

Top-right of the header, a `⋯` toggle reveals three export buttons:
- 📋 Copy — high-DPI PNG to clipboard
- 🖼️ PNG — high-DPI PNG download
- 📄 PDF — PNG embedded in one-page PDF via jsPDF

Implementation in `template.html`. Uses html2canvas with `scale: 2`, captures `#report-container` + 32 px padding, ignores the toolbar itself via `ignoreElements`.

## Footer

Single line, slate-700, 0.75 rem font. Format:

```
ProjectName · diagram name · YYYY-MM-DD · companion to <related-spec>
```

## What this design system is NOT

- Not a generic "infographic" style. Diagrams are technical artifacts; they should look serious.
- Not a "flat design" minimalism. Components have semi-transparent fills, halos, dashed boundaries — texture matters for distinguishing layers.
- Not light-theme. Dark theme is non-negotiable. Auditor screenshots, sales decks, technical blog posts all benefit from dark backgrounds for screen viewing.
- Not vector-graphic abstract. Real technical content (IP addresses, hostnames, version numbers) goes on the diagram. No mystery boxes labeled "Service".
