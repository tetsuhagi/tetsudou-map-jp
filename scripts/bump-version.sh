#!/bin/bash
# Bump cache-buster version across all files.
# Usage: ./scripts/bump-version.sh <new_version>
# Example: ./scripts/bump-version.sh 40

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <new_version>"
  exit 1
fi

NEW="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Extract current version from index.html
OLD=$(grep -oE 'src/app\.js\?v=[0-9]+' "$ROOT/index.html" | grep -oE '[0-9]+$')
if [ -z "$OLD" ]; then
  echo "ERROR: could not detect current version in index.html"
  exit 1
fi

if [ "$OLD" = "$NEW" ]; then
  echo "Already at v=$NEW, nothing to do"
  exit 0
fi

echo "Bumping ?v=$OLD -> ?v=$NEW"

for f in "$ROOT/index.html" "$ROOT/src/app.js" "$ROOT/src/data.js"; do
  sed -i '' "s/?v=$OLD/?v=$NEW/g" "$f"
  echo "  updated: $f"
done

echo "Done. Don't forget to commit and push."
