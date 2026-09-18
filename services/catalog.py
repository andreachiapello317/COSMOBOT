"""Identificatori (nomi e Q-id Wikidata). Non sono misure astronomiche."""

from __future__ import annotations

PLANETS: tuple[dict[str, str], ...] = (
    {"id": "sun", "qid": "Q525", "en": "Sun", "it": "Sole", "wiki": "Sun", "wiki_it": "Sole_(astronomia)", "emoji": "☀️"},
    {"id": "mercury", "qid": "Q308", "en": "Mercury", "it": "Mercurio", "wiki": "Mercury_(planet)", "wiki_it": "Mercurio_(astronomia)", "emoji": "🪨"},
    {"id": "venus", "qid": "Q313", "en": "Venus", "it": "Venere", "wiki": "Venus", "wiki_it": "Venere_(astronomia)", "emoji": "🌕"},
    {"id": "earth", "qid": "Q2", "en": "Earth", "it": "Terra", "wiki": "Earth", "wiki_it": "Terra", "emoji": "🌍"},
    {"id": "mars", "qid": "Q111", "en": "Mars", "it": "Marte", "wiki": "Mars", "wiki_it": "Marte_(astronomia)", "emoji": "🔴"},
    {"id": "jupiter", "qid": "Q319", "en": "Jupiter", "it": "Giove", "wiki": "Jupiter", "wiki_it": "Giove_(astronomia)", "emoji": "🟠"},
    {"id": "saturn", "qid": "Q193", "en": "Saturn", "it": "Saturno", "wiki": "Saturn", "wiki_it": "Saturno_(astronomia)", "emoji": "🪐"},
    {"id": "uranus", "qid": "Q324", "en": "Uranus", "it": "Urano", "wiki": "Uranus", "wiki_it": "Urano_(astronomia)", "emoji": "🌀"},
    {"id": "neptune", "qid": "Q332", "en": "Neptune", "it": "Nettuno", "wiki": "Neptune", "wiki_it": "Nettuno_(astronomia)", "emoji": "🔵"},
)

MOONS: tuple[dict[str, str], ...] = (
    {"id": "moon", "qid": "Q405", "en": "Moon", "it": "Luna", "wiki": "Moon", "emoji": "🌙"},
    {"id": "io", "qid": "Q3123", "en": "Io", "it": "Io", "wiki": "Io_(moon)", "emoji": "🟠"},
    {"id": "europa", "qid": "Q3143", "en": "Europa", "it": "Europa", "wiki": "Europa_(moon)", "emoji": "❄️"},
    {"id": "ganymede", "qid": "Q3169", "en": "Ganymede", "it": "Ganimede", "wiki": "Ganymede_(moon)", "emoji": "🟤"},
    {"id": "callisto", "qid": "Q3134", "en": "Callisto", "it": "Callisto", "wiki": "Callisto_(moon)", "emoji": "⚫"},
    {"id": "titan", "qid": "Q2565", "en": "Titan", "it": "Titano", "wiki": "Titan_(moon)", "emoji": "🟠"},
    {"id": "enceladus", "qid": "Q15037", "en": "Enceladus", "it": "Encelado", "wiki": "Enceladus", "emoji": "⚪"},
    {"id": "triton", "qid": "Q3359", "en": "Triton", "it": "Tritone", "wiki": "Triton_(moon)", "emoji": "🧊"},
)

GALAXIES: tuple[dict[str, str], ...] = (
    {"id": "mw", "qid": "Q321", "en": "Milky Way", "it": "Via Lattea", "wiki": "Milky_Way", "emoji": "🌌"},
    {"id": "and", "qid": "Q2469", "en": "Andromeda Galaxy", "it": "Andromeda", "wiki": "Andromeda_Galaxy", "emoji": "🌀"},
    {"id": "tri", "qid": "Q2463", "en": "Triangulum Galaxy", "it": "Triangolo", "wiki": "Triangulum_Galaxy", "emoji": "🔺"},
    {"id": "m51", "qid": "Q14380", "en": "Whirlpool Galaxy", "it": "Vortice", "wiki": "Whirlpool_Galaxy", "emoji": "💫"},
    {"id": "m104", "qid": "Q13967", "en": "Sombrero Galaxy", "it": "Sombrero", "wiki": "Sombrero_Galaxy", "emoji": "🎩"},
    {"id": "lmc", "qid": "Q76270", "en": "Large Magellanic Cloud", "it": "Grande Nube di Magellano", "wiki": "Large_Magellanic_Cloud", "emoji": "☁️"},
)

