---
name: architecture-diagram
description: Use when the user asks for a system, infrastructure, cloud, security, network topology, or architecture diagram. Produces polished dark-themed self-contained HTML+SVG files with mathematically-correct label placement, clean-background priority, text halos, and leader lines.
---

# Architecture Diagram Skill

Generate professional technical architecture diagrams as self-contained HTML files with inline SVG graphics, CSS styling, and a built-in export toolbar (PNG / PDF / Copy-to-clipboard).

Built on top of the Cocoon-AI architecture-diagram design system (MIT licensed), extended with hard-won label-placement rules from real diagram production work.

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

## The four most important rules

1. **Label placement: clean background beats geometric midpoint.** Don't put labels at the Bezier midpoint just because the math says so. Find empty visual space the size of the label and put the label there. Use leader lines if needed. See `resources/label-placement.md` for the full algorithm. This rule comes from real user feedback after generating diagrams where strict-midpoint placement produced unreadable visual chaos.
2. **3× spacing between root-level blocks.** Generous padding around every cluster. Default gap between major bands is 100–200 px, not 30 px. Visual hierarchy depends on whitespace.
3. **Floating labels sit in chip rects.** Every label that does not live inside a coloured component box (titles, edge labels, cluster names, annotations) needs an explicit background `<rect>` drawn just before the `<text>`: `fill="rgba(15, 23, 42, 0.92)" stroke="rgba(148, 163, 184, 0.75)" stroke-width="1" rx="3"`. The universal text halo (`paint-order: stroke fill; stroke: rgba(2, 6, 23, 0.75); stroke-width: 1`) stays as defence-in-depth. See `resources/design-system.md` § *Label chip backgrounds*.
4. **Sub-group clusters within larger clusters.** When a logical group has more than ~4 components, partition them into 2–4 named sub-groups with their own dashed boundaries.
5. **Reserve icon space before placing text.** When a component box has an icon in the left padding, the label must NOT centre on the full box — it will slide under the icon. Either centre the text in the space *right of the icon* (`text_x = (icon_right + 8 + box_right) / 2`, `text-anchor="middle"`) or left-align at `icon_right + 8`. Required guard: `icon_size + 16 px` of horizontal space before any text glyph. Same rule mirrored for right-/top-positioned icons. See `resources/design-system.md` § *Icon + text layout*.

## Workflow

1. **Read the design system** — `resources/design-system.md` for colors, fonts, spacing, component patterns.
2. **Read the label-placement rules** — `resources/label-placement.md` for the math + clean-background principle.
3. **Sketch the layout** in 3 horizontal bands minimum: top context (customer/external), middle (your system), bottom (downstream/integrations or detail). Estimate width per box, decide on viewBox dimensions.
4. **Build from `template.html`** — copy and customise. Always preserve the header, toolbar, capture script, halo CSS.
5. **Place components** with adequate padding (40 px between boxes, 80 px between sub-groups).
6. **Place arrows** with proper labels: compute Bezier midpoint first, then look for clean background nearby. If clean space is far from midpoint, use leader line.
7. **Run the audit** — `resources/audit-labels.py <file>.html` reports any label > 50 px from its arrow's midpoint and lacking a leader line.
8. **Render in browser** to verify visually. Iterate on placements.
9. **Output the final file** as `<name>-architecture.html` in the user's docs directory.

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

After generating a diagram, run the audit script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/architecture-diagram/resources/audit-labels.py <file>.html
```

Output flags any arrow label whose position is > 50 px from its arrow's curve midpoint **without** a connecting leader line. Each flag is either:
- Fixable: move label closer or add leader line
- By design: endpoint annotation (label sits near arrow head, separate leader line connects them)

The audit reports each issue with the distance and the relevant line numbers.

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

This skill is derived from and extends the [Cocoon AI architecture-diagram skill](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT license), with significant additions for label placement, audit tooling, and coordinate manipulation based on production diagram work for Socket0 Connect.
