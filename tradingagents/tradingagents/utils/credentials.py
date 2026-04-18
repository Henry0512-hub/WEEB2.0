"""
统一从 is/ 目录与环境变量加载 WRDS 与 LLM 密钥。
WRDS：环境变量 WRDS_USERNAME / WRDS_PASSWORD >（可选 WRDS_ID_FILE）> is/wrds.txt
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv

    _DOTENV = True
except ImportError:
    _DOTENV = False


def _maybe_load_dotenv() -> None:
    if _DOTENV:
        root = get_project_root()
        load_dotenv(root / ".env")
        load_dotenv(root / "is" / ".env")


def get_project_root() -> Path:
    """TradingAgents 项目根目录（含 is/ 的目录）。"""
    return Path(__file__).resolve().parent.parent.parent


def get_is_dir() -> Path:
    return get_project_root() / "is"


def _clean_credential_value(value: str) -> str:
    """
    Normalize credential tokens from txt/env:
    - trim whitespace/quotes
    - tolerate accidental trailing comma/semicolon in copied snippets
    """
    s = (value or "").strip().strip('"').strip("'").strip()
    while s.endswith(",") or s.endswith(";"):
        s = s[:-1].rstrip()
    return s


def _wrds_credentials_file_candidates() -> List[Path]:
    """WRDS 凭据文件：可选 WRDS_ID_FILE，否则使用项目 is/wrds.txt。"""
    out: List[Path] = []
    for key in ("WRDS_ID_FILE", "WRDS_CREDENTIALS_FILE"):
        raw = (os.environ.get(key) or "").strip()
        if raw:
            out.append(Path(raw).expanduser())
    out.append(get_is_dir() / "wrds.txt")
    # 去重且保持顺序
    seen: set[str] = set()
    uniq: List[Path] = []
    for p in out:
        s = str(p.resolve()) if p.is_absolute() else str(p)
        if s in seen:
            continue
        seen.add(s)
        uniq.append(p)
    return uniq


def _parse_wrds_id_file(path: Path) -> Optional[Dict[str, str]]:
    """
    解析 WRDS 凭据文件：
    - key-value：username / user、password / pass（与 _parse_kv_file 一致）
    - 两行式：第一行用户名、第二行密码（可含 # 注释行）
    """
    if not path.is_file():
        return None
    kv = _parse_kv_file(path)
    username = _clean_credential_value(kv.get("username") or kv.get("user") or "")
    password = _clean_credential_value(kv.get("password") or kv.get("pass") or "")
    if username and password:
        return {"username": username, "password": password}
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return None
    lines: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    if len(lines) >= 2:
        return {
            "username": _clean_credential_value(lines[0]),
            "password": _clean_credential_value(lines[1]),
        }
    return None


def load_wrds_credentials() -> Optional[Dict[str, str]]:
    """
    返回 {"username": str, "password": str}，未配置时返回 None。

    优先级：
    1. 环境变量 WRDS_USERNAME / WRDS_USER，WRDS_PASSWORD
    2. 项目根下 **is/wrds.txt**（或 WRDS_ID_FILE / WRDS_CREDENTIALS_FILE 指向的文件）

    文件格式：username / password 键值对，或两行分别为用户名、密码。
    """
    _maybe_load_dotenv()

    u = _clean_credential_value(os.environ.get("WRDS_USERNAME") or os.environ.get("WRDS_USER") or "")
    p = _clean_credential_value(os.environ.get("WRDS_PASSWORD") or "")
    if u and p:
        return {"username": u, "password": p}

    for path in _wrds_credentials_file_candidates():
        creds = _parse_wrds_id_file(path)
        if creds:
            return creds
    return None


def load_alpha_vantage_api_key() -> Optional[str]:
    """
    Alpha Vantage API key for https://www.alphavantage.co/

    优先级：环境变量 ALPHA_VANTAGE_API_KEY > is/av api.txt
    文件可为单行密钥，或 apikey: xxx / key: xxx
    """
    _maybe_load_dotenv()
    k = (os.environ.get("ALPHA_VANTAGE_API_KEY") or "").strip()
    if k:
        return k
    path = get_is_dir() / "av api.txt"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        return None
    key_names = ("apikey", "api_key", "key", "alpha_vantage", "alphavantage", "av_key")
    for line in lines:
        for sep in (":", "=", ","):
            if sep not in line:
                continue
            a, b = line.split(sep, 1)
            if a.strip().lower() in key_names:
                return b.strip().strip('"').strip("'")
    # 整行即密钥
    return lines[0].strip().strip('"').strip("'")


def _parse_kv_file(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.is_file():
        return out
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, val = None, None
            for sep in (":", ",", "="):
                if sep in line:
                    key, val = line.split(sep, 1)
                    break
            if key is None:
                continue
            k = key.strip().lower()
            v = _clean_credential_value(val)
            out[k] = v
    return out


def _env_llm_key_usable(value: str) -> bool:
    """环境变量里的密钥若为占位符或过短，则不要用其覆盖 is/api assents.txt。"""
    s = value.strip()
    # 不强制 sk- 前缀，避免不同平台/网关格式被误判
    if len(s) < 12:
        return False
    low = s.lower()
    if (
        "your-" in low
        or "placeholder" in low
        or "your_api_key" in low
        or "replace_me" in low
        or "example" in low
    ):
        return False
    return True


def _env_gemini_key_usable(value: str) -> bool:
    s = value.strip()
    if len(s) < 20:
        return False
    # 不强制 AIza 前缀，兼容代理网关/转发平台密钥格式
    low = s.lower()
    if (
        "your-" in low
        or "placeholder" in low
        or "your_api_key" in low
        or "replace_me" in low
        or "example" in low
    ):
        return False
    return True


def load_llm_api_keys() -> Dict[str, str]:
    """
    读取 is/api assents.txt，并由环境变量覆盖。

    支持的键：deepseek, kimi, gemini（小写）
    环境变量：DEEPSEEK_API_KEY, KIMI_API_KEY / MOONSHOT_API_KEY, GEMINI_API_KEY / GOOGLE_API_KEY
    """
    _maybe_load_dotenv()

    keys = _parse_kv_file(get_is_dir() / "api assents.txt")
    if "google gemini" in keys:
        keys["gemini"] = keys.pop("google gemini")

    ds = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if ds and _env_llm_key_usable(ds):
        keys["deepseek"] = ds
    km = (os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY") or "").strip()
    if km and _env_llm_key_usable(km):
        keys["kimi"] = km
    gm = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if gm and _env_gemini_key_usable(gm):
        keys["gemini"] = gm

    return keys
