# -*- coding: utf-8 -*-
"""Additional species appended to each realm+biome list in biota_1..3.

Keys are realm+biome codes; "CODE@N" targets variant N of that code.
Duplicates against the base list are dropped at build time.
"""
EXTRA = {}

EXTRA["AF01"] = [
 ["Mandrill","Mandrillus sphinx","M"], ["Black-and-white colobus","Colobus guereza","M"],
 ["Giant forest hog","Hylochoerus meinertzhageni","M"], ["Water chevrotain","Hyemoschus aquaticus","M"],
 ["African golden cat","Caracal aurata","M"], ["Potto","Perodicticus potto","M"],
 ["Tree pangolin","Phataginus tricuspis","M"], ["Hammer-headed bat","Hypsignathus monstrosus","M"],
 ["Grey-necked rockfowl","Picathartes oreas","B"], ["Yellow-casqued hornbill","Ceratogymna elata","B"],
 ["Hartlaub's duck","Pteronetta hartlaubii","B"], ["Gaboon viper","Bitis gabonica","R"],
 ["African rock python","Python sebae","R"], ["Goliath frog","Conraua goliath","A"],
 ["Okoumé","Aucoumea klaineana","P"], ["Iroko","Milicia excelsa","P"],
]
EXTRA["AF02"] = [
 ["Ring-tailed lemur","Lemur catta","M"], ["Coquerel's sifaka","Propithecus coquereli","M"],
 ["Madame Berthe's mouse lemur","Microcebus berthae","M"], ["Narrow-striped mongoose","Mungotictis decemlineata","M"],
 ["Madagascar ground boa","Acrantophis madagascariensis","R"], ["Oustalet's chameleon","Furcifer oustaleti","R"],
 ["Spider tortoise","Pyxis arachnoides","R"], ["Sickle-billed vanga","Falculea palliata","B"],
 ["Madagascar hoopoe","Upupa marginata","B"], ["Giant coua","Coua gigas","B"],
 ["Octopus tree","Didierea madagascariensis","P"], ["Elephant's foot","Pachypodium rosulatum","P"],
]
EXTRA["AF07"] = [
 ["Leopard","Panthera pardus","M"], ["Spotted hyena","Crocuta crocuta","M"],
 ["Black rhinoceros","Diceros bicornis","M"], ["White rhinoceros","Ceratotherium simum","M"],
 ["Cape buffalo","Syncerus caffer","M"], ["Thomson's gazelle","Eudorcas thomsonii","M"],
 ["Impala","Aepyceros melampus","M"], ["Greater kudu","Tragelaphus strepsiceros","M"],
 ["Warthog","Phacochoerus africanus","M"], ["Olive baboon","Papio anubis","M"],
 ["Honey badger","Mellivora capensis","M"], ["Secretarybird","Sagittarius serpentarius","B"],
 ["Lilac-breasted roller","Coracias caudatus","B"], ["Red-billed oxpecker","Buphagus erythrorhynchus","B"],
 ["Kori bustard","Ardeotis kori","B"], ["Puff adder","Bitis arietans","R"],
 ["Leopard tortoise","Stigmochelys pardalis","R"], ["Termite","Macrotermes bellicosus","I"],
 ["Baobab","Adansonia digitata","P"], ["Miombo tree","Brachystegia boehmii","P"],
]
EXTRA["AF08"] = [
 ["Northern rockhopper penguin","Eudyptes moseleyi","B"], ["Sooty albatross","Phoebetria fusca","B"],
 ["Great shearwater","Ardenna gravis","B"], ["Tristan thrush","Turdus eremita","B"],
 ["Wilkins's finch","Nesospiza wilkinsi","B"], ["Gough bunting","Rowettia goughensis","B"],
 ["Southern elephant seal","Mirounga leonina","M"], ["Phylica tree","Phylica arborea","P"],
 ["Island bog fern","Blechnum penna-marina","P"],
]
EXTRA["AF09"] = [
 ["Nile lechwe","Kobus megaceros","M"], ["Puku","Kobus vardonii","M"],
 ["Tsessebe","Damaliscus lunatus","M"], ["Marsh mongoose","Atilax paludinosus","M"],
 ["Spotted-necked otter","Hydrictis maculicollis","M"], ["Saddle-billed stork","Ephippiorhynchus senegalensis","B"],
 ["Grey crowned crane","Balearica regulorum","B"], ["African skimmer","Rynchops flavirostris","B"],
 ["Pel's fishing owl","Scotopelia peli","B"], ["Slaty egret","Egretta vinaceigula","B"],
 ["African rock python","Python sebae","R"], ["Tigerfish","Hydrocynus vittatus","F"],
 ["Nile perch","Lates niloticus","F"], ["Water lily","Nymphaea nouchali","P"],
]
EXTRA["AF10"] = [
 ["Mountain gorilla","Gorilla beringei beringei","M"], ["Golden monkey","Cercopithecus kandti","M"],
 ["Klipspringer","Oreotragus oreotragus","M"], ["Rock hyrax","Procavia capensis","M"],
 ["Ethiopian highland hare","Lepus starcki","M"], ["Blue duiker","Philantomba monticola","M"],
 ["Lammergeier","Gypaetus barbatus","B"], ["Wattled ibis","Bostrychia carunculata","B"],
 ["Blue-winged goose","Cyanochen cyanoptera","B"], ["Rouget's rail","Rougetius rougetii","B"],
 ["Malachite sunbird","Nectarinia famosa","B"], ["Ethiopian mountain adder","Bitis parviocula","R"],
 ["Giant heath","Erica arborea","P"], ["Red hot poker","Kniphofia foliosa","P"],
]
EXTRA["AF12"] = [
 ["Chacma baboon","Papio ursinus","M"], ["Caracal","Caracal caracal","M"],
 ["Bontebok","Damaliscus pygargus","M"], ["Honey badger","Mellivora capensis","M"],
 ["Cape rock elephant shrew","Elephantulus edwardii","M"], ["Cape rockjumper","Chaetops frenatus","B"],
 ["Protea canary","Crithagra leucoptera","B"], ["Black harrier","Circus maurus","B"],
 ["Cape mountain toad","Capensibufo rosei","A"], ["Armadillo girdled lizard","Ouroborus cataphractus","R"],
 ["Cape sundew","Drosera cistiflora","P"], ["Pincushion protea","Leucospermum cordifolium","P"],
 ["Erica","Erica versicolor","P"], ["Restio","Elegia capensis","P"],
]
EXTRA["AF13"] = [
 ["Springbok","Antidorcas marsupialis","M"], ["Black-backed jackal","Lupulella mesomelas","M"],
 ["Cape ground squirrel","Xerus inauris","M"], ["Bat-eared fox","Otocyon megalotis","M"],
 ["Hartmann's mountain zebra","Equus zebra hartmannae","M"], ["Desert-adapted elephant","Loxodonta africana","M"],
 ["Cape fox","Vulpes chama","M"], ["Ludwig's bustard","Neotis ludwigii","B"],
 ["Lappet-faced vulture","Torgos tracheliotos","B"], ["Rüppell's korhaan","Eupodotis rueppelii","B"],
 ["Web-footed gecko","Pachydactylus rangei","R"], ["Horned adder","Bitis caudalis","R"],
 ["Golden mole","Eremitalpa granti","M"], ["Halfmens","Pachypodium namaquanum","P"],
 ["Camel thorn","Vachellia erioloba","P"], ["Nara melon","Acanthosicyos horridus","P"],
]
EXTRA["AF14"] = [
 ["Sitatunga","Tragelaphus spekii","M"], ["Bottlenose dolphin","Tursiops aduncus","M"],
 ["Mangrove kingfisher","Halcyon senegaloides","B"], ["Crab-plover","Dromas ardeola","B"],
 ["Yellow-billed stork","Mycteria ibis","B"], ["Green turtle","Chelonia mydas","R"],
 ["Nile crocodile","Crocodylus niloticus","R"], ["Mangrove oyster","Crassostrea gasar","I"],
 ["Mangrove whelk","Terebralia palustris","I"], ["Black mangrove","Avicennia germinans","P"],
 ["White mangrove","Laguncularia racemosa","P"],
]
EXTRA["AN11"] = [
 ["Chinstrap penguin","Pygoscelis antarcticus","B"], ["Gentoo penguin","Pygoscelis papua","B"],
 ["Snow petrel","Pagodroma nivea","B"], ["Antarctic petrel","Thalassoica antarctica","B"],
 ["Wilson's storm petrel","Oceanites oceanicus","B"], ["Crabeater seal","Lobodon carcinophagus","M"],
 ["Ross seal","Ommatophoca rossii","M"], ["Southern elephant seal","Mirounga leonina","M"],
 ["Springtail","Cryptopygus antarcticus","I"], ["Antarctic mite","Alaskozetes antarcticus","I"],
 ["Antarctic pearlwort","Colobanthus quitensis","P"], ["Snow alga","Chlamydomonas nivalis","P"],
 ["Map lichen","Rhizocarpon geographicum","P"],
]
EXTRA["AU01"] = [
 ["Doria's tree kangaroo","Dendrolagus dorianus","M"], ["Sugar glider","Petaurus breviceps","M"],
 ["Northern common cuscus","Phalanger orientalis","M"], ["Bare-backed fruit bat","Dobsonia moluccensis","M"],
 ["Dwarf cassowary","Casuarius bennetti","B"], ["King bird-of-paradise","Cicinnurus regius","B"],
 ["Wilson's bird-of-paradise","Cicinnurus respublica","B"], ["Vulturine parrot","Psittrichas fulgidus","B"],
 ["Blyth's hornbill","Rhyticeros plicatus","B"], ["Hooded pitohui","Pitohui dichrous","B"],
 ["Boelen's python","Simalia boeleni","R"], ["Green tree python","Morelia viridis","R"],
 ["Papuan frogmouth","Podargus papuensis","B"], ["Sago palm","Metroxylon sagu","P"],
 ["Pandanus","Pandanus julianettii","P"],
]
EXTRA["AU02"] = [
 ["Rote Island snake-necked turtle","Chelodina mccordi","R"], ["Timor python","Malayopython timoriensis","R"],
 ["Flores giant rat","Papagomys armandvillei","M"], ["Sunda pangolin","Manis javanica","M"],
 ["Black-winged myna","Acridotheres melanopterus","B"], ["Flores hawk-eagle","Nisaetus floris","B"],
 ["Red-cheeked parrot","Geoffroyus geoffroyi","B"], ["Crowned fruit dove","Ptilinopus coronulatus","B"],
 ["New Caledonian giant gecko","Rhacodactylus leachianus","R"], ["Cloudy ground gecko","Bavayia cyclura","R"],
 ["Cook pine","Araucaria columnaris","P"], ["Tamarind","Tamarindus indica","P"],
]
EXTRA["AU04"] = [
 ["Common wombat","Vombatus ursinus","M"], ["Short-beaked echidna","Tachyglossus aculeatus","M"],
 ["Eastern grey kangaroo","Macropus giganteus","M"], ["Spotted-tailed quoll","Dasyurus maculatus","M"],
 ["Sugar glider","Petaurus breviceps","M"], ["Long-nosed bandicoot","Perameles nasuta","M"],
 ["Laughing kookaburra","Dacelo novaeguineae","B"], ["Sulphur-crested cockatoo","Cacatua galerita","B"],
 ["Crimson rosella","Platycercus elegans","B"], ["Takahē","Porphyrio hochstetteri","B"],
 ["Tūī","Prosthemadera novaeseelandiae","B"], ["Weka","Gallirallus australis","B"],
 ["Lace monitor","Varanus varius","R"], ["Corroboree frog","Pseudophryne pengilleyi","A"],
 ["Antarctic beech","Nothofagus moorei","P"], ["Rimu","Dacrydium cupressinum","P"],
 ["Tree fern","Dicksonia antarctica","P"],
]
EXTRA["AU07"] = [
 ["Dingo","Canis familiaris dingo","M"], ["Short-eared rock wallaby","Petrogale brachyotis","M"],
 ["Black flying fox","Pteropus alecto","M"], ["Water buffalo","Bubalus bubalis","M"],
 ["Brolga","Antigone rubicunda","B"], ["Black-necked stork","Ephippiorhynchus asiaticus","B"],
 ["Red-tailed black cockatoo","Calyptorhynchus banksii","B"], ["Rainbow bee-eater","Merops ornatus","B"],
 ["Partridge pigeon","Geophaps smithii","B"], ["Olive python","Liasis olivaceus","R"],
 ["Northern death adder","Acanthophis praelongus","R"], ["Cane toad","Rhinella marina","A"],
 ["Cathedral termite","Nasutitermes triodiae","I"], ["Boab","Adansonia gregorii","P"],
 ["Woollybutt","Eucalyptus miniata","P"],
]
EXTRA["AU08"] = [
 ["Western grey kangaroo","Macropus fuliginosus","M"], ["Euro / common wallaroo","Osphranter robustus","M"],
 ["Stripe-faced dunnart","Sminthopsis macroura","M"], ["Greater bilby","Macrotis lagotis","M"],
 ["Emu","Dromaius novaehollandiae","B"], ["Wedge-tailed eagle","Aquila audax","B"],
 ["Banded lapwing","Vanellus tricolor","B"], ["Kea","Nestor notabilis","B"],
 ["Black-fronted tern","Chlidonias albostriatus","B"], ["Bearded dragon","Pogona vitticeps","R"],
 ["Grand skink","Oligosoma grande","R"], ["Mulga","Acacia aneura","P"],
 ["Saltbush","Atriplex nummularia","P"],
]
EXTRA["AU10"] = [
 ["Broad-toothed rat","Mastacomys fuscus","M"], ["Dusky antechinus","Antechinus swainsonii","M"],
 ["Kea","Nestor notabilis","B"], ["Takahē","Porphyrio hochstetteri","B"],
 ["Australian pipit","Anthus australis","B"], ["Alpine grasshopper","Kosciuscola tristis","I"],
 ["Mountain stone wētā","Hemideina maori","I"], ["Bogong moth","Agrotis infusa","I"],
 ["Silver snow daisy","Celmisia astelifolia","P"], ["Mount Cook lily","Ranunculus lyallii","P"],
 ["Alpine speargrass","Aciphylla scott-thomsonii","P"],
]
EXTRA["AU11"] = [
 ["Southern royal albatross","Diomedea epomophora","B"], ["Light-mantled albatross","Phoebetria palpebrata","B"],
 ["Rockhopper penguin","Eudyptes chrysocome","B"], ["Snares penguin","Eudyptes robustus","B"],
 ["Antipodes snipe","Coenocorypha aucklandica","B"], ["Auckland teal","Anas aucklandica","B"],
 ["Southern elephant seal","Mirounga leonina","M"], ["Hooker's sea lion","Phocarctos hookeri","M"],
 ["Ross lily","Bulbinella rossii","P"], ["Campbell Island daisy","Pleurophyllum criniferum","P"],
]
EXTRA["AU12"] = [
 ["Western grey kangaroo","Macropus fuliginosus","M"], ["Woylie","Bettongia penicillata","M"],
 ["Chuditch","Dasyurus geoffroii","M"], ["Western ringtail possum","Pseudocheirus occidentalis","M"],
 ["Red-tailed phascogale","Phascogale calura","M"], ["Baudin's black cockatoo","Zanda baudinii","B"],
 ["Western spinebill","Acanthorhynchus superciliosus","B"], ["Noisy scrub-bird","Atrichornis clamosus","B"],
 ["Ornate dragon","Ctenophorus ornatus","R"], ["Southern heath monitor","Varanus rosenbergi","R"],
 ["Jarrah","Eucalyptus marginata","P"], ["Karri","Eucalyptus diversicolor","P"],
 ["Banksia","Banksia grandis","P"], ["Christmas tree","Nuytsia floribunda","P"],
]
EXTRA["AU13"] = [
 ["Dingo","Canis familiaris dingo","M"], ["Red kangaroo","Osphranter rufus","M"],
 ["Mulgara","Dasycercus blythi","M"], ["Marsupial mole","Notoryctes typhlops","M"],
 ["Black-footed rock wallaby","Petrogale lateralis","M"], ["Wedge-tailed eagle","Aquila audax","B"],
 ["Princess parrot","Polytelis alexandrae","B"], ["Spinifex pigeon","Geophaps plumifera","B"],
 ["Sand goanna","Varanus gouldii","R"], ["Central netted dragon","Ctenophorus nuchalis","R"],
 ["Woma python","Aspidites ramsayi","R"], ["Water-holding frog","Ranoidea platycephala","A"],
 ["Honey ant","Camponotus inflatus","I"], ["Ghost gum","Corymbia aparrerinja","P"],
 ["Sturt's desert pea","Swainsona formosa","P"],
]
EXTRA["AU14"] = [
 ["Fly River turtle","Carettochelys insculpta","R"], ["New Guinea crocodile","Crocodylus novaeguineae","R"],
 ["Spotted cuscus","Spilocuscus maculatus","M"], ["Little kingfisher","Ceyx pusillus","B"],
 ["Beach stone-curlew","Esacus magnirostris","B"], ["Torresian imperial pigeon","Ducula spilorrhoa","B"],
 ["Mud lobster","Thalassina anomala","I"], ["Giant mud crab","Scylla serrata","I"],
 ["Barramundi","Lates calcarifer","F"], ["Sonneratia mangrove","Sonneratia alba","P"],
 ["Rhizophora mangrove","Rhizophora apiculata","P"],
]

