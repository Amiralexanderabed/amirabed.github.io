"""Turn the Muller et al. (2025) plate model into geometry the browser can drift.

The web page never downloads a per-timestep snapshot.  Instead it gets the
present-day outlines once, tagged with the plate each one rides on, plus a small
table of rotations sampled through time.  Every frame the page slerps each
plate's rotation to the current age and spins its vertices into place, so the
continents move continuously instead of cross-fading between stills.

Writes ../data/plates.bin (geometry + rotations) and ../data/plates.json (the
section table describing it).
"""
import json, math, os, struct, sys
import numpy as np
import gpml, rotmodel

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))

# Simplification: 0.12 deg is about 13 km, under a pixel on a full-screen globe
# and still crisp at the deepest zoom the page allows.
TOL_DEG = 0.12
MIN_AREA_LAND = 0.010     # square degrees; drops islets too small to see
MIN_AREA_SHELF = 0.05
ROT_TOL_DEG = 0.15        # max error allowed when the page slerps between samples
AGE_MAX = 1800.0

DEG = math.pi / 180


# --------------------------------------------------------------------- helpers
def to_xyz(pts):
    a = np.asarray(pts, dtype=np.float64)
    lon, lat = np.radians(a[:, 0]), np.radians(a[:, 1])
    c = np.cos(lat)
    return np.stack([c * np.cos(lon), c * np.sin(lon), np.sin(lat)], axis=1)


def simplify(v, tol):
    """Douglas-Peucker on the sphere, measuring perpendicular chord distance."""
    n = len(v)
    if n < 4:
        return list(range(n))
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j - i < 2:
            continue
        a, b = v[i], v[j]
        ab = b - a
        L2 = ab @ ab
        seg = v[i + 1:j]
        if L2 < 1e-18:
            d = np.linalg.norm(seg - a, axis=1)
        else:
            t = np.clip((seg - a) @ ab / L2, 0, 1)
            d = np.linalg.norm(seg - (a + t[:, None] * ab), axis=1)
        k = int(np.argmax(d))
        if d[k] > tol:
            k += i + 1
            keep[k] = True
            stack.append((i, k))
            stack.append((k, j))
    return list(np.nonzero(keep)[0])


def is_simple(p):
    """True when no two non-adjacent edges of the ring cross."""
    n = len(p)
    a = p
    b = np.roll(p, -1, axis=0)
    d = b - a
    for i in range(n):
        j0, j1 = i + 2, n - (1 if i == 0 else 0)
        if j1 <= j0:
            continue
        c, e = a[j0:j1], b[j0:j1]
        di = d[i]
        s1 = di[0] * (c[:, 1] - a[i][1]) - di[1] * (c[:, 0] - a[i][0])
        s2 = di[0] * (e[:, 1] - a[i][1]) - di[1] * (e[:, 0] - a[i][0])
        dj = d[j0:j1]
        s3 = dj[:, 0] * (a[i][1] - c[:, 1]) - dj[:, 1] * (a[i][0] - c[:, 0])
        s4 = dj[:, 0] * (b[i][1] - c[:, 1]) - dj[:, 1] * (b[i][0] - c[:, 0])
        if np.any((s1 * s2 < 0) & (s3 * s4 < 0)):
            return False
    return True


def simplify_simple(v, centre, tol):
    """Simplify, but never past the point where the ring crosses itself."""
    for factor in (1.0, 0.5, 0.25, 0.1, 0.0):
        k = simplify(v, tol * factor) if factor else list(range(len(v)))
        if len(k) < 3:
            continue
        p2 = gnomonic(v[k], centre)
        if is_simple(p2):
            return k, p2
    return None, None


def basis(centre):
    """Orthonormal frame with `centre` as the local up."""
    up = np.array([0.0, 0.0, 1.0])
    if abs(centre[2]) > 0.9:
        up = np.array([1.0, 0.0, 0.0])
    e = np.cross(up, centre)
    e /= np.linalg.norm(e)
    n = np.cross(centre, e)
    return e, n


def gnomonic(v, centre):
    """Project onto the tangent plane at `centre`; great circles become lines,
    so ear clipping in this plane is exact for spherical polygons."""
    e, n = basis(centre)
    d = v @ centre
    d = np.where(d < 1e-6, 1e-6, d)
    return np.stack([(v @ e) / d, (v @ n) / d], axis=1)


