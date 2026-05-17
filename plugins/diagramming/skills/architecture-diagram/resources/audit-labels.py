#!/usr/bin/env python3
"""Audit arrow label placement in an architecture diagram HTML file.

Usage:
    python3 audit-labels.py <diagram>.html

For each <line> or <path> in the SVG, find the next <text> within 4 lines (the
label) and measure the distance from the label position to the arrow's curve
midpoint. Flag labels that are far from the midpoint without a leader line.

Distance budget:
  0  - 30 px : visually attached, no action needed
  30 - 150 px: requires a leader line for clarity
  > 150 px   : endpoint annotation pattern (intentionally far)
"""
import argparse
import re
import sys


def quadratic_midpoint(p0, p1, p2):
    """t=0.5 Bezier midpoint: P = 0.25·P0 + 0.5·P1 + 0.25·P2"""
    return (
        0.25 * p0[0] + 0.5 * p1[0] + 0.25 * p2[0],
        0.25 * p0[1] + 0.5 * p1[1] + 0.25 * p2[1],
    )


def cubic_midpoint(p0, p1, p2, p3):
    """t=0.5 cubic Bezier: 0.125·P0 + 0.375·P1 + 0.375·P2 + 0.125·P3"""
    return (
        0.125 * p0[0] + 0.375 * p1[0] + 0.375 * p2[0] + 0.125 * p3[0],
        0.125 * p0[1] + 0.375 * p1[1] + 0.375 * p2[1] + 0.125 * p3[1],
    )


def parse_path_midpoint(d):
    """Estimate midpoint of an SVG path given its `d` attribute string."""
    nums = re.findall(r'-?\d+(?:\.\d+)?', d)
    if not nums:
        return None
    if 'C' in d.upper() and len(nums) >= 8:
        p0 = (float(nums[0]), float(nums[1]))
        c1 = (float(nums[2]), float(nums[3]))
        c2 = (float(nums[4]), float(nums[5]))
        p1 = (float(nums[6]), float(nums[7]))
        return cubic_midpoint(p0, c1, c2, p1)
    if 'Q' in d.upper() and len(nums) >= 6:
        p0 = (float(nums[0]), float(nums[1]))
        cp = (float(nums[2]), float(nums[3]))
        p1 = (float(nums[4]), float(nums[5]))
        return quadratic_midpoint(p0, cp, p1)
    if len(nums) >= 4:
        # Treat as straight M...L: midpoint of endpoints
        return (
            (float(nums[0]) + float(nums[-2])) / 2,
            (float(nums[1]) + float(nums[-1])) / 2,
        )
    return None


def euclid(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def audit(path):
    with open(path) as f:
        content = f.read()
    if '<svg' not in content:
        print('No SVG found', file=sys.stderr)
        return 1
    svg = content[content.index('<svg'):content.index('</svg>')]
    lines = svg.split('\n')

    issues = []
    for i, line in enumerate(lines):
        m_path = re.search(r'<path\s+d="([^"]+)"', line)
        m_line = re.search(
            r'<line\s+x1="([^"]+)"\s+y1="([^"]+)"\s+x2="([^"]+)"\s+y2="([^"]+)"',
            line,
        )
        if not m_path and not m_line:
            continue
        if m_path:
            mid = parse_path_midpoint(m_path.group(1))
            arrow_kind = 'path'
        else:
            x1, y1, x2, y2 = map(float, m_line.groups())
            mid = ((x1 + x2) / 2, (y1 + y2) / 2)
            arrow_kind = 'line'
        if not mid:
            continue

        # Look for the next text element within 4 lines (the label)
        for j in range(i + 1, min(i + 5, len(lines))):
            m_text = re.search(
                r'<text\s+x="([0-9.]+)"\s+y="([0-9.]+)"[^>]*>([^<]+)</text>',
                lines[j],
            )
            if not m_text:
                continue
            tx, ty = float(m_text.group(1)), float(m_text.group(2))
            label = m_text.group(3).strip()
            if not label:
                break
            dist = euclid((tx, ty), mid)
            # Look for a leader line nearby (a short <line> within 5 lines after the text)
            has_leader = False
            for k in range(j + 1, min(j + 6, len(lines))):
                if re.search(
                    r'<line\s+x1=.*stroke-width="0\.[0-9]+"\s*[^>]*stroke-dasharray="2,2"',
                    lines[k],
                ):
                    has_leader = True
                    break
            issues.append({
                'distance': dist,
                'label': label,
                'arrow_kind': arrow_kind,
                'arrow_line': i + 1,
                'text_line': j + 1,
                'midpoint': mid,
                'label_pos': (tx, ty),
                'has_leader': has_leader,
            })
            break

    # Filter to real issues (distance > 30 AND no leader line)
    real = [i for i in issues if i['distance'] > 30 and not i['has_leader']]
    real.sort(key=lambda r: -r['distance'])

    print(f'Audited {len(issues)} labeled arrows.')
    print()
    if not real:
        print('All labels within 30 px of their arrow midpoint or have leader lines. ✓')
        return 0

    print(f'{len(real)} labels need attention:')
    print()
    for r in real:
        urgency = 'FIX' if r['distance'] < 150 else 'CHECK'
        kind_note = '(endpoint annotation?)' if r['distance'] > 150 else ''
        print(
            f"  [{urgency}] dist={r['distance']:.0f}px  {r['label']!r:50}  {kind_note}"
        )
        print(
            f"          arrow ({r['arrow_kind']}, line {r['arrow_line']})  "
            f"midpoint ({r['midpoint'][0]:.0f},{r['midpoint'][1]:.0f})  "
            f"label ({r['label_pos'][0]:.0f},{r['label_pos'][1]:.0f}) at line {r['text_line']}"
        )
    print()
    print('Action options for each:')
    print('  - Move the label closer to the midpoint (< 30 px)')
    print('  - Add a thin dashed leader line connecting label to nearest point on the curve')
    print('  - If > 150 px and intentional (endpoint annotation), add a leader line and move on')
    return 1


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    p.add_argument('file', help='HTML file containing an SVG architecture diagram')
    args = p.parse_args()
    sys.exit(audit(args.file))


if __name__ == '__main__':
    main()