EXTRA["IN01"] = [
 ["Asian elephant","Elephas maximus","M"], ["Sun bear","Helarctos malayanus","M"],
 ["Marbled cat","Pardofelis marmorata","M"], ["Colugo","Galeopterus variegatus","M"],
 ["Slow loris","Nycticebus coucang","M"], ["Siamang","Symphalangus syndactylus","M"],
 ["Bornean gibbon","Hylobates muelleri","M"], ["Sunda pangolin","Manis javanica","M"],
 ["Sunda clouded leopard","Neofelis diardi","M"], ["Helmeted hornbill","Rhinoplax vigil","B"],
 ["Wreathed hornbill","Rhyticeros undulatus","B"], ["Asian fairy-bluebird","Irena puella","B"],
 ["Bornean bristlehead","Pityriasis gymnocephala","B"], ["King cobra","Ophiophagus hannah","R"],
 ["Paradise tree snake","Chrysopelea paradisi","R"], ["Wallace's flying frog","Rhacophorus nigropalmatus","A"],
 ["Atlas moth","Attacus atlas","I"], ["Pitcher plant","Nepenthes rajah","P"],
 ["Ironwood","Eusideroxylon zwageri","P"],
]
EXTRA["IN02"] = [
 ["Leopard","Panthera pardus fusca","M"], ["Nilgai","Boselaphus tragocamelus","M"],
 ["Sambar","Rusa unicolor","M"], ["Four-horned antelope","Tetracerus quadricornis","M"],
 ["Indian pangolin","Manis crassicaudata","M"], ["Golden jackal","Canis aureus","M"],
 ["Rusty-spotted cat","Prionailurus rubiginosus","M"], ["Hanuman langur","Semnopithecus entellus","M"],
 ["White-rumped vulture","Gyps bengalensis","B"], ["Indian roller","Coracias benghalensis","B"],
 ["Painted stork","Mycteria leucocephala","B"], ["Indian rock python","Python molurus","R"],
 ["Russell's viper","Daboia russelii","R"], ["Star tortoise","Geochelone elegans","R"],
 ["Mahua","Madhuca longifolia","P"], ["Flame of the forest","Butea monosperma","P"],
]
EXTRA["IN03"] = [
 ["Asiatic black bear","Ursus thibetanus","M"], ["Barking deer","Muntiacus muntjak","M"],
 ["Rhesus macaque","Macaca mulatta","M"], ["Philippine deer","Rusa marianna","M"],
 ["Philippine warty pig","Sus philippensis","M"], ["Kalij pheasant","Lophura leucomelanos","B"],
 ["Whiskered treeswift","Hemiprocne comata","B"], ["Flame-breasted flowerpecker","Dicaeum erythrothorax","B"],
 ["Luzon pine snake","Ptyas luzonensis","R"], ["Khasi pine","Pinus kesiya","P"],
 ["Blue pine","Pinus wallichiana","P"], ["Rhododendron","Rhododendron arboreum","P"],
]
EXTRA["IN04"] = [
 ["Clouded leopard","Neofelis nebulosa","M"], ["Golden langur","Trachypithecus geei","M"],
 ["Assam macaque","Macaca assamensis","M"], ["Yellow-throated marten","Martes flavigula","M"],
 ["Binturong","Arctictis binturong","M"], ["Takin","Budorcas taxicolor","M"],
 ["Kalij pheasant","Lophura leucomelanos","B"], ["Ward's trogon","Harpactes wardi","B"],
 ["Fire-tailed sunbird","Aethopyga ignicauda","B"], ["Beautiful nuthatch","Sitta formosa","B"],
 ["Himalayan newt","Tylototriton verrucosus","A"], ["Himalayan oak","Quercus semecarpifolia","P"],
 ["Deodar cedar","Cedrus deodara","P"], ["Daphne","Daphne bholua","P"],
]
EXTRA["IN05"] = [
 ["Snow leopard","Panthera uncia","M"], ["Himalayan tahr","Hemitragus jemlahicus","M"],
 ["Bharal / blue sheep","Pseudois nayaur","M"], ["Stone marten","Martes foina","M"],
 ["Pika","Ochotona roylei","M"], ["Himalayan monal","Lophophorus impejanus","B"],
 ["Snow partridge","Lerwa lerwa","B"], ["Grandala","Grandala coelicolor","B"],
 ["Fire-tailed myzornis","Myzornis pyrrhoura","B"], ["Juniper","Juniperus indica","P"],
 ["Dwarf rhododendron","Rhododendron anthopogon","P"], ["Blue poppy","Meconopsis grandis","P"],
]
EXTRA["IN07"] = [
 ["Gaur","Bos gaurus","M"], ["Sambar","Rusa unicolor","M"],
 ["Sloth bear","Melursus ursinus","M"], ["Smooth-coated otter","Lutrogale perspicillata","M"],
 ["Golden jackal","Canis aureus","M"], ["Gharial","Gavialis gangeticus","R"],
 ["Indian rock python","Python molurus","R"], ["Lesser adjutant","Leptoptilos javanicus","B"],
 ["Swamp francolin","Ortygornis gularis","B"], ["Finn's weaver","Ploceus megarhynchus","B"],
 ["Sal","Shorea robusta","P"], ["Kans grass","Saccharum spontaneum","P"],
]
EXTRA["IN09"] = [
 ["Striped hyena","Hyaena hyaena","M"], ["Jungle cat","Felis chaus","M"],
 ["Indian fox","Vulpes bengalensis","M"], ["Wild boar","Sus scrofa","M"],
 ["Lesser flamingo","Phoeniconaias minor","B"], ["Common crane","Grus grus","B"],
 ["Dalmatian pelican","Pelecanus crispus","B"], ["Indian courser","Cursorius coromandelicus","B"],
 ["Spiny-tailed lizard","Saara hardwickii","R"], ["Saltwort","Salicornia brachiata","P"],
 ["Prosopis scrub","Prosopis cineraria","P"],
]
EXTRA["IN10"] = [
 ["Bornean ferret-badger","Melogale everetti","M"], ["Summit rat","Rattus baluensis","M"],
 ["Whitehead's spiderhunter","Arachnothera juliae","B"], ["Whitehead's trogon","Harpactes whiteheadi","B"],
 ["Kinabalu serpent eagle","Spilornis kinabaluensis","B"], ["Kinabalu horned frog","Xenophrys baluensis","A"],
 ["Rajah Brooke's birdwing","Trogonoptera brookiana","I"], ["Giant pitcher plant","Nepenthes rajah","P"],
 ["Kinabalu balsam","Impatiens platyphylla","P"], ["Trig oak","Leptospermum recurvum","P"],
]
EXTRA["IN13"] = [
 ["Striped hyena","Hyaena hyaena","M"], ["Indian fox","Vulpes bengalensis","M"],
 ["Desert cat","Felis lybica ornata","M"], ["Nilgai","Boselaphus tragocamelus","M"],
 ["Indian hedgehog","Paraechinus micropus","M"], ["Indian courser","Cursorius coromandelicus","B"],
 ["White-browed bushchat","Saxicola macrorhynchus","B"], ["Cream-coloured courser","Cursorius cursor","B"],
 ["Saw-scaled viper","Echis carinatus","R"], ["Indian spiny-tailed lizard","Saara hardwickii","R"],
 ["Rohida","Tecomella undulata","P"], ["Aak","Calotropis procera","P"],
 ["Desert grass","Lasiurus sindicus","P"],
]
EXTRA["IN14"] = [
 ["Smooth-coated otter","Lutrogale perspicillata","M"], ["Rhesus macaque","Macaca mulatta","M"],
 ["Chital","Axis axis","M"], ["Ganges river dolphin","Platanista gangetica","M"],
 ["Water monitor","Varanus salvator","R"], ["Olive ridley turtle","Lepidochelys olivacea","R"],
 ["Lesser adjutant","Leptoptilos javanicus","B"], ["Brown-winged kingfisher","Pelargopsis amauroptera","B"],
 ["Mangrove pitta","Pitta megarhyncha","B"], ["Mud crab","Scylla serrata","I"],
 ["Horseshoe crab","Tachypleus gigas","I"], ["Gewa","Excoecaria agallocha","P"],
 ["Nipa palm","Nypa fruticans","P"],
]
EXTRA["NE02"] = [
 ["Collared peccary","Dicotyles tajacu","M"], ["Coati","Nasua narica","M"],
 ["White-tailed deer","Odocoileus virginianus","M"], ["Mexican long-tongued bat","Choeronycteris mexicana","M"],
 ["Lilac-crowned parrot","Amazona finschi","B"], ["Black-throated magpie-jay","Calocitta colliei","B"],
 ["Rufous-bellied chachalaca","Ortalis wagleri","B"], ["Boa constrictor","Boa imperator","R"],
 ["Mexican beaded lizard","Heloderma horridum","R"], ["Organ pipe cactus","Stenocereus thurberi","P"],
 ["Kapok","Ceiba aesculifolia","P"],
]
EXTRA["NE03"] = [
 ["Black bear","Ursus americanus","M"], ["Coati","Nasua narica","M"],
 ["Volcano rabbit","Romerolagus diazi","M"], ["Mexican fox squirrel","Sciurus nayaritensis","M"],
 ["Elegant trogon","Trogon elegans","B"], ["Red warbler","Cardellina rubra","B"],
 ["Steller's jay","Cyanocitta stelleri","B"], ["Bearded wood partridge","Dendrortyx barbatus","B"],
 ["Rock rattlesnake","Crotalus lepidus","R"], ["Alligator lizard","Barisia imbricata","R"],
 ["Montezuma pine","Pinus montezumae","P"], ["Weeping pine","Pinus patula","P"],
 ["Sacred fir","Abies religiosa","P"],
]
EXTRA["NE04"] = [
 ["Bobcat","Lynx rufus","M"], ["Fisher","Pekania pennanti","M"],
 ["North American porcupine","Erethizon dorsatum","M"], ["Northern flying squirrel","Glaucomys sabrinus","M"],
 ["Beaver","Castor canadensis","M"], ["Coyote","Canis latrans","M"],
 ["Barred owl","Strix varia","B"], ["Ruffed grouse","Bonasa umbellus","B"],
 ["Wood thrush","Hylocichla mustelina","B"], ["Ovenbird","Seiurus aurocapilla","B"],
 ["Spotted salamander","Ambystoma maculatum","A"], ["Wood frog","Lithobates sylvaticus","A"],
 ["Eastern box turtle","Terrapene carolina","R"], ["Timber rattlesnake","Crotalus horridus","R"],
 ["American chestnut","Castanea dentata","P"], ["White oak","Quercus alba","P"],
 ["Tulip tree","Liriodendron tulipifera","P"],
]
EXTRA["NE05"] = [
 ["Mountain lion","Puma concolor","M"], ["Bighorn sheep","Ovis canadensis","M"],
 ["Mountain goat","Oreamnos americanus","M"], ["Mule deer","Odocoileus hemionus","M"],
 ["American marten","Martes americana","M"], ["Pika","Ochotona princeps","M"],
 ["Yellow-bellied marmot","Marmota flaviventris","M"], ["Northern goshawk","Astur atricapillus","B"],
 ["Williamson's sapsucker","Sphyrapicus thyroideus","B"], ["Varied thrush","Ixoreus naevius","B"],
 ["Pacific giant salamander","Dicamptodon tenebrosus","A"], ["Ponderosa pine","Pinus ponderosa","P"],
 ["Lodgepole pine","Pinus contorta","P"], ["Western red cedar","Thuja plicata","P"],
 ["Sitka spruce","Picea sitchensis","P"], ["Bristlecone pine","Pinus longaeva","P"],
]
EXTRA["NE06"] = [
 ["Grey wolf","Canis lupus","M"], ["American black bear","Ursus americanus","M"],
 ["American marten","Martes americana","M"], ["Beaver","Castor canadensis","M"],
 ["Northern flying squirrel","Glaucomys sabrinus","M"], ["Boreal owl","Aegolius funereus","B"],
 ["Northern hawk-owl","Surnia ulula","B"], ["Black-backed woodpecker","Picoides arcticus","B"],
 ["Canada jay","Perisoreus canadensis","B"], ["White-throated sparrow","Zonotrichia albicollis","B"],
 ["Sandhill crane","Antigone canadensis","B"], ["Wood frog","Lithobates sylvaticus","A"],
 ["Jack pine","Pinus banksiana","P"], ["Tamarack","Larix laricina","P"],
 ["Trembling aspen","Populus tremuloides","P"], ["Reindeer lichen","Cladonia rangiferina","P"],
]
EXTRA["NE07"] = [
 ["Coyote","Canis latrans","M"], ["Bobcat","Lynx rufus","M"],
 ["Marsh rice rat","Oryzomys palustris","M"], ["Sandhill crane","Antigone canadensis","B"],
 ["Roseate spoonbill","Platalea ajaja","B"], ["Seaside sparrow","Ammospiza maritima","B"],
 ["Le Conte's sparrow","Ammospiza leconteii","B"], ["Texas horned lizard","Phrynosoma cornutum","R"],
 ["Western diamondback","Crotalus atrox","R"], ["Little bluestem","Schizachyrium scoparium","P"],
 ["Eastern gamagrass","Tripsacum dactyloides","P"],
]
EXTRA["NE08"] = [
 ["Coyote","Canis latrans","M"], ["Badger","Taxidea taxus","M"],
 ["Elk","Cervus canadensis","M"], ["Mule deer","Odocoileus hemionus","M"],
 ["Thirteen-lined ground squirrel","Ictidomys tridecemlineatus","M"], ["Lesser prairie chicken","Tympanuchus pallidicinctus","B"],
 ["Mountain plover","Charadrius montanus","B"], ["Bobolink","Dolichonyx oryzivorus","B"],
 ["Western meadowlark","Sturnella neglecta","B"], ["Sharp-tailed grouse","Tympanuchus phasianellus","B"],
 ["Plains hognose snake","Heterodon nasicus","R"], ["Ornate box turtle","Terrapene ornata","R"],
 ["Monarch butterfly","Danaus plexippus","I"], ["Little bluestem","Schizachyrium scoparium","P"],
 ["Buffalograss","Bouteloua dactyloides","P"], ["Purple coneflower","Echinacea angustifolia","P"],
]
EXTRA["NE11"] = [
 ["Arctic wolf","Canis lupus arctos","M"], ["Wolverine","Gulo gulo","M"],
 ["Arctic hare","Lepus arcticus","M"], ["Walrus","Odobenus rosmarus","M"],
 ["Narwhal","Monodon monoceros","M"], ["Beluga","Delphinapterus leucas","M"],
 ["Gyrfalcon","Falco rusticolus","B"], ["Snow bunting","Plectrophenax nivalis","B"],
 ["King eider","Somateria spectabilis","B"], ["Red phalarope","Phalaropus fulicarius","B"],
 ["Long-tailed jaeger","Stercorarius longicaudus","B"], ["Woolly bear moth","Gynaephora groenlandica","I"],
 ["Mountain avens","Dryas integrifolia","P"], ["Arctic cotton grass","Eriophorum scheuchzeri","P"],
 ["Lapland rosebay","Rhododendron lapponicum","P"],
]
EXTRA["NE12"] = [
 ["Bobcat","Lynx rufus","M"], ["Coyote","Canis latrans","M"],
 ["Ringtail","Bassariscus astutus","M"], ["Dusky-footed woodrat","Neotoma fuscipes","M"],
 ["Acorn woodpecker","Melanerpes formicivorus","B"], ["Wrentit","Chamaea fasciata","B"],
 ["California quail","Callipepla californica","B"], ["Golden eagle","Aquila chrysaetos","B"],
 ["Arboreal salamander","Aneides lugubris","A"], ["California red-legged frog","Rana draytonii","A"],
 ["Western rattlesnake","Crotalus oreganus","R"], ["Valley oak","Quercus lobata","P"],
 ["Toyon","Heteromeles arbutifolia","P"], ["California poppy","Eschscholzia californica","P"],
 ["Bigberry manzanita","Arctostaphylos glauca","P"],
]
EXTRA["NE13"] = [
 ["Coyote","Canis latrans","M"], ["Ringtail","Bassariscus astutus","M"],
 ["Pronghorn","Antilocapra americana","M"], ["Black-tailed jackrabbit","Lepus californicus","M"],
 ["Javelina","Dicotyles tajacu","M"], ["Pallid bat","Antrozous pallidus","M"],
 ["Cactus wren","Campylorhynchus brunneicapillus","B"], ["Elf owl","Micrathene whitneyi","B"],
 ["Costa's hummingbird","Calypte costae","B"], ["Gambel's quail","Callipepla gambelii","B"],
 ["Western diamondback","Crotalus atrox","R"], ["Chuckwalla","Sauromalus ater","R"],
 ["Horned lizard","Phrynosoma platyrhinos","R"], ["Ocotillo","Fouquieria splendens","P"],
 ["Barrel cactus","Ferocactus wislizeni","P"], ["Big sagebrush","Artemisia tridentata","P"],
 ["Prickly pear","Opuntia engelmannii","P"],
]
EXTRA["OC01"] = [
 ["Hawaiian hoary bat","Lasiurus semotus","M"], ["Fiji flying fox","Mirimiri acrodonta","M"],
 ["Nēnē / Hawaiian goose","Branta sandvicensis","B"], ["Hawaiian hawk","Buteo solitarius","B"],
 ["Palila","Loxioides bailleui","B"], ["Kauai 'elepaio","Chasiempis sclateri","B"],
 ["Orange dove","Ptilinopus victor","B"], ["Kadavu musk parrot","Prosopeia splendens","B"],
 ["Tooth-billed pigeon","Didunculus strigirostris","B"], ["Fiji crested iguana","Brachylophus vitiensis","R"],
 ["Pacific boa","Candoia bibroni","R"], ["Kāhuli tree snail","Achatinella mustelina","I"],
 ["Kamehameha butterfly","Vanessa tameamea","I"], ["Koa","Acacia koa","P"],
 ["Hala / screwpine","Pandanus tectorius","P"], ["Tree fern","Cibotium glaucum","P"],
]

