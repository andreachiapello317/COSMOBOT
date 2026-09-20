"""Dati sulla Terra per NATURA: cataloghi Wikipedia + feed live. Niente geologia inventata."""

from __future__ import annotations

import html
import math
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx

ROME = ZoneInfo("Europe/Rome")

EARTH_TOPICS: tuple[dict[str, str], ...] = (
    {"id": "earth", "it": "La Terra", "wiki_it": "Terra", "wiki": "Earth", "emoji": "🌍", "qid": "Q2"},
    {"id": "crust", "it": "Crosta", "wiki_it": "Crosta_terrestre", "wiki": "Crust_(geology)", "emoji": "🪨", "qid": "Q82378"},
    {"id": "mantle", "it": "Mantello", "wiki_it": "Mantello_terrestre", "wiki": "Mantle_(geology)", "emoji": "🟠", "qid": "Q83296"},
    {"id": "core", "it": "Nucleo", "wiki_it": "Nucleo_terrestre", "wiki": "Earth's_inner_core", "emoji": "🔥", "qid": "Q214164"},
    {"id": "mag", "it": "Campo magnetico", "wiki_it": "Campo_geomagnetico", "wiki": "Earth's_magnetic_field", "emoji": "🧲", "qid": "Q185674"},
    {"id": "atm", "it": "Atmosfera", "wiki_it": "Atmosfera_terrestre", "wiki": "Atmosphere_of_Earth", "emoji": "💨", "qid": "Q3230"},
    {"id": "tect", "it": "Tettonica", "wiki_it": "Tettonica_delle_placche", "wiki": "Plate_tectonics", "emoji": "🧭", "qid": "Q83267"},
    {"id": "cycle", "it": "Ciclo delle rocce", "wiki_it": "Ciclo_litologico", "wiki": "Rock_cycle", "emoji": "🔄", "qid": "Q207066"},
    {"id": "lith", "it": "Litosfera", "wiki_it": "Litosfera", "wiki": "Lithosphere", "emoji": "🪨", "qid": "Q83270"},
    {"id": "hydros", "it": "Idrosfera", "wiki_it": "Idrosfera", "wiki": "Hydrosphere", "emoji": "💧", "qid": "Q48190"},
    {"id": "cont", "it": "Continenti", "wiki_it": "Continente", "wiki": "Continent", "emoji": "🗺️", "qid": "Q5107"},
    {"id": "surf", "it": "Superficie", "wiki_it": "Superficie_terrestre", "wiki": "Earth's_surface", "emoji": "🌐", "qid": "Q1349417"},
)

VOLCANOES: tuple[dict[str, str], ...] = (
    {"id": "etna", "it": "Etna", "wiki_it": "Etna", "wiki": "Mount_Etna", "emoji": "🌋", "qid": "Q16983"},
    {"id": "ves", "it": "Vesuvio", "wiki_it": "Vesuvio", "wiki": "Mount_Vesuvius", "emoji": "🌋", "qid": "Q7699"},
    {"id": "stro", "it": "Stromboli", "wiki_it": "Stromboli", "wiki": "Stromboli", "emoji": "🌋", "qid": "Q189858"},
    {"id": "yell", "it": "Yellowstone", "wiki_it": "Caldera_di_Yellowstone", "wiki": "Yellowstone_Caldera", "emoji": "🌋", "qid": "Q620799"},
    {"id": "kila", "it": "Kīlauea", "wiki_it": "Kīlauea", "wiki": "Kilauea", "emoji": "🌋", "qid": "Q244322"},
    {"id": "fuji", "it": "Fuji", "wiki_it": "Fuji", "wiki": "Mount_Fuji", "emoji": "🗻", "qid": "Q39231"},
    {"id": "krak", "it": "Krakatoa", "wiki_it": "Krakatoa", "wiki": "Krakatoa", "emoji": "🌋", "qid": "Q81967"},
    {"id": "popo", "it": "Popocatépetl", "wiki_it": "Popocatépetl", "wiki": "Popocatépetl", "emoji": "🌋", "qid": "Q182668"},
    {"id": "sthel", "it": "St. Helens", "wiki_it": "Monte_Saint_Helens", "wiki": "Mount_St._Helens", "emoji": "🌋", "qid": "Q217386"},
    {"id": "tamb", "it": "Tambora", "wiki_it": "Tambora", "wiki": "Mount_Tambora", "emoji": "🌋", "qid": "Q202478"},
    {"id": "eyja", "it": "Eyjafjallajökull", "wiki_it": "Eyjafjöll", "wiki": "Eyjafjallajökull", "emoji": "🌋", "qid": "Q202765"},
    {"id": "nyir", "it": "Nyiragongo", "wiki_it": "Nyiragongo", "wiki": "Mount_Nyiragongo", "emoji": "🌋", "qid": "Q844890"},
    {"id": "mauna", "it": "Mauna Loa", "wiki_it": "Mauna_Loa", "wiki": "Mauna_Loa", "emoji": "🌋", "qid": "Q201147"},
    {"id": "pina", "it": "Pinatubo", "wiki_it": "Pinatubo", "wiki": "Mount_Pinatubo", "emoji": "🌋", "qid": "Q201158"},
)

