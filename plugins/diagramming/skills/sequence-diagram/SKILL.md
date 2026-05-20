---
name: sequence-diagram
description: Use when the user asks for a sequence diagram, ladder diagram, message-exchange diagram, or any temporal flow showing who talks to whom in order ("draw the OAuth flow", "show the request lifecycle", "diagram the protocol over time", "sequence diagram for X"). Produces dark-themed self-contained SVG with actor lifelines, sync/async/return messages, self-loops, halo text, and a geometry-audit gate that knows about lifelines.
---

# Sequence Diagram Skill

Generate UML-2.x-lite sequence diagrams as self-contained SVG files, sharing the blueprint aesthetic of the sibling `architecture-diagram` and `mindmap` skills: dark `#020617` background, JetBrains Mono, halo text, semantic palette, deterministic geometry-audit gate.

## What triggers this skill

- "Draw a sequence diagram of X"
- "Show the [OAuth | login | checkout | webhook] flow over time"
- "Ladder diagram for protocol Y"
- "Show the message exchange between A and B"
- "Activity diagram of [request]" — users frequently conflate these; default to sequence when there's a clear temporal order of messages between named actors
- Any request whose answer is "X happens, then Y, then Z" with named actors

## When to use this skill vs siblings

| You want… | Skill |
|---|---|
| Static topology — what calls what, where it lives, how it's deployed | `architecture-diagram` |
| Radial topic tree — one focal point, themes radiating out | `mindmap` |
| **Temporal sequence — who talks to whom, in what order, over time** | **`sequence-diagram`** (this one) |

Rule of thumb: if every arrow in your diagram needs a *number* to make sense, you want a sequence diagram.

## Output contract

Same as the rest of the plugin:
- Self-contained `.svg` file (or `.html` if delivering to a user with the export toolbar — copy from `../architecture-diagram/resources/template.html` and swap the SVG body).
- Dark `#020617` background, JetBrains Mono via the inline `<style>` block, halo text via `paint-order: stroke fill`.
- Geometry-audit (`../architecture-diagram/resources/geometry-audit.py`) must exit 0 before the diagram is done.

## Visual conventions (UML 2.x, blueprint-adapted)

| Element | Notation | Implementation |
|---|---|---|
| Actor box | rounded rect, semantic color | `<rect class="component <color>" rx="2">` with name + optional sub-label |
| Lifeline | dashed vertical line below actor | **`<line class="lifeline" stroke-dasharray="4,4">`** — the `lifeline` class makes the audit skip it for edge-edge / edge-crosses-component checks |
| Synchronous call | solid arrow, filled V chevron | `<path d="M src,y L tgt,y" marker-end="url(#ah-<color>)">` |
| Async call | dashed arrow, open V chevron | same path + `stroke-dasharray="5,3"` |
| Return | dashed line, open chevron, optional label | `stroke-dasharray="4,3"`, lighter stroke |
| Self-loop | right-side bump arrow | `<path d="M x,y q 32,0 32,16 T x,y+16">` with arrowhead at end |
| Activation bar (optional) | thin rect on lifeline | `<rect width="8" fill="rgba(...)">` overlapping lifeline at activation span |
| Note | halo-only text in clear space | `<text class="note">` — no chip rect |
| Numbering (optional) | small badge or prefix on label | label = `"1. login"` — simplest readable form |

### Semantic colors per actor type (reuse from architecture-diagram)

| Actor type | `kind` | Stroke |
|---|---|---|
| Human user | `slate` | `#94a3b8` |
| Frontend / SPA / mobile | `cyan` | `#22d3ee` |
| Backend service | `emerald` | `#34d399` |
| Database / store | `violet` | `#a78bfa` |
| Auth / IDP / KMS | `rose` | `#fb7185` |
| Cloud edge / LB / CDN | `amber` | `#fbbf24` |
| External system | `slate` | `#94a3b8` |

## Workflow

1. **Extract actors from the brief.** Read the user's prose; identify the distinct named participants (USER, SPA, AUTH SERVER, DB, API, …). Typical count: 3–6. Cap at 7 — beyond that, split the diagram.
2. **Extract messages in order.** Each message = (src actor, tgt actor, label, kind ∈ {sync, async, return, self}). Keep labels short — verbs preferred ("request token", "fetch user").
3. **Compute layout** (algorithm below).
4. **Emit SVG.** Actor row first, then lifelines, then messages top-to-bottom.
5. **Run geometry-audit.** Must be clean. Lifelines are now exempt from edge-edge crossings (see *Audit notes* below).

## Layout algorithm

The diagram is two zones: an **actor row** at the top, then a **message ladder** below.

### Step 1 — column widths and positions

```
N = number of actors
LEFT  = 60                  # left margin
RIGHT = 60                  # right margin
COL_W_i  = max(180, label_w_i + 40)         # per-actor; longest of name and sub-label drives width
x_i      = LEFT + sum(COL_W_j for j < i) + COL_W_i / 2     # actor center

W = LEFT + sum(COL_W) + RIGHT
```

### Step 2 — actor row

```
ACTOR_TOP    = 80
ACTOR_H      = 56
actor_box_i  = rect(x = x_i - aw_i/2, y = ACTOR_TOP, w = aw_i, h = ACTOR_H, rx = 4)
  where aw_i = max(140, label_w_i + 28)
```

Title and subtitle live above the actor row (`y = 32` and `y = 52`), same as every other diagram in this plugin.

