"""
Trading 2.0 — 交互式 CLI（run_integrated_analysis.py），无加密货币支持。
用法: python "Trading 2.0/start_cli.py"
"""
from __future__ import annotations

import os
import runpy
import sys

_T20 = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_T20, ".."))

if __name__ == "__main__":
    os.chdir(_ROOT)
    if _T20 not in sys.path:
        sys.path.insert(0, _T20)
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

    from bootstrap import apply_no_crypto_patch

    apply_no_crypto_patch()

    target = os.path.join(_ROOT, "run_integrated_analysis.py")
    sys.argv[0] = target
    runpy.run_path(target, run_name="__main__")
