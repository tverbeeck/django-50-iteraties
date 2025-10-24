"""
Genereer wiki-achtige HTML docs met pdoc (versie-onafhankelijk via CLI).
"""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]  # D:\Django
DOCS = ROOT / "docs"

# Zorg dat .nojekyll bestaat
(DOCS / ".nojekyll").write_text("", encoding="ascii")

# Run pdoc CLI: -o docs, met Google-stijl voor docstrings
cmd = [
    sys.executable,
    "-m",
    "pdoc",
    "-o",
    str(DOCS),
    "-d",
    "google",
    "siteproject",
    "home",
    "notes",
]
subprocess.run(cmd, check=True)
print("Docs gegenereerd in ./docs")
