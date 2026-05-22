#!/bin/bash
# Bump cache-buster version across map-related files.
# Usage: ./scripts/bump-version.sh <new_version>
# Example: ./scripts/bump-version.sh 130
#
# Note: 2026-05-21 のサイト構成変更で、マップ画面は index.html から
# map.html に移動した (/ = 記事 hub、/map = マップ画面)。本スクリプトは
# マップ画面用のキャッシュバスタを管理する。

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <new_version>"
  exit 1
fi

NEW="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Extract current version from map.html (旧: index.html)
OLD=$(grep -oE 'src/app\.js\?v=[0-9]+' "$ROOT/map.html" | grep -oE '[0-9]+$')
if [ -z "$OLD" ]; then
  echo "ERROR: could not detect current version in map.html"
  exit 1
fi

if [ "$OLD" = "$NEW" ]; then
  echo "Already at v=$NEW, nothing to do"
  exit 0
fi

echo "Bumping ?v=$OLD -> ?v=$NEW"

for f in "$ROOT/map.html" "$ROOT/src/app.js" "$ROOT/src/data.js"; do
  sed -i '' "s/?v=$OLD/?v=$NEW/g" "$f"
  echo "  updated: $f"
done

echo "Done. Don't forget to commit and push."