BLACK_HOLES: tuple[dict[str, str], ...] = (
    {"id": "sgr", "qid": "Q14579", "en": "Sagittarius A*", "it": "Sagittarius A*", "wiki": "Sagittarius_A*", "emoji": "🕳️"},
    {"id": "m87", "qid": "Q199738", "en": "Messier 87", "it": "M87*", "wiki": "Messier_87", "emoji": "🕳️"},
    {"id": "cyg", "qid": "Q83373", "en": "Cygnus X-1", "it": "Cygnus X-1", "wiki": "Cygnus_X-1", "emoji": "🕳️"},
)

MISSIONS: tuple[dict[str, str], ...] = (
    {"id": "artemis", "en": "Artemis program", "it": "Artemis", "wiki": "Artemis_program", "emoji": "🌙"},
    {"id": "jwst", "en": "James Webb Space Telescope", "it": "James Webb", "wiki": "James_Webb_Space_Telescope", "emoji": "🔭"},
    {"id": "clipper", "en": "Europa Clipper", "it": "Europa Clipper", "wiki": "Europa_Clipper", "emoji": "❄️"},
    {"id": "juice", "en": "Jupiter Icy Moons Explorer", "it": "JUICE", "wiki": "Jupiter_Icy_Moons_Explorer", "emoji": "🛰️"},
    {"id": "voyager", "en": "Voyager program", "it": "Voyager", "wiki": "Voyager_program", "emoji": "🚀"},
    {"id": "nh", "en": "New Horizons", "it": "New Horizons", "wiki": "New_Horizons", "emoji": "❄️"},
    {"id": "cassini", "en": "Cassini–Huygens", "it": "Cassini", "wiki": "Cassini–Huygens", "emoji": "🪐"},
    {"id": "juno", "en": "Juno (spacecraft)", "it": "Juno", "wiki": "Juno_(spacecraft)", "emoji": "🟠"},
    {"id": "hubble", "en": "Hubble Space Telescope", "it": "Hubble", "wiki": "Hubble_Space_Telescope", "emoji": "👁️"},
    {"id": "perseverance", "en": "Perseverance (rover)", "it": "Perseverance", "wiki": "Perseverance_(rover)", "emoji": "🔴"},
    {"id": "galileo", "en": "Galileo (spacecraft)", "it": "Galileo", "wiki": "Galileo_(spacecraft)", "emoji": "🟠"},
    {"id": "osiris", "en": "OSIRIS-REx", "it": "OSIRIS-REx", "wiki": "OSIRIS-REx", "emoji": "🪨"},
    {"id": "hayabusa", "en": "Hayabusa", "it": "Hayabusa", "wiki": "Hayabusa_(spacecraft)", "emoji": "🪨"},
    {"id": "rosetta", "en": "Rosetta (spacecraft)", "it": "Rosetta", "wiki": "Rosetta_(spacecraft)", "emoji": "☄️"},
    {"id": "mro", "en": "Mars Reconnaissance Orbiter", "it": "MRO", "wiki": "Mars_Reconnaissance_Orbiter", "emoji": "🔴"},
    {"id": "curiosity", "en": "Curiosity (rover)", "it": "Curiosity", "wiki": "Curiosity_(rover)", "emoji": "🔴"},
)

ASTRONAUTS: tuple[dict[str, str], ...] = (
    {"id": "gagarin", "en": "Yuri Gagarin", "it": "Jurij Gagarin", "wiki": "Yuri_Gagarin", "emoji": "👨‍🚀"},
    {"id": "armstrong", "en": "Neil Armstrong", "it": "Neil Armstrong", "wiki": "Neil_Armstrong", "emoji": "👨‍🚀"},
    {"id": "tereshkova", "en": "Valentina Tereshkova", "it": "Valentina Tereškova", "wiki": "Valentina_Tereshkova", "emoji": "👩‍🚀"},
    {"id": "ride", "en": "Sally Ride", "it": "Sally Ride", "wiki": "Sally_Ride", "emoji": "👩‍🚀"},
    {"id": "mcclain", "en": "Anne McClain", "it": "Anne McClain", "wiki": "Anne_McClain", "emoji": "👩‍🚀"},
)

