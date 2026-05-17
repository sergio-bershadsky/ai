#!/usr/bin/env python3
"""Add vertical space between root-level blocks in an architecture diagram.

Usage:
    python3 coordinate-shifter.py <diagram>.html --tiers "260:120,985:60,1700:90"

The --tiers argument is a comma-separated list of `boundary_y:delta` pairs.
Every y-coordinate at or above each boundary gets shifted by the cumulative
delta. The viewBox height is grown to match.

Example: --tiers "260:120,985:60,1700:90"
  - y < 260      : no shift           (top context band stays)
  - 260 ≤ y < 985: shift by +120      (control plane drops)
  - 985 ≤ y < 1700: shift by +180     (fan-out / region drops more)
  - y ≥ 1700     : shift by +270      (legend drops most)

Handles y=, y1=, y2=, cy= attributes AND y-coordinates inside `d="..."` path
commands for absolute commands (M, L, T, C, S, Q, V, A — uppercase only).
"""
import argparse
import re
import sys
from pathlib import Path


def build_shift_fn(tiers):
    """tiers = sorted list of (boundary_y, delta) -> shift function."""
    boundaries = sorted(tiers, key=lambda t: t[0])

    def shift(y):
        y = float(y)
        cumulative = 0
        for boundary, delta in boundaries:
            if y >= boundary:
                cumulative += delta
        return y + cumulative

    return shift


def shift_attributes(svg, shift_fn):
    """Shift y= y1= y2= cy= attributes."""

    def repl(m):
        attr = m.group(1)
        num = m.group(2)
        new = shift_fn(num)
        if '.' not in num:
            return f'{attr}="{int(new)}"'
        return f'{attr}="{new}"'

    return re.sub(r'\b(y|y1|y2|cy)="([0-9]+(?:\.[0-9]+)?)"', repl, svg)


def shift_path_d(svg, shift_fn):
    """Shift y-coordinates inside absolute SVG path commands."""

    def repl_path(m):
        d = m.group(1)
        tokens = re.findall(r'[MLHVCSQTAZmlhvcsqtaz]|-?[0-9]+(?:\.[0-9]+)?', d)
        out = []
        cmd = None
        coord_index = 0
        for tok in tokens:
            if re.fullmatch(r'[MLHVCSQTAZmlhvcsqtaz]', tok):
                cmd = tok
                out.append(tok)
                coord_index = 0
                continue
            try:
                val = float(tok)
            except ValueError:
                out.append(tok)
                continue
            is_y = False
            if cmd in ('M', 'L', 'T', 'C', 'S', 'Q'):
                is_y = (coord_index % 2 == 1)
                coord_index += 1
            elif cmd == 'V':
                is_y = True
                coord_index += 1
            elif cmd == 'H':
                is_y = False
                coord_index += 1
            elif cmd == 'A':
                is_y = (coord_index % 7 == 6)
                coord_index += 1
            else:
                # lowercase = relative, don't shift; or unknown
                coord_index += 1
            if is_y and cmd and cmd.isupper():
                new = shift_fn(val)
                out.append(str(int(new)) if '.' not in tok else str(new))
            else:
                out.append(tok)
        return f'd="{" ".join(out)}"'

    return re.sub(r'\bd="([^"]+)"', repl_path, svg)


def grow_viewbox(svg, total_shift):
    """Grow the SVG viewBox height by total_shift px."""

    def repl(m):
        parts = m.group(1).split()
        if len(parts) == 4:
            parts[3] = str(int(float(parts[3]) + total_shift))
        return f'viewBox="{" ".join(parts)}"'

    return re.sub(r'viewBox="([^"]+)"', repl, svg)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    p.add_argument('file', help='HTML file containing an SVG diagram')
    p.add_argument(
        '--tiers',
        required=True,
        help='Comma-separated list of boundary_y:delta pairs, e.g. "260:120,985:60,1700:90"',
    )
    p.add_argument(
        '--dry-run', action='store_true', help='Print the resulting file to stdout instead of writing'
    )
    args = p.parse_args()

    # Parse tiers
    tiers = []
    for pair in args.tiers.split(','):
        boundary, delta = pair.split(':')
        tiers.append((float(boundary), float(delta)))

    shift_fn = build_shift_fn(tiers)
    total_shift = sum(d for _, d in tiers)

    content = Path(args.file).read_text()
    if '<svg' not in content:
        print('No SVG found', file=sys.stderr)
        return 1

    svg_start = content.index('<svg')
    svg_end = content.index('</svg>') + len('</svg>')
    before = content[:svg_start]
    svg = content[svg_start:svg_end]
    after = content[svg_end:]

    svg = shift_attributes(svg, shift_fn)
    svg = shift_path_d(svg, shift_fn)
    svg = grow_viewbox(svg, total_shift)

    out = before + svg + after
    if args.dry_run:
        print(out)
    else:
        Path(args.file).write_text(out)
        print(f'Shifted {Path(args.file).name} (total +{total_shift:g}px). viewBox grown.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
