"""The written spine of the timeline: one chapter per slice of Earth history.

Everything a chapter shows that is *not* measured data lives here - the
narrative, the dated events, the curated species, and the parameters the globe
shades itself with (ice line, how green the land is, how deep the shelf seas
are).  The measured layers - plate positions, fossil localities, species lists -
are fetched by the other build scripts and joined to these by chapter id.

Writes ../data/chapters.json.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'data'))


# ---------------------------------------------------------------------------
# Global curves.  Control points are digitised from the published compilations
# named in SOURCES; the page interpolates between them and labels them as
# indicative rather than as the source data.  Ages in Ma.
# ---------------------------------------------------------------------------

# Global mean surface temperature, degrees C.
# Scotese et al. 2021 (Earth-Sci. Rev. 215) for the Phanerozoic, cross-checked
# against Judd et al. 2024 (Science 385) PhanDA; Precambrian is a coarse
# consensus sketch and is drawn dashed on the page.
TEMP = [
    (4500, 85), (4000, 70), (3500, 55), (3000, 45), (2600, 35), (2450, 22),
    (2350, 5), (2200, 20), (1800, 25), (1400, 24), (1100, 22), (900, 20),
    (717, 4), (700, -5), (660, 8), (650, -4), (635, 12), (600, 18), (560, 20),
    (541, 22), (520, 26), (500, 28), (490, 26), (470, 24), (455, 20), (445, 14),
    (440, 18), (430, 22), (420, 23), (410, 24), (395, 25), (380, 26), (370, 23),
    (359, 20), (345, 18), (330, 15), (315, 13), (300, 13), (290, 16), (275, 20),
    (260, 22), (252, 28), (250, 30), (245, 26), (237, 24), (220, 23), (201, 25),
    (195, 22), (180, 21), (165, 20), (150, 21), (130, 22), (120, 25), (94, 28),
    (80, 25), (70, 23), (66, 24), (60, 22), (56, 27), (50, 26), (40, 22),
    (34, 17), (30, 16), (23, 17), (16, 18), (10, 15), (5, 14), (3, 15),
    (2, 13), (0.8, 11), (0.02, 12), (0, 15),
]

# Atmospheric CO2, ppm.  Foster, Royer & Lunt 2017 (Nat. Commun. 8) for the
# Phanerozoic; GEOCARB-style estimates before it.
CO2 = [
    (4500, 400000), (4000, 200000), (3500, 90000), (3000, 40000),
    (2500, 20000), (2400, 3000), (2000, 8000), (1500, 6000), (1000, 4000),
    (720, 1500), (700, 3000), (635, 2000), (600, 1800), (541, 4500),
    (500, 5000), (460, 4000), (445, 2500), (430, 3500), (400, 3000),
    (380, 2200), (360, 1200), (340, 600), (320, 350), (300, 280), (290, 400),
    (275, 900), (260, 1200), (252, 2500), (245, 2000), (220, 1800),
    (201, 2400), (180, 1800), (150, 1200), (120, 1000), (94, 1100), (80, 700),
    (66, 600), (60, 500), (56, 900), (50, 700), (40, 500), (34, 350),
    (23, 300), (16, 400), (5, 350), (2.6, 300), (0.8, 250), (0.02, 265),
    (0, 420),
]

# Atmospheric O2, percent by volume.  Berner GEOCARBSULF and Lenton et al. 2016;
# the Proterozoic values are order-of-magnitude only.
O2 = [
    (4500, 0.0001), (3000, 0.0001), (2500, 0.001), (2400, 2), (2200, 4),
    (2000, 3), (1800, 2), (1400, 2), (1000, 3), (800, 5), (700, 6), (635, 8),
    (580, 12), (541, 14), (500, 15), (460, 15), (445, 16), (430, 17),
    (400, 17), (380, 18), (370, 20), (359, 22), (340, 26), (320, 31),
    (305, 35), (300, 33), (290, 30), (275, 25), (260, 22), (252, 16),
    (250, 12), (240, 13), (220, 16), (201, 17), (180, 18), (150, 20),
    (120, 21), (94, 22), (66, 23), (56, 22), (34, 21), (23, 21), (5, 21),
    (0, 20.9),
]

# Sea level relative to today, metres.  Haq & Schutter 2008 / Miller et al. 2005
# long-term curve, smoothed.
SEA = [
    (4500, 0), (1000, 20), (720, 10), (635, 20), (541, 30), (500, 120),
    (470, 180), (445, 60), (430, 140), (400, 150), (380, 220), (359, 100),
    (340, 80), (320, 40), (300, -20), (290, 20), (260, 40), (252, 20),
    (245, 30), (220, 60), (201, 40), (180, 80), (150, 120), (120, 140),
    (94, 250), (80, 200), (66, 120), (56, 90), (34, 40), (23, 30), (16, 40),
    (5, 20), (2.6, 10), (0.8, -60), (0.02, -35), (0, 0),
]

# Latitude the year-round ice reaches, degrees from the pole's own hemisphere.
# 90 = no permanent ice at all.  From the glacial record: Huronian, Cryogenian,
# Hirnantian, Karoo, and the Cenozoic build-up.
ICE = [
    (4500, 90), (2450, 90), (2400, 25), (2300, 90), (1000, 90), (720, 90),
    (717, 7), (665, 7), (660, 55), (655, 62), (650, 6), (636, 6), (635, 82),
    (541, 90), (450, 90), (445, 45),
    (440, 80), (430, 90), (360, 90), (340, 60), (320, 40), (300, 35),
    (290, 50), (270, 72), (260, 90), (66, 90), (40, 86), (34, 74), (30, 72),
    (23, 73), (14, 70), (10, 69), (5, 68), (3, 66), (2.6, 62), (1, 58),
    (0.021, 55), (0.02, 50), (0.015, 58), (0, 68),
]

# How much of the land is covered by plants, 0-1.  Drives the globe's colour:
# bare rock before the Ordovician, greening through the Silurian and Devonian,
# forested from the Carboniferous on.
GREEN = [
    (4500, 0), (500, 0), (470, 0.02), (443, 0.05), (430, 0.10), (420, 0.15),
    (400, 0.25), (385, 0.45), (370, 0.60), (359, 0.70), (330, 0.85),
    (305, 0.90), (299, 0.75), (280, 0.65), (252, 0.25), (250, 0.20),
    (240, 0.45), (220, 0.60), (201, 0.65), (180, 0.72), (145, 0.75),
    (100, 0.80), (66, 0.70), (60, 0.80), (50, 0.88), (34, 0.82), (23, 0.80),
    (10, 0.78), (2.6, 0.72), (0.02, 0.78), (0, 0.70),
]

# How much of the surface is still a magma ocean, 0-1.  Zircon evidence puts
# liquid water on the surface by about 4.4 Ga.
MOLTEN = [(4567, 1.0), (4500, 1.0), (4450, 0.85), (4400, 0.35), (4350, 0.08), (4300, 0)]

SOURCES = [
    ('Plate reconstruction',
     'Müller et al. (2025) global plate model, 0–1800 Ma, via the GPlates Plate '
     'Model Manager. Coastlines and continental crust are rotated by the model’s '
     'own finite-rotation file; positions match the GPlates Web Service to 1e-4°.'),
    ('Fossil localities and species',
     'The Paleobiology Database (paleobiodb.org), downloaded per chapter. Each '
     'locality is placed on its plate and drifts with it.'),
    ('Temperature',
     'Scotese et al. (2021), Earth-Science Reviews 215; cross-checked against '
     'Judd et al. (2024) PhanDA.'),
    ('CO₂', 'Foster, Royer & Lunt (2017), Nature Communications 8; GEOCARB for '
            'the Precambrian.'),
    ('O₂', 'Berner GEOCARBSULF and Lenton et al. (2016).'),
    ('Sea level', 'Haq & Schutter (2008) and Miller et al. (2005), smoothed.'),
    ('Images', 'Wikipedia and Wikimedia Commons; each photo credits its author '
               'and licence. No image is copied into this site.'),
]

DISCLAIMER = (
    'Curves are digitised from the published compilations listed above and are '
    'indicative, not the source data. Deep-time values — especially before the '
    'Cambrian — carry large uncertainties.'
)


CHAPTERS = [
{
 'id': 'hadean', 'name': 'Hadean', 'sub': 'A planet made of fire',
 'start': 4567, 'end': 4031, 'color': '#A83A94', 'era': 'Hadean', 'eon': 'Hadean',
 'lede': 'Earth assembles out of the debris around a young Sun, is hit by a '
         'planet, and cools just enough to hold an ocean.',
 'story': [
   'The Earth grows by collision. Rock and metal left over from the Sun’s '
   'formation clump into ever larger bodies until, within about 100 million '
   'years, one of them is our planet. The energy of all that infalling matter '
   'has nowhere to go, so the surface is molten: a magma ocean hundreds of '
   'kilometres deep, under a thick atmosphere of steam and carbon dioxide, lit '
   'by a Sun about 30% fainter than today’s.',
   'Then something the size of Mars hits. The impact strips away a huge volume '
   'of Earth’s mantle, re-melts what is left, and the debris settles into orbit '
   'and coalesces into the Moon — which at first hangs perhaps fifteen times '
   'closer than it does now, raising enormous tides and pulling the young '
   'Earth’s day down to a few hours.',
   'Cooling is faster than the name "Hadean" suggests. Zircon crystals from the '
   'Jack Hills of Western Australia, some of them 4.4 billion years old, formed '
   'in granite-like melts in the presence of liquid water. Within roughly 150 '
   'million years of the Moon-forming impact there is already an ocean, a '
   'crust, and a chemistry set running on a global scale.',
 ],
 'world': 'No continents in any modern sense — only scraps of proto-crust '
          'floating on a mantle far hotter than today’s, repeatedly resurfaced '
          'by impacts and eruptions.',
 'events': [
   (4567, 'The Solar System begins', 'The oldest solids in meteorites — '
    'calcium-aluminium inclusions — condense. This date is the zero point for '
    'the age of everything else.'),
   (4510, 'The Moon-forming impact', 'A Mars-sized body, usually called Theia, '
    'strikes the proto-Earth. The Moon forms from the debris within a century '
    'or so, and Earth’s spin axis and day length are set.'),
   (4400, 'Liquid water', 'The Jack Hills zircons record granitic melts and '
    'water-rock interaction — the oldest direct evidence that Earth had an '
    'ocean and something like a crust.'),
   (4100, 'Possible earliest life', 'Graphite grains in Jack Hills zircons, and '
    'later carbon in Greenland rocks, carry the light carbon signature that '
    'life leaves behind. The evidence is contested but persistent.'),
 ],
 'firsts': ['An ocean', 'A crust', 'A moon', 'A magnetic field'],
 'featured': [],
 'scenes': ['Hadean', 'Giant-impact hypothesis', 'Magma ocean', 'Jack Hills'],
},
{
 'id': 'archean', 'name': 'Archean', 'sub': 'Life without oxygen',
 'start': 4031, 'end': 2500, 'color': '#F0047F', 'era': 'Archean', 'eon': 'Archean',
 'lede': 'For a billion and a half years the planet is inhabited, warm, and '
         'almost completely airless in the sense that matters to us: no oxygen.',
 'story': [
   'By 3.5 billion years ago life is unmistakable. Stromatolites — layered '
   'mounds built by mats of microbes trapping sediment — appear in Western '
   'Australia and South Africa, and their descendants still grow in Shark Bay '
   'today. The metabolisms of the time run on hydrogen, iron, sulphur and '
   'methane. Photosynthesis exists but does not yet split water.',
   'The atmosphere is nitrogen and carbon dioxide with a great deal of methane '
   'and no free oxygen. The Sun is still 20–25% dimmer than today, yet there is '
   'no global glaciation for most of this eon — the "faint young Sun paradox", '
   'resolved by a much stronger greenhouse.',
   'Continents are being made. Small cratons — the ancient cores of every '
   'modern continent, from the Pilbara to the Kaapvaal to the Superior — weld '
   'together out of volcanic arcs and greenstone belts. Some time in this eon, '
   'cyanobacteria invent oxygenic photosynthesis, and the oxygen they release '
   'is soaked up by dissolved iron, which settles out as the banded iron '
   'formations that supply most of the world’s iron ore.',
 ],
 'world': 'Dozens of small, hot cratons in a global ocean. Plate tectonics is '
          'starting up, but the crust is thinner and the mantle hotter, so the '
          'style is not quite the modern one.',
 'events': [
   (4031, 'The oldest rock', 'The Acasta Gneiss in northwest Canada — the '
    'oldest intact piece of continental crust yet dated, and the marker that '
    'now defines the base of the Archean.'),
   (3700, 'Isua', 'Banded iron and pillow lavas in Greenland record deep water, '
    'and carbon isotopes there are widely read as biological.'),
   (3480, 'Stromatolites', 'The Dresser Formation of the Pilbara preserves '
    'microbial mounds, and with them the oldest broadly accepted fossils.'),
   (3200, 'Oxygenic photosynthesis', 'Cyanobacteria begin splitting water for '
    'hydrogen and dumping oxygen as waste. It will take the better part of a '
    'billion years for that waste to accumulate.'),
   (2700, 'Cratons stabilise', 'A pulse of continental growth builds the cores '
    'of most modern continents.'),
 ],
 'firsts': ['Cells', 'Stromatolites', 'Photosynthesis', 'Continental crust'],
 'featured': [
   ('Cyanobacteria', 'The organism that changed the atmosphere: the first to '
    'split water for hydrogen and release oxygen as waste.'),
   ('Stromatolite', 'Not a species but a structure — layered rock built up by '
    'microbial mats, and the dominant fossil of the Precambrian.'),
   ('Archaea', 'A whole domain of life adapted to heat, salt and sulphur, and '
    'the lineage our own cells’ ancestor came from.'),
 ],
 'scenes': ['Archean', 'Stromatolite', 'Banded iron formation', 'Greenstone belt'],
},
{
 'id': 'paleoproterozoic', 'name': 'Paleoproterozoic', 'sub': 'The oxygen catastrophe',
 'start': 2500, 'end': 1600, 'color': '#F74370', 'era': 'Paleoproterozoic',
 'eon': 'Proterozoic',
 'lede': 'Oxygen floods the air, nearly everything alive is poisoned, the '
         'planet freezes — and the complex cell is invented.',
 'story': [
   'Around 2.4 billion years ago, free oxygen finally overwhelms the chemical '
   'sinks that had been absorbing it and starts to build up in the atmosphere. '
   'For the anaerobic microbes that had run the world, oxygen is a poison, and '
   'the Great Oxidation Event is probably the largest extinction in Earth’s '
   'history measured by the fraction of life affected.',
   'It also breaks the climate. Oxygen destroys atmospheric methane, a powerful '
   'greenhouse gas, and the planet drops into the Huronian glaciation — a '
   'series of ice ages lasting on and off for 300 million years, quite possibly '
   'the first time ice reached the equator.',
   'Out of that upheaval comes the eukaryotic cell. One cell takes up another — '
   'a bacterium that could use oxygen — and instead of digesting it, keeps it. '
   'That captive becomes the mitochondrion, and every plant, animal, fungus and '
   'seaweed since is descended from that merger. By the end of this era the '
   'first supercontinent we can map with confidence, Nuna, is assembled.',
 ],
 'world': 'Cratons collide into Nuna (also called Columbia), the first '
          'reasonably well-established supercontinent, around 1.8 billion years '
          'ago.',
 'events': [
   (2450, 'The Great Oxidation Event', 'Free oxygen appears in the atmosphere '
    'for good. Banded iron formation peaks and then largely stops: the oceans '
    'have run out of dissolved iron to rust.'),
   (2400, 'Huronian glaciation', 'With methane oxidised away, ice spreads '
    'possibly to the tropics — arguably the first Snowball Earth.'),
   (2100, 'Eukaryotes', 'Cells with a nucleus and mitochondria. The Francevillian '
    'biota of Gabon, from about this age, may be the oldest large '
    'multicellular organisms, though the interpretation is debated.'),
   (1800, 'Nuna assembles', 'A supercontinent forms; the Gunflint chert of '
    'Ontario preserves an exquisite microbial ecosystem from about this time.'),
 ],
 'firsts': ['Free oxygen', 'Global glaciation', 'The eukaryotic cell',
            'Mitochondria', 'A supercontinent'],
 'featured': [
   ('Grypania', 'Coiled ribbons up to a few centimetres long — possibly the '
    'oldest large organism, and probably an alga.'),
   ('Gunflintia', 'A filamentous microfossil from the 1.88-billion-year-old '
    'Gunflint chert, one of the first Precambrian fossils ever recognised.'),
   ('Francevillian biota', 'Centimetre-scale disc and lobe shapes from Gabon, '
    'possibly colonial life 2.1 billion years ago.'),
 ],
 'scenes': ['Great Oxidation Event', 'Huronian glaciation', 'Gunflint chert',
            'Eukaryote'],
},
{
 'id': 'mesoproterozoic', 'name': 'Mesoproterozoic', 'sub': 'The billion quiet years',
 'start': 1600, 'end': 1000, 'color': '#FDB462', 'era': 'Mesoproterozoic',
 'eon': 'Proterozoic',
 'lede': 'Six hundred million years of remarkably little change — and then sex, '
         'and the first thing that looks like a plant.',
 'story': [
   'This stretch has a nickname among geologists: the Boring Billion. Carbon '
   'and oxygen isotopes stay flat, there are no global glaciations, sea level '
   'barely moves, and the supercontinent Nuna sits largely intact before '
   'reassembling as Rodinia. Oxygen appears to have stalled at a few percent of '
   'modern levels — enough for eukaryotes, not enough for animals.',
   'Underneath the quiet, cells are getting more elaborate. Around 1.05 billion '
   'years ago, a red alga called *Bangiomorpha* is preserved in Arctic Canada '
   'in the act of doing something new: it has differentiated cell types, it is '
   'anchored to the seafloor, and it reproduces sexually. It is the oldest '
   'fossil that can be assigned to a living group with confidence, and the '
   'oldest good evidence for sex.',
   'Meanwhile a second endosymbiosis has happened — a eukaryote swallows a '
   'cyanobacterium and keeps it as a chloroplast. Everything that photosynthesises '
   'in a nucleated cell, from kelp to oak trees, traces back to that event.',
 ],
 'world': 'Nuna breaks up slowly and its pieces re-gather into Rodinia toward '
          'the end of the era, with the Grenville mountain belt marking the '
          'final collisions.',
 'events': [
   (1400, 'Oxygen stalls', 'Atmospheric oxygen holds at perhaps 1–4% of the '
    'modern level for hundreds of millions of years, apparently limited by '
    'nutrient supply and a sulphidic ocean.'),
   (1200, 'Bangiomorpha', 'A red alga with specialised cells and sexual '
    'reproduction — the first fossil that can be placed in a modern group.'),
   (1100, 'Rodinia assembles', 'The Grenville orogeny welds the continents '
    'together into a supercontinent that will sit astride the equator.'),
 ],
 'firsts': ['Sexual reproduction', 'Chloroplasts', 'Multicellular algae'],
 'featured': [
   ('Bangiomorpha', 'A one-millimetre red alga from 1.05 billion years ago — '
    'the oldest fossil with differentiated cells and sex.'),
   ('Rafatazmia', 'Filaments in 1.6-billion-year-old Indian phosphorite that '
    'may push crown-group red algae back further still.'),
   ('Acritarch', 'A catch-all name for organic-walled microfossils — mostly the '
    'resting cysts of single-celled eukaryotes, and the workhorse of '
    'Precambrian biostratigraphy.'),
 ],
 'scenes': ['Boring Billion', 'Bangiomorpha', 'Rodinia', 'Red algae'],
},
{
 'id': 'tonian', 'name': 'Tonian', 'sub': 'Rodinia comes apart',
 'start': 1000, 'end': 720, 'color': '#FEBF4E', 'era': 'Neoproterozoic',
 'eon': 'Proterozoic',
 'lede': 'A supercontinent splits along its middle, flooding the world with new '
         'coastline — and the first animals appear, too small and soft to '
         'leave much behind.',
 'story': [
   'Rodinia begins to rift apart around 825 million years ago. Rifting is a '
   'climate event as much as a tectonic one: fresh basalt weathers fast, '
   'drawing carbon dioxide out of the air, while new shallow seas bury organic '
   'carbon. Both push the planet toward the deep freeze that follows.',
   'Molecular clocks — the rate at which genetic differences accumulate between '
   'living lineages — put the origin of animals somewhere in this period. The '
   'fossil record is thin, but there are biomarkers: 24-isopropylcholestane, a '
   'molecule made by demosponges, turns up in rocks of this age. The first '
   'animals were probably sponge-grade, millimetres across, and sitting on the '
   'seafloor.',
   'Eukaryotes diversify visibly for the first time. Vase-shaped microfossils — '
   'the tests of amoebae — appear in the Grand Canyon and elsewhere, and give '
   'the first clear evidence of one eukaryote eating another.',
 ],
 'world': 'Rodinia straddles the equator and starts to break apart, opening the '
          'first rift basins along what will become the margins of Laurentia.',
 'events': [
   (825, 'Rodinia rifts', 'Large igneous provinces punch through the '
    'supercontinent and it begins to separate, opening new ocean basins.'),
   (800, 'Vase-shaped microfossils', 'Testate amoebae leave the first clear '
    'record of eukaryotes preying on eukaryotes.'),
   (760, 'Sponge biomarkers', 'Steroid molecules unique to demosponges appear '
    'in Omani rocks — chemical traces of the first animals.'),
 ],
 'firsts': ['Animals (probably)', 'Predatory eukaryotes', 'Biomineralised scales'],
 'featured': [
   ('Melanocyrillium', 'A vase-shaped microfossil — the shell of an amoeba, and '
    'evidence that eukaryotes were already eating each other.'),
   ('Demosponge', 'The sponge lineage whose distinctive steroids appear in '
    'rocks of this age, before any sponge body fossil.'),
   ('Cladophora', 'Green algae of this general kind were already photosynthesising '
    'in Tonian seas.'),
 ],
 'scenes': ['Tonian', 'Rodinia', 'Sponge', 'Neoproterozoic'],
},
{
 'id': 'cryogenian', 'name': 'Cryogenian', 'sub': 'Snowball Earth',
 'start': 720, 'end': 635, 'color': '#FECC5C', 'era': 'Neoproterozoic',
 'eon': 'Proterozoic',
 'lede': 'Twice, ice reaches the equator and stays for millions of years. Life '
         'survives, and comes out the other side about to become complicated.',
 'story': [
   'The Sturtian glaciation begins around 717 million years ago and lasts, '
   'astonishingly, some 57 million years. Glacial deposits of this age are '
   'found on every continent, including at sea level in the tropics. The '
   'standard explanation is a runaway: ice reflects sunlight, cooling the '
   'planet, which grows more ice. Once the ice line reaches about 30° latitude '
   'the feedback runs away to the equator.',
   'What ends it is volcanoes. With the water cycle shut down there is almost '
   'no weathering to remove carbon dioxide, so volcanic CO₂ builds up over '
   'millions of years until the greenhouse is strong enough to melt the ice — '
   'catastrophically fast, into a hothouse, leaving the strange "cap carbonates" '
   'that sit directly on glacial debris the world over.',
   'It happens again: the Marinoan glaciation, ending about 635 million years '
   'ago. Life came through both, presumably in refuges — open water near '
   'volcanoes, meltwater ponds on the ice, the deep sea. And the oceans that '
   'followed were better oxygenated than any before them.',
 ],
 'world': 'The rifted fragments of Rodinia sit mostly at low latitudes, which '
          'is part of why the runaway was possible: tropical continents weather '
          'fast and pull down CO₂.',
 'events': [
   (717, 'Sturtian glaciation begins', 'Ice sheets reach sea level in the '
    'tropics and hold there for some 57 million years — the longest glaciation '
    'in Earth history.'),
   (660, 'The Sturtian ends', 'Volcanic CO₂ accumulates until the ice melts '
    'abruptly, leaving cap carbonates over glacial till.'),
   (650, 'Marinoan glaciation', 'A second snowball, shorter but just as '
    'extensive.'),
   (635, 'The last snowball melts', 'The Marinoan ends; ocean oxygen rises and '
    'the Ediacaran begins.'),
 ],
 'firsts': ['Cap carbonates', 'Oxygenated deep ocean'],
 'featured': [
   ('Sponge', 'Sponge-grade animals are the best candidates for what lived '
    'through the snowballs.'),
   ('Cyanobacteria', 'Microbial mats persisted in refuges — meltwater ponds, '
    'volcanic vents, and cracks in the sea ice.'),
 ],
 'scenes': ['Snowball Earth', 'Cryogenian', 'Cap carbonate'],
},
{
 'id': 'ediacaran', 'name': 'Ediacaran', 'sub': 'The first large life',
 'start': 635, 'end': 538.8, 'color': '#FED96A', 'era': 'Neoproterozoic',
 'eon': 'Proterozoic',
 'lede': 'Soft, quilted, frond-like organisms up to a metre across cover the '
         'seafloor — the first big living things, and unlike anything alive now.',
 'story': [
   'The Ediacaran biota appears about 575 million years ago in deep water off '
   'Newfoundland: fronds and spindles anchored to the mud, in water too dark '
   'for photosynthesis, apparently absorbing nutrients straight through their '
   'surfaces. They are built out of repeated quilted units on a fractal plan '
   'that no living group uses.',
   'Later assemblages in the White Sea and Namibia include organisms that are '
   'easier to recognise. *Kimberella* looks like a mollusc and left scratch '
   'marks where it rasped a microbial mat. *Dickinsonia* left a series of '
   'resting traces as it moved and fed, and its fossils retain cholesterol — '
   'so it was an animal. Trace fossils show something burrowing.',
   'At the very end, animals start to build hard parts. *Cloudina* and '
   '*Namacalathus* make small calcareous tubes and cups, and some *Cloudina* '
   'tubes have holes bored in them: the first predators, and the first arms '
   'race. Then the whole assemblage vanishes at the Cambrian boundary.',
 ],
 'world': 'Rodinia’s fragments are drifting toward Gondwana; the Pan-African '
          'collisions are underway. Shallow seas are widespread and, for the '
          'first time, reliably oxygenated.',
 'events': [
   (635, 'The ice ends', 'Cap carbonates blanket the world as the Marinoan '
    'glaciation collapses.'),
   (575, 'The Avalon assemblage', 'Fronds and spindles at Mistaken Point, '
    'Newfoundland — the oldest large complex organisms, preserved under '
    'volcanic ash.'),
   (560, 'The White Sea assemblage', 'Dickinsonia, Kimberella, Spriggina; '
    'movement, feeding traces, and the first grazing.'),
   (550, 'Skeletons and predators', 'Cloudina builds calcareous tubes — and '
    'something starts drilling holes in them.'),
   (539, 'The Ediacarans vanish', 'The assemblage disappears at the Cambrian '
    'boundary, whether by extinction, by being eaten, or by having its '
    'microbial-mat world churned up.'),
 ],
 'firsts': ['Large multicellular organisms', 'Movement', 'Predation',
            'Skeletons', 'Burrows'],
 'featured': [
   ('Dickinsonia', 'A flat, ribbed oval up to 1.4 m across that fed by resting '
    'on microbial mats. Its cholesterol proves it was an animal.'),
   ('Charnia', 'A fern-like frond anchored in deep water, far below the reach '
    'of sunlight — the first complex fossil found in Precambrian rock.'),
   ('Kimberella', 'A slug-like grazer that left paired scratch marks, and the '
    'best candidate for an early mollusc.'),
   ('Spriggina', 'A segmented, head-bearing creature once read as an ancestral '
    'trilobite, now more cautiously left unplaced.'),
   ('Cloudina', 'Stacked calcareous cones a few millimetres wide — among the '
    'first skeletons, and the first to be drilled by predators.'),
   ('Tribrachidium', 'A disc with three raised arms in a spiral — a body plan '
    'with no three-fold living counterpart.'),
   ('Rangea', 'The original "rangeomorph" frond, built from self-similar quilted '
    'branches repeated at four scales.'),
   ('Funisia', 'Dense stands of tubes preserved in cohorts, suggesting sexual '
    'reproduction and larval settlement.'),
 ],
 'scenes': ['Ediacaran biota', 'Dickinsonia', 'Charnia', 'Mistaken Point',
            'Kimberella'],
},
]

CHAPTERS += [
{
 'id': 'cambrian', 'name': 'Cambrian', 'sub': 'The explosion',
 'start': 538.8, 'end': 486.85, 'color': '#7FA056', 'era': 'Paleozoic',
 'eon': 'Phanerozoic',
 'lede': 'In perhaps 20 million years almost every animal body plan still in '
         'use today appears in the fossil record, most of them already armoured, '
         'eyed, and hunting each other.',
 'story': [
   'It starts with burrows. Through the earliest Cambrian, trace fossils get '
   'deeper, more varied and more three-dimensional as animals learn to dig. '
   'Then shells: tiny caps, tubes, spines and plates — the "small shelly '
   'fauna" — and then, around 521 million years ago, the trilobites, which will '
   'be the most conspicuous animals in the sea for the next 250 million years.',
   'What makes the Cambrian legible is a handful of deposits that preserve soft '
   'tissue: Chengjiang in Yunnan, Sirius Passet in Greenland, and the Burgess '
   'Shale in British Columbia. In them the shelly fossils turn out to be a small '
   'minority. There are swimming predators a half-metre long with grasping '
   'appendages, five-eyed animals with a nozzle for a mouth, worms with spines '
   'and armour, and — small and easily missed — the first chordates.',
   'The trigger is argued about endlessly: rising oxygen, the arrival of '
   'predation, the invention of eyes, the genetic toolkit reaching a threshold, '
   'or simply the fact that once anything is worth eating, everything else has '
   'to respond. Probably all of them, feeding back on each other. Ecology '
   'became an arms race and never stopped being one.',
 ],
 'world': 'Gondwana is assembled in the south; Laurentia, Baltica and Siberia '
          'are separate, spread through the tropics. Sea level is high and warm '
          'shallow shelves are everywhere — which is where all of this happens.',
 'events': [
   (538.8, 'The Cambrian begins', 'Defined by the first appearance of the '
    'complex burrow Treptichnus pedum — the boundary is drawn on a trace fossil, '
    'not a body.'),
   (521, 'Trilobites appear', 'Fully formed, with compound eyes, in several '
    'places at once.'),
   (518, 'Chengjiang', 'The Maotianshan Shales of Yunnan preserve a whole soft-'
    'bodied ecosystem, including the earliest fish-like chordates.'),
   (508, 'The Burgess Shale', 'A mudslide buries a reef-edge community in '
    'British Columbia and preserves it in extraordinary detail.'),
   (497, 'End-Cambrian extinctions', 'A series of pulses (the SPICE event and '
    'others) repeatedly cull trilobite faunas.'),
 ],
 'firsts': ['Trilobites', 'Compound eyes', 'Hard skeletons', 'Chordates',
            'Vertebrates', 'Reefs (archaeocyaths)'],
 'featured': [
   ('Anomalocaris', 'A metre-long swimming predator with grasping appendages '
    'and stalked eyes — the largest animal of its age.'),
   ('Opabinia', 'Five eyes and a single flexible nozzle ending in a claw. When '
    'it was first described properly, the audience laughed.'),
   ('Hallucigenia', 'A spined worm reconstructed upside down and back to front '
    'for decades before its head was identified.'),
   ('Wiwaxia', 'An armoured slug-like animal covered in overlapping scales and '
    'long spines, related to molluscs or annelids.'),
   ('Marrella', 'The most abundant Burgess Shale arthropod — small, delicate, '
    'and not a member of any surviving group.'),
   ('Pikaia', 'A flattened, ribbon-like swimmer with a notochord: one of the '
    'first chordates, and so a distant relative of ours.'),
   ('Haikouichthys', 'A 2.5-centimetre animal from Chengjiang with a skull, '
    'eyes and vertebral elements — arguably the first vertebrate.'),
   ('Olenellus', 'A spiny trilobite of the early Cambrian, used to correlate '
    'rocks across Laurentia.'),
   ('Ottoia', 'A priapulid worm that lived in a U-shaped burrow; gut contents '
    'show it ate hyoliths and, sometimes, other Ottoia.'),
   ('Aysheaia', 'A soft, stubby-legged animal that probably grazed on sponges — '
    'close to the ancestry of velvet worms.'),
   ('Archaeocyatha', 'Sponge-like animals that built the first true reefs, then '
    'went extinct before the Cambrian ended.'),
   ('Paradoxides', 'A giant trilobite up to 40 cm long, characteristic of the '
    'Cambrian of Gondwana and Avalonia.'),
 ],
 'scenes': ['Cambrian explosion', 'Burgess Shale', 'Anomalocaris',
            'Maotianshan Shales', 'Trilobite'],
},
{
 'id': 'ordovician', 'name': 'Ordovician', 'sub': 'Life fills the sea, then freezes',
 'start': 486.85, 'end': 443.1, 'color': '#009270', 'era': 'Paleozoic',
 'eon': 'Phanerozoic',
 'lede': 'Marine diversity triples, plants creep onto land, and then a glaciation '
         'kills roughly 85% of species.',
 'story': [
   'The Cambrian invented the body plans; the Ordovician builds the ecosystems. '
   'In the Great Ordovician Biodiversification Event the number of marine '
   'families roughly triples. Reefs are taken over by corals and bryozoans, the '
   'seafloor fills with brachiopods and crinoid meadows, graptolites drift in '
   'the plankton, and enormous straight-shelled nautiloids — some over five '
   'metres — become the top predators.',
   'On land, something quieter happens. Spores with the distinctive walls of '
   'land plants appear in Ordovician rocks: liverwort-grade plants, low and '
   'damp, without roots or vascular tissue. They begin, very slowly, to weather '
   'rock into soil, which draws down CO₂ — one candidate cause for what comes '
   'next.',
   'At the end of the period Gondwana sits over the South Pole, ice sheets '
   'build, sea level falls by 100 metres or more, and the shallow shelves where '
   'nearly everything lived drain away. The Hirnantian extinction arrives in '
   'two pulses: cooling first, then the anoxic water that floods back as the ice '
   'melts. It is the second-worst extinction in Earth history.',
 ],
 'world': 'Gondwana drifts over the South Pole. Laurentia sits on the equator '
          'under a warm shallow sea. The Iapetus Ocean between them begins to '
          'close.',
 'events': [
   (470, 'The GOBE', 'Marine diversity climbs steeply for 25 million years, the '
    'largest sustained rise in the record.'),
   (470, 'Plants reach land', 'Cryptospores — the resistant spores of early land '
    'plants — appear worldwide.'),
   (466, 'The L-chondrite shower', 'An asteroid breakup in the main belt showers '
    'Earth with meteorites; fossil meteorites are common in Swedish limestone '
    'of this age.'),
   (455, 'Nautiloid giants', 'Cameroceras and Endoceras reach several metres — '
    'the largest animals yet to have lived.'),
   (445, 'Hirnantian glaciation and mass extinction', 'Ice on Gondwana, sea '
    'level crashes, and about 85% of species disappear in two pulses.'),
 ],
 'firsts': ['Land plants', 'Coral reefs', 'Jawless fish with bone',
            'Fungi on land', 'A mass extinction'],
 'featured': [
   ('Cameroceras', 'A straight-shelled nautiloid, possibly six metres long, and '
    'the apex predator of Ordovician seas.'),
   ('Sacabambaspis', 'An armoured jawless fish from Bolivia with a bony head '
    'shield and eyes set right at the front.'),
   ('Astraspis', 'One of the first vertebrates with real bone, its head plated '
    'in star-patterned tubercles.'),
   ('Isotelus', 'A trilobite that could exceed 70 cm — among the largest ever '
    'found.'),
   ('Didymograptus', 'A tuning-fork graptolite; colonial hemichordates that '
    'drifted in the plankton and are superb for dating rocks.'),
   ('Orthoceras', 'The archetypal straight cone shell, common enough that '
    'polished slabs of it are sold as ornaments.'),
   ('Promissum', 'A conodont — an eel-like animal known mostly from its tooth '
    'apparatus, here preserved whole.'),
   ('Cystoidea', 'Stalked, plated echinoderms that formed dense gardens on the '
    'Ordovician seafloor.'),
   ('Flexicalymene', 'A trilobite that rolled into a ball when threatened; '
    'enrolled specimens are among the commonest Ordovician fossils.'),
   ('Rafinesquina', 'A broad, thin brachiopod that lay concave-down on the '
    'seafloor in enormous numbers.'),
 ],
 'scenes': ['Ordovician', 'Great Ordovician Biodiversification Event',
            'Late Ordovician mass extinction', 'Cameroceras', 'Graptolite'],
},
{
 'id': 'silurian', 'name': 'Silurian', 'sub': 'Life gets a backbone on land',
 'start': 443.1, 'end': 419.62, 'color': '#B3E1B6', 'era': 'Paleozoic',
 'eon': 'Phanerozoic',
 'lede': 'The ice melts, reefs rebuild, and the first plants with plumbing stand '
         'upright — with millipedes and scorpions right behind them.',
 'story': [
   'Recovery is fast. Sea level rises again, and reefs — now built by tabulate '
   'and rugose corals and by stromatoporoid sponges — spread across the tropics. '
   'The Silurian is short, but it is when the sea gets crowded in a modern way: '
   'jawed fish appear and start to matter.',
   'The decisive change is on land. *Cooksonia* is a few centimetres of forking '
   'green stem with a spore capsule on each tip and, critically, vascular '
   'tissue — cells stiffened with lignin that carry water upward. That is the '
   'invention that lets a plant stand up against gravity, and everything from '
   'ferns to redwoods follows from it.',
   'Animals follow the plants. *Pneumodesmus newmani*, a millipede from '
   'Aberdeenshire, has spiracles — holes for breathing air — making it one of '
   'the oldest known air-breathing animals. In the water, eurypterids ("sea '
   'scorpions") become formidable: *Pterygotus* reached over 1.5 metres.',
 ],
 'world': 'Laurentia and Baltica collide to form Laurussia, throwing up the '
          'Caledonian mountains; Gondwana remains in the south. Sea level is '
          'high again and the tropics are lined with reefs.',
 'events': [
   (443, 'Recovery', 'Diversity rebuilds quickly after the Hirnantian, though '
    'with a changed cast.'),
   (433, 'Vascular plants', 'Cooksonia — forking stems with sporangia and '
    'lignified conducting tissue — establishes the vascular plant lineage.'),
   (428, 'Air breathers on land', 'Pneumodesmus, a millipede with spiracles, '
    'from Scotland.'),
   (425, 'Jawed fish diversify', 'Acanthodians and early bony fish spread; '
    'Guiyu oneiros from China is a complete early bony fish.'),
   (420, 'Sea scorpions peak', 'Eurypterids reach their greatest size and '
    'diversity.'),
 ],
 'firsts': ['Vascular plants', 'Air-breathing land animals', 'Bony fish',
            'Coral-stromatoporoid reefs'],
 'featured': [
   ('Cooksonia', 'A few centimetres of forking stem tipped with spore capsules '
    '— the first vascular plant, and the ancestor of every tree.'),
   ('Pterygotus', 'A eurypterid over 1.5 m long with paddle limbs and grasping '
    'claws — one of the largest arthropods that ever lived.'),
   ('Eurypterus', 'The best-known sea scorpion, abundant in the lagoons of what '
    'is now New York State.'),
   ('Guiyu oneiros', 'A complete early bony fish from China that mixes lobe-finned and '
    'ray-finned features.'),
   ('Birkenia', 'A small jawless anaspid fish, streamlined and scaled, from '
    'Scottish rocks.'),
   ('Climatius', 'A spiny "acanthodian" with up to six pairs of fin spines '
    'along its belly.'),
   ('Pneumodesmus', 'A millipede with breathing holes — among the first animals '
    'known to have breathed air.'),
   ('Baragwanathia', 'A clubmoss with real leaves and thick stems, surprisingly '
    'advanced for its age.'),
   ('Halysites', 'The "chain coral", whose colonies form linked rings in '
    'Silurian reef limestone.'),
   ('Dalmanites', 'A large-eyed trilobite with a long tail spine, common in '
    'Silurian shelf seas.'),
 ],
 'scenes': ['Silurian', 'Cooksonia', 'Eurypterid', 'Evolutionary history of plants'],
},
{
 'id': 'devonian', 'name': 'Devonian', 'sub': 'The age of fishes — and the first forests',
 'start': 419.62, 'end': 358.86, 'color': '#CB8C37', 'era': 'Paleozoic',
 'eon': 'Phanerozoic',
 'lede': 'Armoured fish the size of cars patrol the seas, trees invent wood and '
         'roots, and something with fins and a neck crawls out of the water.',
 'story': [
   'Fish take over. Placoderms — armoured, jawed, and often enormous — dominate, '
   'with *Dunkleosteus* reaching perhaps six metres and biting with shearing '
   'bony plates instead of teeth. Sharks appear in numbers, lobe-finned fish '
   'diversify, and the ray-finned fish that make up most of today’s species get '
   'started.',
   'On land, plants solve the two remaining problems: roots and wood. '
   '*Archaeopteris* has a proper trunk with growth rings and a root system '
   'metres deep, and forms the first forests. Roots crack rock into soil, and '
   'the runoff of that new nutrient supply feeds algal blooms in the sea, '
   'stripping the water of oxygen — a plausible mechanism for the extinctions '
   'that punctuate the period.',
   'And then the fin becomes a limb. *Eusthenopteron*, *Panderichthys*, '
   '*Tiktaalik*, *Acanthostega*, *Ichthyostega* — a sequence of fossils, mostly '
   'found since 1930, that shows the shoulder freeing itself from the skull, a '
   'neck appearing, and fins acquiring digits. The earliest tetrapods still had '
   'gills and probably still lived in water; the limbs came first, and the land '
   'came after.',
 ],
 'world': 'Laurussia — the "Old Red Sandstone continent" — straddles the '
          'equator, its interior a vast arid floodplain. Gondwana is closing in '
          'from the south; the sea between them is warm and reef-rich.',
 'events': [
   (410, 'The Rhynie chert', 'A hot spring in Scotland silicifies an entire '
    'early land ecosystem — plants, mites, springtails, and the oldest insect '
    'fragments.'),
   (390, 'The first forests', 'Archaeopteris grows real wood and deep roots; '
    'Gilboa in New York preserves stumps of the earliest trees.'),
   (385, 'Placoderms peak', 'Dunkleosteus and its relatives dominate marine '
    'food webs.'),
   (372, 'Kellwasser event', 'The Late Devonian extinction begins; reefs '
    'collapse and do not fully recover for over 100 million years.'),
   (365, 'Tetrapods', 'Acanthostega and Ichthyostega have limbs with digits — '
    'eight on each in Acanthostega’s case — but still breathe with gills.'),
   (359, 'Hangenberg event', 'A second crisis at the end of the period wipes out '
    'the placoderms entirely and resets vertebrate evolution.'),
 ],
 'firsts': ['Forests', 'Wood', 'Roots', 'Seeds', 'Insects', 'Tetrapods',
            'Ammonoids'],
 'featured': [
   ('Dunkleosteus', 'A placoderm up to six metres long, its head and thorax '
    'sheathed in bone, biting with self-sharpening plates.'),
   ('Tiktaalik', 'A flat-headed fish with a neck, ribs and a wrist — the '
    'textbook intermediate between fish and tetrapod.'),
   ('Acanthostega', 'An early tetrapod with eight digits per limb and internal '
    'gills: limbs evolved in the water, not on land.'),
   ('Ichthyostega', 'A sturdier early tetrapod with a rib cage strong enough to '
    'support its body out of water.'),
   ('Eusthenopteron', 'A lobe-finned fish whose fin bones line up with the '
    'humerus, radius and ulna of a limb.'),
   ('Archaeopteris', 'The first modern-looking tree: a real trunk with growth '
    'rings, deep roots, and fern-like foliage.'),
   ('Bothriolepis', 'A small armoured placoderm found on nearly every continent '
    '— one of the most abundant Devonian fossils.'),
   ('Cladoselache', 'An early shark with a streamlined body and short jaws, '
    'preserved with its last meal intact.'),
   ('Rhyniognatha', 'Jaw fragments from the Rhynie chert, argued to be the '
    'oldest known insect.'),
   ('Materpiscis', 'A placoderm preserved with an embryo and umbilical cord — '
    'the oldest known live birth in a vertebrate.'),
   ('Titanichthys', 'A placoderm as big as Dunkleosteus but toothless: a filter '
    'feeder.'),
   ('Elkinsia', 'One of the earliest seed plants, freeing reproduction from '
    'standing water.'),
   ('Prototaxites', 'A twenty-foot spire, probably a giant fungus, and the '
    'tallest organism on land for millions of years.'),
 ],
 'scenes': ['Devonian', 'Dunkleosteus', 'Tiktaalik', 'Rhynie chert',
            'Late Devonian extinction', 'Archaeopteris'],
},
{
 'id': 'carboniferous', 'name': 'Carboniferous', 'sub': 'Coal, oxygen and giant insects',
 'start': 358.86, 'end': 298.9, 'color': '#67A599', 'era': 'Paleozoic',
 'eon': 'Phanerozoic',
 'lede': 'Swamp forests bury so much carbon that oxygen reaches 35% of the air — '
         'and dragonflies grow to the size of hawks.',
 'story': [
   'Wet equatorial lowlands fill with forests of lycopsids — *Lepidodendron* '
   'and *Sigillaria*, 30 metres tall, with trunks armoured in diamond-patterned '
   'leaf scars — along with horsetails the size of trees and the first conifers '
   'on drier ground. When they fall into waterlogged swamp, they do not fully '
   'rot. Buried, compressed, and cooked, they become the coal that would later '
   'be dug up to run the Industrial Revolution.',
   'Burying that much carbon without burning it pushes atmospheric oxygen to '
   'around 35%, the highest in Earth history, while CO₂ falls to near modern '
   'levels and the planet cools into the long Karoo ice age. High oxygen makes '
   'diffusion-limited breathing work at larger sizes, and arthropods take '
   'advantage: *Meganeura* had a 70-centimetre wingspan and *Arthropleura* was '
   'a two-and-a-half-metre millipede.',
   'Vertebrates settle in. Amphibians of every shape fill the swamps, and '
   'somewhere in the middle of the period one lineage evolves the amniotic egg '
   '— a private pond with a shell — which finally severs reproduction from open '
   'water. *Hylonomus*, a lizard-shaped animal found inside fossil tree stumps '
   'in Nova Scotia, is among the first reptiles.',
 ],
 'world': 'Gondwana and Laurussia converge and collide, raising the '
          'Appalachians, the Variscan belt and the Urals, and assembling '
          'Pangea. Ice covers much of the southern continent.',
 'events': [
   (359, 'Romer’s gap', 'A thin stretch of tetrapod record after the Hangenberg '
    'extinction, now slowly being filled in.'),
   (330, 'Coal swamps', 'Vast wetland forests spread across the tropics; the '
    'Karoo glaciation grips the south.'),
   (318, 'The amniotic egg', 'Hylonomus and its relatives reproduce without '
    'water — the reptile line begins.'),
   (307, 'Oxygen peaks', 'Atmospheric O₂ reaches roughly 35%, and arthropods '
    'reach sizes never repeated.'),
   (305, 'Rainforest collapse', 'The coal forests fragment abruptly during an '
    'arid pulse, isolating populations and favouring reptiles over amphibians.'),
 ],
 'firsts': ['Amniotic egg', 'Reptiles', 'Winged insects in numbers',
            'Conifers', 'Coal'],
 'featured': [
   ('Meganeura', 'A griffinfly with a 70-centimetre wingspan, hunting other '
    'insects over the swamps.'),
   ('Arthropleura', 'A millipede relative up to 2.5 metres long — the largest '
    'land invertebrate that has ever lived.'),
   ('Lepidodendron', 'A 30-metre scale tree with a photosynthetic trunk that '
    'grew fast, reproduced once, and died.'),
   ('Sigillaria', 'A lycopsid with a tall unbranched trunk and a crown of long '
    'grassy leaves.'),
   ('Calamites', 'A horsetail the size of a tree, growing in dense stands along '
    'river channels.'),
   ('Hylonomus', 'A 20-centimetre reptile found inside hollow lycopsid stumps — '
    'one of the earliest known amniotes.'),
   ('Pulmonoscorpius', 'A scorpion 70 centimetres long from the Scottish '
    'Carboniferous.'),
   ('Crassigyrinus', 'A long-bodied aquatic tetrapod with huge jaws and almost '
    'useless forelimbs.'),
   ('Eryops', 'A metre-and-a-half amphibian built like a crocodile, hunting in '
    'and around water.'),
   ('Tullimonstrum', 'The Tully Monster of Illinois — stalked eyes, a long '
    'proboscis with teeth, and still no agreed place on the tree of life.'),
   ('Helicoprion', 'A shark relative whose lower jaw carried a spiral buzz-saw '
    'of teeth.'),
   ('Westlothiana', 'A small, slender animal from Scotland close to the origin '
    'of the amniotes.'),
   ('Stethacanthus', 'A shark with an anvil-shaped dorsal structure covered in '
    'tooth-like denticles.'),
 ],
 'scenes': ['Carboniferous', 'Meganeura', 'Arthropleura', 'Lepidodendron',
            'Carboniferous rainforest collapse'],
},
{
 'id': 'permian', 'name': 'Permian', 'sub': 'Pangea, and the great dying',
 'start': 298.9, 'end': 251.902, 'color': '#F04028', 'era': 'Paleozoic',
 'eon': 'Phanerozoic',
 'lede': 'One supercontinent, one desert interior, a world of mammal ancestors — '
         'and then the worst extinction in the history of life.',
 'story': [
   'Pangea is complete: a single landmass from pole to pole, with an interior '
   'so far from any ocean that it becomes one of the driest places the planet '
   'has ever had. The Karoo ice age fades and the world warms. Coal swamps give '
   'way to conifers, seed ferns and the *Glossopteris* flora that carpets '
   'Gondwana — the same fossil leaf found in India, Africa, Australia, South '
   'America and Antarctica, which is how Wegener knew the continents had moved.',
   'The land belongs to synapsids — the lineage that leads to mammals. Early on '
   'they are sail-backed pelycosaurs like *Dimetrodon*; later come the '
   'therapsids, which stand with legs under the body, have differentiated '
   'teeth, and may well have been furry and warm-blooded. Alongside them are '
   'the armoured pareiasaurs and the first true reptile radiations.',
   'Then, 252 million years ago, the Siberian Traps erupt through coal beds and '
   'evaporites, injecting carbon dioxide, methane and halogens into the '
   'atmosphere over perhaps a million years. Temperatures rise about 10°C, the '
   'oceans acidify, lose oxygen and fill with hydrogen sulphide. Something like '
   '81% of marine species and 70% of land vertebrates disappear. The trilobites '
   'end here. So do the eurypterids. It takes 10 million years for ecosystems '
   'to rebuild.',
 ],
 'world': 'Pangea, surrounded by the single Panthalassic Ocean, with the '
          'Tethys Sea biting into its eastern side. The interior is desert; the '
          'coasts are seasonal and monsoonal.',
 'events': [
   (299, 'Pangea complete', 'The last collisions weld the supercontinent '
    'together; the Karoo glaciation begins its long retreat.'),
   (273, 'Therapsids take over', 'Mammal-line synapsids with upright limbs and '
    'specialised teeth become the dominant land vertebrates.'),
   (260, 'Capitanian extinction', 'An earlier, smaller crisis, linked to the '
    'Emeishan Traps in China, removes many marine groups.'),
   (252, 'Siberian Traps', 'Millions of cubic kilometres of lava erupt through '
    'coal and salt deposits, releasing carbon and halogens.'),
   (251.9, 'The Great Dying', 'The end-Permian extinction: roughly 81% of '
    'marine species gone. Trilobites, eurypterids and blastoids end for good.'),
 ],
 'firsts': ['Gliding reptiles', 'Beetles', 'Modern-style conifers'],
 'featured': [
   ('Dimetrodon', 'A sail-backed predator, and a synapsid — closer to us than '
    'to any dinosaur, despite being everyone’s idea of one.'),
   ('Inostrancevia', 'A gorgonopsian with sabre-like canines, over three metres '
    'long, from the Russian Permian.'),
   ('Scutosaurus', 'A heavily armoured, barrel-bodied pareiasaur that ate '
    'low-growing plants.'),
   ('Lystrosaurus', 'A tusked, pig-sized dicynodont that survived the '
    'extinction and briefly made up most land vertebrates on Earth.'),
   ('Edaphosaurus', 'A sail-backed herbivore with a broad body and crossbars on '
    'its sail spines.'),
   ('Diictodon', 'A burrowing dicynodont known from thousands of specimens, '
    'sometimes found in pairs in spiral burrows.'),
   ('Estemmenosuchus', 'A bulky herbivore with antler-like bony outgrowths on '
    'its skull.'),
   ('Gorgonops', 'The archetypal sabre-toothed therapsid predator of the late '
    'Permian.'),
   ('Mesosaurus', 'A small freshwater reptile found only in Brazil and southern '
    'Africa — early evidence that the two were once joined.'),
   ('Glossopteris', 'The tongue-shaped leaf that carpeted Gondwana and helped '
    'prove continental drift.'),
   ('Coelurosauravus', 'A reptile that glided on membranes stretched over rods '
    'grown from its skin, not from its ribs.'),
 ],
 'scenes': ['Permian', 'Permian–Triassic extinction event', 'Dimetrodon',
            'Siberian Traps', 'Pangaea', 'Glossopteris'],
},
]

CHAPTERS += [
{
 'id': 'triassic', 'name': 'Triassic', 'sub': 'Rebuilding, and the first dinosaurs',
 'start': 251.902, 'end': 201.4, 'color': '#812B92', 'era': 'Mesozoic',
 'eon': 'Phanerozoic',
 'lede': 'A hot, empty world refills — with dinosaurs, mammals, pterosaurs and '
         'the first reptiles to go back to the sea.',
 'story': [
   'The early Triassic is a strange, impoverished place. Coal is absent from '
   'the record for millions of years — the "coal gap" — reefs are gone, and on '
   'land the dicynodont *Lystrosaurus* is so abundant it accounts for most '
   'vertebrate fossils found. Equatorial regions may have been too hot for '
   'large animals for stretches of time.',
   'Recovery, when it comes, is inventive. Archosaurs split into two great '
   'branches: one leading to crocodiles, which for most of the Triassic are the '
   'more successful group, producing armoured herbivores and land predators; '
   'the other to pterosaurs and dinosaurs. The first dinosaurs, around 230 '
   'million years ago, are small, bipedal and unremarkable — a minor part of '
   'the fauna for 30 million years.',
   'Two other things start here. Pterosaurs become the first vertebrates to fly '
   'under their own power. And small, shrew-like animals with a new jaw joint, '
   'a differentiated dentition and probably fur — the first mammals — appear '
   'near the end of the period, and spend the next 135 million years being '
   'small.',
 ],
 'world': 'Pangea is still whole but starting to strain. The Tethys Ocean opens '
          'westward into the supercontinent; the interior stays arid and '
          'strongly monsoonal.',
 'events': [
   (251.9, 'The empty world', 'Life after the Great Dying: low diversity, '
    'disaster taxa, no coal, no reefs.'),
   (247, 'Marine reptiles', 'Ichthyosaurs and sauropterygians return to the sea '
    'and diversify rapidly; Shonisaurus will reach 20 metres.'),
   (237, 'Modern corals', 'Scleractinian corals — the reef builders of today — '
    'appear and begin rebuilding reefs.'),
   (230, 'The first dinosaurs', 'Eoraptor and Herrerasaurus in Argentina: small, '
    'fast bipeds in a world still run by crocodile-line archosaurs.'),
   (225, 'The first mammals', 'Morganucodon and its relatives — small, '
    'nocturnal, insectivorous, with a new jaw joint and precise occlusion.'),
   (201.4, 'End-Triassic extinction', 'The Central Atlantic Magmatic Province '
    'erupts as Pangea starts to rift; about half of species disappear and the '
    'crocodile-line archosaurs are cut down, leaving the field to dinosaurs.'),
 ],
 'firsts': ['Dinosaurs', 'Mammals', 'Pterosaurs', 'Modern corals',
            'Turtles', 'Frogs'],
 'featured': [
   ('Eoraptor', 'A metre-long biped from Argentina, near the very base of the '
    'dinosaur family tree.'),
   ('Herrerasaurus', 'An early predatory dinosaur with a sliding lower jaw '
    'joint for gripping prey.'),
   ('Coelophysis', 'A slender, fast theropod known from a bone bed at Ghost '
    'Ranch containing hundreds of individuals.'),
   ('Plateosaurus', 'A five-metre long-necked plant-eater, and one of the first '
    'really large dinosaurs.'),
   ('Morganucodon', 'A shrew-sized animal with mammalian teeth and jaw joint — '
    'about as close to the first mammal as the record gets.'),
   ('Eudimorphodon', 'An early pterosaur with a wingspan under a metre and '
    'multi-cusped teeth for catching fish.'),
   ('Shonisaurus', 'An ichthyosaur up to 20 metres long, known from a Nevada '
    'site where dozens died together.'),
   ('Tanystropheus', 'A marine reptile whose neck was longer than the rest of '
    'its body combined.'),
   ('Postosuchus', 'A crocodile-line predator that walked on upright limbs and '
    'topped the food chain before dinosaurs did.'),
   ('Desmatosuchus', 'An armoured aetosaur with huge shoulder spikes, built '
    'like a tank and eating plants.'),
   ('Placodus', 'A marine reptile with protruding front teeth and flat crushing '
    'palate teeth for shellfish.'),
   ('Nothosaurus', 'A long-bodied, seal-like fish hunter of the Tethys coasts.'),
   ('Lystrosaurus', 'The survivor: for a while after the extinction, most land '
    'vertebrate fossils in the world belong to this one genus.'),
   ('Sharovipteryx', 'A gliding reptile whose main membranes stretched between '
    'its hind legs.'),
 ],
 'scenes': ['Triassic', 'Triassic–Jurassic extinction event', 'Coelophysis',
            'Ichthyosauria', 'Pterosaur'],
},
{
 'id': 'jurassic', 'name': 'Jurassic', 'sub': 'Giants, and the first birds',
 'start': 201.4, 'end': 143.1, 'color': '#34B2C9', 'era': 'Mesozoic',
 'eon': 'Phanerozoic',
 'lede': 'Pangea splits, the climate turns warm and wet, sauropods become the '
         'largest animals ever to walk, and a feathered dinosaur takes off.',
 'story': [
   'Pangea comes apart. The Atlantic begins to open, Gondwana separates from '
   'Laurasia, and the flooded gaps between them become shallow seas full of '
   'ammonites, belemnites and marine reptiles. All that new coastline makes the '
   'world wetter, and the arid supercontinental interior gives way to forests '
   'of conifers, cycads, ginkgos and tree ferns.',
   'With the crocodile-line archosaurs cut back by the end-Triassic extinction, '
   'dinosaurs expand into everything. Sauropods evolve into the largest land '
   'animals that have ever existed: a column-legged body plan with a long neck '
   'to reach food without moving, air-filled bones to keep the weight down, and '
   'a tiny head that never has to chew. *Brachiosaurus*, *Diplodocus* and '
   '*Apatosaurus* all come from the Morrison Formation of the American West.',
   'And in a German lagoon, 150 million years ago, a small feathered dinosaur '
   'falls into the water and is buried in fine lime mud. *Archaeopteryx* has '
   'wings, flight feathers and a wishbone — and also teeth, claws on its hands, '
   'and a long bony tail. Found two years after *On the Origin of Species*, it '
   'remains the most famous transitional fossil ever collected.',
 ],
 'world': 'The supercontinent divides. The Central Atlantic opens; the Tethys '
          'runs the width of the globe. High sea level floods Europe into an '
          'archipelago of islands and lagoons.',
 'events': [
   (201, 'Dinosaurs inherit the land', 'With their rivals gone, dinosaur '
    'diversity and size climb steeply.'),
   (183, 'Toarcian ocean anoxia', 'A warming pulse strips oxygen from the '
    'oceans and lays down black shales across Europe.'),
   (170, 'The Atlantic opens', 'Seafloor spreading begins in earnest between '
    'the Americas and Africa.'),
   (155, 'The Morrison Formation', 'A seasonal floodplain in the American West '
    'preserves the classic sauropod-and-Allosaurus fauna.'),
   (150, 'Archaeopteryx', 'A feathered, winged dinosaur in the Solnhofen '
    'limestone — the link between dinosaurs and birds.'),
 ],
 'firsts': ['Birds', 'Salamanders', 'Lizards', 'Placental mammal ancestors'],
 'featured': [
   ('Archaeopteryx', 'Feathers, wings and a wishbone, plus teeth, clawed hands '
    'and a bony tail — the classic transitional fossil.'),
   ('Brachiosaurus', 'A sauropod with front legs longer than its back legs, '
    'holding its head 12 metres up.'),
   ('Diplodocus', 'Twenty-five metres of mostly neck and tail, weighing far '
    'less than its length suggests.'),
   ('Apatosaurus', 'A heavily built sauropod whose tail may have been able to '
    'crack like a whip.'),
   ('Stegosaurus', 'Two rows of plates along the back and four tail spikes — '
    'the plates probably for display and heat exchange.'),
   ('Allosaurus', 'The dominant Morrison predator, nine metres long with '
    'blade-like teeth and ridges over its eyes.'),
   ('Compsognathus', 'A chicken-sized theropod, once thought the smallest '
    'dinosaur, found with a lizard in its stomach.'),
   ('Ichthyosaurus', 'A dolphin-shaped marine reptile with enormous eyes, '
    'giving birth to live young at sea.'),
   ('Plesiosaurus', 'Four flippers and a long neck; the group that '
    'inadvertently gave the Loch Ness monster its shape.'),
   ('Liopleurodon', 'A short-necked pliosaur with a skull well over a metre '
    'long, hunting other marine reptiles.'),
   ('Pterodactylus', 'A small, long-jawed pterosaur, the first to be described '
    'and the source of the word "pterodactyl".'),
   ('Rhamphorhynchus', 'A long-tailed pterosaur with a diamond-shaped vane on '
    'its tail tip.'),
   ('Anchiornis', 'A four-winged feathered dinosaur whose fossilised melanosomes '
    'reveal a grey body, black wings and a red crest.'),
   ('Yi qi', 'A pigeon-sized dinosaur that glided on bat-like membranes '
    'stretched from a long wrist bone.'),
   ('Castorocauda', 'A swimming, beaver-tailed early mammal relative with '
    'preserved fur.'),
   ('Ammonite', 'Coiled cephalopods so abundant and so fast-changing that they '
    'are used to date Jurassic rocks to within a few hundred thousand years.'),
 ],
 'scenes': ['Jurassic', 'Archaeopteryx', 'Morrison Formation', 'Sauropoda',
            'Solnhofen Limestone'],
},
{
 'id': 'cretaceous', 'name': 'Cretaceous', 'sub': 'Flowers, feathers, and an asteroid',
 'start': 143.1, 'end': 66, 'color': '#7FC64E', 'era': 'Mesozoic',
 'eon': 'Phanerozoic',
 'lede': 'The world turns green with flowers and loud with insects, dinosaurs '
         'reach their peak — and then, in an afternoon, it ends.',
 'story': [
   'Flowering plants appear in the early Cretaceous and spread with remarkable '
   'speed, out-competing conifers and cycads across much of the world. They '
   'bring with them a co-evolutionary explosion: bees, butterflies, ants and '
   'the flowers that feed them diversify together, and the modern terrestrial '
   'ecosystem — flowers, pollinators, fruit, seed dispersers — takes shape.',
   'It is a hothouse. There is no permanent polar ice; forests grow inside the '
   'Arctic Circle, and the mid-Cretaceous is one of the warmest intervals of '
   'the last 500 million years. Sea level is up to 250 metres higher than '
   'today, splitting North America down the middle with the Western Interior '
   'Seaway and drowning much of Europe.',
   'Dinosaurs reach their greatest variety: tyrannosaurs, the horned and '
   'duck-billed herbivores, the enormous titanosaurs of the southern '
   'continents, and feathered dromaeosaurs. Birds and mammals are both '
   'diversifying quietly alongside them. Then a 10-kilometre asteroid strikes '
   'the Yucatán at about 20 km/s. The impact throws enough dust and sulphate '
   'into the stratosphere to shut down photosynthesis for months to years. '
   'Three-quarters of species die, including every dinosaur that was not a bird.',
 ],
 'world': 'The Atlantic widens; India breaks free and races north; Africa and '
          'South America separate for good. Shallow seas cover a third of the '
          'continents.',
 'events': [
   (130, 'Flowers', 'Angiosperms appear and begin their rapid spread; the '
    'Jehol biota of China preserves the earliest known flowering plants '
    'alongside feathered dinosaurs.'),
   (125, 'The Jehol biota', 'Volcanic ash in Liaoning preserves feathers, '
    'stomach contents and colour-bearing melanosomes in extraordinary detail.'),
   (94, 'Cenomanian–Turonian hothouse', 'Peak Cretaceous warmth and a global '
    'ocean anoxic event.'),
   (68, 'Tyrannosaurus', 'The last and largest tyrannosaur, in a North America '
    'split by an inland sea.'),
   (66.05, 'Deccan Traps', 'Enormous eruptions in India begin stressing the '
    'climate before the impact.'),
   (66, 'Chicxulub', 'A 10-kilometre asteroid hits the Yucatán. Wildfires, '
    'tsunamis, and years of darkness. 75% of species are gone.'),
 ],
 'firsts': ['Flowering plants', 'Bees', 'Ants', 'Snakes', 'Modern birds',
            'Placental and marsupial mammals'],
 'featured': [
   ('Tyrannosaurus', 'Twelve metres, banana-sized teeth, and a bite that could '
    'crush bone — the most-studied dinosaur there is.'),
   ('Triceratops', 'Three horns and a solid frill; one of the last dinosaurs to '
    'exist before the impact.'),
   ('Velociraptor', 'Turkey-sized, feathered, with one sickle claw per foot — '
    'famously nothing like the films.'),
   ('Spinosaurus', 'A fish-eating theropod longer than T. rex, with a huge sail '
    'and a paddle-like tail.'),
   ('Argentinosaurus', 'A titanosaur estimated at 30-plus metres and 60-plus '
    'tonnes — among the largest land animals known.'),
   ('Ankylosaurus', 'Armoured from snout to tail and swinging a bony club.'),
   ('Parasaurolophus', 'A hadrosaur whose metre-long head crest was a resonating '
    'tube it could call through.'),
   ('Quetzalcoatlus', 'A pterosaur the height of a giraffe with a ten-metre '
    'wingspan, likely stalking prey on foot.'),
   ('Mosasaurus', 'A marine lizard up to 15 metres, with a second set of teeth '
    'on the palate.'),
   ('Pteranodon', 'A crested, toothless pterosaur that soared over the Western '
    'Interior Seaway.'),
   ('Microraptor', 'A four-winged dromaeosaur with iridescent black plumage '
    'that glided between trees.'),
   ('Confuciusornis', 'An early bird with a true beak, known from thousands of '
    'specimens, many with long tail streamers.'),
   ('Repenomamus', 'A badger-sized mammal found with a young dinosaur in its '
    'stomach — mammals were not only prey.'),
   ('Deinonychus', 'The dinosaur whose 1969 description restarted the argument '
    'that dinosaurs were active and warm-blooded.'),
   ('Archaefructus', 'One of the earliest known flowering plants, an aquatic '
    'herb from the Jehol lake beds.'),
   ('Sarcosuchus', 'A twelve-metre crocodile relative with a bulbous snout tip, '
    'hunting in African rivers.'),
   ('Therizinosaurus', 'A theropod with metre-long hand claws that it used on '
    'plants, not prey.'),
   ('Xiphactinus', 'A five-metre bony fish, frequently found with an entire '
    'other fish inside it.'),
 ],
 'scenes': ['Cretaceous', 'Cretaceous–Paleogene extinction event',
            'Chicxulub crater', 'Tyrannosaurus', 'Jehol Biota',
            'Western Interior Seaway'],
},
]

CHAPTERS += [
{
 'id': 'paleocene', 'name': 'Paleocene', 'sub': 'The world after',
 'start': 66, 'end': 56, 'color': '#FDA75F', 'era': 'Cenozoic',
 'eon': 'Phanerozoic',
 'lede': 'Ferns, then forests. Mammals inherit an empty planet and, within ten '
         'million years, are producing animals the size of cows — and snakes '
         'that eat crocodiles.',
 'story': [
   'The first thing that grows back is ferns. Sediments just above the impact '
   'layer are dominated by fern spores — the classic signature of a landscape '
   'stripped and recolonised. Within a few tens of thousands of years, forests '
   'return, and they return to a world with no large land animals in it at all.',
   'Mammals had been around for 135 million years without exceeding badger '
   'size. Now, released from that ceiling, they radiate fast. Within four '
   'million years there are hoofed herbivores the size of cattle, and the '
   'first primate-like animals are in the trees. Birds also take their chance: '
   'flightless giants like *Gastornis* stand two metres tall.',
   'It is hot, and getting hotter. At the very end of the epoch, roughly 56 '
   'million years ago, an enormous pulse of carbon enters the ocean-atmosphere '
   'system and global temperatures jump 5–8°C in a few thousand years. The '
   'Paleocene–Eocene Thermal Maximum is the closest analogue the geological '
   'record offers to what humans are doing now — and even it released carbon '
   'roughly ten times more slowly.',
 ],
 'world': 'The Atlantic keeps widening. North America and Europe are still '
          'connected across the north, which lets mammals move between them. '
          'India is closing on Asia. There is no polar ice.',
 'events': [
   (66, 'The fern spike', 'Ferns dominate the recovering landscape immediately '
    'above the impact layer.'),
   (64, 'Mammals radiate', 'Placental mammal orders diversify rapidly into the '
    'vacated large-herbivore and predator niches.'),
   (60, 'Giant birds', 'Gastornis and its relatives stand two metres tall in '
    'the northern forests.'),
   (58, 'Titanoboa', 'A 13-metre snake in a Colombian rainforest so hot it '
    'implies year-round temperatures around 30–34°C.'),
   (56, 'The PETM', 'A carbon release warms the planet 5–8°C in a few thousand '
    'years, acidifies the ocean, and drives a deep-sea extinction.'),
 ],
 'firsts': ['Large mammals', 'Primates', 'Rodents', 'Modern bird orders'],
 'featured': [
   ('Titanoboa', 'A 13-metre, one-tonne snake — the largest ever found — eating '
    'crocodile relatives in a Paleocene rainforest.'),
   ('Gastornis', 'A two-metre flightless bird with an enormous beak, now '
    'thought to have been a plant-eater.'),
   ('Purgatorius', 'A small, insect-and-fruit-eating animal near the base of '
    'the primate family tree.'),
   ('Plesiadapis', 'A squirrel-like early primate relative with rodent-like '
    'front teeth.'),
   ('Coryphodon', 'A hippo-shaped semi-aquatic herbivore, one of the first '
    'really large mammals.'),
   ('Carbonemys', 'A freshwater turtle with a shell nearly two metres across, '
    'from the same deposits as Titanoboa.'),
   ('Barylambda', 'A heavy, slow herbivore with a thick tail that may have '
    'propped it up to reach branches.'),
   ('Champsosaurus', 'A gharial-shaped reptile that survived the extinction and '
    'kept fishing in northern rivers.'),
 ],
 'scenes': ['Paleocene', 'Paleocene–Eocene Thermal Maximum', 'Titanoboa',
            'Gastornis'],
},
{
 'id': 'eocene', 'name': 'Eocene', 'sub': 'The hothouse, and the whales',
 'start': 56, 'end': 33.9, 'color': '#FDB46C', 'era': 'Cenozoic',
 'eon': 'Phanerozoic',
 'lede': 'Palms grow in Alaska and crocodiles bask above the Arctic Circle. '
         'Then, over twenty million years, the planet cools into the ice ages '
         'we still live in.',
 'story': [
   'The early Eocene is the warmest sustained climate of the last 65 million '
   'years. There is no ice at either pole. Rainforest reaches into Canada and '
   'Europe, Antarctica is forested, and the Arctic Ocean is a warm, brackish '
   'lake covered in freshwater fern. Modern mammal orders — bats, horses, '
   'whales, primates — all appear in this interval, most of them in the first '
   'few million years.',
   'The best evidence is in two lake deposits. Messel Pit in Germany preserves '
   'mammals with fur, stomach contents and gut bacteria; Green River in Wyoming '
   'preserves fish, birds, insects and leaves in laminated shale. Between them '
   'they show a world of small horses no bigger than dogs, early bats already '
   'echolocating, and primates with grasping hands.',
   'And whales go to sea. *Pakicetus* is a wolf-sized land animal with a whale’s '
   'inner ear; *Ambulocetus* swims like an otter; *Rodhocetus* has a tail fluke; '
   'and by the late Eocene *Basilosaurus* is an 18-metre fully aquatic '
   'predator with tiny, useless hind legs. Meanwhile the planet cools: India '
   'collides with Asia, the Himalayas rise, weathering pulls CO₂ down, and at '
   '34 million years ago ice sheets appear on Antarctica for the first time in '
   'over 100 million years.',
 ],
 'world': 'India slams into Asia and the Himalayas begin to rise. Australia '
          'and South America separate from Antarctica, opening the Southern '
          'Ocean and letting a current circle the pole.',
 'events': [
   (56, 'Peak warmth', 'The Early Eocene Climatic Optimum: no polar ice, '
    'forests at both poles.'),
   (49, 'The Azolla event', 'A freshwater fern blooms across a stagnant Arctic '
    'Ocean and, by sinking, may have drawn down enough CO₂ to help start the '
    'long cooling.'),
   (47, 'Messel and Green River', 'Two lake deposits preserve Eocene life in '
    'extraordinary completeness.'),
   (40, 'Whales go fully aquatic', 'Basilosaurus and Dorudon have flippers, '
    'flukes, and vestigial hind limbs.'),
   (34, 'Antarctic glaciation', 'The Eocene–Oligocene transition: ice sheets '
    'form on Antarctica and the Grande Coupure reshapes European faunas.'),
 ],
 'firsts': ['Whales', 'Bats', 'Horses', 'Elephant ancestors', 'Grasses spreading',
            'Antarctic ice'],
 'featured': [
   ('Basilosaurus', 'An 18-metre serpentine whale with hind legs the size of a '
    'human hand.'),
   ('Ambulocetus', 'The "walking whale": an otter-like amphibious predator with '
    'a whale’s ear bones.'),
   ('Pakicetus', 'A wolf-sized land animal whose skull already carries the '
    'hearing apparatus of a whale.'),
   ('Eohippus', 'A dog-sized forest browser with four toes in front — the '
    'earliest horse.'),
   ('Uintatherium', 'A rhino-sized herbivore with six blunt horns and sabre-like '
    'canines.'),
   ('Darwinius', 'A superbly complete early primate from Messel, preserved down '
    'to its stomach contents.'),
   ('Icaronycteris', 'An early bat with a claw on each finger, and an inner ear '
    'already built for echolocation.'),
   ('Andrewsarchus', 'Known from a single metre-long skull; a huge hoofed '
    'carnivore related to whales and hippos.'),
   ('Arsinoitherium', 'A rhino-like herbivore with two enormous hollow horns '
    'growing side by side.'),
   ('Moeritherium', 'A tapir-shaped early relative of elephants, living in '
    'North African swamps.'),
   ('Palaeophis', 'A giant sea snake found in Eocene marine rocks on several '
    'continents.'),
 ],
 'scenes': ['Eocene', 'Messel pit', 'Green River Formation',
            'Evolution of cetaceans', 'Basilosaurus'],
},
{
 'id': 'oligocene', 'name': 'Oligocene', 'sub': 'Grass, and the biggest land mammal',
 'start': 33.9, 'end': 23.04, 'color': '#FDC07A', 'era': 'Cenozoic',
 'eon': 'Phanerozoic',
 'lede': 'The world dries and opens out. Forests give way to grassland, and the '
         'largest land mammal that ever lived browses across central Asia.',
 'story': [
   'With Antarctic ice established and CO₂ falling, the climate becomes cooler '
   'and much more seasonal. Closed forest breaks up into woodland and open '
   'country, and grasses — which had existed for tens of millions of years '
   'without dominating anything — begin to spread across continental interiors.',
   'Grass is abrasive: it carries silica phytoliths that grind teeth down. '
   'Herbivores respond with taller crowns and more complex enamel, and legs '
   'built for running in the open rather than dodging between trees. Horses '
   'lose toes. The result is the beginning of the modern grazing fauna.',
   'The extreme case is *Paraceratherium*, a hornless rhinoceros relative '
   'standing five metres at the shoulder and weighing perhaps 20 tonnes — the '
   'largest land mammal known. In the sea, whales split into the two groups '
   'alive today: the toothed whales, which by now echolocate, and the baleen '
   'whales, which begin filtering.',
 ],
 'world': 'The Antarctic Circumpolar Current is fully established, thermally '
          'isolating Antarctica. The Alps and Himalayas continue to rise; the '
          'Tethys is reduced to the Mediterranean and its relics.',
 'events': [
   (33.9, 'The Grande Coupure', 'Cooling and a land connection let Asian '
    'mammals replace much of the European fauna.'),
   (30, 'Grasslands spread', 'Open habitats expand; herbivore teeth get taller '
    'and legs get longer.'),
   (28, 'Paraceratherium', 'The largest land mammal known browses the woodlands '
    'of central Asia.'),
   (25, 'Baleen', 'Filter-feeding whales appear as cold, productive southern '
    'waters open up.'),
 ],
 'firsts': ['Baleen whales', 'Echolocating toothed whales', 'Open grassland faunas'],
 'featured': [
   ('Paraceratherium', 'Five metres at the shoulder and perhaps 20 tonnes — the '
    'largest land mammal that has ever lived.'),
   ('Entelodon', 'The "hell pig": a bison-sized omnivore with a bone-crushing '
    'bite and a face full of bony flanges.'),
   ('Mesohippus', 'A three-toed horse the size of a large dog, with a longer '
    'face and better teeth than its ancestors.'),
   ('Aegyptopithecus', 'An early ape-and-monkey ancestor from the Fayum of '
    'Egypt, with a small brain and large canines.'),
   ('Hyaenodon', 'A widespread predator from an extinct order, with shearing '
    'teeth set further back in the jaw than a modern carnivore’s.'),
   ('Archaeotherium', 'A long-legged entelodont with a huge head and a taste '
    'for carrion.'),
   ('Poebrotherium', 'An early camel, gazelle-sized and built for open ground.'),
   ('Aetiocetus', 'A whale with both teeth and the beginnings of baleen '
    'attachment.'),
 ],
 'scenes': ['Oligocene', 'Paraceratherium', 'Grassland', 'Entelodont'],
},
{
 'id': 'miocene', 'name': 'Miocene', 'sub': 'Apes, grass and megalodon',
 'start': 23.04, 'end': 5.333, 'color': '#FFFF00', 'era': 'Cenozoic',
 'eon': 'Phanerozoic',
 'lede': 'Grasslands take over the continents, apes diversify across Africa and '
         'Eurasia, and the largest shark in history hunts whales.',
 'story': [
   'The middle Miocene is a warm interval — the Miocene Climatic Optimum — '
   'followed by renewed cooling and drying. Grasslands expand enormously, and '
   'around 8 million years ago plants using the C4 photosynthetic pathway, '
   'better suited to low CO₂ and heat, spread across the tropics and remake '
   'the savanna.',
   'This is the great age of apes. Dozens of genera range across Africa, Europe '
   'and Asia — *Proconsul*, *Ekembo*, *Dryopithecus*, *Sivapithecus*, and '
   '*Gigantopithecus*, which stood perhaps three metres tall. Somewhere in the '
   'late Miocene, in Africa, the lineage leading to chimpanzees and the lineage '
   'leading to us separate.',
   'In the oceans, *Otodus megalodon* — up to 18 metres, with teeth the size of '
   'a hand — preys on whales. On land, elephant relatives with four tusks, '
   'clawed horse-relatives that walked on their knuckles, and the enormous '
   'flightless *Argentavis*, with a seven-metre wingspan, share a world already '
   'recognisably modern in its outlines.',
 ],
 'world': 'Africa and India are locked onto Eurasia, the Tethys is destroyed, '
          'and the Alps, Himalayas and Andes are all rising. Around 6 million '
          'years ago the Mediterranean is cut off and very nearly dries out.',
 'events': [
   (23, 'Apes radiate', 'Proconsul and its relatives spread through African '
    'forests.'),
   (16, 'The Miocene Climatic Optimum', 'A warm peak before the long slide into '
    'the ice ages.'),
   (10, 'Hominins and chimps split', 'Molecular and fossil evidence place the '
    'divergence somewhere between 9 and 6 million years ago.'),
   (8, 'The C4 revolution', 'Grasses using a low-CO₂ photosynthetic pathway '
    'spread worldwide, remaking tropical ecosystems.'),
   (5.96, 'The Messinian salinity crisis', 'The Mediterranean is cut off from '
    'the Atlantic and evaporates almost completely, leaving kilometres of salt.'),
 ],
 'firsts': ['Savanna', 'Hominins', 'Kelp forests', 'Modern grazing herds'],
 'featured': [
   ('Otodus megalodon', 'A shark up to 18 metres long, with teeth the size of a '
    'hand, that specialised in whales.'),
   ('Proconsul', 'An early ape with no tail and a monkey-like body, from the '
    'forests of East Africa.'),
   ('Sivapithecus', 'An Asian ape whose face is strikingly like an orangutan’s '
    '— and probably an orangutan ancestor.'),
   ('Gigantopithecus', 'Known mostly from teeth and jaws; the largest ape that '
    'has ever existed.'),
   ('Deinotherium', 'An elephant relative with tusks curving down and backward '
    'from its lower jaw.'),
   ('Gomphotherium', 'A four-tusked elephant relative that spread across three '
    'continents.'),
   ('Argentavis', 'A teratorn with a seven-metre wingspan, soaring over the '
    'Argentine pampas.'),
   ('Chalicotherium', 'A horse relative with long clawed forelimbs that walked '
    'on its knuckles and pulled down branches.'),
   ('Thalassocnus', 'A sloth that returned to the sea and grazed on seagrass '
    'along the Peruvian coast.'),
   ('Livyatan', 'A sperm whale with functional teeth in both jaws, hunting '
    'other whales alongside megalodon.'),
   ('Synthetoceras', 'A North American ruminant with a Y-shaped horn growing '
    'from its snout.'),
   ('Amphicyon', 'The "bear-dog": a heavy predator combining features of both.'),
   ('Ekembo', 'An early ape from Kenya, now separated from Proconsul, with a '
    'mix of monkey and ape traits.'),
 ],
 'scenes': ['Miocene', 'Megalodon', 'Proconsul', 'Messinian salinity crisis',
            'Grassland'],
},
{
 'id': 'pliocene', 'name': 'Pliocene', 'sub': 'Walking upright',
 'start': 5.333, 'end': 2.58, 'color': '#FFFF99', 'era': 'Cenozoic',
 'eon': 'Phanerozoic',
 'lede': 'The Isthmus of Panama closes, two continents exchange their faunas, '
         'the northern ice sheets begin — and in East Africa something starts '
         'walking on two legs.',
 'story': [
   'The Pliocene is close enough to today that the map looks familiar and cold '
   'enough that the ice ages are visibly coming. Early on it is still 2–3°C '
   'warmer than the pre-industrial world with CO₂ near 400 ppm — which is why '
   'it gets cited so often as an analogue for where we are heading — and sea '
   'level is perhaps 20 metres higher.',
   'Panama rises from the sea, joining North and South America for the first '
   'time in tens of millions of years. The Great American Biotic Interchange '
   'follows: placentals move south in force, and South America’s endemic '
   'marsupial predators and strange native hoofed mammals mostly lose. Going '
   'the other way are armadillos, opossums, porcupines and giant ground sloths.',
   'In East Africa, *Australopithecus* walks fully upright. The Laetoli '
   'footprints, 3.6 million years old, are three individuals crossing wet '
   'volcanic ash with a modern human stride — arches, no divergent big toe, '
   'heel first. The brain is still ape-sized. Bipedalism came first; the '
   'expensive brain came later.',
 ],
 'world': 'Effectively the modern map, with one important difference: the '
          'Isthmus of Panama closes, cutting the Atlantic off from the Pacific '
          'and reorganising ocean circulation.',
 'events': [
   (5.33, 'The Zanclean flood', 'The Atlantic breaks through Gibraltar and '
    'refills the Mediterranean, possibly within a couple of years.'),
   (4.4, 'Ardipithecus', 'A hominin with a grasping foot that still climbed but '
    'also walked upright.'),
   (3.6, 'The Laetoli footprints', 'Three hominins cross fresh volcanic ash in '
    'Tanzania and leave an unambiguous record of a modern walking gait.'),
   (3.2, 'Lucy', 'An Australopithecus afarensis skeleton from Hadar, 40% '
    'complete, that settled the argument about upright walking.'),
   (2.8, 'Northern ice sheets', 'Glaciation begins in the Northern Hemisphere; '
    'the first stone tools appear at about the same time.'),
 ],
 'firsts': ['Bipedal hominins', 'Stone tools', 'Northern Hemisphere ice sheets'],
 'featured': [
   ('Australopithecus', 'Ape-sized brain, human-like pelvis and feet — the '
    'genus that established upright walking.'),
   ('Ardipithecus', 'An earlier hominin with a grasping big toe: at home both '
    'in the trees and on two legs.'),
   ('Megatherium', 'A ground sloth the size of an elephant, able to rear up on '
    'its hind legs to feed.'),
   ('Glyptodon', 'An armadillo relative as big as a small car, with a domed '
    'shell of fused bony plates.'),
   ('Smilodon', 'The sabre-toothed cat: heavily built, ambush-hunting, with '
    'canines up to 28 centimetres.'),
   ('Titanis', 'A "terror bird" that crossed into North America — two and a '
    'half metres tall with a hatchet-shaped beak.'),
   ('Macrauchenia', 'A South American native ungulate with a trunk-like nose '
    'and no close living relatives.'),
   ('Toxodon', 'A rhino-shaped South American herbivore that Darwin collected '
    'and could not place.'),
   ('Paranthropus', 'A robust hominin with a bony crest anchoring huge chewing '
    'muscles, built for tough plant food.'),
 ],
 'scenes': ['Pliocene', 'Great American Interchange', 'Australopithecus',
            'Laetoli', 'Isthmus of Panama'],
},
{
 'id': 'pleistocene', 'name': 'Pleistocene', 'sub': 'Ice ages and megafauna',
 'start': 2.58, 'end': 0.0117, 'color': '#FFF2AE', 'era': 'Cenozoic',
 'eon': 'Phanerozoic',
 'lede': 'Ice sheets advance and retreat fifty times, mammoths and giant sloths '
         'range across the continents, and one primate spreads to every one '
         'of them.',
 'story': [
   'The Pleistocene is not one ice age but dozens, paced by slow wobbles in '
   'Earth’s orbit. Every hundred thousand years or so, ice sheets three '
   'kilometres thick spread over Canada and Scandinavia, sea level drops by '
   '120 metres, Britain joins Europe, Siberia joins Alaska, and vast cold '
   'grassland — the mammoth steppe — stretches from Spain to the Yukon.',
   'That steppe supports an extraordinary megafauna: woolly mammoths and woolly '
   'rhinos, cave lions and cave bears, giant deer with three-and-a-half-metre '
   'antlers, and in the Americas ground sloths, mastodons, sabre-toothed cats '
   'and *Arctodus*. Australia has marsupial lions, three-metre kangaroos, and '
   '*Diprotodon*, a wombat the size of a rhinoceros.',
   'And there are several kinds of human. *Homo erectus* leaves Africa nearly '
   'two million years ago; Neanderthals occupy Europe and western Asia; '
   'Denisovans occupy the east; *Homo floresiensis* is a metre tall on an '
   'Indonesian island. *Homo sapiens* appears in Africa around 300,000 years '
   'ago and spreads worldwide after about 60,000. By the end of the epoch every '
   'other human lineage is gone, and so is most of the megafauna on every '
   'continent humans reached — with the timing of those extinctions tracking '
   'human arrival more closely than it tracks climate.',
 ],
 'world': 'The modern map, repeatedly redrawn at the edges: with each glacial '
          'maximum, sea level falls 120 metres and land bridges open between '
          'Asia and America, Britain and Europe, and across Indonesia.',
 'events': [
   (2.58, 'The ice ages begin', 'Northern ice sheets become a permanent feature '
    'and start their orbital rhythm.'),
   (1.9, 'Out of Africa, the first time', 'Homo erectus spreads into Eurasia, '
    'reaching Georgia, China and Java.'),
   (0.9, 'The mid-Pleistocene transition', 'Glacial cycles switch from 41,000 '
    'to 100,000 years and become much more severe.'),
   (0.3, 'Homo sapiens', 'The oldest fossils of our own species, from Jebel '
    'Irhoud in Morocco.'),
   (0.06, 'The global expansion', 'Modern humans spread across Eurasia, reach '
    'Australia by 65,000 years ago and the Americas by at least 15,000.'),
   (0.0117, 'The megafauna are gone', 'On every continent humans reached, most '
    'large mammals disappear within a few thousand years of arrival.'),
 ],
 'firsts': ['Fire', 'Art', 'Clothing', 'Burial', 'People on every continent'],
 'featured': [
   ('Mammuthus', 'The woolly mammoth: small ears, thick underwool, and a fat '
    'hump — a cold-adapted elephant that lasted on Wrangel Island until 4,000 '
    'years ago.'),
   ('Coelodonta', 'The woolly rhinoceros, with a flattened front horn used to '
    'sweep snow off vegetation.'),
   ('Smilodon', 'A sabre-toothed cat with forelimbs strong enough to pin prey '
    'while it delivered a precise throat bite.'),
   ('Megaloceros', 'The "Irish elk": antlers up to 3.6 metres across, on a deer '
    'that ranged from Ireland to Siberia.'),
   ('Homo neanderthalensis', 'Cold-adapted, big-brained, tool-making Europeans '
    'who buried their dead — and whose DNA is still in most of us.'),
   ('Homo erectus', 'The first human to leave Africa, and the longest-lived '
    'human species so far.'),
   ('Ursus spelaeus', 'The cave bear: a huge, largely vegetarian bear known '
    'from caves full of the bones of animals that died hibernating.'),
   ('Diprotodon', 'The largest marsupial known, a three-tonne relative of '
    'wombats.'),
   ('Thylacoleo', 'The marsupial lion, with bolt-cutter premolars and a thumb '
    'claw, and pound for pound the strongest bite of any mammal.'),
   ('Arctodus', 'The short-faced bear, standing 3.5 metres upright, with long '
    'legs built for covering ground.'),
   ('Panthera leo', 'Cave lions ranged from Spain to Alaska and appear in some '
    'of the oldest cave paintings.'),
   ('Doedicurus', 'A glyptodont with a spiked, club-like tail it apparently '
    'used on rivals.'),
   ('Homo floresiensis', 'A metre-tall human on Flores, making stone tools '
    'until about 50,000 years ago.'),
   ('Bison', 'Steppe bison ranged across the mammoth steppe and are among the '
    'commonest animals in Ice Age cave art.'),
 ],
 'scenes': ['Pleistocene', 'Woolly mammoth', 'Last Glacial Maximum',
            'Quaternary extinction event', 'Neanderthal', 'Mammoth steppe'],
},
{
 'id': 'holocene', 'name': 'Holocene', 'sub': 'The human epoch',
 'start': 0.0117, 'end': 0, 'color': '#FEF2E0', 'era': 'Cenozoic',
 'eon': 'Phanerozoic',
 'lede': 'Eleven thousand years of unusually steady climate — long enough to '
         'invent farming, cities and writing, and to start changing the '
         'atmosphere ourselves.',
 'story': [
   'The ice retreats and the climate settles into the most stable stretch in '
   'at least 100,000 years. Within two thousand years agriculture is invented '
   'independently in at least eleven places — wheat and barley in the Fertile '
   'Crescent, rice and millet in China, maize and squash in Mesoamerica, '
   'potatoes in the Andes. Everything else follows from that: surplus, cities, '
   'writing, states.',
   'The biological consequences are enormous. A handful of domesticated species '
   'expand to cover much of the planet’s land surface, and today the combined '
   'mass of livestock is far greater than that of all wild mammals. Species are '
   'moved between continents at a rate no land bridge ever matched, and '
   'extinction rates rise to somewhere between ten and a hundred times the '
   'long-term background.',
   'And the carbon comes back. The coal buried in Carboniferous swamps, the oil '
   'from Cretaceous and Jurassic plankton, the gas from both, are being returned '
   'to the atmosphere in a couple of centuries. CO₂ is now above 420 ppm, '
   'higher than at any point in at least the last 3 million years, and rising '
   'about ten times faster than during the PETM — the fastest natural carbon '
   'release we can find in the record.',
 ],
 'world': 'The map as we know it. Sea level rose about 120 metres as the ice '
          'melted, drowning the land bridges and creating the modern coastline '
          'roughly 7,000 years ago.',
 'events': [
   (0.0117, 'The Holocene begins', 'The Younger Dryas cold snap ends abruptly '
    'and the climate stabilises.'),
   (0.0105, 'Agriculture', 'Wheat, barley, rice, maize and potatoes are '
    'domesticated independently around the world.'),
   (0.0052, 'Writing', 'Cuneiform in Mesopotamia; the historical record begins.'),
   (0.00035, 'Fossil carbon', 'Industrial coal burning starts returning '
    'Carboniferous carbon to the air.'),
   (0.00007, 'The Great Acceleration', 'Population, energy use, and material '
    'flows all turn sharply upward after 1950.'),
   (0, 'Now', 'CO₂ above 420 ppm — the highest in at least 3 million years — '
    'and rising roughly ten times faster than during the PETM.'),
 ],
 'firsts': ['Agriculture', 'Cities', 'Writing', 'Industrial carbon release'],
 'featured': [
   ('Homo sapiens', 'One species, every continent, and the first to alter the '
    'atmosphere deliberately enough to be visible in ice cores.'),
   ('Raphus cucullatus', 'The dodo: a flightless pigeon on Mauritius, extinct '
    'within a century of humans arriving.'),
   ('Hydrodamalis gigas', 'Steller’s sea cow, a nine-metre relative of the '
    'dugong, hunted out within 27 years of being described.'),
   ('Thylacinus cynocephalus', 'The thylacine, the last of a marsupial predator '
    'lineage, shot out of Tasmania by 1936.'),
   ('Ectopistes migratorius', 'The passenger pigeon went from billions of birds '
    'to none in about fifty years.'),
   ('Bos taurus', 'Cattle: descended from the aurochs, and now with a combined '
    'mass many times that of all wild land mammals.'),
   ('Triticum', 'Wheat: a grass whose domestication underwrites most of human '
    'civilisation.'),
   ('Canis lupus familiaris', 'The dog, domesticated from wolves well before '
    'agriculture — the first species we changed.'),
 ],
 'scenes': ['Holocene', 'Neolithic Revolution', 'Holocene extinction',
            'Anthropocene', 'Keeling Curve'],
},
]


def curve(points, t):
    """Linear interpolation over a (age, value) table given oldest-first."""
    pts = sorted(points, key=lambda p: -p[0])
    if t >= pts[0][0]:
        return pts[0][1]
    if t <= pts[-1][0]:
        return pts[-1][1]
    for (a1, v1), (a2, v2) in zip(pts, pts[1:]):
        if a2 <= t <= a1:
            u = 0 if a1 == a2 else (a1 - t) / (a1 - a2)
            return v1 + (v2 - v1) * u
    return pts[-1][1]


def main():
    out = {
        'chapters': [{
            'id': c['id'], 'name': c['name'], 'sub': c['sub'],
            'start': c['start'], 'end': c['end'], 'color': c['color'],
            'era': c['era'], 'eon': c['eon'], 'lede': c['lede'],
            'story': c['story'], 'world': c['world'],
            'events': [{'age': a, 'title': t, 'text': x} for a, t, x in c['events']],
            'firsts': c['firsts'],
            'featured': [{'name': n, 'note': b} for n, b in c['featured']],
            'scenes': c['scenes'],
        } for c in CHAPTERS],
        'curves': {'temp': TEMP, 'co2': CO2, 'o2': O2, 'sea': SEA,
                   'ice': ICE, 'green': GREEN, 'molten': MOLTEN},
        'sources': [{'what': w, 'cite': c} for w, c in SOURCES],
        'disclaimer': DISCLAIMER,
    }
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(f'{OUT}/chapters.json', 'w'),
              separators=(',', ':'), ensure_ascii=False)
    n = sum(len(c['featured']) for c in CHAPTERS)
    print(f'wrote chapters.json: {len(CHAPTERS)} chapters, {n} featured species, '
          f'{sum(len(c["events"]) for c in CHAPTERS)} events '
          f'({os.path.getsize(f"{OUT}/chapters.json")/1024:.0f} KB)')


if __name__ == '__main__':
    main()