LIFE_TOPICS: tuple[dict[str, str], ...] = (
    {"id": "search", "it": "Come cerchiamo la vita", "wiki": "Search_for_extraterrestrial_intelligence", "emoji": "🔬"},
    {"id": "ocean", "it": "Oceani sotto il ghiaccio", "wiki": "Europa_(moon)", "emoji": "🌊"},
    {"id": "exo", "it": "Esopianeti", "wiki": "Exoplanet", "emoji": "🪐"},
    {"id": "seti", "it": "SETI", "wiki": "SETI", "emoji": "📡"},
    {"id": "bio", "it": "Firme biologiche", "wiki": "Biosignature", "emoji": "🧫"},
    {"id": "micro", "it": "Estremofili", "wiki": "Extremophile", "emoji": "🦠"},
    {"id": "hz", "it": "Zona abitabile", "wiki": "Circumstellar_habitable_zone", "emoji": "🌍"},
    {"id": "org", "it": "Molecole organiche", "wiki": "Organic_compound", "emoji": "🧪"},
    {"id": "fermi", "it": "Paradosso di Fermi", "wiki": "Fermi_paradox", "emoji": "👽"},
    {"id": "rogue", "it": "Pianeti erranti", "wiki": "Rogue_planet", "emoji": "🌑"},
)

LEARN_TOPICS: tuple[dict[str, str], ...] = (
    {"id": "ss", "it": "Sistema Solare", "wiki": "Solar_System", "emoji": "☀️"},
    {"id": "stars", "it": "Stelle", "wiki": "Star", "emoji": "⭐"},
    {"id": "bh", "it": "Buchi neri", "wiki": "Black_hole", "emoji": "🕳️"},
    {"id": "gal", "it": "Galassie", "wiki": "Galaxy", "emoji": "🌌"},
    {"id": "mis", "it": "Missioni", "wiki": "Space_exploration", "emoji": "🚀"},
    {"id": "exo", "it": "Esopianeti", "wiki": "Exoplanet", "emoji": "👽"},
)

SATELLITES: tuple[dict[str, str], ...] = (
    {"id": "iss", "it": "Stazione Spaziale", "wiki": "International_Space_Station", "emoji": "🛰️"},
    {"id": "hubble", "it": "Hubble", "wiki": "Hubble_Space_Telescope", "emoji": "👁️"},
    {"id": "jwst", "it": "James Webb", "wiki": "James_Webb_Space_Telescope", "emoji": "🔭"},
    {"id": "chandra", "it": "Chandra", "wiki": "Chandra_X-ray_Observatory", "emoji": "📡"},
    {"id": "terra", "it": "Terra (EOS)", "wiki": "Terra_(satellite)", "emoji": "🌍"},
)

PROBES: tuple[dict[str, str], ...] = (
    {"id": "voyager", "it": "Voyager", "wiki": "Voyager_program", "emoji": "🚀"},
    {"id": "nh", "it": "New Horizons", "wiki": "New_Horizons", "emoji": "❄️"},
    {"id": "cassini", "it": "Cassini", "wiki": "Cassini–Huygens", "emoji": "🪐"},
    {"id": "juno", "it": "Juno", "wiki": "Juno_(spacecraft)", "emoji": "🟠"},
    {"id": "juice", "it": "JUICE", "wiki": "Jupiter_Icy_Moons_Explorer", "emoji": "🛰️"},
    {"id": "clipper", "it": "Europa Clipper", "wiki": "Europa_Clipper", "emoji": "❄️"},
)

RANDOM_OBJECTS: tuple[dict[str, str], ...] = (
    {"id": "orion", "it": "Nebulosa di Orione", "wiki": "Orion_Nebula", "emoji": "🌌"},
    {"id": "crab", "it": "Nebulosa del Granchio", "wiki": "Crab_Nebula", "emoji": "🦀"},
    {"id": "pleiades", "it": "Pleiadi", "wiki": "Pleiades", "emoji": "✨"},
    {"id": "and", "it": "Andromeda", "wiki": "Andromeda_Galaxy", "emoji": "🌀"},
    {"id": "betel", "it": "Betelgeuse", "wiki": "Betelgeuse", "emoji": "⭐"},
    {"id": "ring", "it": "Nebulosa Anello", "wiki": "Ring_Nebula", "emoji": "💍"},
    {"id": "pillars", "it": "Pilastri della Creazione", "wiki": "Pillars_of_Creation", "emoji": "🌫️"},
)

