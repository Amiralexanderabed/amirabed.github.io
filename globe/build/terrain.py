"""Basemap and relief textures.

Blue Marble -> data/basemap.jpg          (6144x3072 equirectangular colour)
GEBCO       -> data/relief.png           (2160x1080, height split across R/G)

The GEBCO grey ramp clamps everything at or below sea level to 0 and saturates
somewhere near 6,300 m, so it is used for *relative* shading only - the app
never reports elevations from it.
"""
import os
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))

def basemap():
    im = Image.open(os.path.join(SRC, 'bluemarble.jpg')).convert('RGB')
    print('  source', im.size)
    im = im.resize((6144, 3072), Image.LANCZOS)
    im.save(os.path.join(OUT, 'basemap.jpg'), quality=82, optimize=True, progressive=True)

def relief():
    im = Image.open(os.path.join(SRC, 'gebco.png')).convert('L')
    W, H = im.size                      # 21600 x 10800
    OW, OH = 2160, 1080                 # exact 10x box downsample
    f, rows = 10, 108
    out = np.zeros((OH, OW), dtype=np.float32)
    for s in range(OH // rows):
        strip = np.asarray(im.crop((0, s * rows * f, W, (s + 1) * rows * f)), dtype=np.float32)
        out[s * rows:(s + 1) * rows] = strip.reshape(rows, f, OW, f).mean(axis=(1, 3))
    v = np.clip(out / 255.0, 0, 1) * 255.0
    hi = np.floor(v).astype(np.uint8)
    lo = np.clip(np.round((v - np.floor(v)) * 255.0), 0, 255).astype(np.uint8)
    Image.fromarray(np.stack([hi, lo, np.zeros_like(hi)], axis=2), 'RGB').save(
        os.path.join(OUT, 'relief.png'), optimize=True)

os.makedirs(OUT, exist_ok=True)
print('basemap...'); basemap()
print('relief...');  relief()
print('done')
