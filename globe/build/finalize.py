"""Add per-ecoregion representative points and the Koppen legend to ecoregions.json.

The representative point is the ecoregion's own pixel nearest its centroid
(circular mean in longitude, so regions crossing the antimeridian behave), which
guarantees the point the app flies to actually lies inside the region.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))

KOPPEN_COLORS = ['#00000000',
 '#0000FE','#0077FF','#46A9FA','#FE0000','#FE9695','#F5A301','#FFDB63','#FFFF00','#C6C700','#969600',
 '#96FF96','#63C764','#329633','#C6FF4E','#66FF33','#33C701','#FF00FE','#C600C7','#963194','#966495',
 '#ABB1FF','#5A77DB','#4C51B5','#320087','#00FFFF','#37C8FF','#007E7D','#00455E','#B2B2B2','#686868']
KOPPEN_NAMES = ['No data',
 'Tropical rainforest','Tropical monsoon','Tropical savanna','Hot desert','Cold desert','Hot semi-arid',
 'Cold semi-arid','Hot-summer Mediterranean','Warm-summer Mediterranean','Cold-summer Mediterranean',
 'Monsoon humid subtropical','Subtropical highland','Cold subtropical highland','Humid subtropical',
 'Oceanic','Subpolar oceanic','Hot-summer Mediterranean continental','Warm-summer Mediterranean continental',
 'Mediterranean subarctic','Mediterranean extremely cold','Monsoon hot-summer continental',
 'Monsoon warm-summer continental','Monsoon subarctic','Monsoon extremely cold subarctic',
 'Hot-summer humid continental','Warm-summer humid continental','Subarctic','Extremely cold subarctic',
 'Tundra','Ice cap']

g = np.load(os.path.join(SRC, 'eco_grid.npy'))
H, W = g.shape
meta = json.load(open(f'{OUT}/ecoregions.json'))
n = len(meta['ecoregions'])

flat = g.ravel(); m = flat > 0
ids = flat[m]; pos = np.nonzero(m)[0]
ys = (pos // W).astype(np.float64); xs = (pos % W).astype(np.float64)
ang = xs / W * 2 * np.pi
cnt = np.bincount(ids, minlength=n + 1).astype(np.float64)
cy = np.bincount(ids, weights=ys, minlength=n + 1) / np.maximum(cnt, 1)
cx = (np.arctan2(np.bincount(ids, weights=np.sin(ang), minlength=n + 1),
                 np.bincount(ids, weights=np.cos(ang), minlength=n + 1)) % (2 * np.pi)) / (2 * np.pi) * W

order = np.argsort(ids, kind='stable'); ids_s = ids[order]
start = np.searchsorted(ids_s, np.arange(n + 2))
for i, e in enumerate(meta['ecoregions'], start=1):
    a, b = start[i], start[i + 1]
    if a >= b:
        continue
    sel = order[a:b]
    py = pos[sel] // W; px = pos[sel] % W
    dx = np.abs(px - cx[i]); dx = np.minimum(dx, W - dx)
    j = np.argmin((py - cy[i]) ** 2 + dx ** 2)
    e['lat'] = round(float(90.0 - (int(py[j]) + 0.5) * (180.0 / H)), 3)
    e['lon'] = round(float((int(px[j]) + 0.5) * (360.0 / W) - 180.0), 3)

meta['koppenColors'] = KOPPEN_COLORS
meta['koppenNames'] = KOPPEN_NAMES
json.dump(meta, open(f'{OUT}/ecoregions.json', 'w'), separators=(',', ':'))
print('representative points + Koppen legend written')
