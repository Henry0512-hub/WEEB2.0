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

# 1) 子进程改为执行 Trading 2.0/run_analysis_web.py
# 必须用「类」替换 Popen：若换成普通函数，asyncio 里 `class Popen(subprocess.Popen)` 会崩溃（Python 3.13）。
class _PopenTrading20(subprocess.Popen):
    def __init__(self, args, *pargs, **kwargs):
        if isinstance(args, (list, tuple)):
            args = list(args)
            alt = os.path.join(_T20, "run_analysis_web.py")
            for i, part in enumerate(args):
                s = os.path.normpath(str(part))
                if s.endswith(os.path.normpath("run_analysis_web.py")) and "Trading 2.0" not in s:
                    args[i] = alt
                    break
        super().__init__(args, *pargs, **kwargs)


subprocess.Popen = _PopenTrading20

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
