# -*- coding: utf-8 -*-
# Curated biogeography content, keyed by RESOLVE realm+biome code.
# species entries: [common name, scientific name, group]
#   M mammal  B bird  R reptile  A amphibian  F fish  I invertebrate  P plant

BIOMES = {
 1:  ("Tropical & Subtropical Moist Broadleaf Forests", "Tropical rainforest", "#2e6b32",
      "Closed-canopy forest with year-round warmth and heavy rain. The most species-rich habitat on land: half of all described species live in rainforest covering about 7% of the planet."),
 2:  ("Tropical & Subtropical Dry Broadleaf Forests", "Tropical dry forest", "#7a9a3c",
      "Warm all year with a long, severe dry season. Most trees drop their leaves to survive it, so the forest floor swings between deep shade and open sunlight."),
 3:  ("Tropical & Subtropical Coniferous Forests", "Tropical conifer forest", "#4f8f6b",
      "Pine and other conifers at low latitudes, usually on poor soils, ridgelines or fire-swept slopes where broadleaf trees cannot hold on."),
 4:  ("Temperate Broadleaf & Mixed Forests", "Temperate broadleaf forest", "#5f9e4a",
      "Four distinct seasons and deciduous trees that shed leaves before winter. Heavily settled by people — much of the original extent is farmland or regrowth."),
 5:  ("Temperate Conifer Forests", "Temperate conifer forest", "#2f7a5e",
      "Evergreen needle-leaf forest in mild, wet or mountainous temperate zones. Includes the tallest and most massive trees alive."),
 6:  ("Boreal Forests/Taiga", "Boreal forest / taiga", "#3d6b5a",
      "The largest continuous forest on Earth, ringing the northern hemisphere. Short cool summers, brutal winters, and only a handful of tree species."),
 7:  ("Tropical & Subtropical Grasslands, Savannas & Shrublands", "Tropical savanna", "#c9a53f",
      "Grass-dominated country with scattered trees, shaped by seasonal rain, fire and large grazing animals. Home to the planet's biggest surviving herds."),
 8:  ("Temperate Grasslands, Savannas & Shrublands", "Temperate grassland", "#d4c25e",
      "Prairie, steppe and pampas. Too dry for forest, too wet for desert — deep soils that made these the world's most thoroughly ploughed biome."),
 9:  ("Flooded Grasslands & Savannas", "Flooded grassland", "#5aa8c9",
      "Grassland that floods on a seasonal or permanent cycle. Small in area but extraordinary for waterbirds, which gather here in enormous concentrations."),
 10: ("Montane Grasslands & Shrublands", "Montane grassland", "#9d8bb0",
      "High-elevation grass and scrub above the treeline. Intense sun, thin air and freezing nights select for compact, hairy, slow-growing plants."),
 11: ("Tundra", "Tundra", "#a9bcc4",
      "Treeless ground underlain by permafrost. The growing season is measured in weeks, and almost all plant mass sits below the surface."),
 12: ("Mediterranean Forests, Woodlands & Scrub", "Mediterranean scrub", "#c47f4a",
      "Hot dry summers, mild wet winters. Only five small patches worldwide, and all five are exceptionally rich in plants found nowhere else."),
 13: ("Deserts & Xeric Shrublands", "Desert & xeric shrubland", "#d9a566",
      "Less than 250 mm of rain a year, or evaporation that far outstrips it. Life here is built around storing water and avoiding heat."),
 14: ("Mangroves", "Mangrove", "#4a7f6b",
      "Salt-tolerant forest along tropical coasts, rooted in tidal mud. Acts as nursery for reef fish and as the coast's first defence against storms."),
}

REALMS = {
 "AF": ("Afrotropic", "Sub-Saharan Africa, Madagascar and southern Arabia. The one realm that kept its full megafauna through the Pleistocene extinctions."),
 "AN": ("Antarctica", "The southern polar continent. Terrestrial life is reduced to two flowering plants, mosses, lichens and invertebrates."),
 "AU": ("Australasia", "Australia, New Guinea, New Zealand and eastern Indonesia beyond Wallace's Line. Marsupials and ancient Gondwanan lineages dominate."),
 "IN": ("Indomalayan", "South and Southeast Asia from Pakistan to Wallacea. Dense human population layered over some of the richest forests on Earth."),
 "NE": ("Nearctic", "North America down to the Mexican highlands. Shares deep history with the Palearctic across the old Bering land bridge."),
 "NO": ("Neotropic", "South and Central America and the Caribbean. Isolated for tens of millions of years — the most species-rich realm of all."),
 "OC": ("Oceania", "Remote Pacific islands. Tiny land area, extreme endemism, and the highest extinction rate of any realm."),
 "PA": ("Palearctic", "Europe, North Africa, and Asia north of the Himalaya. Vast, cold-adapted, and the longest continuously settled by humans."),
}

