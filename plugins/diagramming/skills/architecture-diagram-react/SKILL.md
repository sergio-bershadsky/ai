---
name: architecture-diagram-react
description: Use when the user wants to embed an architecture diagram directly inside a React/Vite site as inline SVG (no html2canvas, no external scripts, no separate HTML file). Produces an `arch-diagram` fenced markdown block that the site's React renderer expands — including `<lucide-icon>` placeholders for semantic icons. Companion to the `architecture-diagram` skill, which produces standalone HTML.
---

# Architecture Diagram — React/Inline-SVG Embedding

This is the **embedded** counterpart to the `architecture-diagram` skill. The parent skill ships a self-contained `.html` file with its own toolbar, html2canvas/jsPDF CDN scripts, summary cards, and footer. This skill produces a leaner artifact suited for direct embedding inside a React-rendered markdown page: a fenced markdown block whose body is inline `<svg>` augmented with `<lucide-icon>` placeholders.

The runtime renderer lives in the consumer repo (see "Consumer contract" below). The React component provides the chrome (frame, FIG label, copy/save toolbar, slate-950 grid background, JetBrains Mono surface) — so the SVG you emit must contain **only the diagram itself**, not the chrome.

## What triggers this skill

- "Embed this diagram inside the blog post"
- "Generate the SVG for an `arch-diagram` block"
- "Make a React-embedded version of the architecture diagram"
- Any request where the user wants the diagram **inline in a page**, not as a downloadable HTML file
- Follow-on to the `architecture-diagram` skill when the user says "now put this on the site"

If the user wants a shareable standalone artifact (Slack, PDF, slides), use the parent `architecture-diagram` skill instead.

## Workflow

1. **Read** the parent skill's [`design-system.md`](../architecture-diagram/resources/design-system.md) and [`label-placement.md`](../architecture-diagram/resources/label-placement.md). Every rule there still applies: semantic colors, JetBrains Mono sizes, halos, label-placement priority, 40 px minimum gaps, 100–200 px between bands. **None of those rules are duplicated here.**
2. **Produce the SVG** following those rules — `viewBox`, component rects, arrows, halos, leader lines.
3. **Convert to embedded form** — strip everything that belongs to the standalone HTML chrome (see "What to strip" below).
4. **Add the metadata comment** — `<!-- fig: ... | title: ... | label: ... -->` as the first line inside the fence.
5. **Promote icons to `<lucide-icon>` placeholders** wherever a component box would benefit from a recognisable glyph (see "Lucide icon promotion" below).
6. **Run the audit** if available — `audit-labels.py` works on raw SVG too; pipe the fenced-block body to it.
7. **Output** as a single fenced markdown block tagged `arch-diagram`.

## Output contract — the fenced block

````markdown
```arch-diagram
<!-- fig: 2.1 | title: REQUEST FLOW | label: SYSTEM -->
<svg viewBox="0 0 1000 400" xmlns="http://www.w3.org/2000/svg">
  ...everything from <defs> through every <rect>, <path>, <text>, <lucide-icon>...
</svg>
```
````

- **Fence language: `arch-diagram`** — the React renderer keys off this exact tag.
- **Metadata comment is the first line** inside the fence. Fields are pipe-separated `key: value`. Recognised keys:
  - `fig` — appears as `FIG {fig}` in the chrome (e.g., `2.1`, `A`, `3`)
  - `title` — uppercase title shown after `FIG x //`
  - `label` — small right-aligned tag (e.g., `SYSTEM`, `CONTROL_PLANE`, `AUTH`)
  - All three are optional; defaults are `A` / `ARCHITECTURE` / `ARCH_V2`.
- **Body must start with `<svg>`** (after the metadata comment). The renderer's auto-detection looks for `<svg` after the comment. If the body doesn't begin with `<svg`, the renderer treats it as ordinary code.

## What to strip from a standalone-HTML diagram

When converting output of the parent skill to embedded form, **remove**:

| Strip | Why |
|---|---|
| `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>` | Renderer is inside a React tree |
| Google Fonts `<link>` | Surface already loads JetBrains Mono via `font-family` |
| html2canvas + jspdf `<script>` tags | Renderer provides Copy/Save via React |
| `.toolbar`, `.toolbar-toggle`, `.toolbar-actions` markup + CSS | Chrome is the React component's job |
| `.container`, `.header`, `.header-row`, `.pulse-dot`, `.subtitle` | Chrome — frame + FIG label come from React |
| `.summary-cards`, `.card`, footer divs | Embedded diagrams have no info-cards / footer |
| `copyAsImage()`, `downloadPNG()`, `downloadPDF()` scripts | Replaced by React Copy/Save |
| `@media print { ... }` | Not applicable inside an SPA page |
| Page-level `body { padding: 2rem; ... }` styles | Renderer controls outer padding |

