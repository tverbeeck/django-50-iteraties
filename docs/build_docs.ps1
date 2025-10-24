# pdoc-buildscript voor wiki-achtige HTML uit docstrings
# Gebruik:  ./docs/build_docs.ps1
# Output:   ./docs/ (GitHub Pages-ready via /docs op main)

$ErrorActionPreference = "Stop"

# Zorg dat GitHub Pages niets “jekyllt”
"" | Out-File -FilePath "docs/.nojekyll" -Encoding ascii

# (optioneel) opruimen van oude HTML (pdoc overschrijft meestal prima zonder deze stap)
# Get-ChildItem docs -Include *.html -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue

# Genereer documentatie voor je pakketten (pdoc v14+)
# -o docs  => schrijf HTML-bestanden in ./docs
# -d google => (optioneel) docstringstijl; kies 'google', 'numpy' of 'restructuredtext'
pdoc `
  -o docs `
  -d google `
  siteproject `
  home `
  notes

Write-Host "Docs gegenereerd in ./docs. Open docs/index.html"
