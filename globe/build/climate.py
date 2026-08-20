"""Derive Koppen-Geiger classes + climate values from WorldClim 2.1 (10 arc-min).

Classification follows Peel, Finlayson & McMahon (2007).
Outputs two 2048x1024 equirectangular RGB PNGs plus per-ecoregion aggregates.
"""
import json
import numpy as np
from PIL import Image

import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))
CW, CH = 2048, 1024

KOPPEN = ['--',
    'Af','Am','Aw','BWh','BWk','BSh','BSk',
    'Csa','Csb','Csc','Cwa','Cwb','Cwc','Cfa','Cfb','Cfc',
    'Dsa','Dsb','Dsc','Dsd','Dwa','Dwb','Dwc','Dwd','Dfa','Dfb','Dfc','Dfd',
    'ET','EF']
KID = {k: i for i, k in enumerate(KOPPEN)}

def load_stack(kind):
    arrs = []
    for m in range(1, 13):
        a = np.array(Image.open(os.path.join(SRC, 'wc', f'wc2.1_10m_{kind}_{m:02d}.tif')), dtype=np.float32)
        arrs.append(a)
    return np.stack(arrs, axis=0)   # (12, H, W)

def main():
    print('loading WorldClim...', flush=True)
    T = load_stack('tavg')
    P = load_stack('prec')
    _, H, W = T.shape
    print('native grid', W, 'x', H, flush=True)

    valid = (T > -1e30).all(axis=0) & (P > -1e30).all(axis=0)
    T = np.where(T > -1e30, T, np.nan)
    P = np.where(P > -1e30, P, 0.0)
    P = np.maximum(P, 0.0)

    MAT = np.nanmean(T, axis=0)
    MAP = np.nansum(P, axis=0)
    Tcold = np.nanmin(T, axis=0)
    Thot = np.nanmax(T, axis=0)
    Tmon10 = np.nansum(T > 10, axis=0)
    Pdry = np.nanmin(P, axis=0)

    lat = 90.0 - (np.arange(H) + 0.5) * (180.0 / H)
    north = (lat[:, None] >= 0) & np.ones((H, W), dtype=bool)

    # Summer = Apr-Sep in the north, Oct-Mar in the south.
    apr_sep = np.zeros(12, dtype=bool); apr_sep[3:9] = True
    sum_mask = np.where(north[None, :, :], apr_sep[:, None, None], ~apr_sep[:, None, None])
    win_mask = ~sum_mask

    big = 1e9
    Psum = np.where(sum_mask, P, 0).sum(axis=0)
    Pwin = np.where(win_mask, P, 0).sum(axis=0)
    Psdry = np.where(sum_mask, P, big).min(axis=0)
    Pwdry = np.where(win_mask, P, big).min(axis=0)
    Pswet = np.where(sum_mask, P, -big).max(axis=0)
    Pwwet = np.where(win_mask, P, -big).max(axis=0)

    Pth = np.where(Pwin >= 0.7 * MAP, 2 * MAT,
          np.where(Psum >= 0.7 * MAP, 2 * MAT + 28, 2 * MAT + 14))

    kop = np.zeros((H, W), dtype=np.uint8)

    is_B = MAP < 10 * Pth
    is_A = (~is_B) & (Tcold >= 18)
    is_C = (~is_B) & (~is_A) & (Thot > 10) & (Tcold > 0) & (Tcold < 18)
    is_D = (~is_B) & (~is_A) & (Thot > 10) & (Tcold <= 0)
    is_E = (~is_B) & (~is_A) & (~is_C) & (~is_D) & (Thot <= 10)

    # --- A ---
    Af = is_A & (Pdry >= 60)
    Am = is_A & ~Af & (Pdry >= 100 - MAP / 25)
    Aw = is_A & ~Af & ~Am
    kop[Af] = KID['Af']; kop[Am] = KID['Am']; kop[Aw] = KID['Aw']

    # --- B ---
    arid = MAP < 5 * Pth
    hot = MAT >= 18
    kop[is_B &  arid &  hot] = KID['BWh']
    kop[is_B &  arid & ~hot] = KID['BWk']
    kop[is_B & ~arid &  hot] = KID['BSh']
    kop[is_B & ~arid & ~hot] = KID['BSk']

    # --- C / D second + third letters ---
    s2 = (Psdry < 40) & (Psdry < Pwwet / 3)
    w2 = (~s2) & (Pwdry < Pswet / 10)
    f2 = ~s2 & ~w2

    a3 = Thot >= 22
    b3 = (~a3) & (Tmon10 >= 4)
    c3 = (~a3) & (~b3)
    d3 = c3 & (Tcold <= -38)
    c3 = c3 & ~d3

    for grp, flag in (('C', is_C), ('D', is_D)):
        for l2, m2 in (('s', s2), ('w', w2), ('f', f2)):
            for l3, m3 in (('a', a3), ('b', b3), ('c', c3), ('d', d3)):
                key = grp + l2 + l3
                if key not in KID:
                    continue
                kop[flag & m2 & m3] = KID[key]

    # --- E ---
    kop[is_E & (Thot > 0)] = KID['ET']
    kop[is_E & (Thot <= 0)] = KID['EF']

    kop[~valid] = 0

    # --- fill coastal nodata so shoreline clicks still resolve ---
    def dilate(arr, mask, iters=6, nearest=False):
        a = arr.copy(); m = mask.copy()
        for _ in range(iters):
            if m.all():
                break
            acc = np.zeros_like(a, dtype=np.float64)
            cnt = np.zeros(a.shape, dtype=np.int32)
            src = np.zeros_like(a)
            for dy, dx in ((0,1),(0,-1),(1,0),(-1,0)):
                sa = np.roll(np.where(m, a, 0), (dy, dx), (0, 1))
                sm = np.roll(m, (dy, dx), (0, 1))
                acc += np.where(sm, sa, 0); cnt += sm
                src = np.where((cnt == 1) & sm & ~m, sa, src)
            newm = (~m) & (cnt > 0)
            if nearest:
                a = np.where(newm, src, a)
            else:
                a = np.where(newm, acc / np.maximum(cnt, 1), a)
            m = m | newm
        return a, m

    vf = valid.copy()
    kopf, _ = dilate(kop.astype(np.float64), vf, 6, nearest=True)
    matf, _ = dilate(np.nan_to_num(MAT), vf, 6)
    mapf, _ = dilate(np.nan_to_num(MAP), vf, 6)
    tcf, _  = dilate(np.nan_to_num(Tcold), vf, 6)
    thf, _  = dilate(np.nan_to_num(Thot), vf, 6)
    pdf, filled = dilate(np.nan_to_num(Pdry), vf, 6)
    kop = np.rint(kopf).astype(np.uint8)

    # --- encode ---
    def enc_T(t):   # -60..67.5 C in 0.5 C steps
        return np.clip(np.rint((t + 60.0) * 2.0), 0, 255).astype(np.uint8)
    PMAX = np.log1p(12000.0)
    def enc_P(p):
        return np.clip(np.rint(np.log1p(np.maximum(p, 0)) / PMAX * 255.0), 0, 255).astype(np.uint8)

    def to_img(chans, resample_first_nearest):
        h, w = chans[0].shape
        out = []
        for i, c in enumerate(chans):
            im = Image.fromarray(c, 'L')
            rs = Image.NEAREST if (i == 0 and resample_first_nearest) else Image.BILINEAR
            out.append(np.array(im.resize((CW, CH), rs)))
        return np.stack(out, axis=2)

    a = to_img([kop, enc_T(matf), enc_P(mapf)], True)
    b = to_img([enc_T(tcf), enc_T(thf), enc_P(pdf)], False)
    a[:, :, 0] = np.array(Image.fromarray(kop, 'L').resize((CW, CH), Image.NEAREST))
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(a, 'RGB').save(f'{OUT}/climate_a.png', optimize=True)
    Image.fromarray(b, 'RGB').save(f'{OUT}/climate_b.png', optimize=True)

    # --- per-ecoregion aggregates ---
    grid = np.load(os.path.join(SRC, 'eco_grid.npy'))            # 4096x2048
    gh, gw = grid.shape
    sy = (np.arange(gh) * H // gh); sx = (np.arange(gw) * W // gw)
    kop_g = kop[np.ix_(sy, sx)]
    mat_g = matf[np.ix_(sy, sx)]
    map_g = mapf[np.ix_(sy, sx)]
    ok_g = filled[np.ix_(sy, sx)]

    coslat = np.cos(np.deg2rad(90.0 - (np.arange(gh) + 0.5) * (180.0 / gh)))[:, None]
    wgt = np.broadcast_to(coslat, grid.shape)

    meta = json.load(open(f'{OUT}/ecoregions.json'))
    n = len(meta['ecoregions'])
    flat = grid.ravel()
    m = (flat > 0) & ok_g.ravel()
    ids = flat[m]
    wm = wgt.ravel()[m]
    wsum = np.bincount(ids, weights=wm, minlength=n + 1)
    tsum = np.bincount(ids, weights=wm * mat_g.ravel()[m], minlength=n + 1)
    psum = np.bincount(ids, weights=wm * map_g.ravel()[m], minlength=n + 1)
    area = np.bincount(flat[flat > 0], weights=wgt.ravel()[flat > 0], minlength=n + 1)
    # dominant koppen per ecoregion
    kk = kop_g.ravel()[m].astype(np.int64)
    pair = ids.astype(np.int64) * 31 + kk
    cnt = np.bincount(pair, weights=wm, minlength=(n + 1) * 31).reshape(n + 1, 31)
    cnt[:, 0] = 0
    dom = cnt.argmax(axis=1)

    cell = (360.0 / gw) * (180.0 / gh) * (np.pi / 180.0) ** 2 * 6371.0 ** 2
    for i, e in enumerate(meta['ecoregions'], start=1):
        if wsum[i] > 0:
            e['tempC'] = round(float(tsum[i] / wsum[i]), 1)
            e['precipMm'] = int(round(float(psum[i] / wsum[i])))
            e['koppen'] = KOPPEN[int(dom[i])]
        e['areaKm2'] = int(round(float(area[i] * cell)))
    meta['koppen'] = KOPPEN
    json.dump(meta, open(f'{OUT}/ecoregions.json', 'w'), separators=(',', ':'))

    tot = np.bincount(kop[valid].ravel(), minlength=31)
    print('\nKoppen distribution (land pixels):')
    for i in np.argsort(-tot):
        if tot[i] and i: print(f'  {KOPPEN[i]:4s} {tot[i]:7d}')
    print('\nwrote climate_a.png, climate_b.png', flush=True)

main()
