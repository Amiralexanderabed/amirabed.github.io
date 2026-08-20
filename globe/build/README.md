# Building `globe/data`

Everything the globe loads is derived from four public datasets. The sources are
large (~200 MB) and are **not** committed; only the derived textures in
`globe/data/` are. Regenerate them with:

```bash
python3 -m pip install numpy pillow pyshp
./fetch.sh        # download sources into build/src/ (~200 MB, one time)
./build_all.sh    # regenerate everything in ../data
```

`build_all.sh` runs the steps in the order they depend on each other:

| Step | Writes |
|---|---|
| `rasterize_eco.py` | `ecoregions.png`, `ecoregions.json`, `src/eco_grid.npy` |
| `rasterize_marine.py` | `marine.png`, `marine.json` |
| `climate.py` | `climate_a.png`, `climate_b.png`, per-ecoregion climate stats |
| `finalize.py` | representative points + Köppen legend into `ecoregions.json` |
| `terrain.py` | `basemap.jpg`, `relief.png` |
| `build_biota.py` | `biota.json`, `src/species_index.json` |
| `images.py` | `species_images.json` (Wikimedia lookups, cached in `src/`) |

Order matters — `climate.py` and `finalize.py` both read files
`rasterize_eco.py` writes, and rerunning the rasteriser alone will leave
`ecoregions.json` without its climate fields.

## Sources

| Dataset | Used for | Licence |
|---|---|---|
| [RESOLVE Ecoregions 2017](https://ecoregions.appspot.com/) | 846 land ecoregions, biome, realm, protection status | CC BY 4.0 |
| [MEOW + PPOW](https://data.unep-wcmc.org/datasets/38) (Spalding 2007/2012) | 232 marine ecoregions + 37 pelagic provinces | UNEP-WCMC general terms |
| [WorldClim 2.1](https://www.worldclim.org/) (10 arc-min monthly tavg + prec) | temperature, rainfall, Köppen classes | free for non-commercial use |
| [NASA Blue Marble Next Generation](https://visibleearth.nasa.gov/collection/1484/blue-marble) | surface imagery | public domain |
| [GEBCO / NASA elevation](https://visibleearth.nasa.gov/images/73934/) | hillshading | public domain |

## Output formats

- **`ecoregions.png`** — 4096×2048 equirectangular. `R + G*256` is the 1-based
  ecoregion index (0 = ocean or ice); `B` is the biome number. The app uploads
  it as `RG8` and samples it with `texelFetch`, so it must never be filtered.
- **`marine.png`** — same grid and encoding, indexing `marine.json`. Pelagic
  provinces are painted first and shelf ecoregions over them, and anything
  falling on land is cleared so the two rasters never overlap.
- **`species_images.json`** — `{binomial: {u: thumbnail URL, a: author,
  l: licence}}`. Photos are hotlinked from Wikimedia Commons, never copied into
  the repo; the page credits author and licence on hover.
- **`climate_a.png` / `climate_b.png`** — 2048×1024. `a` = Köppen class, annual
  mean temp, annual precipitation; `b` = coldest-month temp, warmest-month temp,
  driest-month precipitation. Temperatures are `(°C + 60) × 2`; precipitation is
  `log1p(mm) / log1p(12000) × 255`.
- **`relief.png`** — 2160×1080, height as a 16-bit value split across R (high
  byte) and G (low byte). Relative shading only: the source clamps below sea
  level and saturates near 6,300 m.
- **`ecoregions.json`** — per-ecoregion name, biome, realm, protection status,
  area, mean climate, and a representative lat/lon guaranteed to fall inside the
  region.
- **`biota.json`** — biome and realm descriptions plus curated species lists
  keyed by realm+biome code. Codes that span disjoint regions (`PA05` covers both
  the Alps and the Hengduan Mountains) carry `variants` with a lon/lat box; the
  first box containing the clicked point wins.

## Köppen classification

`climate.py` implements Peel, Finlayson & McMahon (2007) from the 12 monthly
WorldClim layers, with summer/winter chosen per hemisphere. Spot-checked against
known cities it agrees exactly for 12 of 14; Reykjavík and Nairobi land one class
away because the 10 arc-min cell straddles a boundary, not because of the
algorithm.