PLANET_EXPLORE_WIKI: dict[str, str] = {
    "mercury": "Exploration_of_Mercury",
    "venus": "Exploration_of_Venus",
    "earth": "Discovery_and_exploration_of_the_Solar_System",
    "mars": "Exploration_of_Mars",
    "jupiter": "Exploration_of_Jupiter",
    "saturn": "Exploration_of_Saturn",
    "uranus": "Exploration_of_Uranus",
    "neptune": "Exploration_of_Neptune",
}

DAILY_MISSIONS: tuple[dict[str, str | int], ...] = (
    {"id": "orion", "title": "Stasera trova Orione nel cielo.", "diff": 2, "mins": 10, "kind": "constellation", "hint": "Tre stelle in fila (la Cintura) sotto un rettangolo di spalle e piedi."},
    {"id": "moon", "title": "Osserva la Luna e nota la fase.", "diff": 1, "mins": 5, "kind": "moon", "hint": "Apri /luna, poi alzati e confronta con ciò che vedi."},
    {"id": "apod", "title": "Guarda l'APOD di oggi e leggi la didascalia.", "diff": 1, "mins": 5, "kind": "apod", "hint": "Tocca NASA APOD, poi torna qui e segna fatto."},
    {"id": "quiz", "title": "Completa un quiz (almeno una domanda).", "diff": 2, "mins": 5, "kind": "quiz", "hint": "Parti dal livello facile: le domande nascono da Wikipedia/Wikidata."},
    {"id": "planet", "title": "Scegli un pianeta e leggi la scheda.", "diff": 1, "mins": 8, "kind": "planet", "hint": "Apri /pianeta, poi un mondo. Masse e diametri arrivano da Wikidata."},
    {"id": "reading", "title": "Completa una lettura: tarocchi, I Ching o rune.", "diff": 2, "mins": 10, "kind": "reading", "hint": "Una sola, fatta per intero. È un rituale, non un dato astronomico."},
    {"id": "star", "title": "Impara una stella: apri /stelle.", "diff": 1, "mins": 5, "kind": "star", "hint": "Apri /stelle: casuale, del giorno o visibili ora. Poi segna fatto."},
    {"id": "exo", "title": "Scopri un esopianeta casuale.", "diff": 2, "mins": 6, "kind": "exo", "hint": "/esopianeta pesca dalla NASA Exoplanet Archive."},
)

QUIZ_LEVELS: tuple[tuple[str, str, str], ...] = (
    ("easy", "🟢 Facile", "Pianeti del Sistema Solare"),
    ("medium", "🟡 Medio", "Misure Wikidata"),
    ("hard", "🔴 Difficile", "Lune, galassie, missioni"),
    ("expert", "☠️ Esperto", "Esopianeti dall'archivio NASA"),
)

MIRROR_QUESTIONS: tuple[str, ...] = (
    "Cosa stai evitando di vedere chiaramente?",
    "Quale parte di te chiede più spazio, in questo periodo?",
    "Se potessi nominare la tua paura principale, come la chiameresti?",
    "Cosa torneresti a curare, se avessi una settimana più lenta?",
    "Quale verità piccola stai già sapendo, ma non hai detto ad alta voce?",
    "Dove stai usando la forza, e dove basterebbe l'attenzione?",
    "Che cosa, se lo lasciassi andare, ti renderebbe più leggero?",
)


DWARFS: tuple[dict[str, str], ...] = (
    {"id": "pluto", "qid": "Q339", "en": "Pluto", "it": "Plutone", "wiki": "Pluto", "emoji": "🧊"},
    {"id": "ceres", "qid": "Q596", "en": "Ceres", "it": "Cerere", "wiki": "Ceres_(dwarf_planet)", "emoji": "🪨"},
    {"id": "eris", "qid": "Q601", "en": "Eris", "it": "Eris", "wiki": "Eris_(dwarf_planet)", "emoji": "💜"},
    {"id": "haumea", "qid": "Q10756", "en": "Haumea", "it": "Haumea", "wiki": "Haumea", "emoji": "🥚"},
    {"id": "makemake", "qid": "Q10757", "en": "Makemake", "it": "Makemake", "wiki": "Makemake", "emoji": "🔴"},
)

