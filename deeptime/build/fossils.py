"""Per-chapter fossil localities and species lists from the Paleobiology Database.

For each chapter we pull every collection whose age falls inside it, thin them
down to a set that covers the map without burying the browser, and attach the
taxa found at each one.  Localities are given a plate id from the same model the
globe is drawn with, so a site stays glued to its own continent as the page
scrubs through time instead of floating off it.

Also writes ../data/places.json: every country and state the localities fall
in, with a representative point and the plate it rides on, so the search box can
fly the globe to a modern place at whatever age is on screen.

Writes ../data/ch/<chapter>.json, one file per chapter, loaded on demand.
Raw API responses are cached in src/pbdb/, so re-runs are cheap.
"""
import hashlib, json, math, os, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
CACHE = os.path.join(SRC, 'pbdb')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data', 'ch'))

sys.path.insert(0, HERE)
import locate, rotmodel
from chapters import CHAPTERS

API = 'https://paleobiodb.org/data1.2/'
UA = 'DeepTime/1.0 (https://amirabed.com; educational project)'

MAX_SITES = 1000        # per chapter, after thinning
MAX_TAXA_PER_SITE = 24
ROSTER = 600            # genera listed per chapter
BIN_DEG = 2.0           # paleo-degrees; one site per bin before any doubling up

# Coarse groups, in priority order: the first one a taxon matches wins.  Used to
# colour markers and to break the species roster into readable sections.
GROUPS = [
    ('Vertebrates', ('Chordata',)),
    ('Arthropods', ('Arthropoda', 'Trilobita')),
    ('Molluscs', ('Mollusca',)),
    ('Brachiopods', ('Brachiopoda',)),
    ('Corals & relatives', ('Cnidaria',)),
    ('Echinoderms', ('Echinodermata',)),
    ('Bryozoans', ('Bryozoa',)),
    ('Sponges', ('Porifera', 'Archaeocyatha')),
    ('Graptolites', ('Hemichordata',)),
    ('Worms', ('Annelida', 'Priapulida', 'Nemertina')),
    ('Plants', ('Tracheophyta', 'Plantae', 'Anthophyta', 'Pteridophyta',
                'Bryophyta', 'Coniferophyta', 'Cycadophyta', 'Ginkgophyta',
                'Lycophyta', 'Pinophyta', 'Spermatophyta')),
    ('Algae & microbes', ('Chlorophyta', 'Rhodophyta', 'Chrysophyta',
                          'Bacillariophyta', 'Cyanobacteria', 'Foraminifera',
                          'Radiolaria', 'Protista', 'Bacteria')),
    ('Fungi', ('Fungi',)),
]
OTHER = len(GROUPS)


def get(path, params, tag):
    """Cached GET against the PBDB API."""
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, tag + '.json')
    if os.path.exists(fn) and os.path.getsize(fn) > 2:
        with open(fn) as fh:
            return json.load(fh)
    url = API + path + '?' + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            break
        except Exception as e:
            if attempt == 3:
                print(f'    ! {tag}: {e}')
                return {'records': []}
            time.sleep(3 * (attempt + 1))
    with open(fn, 'w') as fh:
        json.dump(d, fh)
    time.sleep(0.4)
    return d


def country_names():
    recs = get('config.json', {'show': 'countries'}, 'countries').get('records', [])
    return {r['cod']: r['nam'] for r in recs if r.get('cod') and r.get('nam')}


def group_of(rec):
    phylum = rec.get('phl') or ''
    cls = rec.get('cll') or ''
    for i, (_, keys) in enumerate(GROUPS):
        if phylum in keys or cls in keys:
            return i
    return OTHER


def clean(s, n=70):
    s = (s or '').strip().replace('\n', ' ')
    return s[:n]


