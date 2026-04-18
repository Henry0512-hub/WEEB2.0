"""
Prefer the vendored Micro-sheep/efinance copy under ``vendor/efinance`` over PyPI.

Call ``ensure_vendored_efinance()`` before ``import efinance`` so the repo-pinned
source wins (fixes flaky/outdated pip installs).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_vendored_efinance() -> None:
    root = _project_root()
    vend = root / "vendor" / "efinance"
    marker = vend / "efinance" / "__init__.py"
    if not marker.is_file():
        return
    s = str(vend.resolve())
    if s not in sys.path:
        sys.path.insert(0, s)