COMETS: tuple[dict[str, str], ...] = (
    {"id": "halley", "qid": "Q23054", "en": "Halley's Comet", "it": "Halley", "wiki": "Halley's_Comet", "emoji": "☄️"},
    {"id": "encke", "qid": "Q14153", "en": "Comet Encke", "it": "Encke", "wiki": "Comet_Encke", "emoji": "☄️"},
    {"id": "67p", "qid": "Q13888", "en": "67P/Churyumov–Gerasimenko", "it": "67P", "wiki": "67P/Churyumov–Gerasimenko", "emoji": "🥔"},
    {"id": "halebopp", "qid": "Q14372", "en": "Comet Hale–Bopp", "it": "Hale-Bopp", "wiki": "Comet_Hale–Bopp", "emoji": "☄️"},
    {"id": "neowise", "qid": "Q85734766", "en": "C/2020 F3 (NEOWISE)", "it": "NEOWISE", "wiki": "C/2020_F3_(NEOWISE)", "emoji": "☄️"},
    {"id": "tsuchinshan", "qid": "Q123468937", "en": "C/2023 A3 (Tsuchinshan–ATLAS)", "it": "Tsuchinshan–ATLAS", "wiki": "C/2023_A3_(Tsuchinshan–ATLAS)", "emoji": "☄️"},
)

FAMOUS_ASTEROIDS: tuple[dict[str, str], ...] = (
    {"id": "vesta", "qid": "Q3030", "en": "4 Vesta", "it": "Vesta", "wiki": "4_Vesta", "emoji": "🪨"},
    {"id": "pallas", "qid": "Q3034", "en": "2 Pallas", "it": "Pallade", "wiki": "2_Pallas", "emoji": "🪨"},
    {"id": "hygiea", "qid": "Q3049", "en": "10 Hygiea", "it": "Igea", "wiki": "10_Hygiea", "emoji": "🪨"},
    {"id": "eros", "qid": "Q16711", "en": "433 Eros", "it": "Eros", "wiki": "433_Eros", "emoji": "🪨"},
    {"id": "bennu", "qid": "Q11518", "en": "101955 Bennu", "it": "Bennu", "wiki": "101955_Bennu", "emoji": "🪨"},
    {"id": "psyche", "qid": "Q59164", "en": "16 Psyche", "it": "Psyche", "wiki": "16_Psyche", "emoji": "🪨"},
    {"id": "itokawa", "qid": "Q147555", "en": "25143 Itokawa", "it": "Itokawa", "wiki": "25143_Itokawa", "emoji": "🪨"},
)

STARS: tuple[dict[str, str], ...] = (
    {"id": "sirius", "qid": "Q1290", "en": "Sirius", "it": "Sirio", "wiki": "Sirius", "emoji": "⭐"},
    {"id": "vega", "qid": "Q3427", "en": "Vega", "it": "Vega", "wiki": "Vega", "emoji": "⭐"},
    {"id": "betel", "qid": "Q12133", "en": "Betelgeuse", "it": "Betelgeuse", "wiki": "Betelgeuse", "emoji": "🔴"},
    {"id": "rigel", "qid": "Q105513", "en": "Rigel", "it": "Rigel", "wiki": "Rigel", "emoji": "🔵"},
    {"id": "polaris", "qid": "Q12980", "en": "Polaris", "it": "Stella Polare", "wiki": "Polaris", "emoji": "⭐"},
    {"id": "proxima", "qid": "Q14266", "en": "Proxima Centauri", "it": "Proxima Centauri", "wiki": "Proxima_Centauri", "emoji": "🔴"},
    {"id": "barnard", "qid": "Q12147", "en": "Barnard's Star", "it": "Stella di Barnard", "wiki": "Barnard's_Star", "emoji": "🔴"},
    {"id": "altair", "qid": "Q12975", "en": "Altair", "it": "Altair", "wiki": "Altair", "emoji": "⭐"},
    {"id": "capella", "qid": "Q12174", "en": "Capella", "it": "Capella", "wiki": "Capella", "emoji": "⭐"},
    {"id": "aldebaran", "qid": "Q12923", "en": "Aldebaran", "it": "Aldebaran", "wiki": "Aldebaran", "emoji": "🟠"},
    {"id": "antares", "qid": "Q5921", "en": "Antares", "it": "Antares", "wiki": "Antares", "emoji": "🔴"},
    {"id": "arcturus", "qid": "Q12982", "en": "Arcturus", "it": "Arcturo", "wiki": "Arcturus", "emoji": "🟠"},
    {"id": "deneb", "qid": "Q13094", "en": "Deneb", "it": "Deneb", "wiki": "Deneb", "emoji": "⭐"},
    {"id": "canopus", "qid": "Q911579", "en": "Canopus", "it": "Canopo", "wiki": "Canopus", "emoji": "⭐"},
    {"id": "procyon", "qid": "Q12169", "en": "Procyon", "it": "Procione", "wiki": "Procyon", "emoji": "⭐"},
    {"id": "spica", "qid": "Q12767", "en": "Spica", "it": "Spica", "wiki": "Spica", "emoji": "⭐"},
    {"id": "fomalhaut", "qid": "Q12163", "en": "Fomalhaut", "it": "Fomalhaut", "wiki": "Fomalhaut", "emoji": "⭐"},
    {"id": "polaris_a", "qid": "Q9971149", "en": "Sirius B", "it": "Sirio B", "wiki": "Sirius", "emoji": "⚪"},
)

