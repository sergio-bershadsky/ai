#!/usr/bin/env python3
"""Deterministic geometry linter for architecture-diagram SVG/HTML files.

Reports intersections that should not exist in a clean blueprint:
  1. component <-> component overlap
  2. component overflowing its parent cluster
  3. path segment crossing a component box that is NOT its endpoint
  4. two path segments crossing each other (not just sharing an endpoint)
  5. text label bbox overlapping a component box it does not belong to
  6. path segment passing through a text bbox (other than its own label)

Each finding is printed as a single line with svg line numbers so the model
can iteratively refine the source.

Usage:
    python3 geometry-audit.py <file>.svg|<file>.html [--json] [--ignore-edge-edge]

Heuristics:
  * A path's endpoints are the first and last (x,y) in its `d` attribute.
    A component rect is considered the path's source/target when an endpoint
    lies within `ENDPOINT_TOL` of the rect perimeter.
  * Cluster rects are detected by `fill="none"` + dashed stroke.
  * Q (quadratic) commands are treated as a single bend point — fine for the
    12px fillets used by this skill.
  * Text bbox is estimated as: width = len * fontsize * 0.6, height = fontsize * 1.2,
    centered for text-anchor=middle, else left-anchored at (x,y).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

ENDPOINT_TOL = 2.0           # endpoint counts as on rect-edge if within this many px
COLLINEAR_TOL = 0.5          # two segments collinear if axis offset less than this
EDGE_CORRIDOR_TOL = 6.0      # ignore intersections this close to shared endpoint
TEXT_PADDING = 2.0           # padding around text bbox for hit-test
COMPONENT_PADDING = 0.0      # extra inflation for component hit-test (keep 0 = strict)
CLUSTER_BORDER_TOL = 2.5     # path segment within this distance of a cluster border = visual merge
CLUSTER_BORDER_MIN_OVERLAP = 8.0  # minimum overlap length to flag (skip tangent corners)


@dataclass
class Rect:
    x: float; y: float; w: float; h: float
    line: int
    is_cluster: bool
    css_class: str = ""

    @property
    def x2(self) -> float: return self.x + self.w
    @property
    def y2(self) -> float: return self.y + self.h
    @property
    def cx(self) -> float: return self.x + self.w / 2
    @property
    def cy(self) -> float: return self.y + self.h / 2

    def contains_point(self, px: float, py: float, pad: float = 0.0) -> bool:
        return (self.x - pad <= px <= self.x2 + pad) and (self.y - pad <= py <= self.y2 + pad)

    def point_on_perimeter(self, px: float, py: float, tol: float = ENDPOINT_TOL) -> bool:
        on_v = (abs(px - self.x) <= tol or abs(px - self.x2) <= tol) and (self.y - tol <= py <= self.y2 + tol)
        on_h = (abs(py - self.y) <= tol or abs(py - self.y2) <= tol) and (self.x - tol <= px <= self.x2 + tol)
        return on_v or on_h


@dataclass
class Segment:
    x1: float; y1: float; x2: float; y2: float
    path_line: int
    path_id: int

    @property
    def horizontal(self) -> bool: return abs(self.y1 - self.y2) < COLLINEAR_TOL
    @property
    def vertical(self) -> bool: return abs(self.x1 - self.x2) < COLLINEAR_TOL
    @property
    def length(self) -> float: return ((self.x2-self.x1)**2 + (self.y2-self.y1)**2) ** 0.5


@dataclass
class PathInfo:
    line: int
    d: str
    segments: list[Segment] = field(default_factory=list)
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    css_class: str = ""

    @property
    def is_lifeline(self) -> bool:
        # Sequence-diagram time axes — decorative, every horizontal message
        # crosses every lifeline by design. Exempt from edge-edge and
        # edge-crosses-component checks.
        return "lifeline" in self.css_class.split()


@dataclass
class TextInfo:
    x: float; y: float
    text: str
    line: int
    anchor: str
    font_size: float

    @property
    def bbox(self) -> tuple[float, float, float, float]:
        # rough monospace estimate
        w = max(len(self.text), 1) * self.font_size * 0.6
        h = self.font_size * 1.1
        if self.anchor == "middle":
            x = self.x - w / 2
        elif self.anchor == "end":
            x = self.x - w
        else:
            x = self.x
        # text y is baseline; box top is y - h*0.8
        y = self.y - h * 0.8
        return (x - TEXT_PADDING, y - TEXT_PADDING,
                x + w + TEXT_PADDING, y + h + TEXT_PADDING)


# ---------- parsing ----------

_NUM = r'-?\d+(?:\.\d+)?'


def parse_rects(svg_lines: list[str], inside_g_lines: set[int]) -> list[Rect]:
    """Extract component and cluster rectangles from SVG lines.

    Identification is by attribute, not nesting depth — ELK output wraps all
    content in a single <g transform> so a blanket "skip inside <g>" rule
    erroneously hides everything. We use:
      * class contains "component" → component
      * fill="none" AND stroke-dasharray present → cluster
      * anything else (icon stencils, backgrounds, grid) → skip

    `inside_g_lines` is still consulted as a tie-breaker: a rect that's not
    explicitly classed AND lives inside a <g> is treated as decoration.
    """
    rects = []
    rect_re = re.compile(r'<rect\b([^/>]*)/?>')
    attr_re = re.compile(r'(\w[\w-]*)="([^"]*)"')
    for i, line in enumerate(svg_lines, start=1):
        for m in rect_re.finditer(line):
            attrs = dict(attr_re.findall(m.group(1)))
            try:
                x = float(attrs.get("x", 0)); y = float(attrs.get("y", 0))
                w = float(attrs["width"]); h = float(attrs["height"])
            except (KeyError, ValueError):
                continue
            if "url(" in attrs.get("fill", ""):
                continue  # grid/pattern background
            css_class = attrs.get("class", "")
            has_dasharray = bool(attrs.get("stroke-dasharray", "").strip())
            is_component = "component" in css_class
            is_cluster = (not is_component) and attrs.get("fill") == "none" and has_dasharray
            if not is_component and not is_cluster:
                # fall back to legacy heuristic: untyped fill=none rects outside
                # any <g> are clusters, inside <g> are icon stencils.
                if attrs.get("fill") == "none" and i not in inside_g_lines:
                    is_cluster = True
                else:
                    continue
            rects.append(Rect(x, y, w, h, i, is_cluster, css_class))
    return rects


def find_g_block_lines(svg_text: str) -> set[int]:
    """Return the set of 1-based line numbers that fall inside any <g ...>...</g>
    block (used to skip decorative shapes inside icon groups)."""
    inside: set[int] = set()
    for m in re.finditer(r'<g\b[^>]*>(.*?)</g>', svg_text, flags=re.DOTALL):
        prefix = svg_text[:m.start()]
        start_line = prefix.count('\n') + 1
        end_line = start_line + m.group(0).count('\n')
        for ln in range(start_line, end_line + 1):
            inside.add(ln)
    return inside


def parse_paths(svg_lines: list[str]) -> list[PathInfo]:
    paths = []
    path_re = re.compile(r'<path\b([^>]*)>')
    line_re = re.compile(r'<line\b([^>]*)/?>')
    class_re = re.compile(r'\bclass="([^"]*)"')
    d_re = re.compile(r'\bd="([^"]+)"')
    coord_re = re.compile(r'\b(x1|y1|x2|y2)="(' + _NUM + r')"')
    for i, line in enumerate(svg_lines, start=1):
        # <path d="...">
        for m in path_re.finditer(line):
            attrs = m.group(1)
            d_m = d_re.search(attrs)
            if not d_m:
                continue
            d = d_m.group(1)
            cls_m = class_re.search(attrs)
            pi = PathInfo(line=i, d=d, css_class=cls_m.group(1) if cls_m else "")
            pi.segments = decompose_path(d, i, len(paths))
            if pi.segments:
                pi.start = (pi.segments[0].x1, pi.segments[0].y1)
                pi.end = (pi.segments[-1].x2, pi.segments[-1].y2)
            paths.append(pi)
        # <line x1=".." y1=".." x2=".." y2=".."> — single straight segment.
        # Used for lifelines in sequence diagrams; also a valid way to draw a
        # simple message arrow.
        for m in line_re.finditer(line):
            attrs = m.group(1)
            coords = {k: float(v) for k, v in coord_re.findall(attrs)}
            if not all(k in coords for k in ("x1", "y1", "x2", "y2")):
                continue
            cls_m = class_re.search(attrs)
            pi = PathInfo(
                line=i,
                d=f'M{coords["x1"]},{coords["y1"]} L{coords["x2"]},{coords["y2"]}',
                css_class=cls_m.group(1) if cls_m else "",
            )
            seg = Segment(coords["x1"], coords["y1"], coords["x2"], coords["y2"], i, len(paths))
            pi.segments = [seg]
            pi.start = (seg.x1, seg.y1)
            pi.end = (seg.x2, seg.y2)
            paths.append(pi)
    return paths


def decompose_path(d: str, path_line: int, path_id: int) -> list[Segment]:
    """Decompose an orthogonal path with Q fillets into straight segments.

    Supports: M x,y | V y | H x | L x,y | Q cx,cy x,y (treated as corner-only).
    Multi-segment with implicit continuation."""
    toks = re.findall(r'[MLHVQCZmlhvqcz]|' + _NUM, d)
    segs = []
    cx, cy = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    i = 0
    last_cmd = None
    while i < len(toks):
        t = toks[i]
        if t in 'MmLlHhVvQqCcZz':
            cmd = t; i += 1
        else:
            cmd = last_cmd  # implicit repeat
        if cmd is None:
            i += 1; continue
        last_cmd = cmd
        try:
            if cmd in 'Mm':
                x = float(toks[i]); y = float(toks[i+1]); i += 2
                if cmd == 'm':
                    x += cx; y += cy
                cx, cy = x, y
                start_x, start_y = x, y
                last_cmd = 'L' if cmd == 'M' else 'l'
            elif cmd in 'Ll':
                x = float(toks[i]); y = float(toks[i+1]); i += 2
                if cmd == 'l':
                    x += cx; y += cy
                segs.append(Segment(cx, cy, x, y, path_line, path_id))
                cx, cy = x, y
            elif cmd in 'Hh':
                x = float(toks[i]); i += 1
                if cmd == 'h': x += cx
                segs.append(Segment(cx, cy, x, cy, path_line, path_id))
                cx = x
            elif cmd in 'Vv':
                y = float(toks[i]); i += 1
                if cmd == 'v': y += cy
                segs.append(Segment(cx, cy, cx, y, path_line, path_id))
                cy = y
            elif cmd in 'Qq':
                # control point + endpoint; treat as a single straight segment
                # from current to endpoint (the Q is a 12px fillet — negligible).
                _ = (float(toks[i]), float(toks[i+1]))  # control point ignored
                x = float(toks[i+2]); y = float(toks[i+3]); i += 4
                if cmd == 'q':
                    x += cx; y += cy
                segs.append(Segment(cx, cy, x, y, path_line, path_id))
                cx, cy = x, y
            elif cmd in 'Cc':
                # cubic — ignored for orthogonal architecture diagrams
                i += 6
            elif cmd in 'Zz':
                segs.append(Segment(cx, cy, start_x, start_y, path_line, path_id))
                cx, cy = start_x, start_y
            else:
                i += 1
        except (IndexError, ValueError):
            break
    return segs


def parse_texts(svg_lines: list[str]) -> list[TextInfo]:
    texts = []
    text_re = re.compile(
        r'<text\b([^>]*)>([^<]*)</text>'
    )
    attr_re = re.compile(r'(\w[\w-]*)="([^"]*)"')
    # default font-size by class (matches the skill template)
    size_for_class = {"title": 16, "sub": 10, "lbl": 11, "cluster": 11, "": 12}
    for i, line in enumerate(svg_lines, start=1):
        for m in text_re.finditer(line):
            attrs = dict(attr_re.findall(m.group(1)))
            body = m.group(2).strip()
            if not body:
                continue
            try:
                x = float(attrs.get("x", 0)); y = float(attrs.get("y", 0))
            except ValueError:
                continue
            cls = attrs.get("class", "").strip().split()[0] if attrs.get("class") else ""
            font_size = size_for_class.get(cls, 12)
            anchor = attrs.get("text-anchor", "start")
            texts.append(TextInfo(x, y, body, i, anchor, font_size))
    return texts


# ---------- geometry primitives ----------

def rects_overlap(a: Rect, b: Rect) -> bool:
    return not (a.x2 <= b.x or b.x2 <= a.x or a.y2 <= b.y or b.y2 <= a.y)


def rect_contains_rect(outer: Rect, inner: Rect) -> bool:
    return outer.x <= inner.x and outer.y <= inner.y and \
        outer.x2 >= inner.x2 and outer.y2 >= inner.y2


def seg_intersects_rect(s: Segment, r: Rect, pad: float = 0.0) -> Optional[tuple[float, float]]:
    """Liang-Barsky on axis-aligned rect. Returns the midpoint of the clipped
    portion if the segment passes through the rect interior, else None."""
    x_min, y_min = r.x - pad, r.y - pad
    x_max, y_max = r.x2 + pad, r.y2 + pad
    dx, dy = s.x2 - s.x1, s.y2 - s.y1
    p = [-dx, dx, -dy, dy]
    q = [s.x1 - x_min, x_max - s.x1, s.y1 - y_min, y_max - s.y1]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
            continue
        t = qi / pi
        if pi < 0:
            if t > u2: return None
            if t > u1: u1 = t
        else:
            if t < u1: return None
            if t < u2: u2 = t
    if u1 > u2:
        return None
    # Only flag if the intersection includes interior (not tangent on edge)
    mx = s.x1 + dx * (u1 + u2) / 2
    my = s.y1 + dy * (u1 + u2) / 2
    # If midpoint of clip is exactly on rect edge, it's tangential — skip.
    on_edge = (abs(mx - r.x) < 0.5 or abs(mx - r.x2) < 0.5 or
               abs(my - r.y) < 0.5 or abs(my - r.y2) < 0.5)
    inside_amount = (u2 - u1) * s.length
    if on_edge and inside_amount < 1.0:
        return None
    return (mx, my)


def segs_cross(a: Segment, b: Segment) -> Optional[tuple[float, float]]:
    """Cross point of two orthogonal segments — returns None if no proper crossing."""
    if a.horizontal and b.vertical:
        ax_min, ax_max = sorted((a.x1, a.x2))
        by_min, by_max = sorted((b.y1, b.y2))
        if ax_min - 0.5 < b.x1 < ax_max + 0.5 and by_min - 0.5 < a.y1 < by_max + 0.5:
            return (b.x1, a.y1)
        return None
    if a.vertical and b.horizontal:
        return segs_cross(b, a)
    if a.horizontal and b.horizontal:
        if abs(a.y1 - b.y1) > COLLINEAR_TOL: return None
        ax_min, ax_max = sorted((a.x1, a.x2))
        bx_min, bx_max = sorted((b.x1, b.x2))
        lo, hi = max(ax_min, bx_min), min(ax_max, bx_max)
        if hi - lo > 1.0:
            return ((lo + hi) / 2, a.y1)
    if a.vertical and b.vertical:
        if abs(a.x1 - b.x1) > COLLINEAR_TOL: return None
        ay_min, ay_max = sorted((a.y1, a.y2))
        by_min, by_max = sorted((b.y1, b.y2))
        lo, hi = max(ay_min, by_min), min(ay_max, by_max)
        if hi - lo > 1.0:
            return (a.x1, (lo + hi) / 2)
    return None


def near(p: tuple[float, float], q: tuple[float, float], tol: float = EDGE_CORRIDOR_TOL) -> bool:
    return abs(p[0] - q[0]) <= tol and abs(p[1] - q[1]) <= tol


# ---------- audit checks ----------

def audit(svg_text: str, ignore_edge_edge: bool = False) -> list[dict]:
    # Strip <defs>...</defs> so marker/pattern internals don't pollute results,
    # but preserve line numbers by replacing with blanks of equal length.
    def _blank_defs(text: str) -> str:
        pattern = re.compile(r'<defs\b.*?</defs>', re.DOTALL)
        def _sub(m: re.Match) -> str:
            return ''.join('\n' if c == '\n' else ' ' for c in m.group(0))
        return pattern.sub(_sub, text)
    svg_text = _blank_defs(svg_text)
    lines = svg_text.split('\n')
    inside_g = find_g_block_lines(svg_text)
    rects = parse_rects(lines, inside_g)
    paths = parse_paths(lines)
    texts = parse_texts(lines)

    components = [r for r in rects if not r.is_cluster]
    clusters = [r for r in rects if r.is_cluster]

    findings: list[dict] = []

    # 1. component <-> component overlap
    for i, a in enumerate(components):
        for b in components[i+1:]:
            if rects_overlap(a, b):
                findings.append({
                    "kind": "component-overlap",
                    "at": (round(max(a.x, b.x), 1), round(max(a.y, b.y), 1)),
                    "line_a": a.line, "line_b": b.line,
                    "msg": f"rects at lines {a.line} and {b.line} overlap",
                })

    # 2. component outside parent cluster (find best parent by smallest enclosing cluster)
    for c in components:
        parents = [cl for cl in clusters if rects_overlap(cl, c)]
        if not parents:
            continue
        best = min(parents, key=lambda r: r.w * r.h)
        if not rect_contains_rect(best, c):
            findings.append({
                "kind": "component-overflow-cluster",
                "at": (round(c.x, 1), round(c.y, 1)),
                "line_component": c.line, "line_cluster": best.line,
                "msg": f"component at line {c.line} pokes outside cluster at line {best.line}",
            })

    # 3. path crosses a component that is not its endpoint
    for p in paths:
        if p.is_lifeline:
            continue
        endpoint_rects = set()
        for r_idx, r in enumerate(components):
            if r.point_on_perimeter(*p.start) or r.point_on_perimeter(*p.end):
                endpoint_rects.add(r_idx)
        for s in p.segments:
            for r_idx, r in enumerate(components):
                if r_idx in endpoint_rects:
                    continue
                hit = seg_intersects_rect(s, r, pad=COMPONENT_PADDING)
                if hit is not None:
                    # ignore if hit is right at segment endpoint (corner pass)
                    if near(hit, (s.x1, s.y1), 0.5) or near(hit, (s.x2, s.y2), 0.5):
                        continue
                    findings.append({
                        "kind": "edge-crosses-component",
                        "at": (round(hit[0], 1), round(hit[1], 1)),
                        "line_path": p.line, "line_rect": r.line,
                        "msg": f"path at line {p.line} crosses component at line {r.line} near ({hit[0]:.0f},{hit[1]:.0f})",
                    })

    # 4. edge <-> edge crossing (paired, dedup)
    if not ignore_edge_edge:
        seen_pairs = set()
        for i, p1 in enumerate(paths):
            if p1.is_lifeline:
                continue
            for p2 in paths[i+1:]:
                if p2.is_lifeline:
                    continue
                for s1 in p1.segments:
                    for s2 in p2.segments:
                        x = segs_cross(s1, s2)
                        if x is None:
                            continue
                        # Skip if cross is at a shared endpoint of the two paths
                        if (near(x, p1.start) or near(x, p1.end)) and \
                           (near(x, p2.start) or near(x, p2.end)):
                            continue
                        key = (p1.line, p2.line, round(x[0]), round(x[1]))
                        if key in seen_pairs:
                            continue
                        seen_pairs.add(key)
                        findings.append({
                            "kind": "edge-crosses-edge",
                            "at": (round(x[0], 1), round(x[1], 1)),
                            "line_a": p1.line, "line_b": p2.line,
                            "msg": f"paths at lines {p1.line} and {p2.line} cross at ({x[0]:.0f},{x[1]:.0f})",
                        })

    # 5. text bbox overlaps a component (other than its own)
    # Heuristic: text "owns" the component whose center is closest AND within
    # the component's expanded bbox.
    for t in texts:
        tx0, ty0, tx1, ty1 = t.bbox
        # find owning component
        owner = None
        for r in components:
            if r.contains_point(t.x, t.y, pad=2):
                owner = r; break
        for r in components:
            if r is owner:
                continue
            if not (tx1 <= r.x or r.x2 <= tx0 or ty1 <= r.y or r.y2 <= ty0):
                findings.append({
                    "kind": "label-overlaps-component",
                    "at": (round(t.x, 1), round(t.y, 1)),
                    "line_text": t.line, "line_rect": r.line,
                    "msg": f"text {t.text!r} at line {t.line} overlaps component at line {r.line}",
                })

    # 6. path passes through a label bbox (not its own)
    # Find each path's "own" label = nearest text within 4 lines below in source.
    own_label_line: dict[int, int] = {}
    for p in paths:
        for t in texts:
            if 0 < t.line - p.line <= 4:
                own_label_line[p.line] = t.line
                break
    for p in paths:
        own = own_label_line.get(p.line)
        for t in texts:
            if t.line == own:
                continue
            tx0, ty0, tx1, ty1 = t.bbox
            tw, th = tx1 - tx0, ty1 - ty0
            faux = Rect(tx0, ty0, tw, th, t.line, False)
            for s in p.segments:
                if seg_intersects_rect(s, faux):
                    findings.append({
                        "kind": "edge-crosses-label",
                        "at": (round(t.x, 1), round(t.y, 1)),
                        "line_path": p.line, "line_text": t.line,
                        "msg": f"path at line {p.line} crosses label {t.text!r} at line {t.line}",
                    })
                    break

    # 7. arrowhead reversed — tangent at path endpoint points AWAY from target rect interior
    for p in paths:
        if not p.segments:
            continue
        # find target rect: the component rect whose perimeter contains the path's end
        target = None
        for r in components:
            if r.point_on_perimeter(*p.end):
                target = r; break
        if target is None:
            continue
        # tangent at end = direction of last segment (parser flattens Q to control->end)
        last = p.segments[-1]
        dx, dy = last.x2 - last.x1, last.y2 - last.y1
        L = (dx*dx + dy*dy) ** 0.5
        if L < 1e-6:
            continue
        tx, ty = dx / L, dy / L
        ex, ey = p.end
        # inward normal of the rect at endpoint
        nx, ny = 0.0, 0.0
        if abs(ey - target.y) <= ENDPOINT_TOL: ny = 1   # on TOP edge → inward is +y (down)
        elif abs(ey - target.y2) <= ENDPOINT_TOL: ny = -1  # on BOTTOM → inward is -y (up)
        if abs(ex - target.x) <= ENDPOINT_TOL: nx = 1   # on LEFT edge → inward is +x (right)
        elif abs(ex - target.x2) <= ENDPOINT_TOL: nx = -1  # on RIGHT → inward is -x (left)
        if nx == 0 and ny == 0:
            continue
        # require tangent · inward normal > 0 (arrow pointing INTO rect)
        dot = tx * nx + ty * ny
        if dot <= 0.05:  # small slack for tangents that are perpendicular to inward (no info)
            findings.append({
                "kind": "arrowhead-reversed",
                "at": (round(ex, 1), round(ey, 1)),
                "line_path": p.line, "line_rect": target.line,
                "msg": f"path at line {p.line} ends at ({ex:.0f},{ey:.0f}) on rect (line {target.line}) but arrow tangent points away (dot={dot:+.2f})",
            })

    # 8. edge runs on top of a cluster border (visual merge)
    for cl in clusters:
        border_lines = [
            ("top",    cl.y,  "h", cl.x, cl.x2),
            ("bottom", cl.y2, "h", cl.x, cl.x2),
            ("left",   cl.x,  "v", cl.y, cl.y2),
            ("right",  cl.x2, "v", cl.y, cl.y2),
        ]
        for p in paths:
            for s in p.segments:
                for side, axis_v, orient, lo, hi in border_lines:
                    if orient == "h" and s.horizontal:
                        if abs(s.y1 - axis_v) > CLUSTER_BORDER_TOL: continue
                        sx_min, sx_max = sorted((s.x1, s.x2))
                        ov = min(sx_max, hi) - max(sx_min, lo)
                        if ov >= CLUSTER_BORDER_MIN_OVERLAP:
                            findings.append({
                                "kind": "edge-on-cluster-border",
                                "at": (round((max(sx_min, lo) + min(sx_max, hi)) / 2, 1), round(axis_v, 1)),
                                "line_path": p.line, "line_cluster": cl.line,
                                "msg": f"path at line {p.line} runs along cluster {side} border (line {cl.line}) for {ov:.0f}px — visually merges with the dashed boundary",
                            })
                    elif orient == "v" and s.vertical:
                        if abs(s.x1 - axis_v) > CLUSTER_BORDER_TOL: continue
                        sy_min, sy_max = sorted((s.y1, s.y2))
                        ov = min(sy_max, hi) - max(sy_min, lo)
                        if ov >= CLUSTER_BORDER_MIN_OVERLAP:
                            findings.append({
                                "kind": "edge-on-cluster-border",
                                "at": (round(axis_v, 1), round((max(sy_min, lo) + min(sy_max, hi)) / 2, 1)),
                                "line_path": p.line, "line_cluster": cl.line,
                                "msg": f"path at line {p.line} runs along cluster {side} border (line {cl.line}) for {ov:.0f}px — visually merges with the dashed boundary",
                            })

    return findings


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").split('\n', 1)[0])
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--ignore-edge-edge", action="store_true",
                    help="skip path-path crossing detection")
    args = ap.parse_args()
    with open(args.file) as f:
        text = f.read()
    if "<svg" in text:
        svg = text[text.index("<svg"):text.index("</svg>") + len("</svg>")]
    else:
        print("no <svg> element found", file=sys.stderr); sys.exit(2)
    findings = audit(svg, ignore_edge_edge=args.ignore_edge_edge)
    if args.json:
        print(json.dumps(findings, indent=2))
        sys.exit(1 if findings else 0)
    if not findings:
        print(f"clean — no geometry issues in {args.file}")
        sys.exit(0)
    by_kind: dict[str, list] = {}
    for f in findings:
        by_kind.setdefault(f["kind"], []).append(f)
    print(f"{len(findings)} issue(s) in {args.file}:\n")
    for kind, items in by_kind.items():
        print(f"  [{kind}]  x{len(items)}")
        for f in items:
            print(f"    - {f['msg']}  @ {f['at']}")
        print()
    sys.exit(1)


if __name__ == "__main__":
    main()