WATER: tuple[dict[str, str], ...] = (
    {"id": "pac", "it": "Pacifico", "wiki_it": "Oceano_Pacifico", "wiki": "Pacific_Ocean", "emoji": "🌊", "qid": "Q98"},
    {"id": "atl", "it": "Atlantico", "wiki_it": "Oceano_Atlantico", "wiki": "Atlantic_Ocean", "emoji": "🌊", "qid": "Q97"},
    {"id": "ind", "it": "Indiano", "wiki_it": "Oceano_Indiano", "wiki": "Indian_Ocean", "emoji": "🌊", "qid": "Q1239"},
    {"id": "med", "it": "Mediterraneo", "wiki_it": "Mar_Mediterraneo", "wiki": "Mediterranean_Sea", "emoji": "🌊", "qid": "Q4918"},
    {"id": "arc", "it": "Artico", "wiki_it": "Oceano_Artico", "wiki": "Arctic_Ocean", "emoji": "🧊", "qid": "Q788"},
    {"id": "so", "it": "Australe", "wiki_it": "Oceano_Australe", "wiki": "Southern_Ocean", "emoji": "🧊", "qid": "Q7354"},
    {"id": "mar", "it": "Fossa delle Marianne", "wiki_it": "Fossa_delle_Marianne", "wiki": "Mariana_Trench", "emoji": "⬇️", "qid": "Q180847"},
    {"id": "gulf", "it": "Corrente del Golfo", "wiki_it": "Corrente_del_Golfo", "wiki": "Gulf_Stream", "emoji": "🌀", "qid": "Q81935"},
    {"id": "hydro", "it": "Ciclo dell'acqua", "wiki_it": "Ciclo_dell'acqua", "wiki": "Water_cycle", "emoji": "💧", "qid": "Q7902"},
    {"id": "ice", "it": "Criostera", "wiki_it": "Criosfera", "wiki": "Cryosphere", "emoji": "❄️", "qid": "Q104834"},
)

