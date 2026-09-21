"""CITY LIFE in TERRA: OpenStreetMap intorno al luogo. Overpass, niente GPS e niente TomTom."""

from __future__ import annotations

import html as _html
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import httpx

from services.earth import haversine_km, _latlon_it

log = logging.getLogger("stellebot.citylife")

OVERPASS_URLS = (
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
USER_AGENT = "StelleBot/1.0 (Telegram; CITY LIFE; OpenStreetMap Overpass)"
PAGE_SIZE = 6
MAX_ITEMS = 24
CACHE_TTL = 180
HOST_COOLDOWN = 45
OSM_NOTE = "OpenStreetMap via Overpass. Copertura volontaria, non un elenco ufficiale."

KINDS = {
    "near": {"it": "Vicino", "emoji": "📍", "blurb": "Servizi e fermate nel raggio di un chilometro."},
    "mobility": {"it": "Mobilità", "emoji": "🚦", "blurb": "Fermate, sharing, parcheggi. Niente ritardi live."},
    "safety": {"it": "Sicurezza", "emoji": "🏥", "blurb": "Ospedali e farmacie OSM, allerte Meteoalarm se ci sono."},
    "culture": {"it": "Vita in città", "emoji": "🎭", "blurb": "Cinema, musei, mercati, ristoranti. Orario OSM se c'è."},
    "services": {"it": "Servizi", "emoji": "⛲", "blurb": "Fontanelle, WiFi, bagni, webcam taggate."},
    "walk": {"it": "Passeggiata", "emoji": "🚶", "blurb": "Punti a piedi, dal più vicino."},
}

FILTERS: dict[str, tuple[str, ...]] = {
    "mobility": (
        "[highway=bus_stop]",
        "[railway=tram_stop]",
        "[railway=subway_entrance]",
        "[station=subway]",
        "[public_transport=station]",
        "[amenity=bicycle_rental]",
        "[amenity=car_sharing]",
        "[amenity=kick-scooter-rental]",
        "[amenity=parking]",
        '["contact:webcam"]',
        "[webcam]",
        '[man_made=surveillance]["camera:type"="webcam"]',
    ),
    "safety": (
        "[amenity=hospital]",
        "[amenity=clinic]",
        "[amenity=doctors]",
        "[amenity=pharmacy]",
        "[emergency=yes]",
    ),
    "culture": (
        "[amenity=cinema]",
        "[amenity=theatre]",
        "[amenity=marketplace]",
        "[amenity=restaurant]",
        "[amenity=cafe]",
        "[amenity=bar]",
        "[tourism=museum]",
        "[tourism=attraction]",
        "[tourism=gallery]",
        "[historic=monument]",
        "[leisure=park]",
        "[leisure=stadium]",
    ),
    "services": (
        "[amenity=drinking_water]",
        "[amenity=fountain]",
        "[amenity=toilets]",
        "[internet_access=wlan]",
        "[amenity=internet_cafe]",
        '["contact:webcam"]',
        "[webcam]",
        '[man_made=surveillance]["camera:type"="webcam"]',
    ),
    "walk": (
        "[amenity=drinking_water]",
        "[amenity=fountain]",
        "[amenity=toilets]",
        "[amenity=cafe]",
        "[tourism=viewpoint]",
        "[tourism=artwork]",
        "[tourism=attraction]",
        "[leisure=park]",
        "[amenity=pharmacy]",
    ),
    "near": (
        "[amenity=pharmacy]",
        "[amenity=hospital]",
        "[amenity=parking]",
        "[amenity=bicycle_rental]",
        "[amenity=drinking_water]",
        "[amenity=restaurant]",
        "[amenity=cafe]",
        "[amenity=cinema]",
        "[amenity=theatre]",
        "[highway=bus_stop]",
        "[railway=tram_stop]",
        "[railway=subway_entrance]",
        "[internet_access=wlan]",
        "[tourism=museum]",
        "[tourism=attraction]",
        "[amenity=marketplace]",
    ),
}

RADIUS_M = {
    "near": 1200,
    "mobility": 2500,
    "safety": 3500,
    "culture": 2000,
    "services": 1500,
    "walk": 1200,
}

LABELS = {
    "parking": "Parcheggio",
    "bike": "Bici sharing",
    "car": "Auto sharing",
    "scooter": "Monopattini",
    "pharmacy": "Farmacia",
    "hospital": "Ospedale / PS",
    "water": "Fontanella",
    "toilets": "Bagni",
    "bench": "Panchina",
    "wifi": "WiFi",
    "restaurant": "Ristorante",
    "cafe": "Locale",
    "cinema": "Cinema",
    "theatre": "Teatro",
    "market": "Mercato",
    "museum": "Museo",
    "attraction": "Attrazione",
    "viewpoint": "Belvedere",
    "park": "Parco",
    "stadium": "Stadio",
    "bus": "Bus",
    "tram": "Tram",
    "metro": "Metro",
    "stop": "Fermata",
    "webcam": "Webcam",
    "poi": "Luogo",
}

GROUP_EMOJI = {
    "parking": "🅿️",
    "bike": "🚲",
    "car": "🚗",
    "scooter": "🛴",
    "pharmacy": "💊",
    "hospital": "🏥",
    "water": "⛲",
    "toilets": "🚻",
    "bench": "🪑",
    "wifi": "📶",
    "restaurant": "🍴",
    "cafe": "☕",
    "cinema": "🎬",
    "theatre": "🎭",
    "market": "🛒",
    "museum": "🏛️",
    "attraction": "📍",
    "viewpoint": "🔭",
    "park": "🌳",
    "stadium": "🏟️",
    "bus": "🚌",
    "tram": "🚊",
    "metro": "🚇",
    "stop": "🚏",
    "webcam": "📷",
    "poi": "📍",
}

METEOALARM = "https://feeds.meteoalarm.org/api/v1/warnings/{feed}"
_METEO_FEEDS = {
    "it": "feeds-italy",
    "fr": "feeds-france",
    "de": "feeds-germany",
    "es": "feeds-spain",
    "at": "feeds-austria",
    "ch": "feeds-switzerland",
    "be": "feeds-belgium",
    "nl": "feeds-netherlands",
    "pl": "feeds-poland",
    "gr": "feeds-greece",
    "hr": "feeds-croatia",
    "si": "feeds-slovenia",
    "hu": "feeds-hungary",
    "cz": "feeds-czechia",
    "sk": "feeds-slovakia",
    "ie": "feeds-ireland",
    "gb": "feeds-united-kingdom",
    "uk": "feeds-united-kingdom",
}

_DAY = {"mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4, "sa": 5, "su": 6}
_TIME = re.compile(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})")
_DAYS = re.compile(
    r"\b(mo|tu|we|th|fr|sa|su)(?:\s*-\s*(mo|tu|we|th|fr|sa|su))?(?:\s*,\s*(mo|tu|we|th|fr|sa|su))*",
    re.I,
)
_MONTHISH = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|sh)\b")

