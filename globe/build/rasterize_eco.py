"""Rasterize RESOLVE Ecoregions 2017 to an equirectangular index raster.

Output: globe/data/ecoregions.png  (R = idx & 255, G = idx >> 8, B = biome_num)
        globe/data/ecoregions.json (index -> {name, biome, realm, ...})
idx 0 means "no terrestrial ecoregion" (ocean / rock & ice).
"""
import json, sys
import numpy as np
import shapefile
from PIL import Image, ImageDraw

import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))

W, H = 4096, 2048
SHP = os.path.join(SRC, 'eco', 'Ecoregions2017')

REALM_NAMES = {
    'AF': 'Afrotropic', 'AN': 'Antarctica', 'AU': 'Australasia', 'IN': 'Indomalayan',
    'NA': 'Nearctic', 'NE': 'Nearctic', 'NO': 'Neotropic', 'OC': 'Oceania', 'PA': 'Palearctic',
}

def lonlat_to_px(lons, lats):
    x = (lons + 180.0) / 360.0 * W
    y = (90.0 - lats) / 180.0 * H
    return x, y

def unwrap_lons(lons):
    """Make a ring continuous across the antimeridian."""
    out = lons.copy()
    d = np.diff(out)
    shift = np.zeros(len(out))
    acc = 0.0
    for i, dd in enumerate(d):
        if dd > 180.0:
            acc -= 360.0
        elif dd < -180.0:
            acc += 360.0
        shift[i + 1] = acc
    return out + shift

def main():
    r = shapefile.Reader(SHP, encoding='latin-1')
    fn = [f[0] for f in r.fields[1:]]
    records = [dict(zip(fn, x)) for x in r.records()]
    n = len(records)
    print(f'{n} ecoregions', flush=True)

    grid = np.zeros((H, W), dtype=np.uint16)

    # Draw largest first so small ecoregions (islands, enclaves) survive on top.
    order = sorted(range(n), key=lambda i: -float(records[i]['SHAPE_AREA']))
    painted = np.zeros(n + 1, dtype=np.int64)

    for count, si in enumerate(order):
        shp = r.shape(si)
        idx = si + 1
        pts = np.asarray(shp.points, dtype=np.float64)
        if len(pts) == 0:
            continue
        parts = list(shp.parts) + [len(pts)]

        rings = []
        for p in range(len(parts) - 1):
            ring = pts[parts[p]:parts[p + 1]]
            if len(ring) < 3:
                continue
            lons = ring[:, 0]
            if lons.max() - lons.min() > 180.0:
                lons = unwrap_lons(lons)
            x, y = lonlat_to_px(lons, ring[:, 1])
            rings.append((x, y))
        if not rings:
            continue

        x0 = min(rx.min() for rx, ry in rings)
        x1 = max(rx.max() for rx, ry in rings)
        y0 = min(ry.min() for rx, ry in rings)
        y1 = max(ry.max() for rx, ry in rings)
        ix0, iy0 = int(np.floor(x0)) - 1, max(0, int(np.floor(y0)) - 1)
        ix1, iy1 = int(np.ceil(x1)) + 1, min(H, int(np.ceil(y1)) + 1)
        bw, bh = ix1 - ix0, iy1 - iy0
        if bw <= 0 or bh <= 0:
            continue
        # Guard against pathological bboxes
        if bw > 4 * W:
            continue

        # Even-odd fill across all rings => holes handled regardless of winding.
        acc = np.zeros((bh, bw), dtype=bool)
        for rx, ry in rings:
            img = Image.new('1', (bw, bh), 0)
            d = ImageDraw.Draw(img)
            poly = list(zip((rx - ix0).tolist(), (ry - iy0).tolist()))
            d.polygon(poly, fill=1, outline=1)
            acc ^= np.array(img, dtype=bool)

        ys, xs = np.nonzero(acc)
        if len(ys) == 0:
            # Too small to hit a pixel centre - stamp the centroid.
            cx = int(round((x0 + x1) * 0.5)) % W
            cy = min(H - 1, max(0, int(round((y0 + y1) * 0.5))))
            grid[cy, cx] = idx
            painted[idx] = 1
            continue
        gy = ys + iy0
        gx = (xs + ix0) % W
        keep = (gy >= 0) & (gy < H)
        grid[gy[keep], gx[keep]] = idx
        painted[idx] = int(keep.sum())

        if count % 100 == 0:
            print(f'  {count}/{n}', flush=True)

    missing = [i for i in range(1, n + 1) if painted[i] == 0]
    print(f'ecoregions with no pixels: {len(missing)}', flush=True)
    cover = float((grid > 0).sum()) / (W * H)
    print(f'land coverage: {cover*100:.2f}% of raster', flush=True)

    # --- metadata ---
    biome_of = np.zeros(n + 1, dtype=np.uint8)
    meta = [None] * (n + 1)
    biomes, realms = {}, {}
    for i, rec in enumerate(records):
        idx = i + 1
        bn = int(rec['BIOME_NUM'])
        code = (rec['ECO_BIOME_'] or '').strip()
        realm = (rec['REALM'] or '').strip()
        if bn > 90 or realm in ('N/A', ''):
            bn = 0
        biome_of[idx] = bn
        biomes[bn] = rec['BIOME_NAME']
        if realm and realm != 'N/A':
            realms[code[:2]] = realm
        meta[idx] = {
            'name': rec['ECO_NAME'],
            'biome': bn,
            'realm': realm,
            'code': code,
            'nnh': int(rec['NNH']),
            'nnhName': rec['NNH_NAME'],
            'color': rec['COLOR'],
            'ecoId': int(rec['ECO_ID']),
        }

    # --- encode PNG ---
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[:, :, 0] = (grid & 0xFF).astype(np.uint8)
    rgb[:, :, 1] = (grid >> 8).astype(np.uint8)
    rgb[:, :, 2] = biome_of[grid]
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(rgb, 'RGB').save(os.path.join(OUT, 'ecoregions.png'), optimize=True)
    np.save(os.path.join(SRC, 'eco_grid.npy'), grid)

    with open(os.path.join(OUT, 'ecoregions.json'), 'w') as f:
        json.dump({
            'width': W, 'height': H,
            'biomes': {str(k): v for k, v in sorted(biomes.items())},
            'realms': realms,
            'ecoregions': meta[1:],
        }, f, separators=(',', ':'))

    print('wrote', os.path.join(OUT, 'ecoregions.png'), flush=True)

main()