OCEANS: tuple[dict[str, str], ...] = (
    {"id": "oce", "it": "Oceano", "wiki_it": "Oceano", "wiki": "Ocean", "emoji": "🌊", "qid": "Q9430"},
    {"id": "pac", "it": "Pacifico", "wiki_it": "Oceano_Pacifico", "wiki": "Pacific_Ocean", "emoji": "🌊", "qid": "Q98"},
    {"id": "atl", "it": "Atlantico", "wiki_it": "Oceano_Atlantico", "wiki": "Atlantic_Ocean", "emoji": "🌊", "qid": "Q97"},
    {"id": "ind", "it": "Indiano", "wiki_it": "Oceano_Indiano", "wiki": "Indian_Ocean", "emoji": "🌊", "qid": "Q1239"},
    {"id": "arc", "it": "Artico", "wiki_it": "Oceano_Artico", "wiki": "Arctic_Ocean", "emoji": "🧊", "qid": "Q788"},
    {"id": "so", "it": "Australe", "wiki_it": "Oceano_Australe", "wiki": "Southern_Ocean", "emoji": "🧊", "qid": "Q7354"},
    {"id": "mar", "it": "Fossa delle Marianne", "wiki_it": "Fossa_delle_Marianne", "wiki": "Mariana_Trench", "emoji": "⬇️", "qid": "Q180847"},
    {"id": "gulf", "it": "Corrente del Golfo", "wiki_it": "Corrente_del_Golfo", "wiki": "Gulf_Stream", "emoji": "🌀", "qid": "Q81935"},
    {"id": "hydro", "it": "Ciclo dell'acqua", "wiki_it": "Ciclo_dell'acqua", "wiki": "Water_cycle", "emoji": "💧", "qid": "Q7902"},
    {"id": "ridge", "it": "Dorsale medio-oceanica", "wiki_it": "Dorsale_oceanica", "wiki": "Mid-ocean_ridge", "emoji": "〰️", "qid": "Q190163"},
)

SEAS: tuple[dict[str, str], ...] = (
    {"id": "med", "it": "Mediterraneo", "wiki_it": "Mar_Mediterraneo", "wiki": "Mediterranean_Sea", "emoji": "🌊", "qid": "Q4918"},
    {"id": "adr", "it": "Adriatico", "wiki_it": "Mar_Adriatico", "wiki": "Adriatic_Sea", "emoji": "🌊", "qid": "Q13924"},
    {"id": "tir", "it": "Tirreno", "wiki_it": "Mar_Tirreno", "wiki": "Tyrrhenian_Sea", "emoji": "🌊", "qid": "Q38882"},
    {"id": "nero", "it": "Mar Nero", "wiki_it": "Mar_Nero", "wiki": "Black_Sea", "emoji": "🌊", "qid": "Q166"},
    {"id": "rosso", "it": "Mar Rosso", "wiki_it": "Mar_Rosso", "wiki": "Red_Sea", "emoji": "🌊", "qid": "Q23406"},
    {"id": "bal", "it": "Baltico", "wiki_it": "Mar_Baltico", "wiki": "Baltic_Sea", "emoji": "🌊", "qid": "Q545"},
    {"id": "nord", "it": "Mare del Nord", "wiki_it": "Mare_del_Nord", "wiki": "North_Sea", "emoji": "🌊", "qid": "Q1693"},
    {"id": "car", "it": "Caraibi", "wiki_it": "Mar_dei_Caraibi", "wiki": "Caribbean_Sea", "emoji": "🌊", "qid": "Q1247"},
    {"id": "casp", "it": "Caspio", "wiki_it": "Mar_Caspio", "wiki": "Caspian_Sea", "emoji": "🌊", "qid": "Q5484"},
    {"id": "scs", "it": "Cinese meridionale", "wiki_it": "Mar_Cinese_Meridionale", "wiki": "South_China_Sea", "emoji": "🌊", "qid": "Q37660"},
)