_cache: dict[str, tuple[float, Any]] = {}
_dead_until: dict[str, float] = {}


class CityLifeError(RuntimeError):
    """Overpass o feed città non usabile."""


def e(text: Any) -> str:
    return _html.escape(str(text), quote=False)


def osm_url(lat: float, lon: float, zoom: int = 16) -> str:
    return f"https://www.openstreetmap.org/?mlat={lat:.5f}&mlon={lon:.5f}#map={zoom}/{lat:.5f}/{lon:.5f}"


def resolve_kind(raw: str | None) -> str | None:
    key = (raw or "").strip().lower()
    aliases = {
        "vicino": "near",
        "traffico": "mobility",
        "allerte": "safety",
        "vita": "culture",
        "fontanelle": "services",
        "passeggiata": "walk",
    }
    key = aliases.get(key, key)
    return key if key in KINDS else None


def kind_meta(kind: str) -> dict[str, str]:
    return KINDS.get(kind) or KINDS["near"]


def country_hint(place: str) -> str:
    blob = str(place or "").lower()
    table = (
        (("italia", "italy", "cuneo", "milano", "torino", "roma", "piemonte"), "it"),
        (("france", "francia", "paris", "parigi"), "fr"),
        (("deutschland", "germany", "germania"), "de"),
        (("españa", "spain", "spagna"), "es"),
        (("schweiz", "svizzera", "switzerland"), "ch"),
        (("österreich", "austria"), "at"),
    )
    for tokens, cc in table:
        if any(tok in blob for tok in tokens):
            return cc
    return "it"


