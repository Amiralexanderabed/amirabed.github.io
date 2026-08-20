"""Rasterize MEOW + PPOW (Spalding et al. 2007/2012) to an equirectangular index raster.

PPOW pelagic provinces are painted first as the open-ocean background, then the
finer MEOW shelf ecoregions on top, so every sea pixel resolves to the most
specific unit available.

Output: globe/data/marine.png   (R = idx & 255, G = idx >> 8; 0 = land / no data)
        globe/data/marine.json  (index -> {name, province, realm, biome, ...})
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
SHP = os.path.join(SRC, 'meow', 'DataPack-14_001_WCMC036_MEOW_PPOW_2007_2012_v1',
                   '01_Data', 'WCMC-036-MEOW-PPOW-2007-2012')

# Marine biomes for the Biomes layer. Pelagic ones come straight from PPOW's own
# BIOME field; shelf ones are assigned per MEOW province by thermal regime, which
# is how MEOW's realms and provinces are themselves defined.
PELAGIC_BIOME = {
    'Gyre': 'Subtropical gyre',
    'Equatorial': 'Equatorial current',
    'Boundary - western': 'Western boundary current',
    'Boundary - eastern': 'Eastern boundary upwelling',
    'Semi-enclosed sea': 'Semi-enclosed sea',
    'Transitional': 'Transitional open ocean',
    'Polar': 'Polar open ocean',
}
SHELF_BIOME = {
    # tropical coral seas
    'Western Coral Triangle': 'Tropical coral sea', 'Eastern Coral Triangle': 'Tropical coral sea',
    'Sunda Shelf': 'Tropical coral sea', 'Sahul Shelf': 'Tropical coral sea',
    'South China Sea': 'Tropical coral sea', 'Java Transitional': 'Tropical coral sea',
    'Tropical Northwestern Pacific': 'Tropical coral sea',
    'Tropical Southwestern Pacific': 'Tropical coral sea',
    'Northeast Australian Shelf': 'Tropical coral sea',
    'Northwest Australian Shelf': 'Tropical coral sea',
    'South Kuroshio': 'Tropical coral sea', 'Lord Howe and Norfolk Islands': 'Tropical coral sea',
    'Central Polynesia': 'Tropical coral sea', 'Southeast Polynesia': 'Tropical coral sea',
    'Marquesas': 'Tropical coral sea', 'Easter Island': 'Tropical coral sea',
    'Hawaii': 'Tropical coral sea', 'Marshall, Gilbert and Ellis Islands': 'Tropical coral sea',
    'Red Sea and Gulf of Aden': 'Tropical coral sea', 'Andaman': 'Tropical coral sea',
    'Western Indian Ocean': 'Tropical coral sea', 'Central Indian Ocean Islands': 'Tropical coral sea',
    'Bay of Bengal': 'Tropical coral sea', 'West and South Indian Shelf': 'Tropical coral sea',
    'Somali/Arabian': 'Tropical coral sea',
    'Tropical Northwestern Atlantic': 'Tropical coral sea',
    'Tropical Southwestern Atlantic': 'Tropical coral sea',
    'North Brazil Shelf': 'Tropical coral sea', 'Gulf of Guinea': 'Tropical coral sea',
    'St. Helena and Ascension Islands': 'Tropical coral sea',
    'Tropical East Pacific': 'Tropical coral sea', 'Galapagos': 'Tropical coral sea',
    # warm temperate
    'Lusitanian': 'Warm-temperate shelf', 'Mediterranean Sea': 'Warm-temperate shelf',
    'Black Sea': 'Warm-temperate shelf', 'West African Transition': 'Warm-temperate shelf',
    'Warm Temperate Northwest Atlantic': 'Warm-temperate shelf',
    'Warm Temperate Northeast Pacific': 'Warm-temperate shelf',
    'Warm Temperate Northwest Pacific': 'Warm-temperate shelf',
    'Warm Temperate Southeastern Pacific': 'Warm-temperate shelf',
    'Warm Temperate Southwestern Atlantic': 'Warm-temperate shelf',
    'Agulhas': 'Warm-temperate shelf', 'Benguela': 'Warm-temperate shelf',
    'East Central Australian Shelf': 'Warm-temperate shelf',
    'West Central Australian Shelf': 'Warm-temperate shelf',
    'Northern New Zealand': 'Warm-temperate shelf',
    'Juan Fernández and Desventuradas': 'Warm-temperate shelf',
    'Amsterdam-St Paul': 'Warm-temperate shelf',
    # cold temperate
    'Northern European Seas': 'Cold-temperate shelf', 'Cold Temperate Northwest Atlantic': 'Cold-temperate shelf',
    'Cold Temperate Northeast Pacific': 'Cold-temperate shelf', 'Cold Temperate Northwest Pacific': 'Cold-temperate shelf',
    'Magellanic': 'Cold-temperate shelf', 'Tristan Gough': 'Cold-temperate shelf',
    'Southeast Australian Shelf': 'Cold-temperate shelf', 'Southwest Australian Shelf': 'Cold-temperate shelf',
    'Southern New Zealand': 'Cold-temperate shelf',
    # polar
    'Arctic': 'Polar shelf & sea ice', 'Continental High Antarctic': 'Polar shelf & sea ice',
    'Scotia Sea': 'Polar shelf & sea ice', 'Subantarctic Islands': 'Polar shelf & sea ice',
    'Subantarctic New Zealand': 'Polar shelf & sea ice',
}

# The published DBF carries a non-breaking space where an accent belongs.
NAME_FIX = {'Juan Fern\xa0ndez and Desventuradas': 'Juan Fern\u00e1ndez and Desventuradas'}
def fix(s):
    s = (s or '').strip()
    return NAME_FIX.get(s, s)

def unwrap_lons(lons):
    out = lons.copy()
    acc = 0.0
    shift = np.zeros(len(out))
    for i, dd in enumerate(np.diff(out)):
        if dd > 180.0:   acc -= 360.0
        elif dd < -180.0: acc += 360.0
        shift[i + 1] = acc
    return out + shift

def main():
    r = shapefile.Reader(SHP, encoding='utf-8')
    fn = [f[0] for f in r.fields[1:]]
    records = [dict(zip(fn, x)) for x in r.records()]
    n = len(records)
    print(f'{n} marine units', flush=True)

    grid = np.zeros((H, W), dtype=np.uint16)
    # PPOW first (open-ocean background), MEOW second (shelf detail on top);
    # within each, largest first so small units survive.
    def area_of(i):
        b = r.shape(i).bbox
        return (b[2] - b[0]) * (b[3] - b[1])
    ppow = sorted([i for i in range(n) if records[i]['TYPE'] == 'PPOW'], key=lambda i: -area_of(i))
    meow = sorted([i for i in range(n) if records[i]['TYPE'] == 'MEOW'], key=lambda i: -area_of(i))

    painted = np.zeros(n + 1, dtype=np.int64)
    for count, si in enumerate(ppow + meow):
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
            rings.append(((lons + 180.0) / 360.0 * W, (90.0 - ring[:, 1]) / 180.0 * H))
        if not rings:
            continue
        x0 = min(rx.min() for rx, _ in rings); x1 = max(rx.max() for rx, _ in rings)
        y0 = min(ry.min() for _, ry in rings); y1 = max(ry.max() for _, ry in rings)
        ix0, ix1 = int(np.floor(x0)) - 1, int(np.ceil(x1)) + 1
        iy0, iy1 = max(0, int(np.floor(y0)) - 1), min(H, int(np.ceil(y1)) + 1)
        bw, bh = ix1 - ix0, iy1 - iy0
        if bw <= 0 or bh <= 0 or bw > 4 * W:
            continue
        acc = np.zeros((bh, bw), dtype=bool)
        for rx, ry in rings:
            img = Image.new('1', (bw, bh), 0)
            ImageDraw.Draw(img).polygon(
                list(zip((rx - ix0).tolist(), (ry - iy0).tolist())), fill=1, outline=1)
            acc ^= np.array(img, dtype=bool)
        ys, xs = np.nonzero(acc)
        if len(ys) == 0:
            cx = int(round((x0 + x1) * 0.5)) % W
            cy = min(H - 1, max(0, int(round((y0 + y1) * 0.5))))
            grid[cy, cx] = idx; painted[idx] = 1
            continue
        gy = ys + iy0; gx = (xs + ix0) % W
        keep = (gy >= 0) & (gy < H)
        grid[gy[keep], gx[keep]] = idx
        painted[idx] = int(keep.sum())
        if count % 40 == 0:
            print(f'  {count}/{n}', flush=True)

    # Clear anything that fell on land: the terrestrial raster owns those pixels.
    land = np.load(os.path.join(SRC, 'eco_grid.npy'))
    grid[land > 0] = 0

    print('units with no pixels:', int((painted[1:] == 0).sum()), flush=True)
    print(f'sea coverage: {(grid > 0).sum() / (W * H) * 100:.1f}% of raster', flush=True)

    meta = [None] * (n + 1)
    for i, rec in enumerate(records, start=1):
        typ = rec['TYPE']
        prov = fix(rec['PROVINC'])
        eco = fix(rec['ECOREGION'])
        biome = (PELAGIC_BIOME.get(rec['BIOME'].strip(), 'Open ocean') if typ == 'PPOW'
                 else SHELF_BIOME.get(prov, 'Continental shelf'))
        meta[i] = {
            'name': eco or prov,
            'province': prov,
            'realm': fix(rec['REALM']),
            'biome': biome,
            'type': typ,
            'pelagic': fix(rec['BIOME']) or None,
        }

    unmapped = sorted({m['province'] for m in meta[1:]
                       if m['type'] == 'MEOW' and m['province'] not in SHELF_BIOME})
    if unmapped:
        print('WARNING unmapped provinces:', unmapped, flush=True)

    # representative point per unit: its own pixel nearest the circular centroid
    flat = grid.ravel(); msk = flat > 0
    ids = flat[msk]; pos = np.nonzero(msk)[0]
    ys = (pos // W).astype(np.float64); xs = (pos % W).astype(np.float64)
    ang = xs / W * 2 * np.pi
    cnt = np.bincount(ids, minlength=n + 1).astype(np.float64)
    cy = np.bincount(ids, weights=ys, minlength=n + 1) / np.maximum(cnt, 1)
    cx = (np.arctan2(np.bincount(ids, weights=np.sin(ang), minlength=n + 1),
                     np.bincount(ids, weights=np.cos(ang), minlength=n + 1))
          % (2 * np.pi)) / (2 * np.pi) * W
    order = np.argsort(ids, kind='stable'); ids_s = ids[order]
    start = np.searchsorted(ids_s, np.arange(n + 2))
    cell = (360.0 / W) * (180.0 / H) * (np.pi / 180.0) ** 2 * 6371.0 ** 2
    for i in range(1, n + 1):
        a, b = start[i], start[i + 1]
        if a >= b or meta[i] is None:
            continue
        sel = order[a:b]
        py = pos[sel] // W; px_ = pos[sel] % W
        dx = np.abs(px_ - cx[i]); dx = np.minimum(dx, W - dx)
        j = np.argmin((py - cy[i]) ** 2 + dx ** 2)
        meta[i]['lat'] = round(float(90.0 - (int(py[j]) + 0.5) * (180.0 / H)), 3)
        meta[i]['lon'] = round(float((int(px_[j]) + 0.5) * (360.0 / W) - 180.0), 3)
        meta[i]['areaKm2'] = int(round(float(
            np.sum(np.cos(np.deg2rad(90.0 - (py + 0.5) * (180.0 / H)))) * cell)))

    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[:, :, 0] = (grid & 0xFF).astype(np.uint8)
    rgb[:, :, 1] = (grid >> 8).astype(np.uint8)
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(rgb, 'RGB').save(os.path.join(OUT, 'marine.png'), optimize=True)
    np.save(os.path.join(SRC, 'marine_grid.npy'), grid)
    json.dump({'width': W, 'height': H, 'units': meta[1:]},
              open(os.path.join(OUT, 'marine.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    print('wrote marine.png + marine.json', flush=True)

main()