GLACIERS: tuple[dict[str, str], ...] = (
    {"id": "glac", "it": "Ghiacciaio", "wiki_it": "Ghiacciaio", "wiki": "Glacier", "emoji": "🧊", "qid": "Q35666"},
    {"id": "sheet", "it": "Calotta glaciale", "wiki_it": "Calotta_glaciale", "wiki": "Ice_sheet", "emoji": "🧊", "qid": "Q1135137"},
    {"id": "cryo", "it": "Criosfera", "wiki_it": "Criosfera", "wiki": "Cryosphere", "emoji": "❄️", "qid": "Q104834"},
    {"id": "ant", "it": "Antartide", "wiki_it": "Antartide", "wiki": "Antarctica", "emoji": "🧊", "qid": "Q51"},
    {"id": "grl", "it": "Calotta groenlandese", "wiki_it": "Calotta_glaciale_della_Groenlandia", "wiki": "Greenland_ice_sheet", "emoji": "🧊", "qid": "Q673517"},
    {"id": "perito", "it": "Perito Moreno", "wiki_it": "Ghiacciaio_Perito_Moreno", "wiki": "Perito_Moreno_Glacier", "emoji": "🧊", "qid": "Q506447"},
    {"id": "alet", "it": "Aletsch", "wiki_it": "Ghiacciaio_dell'Aletsch", "wiki": "Aletsch_Glacier", "emoji": "🧊", "qid": "Q688742"},
    {"id": "vatna", "it": "Vatnajökull", "wiki_it": "Vatnajökull", "wiki": "Vatnajökull", "emoji": "🧊", "qid": "Q207325"},
    {"id": "khumbu", "it": "Khumbu", "wiki_it": "Ghiacciaio_del_Khumbu", "wiki": "Khumbu_Glacier", "emoji": "🧊", "qid": "Q1740544"},
    {"id": "hubb", "it": "Hubbard", "wiki_it": "Ghiacciaio_Hubbard", "wiki": "Hubbard_Glacier", "emoji": "🧊", "qid": "Q1630684"},
    {"id": "forni", "it": "Dei Forni", "wiki_it": "Ghiacciaio_dei_Forni", "wiki": "Forni_Glacier", "emoji": "🧊", "qid": "Q3768133"},
    {"id": "perm", "it": "Permafrost", "wiki_it": "Permafrost", "wiki": "Permafrost", "emoji": "❄️", "qid": "Q179918"},
    {"id": "berg", "it": "Iceberg", "wiki_it": "Iceberg", "wiki": "Iceberg", "emoji": "🧊", "qid": "Q47568"},
)

PLATES: tuple[dict[str, str], ...] = (
    {"id": "pac", "it": "Placca pacifica", "wiki_it": "Placca_pacifica", "wiki": "Pacific_Plate", "emoji": "🧭", "qid": "Q272466"},
    {"id": "nam", "it": "Nordamericana", "wiki_it": "Placca_nordamericana", "wiki": "North_American_Plate", "emoji": "🧭", "qid": "Q847583"},
    {"id": "eur", "it": "Eurasiatica", "wiki_it": "Placca_eurasiatica", "wiki": "Eurasian_Plate", "emoji": "🧭", "qid": "Q207814"},
    {"id": "afr", "it": "Africana", "wiki_it": "Placca_africana", "wiki": "African_Plate", "emoji": "🧭", "qid": "Q272399"},
    {"id": "sam", "it": "Sudamericana", "wiki_it": "Placca_sudamericana", "wiki": "South_American_Plate", "emoji": "🧭", "qid": "Q847576"},
    {"id": "ind", "it": "Indo-australiana", "wiki_it": "Placca_indo-australiana", "wiki": "Indo-Australian_Plate", "emoji": "🧭", "qid": "Q271269"},
    {"id": "ant", "it": "Antartica", "wiki_it": "Placca_antartica", "wiki": "Antarctic_Plate", "emoji": "🧭", "qid": "Q831414"},
    {"id": "naz", "it": "Nazca", "wiki_it": "Placca_di_Nazca", "wiki": "Nazca_Plate", "emoji": "🧭", "qid": "Q207373"},
    {"id": "phi", "it": "Delle Filippine", "wiki_it": "Placca_delle_Filippine", "wiki": "Philippine_Sea_Plate", "emoji": "🧭", "qid": "Q841778"},
    {"id": "ara", "it": "Arabica", "wiki_it": "Placca_arabica", "wiki": "Arabian_Plate", "emoji": "🧭", "qid": "Q654627"},
)