CODES = {}

CODES["AF01"] = ("Congo Basin & Guinean rainforest",
 "The second largest rainforest on Earth. Lowland Congolian forest holds intact elephant and great-ape populations; the West African Guinean block is far more fragmented.", [
 ["Western lowland gorilla","Gorilla gorilla gorilla","M"],
 ["Chimpanzee","Pan troglodytes","M"],
 ["Bonobo","Pan paniscus","M"],
 ["Okapi","Okapia johnstoni","M"],
 ["African forest elephant","Loxodonta cyclotis","M"],
 ["Bongo","Tragelaphus eurycerus","M"],
 ["Congo peafowl","Afropavo congensis","B"],
 ["Great blue turaco","Corythaeola cristata","B"],
 ["African grey parrot","Psittacus erithacus","B"],
 ["Goliath beetle","Goliathus goliatus","I"],
 ["African mahogany","Khaya anthotheca","P"],
])

CODES["AF02"] = ("Madagascar & Zambezian dry forest",
 "Madagascar's western dry deciduous forest is one of the most threatened forest types anywhere — reduced to fragments, yet almost everything in it is endemic.", [
 ["Fossa","Cryptoprocta ferox","M"],
 ["Verreaux's sifaka","Propithecus verreauxi","M"],
 ["Giant jumping rat","Hypogeomys antimena","M"],
 ["Madagascar fish eagle","Haliaeetus vociferoides","B"],
 ["Labord's chameleon","Furcifer labordi","R"],
 ["Grandidier's baobab","Adansonia grandidieri","P"],
 ["Radiated tortoise","Astrochelys radiata","R"],
])

CODES["AF07"] = ("African savanna & miombo woodland",
 "The classic African savanna belt — Sahel, Sudanian, Serengeti and the miombo woodlands. Still carries the largest intact assemblage of big mammals on Earth.", [
 ["African bush elephant","Loxodonta africana","M"],
 ["Lion","Panthera leo","M"],
 ["Cheetah","Acinonyx jubatus","M"],
 ["Blue wildebeest","Connochaetes taurinus","M"],
 ["Plains zebra","Equus quagga","M"],
 ["Giraffe","Giraffa camelopardalis","M"],
 ["African wild dog","Lycaon pictus","M"],
 ["Ostrich","Struthio camelus","B"],
 ["Southern ground hornbill","Bucorvus leadbeateri","B"],
 ["Nile crocodile","Crocodylus niloticus","R"],
 ["Umbrella thorn acacia","Vachellia tortilis","P"],
])

CODES["AF08"] = ("South Atlantic island grassland",
 "Tristan da Cunha, Gough and Amsterdam Island — tiny, wind-hammered specks of temperate grassland that serve as globally critical seabird colonies.", [
 ["Tristan albatross","Diomedea dabbenena","B"],
 ["Atlantic yellow-nosed albatross","Thalassarche chlororhynchos","B"],
 ["Gough moorhen","Gallinula comeri","B"],
 ["Inaccessible Island rail","Laterallus rogersi","B"],
 ["Subantarctic fur seal","Arctocephalus tropicalis","M"],
 ["Island tree fern","Blechnum palmiforme","P"],
])

CODES["AF09"] = ("African flooded grassland",
 "The Sudd, Okavango, Bangweulu and Lake Chad — inland deltas and seasonal floodplains that concentrate staggering numbers of waterbirds and antelope.", [
 ["Shoebill","Balaeniceps rex","B"],
 ["Red lechwe","Kobus leche","M"],
 ["Sitatunga","Tragelaphus spekii","M"],
 ["Hippopotamus","Hippopotamus amphibius","M"],
 ["White-eared kob","Kobus kob leucotis","M"],
 ["Wattled crane","Grus carunculata","B"],
 ["African fish eagle","Icthyophaga vocifer","B"],
 ["Papyrus sedge","Cyperus papyrus","P"],
])

CODES["AF10"] = ("Ethiopian & African montane grassland",
 "Sky islands — the Ethiopian Highlands, Drakensberg and Albertine Rift peaks. Long isolation above the surrounding lowlands has produced dense endemism.", [
 ["Ethiopian wolf","Canis simensis","M"],
 ["Gelada","Theropithecus gelada","M"],
 ["Walia ibex","Capra walie","M"],
 ["Mountain nyala","Tragelaphus buxtoni","M"],
 ["Bearded vulture","Gypaetus barbatus","B"],
 ["Giant lobelia","Lobelia rhynchopetalum","P"],
 ["Giant groundsel","Dendrosenecio keniodendron","P"],
])