def city_now(*, lon: float = 7.55) -> datetime:
    try:
        return datetime.now(ZoneInfo("Europe/Rome"))
    except Exception:
        hours = max(-12, min(14, int(round(float(lon) / 15.0))))
        return datetime.now(timezone(timedelta(hours=hours)))


def _days_from(token: str) -> set[int] | None:
    token = token.strip().lower()
    if not token:
        return None
    found: set[int] = set()
    for part in (p.strip() for p in token.split(",") if p.strip()):
        if "-" in part:
            a, b = (x.strip() for x in part.split("-", 1))
            if a not in _DAY or b not in _DAY:
                return None
            i = _DAY[a]
            found.add(i)
            while i != _DAY[b]:
                i = (i + 1) % 7
                found.add(i)
        else:
            if part not in _DAY:
                return None
            found.add(_DAY[part])
    return found or None


def is_open_now(opening_hours: str | None, now: datetime | None = None) -> bool | None:
    raw = (opening_hours or "").strip()
    if not raw:
        return None
    text = " ".join(raw.split())
    low = text.lower()
    if low in {"24/7", "24/7;"}:
        return True
    if low in {"closed", "off"}:
        return False
    if _MONTHISH.search(low) or "sunrise" in low or "sunset" in low or "||" in low:
        return None
    now = now or datetime.now(timezone.utc)
    weekday = now.weekday()
    minute = now.hour * 60 + now.minute
    matched = False
    known = False
    for rule in text.split(";"):
        chunk = rule.strip()
        if not chunk:
            continue
        low_c = chunk.lower()
        if low_c.startswith("ph"):
            if low_c in {"ph off", "ph closed"}:
                continue
            return None
        times: list[tuple[int, int]] = []
        for match in _TIME.finditer(chunk):
            h1, m1, h2, m2 = (int(match.group(i)) for i in range(1, 5))
            a = min(h1, 23) * 60 + (0 if h1 == 24 else m1)
            b = 24 * 60 if h2 == 24 and m2 == 0 else min(h2, 23) * 60 + m2
            times.append((a, b))
        day_blob = _DAYS.search(chunk)
        days = _days_from(day_blob.group(0)) if day_blob else None
        if times and days is None and not day_blob:
            days = set(range(7))
        if not times and ("off" in low_c or "closed" in low_c) and days is not None:
            known = True
            if weekday in days:
                matched = False
            continue
        if not times or days is None:
            return None
        known = True
        if weekday in days:
            if any((a <= minute < b) if a < b else (minute >= a or minute < b) for a, b in times):
                matched = True
            elif "off" in low_c:
                matched = False
    if not known:
        return None
    return matched


def _open_label(row: dict[str, Any], now: datetime) -> str:
    flag = is_open_now(row.get("opening_hours"), now)
    if flag is True:
        return "aperto ora"
    if flag is False:
        return "chiuso ora"
    if row.get("opening_hours"):
        return str(row["opening_hours"])[:36]
    return "orario n/d"


def classify(tags: dict[str, Any]) -> str:
    amenity = str(tags.get("amenity") or "")
    tourism = str(tags.get("tourism") or "")
    railway = str(tags.get("railway") or "")
    highway = str(tags.get("highway") or "")
    leisure = str(tags.get("leisure") or "")
    historic = str(tags.get("historic") or "")
    if tags.get("contact:webcam") or tags.get("webcam") or tags.get("camera:type") == "webcam":
        return "webcam"
    mapping = {
        "parking": "parking",
        "bicycle_rental": "bike",
        "car_sharing": "car",
        "kick-scooter-rental": "scooter",
        "pharmacy": "pharmacy",
        "drinking_water": "water",
        "fountain": "water",
        "toilets": "toilets",
        "bench": "bench",
        "internet_cafe": "wifi",
        "restaurant": "restaurant",
        "cafe": "cafe",
        "bar": "cafe",
        "fast_food": "cafe",
        "cinema": "cinema",
        "theatre": "theatre",
        "marketplace": "market",
    }
    if amenity in mapping:
        return mapping[amenity]
    if amenity in {"hospital", "clinic", "doctors"} or tags.get("emergency") == "yes":
        return "hospital"
    if tags.get("internet_access") == "wlan":
        return "wifi"
    if tourism in {"museum", "gallery"}:
        return "museum"
    if tourism in {"attraction", "artwork"} or historic == "monument":
        return "attraction"
    if tourism == "viewpoint":
        return "viewpoint"
    if leisure == "park":
        return "park"
    if leisure == "stadium":
        return "stadium"
    if highway == "bus_stop":
        return "bus"
    if railway == "tram_stop":
        return "tram"
    if railway == "subway_entrance" or tags.get("station") == "subway":
        return "metro"
    if tags.get("public_transport") == "station":
        return "stop"
    return "poi"