EXTRA["NO01"] = [
 ["Puma","Puma concolor","M"], ["Ocelot","Leopardus pardalis","M"],
 ["Tapir","Tapirus terrestris","M"], ["White-lipped peccary","Tayassu pecari","M"],
 ["Red howler monkey","Alouatta seniculus","M"], ["Spider monkey","Ateles belzebuth","M"],
 ["Pygmy marmoset","Cebuella pygmaea","M"], ["Kinkajou","Potos flavus","M"],
 ["Giant anteater","Myrmecophaga tridactyla","M"], ["Toco toucan","Ramphastos toco","B"],
 ["Cock-of-the-rock","Rupicola peruvianus","B"], ["Umbrellabird","Cephalopterus ornatus","B"],
 ["Sunbittern","Eurypyga helias","B"], ["Emerald tree boa","Corallus caninus","R"],
 ["Black caiman","Melanosuchus niger","R"], ["Matamata turtle","Chelus fimbriata","R"],
 ["Glass frog","Hyalinobatrachium valerioi","A"], ["Arapaima","Arapaima gigas","F"],
 ["Bullet ant","Paraponera clavata","I"], ["Kapok tree","Ceiba pentandra","P"],
 ["Rubber tree","Hevea brasiliensis","P"],
]
EXTRA["NO02"] = [
 ["Puma","Puma concolor","M"], ["Ocelot","Leopardus pardalis","M"],
 ["Six-banded armadillo","Euphractus sexcinctus","M"], ["Collared peccary","Dicotyles tajacu","M"],
 ["Grey brocket deer","Mazama gouazoubira","M"], ["Blue-fronted amazon","Amazona aestiva","B"],
 ["Red-legged seriema","Cariama cristata","B"], ["White-naped jay","Cyanocorax cyanopogon","B"],
 ["Caatinga cacholote","Pseudoseisura cristata","B"], ["Boa constrictor","Boa constrictor","R"],
 ["Tegu lizard","Salvator merianae","R"], ["Umbu tree","Spondias tuberosa","P"],
 ["Mandacaru cactus","Cereus jamacaru","P"], ["Carnauba palm","Copernicia prunifera","P"],
]
EXTRA["NO03"] = [
 ["Puma","Puma concolor","M"], ["Margay","Leopardus wiedii","M"],
 ["Mexican grey squirrel","Sciurus aureogaster","M"], ["Hispaniolan hutia","Plagiodontia aedium","M"],
 ["Azure-rumped tanager","Poecilostreptus cabanisi","B"], ["Highland guan","Penelopina nigra","B"],
 ["Golden-cheeked warbler","Setophaga chrysoparia","B"], ["Ridgway's hawk","Buteo ridgwayi","B"],
 ["Rhinoceros iguana","Cyclura cornuta","R"], ["Hispaniolan boa","Chilabothrus striatus","R"],
 ["Ocote pine","Pinus oocarpa","P"], ["Hispaniolan pine","Pinus occidentalis","P"],
 ["Sweetgum","Liquidambar styraciflua","P"],
]
EXTRA["NO04"] = [
 ["Guiña / kodkod","Leopardus guigna","M"], ["Culpeo fox","Lycalopex culpaeus","M"],
 ["Southern pudú","Pudu puda","M"], ["Monito del monte","Dromiciops gliroides","M"],
 ["Marine otter","Lontra felina","M"], ["Chucao tapaculo","Scelorchilus rubecula","B"],
 ["Des Murs's wiretail","Sylviorthorhynchus desmursii","B"], ["Slender-billed parakeet","Enicognathus leptorhynchus","B"],
 ["Austral pygmy owl","Glaucidium nana","B"], ["Chilean tree frog","Batrachyla taeniata","A"],
 ["Coigüe","Nothofagus dombeyi","P"], ["Lenga beech","Nothofagus pumilio","P"],
 ["Chilean bellflower","Lapageria rosea","P"], ["Nalca","Gunnera tinctoria","P"],
]
EXTRA["NO07"] = [
 ["Puma","Puma concolor","M"], ["Jaguar","Panthera onca","M"],
 ["Marsh deer","Blastocerus dichotomus","M"], ["South American tapir","Tapirus terrestris","M"],
 ["Six-banded armadillo","Euphractus sexcinctus","M"], ["Crab-eating fox","Cerdocyon thous","M"],
 ["Red-legged seriema","Cariama cristata","B"], ["Toco toucan","Ramphastos toco","B"],
 ["Hyacinth macaw","Anodorhynchus hyacinthinus","B"], ["Burrowing owl","Athene cunicularia","B"],
 ["Yellow anaconda","Eunectes notaeus","R"], ["Tegu lizard","Salvator merianae","R"],
 ["Leafcutter ant","Atta laevigata","I"], ["Buriti palm","Mauritia flexuosa","P"],
 ["Ipê tree","Handroanthus impetiginosus","P"],
]
EXTRA["NO08"] = [
 ["Culpeo fox","Lycalopex culpaeus","M"], ["Geoffroy's cat","Leopardus geoffroyi","M"],
 ["Southern viscacha","Lagidium viscacia","M"], ["Big hairy armadillo","Chaetophractus villosus","M"],
 ["Tuco-tuco","Ctenomys magellanicus","M"], ["Burrowing owl","Athene cunicularia","B"],
 ["Upland goose","Chloephaga picta","B"], ["Long-tailed meadowlark","Leistes loyca","B"],
 ["Austral thrush","Turdus falcklandii","B"], ["Patagonian lancehead","Bothrops ammodytoides","R"],
 ["Neuquén gecko","Homonota darwinii","R"], ["Neneo shrub","Mulinum spinosum","P"],
 ["Pampas grass","Cortaderia selloana","P"],
]
EXTRA["NO09"] = [
 ["Giant otter","Pteronura brasiliensis","M"], ["Marsh deer","Blastocerus dichotomus","M"],
 ["South American tapir","Tapirus terrestris","M"], ["Giant anteater","Myrmecophaga tridactyla","M"],
 ["Snail kite","Rostrhamus sociabilis","B"], ["Limpkin","Aramus guarauna","B"],
 ["Wood stork","Mycteria americana","B"], ["Anhinga","Anhinga anhinga","B"],
 ["Sunbittern","Eurypyga helias","B"], ["Green anaconda","Eunectes murinus","R"],
 ["Golden tegu","Tupinambis teguixin","R"], ["Piranha","Pygocentrus nattereri","F"],
 ["Pacu","Piaractus mesopotamicus","F"], ["Water hyacinth","Pontederia crassipes","P"],
 ["Giant water lily","Victoria amazonica","P"],
]
EXTRA["NO10"] = [
 ["Guanaco","Lama guanicoe","M"], ["Culpeo fox","Lycalopex culpaeus","M"],
 ["Andean cat","Leopardus jacobita","M"], ["Chinchilla","Chinchilla chinchilla","M"],
 ["Northern viscacha","Lagidium peruanum","M"], ["Andean fox","Lycalopex culpaeus","M"],
 ["Andean goose","Oressochen melanopterus","B"], ["Puna ibis","Plegadis ridgwayi","B"],
 ["Giant coot","Fulica gigantea","B"], ["James's flamingo","Phoenicoparrus jamesi","B"],
 ["Diademed sandpiper-plover","Phegornis mitchellii","B"], ["Andean toad","Rhinella spinulosa","A"],
 ["Yareta","Azorella compacta","P"], ["Polylepis","Polylepis tarapacana","P"],
 ["Ichu grass","Jarava ichu","P"],
]
EXTRA["NO12"] = [
 ["Culpeo fox","Lycalopex culpaeus","M"], ["Chilean myotis","Myotis chiloensis","M"],
 ["Long-tailed pygmy rice rat","Oligoryzomys longicaudatus","M"], ["Moustached turca","Pteroptochos megapodius","B"],
 ["Chilean tinamou","Nothoprocta perdicaria","B"], ["Giant hummingbird","Patagona gigas","B"],
 ["Chilean four-eyed frog","Pleurodema thaul","A"], ["Chilean palm weevil","Rhinostomus barbirostris","I"],
 ["Espino","Vachellia caven","P"], ["Litre","Lithraea caustica","P"],
 ["Chagual","Puya chilensis","P"],
]
EXTRA["NO13"] = [
 ["Sea lion","Otaria flavescens","M"], ["Culpeo fox","Lycalopex culpaeus","M"],
 ["Guanaco","Lama guanicoe","M"], ["Vicuña","Vicugna vicugna","M"],
 ["Peruvian booby","Sula variegata","B"], ["Guanay cormorant","Leucocarbo bougainvillii","B"],
 ["Inca tern","Larosterna inca","B"], ["Grey gull","Leucophaeus modestus","B"],
 ["Galápagos land iguana","Conolophus subcristatus","R"], ["Lava lizard","Microlophus albemarlensis","R"],
 ["Atacama desert lizard","Liolaemus atacamensis","R"], ["Desert bloom","Cistanthe longiscapa","P"],
 ["Prickly pear","Opuntia echios","P"], ["Tamarugo","Strombocarpa tamarugo","P"],
]
EXTRA["NO14"] = [
 ["Neotropical otter","Lontra longicaudis","M"], ["Silky anteater","Cyclopes didactylus","M"],
 ["Mangrove howler","Alouatta palliata","M"], ["Bottlenose dolphin","Tursiops truncatus","M"],
 ["Roseate spoonbill","Platalea ajaja","B"], ["Scarlet ibis","Eudocimus ruber","B"],
 ["Mangrove cuckoo","Coccyzus minor","B"], ["Reddish egret","Egretta rufescens","B"],
 ["Green turtle","Chelonia mydas","R"], ["Spectacled caiman","Caiman crocodilus","R"],
 ["Mangrove tree crab","Aratus pisonii","I"], ["Black mangrove","Avicennia germinans","P"],
 ["White mangrove","Laguncularia racemosa","P"],
]
EXTRA["PA01"] = [
 ["Clouded leopard","Neofelis nebulosa","M"], ["Chinese muntjac","Muntiacus reevesi","M"],
 ["Masked palm civet","Paguma larvata","M"], ["Père David's rock squirrel","Sciurotamias davidianus","M"],
 ["Temminck's tragopan","Tragopan temminckii","B"], ["Golden pheasant","Chrysolophus pictus","B"],
 ["Red-billed leiothrix","Leiothrix lutea","B"], ["Chinese bamboo partridge","Bambusicola thoracicus","B"],
 ["Chinese crocodile lizard","Shinisaurus crocodilurus","R"], ["Emei moustache toad","Leptobrachium boringii","A"],
 ["Ginkgo","Ginkgo biloba","P"], ["Dawn redwood","Metasequoia glyptostroboides","P"],
 ["Moso bamboo","Phyllostachys edulis","P"],
]
EXTRA["PA06"] = [
 ["Grey wolf","Canis lupus","M"], ["Wolverine","Gulo gulo","M"],
 ["Siberian flying squirrel","Pteromys volans","M"], ["Mountain hare","Lepus timidus","M"],
 ["Eurasian beaver","Castor fiber","M"], ["Elk / wapiti","Cervus canadensis sibiricus","M"],
 ["Hazel grouse","Tetrastes bonasia","B"], ["Black grouse","Lyrurus tetrix","B"],
 ["Three-toed woodpecker","Picoides tridactylus","B"], ["Pine grosbeak","Pinicola enucleator","B"],
 ["Waxwing","Bombycilla garrulus","B"], ["Siberian salamander","Salamandrella keyserlingii","A"],
 ["Dahurian larch","Larix gmelinii","P"], ["Siberian pine","Pinus sibirica","P"],
 ["Downy birch","Betula pubescens","P"], ["Cloudberry","Rubus chamaemorus","P"],
]
EXTRA["PA10"] = [
 ["Tibetan wild ass","Equus kiang","M"], ["Tibetan gazelle","Procapra picticaudata","M"],
 ["Argali","Ovis ammon","M"], ["Siberian ibex","Capra sibirica","M"],
 ["Tibetan fox","Vulpes ferrilata","M"], ["Pallas's cat","Otocolobus manul","M"],
 ["Plateau pika","Ochotona curzoniae","M"], ["Tibetan snowcock","Tetraogallus tibetanus","B"],
 ["Himalayan griffon","Gyps himalayensis","B"], ["Ground tit","Pseudopodoces humilis","B"],
 ["Ibisbill","Ibidorhyncha struthersii","B"], ["Saussurea","Saussurea medusa","P"],
 ["Snow lotus","Saussurea laniceps","P"], ["Stipa steppe grass","Stipa purpurea","P"],
]
EXTRA["PA11"] = [
 ["Muskox","Ovibos moschatus","M"], ["Wolverine","Gulo gulo","M"],
 ["Arctic ground squirrel","Urocitellus parryii","M"], ["Mountain hare","Lepus timidus","M"],
 ["Gyrfalcon","Falco rusticolus","B"], ["Rough-legged buzzard","Buteo lagopus","B"],
 ["Willow ptarmigan","Lagopus lagopus","B"], ["Bewick's swan","Cygnus columbianus bewickii","B"],
 ["Sabine's gull","Xema sabini","B"], ["Long-tailed skua","Stercorarius longicaudus","B"],
 ["Arctic bumblebee","Bombus polaris","I"], ["Arctic poppy","Papaver radicatum","P"],
 ["Purple saxifrage","Saxifraga oppositifolia","P"], ["Cotton grass","Eriophorum vaginatum","P"],
]
EXTRA["PA12"] = [
 ["Wild boar","Sus scrofa","M"], ["Red fox","Vulpes vulpes","M"],
 ["Egyptian mongoose","Herpestes ichneumon","M"], ["European genet","Genetta genetta","M"],
 ["Bonelli's eagle","Aquila fasciata","B"], ["Eleonora's falcon","Falco eleonorae","B"],
 ["European roller","Coracias garrulus","B"], ["Hoopoe","Upupa epops","B"],
 ["Sardinian warbler","Curruca melanocephala","B"], ["Montpellier snake","Malpolon monspessulanus","R"],
 ["Fire salamander","Salamandra salamandra","A"], ["Holm oak","Quercus ilex","P"],
 ["Kermes oak","Quercus coccifera","P"], ["Rosemary","Salvia rosmarinus","P"],
 ["Stone pine","Pinus pinea","P"],
]
# --- variants ---
EXTRA["PA04@0"] = [
 ["Sika deer","Cervus nippon","M"], ["Siberian musk deer","Moschus moschiferus","M"],
 ["Raccoon dog","Nyctereutes procyonoides","M"], ["Siberian weasel","Mustela sibirica","M"],
 ["Steller's sea eagle","Haliaeetus pelagicus","B"], ["Japanese serow","Capricornis crispus","M"],
 ["Copper pheasant","Syrmaticus soemmerringii","B"], ["Fairy pitta","Pitta nympha","B"],
 ["Japanese giant salamander","Andrias japonicus","A"], ["Mongolian oak","Quercus mongolica","P"],
 ["Japanese cedar","Cryptomeria japonica","P"],
]
EXTRA["PA05@0"] = [
 ["Chinese red panda","Ailurus styani","M"], ["Snow leopard","Panthera uncia","M"],
 ["Asiatic black bear","Ursus thibetanus","M"], ["Golden takin","Budorcas taxicolor bedfordi","M"],
 ["Temminck's tragopan","Tragopan temminckii","B"], ["Lady Amherst's pheasant","Chrysolophus amherstiae","B"],
 ["Firethroat","Calliope pectardens","B"], ["Chinese hemlock","Tsuga chinensis","P"],
 ["Handkerchief tree","Davidia involucrata","P"], ["Chinese fir","Cunninghamia lanceolata","P"],
]
EXTRA["PA08@0"] = [
 ["Argali","Ovis ammon","M"], ["Goitered gazelle","Gazella subgutturosa","M"],
 ["Grey wolf","Canis lupus chanco","M"], ["Tolai hare","Lepus tolai","M"],
 ["Cinereous vulture","Aegypius monachus","B"], ["Upland buzzard","Buteo hemilasius","B"],
 ["Mongolian lark","Melanocorypha mongolica","B"], ["Pallas's sandgrouse","Syrrhaptes paradoxus","B"],
 ["Feather grass","Stipa grandis","P"], ["Leymus grass","Leymus chinensis","P"],
]
EXTRA["PA13@0"] = [
 ["Snow leopard","Panthera uncia","M"], ["Marbled polecat","Vormela peregusna","M"],
 ["Corsac fox","Vulpes corsac","M"], ["Tolai hare","Lepus tolai","M"],
 ["Mongolian gazelle","Procapra gutturosa","M"], ["Pallas's sandgrouse","Syrrhaptes paradoxus","B"],
 ["Saxaul sparrow","Passer ammodendri","B"], ["Central Asian pit viper","Gloydius halys","R"],
 ["Tamarisk","Tamarix ramosissima","P"], ["Desert poplar","Populus euphratica","P"],
]
EXTRA["PA09@0"] = [
 ["Golden jackal","Canis aureus","M"], ["Jungle cat","Felis chaus","M"],
 ["Egyptian mongoose","Herpestes ichneumon","M"], ["Purple swamphen","Porphyrio porphyrio","B"],
 ["Squacco heron","Ardeola ralloides","B"], ["Pygmy cormorant","Microcarbo pygmaeus","B"],
 ["Nile softshell turtle","Trionyx triunguis","R"], ["Papyrus sedge","Cyperus papyrus","P"],
 ["Reedmace","Typha domingensis","P"],
]
EXTRA["IN01@0"] = [
 ["Indian giant squirrel","Ratufa indica","M"], ["Nilgiri langur","Semnopithecus johnii","M"],
 ["Dhole","Cuon alpinus","M"], ["Brown palm civet","Paradoxurus jerdoni","M"],
 ["Malabar grey hornbill","Ocyceros griseus","B"], ["Sri Lanka blue magpie","Urocissa ornata","B"],
 ["Nilgiri flycatcher","Eumyias albicaudatus","B"], ["Malabar pit viper","Craspedocephalus malabaricus","R"],
 ["Sri Lankan junglefowl","Gallus lafayettii","B"], ["Wild nutmeg","Myristica malabarica","P"],
]
EXTRA["NO01@0"] = [
 ["Ocelot","Leopardus pardalis","M"], ["Bush dog","Speothos venaticus","M"],
 ["Northern muriqui","Brachyteles hyacinthinus","M"], ["Black lion tamarin","Leontopithecus chrysopygus","M"],
 ["Bare-throated bellbird","Procnias nudicollis","B"], ["Black-fronted piping guan","Pipile jacutinga","B"],
 ["Saffron toucanet","Pteroglossus bailloni","B"], ["Golden lancehead","Bothrops insularis","R"],
 ["Brazilian tree fern","Dicksonia sellowiana","P"], ["Paraná pine","Araucaria angustifolia","P"],
]
EXTRA["NO02@0"] = [
 ["Ocelot","Leopardus pardalis","M"], ["Coati","Nasua narica","M"],
 ["Mexican howler monkey","Alouatta palliata mexicana","M"], ["Lilac-crowned parrot","Amazona finschi","B"],
 ["Citreoline trogon","Trogon citreolus","B"], ["West Mexican chachalaca","Ortalis poliocephala","B"],
 ["Black iguana","Ctenosaura similis","R"], ["Mexican vine snake","Oxybelis aeneus","R"],
 ["Morning glory tree","Ipomoea arborescens","P"], ["Cardón cactus","Pachycereus pecten-aboriginum","P"],
]
EXTRA["AU01@0"] = [
 ["Sulawesi palm civet","Macrogalidia musschenbroekii","M"], ["Dwarf cuscus","Strigocuscus celebensis","M"],
 ["Sulawesi warty pig","Sus celebensis","M"], ["Purple-winged roller","Coracias temminckii","B"],
 ["Sulawesi hornbill","Rhabdotorrhinus exarhatus","B"], ["Red-knobbed hornbill","Rhyticeros cassidix","B"],
 ["Sulawesi masked owl","Tyto rosenbergii","B"], ["Sulawesi lined gecko","Gekko fasciatus","R"],
 ["Ebony","Diospyros celebica","P"], ["Agathis","Agathis dammara","P"],
]

