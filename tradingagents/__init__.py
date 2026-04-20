import os
import warnings

os.environ.setdefault("PYTHONUTF8", "1")

# Before transitive `import requests` (dependency warning noise on Windows pip mixes).
warnings.filterwarnings(
    "ignore",
    message=r".*doesn't match a supported version.*",
)

try:
    from urllib3.exceptions import NotOpenSSLWarning
except ImportError:
    NotOpenSSLWarning = None  # type: ignore[misc, assignment]

if NotOpenSSLWarning is not None:
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