CODES["AF12"] = ("Cape fynbos & Albany thicket",
 "The Cape Floristic Region: the smallest of the world's six floral kingdoms, and by some measures the richest flora on Earth for its area. Fire is essential to it.", [
 ["Cape sugarbird","Promerops cafer","B"],
 ["Orange-breasted sunbird","Anthobaphes violacea","B"],
 ["Cape grysbok","Raphicerus melanotis","M"],
 ["Geometric tortoise","Psammobates geometricus","R"],
 ["Table Mountain ghost frog","Heleophryne rosei","A"],
 ["King protea","Protea cynaroides","P"],
 ["Silver tree","Leucadendron argenteum","P"],
])

CODES["AF13"] = ("Namib, Kalahari & Karoo",
 "From the Namib — the oldest desert on Earth, watered mainly by coastal fog — to the Karoo's succulent shrublands and the Kalahari's sand sheets.", [
 ["Gemsbok","Oryx gazella","M"],
 ["Meerkat","Suricata suricatta","M"],
 ["Brown hyena","Parahyaena brunnea","M"],
 ["Aardvark","Orycteropus afer","M"],
 ["Sociable weaver","Philetairus socius","B"],
 ["Namaqua chameleon","Chamaeleo namaquensis","R"],
 ["Fog-basking beetle","Onymacris unguicularis","I"],
 ["Welwitschia","Welwitschia mirabilis","P"],
 ["Quiver tree","Aloidendron dichotomum","P"],
])

CODES["AF14"] = ("African mangroves",
 "Mangrove belts along the Guinean and Central African coasts, East Africa and Madagascar — nurseries for coastal fisheries and buffers against erosion.", [
 ["West African manatee","Trichechus senegalensis","M"],
 ["Mangrove monitor","Varanus niloticus","R"],
 ["Goliath heron","Ardea goliath","B"],
 ["Mudskipper","Periophthalmus barbarus","F"],
 ["Fiddler crab","Afruca tangeri","I"],
 ["Red mangrove","Rhizophora racemosa","P"],
])

CODES["AN11"] = ("Antarctic tundra",
 "Ice-free rock and the Antarctic Peninsula. Just two native flowering plants exist on the whole continent; the food web runs on the sea, not the land.", [
 ["Emperor penguin","Aptenodytes forsteri","B"],
 ["Adélie penguin","Pygoscelis adeliae","B"],
 ["Weddell seal","Leptonychotes weddellii","M"],
 ["Leopard seal","Hydrurga leptonyx","M"],
 ["South polar skua","Stercorarius maccormicki","B"],
 ["Antarctic midge","Belgica antarctica","I"],
 ["Antarctic hair grass","Deschampsia antarctica","P"],
])

CODES["AU01"] = ("New Guinea & Moluccan rainforest",
 "New Guinea holds perhaps 5% of the world's species on under 1% of its land, and remains one of the least biologically explored places on Earth.", [
 ["Goodfellow's tree kangaroo","Dendrolagus goodfellowi","M"],
 ["Western long-beaked echidna","Zaglossus bruijni","M"],
 ["Common spotted cuscus","Spilocuscus maculatus","M"],
 ["New Guinea singing dog","Canis lupus hallstromi","M"],
 ["Raggiana bird-of-paradise","Paradisaea raggiana","B"],
 ["Southern cassowary","Casuarius casuarius","B"],
 ["Palm cockatoo","Probosciger aterrimus","B"],
 ["Victoria crowned pigeon","Goura victoria","B"],
 ["Queen Alexandra's birdwing","Ornithoptera alexandrae","I"],
 ["Klinki pine","Araucaria hunsteinii","P"],
])

CODES["AU02"] = ("Lesser Sunda & New Caledonia dry forest",
 "Monsoon-dry islands east of Bali plus New Caledonia's dry forest — the latter reduced to about 1% of its original extent.", [
 ["Komodo dragon","Varanus komodoensis","R"],
 ["Timor deer","Rusa timorensis","M"],
 ["Yellow-crested cockatoo","Cacatua sulphurea","B"],
 ["Kagu","Rhynochetos jubatus","B"],
 ["New Caledonian crow","Corvus moneduloides","B"],
 ["Sandalwood","Santalum album","P"],
])

CODES["AU04"] = ("Australian & New Zealand temperate forest",
 "Eucalypt forest along Australia's southeast plus New Zealand's podocarp and kauri forest — the latter evolved with no land mammals at all, so birds took every role.", [
 ["Koala","Phascolarctos cinereus","M"],
 ["Platypus","Ornithorhynchus anatinus","M"],
 ["Tasmanian devil","Sarcophilus harrisii","M"],
 ["Superb lyrebird","Menura novaehollandiae","B"],
 ["Kea","Nestor notabilis","B"],
 ["North Island brown kiwi","Apteryx mantelli","B"],
 ["Kākāpō","Strigops habroptilus","B"],
 ["Tuatara","Sphenodon punctatus","R"],
 ["Mountain ash","Eucalyptus regnans","P"],
 ["Kauri","Agathis australis","P"],
])