def signed_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def earcut(p):
    """Ear clipping for a simple polygon, CCW or CW.  Returns index triples
    into `p`.  Rings here span at most ~25 degrees so the planar projection is
    faithful and the naive algorithm is both correct and fast enough."""
    n = len(p)
    if n < 3:
        return []
    if signed_area(p) < 0:
        p = p[::-1]
        flip = True
    else:
        flip = False
    idx = list(range(n))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 4 * n:
        clipped = False
        m = len(idx)
        for k in range(m):
            i0, i1, i2 = idx[(k - 1) % m], idx[k], idx[(k + 1) % m]
            a, b, c = p[i0], p[i1], p[i2]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if cross <= 0:                       # reflex or degenerate: not an ear
                continue
            rest = [j for j in idx if j not in (i0, i1, i2)]
            if rest:
                q = p[rest]
                d0 = (b[0] - a[0]) * (q[:, 1] - a[1]) - (b[1] - a[1]) * (q[:, 0] - a[0])
                d1 = (c[0] - b[0]) * (q[:, 1] - b[1]) - (c[1] - b[1]) * (q[:, 0] - b[0])
                d2 = (a[0] - c[0]) * (q[:, 1] - c[1]) - (a[1] - c[1]) * (q[:, 0] - c[0])
                if np.any((d0 >= 0) & (d1 >= 0) & (d2 >= 0)):
                    continue                     # something is inside the ear
            tris.append((i0, i1, i2))
            idx.pop(k)
            clipped = True
            break
        if not clipped:
            # No ear found - the ring has a degenerate or self-touching stretch.
            # Clip the most convex corner anyway; the sliver it leaves is far
            # smaller than a pixel and the polygon stays fully covered.
            best, bk = None, 0
            for k in range(m):
                a, b, c = p[idx[(k - 1) % m]], p[idx[k]], p[idx[(k + 1) % m]]
                cr = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
                if best is None or cr > best:
                    best, bk = cr, k
            tris.append((idx[(bk - 1) % m], idx[bk], idx[(bk + 1) % m]))
            idx.pop(bk)
            guard += 1
        else:
            guard = 0
    if len(idx) == 3:
        tris.append(tuple(idx))
    if flip:
        tris = [(n - 1 - a, n - 1 - b, n - 1 - c) for a, b, c in tris]
    return tris


# ---------------------------------------------------------------- build a layer
def build_layer(feats, min_area, tol):
    """-> (positions Nx3 float, feature id per vertex, triangles, feature table)"""
    P, F, T, table, cover = [], [], [], [], []
    nvert = 0
    dropped = kept_area = lost_area = 0
    for f in feats:
        ring = f['rings'][0]                     # interior rings are lakes; filled
        v = to_xyz(ring)
        if len(v) > 3 and np.allclose(v[0], v[-1]):
            v = v[:-1]
        if len(v) < 3:
            continue
        centre = v.mean(axis=0)
        nrm = np.linalg.norm(centre)
        if nrm < 1e-9:
            continue
        centre /= nrm
        area = abs(signed_area(gnomonic(v, centre))) * (180 / math.pi) ** 2
        if area < min_area:
            dropped += 1
            lost_area += area
            continue
        kept_area += area

        k, p2 = simplify_simple(v, centre, tol * DEG)
        if k is None:
            continue
        v = v[k]
        tris = earcut(p2)
        if not tris:
            continue

        tri_area = sum(abs((p2[b][0]-p2[a][0])*(p2[c][1]-p2[a][1])
                           - (p2[b][1]-p2[a][1])*(p2[c][0]-p2[a][0])) / 2
                       for a, b, c in tris) * (180 / math.pi) ** 2
        ring_area = abs(signed_area(p2)) * (180 / math.pi) ** 2
        if ring_area > 0:
            cover.append(tri_area / ring_area)

        fid = len(table)
        base = nvert
        P.append(v)
        F.append(np.full(len(v), fid, dtype=np.uint16))
        T.append(np.asarray(tris, dtype=np.uint32) + base)
        nvert += len(v)
        table.append((f['plate'], f['from_age'], f['to_age'], f['name']))
    cover.sort()
    print(f'    triangulated area / polygon area: min {cover[0]:.4f} '
          f'median {cover[len(cover)//2]:.4f} max {cover[-1]:.4f}')
    print(f'    kept {len(table)} polygons ({dropped} below {min_area} sq.deg, '
          f'{100*lost_area/(kept_area+lost_area):.2f}% of area)')
    return (np.concatenate(P), np.concatenate(F), np.concatenate(T), table)


# ------------------------------------------------------------------- rotations
def rotation_samples(model, plate, tmin, tmax):
    """Times + quaternions such that slerping between them stays within
    ROT_TOL_DEG of the full model.  Douglas-Peucker on the rotation curve."""
    tmin = max(0.0, math.floor(tmin))
    tmax = max(tmin + 1.0, math.ceil(tmax))
    dense = np.arange(tmin, tmax + 0.5, 1.0)
    q = np.array([model.absolute(plate, float(t)) for t in dense])
    n = len(dense)
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    tol = math.cos(ROT_TOL_DEG * DEG / 2)
    while stack:
        i, j = stack.pop()
        if j - i < 2:
            continue
        worst, wk = 1.0, -1
        qi, qj = q[i], q[j]
        for k in range(i + 1, j):
            u = (dense[k] - dense[i]) / (dense[j] - dense[i])
            approx = rotmodel.slerp(tuple(qi), tuple(qj), u)
            d = abs(float(np.dot(approx, q[k])))
            if d < worst:
                worst, wk = d, k
        if worst < tol:
            keep[wk] = True
            stack.append((i, wk))
            stack.append((wk, j))
    ks = np.nonzero(keep)[0]
    return dense[ks], q[ks]


