"""Assemble data/biota.json from the curated terrestrial and marine lists."""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biota_1, biota_2, biota_3, biota_var, biota_more, marine_biota

OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))

def merge(base, extra):
    """Append extra species, dropping anything already present by binomial."""
    seen = {s[1] for s in base}
    out = list(base)
    for s in extra or []:
        if s[1] not in seen:
            seen.add(s[1])
            out.append(s)
    return out

codes = {}
for m in (biota_1, biota_2, biota_3):
    codes.update(m.CODES)
codes.update(biota_var.BASE_OVERRIDE)

meta = json.load(open(f'{OUT}/ecoregions.json'))
present = {e['code'] for e in meta['ecoregions'] if e['code'] and e['code'] != 'N/A'}
assert not (present - set(codes)), sorted(present - set(codes))
assert not (set(codes) - present), sorted(set(codes) - present)

biota = {
    'biomes': {str(k): {'name': v[0], 'short': v[1], 'color': v[2], 'about': v[3]}
               for k, v in biota_1.BIOMES.items()},
    'realms': {k: {'name': v[0], 'about': v[1]} for k, v in biota_1.REALMS.items()},
    'groups': {'M': 'Mammal', 'B': 'Bird', 'R': 'Reptile', 'A': 'Amphibian',
               'F': 'Fish', 'I': 'Invertebrate', 'P': 'Plant', 'O': 'Other'},
    'codes': {},
}

for k, (title, about, species) in codes.items():
    biota['codes'][k] = {'title': title, 'about': about,
                         'species': merge(species, biota_more.EXTRA.get(k))}

for k, vs in biota_var.VARIANTS.items():
    assert k in biota['codes'], k
    biota['codes'][k]['variants'] = [
        {'box': b, 'title': t, 'about': a,
         'species': merge(sp, biota_more.EXTRA.get(f'{k}@{i}'))}
        for i, (b, t, a, sp) in enumerate(vs)]

# --- marine ---
marine_meta = json.load(open(f'{OUT}/marine.json'))
mrealms = {u['realm'] for u in marine_meta['units']}
mprov = {u['province'] for u in marine_meta['units']}
mbiomes = {u['biome'] for u in marine_meta['units']}
assert not (mrealms - set(marine_biota.REALM_SPECIES)), sorted(mrealms - set(marine_biota.REALM_SPECIES))
assert not (set(marine_biota.PROVINCE_SPECIES) - mprov), sorted(set(marine_biota.PROVINCE_SPECIES) - mprov)
assert not (mbiomes - set(marine_biota.MARINE_BIOMES)), sorted(mbiomes - set(marine_biota.MARINE_BIOMES))

biota['marine'] = {
    'biomes': {k: {'color': v[0], 'about': v[1]} for k, v in marine_biota.MARINE_BIOMES.items()},
    'realmColors': marine_biota.MARINE_REALM_COLOR,
    'realms': {k: {'about': marine_biota.REALM_ABOUT[k], 'species': v}
               for k, v in marine_biota.REALM_SPECIES.items()},
    'provinces': {k: {'title': v[0], 'about': v[1], 'species': v[2]}
                  for k, v in marine_biota.PROVINCE_SPECIES.items()},
}

# --- report ---
def all_lists():
    for c in biota['codes'].values():
        yield c['species']
        for v in c.get('variants', []):
            yield v['species']
    for r in biota['marine']['realms'].values():
        yield r['species']
    for p in biota['marine']['provinces'].values():
        yield p['species']

lists = list(all_lists())
species = {s[1]: s[0] for lst in lists for s in lst}
sizes = sorted(len(l) for l in lists)
print(f"lists: {len(lists)}  |  entries: {sum(sizes)}  |  unique species: {len(species)}")
print(f"per-list species: min {sizes[0]}, median {sizes[len(sizes)//2]}, max {sizes[-1]}")
thin = [(len(c['species']), k) for k, c in biota['codes'].items() if len(c['species']) < 12]
if thin:
    print("thin lists:", sorted(thin))

json.dump(biota, open(f'{OUT}/biota.json', 'w'), separators=(',', ':'), ensure_ascii=False)
json.dump(sorted(species.items()), open(os.path.join(HERE, 'src', 'species_index.json'), 'w'),
          ensure_ascii=False)
print('wrote biota.json')
