# Architecture Diagram Design System

Dark-theme, monospace-typography, semantic-color diagrams. Built on the Cocoon-AI design language. Use this as the canonical reference for every diagram produced by this skill.

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

## Text halo (universal)

Every `<text>` element in the SVG renders with a semi-transparent dark stroke behind its fill:

```css
svg text {
  paint-order: stroke fill;
  stroke: rgba(2, 6, 23, 0.5);
  stroke-width: 3;
  stroke-linejoin: round;
  stroke-linecap: round;
}
svg text.heading { stroke-width: 4; }
svg text.label-tiny { stroke-width: 2.5; }
```

This makes labels readable when they unavoidably overlap with cluster boundaries, other boxes, or arrows. It is not a substitute for correct placement; it's defence-in-depth.

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
<rect x="X" y="Y" width="W" height="H" rx="6" fill="#0f172a"/>
<!-- Styled component on top -->
<rect x="X" y="Y" width="W" height="H" rx="6"
      fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
```

## Shapes

- Component boxes: `rect rx="6"` rounded corners, 1.5 px stroke
- Storage / database: `shape=cylinder` (or rect with note label)
- KMS / HSM: hexagon (`<polygon>`) for distinction
- User / actor: oval (`rx="38"` for pill shape)
- Note / file: `shape=note` style — small flag corner

## Boundaries (clusters / regions / security groups)

| Boundary type | Stroke style | Fill | Color |
|---|---|---|---|
| Region / cluster (largest) | `stroke-dasharray="10,6"`, `rx="14"` | Very subtle tint of zone color (0.05 opacity) | Match zone semantics |
| Sub-group within cluster | `stroke-dasharray="6,4"`, `rx="10"` | Very subtle tint (0.04–0.08) | Match group semantics |
| Security group | `stroke-dasharray="4,4"`, `rx="8"` | Transparent | Rose `#fb7185` |
| Process group / node-pair | `stroke-dasharray="4,4"`, `rx="10"` | Transparent | Slate `#475569` |

Cluster labels go at top-left inside the boundary, with `font-size="10–13"` and bold.

## Arrow styles (semantic)

Different line styles communicate different flow types. Be consistent across the whole diagram.

| Style | Semantic meaning | SVG attributes |
|---|---|---|
| Solid | Data plane traffic (HTTPS, mTLS, raw TCP) | `stroke-width="1.5"` |
| Dashed (5,3), cyan or emerald | Control plane (xDS, gRPC config push) | `stroke-dasharray="5,3"` |
| Dashed (3,3), rose | Auth / token / key flow | `stroke-dasharray="3,3"` |
| Dashed (2,3), amber | Egress to upstream / external API | `stroke-dasharray="2,3"` |
| Dotted (1,3), violet | Audit log stream | `stroke-dasharray="1,3"`, `stroke-width="0.7"` |
| Bold solid | Key / secret material flow | `stroke-width="2"` |
| Dashed (4,3), violet thin | Internal store I/O | `stroke-width="1"`, `stroke-dasharray="4,3"` |

Always use `marker-end="url(#arrowhead-X)"` where X matches the line color. Define per-color arrowheads in `<defs>`:

```svg
<marker id="arrowhead-cyan" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#22d3ee" />
</marker>
```

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