**Keep:**

- The whole `<svg>` block: `<defs>`, `<pattern>`, `<marker>`, all `<rect>`/`<path>`/`<line>`/`<polyline>`/`<text>` elements, arrow leader lines, halo styles inlined as SVG attributes.
- **Halos must move from CSS into inline SVG attrs** since the renderer doesn't ship the global `svg text { paint-order: stroke fill; ... }` selector. Each `<text>` that needs a halo must carry its own `paint-order="stroke fill"`, `stroke="rgba(2, 6, 23, 0.5)"`, `stroke-width="3"`. The renderer adds nothing to text — what you emit is what renders.
- Background grid pattern is optional — the renderer surface already paints a slate-950 + 40 px grid. If the SVG also draws one, it just doubles up; usually safe to omit.

## Lucide icon promotion

Replace bespoke icon `<path>` blocks with `<lucide-icon>` tags. The React renderer expands these at runtime via `lucide-react`, so authoring stays compact and icons match the rest of the site.

**Syntax:**

```html
<lucide-icon name="database" x="56" y="56" size="20" color="#a78bfa" stroke-width="2"/>
```

- `name` — required; one of the supported names below. Unknown names are silently stripped at render time, so prefer the parent skill's bespoke SVG over an unsupported guess.
- `x`, `y` — top-left of the icon's 24×24 box in SVG user units (default `0`).
- `size` — pixel size of the bounding box (default `24`; expansion scales by `size/24`).
- `color` — stroke color (default `currentColor`); use the **stroke** colour of the surrounding component box from the semantic palette.
- `stroke-width` — default `2`. Use `1.5` when the icon sits inside a small (≤60 px) component box; default for ≥80 px.

**Supported names** (32 total, from `client/src/components/markdown/archDiagramIcons.ts` in the consumer repo):

`activity`, `bell`, `box`, `boxes`, `cloud`, `code`, `cog`, `container`, `cpu`, `database`, `file-code`, `git-branch`, `globe`, `hard-drive`, `key`, `key-round`, `layers`, `lock`, `mail`, `message-square`, `monitor`, `network`, `search`, `server`, `shield`, `smartphone`, `terminal`, `user`, `users`, `webhook`, `workflow`, `zap`.