STAR_TYPES: tuple[dict[str, str], ...] = (
    {"id": "rg", "it": "Giganti rosse", "wiki": "Red_giant", "emoji": "🔴"},
    {"id": "wd", "it": "Nane bianche", "wiki": "White_dwarf", "emoji": "⚪"},
    {"id": "ns", "it": "Stelle di neutroni", "wiki": "Neutron_star", "emoji": "💠"},
    {"id": "pu", "it": "Pulsar", "wiki": "Pulsar", "emoji": "📡"},
    {"id": "sn", "it": "Supernovae", "wiki": "Supernova", "emoji": "💥"},
    {"id": "bi", "it": "Stelle doppie", "wiki": "Binary_star", "emoji": "⭐"},
)

NEAR_STARS: tuple[str, ...] = ("proxima", "barnard")
GIANT_STARS: tuple[str, ...] = ("betel", "antares", "aldebaran", "arcturus")

CONSTELLATIONS: tuple[dict[str, str], ...] = (
    {"id": "ori", "qid": "Q10506", "en": "Orion", "it": "Orione", "wiki": "Orion_(constellation)", "emoji": "🏹"},
    {"id": "uma", "qid": "Q8918", "en": "Ursa Major", "it": "Orsa Maggiore", "wiki": "Ursa_Major", "emoji": "🐻"},
    {"id": "cas", "qid": "Q10448", "en": "Cassiopeia", "it": "Cassiopea", "wiki": "Cassiopeia_(constellation)", "emoji": "👑"},
    {"id": "cyg", "qid": "Q8921", "en": "Cygnus", "it": "Cigno", "wiki": "Cygnus_(constellation)", "emoji": "🦢"},
    {"id": "sco", "qid": "Q8860", "en": "Scorpius", "it": "Scorpione", "wiki": "Scorpius", "emoji": "🦂"},
    {"id": "leo", "qid": "Q8853", "en": "Leo", "it": "Leone", "wiki": "Leo_(constellation)", "emoji": "🦁"},
    {"id": "tau", "qid": "Q10570", "en": "Taurus", "it": "Toro", "wiki": "Taurus_(constellation)", "emoji": "🐂"},
    {"id": "gem", "qid": "Q8849", "en": "Gemini", "it": "Gemelli", "wiki": "Gemini_(constellation)", "emoji": "👯"},
    {"id": "sgr", "qid": "Q8866", "en": "Sagittarius", "it": "Sagittario", "wiki": "Sagittarius_(constellation)", "emoji": "🏹"},
    {"id": "and", "qid": "Q8891", "en": "Andromeda", "it": "Andromeda", "wiki": "Andromeda_(constellation)", "emoji": "👸"},
    {"id": "lyr", "qid": "Q10464", "en": "Lyra", "it": "Lira", "wiki": "Lyra", "emoji": "🎵"},
    {"id": "cru", "qid": "Q10578", "en": "Crux", "it": "Croce del Sud", "wiki": "Crux", "emoji": "✝️"},
    {"id": "umi", "qid": "Q8922", "en": "Ursa Minor", "it": "Orsa Minore", "wiki": "Ursa_Minor", "emoji": "⭐"},
    {"id": "aqr", "qid": "Q8843", "en": "Aquarius", "it": "Acquario", "wiki": "Aquarius_(constellation)", "emoji": "🏺"},
    {"id": "psc", "qid": "Q8678", "en": "Pisces", "it": "Pesci", "wiki": "Pisces_(constellation)", "emoji": "🐟"},
    {"id": "vir", "qid": "Q8842", "en": "Virgo", "it": "Vergine", "wiki": "Virgo_(constellation)", "emoji": "🌾"},
)

