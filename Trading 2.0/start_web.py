"""
Trading 2.0 — Web 启动器（与主项目功能一致，但不包含加密货币分析）。

用法（在仓库根目录）:
  python "Trading 2.0/start_web.py"
环境变量 PORT 可改端口（默认 5000）。
"""
from __future__ import annotations

import os
import subprocess
import sys

_T20 = os.path.abspath(os.path.dirname(__file__))
_ROOT = os.path.abspath(os.path.join(_T20, ".."))

os.chdir(_ROOT)
if _T20 not in sys.path:
    sys.path.insert(0, _T20)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# 1) 子进程会执行 Trading 2.0/run_analysis_web.py — 先 patch Popen，再 import web_backend
_wrapped = subprocess.Popen


def _popen_trading20(*args, **kwargs):
    cmd = args[0] if args else None
    if isinstance(cmd, (list, tuple)):
        cmd = list(cmd)
        alt = os.path.join(_T20, "run_analysis_web.py")
        for i, part in enumerate(cmd):
            s = os.path.normpath(str(part))
            if s.endswith(os.path.normpath("run_analysis_web.py")) and "Trading 2.0" not in s:
                cmd[i] = alt
                break
        args = (cmd,) + tuple(args[1:])
    return _wrapped(*args, **kwargs)


subprocess.Popen = _popen_trading20

# 2) 分析管线补丁（与 web 子进程一致）
from bootstrap import apply_no_crypto_patch

apply_no_crypto_patch()

import web_backend

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 12 + "Trading 2.0 — Web（无加密货币）")
    print("=" * 80)
    print()
    print("访问: http://localhost:%s" % os.environ.get("PORT", "5000"))
    print()
    _dev = os.environ.get("NTCA_DEV", "").strip().lower() in ("1", "true", "yes", "on")
    web_backend.app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=_dev,
        use_reloader=_dev,
    )