GEO_CATALOGS: dict[str, tuple[dict[str, str], ...]] = {
    "terra": EARTH_TOPICS,
    "volc": VOLCANOES,
    "water": WATER,
    "plate": PLATES,
    "ocean": OCEANS,
    "sea": SEAS,
    "ice": GLACIERS,
}

QUAKE_FEEDS = {
    "day": ("4.5_day", "M ≥ 4,5 nelle ultime 24 ore"),
    "week": ("2.5_week", "M ≥ 2,5 negli ultimi 7 giorni"),
    "sig": ("significant_week", "Eventi significativi della settimana"),
}

EONET_CAT_IT = {
    "wildfires": "Incendi",
    "severeStorms": "Tempeste severe",
    "volcanoes": "Vulcani",
    "seaLakeIce": "Ghiaccio marino / lacustre",
    "earthquakes": "Terremoti",
    "floods": "Alluvioni",
    "drought": "Siccità",
    "dustHaze": "Polvere / caligine",
    "snow": "Neve",
    "tempExtremes": "Temperature estreme",
    "landslides": "Frane",
    "manmade": "Origine umana",
    "waterColor": "Colore delle acque",
}

# Eventi nel mondo: niente elenco di incendi. Restano in 📡 Live se li cerchi.
EONET_WORLD_SKIP = frozenset({"wildfires"})


def geo_item(kind: str, sid: str) -> dict[str, str] | None:
    for row in GEO_CATALOGS.get(kind, ()):
        if row["id"] == sid:
            return row
    return None


def _when_it(ms: float | int | None) -> str:
    if ms is None:
        return "—"
    try:
        when = datetime.fromtimestamp(float(ms) / 1000.0, tz=timezone.utc).astimezone(ROME)
    except (TypeError, ValueError, OSError):
        return "—"
    return f"{when.day:02d}/{when.month:02d} {when.hour:02d}:{when.minute:02d}"


