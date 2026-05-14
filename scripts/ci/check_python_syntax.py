#!/usr/bin/env python3
"""AST-parse every .py file under plugins/ and scripts/ to catch syntax errors.

This is the floor: even files we don't lint with ruff must at minimum parse
as valid Python. Ruff itself is scoped to scripts/ where we own all the code.

Exits 0 on success, 1 if any file fails to parse.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    targets: list[Path] = []
    for sub in ("plugins", "scripts"):
        targets.extend((ROOT / sub).glob("**/*.py"))

    fail = 0
    for path in sorted(targets):
        try:
            ast.parse(path.read_text())
        except SyntaxError as exc:
            sys.stderr.write(f"FAIL: {path.relative_to(ROOT)}: {exc}\n")
            fail += 1

    if fail:
        sys.exit(1)
    print(f"{len(targets)} Python file(s) parse cleanly.")


if __name__ == "__main__":
    main()