### Step 3 — lifeline geometry

Each lifeline runs from the bottom of its actor box down to `LIFELINE_BOTTOM`:

```
LIFELINE_TOP    = ACTOR_TOP + ACTOR_H + 8           # 8 px gap below actor
LIFELINE_BOTTOM = MSG_TOP + M * ROW_H + 16          # 16 px below last message
```

Emit each lifeline as:

```html
<line class="lifeline" x1="x_i" y1="LIFELINE_TOP" x2="x_i" y2="LIFELINE_BOTTOM"
      stroke="#475569" stroke-width="1" stroke-dasharray="4,4"/>
```

**The `class="lifeline"` is required** — the geometry-audit uses this class to skip lifelines in edge-edge and edge-crosses-component checks (otherwise every horizontal message would flag).

### Step 4 — message ladder

```
MSG_TOP = LIFELINE_TOP + 24                          # first message y
ROW_H   = 36                                         # vertical gap per message
y_k     = MSG_TOP + k * ROW_H                        # k = 0..M-1
```

For each message at row k:

- **Standard message** (src ≠ tgt): straight horizontal segment from src lifeline to just-before tgt lifeline (leave 8 px on the marker side so the chevron sits inside the column, not crossing into the next).
  ```
  <path d="M src_x,y_k L tgt_x-sign(tgt-src)*8,y_k"
        stroke="<color>" stroke-width="1.4" marker-end="url(#ah-<color>)"/>
  ```
- **Self-loop** (src = tgt): bump 32 px to the right, down 16 px, back. Total vertical footprint = 16 px, fits inside one row.
  ```
  <path d="M src_x,y_k h 32 v 16 h -32"
        stroke="<color>" stroke-width="1.4" marker-end="url(#ah-<color>)"/>
  ```
  Label sits to the right of the bump: `<text x="src_x + 40" y="y_k + 4">label</text>`.
- **Sync vs async vs return** — pick from the *Visual conventions* table for line style. Different arrowhead is not required, but you can use a smaller arrowhead for returns.

### Step 5 — labels

Centered above the arrow line, with halo:

```
label.x = (src_x + tgt_x) / 2
label.y = y_k - 6
```

If `|src_x − tgt_x| < label_w + 16`, widen the source/target columns so the label fits. Don't shrink the label — verbosity here costs nothing visually.

### Step 6 — canvas height

```
H = LIFELINE_BOTTOM + 40                             # 40 px footer margin
viewBox = "0 0 W H"
```

## Audit notes

The geometry-audit has been extended (in this repo) to recognize `class="lifeline"` on `<line>` and `<path>` elements. Lifelines are:

- **Skipped** in `edge-crosses-edge` (every message crosses every lifeline — by design)
- **Skipped** in `edge-crosses-component` (lifelines shouldn't cross actor boxes anyway; if they do, the actor box layout itself is wrong)
- **Still parsed** so the audit can read them — just exempt from those two checks

Other audit classes apply normally:
- `component-overlap` — actor boxes must not overlap
- `label-overlaps-component` — message labels must not sit on an actor box
- `edge-crosses-label` — different messages' labels must not collide

If you see `edge-crosses-edge` findings in a sequence diagram, those are between **messages** (not lifelines) — typically a sign that two messages share a y-coordinate by mistake, or that a self-loop bump overlaps the next row. Fix by spacing or by re-ordering.

## Worked example

> "Show the OAuth 2.0 authorization code flow with PKCE: user clicks login on the SPA, SPA redirects to the IDP, IDP authenticates the user and stores a code in its DB, IDP redirects back with the code, SPA exchanges the code (with verifier) for a token at the IDP, IDP returns the token, SPA calls the API with the token, API verifies and returns the resource."

Extracted:
- **Actors** (5): USER (slate), SPA (cyan), IDP (rose), DB (violet), API (emerald)
- **Messages** (9): each line of the prose maps to one message in order
- One self-loop on IDP for "authenticate user" (its internal step)

See [`../../examples/14-sequence-oauth-code-flow.svg`](../../examples/14-sequence-oauth-code-flow.svg) for the rendered output.

## What you must not do

- ❌ Don't draw lifelines without `class="lifeline"` — the audit will flag every message as crossing a lifeline.
- ❌ Don't use curved Bezier paths for inter-actor messages. Sequence diagrams expect straight horizontal arrows. Bezier curves are reserved for self-loops.
- ❌ Don't crowd multiple messages on the same `y`. Spacing is what makes sequence diagrams readable.
- ❌ Don't number messages just because UML allows it. Add a number prefix only when there are skipped beats or back-references ("see 3.").
- ❌ Don't try to encode `alt`/`loop`/`par` fragments in v1. If the brief genuinely needs branching, draw two sequence diagrams (one per branch) and reference them in prose.
- ❌ Don't load external images / icons / fonts beyond the Google Fonts JetBrains Mono — same constraint as the rest of the plugin.

## Limits and when to refactor

- > 6 actors → split into two diagrams (e.g., "auth phase" + "API phase").
- > 14 messages → consider folding consecutive same-pair calls into one message with a list label.
- Many parallel branches (`par` fragment territory) → sequence diagrams aren't the right tool; use an architecture diagram with annotated edges instead.

## Attribution

Original work. Follows UML 2.x sequence-diagram semantics where applicable, blueprint-adapted to match the architecture-diagram and mindmap aesthetic in this plugin.
