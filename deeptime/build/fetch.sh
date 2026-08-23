#!/usr/bin/env bash
# Download the Muller et al. (2025) plate model into build/src/ (~5 MB).
# Nothing here is redistributed; only the derived files in ../data are committed.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p src && cd src

PMM=https://repo.gplates.org/webdav/pmm/muller2025
get () { [ -f "$2" ] || { echo "fetching $2"; curl -fL --retry 3 -o "$2" "$1"; }; }

for layer in Rotations Coastlines ContinentalPolygons StaticPolygons; do
  get "$PMM/$layer.zip" "$layer.zip"
  [ -d "$layer" ] || unzip -qo "$layer.zip"
done
echo "plate model ready in $(pwd)"
