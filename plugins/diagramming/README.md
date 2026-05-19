# diagramming — Architecture Diagram Generator

Polished dark-themed architecture diagrams as self-contained HTML+SVG, with the right defaults baked in: text halos, Bezier-correct label placement with **clean-background priority**, leader lines for distant labels, semantic component colors, and a built-in export toolbar (PNG / PDF / Copy).

Built on the [Cocoon AI architecture-diagram](https://github.com/Cocoon-AI/architecture-diagram-generator) design language (MIT), extended with production-tested label-placement rules and tooling.

## Demo gallery

Five patterns the skill produces, rendered to SVG with the canonical design system. All five render in any GitHub view — sources live in [`examples/`](./examples/).

### 1. Three-tier request flow

The minimum viable diagram — external user, edge, compute, storage — illustrating semantic palette (slate / cyan / emerald / violet) and edge dash semantics (solid HTTPS, solid gRPC, dashed SQL).

![Three-tier request flow](./examples/01-client-api-db.svg?v=6)

### 2. Service mesh — xDS control plane / Envoy data plane

Two-cluster layout demonstrating **control plane vs data plane** convention: dashed cyan lines push xDS config, solid emerald lines carry mTLS request traffic. Sub-groups (`pod-a/b/c`) inside the data-plane cluster show two-level nesting.

![Service mesh — xDS / Envoy](./examples/02-service-mesh-xds.svg?v=6)

### 3. OAuth2 / JWT flow with security boundary

Rose dashed lines mark every auth/token edge; a rose-bordered dashed cluster wraps the server-side trust zone. Shows how to keep many short same-coloured edges legible by alternating label sides (above the line / below the line).

![OAuth2 / JWT flow](./examples/03-oauth-flow.svg?v=6)

### 4. Event-driven CQRS with audit stream

Demonstrates three edge semantics in one diagram: solid emerald (synchronous command), amber dashed (pub/sub fan-out), and violet dotted-thin (audit tap). The audit stream visibly recedes — exactly what the dotted-thin convention is for.

![Event-driven CQRS](./examples/04-event-driven-cqrs.svg?v=6)

### 5. Multi-tenant credentials — KMS-wrapped at rest

The strongest stress-test of the design system: nested control-plane / data-plane regions, **bold rose** lines reserved for key material (KMS Encrypt/Decrypt), an inner rose dashed boundary marking the *only* place plaintext lives (RAM-only xDS agent). Label routing avoids cluster borders and the central KMS box.

![Multi-tenant KMS](./examples/05-multi-tenant-kms.svg?v=6)

### 6. Corner-disc icon annotations

Opt-in glyphs anchored to the top-left of selected component boxes. The disc fill matches the box's stroke colour; the stencil glyph inside is drawn in canvas colour. Inside-box label is right-shifted per the icon-space rule. Discs are never emitted by default — the user must request them per box.

![Icon annotations](./examples/06-icon-annotations.svg?v=6)

---

## What you get

- **Two skills** — same design system, two output formats. Pick by where the diagram needs to live:

  - **`architecture-diagram`** — generates a **standalone self-contained `.html` file** from a natural-language description.
    *Use when:* you want a single artifact you can open in a browser, share via email/Slack, attach to a design spec, export as PDF/PNG for an investor deck, drop into a GitHub gist, or include alongside a spec in a docs repo. Output is portable, has zero runtime dependencies, and ships with its own export toolbar.
    *Trigger phrases:* "draw an architecture diagram", "generate a system diagram as HTML", "make me a network topology diagram I can share".

  - **`architecture-diagram-react`** — emits the same diagram as an **`arch-diagram` fenced markdown block** (inline SVG + `<lucide-icon>` placeholders) intended for direct embedding in React/Vite/Next.js sites and MDX-aware documentation platforms (Docusaurus, Nextra, VitePress, MkDocs with the right plugin).
    *Use when:* the diagram is going inside a content page rendered by a React/MDX pipeline — a docs site, marketing site section, internal portal, or a tech-blog post in a content repo. Lucide icons render as live React components rather than baked-in SVG, letting the consuming app theme and animate them.
    *Trigger phrases:* "embed an architecture diagram in our docs site", "add a system diagram to the React app", "MDX-friendly architecture diagram", "diagram with Lucide icons".

  Same skill mechanics underneath — design system, label placement rules, audit and shifter scripts apply to both. The choice is purely about output format.
- **Resources**:
  - `template.html` — canonical starting point, complete with halos, toolbar, capture script
  - `design-system.md` — colors, fonts, shapes, spacing, semantic line styles
  - `label-placement.md` — the math + clean-background principle + leader-line implementation
  - `audit-labels.py` — verifies label placement after generation
  - `coordinate-shifter.py` — bulk-shifts y-coordinates to add space between blocks

## The one rule everyone forgets

When placing arrow labels: **fight for clean visual space over geometric correctness**.

The Bezier midpoint is a starting candidate. If the midpoint lies on top of cluster borders, other text, or path crossings, **move the label** to nearby clean space and connect it back with a thin leader line. Halos help with unavoidable overlaps but should not be the strategy.

Priority order:
1. Clean background under the label
2. Leader-line clarity (so the reader can trace label → arrow)
3. Arrow-curve proximity
4. Geometric midpoint accuracy (lowest)

See `skills/architecture-diagram/resources/label-placement.md` for the full algorithm and audit checklist.

## Tools

### Audit a generated diagram

```bash
python3 plugins/diagramming/skills/architecture-diagram/resources/audit-labels.py mydiagram.html
```

Flags any arrow label more than 30 px from its arrow's midpoint without a connecting leader line.

### Add breathing room between blocks

```bash
python3 plugins/diagramming/skills/architecture-diagram/resources/coordinate-shifter.py mydiagram.html \
    --tiers "260:120,985:60,1700:90"
```

Shifts y-coordinates in tiers. The `boundary:delta` pairs say: at this y-boundary, add this delta to all coordinates at or above it. ViewBox is grown automatically.

## Output contract

Every diagram produced by this skill:
- Is a single self-contained `.html` file
- Embeds all CSS inline (only Google Fonts as external)
- Embeds all SVG inline (no external images)
- Renders identically opened in any modern browser
- Has working PNG / PDF / Copy export buttons (using html2canvas + jsPDF from CDN with SRI hashes)
- Uses the dark theme `#020617` background even in PDF export
- Has halos on all text

## License

Unlicense (this plugin). The underlying Cocoon AI design system is MIT-licensed.
