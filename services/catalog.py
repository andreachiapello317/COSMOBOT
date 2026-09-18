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
    {"id": "bio", "it": "Biosignature", "wiki": "Biosignature", "emoji": "🧫"},
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
    {"id": "star", "title": "Impara una stella: apri /stelle.", "diff": 1, "mins": 5, "kind": "star", "hint": "Una scheda NASA a caso, tradotta. Poi segna fatto."},
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


def by_id(rows: tuple[dict[str, str], ...], item_id: str) -> dict[str, str] | None:
    for row in rows:
        if row["id"] == item_id:
            return row
    return None