CODES["AU07"] = ("Northern Australian savanna",
 "The tropical north — Kimberley, Arnhem Land and the Gulf country. One of the largest savannas left largely intact, though fire regimes and cane toads have reshaped it.", [
 ["Antilopine kangaroo","Osphranter antilopinus","M"],
 ["Northern quoll","Dasyurus hallucatus","M"],
 ["Agile wallaby","Notamacropus agilis","M"],
 ["Saltwater crocodile","Crocodylus porosus","R"],
 ["Frilled lizard","Chlamydosaurus kingii","R"],
 ["Gouldian finch","Chloebia gouldiae","B"],
 ["Emu","Dromaius novaehollandiae","B"],
 ["Darwin stringybark","Eucalyptus tetrodonta","P"],
])

CODES["AU08"] = ("Australian & NZ temperate grassland",
 "Mulga shrubland, southeastern temperate savanna and New Zealand's tussock grasslands — heavily grazed, and among Australia's most-cleared vegetation types.", [
 ["Red kangaroo","Osphranter rufus","M"],
 ["Plains-wanderer","Pedionomus torquatus","B"],
 ["Australian bustard","Ardeotis australis","B"],
 ["Fat-tailed dunnart","Sminthopsis crassicaudata","M"],
 ["New Zealand falcon","Falco novaeseelandiae","B"],
 ["Snow tussock","Chionochloa rigida","P"],
])

CODES["AU10"] = ("Australasian alpine grassland",
 "The Australian Alps, New Zealand's Southern Alps and New Guinea's high central range — small, cold islands above the treeline.", [
 ["Mountain pygmy possum","Burramys parvus","M"],
 ["Corroboree frog","Pseudophryne corroboree","A"],
 ["Rock wren","Xenicus gilviventris","B"],
 ["New Zealand pipit","Anthus novaeseelandiae","B"],
 ["Alpine she-oak skink","Cyclodomorphus praealtus","R"],
 ["Snow gum","Eucalyptus pauciflora","P"],
 ["Vegetable sheep","Raoulia eximia","P"],
])

CODES["AU11"] = ("Subantarctic island tundra",
 "The Antipodes and neighbouring subantarctic islands — cold, wet, wind-scoured, and disproportionately important as seabird breeding grounds.", [
 ["Antipodean albatross","Diomedea antipodensis","B"],
 ["Erect-crested penguin","Eudyptes sclateri","B"],
 ["Antipodes parakeet","Cyanoramphus unicolor","B"],
 ["New Zealand fur seal","Arctocephalus forsteri","M"],
 ["Megaherb","Pleurophyllum speciosum","P"],
])

CODES["AU12"] = ("Southwest Australian mallee & woodland",
 "Mallee eucalypts and the Southwest Australian Floristic Region — a global biodiversity hotspot with thousands of plants found nowhere else.", [
 ["Numbat","Myrmecobius fasciatus","M"],
 ["Quokka","Setonix brachyurus","M"],
 ["Malleefowl","Leipoa ocellata","B"],
 ["Carnaby's black cockatoo","Zanda latirostris","B"],
 ["Honey possum","Tarsipes rostratus","M"],
 ["Kangaroo paw","Anigozanthos manglesii","P"],
 ["Grass tree","Xanthorrhoea preissii","P"],
])

CODES["AU13"] = ("Australian deserts",
 "The Great Sandy, Simpson, Gibson and Great Victoria deserts — the red centre. Rainfall is erratic rather than merely scarce, so life runs in boom and bust.", [
 ["Thorny devil","Moloch horridus","R"],
 ["Bilby","Macrotis lagotis","M"],
 ["Perentie","Varanus giganteus","R"],
 ["Spinifex hopping mouse","Notomys alexis","M"],
 ["Budgerigar","Melopsittacus undulatus","B"],
 ["Zebra finch","Taeniopygia castanotis","B"],
 ["Spinifex","Triodia basedowii","P"],
 ["Desert oak","Allocasuarina decaisneana","P"],
])

CODES["AU14"] = ("New Guinea mangroves",
 "Extensive, largely intact mangrove along New Guinea's southern and northern coasts — among the least disturbed mangrove systems left.", [
 ["Saltwater crocodile","Crocodylus porosus","R"],
 ["Dugong","Dugong dugon","M"],
 ["Great-billed heron","Ardea sumatrana","B"],
 ["Archerfish","Toxotes chatareus","F"],
 ["Nipa palm","Nypa fruticans","P"],
])
