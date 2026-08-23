"""Find a photograph for every species and scene named in chapters.py.

Looks each name up on the English Wikipedia, takes the article's lead image,
then asks Commons who made it and under what licence so the page can credit it.
Only URLs are stored - no image is copied into this repository.

Output: ../data/images.json  { "sp:Name" | "sc:Title": {u, a, l, c} }
Re-runs reuse src/img_cache.json, so only new names hit the network.
"""
import html, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))
CACHE = os.path.join(SRC, 'img_cache.json')
UA = 'DeepTime/1.0 (https://amirabed.com; educational project)'
THUMB = 640

sys.path.insert(0, HERE)
from chapters import CHAPTERS


def api(host, params):
    url = f'https://{host}/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
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
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def first_sentence(s, n=150):
    """Wikipedia intros open with pronunciation and etymology in brackets, which
    `explaintext` empties out into "Sauropoda (), whose ...".  Drop all of it."""
    s = re.sub(r'\s+', ' ', s or '').strip()
    for _ in range(4):
        s = re.sub(r'\s*\([^()]*\)', '', s)
    s = re.sub(r'\s*\([^)]*$', '', s)          # an opening bracket never closed
    s = re.sub(r'\s+([,.;:])', r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip()
    m = re.match(r'^(.{40,%d}?[.!?])(\s|$)' % n, s + ' ')
    out = m.group(1) if m else s[:n].rsplit(' ', 1)[0] + '…'
    return out.strip()


def lookup(titles):
    """title -> (thumb url, commons file, lead sentence)."""
    found = {}
    for batch in chunks(titles, 20):
        d = api('en.wikipedia.org', {
            'action': 'query', 'format': 'json', 'formatversion': '2',
            'redirects': '1', 'prop': 'pageimages|extracts',
            'piprop': 'thumbnail|name', 'pithumbsize': str(THUMB),
            'exintro': '1', 'explaintext': '1', 'exsentences': '2', 'exlimit': 'max',
            'titles': '|'.join(batch)})
        q = d.get('query', {})
        back = {r['to']: r['from'] for r in q.get('redirects', [])}
        back.update({n['to']: n['from'] for n in q.get('normalized', [])})
        for p in q.get('pages', []):
            t = p.get('thumbnail')
            src = back.get(p['title'], p['title'])
            src = back.get(src, src)
            if not t:
                continue
            found[src] = (t['source'].split('?')[0], p.get('pageimage'),
                          first_sentence(p.get('extract', '')))
        print(f'  ...{len(found)}/{len(titles)}', end='\r', flush=True)
        time.sleep(0.15)
    print(' ' * 30, end='\r')
    return found


DIAGRAM = re.compile(r'diagram|chart|cladogram|phylogen|timeline|stratigraph|'
                     r'distribution|\brange\b|scale|logo|icon|graph|\bmap\b|'
                     r'anatomy|question|commons-logo|wiki', re.I)
GOOD = re.compile(r'_NT\b|restoration|reconstruction|life|_BW\b', re.I)


def lead_from_article(title):
    """Some articles have no page image at all.  Fall back to the first
    plausible picture in the article body."""
    t = urllib.parse.quote(title.replace(' ', '_'), safe='')
    req = urllib.request.Request(
        f'https://en.wikipedia.org/api/rest_v1/page/media-list/{t}',
        headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            items = json.load(r).get('items', [])
    except Exception:
        return None
    best, score = None, -99
    first_word = title.split()[0].lower()
    for i, it in enumerate(items[:10]):
        if it.get('type') != 'image':
            continue
        name = it.get('title', '')[5:]
        if not name or name.lower().endswith(('.svg', '.gif')):
            continue
        s = 6 - i
        if DIAGRAM.search(name):
            s -= 8
        if GOOD.search(name):
            s += 4
        if first_word in name.lower():
            s += 3
        if s > score:
            best, score = name, s
    return best


def credits(files, host):
    out = {}
    for batch in chunks(files, 40):
        d = api(host, {
            'action': 'query', 'format': 'json', 'formatversion': '2',
            'prop': 'imageinfo', 'iiprop': 'extmetadata',
            'titles': '|'.join('File:' + f for f in batch)})
        for p in d.get('query', {}).get('pages', []):
            ii = (p.get('imageinfo') or [{}])[0].get('extmetadata', {})
            if not ii:
                continue
            author = strip_html(ii.get('Artist', {}).get('value', ''))[:70]
            lic = strip_html(ii.get('LicenseShortName', {}).get('value', ''))[:34]
            out[p['title'][5:].replace('_', ' ')] = (author, lic)
        print(f'  ...{len(out)}/{len(files)}', end='\r', flush=True)
        time.sleep(0.15)
    print(' ' * 30, end='\r')
    return out


def thumb_url(name):
    """A sized thumbnail for one file.  iiurlwidth only works a page at a time,
    so this is deliberately not batched."""
    d = api('commons.wikimedia.org', {
        'action': 'query', 'format': 'json', 'formatversion': '2',
        'prop': 'imageinfo', 'iiprop': 'url', 'iiurlwidth': str(THUMB),
        'titles': 'File:' + name})
    for p in d.get('query', {}).get('pages', []):
        info = (p.get('imageinfo') or [{}])[0]
        u = info.get('thumburl') or info.get('url')
        if u:
            return u.split('?')[0]
    return ''


def main():
    wanted = {}
    for c in CHAPTERS:
        for name, _ in c['featured']:
            wanted.setdefault('sp:' + name, name)
        for t in c['scenes']:
            wanted.setdefault('sc:' + t, t)

    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = sorted({v for k, v in wanted.items() if k not in cache})
    print(f'{len(wanted)} names, {len(todo)} to look up')

    if todo:
        hits = lookup(todo)
        for k, title in wanted.items():
            if k in cache:
                continue
            h = hits.get(title)
            cache[k] = {'u': h[0], 'f': h[1], 'c': h[2]} if h else None
        misses = sorted({t for k, t in wanted.items() if cache.get(k) is None})
        if misses:
            print(f'{len(misses)} without a lead image, checking article bodies...')
            for i, title in enumerate(misses):
                f = lead_from_article(title)
                if f:
                    for k, t in wanted.items():
                        if t == title and cache.get(k) is None:
                            cache[k] = {'u': '', 'f': f, 'c': ''}
                print(f'  ...{i+1}/{len(misses)}', end='\r', flush=True)
                time.sleep(0.2)
            print(' ' * 30, end='\r')
        json.dump(cache, open(CACHE, 'w'))

    files = sorted({v['f'] for v in cache.values() if v and v.get('f') and 'a' not in v})
    if files:
        print(f'credits for {len(files)} files...')
        cr = credits(files, 'commons.wikimedia.org')
        rest = [f for f in files if f.replace('_', ' ') not in cr]
        if rest:
            cr.update(credits(rest, 'en.wikipedia.org'))
        for v in cache.values():
            if v and v.get('f'):
                v['a'], v['l'] = cr.get(v['f'].replace('_', ' '), ('', ''))
        json.dump(cache, open(CACHE, 'w'))

    # entries that came from the article-body fallback have no URL yet
    need = [v for v in cache.values() if v and v.get('f') and not v.get('u')]
    if need:
        print(f'thumbnails for {len(need)} fallback images...')
        for i, v in enumerate(need):
            v['u'] = thumb_url(v['f'])
            print(f'  ...{i+1}/{len(need)}', end='\r', flush=True)
            time.sleep(0.2)
        print(' ' * 30, end='\r')
        json.dump(cache, open(CACHE, 'w'))

    out = {}
    for k, v in cache.items():
        if not v or not v.get('u'):
            continue
        rec = {'u': v['u'], 'a': v.get('a', ''), 'l': v.get('l', '')}
        if k.startswith('sc:') and v.get('c'):
            rec['c'] = v['c']
        out[k] = rec
    json.dump(out, open(f'{OUT}/images.json', 'w'),
              separators=(',', ':'), ensure_ascii=False)
    miss = [k for k in wanted if k not in out]
    print(f'{len(out)}/{len(wanted)} have a photo ({os.path.getsize(f"{OUT}/images.json")/1024:.0f} KB)')
    if miss:
        print('no photo for:', ', '.join(sorted(m[3:] for m in miss)[:25]),
              f'... ({len(miss)} total)' if len(miss) > 25 else '')


if __name__ == '__main__':
    main()
