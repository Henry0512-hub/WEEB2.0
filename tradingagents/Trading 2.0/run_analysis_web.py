"""
Web 分析子进程入口：先应用 Trading 2.0 补丁，再执行上级目录的 run_analysis_web.py。
由 start_web.py 通过 monkeypatch 的 subprocess 调用，勿单独移动此文件路径。
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

    target = os.path.join(_ROOT, "run_analysis_web.py")
    sys.argv[0] = target
    runpy.run_path(target, run_name="__main__")
