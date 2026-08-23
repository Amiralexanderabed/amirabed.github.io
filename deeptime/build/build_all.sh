#!/usr/bin/env bash
# Regenerate everything in deeptime/data.  Order matters: fossils.py records
# which plates its localities ride on, and plates.py needs that list so those
# plates get rotation samples.
set -euo pipefail
cd "$(dirname "$0")"
[ -d src/Rotations ] || { echo "run ./fetch.sh first"; exit 1; }
python3 chapters.py     # narrative + climate curves      -> data/chapters.json
python3 fossils.py      # Paleobiology Database           -> data/ch/*.json
python3 plates.py       # geometry + rotations            -> data/plates.{bin,json}
python3 images.py       # Wikipedia photo lookups         -> data/images.json
echo
echo "-- rebuilt --  now bump DATA_VERSION in ../deeptime.js"
