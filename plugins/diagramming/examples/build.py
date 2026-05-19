#!/usr/bin/env python3
"""FIXTURE GENERATOR — NOT the skill itself.

The canonical knowledge for producing blueprint diagrams lives in
    ../skills/architecture-diagram/resources/design-system.md
That document contains every algorithm the skill applies at generation
time (layout validation, multi-arrow attachment distribution, orthogonal
routing with rounded corners, knockout text-border, UML endings, etc.).

When the diagramming skill is invoked inside a Claude conversation, the
model computes geometry directly — no Python is run. This script exists
only so the five example SVGs under `examples/` can be regenerated as a
batch when the design system changes, keeping the README gallery in sync
with the spec. Maintainers run it; end users never need to.

Run from the repo root:
    python3 plugins/diagramming/examples/build.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

# Canvas + canonical constants ----------------------------------------------
BG = "#020617"
GRID_STROKE = "#1e293b"
EDGE_R = 12      # orthogonal edge corner radius
RX_COMP = 2
RX_CLUSTER = 4
CHAR_W = 0.6     # JetBrains Mono width factor

# Palette --------------------------------------------------------------------
PALETTE = {
    "cyan":    {"fill": "rgba(8,51,68,0.4)",     "stroke": "#22d3ee"},
    "emerald": {"fill": "rgba(6,78,59,0.4)",     "stroke": "#34d399"},
    "violet":  {"fill": "rgba(76,29,149,0.4)",   "stroke": "#a78bfa"},
    "rose":    {"fill": "rgba(136,19,55,0.4)",   "stroke": "#fb7185"},
    "amber":   {"fill": "rgba(120,53,15,0.3)",   "stroke": "#fbbf24"},
    "slate":   {"fill": "rgba(30,41,59,0.5)",    "stroke": "#94a3b8"},
}

# Domain ---------------------------------------------------------------------
@dataclass
class Box:
    name: str
    x: int
    y: int
    w: int
    h: int
    color: str = "slate"
    sublabel: str = ""

    @property
    def right(self):  return self.x + self.w
    @property
    def bottom(self): return self.y + self.h
    @property
    def cx(self):     return self.x + self.w // 2
    @property
    def cy(self):     return self.y + self.h // 2

@dataclass
class Cluster:
    name: str
    x: int
    y: int
    w: int
    h: int
    color: str = "amber"     # for stroke / tint
    sublabel: str = ""
    @property
    def right(self):  return self.x + self.w
    @property
    def bottom(self): return self.y + self.h

@dataclass
class Edge:
    src: str           # box name
    dst: str           # box name
    label: str = ""
    color: str = "slate"
    dash: Optional[str] = None     # SVG dasharray e.g. "5,3"
    width: float = 1.0
    turn: Literal["h", "v", "auto"] = "auto"   # H-first or V-first turn
    marker: str = "ah"                          # ah | end-tri-open | end-diamond-filled | end-diamond-open | end-dot
    # Optional explicit attachment points (overrides default edge-of-box).
    src_side: Optional[Literal["t","r","b","l"]] = None
    dst_side: Optional[Literal["t","r","b","l"]] = None
    # Optional Z-shape waypoints — supply EITHER via_y (V-H-V) OR via_x (H-V-H).
    via_y: Optional[int] = None
    via_x: Optional[int] = None

@dataclass
class Diagram:
    name: str
    title: str
    subtitle: str
    width: int
    height: int
    boxes: list[Box] = field(default_factory=list)
    clusters: list[Cluster] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    # Optional free-floating annotations (text + optional underline)
    notes: list[tuple[int,int,str,str]] = field(default_factory=list)  # (x, y, text, color)

# Layout validation -----------------------------------------------------------
def _overlap(a: Box, b: Box) -> bool:
    return not (a.right <= b.x or b.right <= a.x or a.bottom <= b.y or b.bottom <= a.y)

def validate(d: Diagram) -> None:
    # 1. No two component bboxes intersect
    for i, a in enumerate(d.boxes):
        for b in d.boxes[i+1:]:
            if _overlap(a, b):
                raise ValueError(f"{d.name}: components overlap — {a.name} ⨯ {b.name}")
    # 2. Each component fits inside at most one cluster, and fully inside if so
    for c in d.clusters:
        for b in d.boxes:
            inside = (b.x >= c.x and b.right <= c.right and
                      b.y >= c.y and b.bottom <= c.bottom)
            partial = (b.x < c.right and b.right > c.x and
                       b.y < c.bottom and b.bottom > c.y)
            if partial and not inside:
                raise ValueError(f"{d.name}: {b.name} partially overlaps cluster {c.name}")
    # 3. Edge endpoints reference existing boxes
    names = {b.name for b in d.boxes}
    for e in d.edges:
        for end in (e.src, e.dst):
            if end not in names:
                raise ValueError(f"{d.name}: edge endpoint '{end}' is not a box")

# Geometry helpers ------------------------------------------------------------
def text_w(text: str, fs: int) -> float:
    return len(text) * fs * CHAR_W

def infer_side(b: Box, toward: tuple[int,int]) -> str:
    """Pick the side of `b` facing the target point."""
    tx, ty = toward
    if abs(tx - b.cx) >= abs(ty - b.cy):
        return "r" if tx > b.cx else "l"
    return "b" if ty > b.cy else "t"

def attach_point(b: Box, side: str, slot: int, total: int) -> tuple[int,int]:
    """Attachment point on a box side for the `slot`-th arrow out of `total`.

    Multiple arrows sharing a (box, side) are distributed evenly across that
    side so the eye can follow each arrow back to its origin/terminus.

    For total=1 the slot lands at the side midpoint (backward-compatible).
    For total=n the slots land at fractions (slot+1)/(n+1) of the side length.
    """
    frac_num = slot + 1                  # 1..n
    frac_den = total + 1                 # 2..n+1
    if side == "t":
        return (b.x + b.w * frac_num // frac_den, b.y)
    if side == "b":
        return (b.x + b.w * frac_num // frac_den, b.bottom)
    if side == "l":
        return (b.x,                              b.y + b.h * frac_num // frac_den)
    if side == "r":
        return (b.right,                          b.y + b.h * frac_num // frac_den)
    raise ValueError(f"bad side {side}")

def ortho_path(x1: int, y1: int, x2: int, y2: int, turn: str = "auto", r: int = EDGE_R) -> str:
    """Generate orthogonal path with rounded corners (one turn)."""
    if y1 == y2:
        return f"M{x1},{y1} H{x2}"
    if x1 == x2:
        return f"M{x1},{y1} V{y2}"
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    if turn == "auto":
        # H-first if horizontal distance is the longer leg, else V-first
        turn = "h" if abs(x2 - x1) >= abs(y2 - y1) else "v"
    if turn == "h":
        # H to (x2 - r·sx) ; quarter arc ; V to y2
        return (f"M{x1},{y1} H{x2 - r*sx} "
                f"Q{x2},{y1} {x2},{y1 + r*sy} "
                f"V{y2}")
    else:  # v-first
        return (f"M{x1},{y1} V{y2 - r*sy} "
                f"Q{x1},{y2} {x1 + r*sx},{y2} "
                f"H{x2}")

def ortho_path_z_v(x1: int, y1: int, x2: int, y2: int, via_y: int, r: int = EDGE_R) -> str:
    """V-H-V routing through an intermediate y row. Use when the straight
    H-then-V path would cross other components in the same band.
    Falls back to a straight vertical when source and destination are nearly
    aligned (avoids the degenerate zigzag where the H leg is shorter than 2r)."""
    if abs(x2 - x1) < 2 * r:
        # Source and destination columns are too close for a clean Z — snap to a
        # straight vertical at the midpoint x and let the natural alignment carry it.
        return f"M{x1},{y1} V{y2}"
    sx  = 1 if x2 > x1 else -1
    sy1 = 1 if via_y > y1 else -1
    sy2 = 1 if y2 > via_y else -1
    return (f"M{x1},{y1} "
            f"V{via_y - r*sy1} Q{x1},{via_y} {x1 + r*sx},{via_y} "
            f"H{x2 - r*sx} Q{x2},{via_y} {x2},{via_y + r*sy2} "
            f"V{y2}")

def ortho_path_z_h(x1: int, y1: int, x2: int, y2: int, via_x: int, r: int = EDGE_R) -> str:
    """H-V-H routing through an intermediate x column."""
    if y1 == y2:
        return f"M{x1},{y1} H{x2}"
    sy  = 1 if y2 > y1 else -1
    sx1 = 1 if via_x > x1 else -1
    sx2 = 1 if x2 > via_x else -1
    return (f"M{x1},{y1} "
            f"H{via_x - r*sx1} Q{via_x},{y1} {via_x},{y1 + r*sy} "
            f"V{y2 - r*sy} Q{via_x},{y2} {via_x + r*sx2},{y2} "
            f"H{x2}")

# SVG emission ---------------------------------------------------------------
def _defs() -> str:
    # Per-color chevron markers + UML endings
    markers = []
    for color, vals in PALETTE.items():
        markers.append(
            f'<marker id="ah-{color}" viewBox="0 0 10 10" markerWidth="8" markerHeight="8" '
            f'refX="9" refY="5" orient="auto" markerUnits="strokeWidth">'
            f'<path d="M0,0 L9,5 L0,10" fill="none" stroke="{vals["stroke"]}" '
            f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        )
    # UML endings (slate-coloured; per-edge can override)
    markers.extend([
        '<marker id="end-tri-open" viewBox="0 0 10 10" markerWidth="9" markerHeight="9" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L9,5 L0,10 Z" fill="{BG}" stroke="#94a3b8" stroke-width="1.2"/></marker>',
        '<marker id="end-diamond-filled" viewBox="0 0 10 10" markerWidth="10" markerHeight="8" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,5 L5,0 L10,5 L5,10 Z" fill="#94a3b8" stroke="#94a3b8" stroke-width="1"/></marker>',
        '<marker id="end-diamond-open" viewBox="0 0 10 10" markerWidth="10" markerHeight="8" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,5 L5,0 L10,5 L5,10 Z" fill="{BG}" stroke="#94a3b8" stroke-width="1"/></marker>',
        '<marker id="end-dot" viewBox="0 0 10 10" markerWidth="6" markerHeight="6" refX="5" refY="5" orient="auto" markerUnits="strokeWidth">'
        '<circle cx="5" cy="5" r="3" fill="#94a3b8"/></marker>',
    ])
    grid = ('<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
            f'<path d="M40 0 L0 0 0 40" fill="none" stroke="{GRID_STROKE}" stroke-width="0.5"/></pattern>')
    return f"<defs>{grid}{''.join(markers)}</defs>"

def _style() -> str:
    return (
        "<style>"
        # Universal text-border knockout halo
        "text{paint-order:stroke fill;stroke:" + BG + ";stroke-width:4;stroke-linejoin:round;stroke-linecap:round;fill:#e2e8f0;font-size:12px;font-family:'JetBrains Mono',ui-monospace,monospace;}"
        "text.title{stroke-width:6;font-size:16px;font-weight:700;fill:#f1f5f9;}"
        "text.sub{stroke-width:3;font-size:10px;fill:#94a3b8;}"
        "text.lbl{font-size:11px;fill:#cbd5e1;}"
        "text.cluster{stroke-width:5;font-size:11px;font-weight:600;fill:#cbd5e1;}"
        # Subtle hover glow
        "rect.component{transition:filter 220ms ease;cursor:pointer;}"
        "rect.component:hover{filter:drop-shadow(0 0 8px var(--glow,rgba(255,255,255,0.2)));}"
        "rect.cyan{--glow:rgba(34,211,238,0.5);}"
        "rect.emerald{--glow:rgba(52,211,153,0.5);}"
        "rect.violet{--glow:rgba(167,139,250,0.5);}"
        "rect.rose{--glow:rgba(251,113,133,0.5);}"
        "rect.amber{--glow:rgba(251,191,36,0.5);}"
        "rect.slate{--glow:rgba(148,163,184,0.4);}"
        "</style>"
    )

def render(d: Diagram) -> str:
    validate(d)
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {d.width} {d.height}">')
    out.append(_defs())
    out.append(_style())
    out.append(f'<rect width="{d.width}" height="{d.height}" fill="{BG}"/>')
    out.append(f'<rect width="{d.width}" height="{d.height}" fill="url(#grid)"/>')

    # Title + subtitle (top-left, no chip)
    out.append(f'<text class="title" x="32" y="44">{d.title}</text>')
    if d.subtitle:
        out.append(f'<text class="sub" x="32" y="64">{d.subtitle}</text>')

    # Clusters (under components)
    for c in d.clusters:
        pal = PALETTE[c.color]
        out.append(
            f'<rect x="{c.x}" y="{c.y}" width="{c.w}" height="{c.h}" rx="{RX_CLUSTER}" '
            f'fill="none" stroke="{pal["stroke"]}" stroke-width="1.5" stroke-dasharray="8,4"/>'
        )
        # Cluster header label sits on the top dashed edge — universal halo masks it
        out.append(f'<text class="cluster" x="{c.x + 16}" y="{c.y + 6}">{c.name}</text>')
        if c.sublabel:
            out.append(f'<text class="sub" x="{c.x + 16}" y="{c.y + 22}">{c.sublabel}</text>')

    # Components
    by_name = {b.name: b for b in d.boxes}
    for b in d.boxes:
        pal = PALETTE[b.color]
        out.append(
            f'<rect class="component {b.color}" x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" rx="{RX_COMP}" '
            f'fill="{pal["fill"]}" stroke="{pal["stroke"]}" stroke-width="1"/>'
        )
        # Inside-box label — text only, centered
        out.append(f'<text x="{b.cx}" y="{b.y + b.h//2 + 4}" text-anchor="middle">{b.name}</text>')
        if b.sublabel:
            out.append(f'<text class="sub" x="{b.cx}" y="{b.y + b.h//2 + 20}" text-anchor="middle">{b.sublabel}</text>')

    # ---- Edge attach-point resolution (Phase 1 of edge rendering) ----
    # When N arrows leave (or arrive at) the same side of a box, distribute
    # their attach points across that side at fractions k/(N+1). For N=1 this
    # is the side midpoint (backward-compatible); for N>1 each arrow gets its
    # own departure/arrival slot so the eye can follow the line from one
    # endpoint to the other without arrows piling up on a single point.

    # group_key = (box_name, side) -> list of (edge_idx, role, toward_xy)
    groups: dict[tuple[str, str], list[tuple[int, str, tuple[int,int]]]] = {}
    for i, e in enumerate(d.edges):
        src, dst = by_name[e.src], by_name[e.dst]
        s_side = e.src_side or infer_side(src, (dst.cx, dst.cy))
        d_side = e.dst_side or infer_side(dst, (src.cx, src.cy))
        groups.setdefault((e.src, s_side), []).append((i, "src", (dst.cx, dst.cy)))
        groups.setdefault((e.dst, d_side), []).append((i, "dst", (src.cx, src.cy)))

    # Resolve each (edge, role) to its concrete (x, y). Slots ordered by the
    # direction the arrow is heading toward, so neighbouring arrows on the
    # same side stay in natural reading order (top-to-bottom on l/r sides,
    # left-to-right on t/b sides).
    resolved: dict[tuple[int, str], tuple[int,int]] = {}
    for (box_name, side), items in groups.items():
        box = by_name[box_name]
        if side in ("l", "r"):
            items.sort(key=lambda it: it[2][1])
        else:
            items.sort(key=lambda it: it[2][0])
        total = len(items)
        for slot, (edge_idx, role, _) in enumerate(items):
            resolved[(edge_idx, role)] = attach_point(box, side, slot, total)

    # ---- Edge emission (Phase 2 of edge rendering) ----
    for i, e in enumerate(d.edges):
        sp = resolved[(i, "src")]
        dp = resolved[(i, "dst")]
        # Trim endpoint by a few px so the chevron doesn't sit on the stroke
        # (marker refX=9 handles the inset on its own).
        if e.via_y is not None:
            path = ortho_path_z_v(sp[0], sp[1], dp[0], dp[1], e.via_y)
        elif e.via_x is not None:
            path = ortho_path_z_h(sp[0], sp[1], dp[0], dp[1], e.via_x)
        else:
            path = ortho_path(sp[0], sp[1], dp[0], dp[1], turn=e.turn)
        pal = PALETTE[e.color]
        dash_attr = f' stroke-dasharray="{e.dash}"' if e.dash else ""
        marker_id = f"ah-{e.color}" if e.marker == "ah" else e.marker
        out.append(
            f'<path d="{path}" fill="none" stroke="{pal["stroke"]}" '
            f'stroke-width="{e.width}"{dash_attr} stroke-linecap="round" stroke-linejoin="round" '
            f'marker-end="url(#{marker_id})"/>'
        )
        if e.label:
            # Inline label at the geometric midpoint of the path's straight legs.
            # For single-turn paths, midpoint of bounding rect is "fine enough" for
            # the example library; user-tuned labels can override later.
            mx = (sp[0] + dp[0]) // 2
            my = (sp[1] + dp[1]) // 2 - 6   # 6 px above line
            fs = 11
            tw = text_w(e.label, fs)
            out.append(f'<text class="lbl" x="{mx}" y="{my}" text-anchor="middle">{e.label}</text>')
            # Underline (image #5 style)
            out.append(
                f'<line x1="{mx - tw/2:.1f}" y1="{my + 4}" '
                f'x2="{mx + tw/2:.1f}" y2="{my + 4}" '
                f'stroke="#94a3b8" stroke-width="0.75"/>'
            )

    # Notes / free-floating labels
    for (x, y, text, color) in d.notes:
        out.append(f'<text class="lbl" x="{x}" y="{y}" fill="{color}">{text}</text>')

    out.append('</svg>')
    return "\n".join(out) + "\n"

# ---------------------------------------------------------------------------
# Diagram definitions
# ---------------------------------------------------------------------------
def diagram_01() -> Diagram:
    d = Diagram(
        name="01-client-api-db",
        title="THREE-TIER REQUEST FLOW",
        subtitle="user · edge · service · storage — blueprint v2 baseline",
        width=960, height=300,
    )
    y_row = 160
    h = 64
    w = 140
    gap = 80
    x0 = 80
    for i, (nm, sub, color) in enumerate([
        ("USER", "browser", "slate"),
        ("API GATEWAY", "edge · TLS", "cyan"),
        ("ORDER SVC", "compute", "emerald"),
        ("POSTGRES", "primary", "violet"),
    ]):
        x = x0 + i * (w + gap)
        d.boxes.append(Box(nm, x=x, y=y_row, w=w, h=h, color=color, sublabel=sub))
    d.edges.extend([
        Edge("USER", "API GATEWAY", label="HTTPS",   color="slate"),
        Edge("API GATEWAY", "ORDER SVC", label="gRPC", color="cyan"),
        Edge("ORDER SVC", "POSTGRES", label="SQL",   color="violet", dash="4,3"),
    ])
    return d

def diagram_02() -> Diagram:
    d = Diagram(
        name="02-service-mesh-xds",
        title="SERVICE MESH — xDS CONTROL PLANE / ENVOY DATA PLANE",
        subtitle="dashed cyan = xDS config push · solid emerald = mTLS · solid violet = sidecar→app",
        width=960, height=600,
    )
    # Layout principle: envoys ABOVE services. This puts the sidecars at the
    # top of each pod where xDS config flows in, and the app services below
    # where the envoy proxies data to them. xDS lines now enter envoys from
    # above through clean canvas — no line crosses any service box.
    pod_w  = 180
    pod_cx = [200, 480, 760]
    pod_x  = [cx - pod_w // 2 for cx in pod_cx]     # 110, 390, 670
    envoy_y   = 310
    service_y = 410
    # Control plane cluster, xDS centred so its line down to envoy B is straight.
    d.clusters.append(Cluster("CONTROL PLANE", x=380, y=110, w=200, h=80, color="cyan"))
    d.boxes.append(Box("xDS SERVER", x=400, y=138, w=160, h=44, color="cyan", sublabel="config"))
    # Data plane cluster wraps both rows (envoys + services).
    d.clusters.append(Cluster("DATA PLANE — pods", x=60, y=270, w=840, h=240, color="emerald"))
    for i, x in enumerate(pod_x):
        suffix = chr(ord('A') + i)
        d.boxes.append(Box(f"ENVOY {suffix}",   x=x, y=envoy_y,   w=pod_w, h=44, color="cyan",    sublabel="sidecar"))
        d.boxes.append(Box(f"SERVICE {suffix}", x=x, y=service_y, w=pod_w, h=44, color="emerald", sublabel="app"))
    # xDS → envoys (top row). Lines arrive cleanly at envoy top edge.
    # For ENVOY A and C the path is a Z through via_y=270 (clear corridor
    # just inside the data-plane cluster, above the envoy row at y=310).
    # ENVOY B sits directly below xDS so the line collapses to a straight V.
    d.edges.append(Edge("xDS SERVER", "ENVOY A", color="cyan", dash="5,3",
                        src_side="b", dst_side="t", via_y=270))
    d.edges.append(Edge("xDS SERVER", "ENVOY B", color="cyan", dash="5,3",
                        src_side="b", dst_side="t"))
    d.edges.append(Edge("xDS SERVER", "ENVOY C", color="cyan", dash="5,3",
                        src_side="b", dst_side="t", via_y=270))
    # Each envoy proxies to its own service (straight V down inside the pod column).
    for suffix in "ABC":
        d.edges.append(Edge(f"ENVOY {suffix}", f"SERVICE {suffix}",
                            color="violet", src_side="b", dst_side="t"))
    # mTLS between adjacent Envoys (same row, horizontal).
    d.edges.append(Edge("ENVOY A", "ENVOY B", label="mTLS", color="emerald", src_side="r", dst_side="l"))
    d.edges.append(Edge("ENVOY B", "ENVOY C", label="mTLS", color="emerald", src_side="r", dst_side="l"))
    return d

def diagram_03() -> Diagram:
    d = Diagram(
        name="03-oauth-flow",
        title="OAUTH2 / JWT FLOW WITH SECURITY BOUNDARY",
        subtitle="rose dashed = auth / token material · rose cluster = trust zone",
        width=960, height=440,
    )
    # Client outside trust zone
    d.boxes.append(Box("SPA CLIENT", x=60,  y=200, w=140, h=64, color="slate", sublabel="browser"))
    # Trust zone cluster containing API, AUTHZ, IDP
    d.clusters.append(Cluster("TRUST ZONE — server-side", x=240, y=140, w=680, h=240, color="rose"))
    d.boxes.append(Box("API",   x=280, y=200, w=140, h=64, color="emerald", sublabel="resource svr"))
    d.boxes.append(Box("AUTHZ", x=480, y=200, w=140, h=64, color="rose",    sublabel="policy decision"))
    d.boxes.append(Box("IDP",   x=720, y=200, w=140, h=64, color="rose",    sublabel="Keycloak / Auth0"))
    d.edges.extend([
        Edge("SPA CLIENT", "API",   label="Bearer JWT", color="rose", dash="3,3"),
        Edge("API",        "AUTHZ", label="introspect", color="rose", dash="3,3"),
        Edge("AUTHZ",      "IDP",   label="JWKS",       color="rose", dash="3,3"),
    ])
    return d

def diagram_04() -> Diagram:
    d = Diagram(
        name="04-event-driven-cqrs",
        title="EVENT-DRIVEN CQRS WITH AUDIT STREAM",
        subtitle="solid = command · amber dashed = pub/sub · violet dotted = audit",
        width=960, height=480,
    )
    d.boxes.append(Box("COMMAND SVC", x=60,  y=200, w=160, h=64, color="emerald", sublabel="write side"))
    d.boxes.append(Box("KAFKA",       x=300, y=200, w=180, h=64, color="amber",   sublabel="orders.events"))
    d.boxes.append(Box("PROJECTOR",   x=560, y=100, w=160, h=64, color="emerald", sublabel="build read model"))
    d.boxes.append(Box("READ DB",     x=760, y=100, w=140, h=64, color="violet",  sublabel="denorm"))
    d.boxes.append(Box("NOTIFIER",    x=560, y=300, w=160, h=64, color="emerald", sublabel="email / push"))
    d.boxes.append(Box("AUDIT SINK",  x=300, y=380, w=180, h=64, color="violet",  sublabel="S3 cold storage"))
    d.edges.extend([
        Edge("COMMAND SVC", "KAFKA", label="produce", color="emerald"),
        Edge("KAFKA", "PROJECTOR",   label="consume", color="amber", dash="5,3"),
        Edge("PROJECTOR", "READ DB", color="violet", dash="4,3"),
        Edge("KAFKA", "NOTIFIER",    label="consume", color="amber", dash="5,3"),
        Edge("KAFKA", "AUDIT SINK",  label="audit tap", color="violet", dash="1,3", width=0.75, src_side="b", dst_side="t"),
    ])
    return d

def diagram_05() -> Diagram:
    d = Diagram(
        name="05-multi-tenant-kms",
        title="MULTI-TENANT CREDENTIALS — KMS-WRAPPED AT REST",
        subtitle="bold rose = key material · emerald = decrypted only in agent memory",
        width=960, height=600,
    )
    # Control plane region
    d.clusters.append(Cluster("CONTROL PLANE — encrypted at rest", x=40, y=100, w=880, h=180, color="amber"))
    d.boxes.append(Box("TENANT CONFIG DB", x=80,  y=170, w=200, h=80, color="violet",  sublabel="creds: KMS-wrapped"))
    d.boxes.append(Box("AWS / GCP KMS",    x=380, y=170, w=200, h=80, color="rose",    sublabel="CMK · HSM-backed"))
    d.boxes.append(Box("ADMIN API",        x=680, y=170, w=200, h=80, color="emerald", sublabel="tenant onboarding"))
    # Data plane region
    d.clusters.append(Cluster("DATA PLANE — plaintext only in agent memory", x=40, y=340, w=880, h=200, color="emerald"))
    d.boxes.append(Box("XDS AGENT", x=300, y=420, w=200, h=80, color="emerald", sublabel="holds plaintext DEK"))
    d.boxes.append(Box("ENVOY",     x=620, y=420, w=200, h=80, color="cyan",    sublabel="per-tenant clusters"))
    d.edges.extend([
        # admin → config DB: route ABOVE the KMS box (via_y=130, above the
        # 170-250 row that holds all three control-plane components)
        Edge("ADMIN API", "TENANT CONFIG DB", label="write wrapped DEK",
             color="violet", dash="4,3",
             src_side="t", dst_side="t", via_y=130),
        # admin → KMS: same row, simple H
        Edge("ADMIN API", "AWS / GCP KMS", label="Encrypt(DEK)",
             color="rose", width=2,
             src_side="l", dst_side="r"),
        # xDS agent → config DB: cross-zone, via via_y=310 (between zones)
        Edge("XDS AGENT", "TENANT CONFIG DB", label="fetch wrapped",
             color="violet", dash="4,3",
             src_side="t", dst_side="b", via_y=310),
        # xDS agent → KMS: bold key flow, cross-zone via via_y=310
        Edge("XDS AGENT", "AWS / GCP KMS", label="Decrypt(wrapped)",
             color="rose", width=2,
             src_side="t", dst_side="b", via_y=310),
        # xDS agent → Envoy: same row, simple H
        Edge("XDS AGENT", "ENVOY", label="xDS push", color="emerald",
             src_side="r", dst_side="l"),
    ])
    return d

# ---------------------------------------------------------------------------
def main():
    out_dir = Path(__file__).parent
    for diag in (diagram_01(), diagram_02(), diagram_03(), diagram_04(), diagram_05()):
        svg = render(diag)
        out = out_dir / f"{diag.name}.svg"
        out.write_text(svg)
        print(f"wrote {out.relative_to(Path.cwd())}  ({len(svg)} bytes, "
              f"{len(diag.boxes)} components, {len(diag.edges)} edges)")

if __name__ == "__main__":
    main()
