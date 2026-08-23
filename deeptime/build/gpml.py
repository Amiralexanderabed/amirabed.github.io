"""Read polygons out of a GPlates .gpmlz feature collection.

GPML is verbose XML; all we want per feature is the plate it rides on, the
window of time it exists for, and its rings.  Coordinates in gml:posList are
lat/lon pairs, which we flip to lon/lat on the way out.
"""
import gzip, xml.etree.ElementTree as ET

GML = '{http://www.opengis.net/gml}'
GPML = '{http://www.gplates.org/gplates}'
DISTANT_PAST, DISTANT_FUTURE = 1e9, -1e9


def _tag(e):
    return e.tag.split('}')[-1]


def _poslist(ring):
    """gml posList -> [(lon, lat), ...]"""
    txt = ring.findtext(f'.//{GML}posList') or ''
    v = txt.split()
    return [(float(v[i + 1]), float(v[i])) for i in range(0, len(v) - 1, 2)]


def _time(el):
    """gml:timePosition -> Ma, mapping the two open-ended sentinels."""
    if el is None:
        return None
    t = (el.text or '').strip()
    if 'distantPast' in t:
        return DISTANT_PAST
    if 'distantFuture' in t:
        return DISTANT_FUTURE
    try:
        return float(t)
    except ValueError:
        return None


def _shapefile_attrs(feat):
    out = {}
    for kv in feat.iter(f'{GPML}KeyValueDictionaryElement'):
        k = kv.findtext(f'{GPML}key')
        v = kv.findtext(f'{GPML}value')
        if k is not None:
            out[k] = v
    return out


def read(path):
    """[{plate, from_age, to_age, name, rings:[[(lon,lat)...], ...]}, ...]

    rings[0] is the exterior; any further rings are holes.
    """
    with gzip.open(path, 'rb') as fh:
        root = ET.fromstring(fh.read())

    feats = []
    for member in root.findall(f'{GML}featureMember'):
        for feat in member:
            attrs = _shapefile_attrs(feat)

            plate = feat.findtext(f'.//{GPML}reconstructionPlateId//{GPML}PlateId')
            if plate is None:
                plate = attrs.get('PLATEID1')
            plate = int(float(plate)) if plate not in (None, '') else 0

            begin = _time(feat.find(f'.//{GML}validTime//{GML}begin//{GML}timePosition'))
            end = _time(feat.find(f'.//{GML}validTime//{GML}end//{GML}timePosition'))
            if begin is None:
                begin = float(attrs.get('FROMAGE') or DISTANT_PAST)
            if end is None:
                end = float(attrs.get('TOAGE') or DISTANT_FUTURE)
            if begin < 0:                      # -999 is the shapefile "always" flag
                begin = DISTANT_PAST
            if end < 0:
                end = DISTANT_FUTURE

            name = (feat.findtext(f'.//{GML}name') or attrs.get('NAME') or '').strip()

            for poly in feat.iter(f'{GML}Polygon'):
                rings = []
                for side in ('exterior', 'interior'):
                    for s in poly.findall(f'{GML}{side}'):
                        pts = _poslist(s)
                        if len(pts) >= 4:
                            rings.append(pts)
                if rings:
                    feats.append({'plate': plate, 'from_age': begin, 'to_age': end,
                                  'name': name, 'rings': rings})
    return feats
