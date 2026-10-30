#!/bin/bash
# Rebuild data and publish to GitHub Pages (main branch, /docs not used: Pages serves gh-pages branch = public/)
set -e; cd "$(dirname "$0")"
python3 scripts/build.py
git add -A; git commit -qm "data update $(TZ=Asia/Taipei date '+%F %T')" || true
git push -q origin main
git subtree split --prefix public -b gh-pages-tmp >/dev/null
git push -qf origin gh-pages-tmp:gh-pages; git branch -D gh-pages-tmp >/dev/null
