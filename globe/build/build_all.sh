#!/usr/bin/env bash
# Regenerate every file in globe/data from build/src. Order matters:
# climate.py and finalize.py both read what rasterize_eco.py writes.
set -euo pipefail
cd "$(dirname "$0")"
[ -d src ] || { echo "run ./fetch.sh first"; exit 1; }
python3 rasterize_eco.py
python3 rasterize_marine.py
python3 climate.py
python3 finalize.py
python3 terrain.py
python3 build_biota.py
python3 images.py
echo "-- data rebuilt --"
