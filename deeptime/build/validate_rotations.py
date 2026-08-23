"""Check our reconstruction against the official GPlates Web Service.

rotmodel.py re-implements finite-rotation composition, so it is worth proving it
agrees with GPlates itself.  The web service does not serve muller2025, so this
runs our own pipeline over muller2022 - which it does serve - and compares every
sampled coastline vertex.  Same file formats, same code path, so agreement here
is agreement for the model the page actually uses.

    python3 validate_rotations.py

Downloads ~2 MB the first time and caches the reference responses in src/gws/.
"""
import json, math, os, random, sys, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
REF = os.path.join(SRC, 'gws')
M22 = os.path.join(SRC, 'm22')
sys.path.insert(0, HERE)
import gpml, rotmodel

AGES = (100, 250, 450, 800)
# The service rounds its output to 4 decimals, so ~0.0001 deg is the floor.
# A handful of vertices sit further out: rotation files contain "crossovers",
# times where a plate changes which plate it is measured against, and the two
# sequences meeting there can disagree slightly.  Plate 28900, the Falkland
# block, crosses over at exactly 250 Ma and lands 0.006 deg (~600 m) apart.
# That is a property of the published file, not of this code, so the gate is on
# the bulk of the vertices with a loose ceiling on the worst.
P99_TOL = 0.0002
MAX_TOL = 0.01


def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 2:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print('  fetching', os.path.basename(path))
    with urllib.request.urlopen(url, timeout=600) as r, open(path, 'wb') as fh:
        fh.write(r.read())
    return path


def ensure_model():
    for layer in ('Rotations', 'Coastlines'):
        z = os.path.join(M22, layer + '.zip')
        fetch(f'https://repo.gplates.org/webdav/pmm/muller2022/{layer}.zip', z)
        if not os.path.isdir(os.path.join(M22, layer)):
            with zipfile.ZipFile(z) as f:
                f.extractall(M22)


def find(root, ext):
    for dirpath, _, names in os.walk(root):
        for n in names:
            if n.endswith(ext):
                return os.path.join(dirpath, n)
    raise SystemExit('missing ' + ext + ' under ' + root)


def reference(age):
    p = os.path.join(REF, f'muller2022_{age}.json')
    fetch(f'https://gws.gplates.org/reconstruct/coastlines/?time={age}&model=MULLER2022', p)
    pts = []
    for f in json.load(open(p))['features']:
        g = f['geometry']
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for poly in polys:
            for ring in poly:
                pts.extend(ring)
    return pts


def main():
    ensure_model()
    feats = gpml.read(find(os.path.join(M22, 'Coastlines'), '.gpmlz'))
    model = rotmodel.RotationModel([find(os.path.join(M22, 'Rotations'), '.rot')])
    print(f'{len(feats)} polygons, {len(model.plates())} plates in muller2022')

    worst_all, failed = 0.0, False
    for age in AGES:
        ref = reference(age)
        grid = {}
        for lon, lat in ref:
            grid.setdefault((int(math.floor(lon)), int(math.floor(lat))), []).append((lon, lat))

        gaps = []
        random.seed(1)
        for f in feats:
            if not (f['to_age'] <= age <= f['from_age']):
                continue
            ring = f['rings'][0]
            for lon, lat in random.sample(ring, min(5, len(ring))):
                rl, ra = model.reconstruct(f['plate'], age, lon, lat)
                best = 1e9
                cx, cy = int(math.floor(rl)), int(math.floor(ra))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for glon, glat in grid.get((cx + dx, cy + dy), ()):
                            dlon = (glon - rl + 180) % 360 - 180
                            best = min(best, math.hypot(
                                dlon * math.cos(math.radians(ra)), glat - ra))
                gaps.append(best)

        gaps.sort()
        n = len(gaps)
        worst, p99 = gaps[-1], gaps[int(n * 0.99)]
        worst_all = max(worst_all, worst)
        ok = p99 <= P99_TOL and worst <= MAX_TOL
        failed |= not ok
        print(f'  {age:4d} Ma  {n:6d} vertices  median {gaps[n // 2]:.6f}  '
              f'p99 {p99:.6f}  max {worst:.6f} deg  '
              f'{"ok" if ok else "MISMATCH"}')

    print(f'\nworst disagreement with GPlates: {worst_all:.6f} deg '
          f'({worst_all * 111:.2f} km)')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
