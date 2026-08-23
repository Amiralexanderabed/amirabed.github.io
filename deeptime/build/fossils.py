"""Per-chapter fossil localities and species lists from the Paleobiology Database.

For each chapter we pull every collection whose age falls inside it, thin them
down to a set that covers the map without burying the browser, and attach the
taxa found at each one.  Localities are given a plate id from the same model the
globe is drawn with, so a site stays glued to its own continent as the page
scrubs through time instead of floating off it.

Writes ../data/ch/<chapter>.json, one file per chapter, loaded on demand.
Raw API responses are cached in src/pbdb/, so re-runs are cheap.
"""
import json, os, sys, time, urllib.parse, urllib.request

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


def build(ch, loc, model):
    lo, hi = ch['end'], ch['start']
    mid = (lo + hi) / 2
    tag = ch['id']
    print(f"  {ch['name']} ({hi}-{lo} Ma)")

    colls = get('colls/list.json',
                {'max_ma': hi, 'min_ma': lo, 'show': 'paleoloc,strat',
                 'limit': 'all'}, f'{tag}_colls').get('records', [])
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
        sites.append({
            'id': c['oid'].split(':')[1], 'lon': lon, 'lat': lat, 'plate': plate,
            'plon': plon, 'plat': plat, 'n': int(c.get('noc') or 0),
            'name': clean(c.get('nam')), 'fm': clean(c.get('sfm') or '', 40),
            'ea': float(c.get('eag') or hi), 'la': float(c.get('lag') or lo),
        })

    kept = thin(sites, model)
    print(f'    {len(colls)} collections, {len(kept)} kept'
          + (f', {unplaced} without a plate' if unplaced else ''))

    # taxa at the kept localities, in batches the API is happy with
    by_coll = {}
    ids = [s['id'] for s in kept]
    for i in range(0, len(ids), 150):
        batch = ids[i:i + 150]
        d = get('occs/list.json',
                {'coll_id': ','.join(batch), 'show': 'class', 'limit': 'all'},
                f'{tag}_occs_{i//150}')
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

    S = {k: [] for k in ('lon', 'lat', 'plate', 'ea', 'la', 'n', 'g', 'nm', 'fm', 'tx')}
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
        'sites': S,
    }
    return out, {s['plate'] for s in kept}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print('loading plate model...')
    loc = locate.PlateLocator(f'{SRC}/StaticPolygons/static_polygons.gpmlz')
    model = rotmodel.load(SRC)
    os.makedirs(OUT, exist_ok=True)

    plates, index = set(), {}
    for ch in CHAPTERS:
        if only and ch['id'] != only:
            continue
        if ch['start'] > 1000:          # PBDB has essentially nothing this old
            print(f"  {ch['name']}: skipped (before the fossil record)")
            continue
        data, used = build(ch, loc, model)
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
        json.dump(sorted(plates), open(f'{SRC}/fossil_plates.json', 'w'))
        print(f'\n{len(index)} chapters with fossils, {len(plates)} plates used')
        print('run plates.py after this so those plates get rotations')


if __name__ == '__main__':
    main()
