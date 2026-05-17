# Arrow Label Placement — Clean Background Over Geometric Midpoint

The single most important rule of this skill. **Wrong placement makes the diagram unreadable; right placement is barely noticeable, which is the point.**

## The principle

**Fight for clean visual space.** Don't place labels at the Bezier midpoint just because the math says so. The midpoint is a *starting candidate*, not the final answer. Find empty space the size of the label and put the label there.

Priority order, highest first:
1. **Clean background under the label** — no overlap with other text, box borders, or path crossings
2. **Leader-line clarity** — if label is far from arrow, a thin dashed line connects them so the reader can trace the association
3. **Arrow-curve proximity** — closer is better, all else equal
4. **Geometric midpoint accuracy** — lowest priority

This rule comes from real production feedback. Strictly placing labels at midpoints produced unreadable diagrams. The fix isn't to recalculate the midpoint more accurately; it's to question the premise.

## Bezier midpoint math (the starting candidate, not the answer)

For a quadratic Bezier path `M Px Py Q Cx Cy Ex Ey`:

```python
def quadratic_midpoint(p0, p1_control, p2):
    """Bezier point at t=0.5: P = 0.25·P0 + 0.5·P1 + 0.25·P2"""
    t = 0.5
    x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1_control[0] + t**2 * p2[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1_control[1] + t**2 * p2[1]
    return (x, y)
```

For a straight line: midpoint is `((x1+x2)/2, (y1+y2)/2)`.

For cubic Bezier `C cx1 cy1 cx2 cy2 ex ey`:

```python
def cubic_midpoint(p0, p1, p2, p3):
    """Bezier point at t=0.5: P = 0.125·P0 + 0.375·P1 + 0.375·P2 + 0.125·P3"""
    return (
        0.125*p0[0] + 0.375*p1[0] + 0.375*p2[0] + 0.125*p3[0],
        0.125*p0[1] + 0.375*p1[1] + 0.375*p2[1] + 0.125*p3[1]
    )
```

## Label bounding box estimation

```python
def label_bbox(text, font_size=9):
    """Conservative bbox estimate for monospace text."""
    width = len(text) * font_size * 0.6
    height = font_size * 1.2
    margin = font_size  # one extra label-height of clear space on each side
    return (width, height, margin)
```

JetBrains Mono is monospace, so character-count × font-size × 0.6 is accurate. For proportional fonts use 0.5 and add buffer.

## The placement algorithm

```python
def place_arrow_label(arrow, label_text, occupied_regions, font_size=9):
    # Step 1: compute midpoint as starting candidate
    midpoint = curve_midpoint(arrow)

    # Step 2: compute label bbox
    label_w, label_h, margin = label_bbox(label_text, font_size)

    # Step 3: spiral search for clean space starting from midpoint
    for candidate in spiral_search(midpoint, step=8, max_radius=300):
        bbox = (
            candidate[0] - label_w/2 - margin,
            candidate[1] - label_h - margin,
            label_w + 2*margin,
            label_h + 2*margin
        )
        if not any_overlap(bbox, occupied_regions):
            distance = euclidean(candidate, midpoint)
            return {
                'x': candidate[0],
                'y': candidate[1],
                'anchor': 'middle',
                'needs_leader_line': distance > 30,
                'distance_from_midpoint': distance
            }

    # Step 4: fallback — accept midpoint with halo as last resort
    return {
        'x': midpoint[0],
        'y': midpoint[1],
        'anchor': 'middle',
        'needs_leader_line': False,
        'fallback': True
    }


def spiral_search(center, step=8, max_radius=300):
    """Yield points spiraling outward from center."""
    yield center
    r = step
    while r <= max_radius:
        # Sample 8 directions at this radius
        for angle_deg in (0, 45, 90, 135, 180, 225, 270, 315):
            import math
            angle = math.radians(angle_deg)
            yield (center[0] + r*math.cos(angle), center[1] + r*math.sin(angle))
        r += step
```

## Distance budget for "label belongs to arrow"

| Distance from midpoint | Required treatment |
|---|---|
| 0–30 px | No additional treatment — visually attached |
| 30–150 px | **Leader line required** (thin dashed line from label to nearest curve point) |
| > 150 px | This is an **endpoint annotation** pattern: label sits near the arrow's head or tail, leader line is mandatory and short |

## Leader line implementation

A leader line is a thin dashed line in the arrow's color, connecting the label's edge to the nearest point on the curve:

```svg
<!-- Label positioned in clear space -->
<text x="350" y="1462" fill="#22d3ee" font-size="10" font-weight="600" text-anchor="middle">
  route to 10.0.0.42:443
</text>
<!-- Leader line: from label's bottom edge to nearest curve point -->
<line x1="430" y1="1480" x2="500" y2="1500"
      stroke="#22d3ee" stroke-width="0.5" stroke-dasharray="2,2"/>
```

Properties:
- `stroke-width="0.5"` or `"1"` — thinner than the arrow itself
- `stroke-dasharray="2,2"` — short dashes to distinguish from arrow style
- Color matches the arrow's color
- Endpoint on curve side: snap to the actual curve, not a guessed point. Compute via:

```python
def nearest_point_on_curve(curve, point, samples=50):
    """Sample the curve at `samples` points and return the closest one."""
    best = None
    best_dist = float('inf')
    for t in [i/samples for i in range(samples+1)]:
        p = curve_at_t(curve, t)
        d = euclidean(p, point)
        if d < best_dist:
            best, best_dist = p, d
    return best
```

## Text halo (defence-in-depth)

For unavoidable small overlaps with backgrounds, use SVG `paint-order: stroke fill` to render a semi-transparent dark stroke behind the text fill:

```css
svg text {
  paint-order: stroke fill;
  stroke: rgba(2, 6, 23, 0.75);
  stroke-width: 1;
  stroke-linejoin: round;
  stroke-linecap: round;
}
```

This is the cartographer's trick for map labels. It does **not** replace correct placement; it makes a small overlap survivable.

## Audit checklist (run after every diagram)

For each labeled arrow:
- [ ] Compute the curve midpoint
- [ ] Measure distance from label position to midpoint
- [ ] If > 30 px: verify a leader line exists
- [ ] If > 150 px: verify it's intentionally an endpoint annotation
- [ ] Check the label's bounding box does not overlap any rect, text, or path

The `audit-labels.py` script automates this. Run it after every generation.

## Common mistakes to avoid

1. **Placing the label *on* the arrow line.** The line and the text fight for the same pixels. Place above or beside the line, not on it.
2. **Putting the label inside a cluster boundary.** The cluster's own title text and border collide with arrow labels. Either move the label outside the cluster, or accept the halo will cover the overlap.
3. **Long labels with no anchor.** Set `text-anchor="middle"` or `"start"` / `"end"` explicitly. Default (`"start"`) extends to the right, often into other content.
4. **Subtitle text just below the main label.** Two-line labels need both lines placed for clean space, not just the first.
5. **Using midpoint for a path that curves sharply.** A path that goes from (0, 0) to (0, 100) via control point (200, 50) has its "geometric midpoint" at (100, 50), nowhere near the actual curve. Always plot the curve mentally.

## Why this matters

A diagram is a tool for communication. If the reader has to puzzle over which arrow a label belongs to, the diagram has failed at its job. The whole point of label-on-arrow positioning is to make associations *instant*. Anything that interferes with that instant recognition — visual chaos from overlaps, ambiguity from distance, halos cluttering text — defeats the purpose.

So: fight for clean space. Use the math as a starting point, not a constraint. And always run the audit.