def main():
    print('reading plate model...')
    coasts = gpml.read(f'{SRC}/Coastlines/shapes_coasts.gpmlz')
    conts = gpml.read(f'{SRC}/ContinentalPolygons/shapes_continents.gpmlz')
    model = rotmodel.load(SRC)
    print(f'  {len(coasts)} coastline polygons, {len(conts)} continental polygons')

    print('  triangulating land...')
    lp, lf, lt, ltab = build_layer(coasts, MIN_AREA_LAND, TOL_DEG)
    print('  triangulating continental crust...')
    sp, sf, st, stab = build_layer(conts, MIN_AREA_SHELF, TOL_DEG * 1.6)

    # one shared vertex array: land first, then shelf
    off = len(lp)
    sf = sf + len(ltab)
    st = st + off
    pos = np.concatenate([lp, sp])
    fid = np.concatenate([lf, sf])
    table = ltab + stab
    print(f'  vertices {len(pos)}  land tris {len(lt)}  shelf tris {len(st)}  '
          f'features {len(table)}')

    used = {t[0] for t in table}
    fp = os.path.join(SRC, 'fossil_plates.json')
    if os.path.exists(fp):
        extra = {int(x) for x in json.load(open(fp))}
        missing = {p for p in extra if p not in used and p in model.seq}
        print(f'  + {len(missing)} plates carrying fossil localities')
        used |= missing
    else:
        print('  (no fossil_plates.json yet - run fossils.py first)')
    plates = sorted(used)
    pindex = {p: i for i, p in enumerate(plates)}
    print(f'  {len(plates)} distinct plates; sampling rotations...')

    # only sample each plate across the ages its own polygons exist for
    span = {}
    for pl, fa, ta, _ in table:
        lo, hi = span.get(pl, (AGE_MAX, 0.0))
        span[pl] = (min(lo, max(0.0, ta)), max(hi, min(AGE_MAX, fa)))
    for p in plates:
        span.setdefault(p, (0.0, AGE_MAX))

    times, quats, offs = [], [], []
    for p in plates:
        lo, hi = span[p]
        ts, qs = rotation_samples(model, p, lo, hi)
        offs.append((len(times), len(ts)))
        times.extend(ts.tolist())
        quats.extend(qs.tolist())
        print(f'    plate {p}: {len(ts)} samples', end='\r')
    print(f'    {len(times)} rotation samples total ({len(times)/len(plates):.0f} per plate)')

    # ---- pack
    qpos = np.clip(np.round(pos * 32767), -32767, 32767).astype('<i2')
    qfid = fid.astype('<u2')
    allidx = np.concatenate([lt, st])
    if allidx.max() > 65535:
        raise SystemExit('too many vertices for 16-bit indices')
    idx = allidx.astype('<u2')
    feat_plate = np.array([pindex[t[0]] for t in table], dtype='<u2')
    feat_from = np.array([min(t[1], 4000) for t in table], dtype='<i2')
    feat_to = np.array([max(t[2], -1) for t in table], dtype='<i2')
    rot_off = np.array([o[0] for o in offs], dtype='<u4')
    rot_len = np.array([o[1] for o in offs], dtype='<u4')
    rot_t = (np.array(times) * 2).round().astype('<i2')          # half-Myr steps
    rot_q = np.clip(np.round(np.array(quats) * 32767), -32767, 32767).astype('<i2')

    sections, blob, cursor = {}, [], 0
    def add(name, arr, kind):
        nonlocal cursor
        b = arr.tobytes()
        pad = (-len(b)) % 4
        sections[name] = {'off': cursor, 'len': int(arr.size), 'type': kind}
        blob.append(b + b'\0' * pad)
        cursor += len(b) + pad

    add('pos', qpos.reshape(-1), 'i16')
    add('fid', qfid, 'u16')
    add('idx', idx, 'u16')
    add('featPlate', feat_plate, 'u16')
    add('featFrom', feat_from, 'i16')
    add('featTo', feat_to, 'i16')
    add('rotOff', rot_off, 'u32')
    add('rotLen', rot_len, 'u32')
    add('rotTime', rot_t, 'i16')
    add('rotQuat', rot_q.reshape(-1), 'i16')

    os.makedirs(OUT, exist_ok=True)
    with open(f'{OUT}/plates.bin', 'wb') as fh:
        for b in blob:
            fh.write(b)

    meta = {
        'model': 'Muller et al. (2025) global plate model, 0-1800 Ma',
        'ageMax': AGE_MAX,
        'vertexCount': int(len(pos)),
        'featureCount': len(table),
        'plateCount': len(plates),
        'land': {'first': 0, 'count': int(len(lt) * 3)},
        'shelf': {'first': int(len(lt) * 3), 'count': int(len(st) * 3)},
        'plateIds': plates,
        'sections': sections,
        'names': [t[3][:48] for t in table],
    }
    json.dump(meta, open(f'{OUT}/plates.json', 'w'), separators=(',', ':'))
    mb = os.path.getsize(f'{OUT}/plates.bin') / 1e6
    print(f'wrote plates.bin ({mb:.2f} MB) and plates.json')


if __name__ == '__main__':
    main()