**Recommended mapping** (extend the parent skill's semantic colors with semantic glyphs):

| Component type | Stroke color | Recommended icon |
|---|---|---|
| Frontend / web client | `#22d3ee` cyan | `monitor`, `smartphone`, `globe` |
| Backend / service | `#34d399` emerald | `server`, `cog`, `workflow`, `box`, `container` |
| Database / store | `#a78bfa` violet | `database`, `hard-drive`, `layers` |
| Cloud edge / LB / CDN | `#fbbf24` amber | `cloud`, `network`, `globe` |
| Security / IDP / KMS | `#fb7185` rose | `shield`, `lock`, `key`, `key-round` |
| Message bus / events | `#fb923c` orange | `zap`, `webhook`, `activity` |
| External / generic | `#94a3b8` slate | `box`, `boxes`, `mail`, `bell` |
| Compute / worker | `#34d399` emerald | `cpu`, `terminal`, `code`, `file-code` |
| Search / index | `#a78bfa` violet | `search` |
| Identity / user | `#94a3b8` slate | `user`, `users` |
| VCS / pipeline | `#34d399` emerald | `git-branch`, `workflow` |

If no listed icon fits, **don't invent one** — author the path inline as the parent skill does. Adding a name to the consumer requires editing `archDiagramIcons.ts` (the icon must be imported from `lucide-react`).

**Placement convention inside a component box:**

```html
<!-- 180×80 component box, icon in top-left padding (16,16 from top-left) -->
<rect x="40" y="40" width="180" height="80" rx="6"
      fill="rgba(6,78,59,0.4)" stroke="#34d399" stroke-width="1.5"/>
<lucide-icon name="server" x="56" y="56" size="20" color="#34d399"/>
<text x="130" y="76" fill="white" font-size="12" font-weight="600"
      text-anchor="middle">API GATEWAY</text>
<text x="130" y="92" fill="#94a3b8" font-size="9" text-anchor="middle">
  AUTHN / RATE-LIMIT
</text>
```

The 20 px icon at `(x+16, y+16)` from the box's top-left leaves room for a centred label on the right two-thirds of the box. For small (≤80 px wide) boxes, drop the sublabel; for tall boxes, centre the icon above the label using `text-anchor="middle"` and place the icon at `(box_cx - 10, box_y + 12)`.

## Consumer contract

The renderer in the consumer repo (this site) lives at:

- `client/src/components/markdown/ArchDiagram.tsx` — frame, toolbar, sanitization, render.
- `client/src/components/markdown/archDiagramIcons.ts` — `<lucide-icon>` expansion + supported-name allowlist.
- `client/src/components/markdown/CodeBlock.tsx` — trigger: `language-arch-diagram` className **or** auto-detected leading `<svg>` (after optional metadata comment).

The renderer:

1. Parses the `<!-- ... -->` metadata comment off the front.
2. Runs `expandLucideIcons()` over the body, replacing `<lucide-icon ... />` with positioned/scaled `<g>` groups containing real Lucide paths.
3. Sanitizes through DOMPurify's SVG profile.
4. Paints the body inside an accent-bordered frame with slate-950 grid background, JetBrains Mono font-family, and a `COPY_SVG` / `SAVE` toolbar.

**What this means for what you emit:**

- You cannot use `<script>` — sanitizer strips it.
- You cannot use `<foreignObject>` — both unsupported in html2canvas (parent skill rule) and stripped by the SVG profile.
- You cannot rely on external CSS — every style must be an SVG attribute or inline `style="..."`.
- You **can** use `<defs>`, `<pattern>`, `<marker>`, `<linearGradient>`, `<radialGradient>`, `<clipPath>`, `<mask>` — all in the SVG profile allowlist.

## Audit

Run the parent skill's audit script on the fenced-block body. Extract everything from `<svg` to `</svg>` and feed it in:

```bash
sed -n '/^<svg/,/<\/svg>/p' diagram-body.txt > /tmp/diagram.svg
python3 ${CLAUDE_PLUGIN_ROOT}/skills/architecture-diagram/resources/audit-labels.py /tmp/diagram.svg
```

If the audit flags labels for being far from the arrow midpoint without a leader line, fix them per the parent skill's algorithm.

## What you must not do

- ❌ Don't emit a full `<html>` document — only the fenced block.
- ❌ Don't include `<script>`, `<link>`, `<style>` outside `<defs>` — sanitizer strips them anyway.
- ❌ Don't omit halos on overlapping text — the React surface doesn't add them globally; each `<text>` must carry its own halo attrs where needed.
- ❌ Don't invent unsupported `<lucide-icon>` names — they silently disappear.
- ❌ Don't double-paint the grid — the React surface already provides slate-950 + 40 px grid; only repeat if the diagram needs a different grid density inside.
- ❌ Don't reach for `<foreignObject>` for rich labels — text + halo is the supported path.

## Minimal example

````markdown
```arch-diagram
<!-- fig: 1 | title: HELLO WORLD | label: DEMO -->
<svg viewBox="0 0 600 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
    </marker>
  </defs>

  <rect x="40" y="60" width="180" height="80" rx="6"
        fill="rgba(8,51,68,0.4)" stroke="#22d3ee" stroke-width="1.5"/>
  <lucide-icon name="monitor" x="56" y="76" size="20" color="#22d3ee"/>
  <text x="130" y="96" fill="white" font-size="12" font-weight="600"
        text-anchor="middle"
        paint-order="stroke fill" stroke="rgba(2,6,23,0.5)" stroke-width="3">CLIENT</text>

  <line x1="220" y1="100" x2="380" y2="100"
        stroke="#64748b" stroke-width="1.5" marker-end="url(#ah)"/>
  <text x="300" y="92" fill="#cbd5e1" font-size="9" text-anchor="middle"
        paint-order="stroke fill" stroke="rgba(2,6,23,0.5)" stroke-width="3">HTTPS</text>

  <rect x="380" y="60" width="180" height="80" rx="6"
        fill="rgba(6,78,59,0.4)" stroke="#34d399" stroke-width="1.5"/>
  <lucide-icon name="server" x="396" y="76" size="20" color="#34d399"/>
  <text x="470" y="96" fill="white" font-size="12" font-weight="600"
        text-anchor="middle"
        paint-order="stroke fill" stroke="rgba(2,6,23,0.5)" stroke-width="3">API</text>
</svg>
```
````

## Attribution

This skill is the React/inline-SVG embedding companion to the `architecture-diagram` skill (which itself extends the [Cocoon AI architecture-diagram skill](https://github.com/Cocoon-AI/architecture-diagram-generator), MIT). All design-system rules — colors, fonts, halos, label placement, spacing — come from the parent skill; this skill only documents the format conversion and consumer contract.
