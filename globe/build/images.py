"""Resolve a Wikimedia Commons photo for every species in biota.json.

Queries the English Wikipedia for each binomial (following redirects), falls
back to the common name, then pulls author and licence from Commons so the page
can attribute each photo. Only URLs are stored - no image is redistributed.

Output: data/species_images.json  { binomial: {u: url, a: author, l: licence} }
Re-runs reuse src/images_cache.json, so only new species hit the network.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))
CACHE = os.path.join(SRC, 'images_cache.json')
UA = 'BiosphereGlobe/1.0 (https://github.com/Amiralexanderabed; educational project)'
THUMB = 400

def api(host, params):
    url = f'https://{host}/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 3:
                print('  ! give up:', e)
                return {}
            time.sleep(2 ** attempt)

def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]

def strip_html(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    return re.sub(r'\s+', ' ', s).strip()

def clean(url):
    return url.split('?')[0] if url else None

def lookup_titles(titles):
    """title -> (thumb url, commons file name) for whatever resolves."""
    found = {}
    for batch in chunks(titles, 50):
        d = api('en.wikipedia.org', {
            'action': 'query', 'format': 'json', 'formatversion': '2', 'redirects': '1',
            'prop': 'pageimages', 'piprop': 'thumbnail|name', 'pithumbsize': str(THUMB),
            'titles': '|'.join(batch)})
        q = d.get('query', {})
        back = {r['to']: r['from'] for r in q.get('redirects', [])}
        back.update({n['to']: n['from'] for n in q.get('normalized', [])})
        for p in q.get('pages', []):
            t = p.get('thumbnail')
            if not t:
                continue
            src = back.get(p['title'], p['title'])
            src = back.get(src, src)
            found[src] = (clean(t['source']), p.get('pageimage'))
        print(f'  ...{len(found)}/{len(titles)}', end='\r', flush=True)
        time.sleep(0.15)
    print()
    return found

def norm(f):
    """MediaWiki normalises underscores to spaces; key everything that way."""
    return (f or '').replace('_', ' ')

def file_credits(files, host):
    """File name -> (author, licence). Keys are normalised."""
    out = {}
    for batch in chunks(files, 50):
        d = api(host, {
            'action': 'query', 'format': 'json', 'formatversion': '2',
            'prop': 'imageinfo', 'iiprop': 'extmetadata',
            'titles': '|'.join('File:' + f for f in batch)})
        for p in d.get('query', {}).get('pages', []):
            ii = (p.get('imageinfo') or [{}])[0].get('extmetadata', {})
            if not ii:
                continue
            author = strip_html(ii.get('Artist', {}).get('value', ''))[:80]
            lic = strip_html(ii.get('LicenseShortName', {}).get('value', ''))[:40]
            if author or lic:
                out[norm(p['title'][5:])] = (author, lic)
        print(f'  ...{len(out)}/{len(files)}', end='\r', flush=True)
        time.sleep(0.15)
    print()
    return out

def main():
    index = dict(json.load(open(os.path.join(SRC, 'species_index.json'))))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [b for b in index if b not in cache]
    print(f'{len(index)} species, {len(todo)} to fetch')

    if todo:
        print('scientific names...')
        hits = lookup_titles(todo)
        for b in todo:
            cache[b] = {'u': hits[b][0], 'f': hits[b][1]} if b in hits else None

        missing = [b for b in todo if cache[b] is None]
        commons = {index[b]: b for b in missing if index[b] not in index}
        if commons:
            print(f'common names for {len(commons)} misses...')
            hits2 = lookup_titles(sorted(commons))
            for name, b in commons.items():
                if name in hits2:
                    cache[b] = {'u': hits2[name][0], 'f': hits2[name][1]}
        json.dump(cache, open(CACHE, 'w'))

    files = sorted({v['f'] for v in cache.values() if v and v.get('f') and 'c' not in v})
    if files:
        print(f'credits for {len(files)} files...')
        creds = file_credits(files, 'commons.wikimedia.org')
        # a minority are hosted on en.wikipedia rather than Commons
        rest = [f for f in files if norm(f) not in creds]
        if rest:
            print(f'{len(rest)} not on Commons, trying en.wikipedia...')
            creds.update(file_credits(rest, 'en.wikipedia.org'))
        for v in cache.values():
            if v and norm(v.get('f')) in creds:
                v['a'], v['l'] = creds[norm(v['f'])]
                v['c'] = 1
        json.dump(cache, open(CACHE, 'w'))

    out = {b: {'u': v['u'], 'a': v.get('a', ''), 'l': v.get('l', '')}
           for b, v in cache.items() if v and v.get('u')}
    json.dump(out, open(f'{OUT}/species_images.json', 'w'),
              separators=(',', ':'), ensure_ascii=False)
    print(f'\n{len(out)}/{len(index)} species have a photo '
          f'({len(index) - len(out)} without)')
    print('wrote species_images.json')

main()