def _tag(tags: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = tags.get(key)
        if value:
            return str(value).strip()
    return ""


def _coords(el: dict[str, Any]) -> tuple[float, float] | None:
    lat, lon = el.get("lat"), el.get("lon")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return float(lat), float(lon)
    center = el.get("center") or {}
    lat, lon = center.get("lat"), center.get("lon")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return float(lat), float(lon)
    return None


def build_around_ql(lat: float, lon: float, radius_m: int, filters: tuple[str, ...], *, timeout: int = 22, limit: int = 50) -> str:
    bits = "\n".join(f"  nwr(around:{int(radius_m)},{lat:.5f},{lon:.5f}){flt};" for flt in filters)
    return f"[out:json][timeout:{timeout}];\n(\n{bits}\n);\nout center {int(limit)};"


def _dead_replica(payload: dict[str, Any]) -> bool:
    osm3s = payload.get("osm3s") if isinstance(payload.get("osm3s"), dict) else {}
    ts = str(osm3s.get("timestamp_osm_base") or "")
    if not ts:
        return False
    return not (len(ts) >= 10 and ts[0:4].isdigit() and "T" in ts)


def _failed_remark(payload: dict[str, Any]) -> bool:
    remark = str(payload.get("remark") or "").lower()
    return any(bit in remark for bit in ("timeout", "error", "out of memory"))


async def overpass(client: httpx.AsyncClient, query: str, *, timeout: float = 26.0) -> dict[str, Any]:
    now = time.time()
    urls = [u for u in OVERPASS_URLS if _dead_until.get(urlparse(u).netloc or "", 0) < now] or list(OVERPASS_URLS)
    last_error = "Overpass non ha risposto"
    for index, url in enumerate(urls):
        host = urlparse(url).netloc or "overpass"
        host_timeout = timeout if index == len(urls) - 1 else min(timeout, 22.0)
        try:
            response = await client.post(
                url,
                data={"data": query},
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                timeout=host_timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            last_error = "Overpass non raggiungibile"
            log.warning("overpass fail host=%s err=%s", host, exc)
            _dead_until[host] = time.time() + HOST_COOLDOWN
            continue
        if not isinstance(payload, dict):
            last_error = "payload Overpass inatteso"
            continue
        if _failed_remark(payload) or _dead_replica(payload):
            last_error = "timeout Overpass" if _failed_remark(payload) else "replica Overpass vuota"
            _dead_until[host] = time.time() + HOST_COOLDOWN
            continue
        payload.setdefault("elements", [])
        payload["ok"] = True
        _dead_until.pop(host, None)
        return payload
    return {"ok": False, "error": last_error, "elements": []}


def normalize_elements(payload: dict[str, Any], *, lat: float, lon: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for el in payload.get("elements") or []:
        if not isinstance(el, dict):
            continue
        coords = _coords(el)
        if coords is None:
            continue
        elat, elon = coords
        tags = el.get("tags") if isinstance(el.get("tags"), dict) else {}
        group = classify(tags)
        name = _tag(tags, "name:it", "name", "official_name", "ref") or LABELS.get(group, "senza nome")
        key = f"{round(elat, 5)}:{round(elon, 5)}:{name.casefold()}"
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "id": f"{el.get('type')}/{el.get('id')}",
                "name": name,
                "lat": elat,
                "lon": elon,
                "group": group,
                "kind": LABELS.get(group, "Luogo"),
                "dist_km": haversine_km(lat, lon, elat, elon),
                "opening_hours": _tag(tags, "opening_hours"),
                "operator": _tag(tags, "operator", "brand", "network"),
                "capacity": _tag(tags, "capacity"),
                "cuisine": _tag(tags, "cuisine"),
                "website": _tag(tags, "website", "contact:website", "url"),
                "webcam": _tag(tags, "contact:webcam", "webcam"),
                "phone": _tag(tags, "phone", "contact:phone"),
                "map": osm_url(elat, elon, 17),
            }
        )
    rows.sort(key=lambda r: (float(r.get("dist_km") or 9e9), str(r.get("name") or "")))
    return rows[:MAX_ITEMS]


async def search_around(client: httpx.AsyncClient, lat: float, lon: float, kind: str) -> dict[str, Any]:
    cat = resolve_kind(kind)
    if not cat:
        raise CityLifeError(f"categoria sconosciuta: {kind}")
    radius = RADIUS_M.get(cat, 2000)
    cache_key = f"life:{cat}:{lat:.3f}:{lon:.3f}:{radius}"
    hit = _cache.get(cache_key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return {"ok": True, "kind": cat, "rows": list(hit[1]), "cached": True, "radius_m": radius}
    filters = FILTERS[cat]
    payload = await overpass(client, build_around_ql(lat, lon, radius, filters))
    if not payload.get("ok"):
        raise CityLifeError(str(payload.get("error") or "Overpass non ha risposto"))
    rows = normalize_elements(payload, lat=lat, lon=lon)
    _cache[cache_key] = (time.time(), rows)
    return {"ok": True, "kind": cat, "rows": rows, "radius_m": radius, "cached": False}


async def fetch_air(client: httpx.AsyncClient, lat: float, lon: float) -> dict[str, Any]:
    try:
        response = await client.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": f"{lat:.4f}",
                "longitude": f"{lon:.4f}",
                "current": "european_aqi,pm2_5,pm10,nitrogen_dioxide,ozone,grass_pollen,birch_pollen",
            },
            timeout=12.0,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return {"ok": False, "current": {}}
    current = data.get("current") if isinstance(data, dict) else {}
    if not isinstance(current, dict):
        current = {}
    return {"ok": True, "current": current}


def _norm(text: str) -> str:
    return " ".join(text.lower().replace("'", " ").split())


async def fetch_meteoalarm(client: httpx.AsyncClient, country_code: str, *, city: str = "") -> dict[str, Any]:
    cc = (country_code or "").strip().lower()
    feed = _METEO_FEEDS.get(cc)
    if not feed:
        return {"ok": True, "rows": [], "supported": False}
    cache_key = f"meteoalarm:{feed}"
    hit = _cache.get(cache_key)
    if hit and time.time() - hit[0] < 1200:
        rows = list((hit[1] or {}).get("rows") or [])
        return {"ok": True, "rows": _filter_alerts(rows, city), "supported": True}
    try:
        response = await client.get(METEOALARM.format(feed=feed), timeout=18.0, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return {"ok": False, "rows": [], "supported": True}
    rows: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for item in payload.get("warnings") or []:
        if not isinstance(item, dict):
            continue
        alert = item.get("alert") if isinstance(item.get("alert"), dict) else {}
        infos = alert.get("info") or []
        if isinstance(infos, dict):
            infos = [infos]
        picked = None
        fallback = None
        for info in infos:
            if not isinstance(info, dict):
                continue
            lang = str(info.get("language") or "").lower()
            if lang.startswith("it"):
                picked = info
                break
            if fallback is None and (lang.startswith("en") or not lang):
                fallback = info
        info = picked or fallback
        if not isinstance(info, dict):
            continue
        desc = str(info.get("description") or "")
        if "No Special Awareness" in desc or "Nessuna allerta" in desc:
            continue
        severity = str(info.get("severity") or "")
        if severity.lower() in {"unknown", "none"}:
            continue
        expires_raw = str(info.get("expires") or "")
        try:
            expires = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if expires < now:
                continue
        except ValueError:
            pass
        areas = info.get("area") or []
        if isinstance(areas, dict):
            areas = [areas]
        area_names = [str(a.get("areaDesc") or "") for a in areas if isinstance(a, dict)]
        event = info.get("event") or info.get("headline") or "allerta"
        if isinstance(event, list):
            event = event[0] if event else "allerta"
        rows.append(
            {
                "event": str(event),
                "severity": severity,
                "areas": [a for a in area_names if a],
                "onset": str(info.get("onset") or info.get("effective") or "")[:16],
                "expires": expires_raw[:16],
            }
        )
    _cache[cache_key] = (time.time(), {"rows": rows})
    return {"ok": True, "rows": _filter_alerts(rows, city), "supported": True}


def _filter_alerts(rows: list[dict[str, Any]], city: str) -> list[dict[str, Any]]:
    mun = _norm(city.split(",")[0] if city else "")
    serious = [r for r in rows if str(r.get("severity") or "").lower() in {"moderate", "severe", "extreme"}]
    if mun:
        local = [r for r in serious if mun in _norm(" ".join(r.get("areas") or []))]
        if local:
            return local[:8]
    return serious[:8]


async def fetch_life(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    kind: str,
    *,
    place: str = "",
) -> dict[str, Any]:
    cat = resolve_kind(kind) or "near"
    bundle = await search_around(client, lat, lon, cat)
    now = city_now(lon=lon)
    if cat == "culture":
        rows = list(bundle.get("rows") or [])
        open_rows = [r for r in rows if is_open_now(r.get("opening_hours"), now) is True]
        rest = [r for r in rows if r not in open_rows]
        bundle["rows"] = open_rows + rest
    if cat == "near":
        air = await fetch_air(client, lat, lon)
        bundle["air"] = air.get("current") or {}
        bundle["air_ok"] = bool(air.get("ok"))
    if cat == "safety":
        alerts = await fetch_meteoalarm(client, country_hint(place), city=place)
        bundle["alerts"] = list(alerts.get("rows") or [])
        bundle["alerts_ok"] = bool(alerts.get("ok"))
        bundle["alerts_supported"] = bool(alerts.get("supported", True))
    bundle["place"] = place
    return bundle


def dump_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(item) for item in items[:MAX_ITEMS]]


def stored_items(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, dict)]