def _iso_it(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return "—"
    try:
        when = datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(ROME)
    except ValueError:
        return text[:16]
    return f"{when.day:02d}/{when.month:02d} {when.hour:02d}:{when.minute:02d}"


async def fetch_quakes(client: httpx.AsyncClient, feed: str) -> dict[str, Any]:
    slug = QUAKE_FEEDS.get(feed, QUAKE_FEEDS["day"])[0]
    response = await client.get(
        f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{slug}.geojson"
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("terremoti vuoti")
    return data


async def fetch_eonet(
    client: httpx.AsyncClient,
    *,
    limit: int = 12,
    category: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"status": "open", "limit": limit}
    if category:
        params["category"] = category
    response = await client.get("https://eonet.gsfc.nasa.gov/api/v3/events", params=params)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("eonet vuoto")
    return data


def format_quakes(data: dict[str, Any], *, feed: str) -> str:
    _slug, blurb = QUAKE_FEEDS.get(feed, QUAKE_FEEDS["day"])
    meta = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    features = data.get("features") if isinstance(data.get("features"), list) else []
    count = meta.get("count")
    generated = meta.get("generated")
    lines = [
        "🌋 <b>TERREMOTI</b>",
        f"<i>USGS · {blurb}</i>",
        f"Eventi nel feed: {count if count is not None else len(features)}",
        f"Aggiornato: {_when_it(generated) if generated else '—'}",
        "",
    ]
    if not features:
        lines.append("In questo intervallo il feed è vuoto.")
        lines.append("")
        lines.append("<i>Catalogo USGS, non un allarme civile e non un oracolo.</i>")
        return "\n".join(lines)
    for item in features[:12]:
        if not isinstance(item, dict):
            continue
        props = item.get("properties") if isinstance(item.get("properties"), dict) else {}
        geom = item.get("geometry") if isinstance(item.get("geometry"), dict) else {}
        coords = geom.get("coordinates") if isinstance(geom.get("coordinates"), list) else []
        mag = props.get("mag")
        place = props.get("place") or "luogo non indicato"
        depth = coords[2] if len(coords) > 2 else None
        try:
            mag_s = f"{float(mag):.1f}"
        except (TypeError, ValueError):
            mag_s = "—"
        try:
            depth_s = f"{float(depth):.0f} km" if depth is not None else "—"
        except (TypeError, ValueError):
            depth_s = "—"
        lines.append(
            f"• <b>M {mag_s}</b> — {html.escape(str(place), quote=False)}\n"
            f"  {_when_it(props.get('time'))} · profondità {depth_s}"
        )
    lines.extend(
        [
            "",
            "<i>United States Geological Survey, feed GeoJSON pubblico. "
            "Non sostituisce le allerte della protezione civile.</i>",
        ]
    )
    return "\n".join(lines)


def format_eonet(data: dict[str, Any], *, category: str | None = None) -> str:
    events = data.get("events") if isinstance(data.get("events"), list) else []
    filt = EONET_CAT_IT.get(category or "", "tutte le categorie aperte")
    lines = [
        "🌪️ <b>EVENTI SULLA TERRA</b>",
        f"<i>NASA EONET · {filt}</i>",
        "",
    ]
    if not events:
        lines.append("Nessun evento aperto in questo filtro.")
        lines.append("")
        lines.append("<i>Earth Observatory Natural Event Tracker. Non è un bollettino di allerta.</i>")
        return "\n".join(lines)
    for event in events[:12]:
        if not isinstance(event, dict):
            continue
        title = str(event.get("title") or "Evento")
        cats = event.get("categories") if isinstance(event.get("categories"), list) else []
        labels = []
        for cat in cats:
            if isinstance(cat, dict):
                key = str(cat.get("id") or "")
                labels.append(EONET_CAT_IT.get(key, str(cat.get("title") or key)))
        geometries = event.get("geometry") if isinstance(event.get("geometry"), list) else []
        when = ""
        if geometries and isinstance(geometries[0], dict):
            when = _iso_it(str(geometries[0].get("date") or ""))
        cat_line = ", ".join(labels) if labels else "—"
        lines.append(f"• <b>{html.escape(title, quote=False)}</b>\n  {html.escape(cat_line, quote=False)} · {when or '—'}")
    lines.extend(
        [
            "",
            "<i>NASA EONET v3, eventi aperti. Titoli del feed; non è una previsione.</i>",
        ]
    )
    return "\n".join(lines)


def format_earth_topic(
    item: dict[str, str],
    *,
    extract: str | None = None,
    facts: list[tuple[str, str]] | None = None,
    url: str | None = None,
) -> str:
    lines = [
        f"{item.get('emoji') or '🌍'} <b>{html.escape(item['it'].upper(), quote=False)}</b>",
        "<i>Voce e misure da Wikipedia / Wikidata. Niente geologia inventata.</i>",
        "",
    ]
    if facts:
        lines.append("📐 <b>Wikidata</b>")
        for label, value in facts[:8]:
            lines.append(f"• {html.escape(str(label), quote=False)}: <code>{html.escape(str(value), quote=False)}</code>")
        lines.append("")
    if extract:
        lines.append("📖 <b>Wikipedia</b>")
        lines.append(html.escape(extract, quote=False))
        if url:
            lines.append(f'\n<a href="{html.escape(url, quote=True)}">Apri la voce</a>')
    else:
        lines.append("La voce Wikipedia non è arrivata. Riprova tra poco.")
    return "\n".join(lines)


NEAR_QUAKE_KM = 500.0
NEAR_EONET_KM = 800.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    chord = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(chord)))


def _coord_pairs(node: Any) -> list[tuple[float, float]]:
    if isinstance(node, list):
        if (
            len(node) >= 2
            and isinstance(node[0], (int, float))
            and isinstance(node[1], (int, float))
            and not isinstance(node[0], list)
        ):
            return [(float(node[1]), float(node[0]))]
        pairs: list[tuple[float, float]] = []
        for item in node:
            pairs.extend(_coord_pairs(item))
        return pairs
    return []


