"""
NTCA Platform — prefetch daily bars into data/ntca/ntca_bars.sqlite3

  python prefetch_ntca.py

US: WRDS CRSP first; if unavailable, Yahoo Finance for the same window.
A-share / HK: efinance / Yahoo Finance (WRDS path in this repo targets US CRSP only).
"""
from ntca_platform.prefetch import run_prefetch

if __name__ == "__main__":
    run_prefetch()
