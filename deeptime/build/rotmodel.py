"""Finite-rotation model: read a PLATES4 .rot file and answer "where was plate P at time t".

A .rot line is

    moving_plate  time  lat  lon  angle  fixed_plate  ! comment

and gives the finite rotation that carries `moving_plate` from its present-day
position to where it sat at `time`, measured *relative to* `fixed_plate`.  To
place a plate on the globe we have to walk the chain of fixed plates up to the
spin axis (plate 000), composing as we go:

    R_abs(P, t) = R_abs(fixed(P, t), t) . R_rel(P -> fixed, t)

Rotations are held as quaternions so that interpolating between the samples in
the file is a slerp, which is what GPlates itself does.
"""
import math, os, re
from collections import defaultdict

DEG = math.pi / 180.0


# ----------------------------------------------------------------- quaternions
def quat_from_pole(lat_deg, lon_deg, angle_deg):
    """Quaternion for a rotation of `angle` about the pole at (lat, lon)."""
    la, lo = lat_deg * DEG, lon_deg * DEG
    c = math.cos(la)
    axis = (c * math.cos(lo), c * math.sin(lo), math.sin(la))
    h = angle_deg * DEG * 0.5
    s = math.sin(h)
    return (math.cos(h), axis[0] * s, axis[1] * s, axis[2] * s)


IDENTITY = (1.0, 0.0, 0.0, 0.0)


def qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)


def qnorm(q):
    n = math.sqrt(sum(c * c for c in q))
    return IDENTITY if n == 0 else tuple(c / n for c in q)


def slerp(a, b, u):
    """Shortest-arc interpolation from a to b."""
    d = sum(x * y for x, y in zip(a, b))
    if d < 0:                      # q and -q are the same rotation; take the short way
        b, d = tuple(-x for x in b), -d
    if d > 0.9999995:              # numerically parallel - lerp and renormalise
        return qnorm(tuple(x + (y - x) * u for x, y in zip(a, b)))
    th = math.acos(max(-1.0, min(1.0, d)))
    s = math.sin(th)
    ca, cb = math.sin((1 - u) * th) / s, math.sin(u * th) / s
    return tuple(x * ca + y * cb for x, y in zip(a, b))


def qmat(q):
    """3x3 rotation matrix, row-major, for a unit quaternion."""
    w, x, y, z = q
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - w * z),     2 * (x * z + w * y)),
            (2 * (x * y + w * z),     1 - 2 * (x * x + z * z), 2 * (y * z - w * x)),
            (2 * (x * z - w * y),     2 * (y * z + w * x),     1 - 2 * (x * x + y * y)))


def qapply(q, v):
    m = qmat(q)
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


# ------------------------------------------------------------------ the model
LINE = re.compile(r'^\s*(\d+)\s+(-?[\d.]+)\s+(-?[\d.eE+]+)\s+(-?[\d.eE+]+)\s+'
                  r'(-?[\d.eE+]+)\s+(\d+)')


class RotationModel:
    def __init__(self, paths):
        # moving plate -> [(time, fixed plate, quaternion), ...]
        samples = defaultdict(list)
        for p in paths:
            with open(p, 'r', errors='replace') as fh:
                for raw in fh:
                    m = LINE.match(raw.split('!')[0])
                    if not m:
                        continue
                    mp, t, lat, lon, ang, fp = m.groups()
                    mp, fp, t = int(mp), int(fp), float(t)
                    if mp == fp:
                        continue                    # self-reference, ignore
                    samples[mp].append((t, fp, quat_from_pole(float(lat), float(lon), float(ang))))

        # Split each plate's samples into runs that share a fixed plate.  A change
        # of fixed plate is a "crossover": the two runs describe the same motion
        # through different anchors, so they must not be interpolated across.
        self.seq = {}
        for mp, rows in samples.items():
            rows.sort(key=lambda r: r[0])
            runs, cur = [], None
            for t, fp, q in rows:
                if cur is None or cur['fixed'] != fp:
                    cur = {'fixed': fp, 'times': [], 'quats': []}
                    runs.append(cur)
                cur['times'].append(t)
                cur['quats'].append(q)
            self.seq[mp] = runs
        self._cache = {}

    def plates(self):
        return sorted(self.seq)

    def covers(self, plate, t):
        """True when t falls inside a sequence the file actually defines."""
        for run in self.seq.get(plate, ()):
            if run['times'][0] - 1e-9 <= t <= run['times'][-1] + 1e-9:
                return True
        return False

    def _relative(self, plate, t):
        """(fixed plate, rotation of `plate` relative to it) at time t."""
        runs = self.seq.get(plate)
        if not runs:
            return None, IDENTITY
        run = None
        for r in runs:
            if r['times'][0] - 1e-9 <= t <= r['times'][-1] + 1e-9:
                run = r
                break
        if run is None:
            # Outside every sequence: hold the nearest end fixed, which is what
            # GPlates does for a plate whose history stops before t.
            run = min(runs, key=lambda r: min(abs(t - r['times'][0]), abs(t - r['times'][-1])))
            t = min(max(t, run['times'][0]), run['times'][-1])
        ts = run['times']
        lo, hi = 0, len(ts) - 1
        while lo < hi - 1:                          # binary search the bracket
            mid = (lo + hi) // 2
            if ts[mid] <= t:
                lo = mid
            else:
                hi = mid
        if hi == lo:
            return run['fixed'], run['quats'][lo]
        span = ts[hi] - ts[lo]
        u = 0.0 if span <= 0 else (t - ts[lo]) / span
        return run['fixed'], slerp(run['quats'][lo], run['quats'][hi], u)

    def absolute(self, plate, t):
        """Rotation carrying present-day coordinates of `plate` to time t."""
        key = (plate, round(t, 6))
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        q, seen = IDENTITY, set()
        p = plate
        while p and p not in seen:
            seen.add(p)
            fixed, rel = self._relative(p, t)
            q = qmul(rel, q)
            if fixed is None or fixed == 0:
                break
            p = fixed
        self._cache[key] = q
        return q

    def reconstruct(self, plate, t, lon, lat):
        """Present-day (lon, lat) -> (lon, lat) at time t."""
        la, lo = lat * DEG, lon * DEG
        c = math.cos(la)
        v = qapply(self.absolute(plate, t), (c * math.cos(lo), c * math.sin(lo), math.sin(la)))
        return (math.atan2(v[1], v[0]) / DEG, math.asin(max(-1.0, min(1.0, v[2]))) / DEG)


def load(src_dir):
    rot = os.path.join(src_dir, 'Rotations')
    files = sorted(os.path.join(rot, f) for f in os.listdir(rot) if f.endswith('.rot'))
    if not files:
        raise SystemExit('no .rot files in ' + rot)
    return RotationModel(files)