def eonet_nearest(
    event: dict[str, Any], lat: float, lon: float
) -> tuple[float, float, float] | None:
    geometries = event.get("geometry") if isinstance(event.get("geometry"), list) else []
    best: tuple[float, float, float] | None = None
    for geom in geometries:
        if not isinstance(geom, dict):
            continue
        for ev_lat, ev_lon in _coord_pairs(geom.get("coordinates")):
            dist = haversine_km(lat, lon, ev_lat, ev_lon)
            if best is None or dist < best[2]:
                best = (ev_lat, ev_lon, dist)
    return best


async def fetch_quakes_near(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    *,
    radius_km: float = NEAR_QUAKE_KM,
    minmagnitude: float = 2.5,
    days: int = 14,
    limit: int = 20,
) -> dict[str, Any]:
    start = datetime.now(timezone.utc) - timedelta(days=days)
    response = await client.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        params={
            "format": "geojson",
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "maxradiuskm": f"{radius_km:.0f}",
            "minmagnitude": f"{minmagnitude:.1f}",
            "orderby": "time",
            "limit": limit,
            "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        },
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("terremoti vicini vuoti")
    return data


def _quake_line(item: dict[str, Any], *, dist_km: float | None = None) -> str:
    props = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    geom = item.get("geometry") if isinstance(item.get("geometry"), dict) else {}
    coords = geom.get("coordinates") if isinstance(geom.get("coordinates"), list) else []
    mag = props.get("mag")
    place = props.get("place") or "luogo non indicato"
    depth = coords[2] if len(coords) > 2 else None
    try:
        mag_s = f"{float(mag):.1f}"
    except (TypeError, ValueError):
        mag_s = "—"
    try:
        depth_s = f"{float(depth):.0f} km" if depth is not None else "—"
    except (TypeError, ValueError):
        depth_s = "—"
    extra = f" · {dist_km:.0f} km" if dist_km is not None else ""
    return (
        f"• <b>M {mag_s}</b> — {html.escape(str(place), quote=False)}\n"
        f"  {_when_it(props.get('time'))} · profondità {depth_s}{extra}"
    )


def _eonet_line(event: dict[str, Any], *, dist_km: float | None = None) -> str:
    title = str(event.get("title") or "Evento")
    cats = event.get("categories") if isinstance(event.get("categories"), list) else []
    labels = []
    for cat in cats:
        if isinstance(cat, dict):
            key = str(cat.get("id") or "")
            labels.append(EONET_CAT_IT.get(key, str(cat.get("title") or key)))
    geometries = event.get("geometry") if isinstance(event.get("geometry"), list) else []
    when = ""
    if geometries and isinstance(geometries[0], dict):
        when = _iso_it(str(geometries[0].get("date") or ""))
    cat_line = ", ".join(labels) if labels else "—"
    extra = f" · {dist_km:.0f} km" if dist_km is not None else ""
    return (
        f"• <b>{html.escape(title, quote=False)}</b>\n"
        f"  {html.escape(cat_line, quote=False)} · {when or '—'}{extra}"
    )


def format_nearby_events(
    *,
    place: str,
    lat: float,
    lon: float,
    quakes: dict[str, Any] | None,
    eonet: dict[str, Any] | None,
    quake_km: float = NEAR_QUAKE_KM,
    eonet_km: float = NEAR_EONET_KM,
) -> str:
    where = html.escape(place, quote=False)
    lines = [
        f"📍 <b>EVENTI QUI — {where.upper()}</b>",
        f"<i>USGS e NASA EONET entro circa {quake_km:.0f}–{eonet_km:.0f} km. "
        "Se non è vicino a questa città, non lo elenco.</i>",
        "",
    ]
    rows: list[tuple[float, str]] = []
    features = (
        quakes.get("features")
        if isinstance(quakes, dict) and isinstance(quakes.get("features"), list)
        else []
    )
    for item in features:
        if not isinstance(item, dict):
            continue
        geom = item.get("geometry") if isinstance(item.get("geometry"), dict) else {}
        coords = geom.get("coordinates") if isinstance(geom.get("coordinates"), list) else []
        if len(coords) < 2:
            continue
        try:
            ev_lon, ev_lat = float(coords[0]), float(coords[1])
        except (TypeError, ValueError):
            continue
        dist = haversine_km(lat, lon, ev_lat, ev_lon)
        if dist > quake_km:
            continue
        rows.append((dist, _quake_line(item, dist_km=dist)))
    events = (
        eonet.get("events")
        if isinstance(eonet, dict) and isinstance(eonet.get("events"), list)
        else []
    )
    for event in events:
        if not isinstance(event, dict):
            continue
        nearest = eonet_nearest(event, lat, lon)
        if nearest is None or nearest[2] > eonet_km:
            continue
        rows.append((nearest[2], _eonet_line(event, dist_km=nearest[2])))
    rows.sort(key=lambda row: row[0])
    if not rows:
        lines.append(f"Entro il raggio da {where} i feed non hanno eventi aperti.")
        lines.append("Non invento fenomeni: se non è vicino, non c'è.")
        lines.append("")
        lines.append("<i>USGS FDSN + NASA EONET. Non è un'allerta della protezione civile.</i>")
        return "\n".join(lines)
    for _dist, line in rows[:14]:
        lines.append(line)
    lines.extend(
        [
            "",
            "<i>Cataloghi pubblici USGS e NASA EONET. Distanza in linea d'aria. "
            "Non sostituisce le allerte locali.</i>",
        ]
    )
    return "\n".join(lines)


def eonet_event_ids(event: dict[str, Any]) -> set[str]:
    cats = event.get("categories") if isinstance(event.get("categories"), list) else []
    ids: set[str] = set()
    for cat in cats:
        if isinstance(cat, dict) and cat.get("id"):
            ids.add(str(cat.get("id")))
    return ids


def eonet_world_keep(event: dict[str, Any]) -> bool:
    return not (eonet_event_ids(event) & EONET_WORLD_SKIP)


def filter_eonet_world(events: list[Any] | None) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for event in events or []:
        if isinstance(event, dict) and eonet_world_keep(event):
            kept.append(event)
    return kept


def format_world_events(
    *,
    quakes: dict[str, Any] | None,
    eonet: dict[str, Any] | None,
) -> str:
    lines = [
        "🌍 <b>EVENTI NEL MONDO</b>",
        "<i>Catastrofi e fenomeni importanti: USGS significativi + NASA EONET. "
        "Gli incendi restano nella cartella Live. Non è un oracolo.</i>",
        "",
    ]
    features = (
        quakes.get("features")
        if isinstance(quakes, dict) and isinstance(quakes.get("features"), list)
        else []
    )
    raw_events = (
        eonet.get("events")
        if isinstance(eonet, dict) and isinstance(eonet.get("events"), list)
        else []
    )
    events = filter_eonet_world(raw_events)
    if features:
        lines.append("⚠️ <b>Terremoti significativi</b> <i>(USGS, settimana)</i>")
        for item in features[:10]:
            if isinstance(item, dict):
                lines.append(_quake_line(item))
        lines.append("")
    if events:
        lines.append("🌪️ <b>Fenomeni aperti</b> <i>(NASA EONET, senza incendi)</i>")
        for event in events[:12]:
            if isinstance(event, dict):
                lines.append(_eonet_line(event))
        lines.append("")
    if not features and not events:
        lines.append("In questo momento i feed non segnalano eventi aperti.")
        lines.append("Non invento catastrofi.")
        lines.append("")
    lines.append(
        "<i>United States Geological Survey e NASA Earth Observatory Natural Event Tracker. "
        "Non è un bollettino di allerta.</i>"
    )
    return "\n".join(lines)
