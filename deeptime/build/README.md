# Building `deeptime/data`

Four scripts produce everything the page loads. The sources they pull from are
not committed; only the derived files in `deeptime/data/` are.

```bash
python3 -m pip install numpy pillow
./fetch.sh        # download the plate model into build/src/ (~5 MB, one time)
./build_all.sh    # regenerate everything in ../data
```

| Step | Reads | Writes |
|---|---|---|
| `chapters.py` | the authored text and curves in the file itself | `chapters.json` |
| `fossils.py` | Paleobiology Database API | `ch/*.json`, `src/fossil_plates.json` |
| `plates.py` | `src/` plate model + `src/fossil_plates.json` | `plates.bin`, `plates.json` |
| `images.py` | Wikipedia + Commons APIs | `images.json` |

`validate_rotations.py` is a check, not a build step; run it after touching
`rotmodel.py`.

**Order matters.** `fossils.py` writes the list of plates its localities sit on,
and `plates.py` unions that into the set it samples rotations for. Run
`plates.py` alone and any locality on a plate with no coastline of its own will
have nowhere to ride.

After a rebuild, bump `DATA_VERSION` in `../deeptime.js`: these files are served
with far-future caching and browsers will otherwise keep the old copies.

`fossils.py` caches every API response under `src/pbdb/` and `images.py` caches
lookups in `src/img_cache.json`, so re-runs are cheap. A full cold run takes
about 25 minutes, nearly all of it waiting on the Paleobiology Database.

## How the globe moves

The page never downloads a map per time step. It downloads the present-day
outlines once, each polygon tagged with the tectonic plate it rides on, plus a
table of rotations sampled through time. Every frame it slerps each plate's
rotation to the current age and spins the vertices into place, so drift is
continuous rather than a cross-fade between stills.

`rotmodel.py` implements the finite-rotation composition: a `.rot` line gives a
plate's rotation relative to some *other* plate, so placing one on the globe
means walking the chain of fixed plates up to the spin axis, slerping within
each sequence and handling crossovers where the anchor changes. `validate_rotations.py` proves the result against the GPlates Web Service: it
reconstructs the muller2022 coastlines (the newest model that service serves)
with this code and compares vertex by vertex at 100, 250, 450 and 800 Ma. The
median disagreement is 0.000035°, which is the rounding floor of the service's
own output. One vertex sits 0.006° (600 m) out, on the Falkland block at exactly
250 Ma, where the published rotation file changes which plate that block is
measured against and the two sequences meeting at the crossover disagree
slightly — a property of the file rather than of this code.

`plates.py` simplifies each outline with Douglas–Peucker and triangulates it by
ear clipping in a gnomonic projection centred on the polygon, where great
circles are straight lines so the planar algorithm is exact. Simplification can
make a simple ring self-intersect, which sends ear clipping outside the
polygon, so the tolerance is backed off per ring until the ring is simple again;
the build asserts that triangulated area matches polygon area.

## Sources

| Dataset | Used for | Licence |
|---|---|---|
| [Müller et al. 2025 plate model](https://repo.gplates.org/webdav/pmm/) | coastlines, continental crust, static polygons, rotations, 0–1800 Ma | CC BY 4.0 |
| [Paleobiology Database](https://paleobiodb.org/) | fossil localities, taxa, diversity | CC BY 4.0 |
| Wikipedia / Wikimedia Commons | photographs, hotlinked with author and licence | per file |

Climate curves are digitised control points typed into `chapters.py`, with the
publications they came from listed in `SOURCES` and shown on the page. They are
indicative, not the source data, and the page says so.

## Output formats

- **`plates.bin`** — one blob of typed arrays described by the `sections` table
  in `plates.json`. `pos` is Int16 unit vectors (present-day), `fid` the polygon
  each vertex belongs to, `idx` triangles (`land` and `shelf` ranges), `feat*`
  the plate and age window per polygon, and `rot*` the per-plate rotation
  samples as Int16 quaternions with times in half-million-year steps.
- **`ch/<chapter>.json`** — up to 1,000 localities thinned to cover the map,
  each with its present-day position, plate, age window and taxon list, plus the
  chapter's 600 commonest genera and a breakdown by group. Localities carry
  modern coordinates and a plate id, not paleo-coordinates, so the page can
  place them at whatever age it is showing.
- **`images.json`** — `{"sp:Name"|"sc:Title": {u, a, l, c}}`: thumbnail URL,
  author, licence, and for scenes a caption. Photos are hotlinked from
  Wikimedia, never copied into this repository.
