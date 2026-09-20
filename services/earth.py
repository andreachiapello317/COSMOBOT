"""Dati sulla Terra per GEO: cataloghi + feed live. Niente geologia inventata."""

from __future__ import annotations

import html
from datetime import datetime, timezone
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