EXTRA["PA04"] = [
 ["Red fox","Vulpes vulpes","M"], ["Pine marten","Martes martes","M"],
 ["Eurasian beaver","Castor fiber","M"], ["Red squirrel","Sciurus vulgaris","M"],
 ["European hedgehog","Erinaceus europaeus","M"], ["Roe deer","Capreolus capreolus","M"],
 ["Tawny owl","Strix aluco","B"], ["Eurasian jay","Garrulus glandarius","B"],
 ["Common nightingale","Luscinia megarhynchos","B"], ["Middle spotted woodpecker","Dendrocoptes medius","B"],
 ["European adder","Vipera berus","R"], ["Great crested newt","Triturus cristatus","A"],
 ["Stag beetle","Lucanus cervus","I"], ["Small-leaved lime","Tilia cordata","P"],
 ["Hornbeam","Carpinus betulus","P"], ["Wild cherry","Prunus avium","P"],
]
EXTRA["PA05"] = [
 ["Chamois","Rupicapra rupicapra","M"], ["Alpine marmot","Marmota marmota","M"],
 ["Red deer","Cervus elaphus","M"], ["Pine marten","Martes martes","M"],
 ["Snow vole","Chionomys nivalis","M"], ["Three-toed woodpecker","Picoides tridactylus","B"],
 ["Nutcracker","Nucifraga caryocatactes","B"], ["Alpine chough","Pyrrhocorax graculus","B"],
 ["Ring ouzel","Turdus torquatus","B"], ["Alpine salamander","Salamandra atra","A"],
 ["Apollo butterfly","Parnassius apollo","I"], ["Silver fir","Abies alba","P"],
 ["Siberian larch","Larix sibirica","P"], ["Alpenrose","Rhododendron ferrugineum","P"],
 ["Edelweiss","Leontopodium nivale","P"],
]
EXTRA["PA08"] = [
 ["Grey wolf","Canis lupus","M"], ["Red fox","Vulpes vulpes","M"],
 ["European ground squirrel","Spermophilus citellus","M"], ["Steppe polecat","Mustela eversmanii","M"],
 ["Great jerboa","Allactaga major","M"], ["Little bustard","Tetrax tetrax","B"],
 ["Pallid harrier","Circus macrourus","B"], ["Red-footed falcon","Falco vespertinus","B"],
 ["Calandra lark","Melanocorypha calandra","B"], ["Rose-coloured starling","Pastor roseus","B"],
 ["Steppe runner","Eremias arguta","R"], ["Steppe tortoise","Testudo horsfieldii","R"],
 ["Fescue","Festuca valesiaca","P"], ["Steppe peony","Paeonia tenuifolia","P"],
]
EXTRA["PA09"] = [
 ["Eurasian otter","Lutra lutra","M"], ["Raccoon dog","Nyctereutes procyonoides","M"],
 ["Water deer","Hydropotes inermis","M"], ["Hooded crane","Grus monacha","B"],
 ["White-naped crane","Antigone vipio","B"], ["Baikal teal","Sibirionetta formosa","B"],
 ["Swan goose","Anser cygnoides","B"], ["Amur ratsnake","Elaphe schrenckii","R"],
 ["Manchurian sedge","Carex schmidtii","P"], ["Reed canary grass","Phalaris arundinacea","P"],
]
EXTRA["PA13"] = [
 ["Striped hyena","Hyaena hyaena","M"], ["Rüppell's fox","Vulpes rueppellii","M"],
 ["Barbary sheep","Ammotragus lervia","M"], ["Slender-horned gazelle","Gazella leptoceros","M"],
 ["Jerboa","Jaculus jaculus","M"], ["Sand gazelle","Gazella marica","M"],
 ["Cream-coloured courser","Cursorius cursor","B"], ["Hoopoe lark","Alaemon alaudipes","B"],
 ["Lanner falcon","Falco biarmicus","B"], ["Egyptian vulture","Neophron percnopterus","B"],
 ["Horned viper","Cerastes cerastes","R"], ["Fringe-toed lizard","Acanthodactylus scutellatus","R"],
 ["Deathstalker scorpion","Leiurus quinquestriatus","I"], ["Acacia","Vachellia tortilis","P"],
 ["Desert gourd","Citrullus colocynthis","P"],
]