def _dist_s(row: dict[str, Any]) -> str:
    dist = row.get("dist_km")
    if not isinstance(dist, (int, float)):
        return ""
    if dist < 1:
        return f"{dist * 1000:.0f} m"
    return f"{dist:.1f} km"


def item_emoji(row: dict[str, Any]) -> str:
    return GROUP_EMOJI.get(str(row.get("group") or ""), "📍")


def item_button_label(row: dict[str, Any], index: int) -> str:
    name = str(row.get("name") or "luogo")
    dist = _dist_s(row)
    prefix = f"{index} {item_emoji(row)} "
    suffix = f" · {dist}" if dist else ""
    room = 34 - len(prefix) - len(suffix)
    if room < 4:
        suffix = ""
        room = 34 - len(prefix)
    if len(name) > room:
        name = name[: max(1, room - 1)].rstrip() + "…"
    return f"{prefix}{name}{suffix}"


def format_life_hub(*, place: str) -> str:
    where = e(place)
    lines = [
        "🏙️ <b>CITTÀ</b>",
        f"📍 <b>{where.upper()}</b>",
        "",
        "Cosa c'è intorno, da OpenStreetMap. Overpass parte solo quando scegli una categoria.",
        "",
    ]
    for key in ("near", "mobility", "safety", "culture", "services", "walk"):
        meta = KINDS[key]
        lines.append(f"{meta['emoji']} <b>{meta['it']}</b> — {meta['blurb']}")
    lines.extend(
        [
            "",
            "<i>Niente traffico TomTom, ritardi bus o posti sharing liberi: servono chiavi o feed locali. "
            f"{OSM_NOTE}</i>",
        ]
    )
    return "\n".join(lines)


