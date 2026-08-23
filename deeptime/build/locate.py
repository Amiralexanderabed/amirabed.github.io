"""Which tectonic plate is a present-day point sitting on?

Fossil localities have to ride the same plates as the coastlines, or they drift
off their own continent.  The static-polygon layer of the plate model covers the
whole globe, so a point-in-polygon test against it gives every locality a plate
id from exactly the model the globe is drawn with.
"""
import math
import numpy as np
import gpml


class PlateLocator:
    def __init__(self, path):
        self.polys = []
        for f in gpml.read(path):
            ring = f['rings'][0]
            a = np.asarray(ring, dtype=np.float64)
            lon, lat = np.radians(a[:, 0]), np.radians(a[:, 1])
            c = np.cos(lat)
            v = np.stack([c * np.cos(lon), c * np.sin(lon), np.sin(lat)], axis=1)
            centre = v.mean(axis=0)
            n = np.linalg.norm(centre)
            if n < 1e-9:
                continue
            centre /= n
            # bounding cap, so most polygons are rejected with one dot product
            cosr = float(np.min(v @ centre))
            self.polys.append((centre, cosr, v, f['plate'], f['from_age'], f['to_age']))
        # widest cap first: big plates win ties, small terranes are tested first
        self.polys.sort(key=lambda p: p[1], reverse=True)
        self.centres = np.array([p[0] for p in self.polys])
        self.cosr = np.array([p[1] for p in self.polys])

    @staticmethod
    def _inside(v, centre, p):
        """Winding test in the polygon's own gnomonic frame."""
        if v @ centre <= 0:
            return False
        up = np.array([0.0, 0.0, 1.0])
        if abs(centre[2]) > 0.9:
            up = np.array([1.0, 0.0, 0.0])
        e = np.cross(up, centre); e /= np.linalg.norm(e)
        n = np.cross(centre, e)
        d = p @ centre
        d = np.where(d < 1e-6, 1e-6, d)
        q = np.stack([(p @ e) / d, (p @ n) / d], axis=1)
        t = v @ centre
        pt = np.array([(v @ e) / t, (v @ n) / t])
        x, y = q[:, 0], q[:, 1]
        x2, y2 = np.roll(x, -1), np.roll(y, -1)
        cross = ((y > pt[1]) != (y2 > pt[1])) & \
                (pt[0] < (x2 - x) * (pt[1] - y) / np.where(y2 == y, 1e-12, y2 - y) + x)
        return bool(np.count_nonzero(cross) % 2)

    def plate_of(self, lon, lat):
        la, lo = math.radians(lat), math.radians(lon)
        c = math.cos(la)
        v = np.array([c * math.cos(lo), c * math.sin(lo), math.sin(la)])
        cand = np.nonzero(self.centres @ v >= self.cosr)[0]
        best = None
        for i in cand:
            centre, cosr, p, plate, fa, ta = self.polys[i]
            if self._inside(v, centre, p):
                # smallest containing polygon wins - terranes sit inside plates
                if best is None or cosr > best[0]:
                    best = (cosr, plate)
        return best[1] if best else None
