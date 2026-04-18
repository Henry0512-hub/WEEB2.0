"""One-off: embed static/industrial.css into templates/index.html"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
css = (ROOT / "static" / "industrial.css").read_text(encoding="utf-8")
html_path = ROOT / "templates" / "index.html"
html = html_path.read_text(encoding="utf-8")

needle = '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'industrial.css\') }}?v=20260410-2">\n'
replacement = "    <style>\n/* industrial.css (inlined — theme always applies) */\n" + css + "\n    </style>\n"

if needle not in html:
    raise SystemExit("Expected link line not found; edit needle in tools/inline_industrial_css.py")

html_path.write_text(html.replace(needle, replacement, 1), encoding="utf-8")
print("OK: industrial.css inlined into index.html")