def _aqi_lines(current: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    aqi = current.get("european_aqi")
    if isinstance(aqi, (int, float)):
        lines.append(f"🌬️ AQI (EEA) {int(round(aqi))}")
    for label, key, unit, digits in (
        ("PM2.5", "pm2_5", " μg/m³", 1),
        ("PM10", "pm10", " μg/m³", 1),
    ):
        val = current.get(key)
        if isinstance(val, (int, float)):
            text = f"{val:.{digits}f}" if digits else str(int(round(val)))
            lines.append(f"{label}: {text}{unit}")
    pollen = []
    for label, key in (("Erba", "grass_pollen"), ("Betulla", "birch_pollen")):
        val = current.get(key)
        if isinstance(val, (int, float)):
            pollen.append(f"{label} {val:.1f}")
    if pollen:
        lines.append("🌾 " + " · ".join(pollen))
    return lines


def format_life_list(
    *,
    kind: str,
    place: str,
    items: list[dict[str, Any]],
    page: int,
    extra: dict[str, Any] | None = None,
) -> str:
    meta = kind_meta(kind)
    extra = extra or {}
    now = city_now()
    where = e(place)
    radius = int(extra.get("radius_m") or RADIUS_M.get(kind, 1200))
    lines = [
        f"{meta['emoji']} <b>{e(meta['it'].upper())}</b>",
        f"📍 {where} · raggio {radius} m",
        f"<i>{e(meta['blurb'])}</i>",
        "",
    ]
    if kind == "near":
        if extra.get("air_ok"):
            air = _aqi_lines(extra.get("air") or {})
            lines.extend(air or ["🌬️ Qualità dell'aria: n/d"])
        else:
            lines.append("🌬️ Qualità dell'aria non disponibile in questo momento.")
        lines.append("")
    if kind == "safety":
        alerts = list(extra.get("alerts") or [])
        if extra.get("alerts_supported") is False:
            lines.append("ℹ️ Allerte Meteoalarm non coperte per questo paese.")
        elif extra.get("alerts_ok") is False:
            lines.append("⚠️ Allerte Meteoalarm non disponibili in questo momento.")
        elif not alerts:
            lines.append("✅ Nessuna allerta Meteoalarm gialla/arancione per la zona.")
        else:
            lines.append("🚨 <b>Allerte</b> (Meteoalarm)")
            for alert in alerts[:6]:
                lines.append(f"• {e(alert.get('event') or 'allerta')} · {e(alert.get('severity') or '')}")
                areas = ", ".join(alert.get("areas") or [])
                if areas:
                    lines.append(f"   📍 {e(areas)}")
        lines.append("<i>Tempi di attesa PS e farmacie di turno non sono su questo piano.</i>")
        lines.append("")
    if not items:
        lines.append("Nessun punto OSM in questo raggio.")
        lines.append("Non invento luoghi.")
        lines.append("")
        lines.append(f"<i>{OSM_NOTE}</i>")
        return "\n".join(lines)
    start = page * PAGE_SIZE
    chunk = items[start : start + PAGE_SIZE]
    for idx, row in enumerate(chunk, start=start + 1):
        bits = [e(str(row.get("kind") or "Luogo"))]
        dist = _dist_s(row)
        if dist:
            bits.append(dist)
        bits.append(_open_label(row, now))
        lines.append(f"{idx}. {item_emoji(row)} <b>{e(row.get('name') or 'luogo')}</b>")
        lines.append(" · ".join(bits))
        if row.get("operator"):
            lines.append(e(str(row["operator"])))
        lines.append("")
    leftover = max(0, len(items) - start - len(chunk))
    if leftover:
        lines.append(f"<i>Altri {leftover} in pagine successive.</i>")
        lines.append("")
    lines.append(f"<i>{OSM_NOTE}</i>")
    return "\n".join(lines)


def format_life_detail(*, place: str, item: dict[str, Any]) -> str:
    now = city_now()
    title = e(item.get("name") or "Luogo")
    kind = e(item.get("kind") or "Luogo")
    dist = _dist_s(item)
    try:
        coord = _latlon_it(float(item["lat"]), float(item["lon"]))
    except (TypeError, ValueError, KeyError):
        coord = "—"
    lines = [
        f"{item_emoji(item)} <b>{title}</b>",
        f"{kind}" + (f" · {dist}" if dist else ""),
        f"📍 {e(place)}",
        f"📍 {coord}",
        _open_label(item, now),
    ]
    if item.get("operator"):
        lines.append(f"🏢 {e(item['operator'])}")
    if item.get("cuisine"):
        lines.append(f"🍴 {e(str(item['cuisine']).replace(';', ', '))}")
    if item.get("capacity"):
        lines.append(f"👥 capienza {e(item['capacity'])}")
    if item.get("phone"):
        lines.append(f"📞 {e(item['phone'])}")
    if item.get("webcam"):
        url = str(item["webcam"])
        if url.startswith("http"):
            lines.append(f'<a href="{_html.escape(url, quote=True)}">webcam</a>')
    if item.get("website"):
        url = str(item["website"])
        if url.startswith("http"):
            lines.append(f'<a href="{_html.escape(url, quote=True)}">sito</a>')
    map_url = str(item.get("map") or "")
    if map_url.startswith("http"):
        lines.append(f'<a href="{_html.escape(map_url, quote=True)}">Apri la mappa OSM</a>')
    lines.extend(["", f"<i>{OSM_NOTE}</i>"])
    return "\n".join(line for line in lines if line)
