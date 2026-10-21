#!/usr/bin/env bash
# Assemble the GitHub Pages site into _site/ (git-ignored).
#   /         pages/index.html (home page linking both tracks)
#   /atlas/   atlas/site/ without its design/ working folder
#   /pharma/  pharma/report/index.html (self-contained report)
# Used by .github/workflows/pages.yml; run locally to preview the same output.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/_site"

rm -rf "$out"
mkdir -p "$out/atlas" "$out/pharma"

cp "$root/pages/index.html" "$out/index.html"
rsync -a --exclude design/ --exclude .DS_Store "$root/atlas/site/" "$out/atlas/"
cp "$root/pharma/report/index.html" "$out/pharma/index.html"

echo "Built $out"
