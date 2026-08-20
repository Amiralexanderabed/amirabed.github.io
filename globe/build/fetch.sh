#!/usr/bin/env bash
# Download the four source datasets into build/src/ (~200 MB, none are redistributed).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p src && cd src

get () { [ -f "$2" ] || { echo "fetching $2"; curl -fL --retry 3 -o "$2" "$1"; }; }

get "https://storage.googleapis.com/teow2016/Ecoregions2017.zip" Ecoregions2017.zip
get "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_tavg.zip" wc_tavg.zip
get "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_prec.zip" wc_prec.zip
get "https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73909/world.topo.bathy.200412.3x21600x10800.jpg" bluemarble.jpg
get "https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73934/gebco_08_rev_elev_21600x10800.png" gebco.png

[ -d eco ] || unzip -q Ecoregions2017.zip -d eco
[ -d wc ]  || { unzip -q wc_tavg.zip -d wc; unzip -q wc_prec.zip -d wc; }
echo "sources ready in $(pwd)"