DEEP_SKY: tuple[dict[str, str], ...] = (
    {"id": "m31", "qid": "Q2469", "en": "Andromeda Galaxy", "it": "M31 Andromeda", "wiki": "Andromeda_Galaxy", "emoji": "🌀"},
    {"id": "m42", "qid": "Q14238", "en": "Orion Nebula", "it": "M42 Orione", "wiki": "Orion_Nebula", "emoji": "🌫️"},
    {"id": "m13", "qid": "Q14260", "en": "Messier 13", "it": "M13 Ercole", "wiki": "Messier_13", "emoji": "✨"},
    {"id": "m45", "qid": "Q24357", "en": "Pleiades", "it": "M45 Pleiadi", "wiki": "Pleiades", "emoji": "✨"},
    {"id": "m51", "qid": "Q14380", "en": "Whirlpool Galaxy", "it": "M51 Vortice", "wiki": "Whirlpool_Galaxy", "emoji": "💫"},
    {"id": "m57", "qid": "Q13875", "en": "Ring Nebula", "it": "M57 Anello", "wiki": "Ring_Nebula", "emoji": "💍"},
    {"id": "m1", "qid": "Q14860", "en": "Crab Nebula", "it": "M1 Granchio", "wiki": "Crab_Nebula", "emoji": "🦀"},
    {"id": "m87", "qid": "Q199738", "en": "Messier 87", "it": "M87", "wiki": "Messier_87", "emoji": "🕳️"},
    {"id": "ngc224", "qid": "Q2469", "en": "NGC 224", "it": "NGC 224", "wiki": "Andromeda_Galaxy", "emoji": "📘"},
    {"id": "3c273", "qid": "Q218419", "en": "3C 273", "it": "3C 273", "wiki": "3C_273", "emoji": "🔴"},
    {"id": "pillars", "qid": "Q23652", "en": "Pillars of Creation", "it": "Pilastri della Creazione", "wiki": "Pillars_of_Creation", "emoji": "🌫️"},
    {"id": "sn1987a", "qid": "Q404892", "en": "SN 1987A", "it": "SN 1987A", "wiki": "SN_1987A", "emoji": "💥"},
)


# Corpi del Sistema Solare toccati da una missione (solo collegamenti di catalogo).
MISSION_WORLDS: dict[str, tuple[tuple[str, str], ...]] = {
    "voyager": (("p", "jupiter"), ("p", "saturn"), ("p", "uranus"), ("p", "neptune")),
    "cassini": (("p", "saturn"), ("m", "titan"), ("m", "enceladus")),
    "juno": (("p", "jupiter"),),
    "galileo": (("p", "jupiter"), ("m", "io"), ("m", "europa"), ("m", "ganymede"), ("m", "callisto")),
    "nh": (("f", "pluto"),),
    "clipper": (("m", "europa"),),
    "juice": (("p", "jupiter"), ("m", "europa"), ("m", "ganymede"), ("m", "callisto")),
    "perseverance": (("p", "mars"),),
    "curiosity": (("p", "mars"),),
    "mro": (("p", "mars"),),
    "osiris": (("z", "bennu"),),
    "hayabusa": (("z", "itokawa"),),
    "rosetta": (("c", "67p"),),
}


def worlds_for_mission(mission_id: str) -> tuple[tuple[str, str], ...]:
    return MISSION_WORLDS.get(mission_id, ())


def missions_for_world(kind: str, item_id: str) -> tuple[str, ...]:
    found: list[str] = []
    for mid, targets in MISSION_WORLDS.items():
        if (kind, item_id) in targets:
            found.append(mid)
    return tuple(found)


def by_id(rows: tuple[dict[str, str], ...], item_id: str) -> dict[str, str] | None:
    for row in rows:
        if row["id"] == item_id:
            return row
    return None