def thin(sites, model):
    """Keep a spread of localities: best in each paleo-bin first, then the
    richest of what is left, up to MAX_SITES."""
    if len(sites) <= MAX_SITES:
        return sites
    bins = {}
    for s in sites:
        key = (int(s['plon'] // BIN_DEG), int(s['plat'] // BIN_DEG))
        cur = bins.get(key)
        if cur is None or s['n'] > cur['n']:
            bins[key] = s
    first = list(bins.values())
    first.sort(key=lambda s: -s['n'])
    if len(first) >= MAX_SITES:
        return first[:MAX_SITES]
    chosen = set(id(s) for s in first)
    rest = sorted((s for s in sites if id(s) not in chosen), key=lambda s: -s['n'])
    return first + rest[:MAX_SITES - len(first)]


def build(ch, loc, model, countries, places):
    lo, hi = ch['end'], ch['start']
    mid = (lo + hi) / 2
    tag = ch['id']
    print(f"  {ch['name']} ({hi}-{lo} Ma)")

    colls = get('colls/list.json',
                {'max_ma': hi, 'min_ma': lo, 'show': 'loc,paleoloc,strat',
                 'limit': 'all'}, f'{tag}_colls_loc').get('records', [])
    if not colls:
        print('    no collections')
        return None, set()

    sites, unplaced = [], 0
    for c in colls:
        try:
            lon, lat = float(c['lng']), float(c['lat'])
        except (KeyError, TypeError, ValueError):
            continue
        plate = loc.plate_of(lon, lat)
        if plate is None or plate not in model.seq:
            g = c.get('gpl')
            plate = int(g) if g and int(g) in model.seq else None
        if plate is None:
            unplaced += 1
            continue
        plon, plat = model.reconstruct(plate, mid, lon, lat)
        country = countries.get(c.get('cc2') or '', '')
        state = (c.get('stp') or '').strip()
        if state in ('__', '?'):
            state = ''
        sites.append({
            'id': c['oid'].split(':')[1], 'lon': lon, 'lat': lat, 'plate': plate,
            'plon': plon, 'plat': plat, 'n': int(c.get('noc') or 0),
            'name': clean(c.get('nam')), 'fm': clean(c.get('sfm') or '', 40),
            'ea': float(c.get('eag') or hi), 'la': float(c.get('lag') or lo),
            'country': country, 'state': state,
        })

    kept = thin(sites, model)
    print(f'    {len(colls)} collections, {len(kept)} kept'
          + (f', {unplaced} without a plate' if unplaced else ''))

    # taxa at the kept localities, in batches the API is happy with
    by_coll = {}
    ids = [s['id'] for s in kept]
    for i in range(0, len(ids), 150):
        batch = ids[i:i + 150]
        key = hashlib.md5(','.join(batch).encode()).hexdigest()[:12]
        d = get('occs/list.json',
                {'coll_id': ','.join(batch), 'show': 'class', 'limit': 'all'},
                f'{tag}_occs_{key}')
        for r in d.get('records', []):
            cid = (r.get('cid') or '').split(':')[-1]
            nm = r.get('tna') or ''
            if not cid or not nm or nm.endswith('indet.'):
                continue
            by_coll.setdefault(cid, []).append((nm, group_of(r)))
        print(f'    taxa {min(i+150, len(ids))}/{len(ids)}', end='\r', flush=True)
    print(' ' * 40, end='\r')

    names, nindex = [], {}
    def name_id(n):
        i = nindex.get(n)
        if i is None:
            i = nindex[n] = len(names)
            names.append(n)
        return i

    locs, lindex = [], {}
    def loc_id(country, state):
        label = ', '.join(x for x in (state, country) if x)
        if not label:
            return -1
        i = lindex.get(label)
        if i is None:
            i = lindex[label] = len(locs)
            locs.append(label)
        return i

    S = {k: [] for k in ('lon', 'lat', 'plate', 'ea', 'la', 'n', 'g', 'nm', 'fm',
                         'tx', 'lc')}
    for s in kept:
        occ = by_coll.get(s['id'], [])
        seen, tx, gcount = set(), [], {}
        for nm, g in occ:
            gcount[g] = gcount.get(g, 0) + 1
            if nm in seen:
                continue
            seen.add(nm)
            if len(tx) < MAX_TAXA_PER_SITE:
                tx.append(name_id(nm))
        S['lon'].append(round(s['lon'], 3)); S['lat'].append(round(s['lat'], 3))
        S['plate'].append(s['plate'])
        S['ea'].append(round(s['ea'], 2)); S['la'].append(round(s['la'], 2))
        S['n'].append(len(seen) or s['n'])
        S['g'].append(max(gcount, key=gcount.get) if gcount else OTHER)
        S['nm'].append(s['name']); S['fm'].append(s['fm'])
        S['tx'].append(tx)
        S['lc'].append(loc_id(s['country'], s['state']))

        for label, kind in ((s['country'], 'country'),
                            (', '.join(x for x in (s['state'], s['country']) if x)
                             if s['state'] else None, 'region')):
            if not label:
                continue
            rec = places.setdefault(label, {'n': 0, 'k': kind, 'pts': []})
            rec['n'] += 1
            if len(rec['pts']) < 400:
                rec['pts'].append((s['lon'], s['lat'], s['plate']))

    # the chapter's species roster and the shape of its biota
    taxa = get('occs/taxa.json',
               {'max_ma': hi, 'min_ma': lo, 'rank': 'genus', 'show': 'class',
                'limit': 'all'}, f'{tag}_taxa').get('records', [])
    taxa.sort(key=lambda r: -(r.get('noc') or 0))
    roster = [[r['nam'], int(r.get('noc') or 0), group_of(r),
               (r.get('ttl') or '') if (r.get('ttl') or '').startswith(r['nam']) else '']
              for r in taxa[:ROSTER] if r.get('nam')]

    gtot = {}
    for r in taxa:
        g = group_of(r)
        c, n = gtot.get(g, (0, 0))
        gtot[g] = (c + 1, n + int(r.get('noc') or 0))
    breakdown = sorted(({'g': g, 'genera': c, 'occs': n}
                        for g, (c, n) in gtot.items()),
                       key=lambda x: -x['genera'])

    out = {
        'id': tag,
        'counts': {'colls': len(colls), 'sites': len(kept),
                   'genera': len(taxa),
                   'occs': sum(int(r.get('noc') or 0) for r in taxa)},
        'breakdown': breakdown,
        'groups': [g[0] for g in GROUPS] + ['Other'],
        'roster': roster,
        'names': names,
        'locs': locs,
        'sites': S,
    }
    return out, {s['plate'] for s in kept}


def gazetteer(places):
    """One searchable entry per place: the locality nearest the middle of its
    own localities, so the point is always somewhere fossils actually are."""
    out = []
    for label, rec in places.items():
        pts = rec['pts']
        if not pts:
            continue
        # mean direction on the sphere, so places spanning the date line behave
        x = y = z = 0.0
        for lon, lat, _ in pts:
            la, lo = math.radians(lat), math.radians(lon)
            c = math.cos(la)
            x += c * math.cos(lo); y += c * math.sin(lo); z += math.sin(la)
        n = math.sqrt(x * x + y * y + z * z)
        if n < 1e-9:
            lon0, lat0, plate = pts[0]
        else:
            x, y, z = x / n, y / n, z / n
            best, bd = pts[0], -2.0
            for lon, lat, plate in pts:
                la, lo = math.radians(lat), math.radians(lon)
                c = math.cos(la)
                d = c * math.cos(lo) * x + c * math.sin(lo) * y + math.sin(la) * z
                if d > bd:
                    bd, best = d, (lon, lat, plate)
            lon0, lat0, plate = best
        out.append({'n': label, 'k': rec['k'], 'c': rec['n'],
                    'lon': round(lon0, 3), 'lat': round(lat0, 3), 'p': plate})
    out.sort(key=lambda r: -r['c'])
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print('loading plate model...')
    loc = locate.PlateLocator(f'{SRC}/StaticPolygons/static_polygons.gpmlz')
    model = rotmodel.load(SRC)
    os.makedirs(OUT, exist_ok=True)
    countries = country_names()
    print(f'{len(countries)} country codes')

    places = {}
    plates, index = set(), {}
    for ch in CHAPTERS:
        if only and ch['id'] != only:
            continue
        if ch['start'] > 1000:          # PBDB has essentially nothing this old
            print(f"  {ch['name']}: skipped (before the fossil record)")
            continue
        data, used = build(ch, loc, model, countries, places)
        if not data:
            continue
        plates |= used
        with open(f'{OUT}/{ch["id"]}.json', 'w') as fh:
            json.dump(data, fh, separators=(',', ':'), ensure_ascii=False)
        kb = os.path.getsize(f'{OUT}/{ch["id"]}.json') / 1024
        index[ch['id']] = {'sites': data['counts']['sites'],
                           'genera': data['counts']['genera'],
                           'occs': data['counts']['occs'],
                           'colls': data['counts']['colls']}
        print(f'    -> {ch["id"]}.json  {kb:.0f} KB  '
              f'{data["counts"]["genera"]} genera')

    if not only:
        json.dump(index, open(f'{OUT}/index.json', 'w'), separators=(',', ':'))
        gaz = gazetteer(places)
        json.dump(gaz, open(f'{os.path.dirname(OUT)}/places.json', 'w'),
                  separators=(',', ':'), ensure_ascii=False)
        plates |= {p['p'] for p in gaz}
        json.dump(sorted(plates), open(f'{SRC}/fossil_plates.json', 'w'))
        print(f'\n{len(index)} chapters with fossils, {len(plates)} plates used')
        print(f'places.json: {len(gaz)} searchable places '
              f'({sum(1 for p in gaz if p["k"] == "country")} countries)')
        print('run plates.py after this so those plates get rotations')


if __name__ == '__main__':
    main()
