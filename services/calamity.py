"""Eventi & Calamità: USGS + EONET + FIRMS, foto NASA Worldview/GIBS. Niente allerte inventate."""

from __future__ import annotations

import csv
import html
import io
import math
import os
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from services.earth import (
    EONET_CAT_IT,
    EONET_WHAT,
    _coord_pairs,
    _eonet_source,
    _latlon_it,
    _mag_word,
    eonet_event_ids,
    eonet_nearest,
    fetch_eonet,
    fetch_quakes,
    fetch_quakes_near,
    haversine_km,
)
from services.satimages import DEFAULT_LAYER, fetch_sat_view, stamp_target_photo

ROME = ZoneInfo("Europe/Rome")

CALAM_CATS: dict[str, dict[str, Any]] = {
    "quake": {
        "it": "Terremoti LIVE",
        "btn": "Terremoti",
        "emoji": "🌋",
        "src": "USGS FDSN",
        "layer": "vii",
        "eonet": None,
        "near_km": 500.0,
        "blurb": "Scosse misurate. Non è un'allerta della protezione civile.",
    },
    "fire": {
        "it": "Incendi LIVE",
        "btn": "Incendi",
        "emoji": "🔥",
        "src": "NASA FIRMS + EONET",
        "layer": "fire",
        "eonet": "wildfires",
        "near_km": 500.0,
        "blurb": "Rilevamenti satellitari e incendi ancora aperti nel catalogo NASA.",
    },
    "storm": {
        "it": "Tempeste",
        "btn": "Tempeste",
        "emoji": "🌪️",
        "src": "NASA EONET",
        "layer": "vii",
        "eonet": "severeStorms",
        "near_km": 2000.0,
        "blurb": "Cicloni, tifoni e tempeste ancora aperti. L'ultimo punto del tracciato.",
    },
    "volc": {
        "it": "Vulcani",
        "btn": "Vulcani",
        "emoji": "🌋",
        "src": "NASA EONET",
        "layer": "false",
        "eonet": "volcanoes",
        "near_km": 2000.0,
        "blurb": "Attività vulcanica che NASA sta ancora seguendo. Non dice se erutterà.",
    },
    "flood": {
        "it": "Alluvioni",
        "btn": "Alluvioni",
        "emoji": "🌊",
        "src": "NASA EONET",
        "layer": "false",
        "eonet": "floods",
        "near_km": 800.0,
        "blurb": "Alluvioni ancora aperte nel tracciatore NASA.",
    },
    "slide": {
        "it": "Frane",
        "btn": "Frane",
        "emoji": "🪨",
        "src": "NASA EONET",
        "layer": "terra",
        "eonet": "landslides",
        "near_km": 800.0,
        "blurb": "Frane segnalate come ancora aperte.",
    },
    "dust": {
        "it": "Polvere / fumo",
        "btn": "Polvere",
        "emoji": "🌫️",
        "src": "NASA EONET",
        "layer": "false",
        "eonet": "dustHaze",
        "near_km": 1500.0,
        "blurb": "Polvere o caligine ancora aperta nel catalogo NASA.",
    },
}

CALAM_KEYS = tuple(CALAM_CATS)
PAGE_SIZE = 5
MAX_ITEMS = 20
HUB_NEAR_KM = 500.0

FIRMS_CSV = (
    "https://firms.modaps.eosdis.nasa.gov/data/active_fire/"
    "{family}/csv/{file}_{area}_24h.csv"
)
FIRMS_AREA_API = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{src}/{west},{south},{east},{north}/1"

FIRMS_REGIONS: tuple[tuple[str, float, float, float, float], ...] = (
    ("Europe", 34.0, 72.0, -25.0, 45.0),
    ("North_America", 15.0, 72.0, -170.0, -50.0),
    ("Central_America", 5.0, 25.0, -120.0, -58.0),
    ("South_America", -56.0, 15.0, -82.0, -34.0),
    ("Northern_and_Central_Africa", 5.0, 38.0, -20.0, 52.0),
    ("Southern_Africa", -36.0, 5.0, -20.0, 52.0),
    ("South_Asia", 5.0, 40.0, 60.0, 100.0),
    ("SouthEast_Asia", -10.0, 28.0, 95.0, 155.0),
    ("Australia_NewZealand", -48.0, -10.0, 110.0, 180.0),
    ("Russia_Asia", 45.0, 80.0, 40.0, 180.0),
)


def calam_meta(key: str) -> dict[str, Any]:
    return CALAM_CATS.get(key) or CALAM_CATS["quake"]


def bbox_around(lat: float, lon: float, km: float) -> str:
    dlat = km / 111.0
    cos_lat = max(0.2, math.cos(math.radians(lat)))
    dlon = km / (111.0 * cos_lat)
    west = max(-180.0, lon - dlon)
    east = min(180.0, lon + dlon)
    south = max(-85.0, lat - dlat)
    north = min(85.0, lat + dlat)
    return f"{west:.3f},{south:.3f},{east:.3f},{north:.3f}"


def _parse_dt(raw: Any) -> datetime | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)):
        try:
            return datetime.fromtimestamp(float(raw) / (1000.0 if float(raw) > 1e11 else 1.0), tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            return None
    text = str(raw).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def ago_it(when: datetime | None) -> str:
    if when is None:
        return "—"
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    sec = int((datetime.now(timezone.utc) - when.astimezone(timezone.utc)).total_seconds())
    if sec < 0:
        sec = 0
    if sec < 60:
        return "adesso"
    if sec < 3600:
        return f"{sec // 60} min fa"
    if sec < 86400:
        hours, minutes = divmod(sec // 60, 60)
        return f"{hours}h {minutes:02d}m" if minutes else f"{hours}h"
    days = sec // 86400
    return f"{days} g fa"


def mag_dot(mag: float | None) -> str:
    if mag is None:
        return "⚪"
    if mag >= 5:
        return "🔴"
    if mag >= 4:
        return "🟠"
    if mag >= 3:
        return "🟡"
    return "🟢"


def firms_area(lat: float, lon: float) -> str:
    for name, south, north, west, east in FIRMS_REGIONS:
        if south <= lat <= north and west <= lon <= east:
            return name
    return "Europe"


def _firms_point(row: dict[str, str]) -> dict[str, Any] | None:
    try:
        lat = float(row.get("latitude") or "")
        lon = float(row.get("longitude") or "")
    except ValueError:
        return None
    conf = str(row.get("confidence") or "").strip().lower()
    if conf in {"l", "low"}:
        return None
    day = str(row.get("acq_date") or "").strip()
    clock = str(row.get("acq_time") or "0000").strip().zfill(4)
    when = None
    if day:
        try:
            when = datetime.strptime(f"{day}{clock}", "%Y-%m-%d%H%M").replace(tzinfo=timezone.utc)
        except ValueError:
            when = _parse_dt(day)
    sat = str(row.get("satellite") or row.get("instrument") or "VIIRS").strip() or "VIIRS"
    return {"lat": lat, "lon": lon, "when": when, "sat": sat}


def cluster_firms(points: list[dict[str, Any]], *, cell: float = 0.35) -> list[dict[str, Any]]:
    buckets: dict[tuple[int, int], dict[str, Any]] = {}
    for point in points:
        key = (round(float(point["lat"]) / cell), round(float(point["lon"]) / cell))
        bucket = buckets.get(key)
        if bucket is None:
            bucket = {
                "lats": [],
                "lons": [],
                "n": 0,
                "when": point.get("when"),
                "sat": str(point.get("sat") or "VIIRS"),
            }
            buckets[key] = bucket
        bucket["lats"].append(float(point["lat"]))
        bucket["lons"].append(float(point["lon"]))
        bucket["n"] += 1
        stamp = point.get("when")
        if isinstance(stamp, datetime) and (
            bucket["when"] is None or stamp > bucket["when"]
        ):
            bucket["when"] = stamp
            bucket["sat"] = str(point.get("sat") or bucket["sat"])
    rows: list[dict[str, Any]] = []
    for bucket in buckets.values():
        n = int(bucket["n"])
        lat = sum(bucket["lats"]) / n
        lon = sum(bucket["lons"]) / n
        rows.append(
            {
                "kind": "firms",
                "title": f"{n} rilevamenti VIIRS",
                "lat": lat,
                "lon": lon,
                "count": n,
                "sensor": str(bucket["sat"] or "VIIRS"),
                "when": bucket["when"],
                "src": "NASA FIRMS",
                "url": "https://firms.modaps.eosdis.nasa.gov/",
            }
        )
    rows.sort(key=lambda row: (-int(row["count"]), row.get("dist_km") or 0))
    return rows


async def fetch_firms_points(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    *,
    radius_km: float = 500.0,
) -> list[dict[str, Any]]:
    key = str(os.environ.get("FIRMS_MAP_KEY") or "").strip()
    if key:
        dlat = radius_km / 111.0
        dlon = radius_km / (111.0 * max(0.2, math.cos(math.radians(lat))))
        url = FIRMS_AREA_API.format(
            key=key,
            src="VIIRS_SNPP_NRT",
            west=f"{lon - dlon:.3f}",
            south=f"{lat - dlat:.3f}",
            east=f"{lon + dlon:.3f}",
            north=f"{lat + dlat:.3f}",
        )
        response = await client.get(url)
        response.raise_for_status()
        text = response.text
        if text.lstrip().startswith("<") or "Invalid" in text[:80]:
            raise ValueError("FIRMS MAP_KEY non usabile")
    else:
        area = firms_area(lat, lon)
        url = FIRMS_CSV.format(
            family="suomi-npp-viirs-c2",
            file="SUOMI_VIIRS_C2",
            area=area,
        )
        response = await client.get(url)
        response.raise_for_status()
        text = response.text
    reader = csv.DictReader(io.StringIO(text))
    points: list[dict[str, Any]] = []
    for row in reader:
        point = _firms_point(row)
        if point is None:
            continue
        dist = haversine_km(lat, lon, point["lat"], point["lon"])
        if dist > radius_km:
            continue
        point["dist_km"] = dist
        points.append(point)
    return points


def _compact_quake(item: dict[str, Any], origin_lat: float, origin_lon: float) -> dict[str, Any] | None:
    props = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    geom = item.get("geometry") if isinstance(item.get("geometry"), dict) else {}
    coords = geom.get("coordinates") if isinstance(geom.get("coordinates"), list) else []
    if len(coords) < 2:
        return None
    try:
        ev_lon, ev_lat = float(coords[0]), float(coords[1])
    except (TypeError, ValueError):
        return None
    try:
        mag = float(props.get("mag"))
    except (TypeError, ValueError):
        mag = None
    depth = None
    if len(coords) > 2:
        try:
            depth = float(coords[2])
        except (TypeError, ValueError):
            depth = None
    when = _parse_dt(props.get("time"))
    return {
        "kind": "quake",
        "id": str(item.get("id") or props.get("code") or ""),
        "title": str(props.get("place") or "scossa"),
        "lat": ev_lat,
        "lon": ev_lon,
        "dist_km": haversine_km(origin_lat, origin_lon, ev_lat, ev_lon),
        "mag": mag,
        "depth": depth,
        "when": when,
        "src": "USGS",
        "url": str(props.get("url") or ""),
    }


def _compact_eonet(event: dict[str, Any], origin_lat: float, origin_lon: float) -> dict[str, Any] | None:
    nearest = eonet_nearest(event, origin_lat, origin_lon)
    geometries = event.get("geometry") if isinstance(event.get("geometry"), list) else []
    latest = geometries[-1] if geometries and isinstance(geometries[-1], dict) else {}
    pairs = []
    if nearest:
        ev_lat, ev_lon, dist = nearest
    else:
        pairs = _coord_pairs(latest.get("coordinates")) if latest else []
        if not pairs:
            return None
        ev_lat, ev_lon = pairs[-1]
        dist = haversine_km(origin_lat, origin_lon, ev_lat, ev_lon)
    cats = eonet_event_ids(event)
    cat = next(iter(cats), "")
    url, _label = _eonet_source(event)
    mag = latest.get("magnitudeValue")
    try:
        mag_f = float(mag) if mag not in {None, ""} else None
    except (TypeError, ValueError):
        mag_f = None
    return {
        "kind": "eonet",
        "id": str(event.get("id") or ""),
        "title": str(event.get("title") or "Evento"),
        "lat": ev_lat,
        "lon": ev_lon,
        "dist_km": dist,
        "when": _parse_dt(latest.get("date")),
        "src": "NASA EONET",
        "url": url or str(event.get("link") or ""),
        "cat": cat,
        "what": EONET_WHAT.get(cat, "Fenomeno ancora aperto nel tracciatore NASA."),
        "cat_it": EONET_CAT_IT.get(cat, cat or "evento"),
        "mag": mag_f,
        "mag_u": str(latest.get("magnitudeUnit") or ""),
    }


def _with_dist(item: dict[str, Any], origin_lat: float, origin_lon: float) -> dict[str, Any]:
    if item.get("dist_km") is None:
        item["dist_km"] = haversine_km(origin_lat, origin_lon, float(item["lat"]), float(item["lon"]))
    return item


def _serialize_when(item: dict[str, Any]) -> dict[str, Any]:
    when = item.get("when")
    if isinstance(when, datetime):
        item = dict(item)
        item["when"] = when.astimezone(timezone.utc).isoformat()
    return item


def _hydrate_when(item: dict[str, Any]) -> dict[str, Any]:
    item = dict(item)
    when = item.get("when")
    if isinstance(when, str):
        item["when"] = _parse_dt(when)
    return item


def stored_items(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    return [_hydrate_when(item) for item in raw if isinstance(item, dict)]


def dump_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_serialize_when(item) for item in items[:MAX_ITEMS]]


async def load_calam_items(
    client: httpx.AsyncClient,
    key: str,
    *,
    lat: float,
    lon: float,
    scope: str = "n",
) -> list[dict[str, Any]]:
    meta = calam_meta(key)
    near_km = float(meta["near_km"])
    items: list[dict[str, Any]] = []
    if key == "quake":
        if scope == "w":
            data = await fetch_quakes(client, "sig")
        else:
            data = await fetch_quakes_near(
                client, lat, lon, radius_km=near_km, minmagnitude=2.5, days=14, limit=MAX_ITEMS
            )
        features = data.get("features") if isinstance(data.get("features"), list) else []
        for feature in features:
            if isinstance(feature, dict):
                row = _compact_quake(feature, lat, lon)
                if row is not None:
                    items.append(row)
        if scope == "n":
            items = [row for row in items if float(row.get("dist_km") or 0) <= near_km]
        items.sort(key=lambda row: float(row.get("dist_km") or 0) if scope == "n" else 0)
        if scope == "w":
            items.sort(key=lambda row: row.get("when") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return items[:MAX_ITEMS]

    if key == "fire" and scope == "n":
        try:
            points = await fetch_firms_points(client, lat, lon, radius_km=near_km)
            for cluster in cluster_firms(points):
                items.append(_with_dist(cluster, lat, lon))
        except Exception:
            points = []
            items = []

    eonet_cat = str(meta.get("eonet") or "")
    bbox = bbox_around(lat, lon, near_km) if scope == "n" and key != "storm" else None
    # Tempeste: bbox stretto taglia i cicloni oceanici; vicino = distanza sul punto.
    if key == "storm" and scope == "n":
        bbox = None
    try:
        data = await fetch_eonet(
            client,
            limit=40 if scope == "w" else 30,
            category=eonet_cat or None,
            bbox=bbox,
        )
    except Exception:
        data = {"events": []}
    events = data.get("events") if isinstance(data.get("events"), list) else []
    for event in events:
        if not isinstance(event, dict):
            continue
        row = _compact_eonet(event, lat, lon)
        if row is None:
            continue
        if scope == "n" and float(row.get("dist_km") or 99999) > near_km:
            continue
        items.append(row)
    items.sort(key=lambda row: (float(row.get("dist_km") or 0), -(row.get("count") or 0)))
    return items[:MAX_ITEMS]


async def hub_counts(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
) -> dict[str, int]:
    counts = {key: 0 for key in CALAM_KEYS}
    try:
        quakes = await fetch_quakes_near(client, lat, lon, radius_km=HUB_NEAR_KM, limit=20)
        features = quakes.get("features") if isinstance(quakes.get("features"), list) else []
        counts["quake"] = sum(1 for item in features if isinstance(item, dict))
    except Exception:
        counts["quake"] = 0
    try:
        data = await fetch_eonet(client, limit=50)
        events = data.get("events") if isinstance(data.get("events"), list) else []
    except Exception:
        events = []
    cat_to_key = {
        "wildfires": "fire",
        "severeStorms": "storm",
        "volcanoes": "volc",
        "floods": "flood",
        "landslides": "slide",
        "dustHaze": "dust",
    }
    for event in events:
        if not isinstance(event, dict):
            continue
        nearest = eonet_nearest(event, lat, lon)
        if nearest is None or nearest[2] > HUB_NEAR_KM:
            continue
        for cid in eonet_event_ids(event):
            mapped = cat_to_key.get(cid)
            if mapped:
                counts[mapped] += 1
    try:
        points = await fetch_firms_points(client, lat, lon, radius_km=HUB_NEAR_KM)
        if points:
            counts["fire"] = max(counts["fire"], len(cluster_firms(points)[:MAX_ITEMS]))
    except Exception:
        pass
    return counts


def format_calam_hub(
    *,
    place: str,
    counts: dict[str, int],
) -> str:
    total = sum(int(counts.get(key) or 0) for key in CALAM_KEYS)
    where = html.escape(place, quote=False)
    if total:
        pulse = f"🔴 <b>{total}</b> eventi nelle vicinanze (circa {HUB_NEAR_KM:.0f} km)"
    else:
        pulse = f"Nessun evento aperto entro circa {HUB_NEAR_KM:.0f} km da {where}."
    bits = [f"{calam_meta(key)['emoji']} {int(counts.get(key) or 0)}" for key in CALAM_KEYS]
    return "\n".join(
        [
            "🌋 <b>EVENTI E CALAMITÀ</b>",
            f"📍 <b>{where.upper()}</b>",
            pulse,
            " · ".join(bits),
            "",
            "USGS per le scosse. NASA EONET per i fenomeni aperti. "
            "FIRMS (VIIRS) per i fuochi vicini. La foto è NASA Worldview / GIBS.",
            "",
            "<i>Non è un bollettino della protezione civile. Se i feed sono vuoti, non invento.</i>",
        ]
    )


def _item_when_bit(item: dict[str, Any]) -> str:
    when = item.get("when")
    if isinstance(when, datetime):
        return ago_it(when)
    if isinstance(when, str):
        parsed = _parse_dt(when)
        return ago_it(parsed) if parsed else "—"
    return "—"


def format_calam_list(
    *,
    key: str,
    place: str,
    scope: str,
    items: list[dict[str, Any]],
    page: int,
) -> str:
    meta = calam_meta(key)
    where = html.escape(place, quote=False)
    area = "mondo" if scope == "w" else f"raggio {meta['near_km']:.0f} km"
    lines = [
        f"{meta['emoji']} <b>{html.escape(str(meta['it']).upper(), quote=False)}</b>",
        f"📍 {where} · {area}",
        f"<i>{html.escape(str(meta['blurb']), quote=False)}</i>",
        "",
    ]
    if not items:
        if scope == "n":
            lines.append(f"Entro il raggio da {where} i feed non hanno eventi aperti.")
        else:
            lines.append("In questo momento i feed non segnalano eventi aperti.")
        lines.append("Non invento fenomeni.")
        lines.extend(["", f"<i>{html.escape(str(meta['src']), quote=False)}.</i>"])
        return "\n".join(lines)
    start = page * PAGE_SIZE
    chunk = items[start : start + PAGE_SIZE]
    for idx, item in enumerate(chunk, start=start + 1):
        lines.append(_list_line(key, item, idx))
        lines.append("")
    leftover = max(0, len(items) - start - len(chunk))
    if leftover:
        lines.append(f"<i>Altri {leftover} in pagine successive.</i>")
        lines.append("")
    lines.append(f"<i>{html.escape(str(meta['src']), quote=False)}. Distanza in linea d'aria.</i>")
    return "\n".join(lines)


def _list_line(key: str, item: dict[str, Any], index: int) -> str:
    title = html.escape(str(item.get("title") or "evento"), quote=False)
    dist = item.get("dist_km")
    dist_s = f"{float(dist):.0f} km" if isinstance(dist, (int, float)) else "—"
    when_s = _item_when_bit(item)
    if key == "quake":
        mag = item.get("mag")
        mag_s = f"{float(mag):.1f}" if isinstance(mag, (int, float)) else "—"
        depth = item.get("depth")
        depth_s = f"{float(depth):.0f} km" if isinstance(depth, (int, float)) else "—"
        return (
            f"{index}. {mag_dot(float(mag) if isinstance(mag, (int, float)) else None)} "
            f"<b>M {mag_s}</b> — {title}\n"
            f"📏 {dist_s} · ⬇️ {depth_s} · 🕐 {when_s}"
        )
    if item.get("kind") == "firms":
        sensor = html.escape(str(item.get("sensor") or "VIIRS"), quote=False)
        n = int(item.get("count") or 0)
        return (
            f"{index}. 🔥 <b>{title}</b>\n"
            f"📏 {dist_s} · 🕐 {when_s} · 🛰️ {sensor}"
            + (f" · {n} punti" if n else "")
        )
    return (
        f"{index}. {calam_meta(key)['emoji']} <b>{title}</b>\n"
        f"📏 {dist_s} · 🕐 {when_s}"
    )


def format_calam_detail(
    *,
    key: str,
    place: str,
    item: dict[str, Any],
) -> str:
    meta = calam_meta(key)
    where = html.escape(place, quote=False)
    title = html.escape(str(item.get("title") or "Evento"), quote=False)
    dist = item.get("dist_km")
    dist_s = f"{float(dist):.0f} km da {where}" if isinstance(dist, (int, float)) else "—"
    when = item.get("when") if isinstance(item.get("when"), datetime) else _parse_dt(item.get("when"))
    when_s = ago_it(when)
    clock = ""
    if isinstance(when, datetime):
        local = when.astimezone(ROME)
        clock = f"{local.day:02d}/{local.month:02d} {local.hour:02d}:{local.minute:02d}"
    try:
        coord = _latlon_it(float(item["lat"]), float(item["lon"]))
    except (TypeError, ValueError, KeyError):
        coord = "—"
    lines = [
        f"{meta['emoji']} <b>{html.escape(str(meta['it']).upper(), quote=False)}</b>",
        f"<b>{title}</b>",
        f"📍 {coord}",
        f"📏 {dist_s}",
        f"🕐 {when_s}" + (f" · {clock}" if clock else ""),
    ]
    if key == "quake":
        mag = item.get("mag")
        if isinstance(mag, (int, float)):
            lines.append(f"{mag_dot(float(mag))} M {float(mag):.1f} · {_mag_word(float(mag))}")
        depth = item.get("depth")
        if isinstance(depth, (int, float)):
            lines.append(f"⬇️ {float(depth):.0f} km sotto terra")
    if item.get("kind") == "firms":
        lines.append(f"🛰️ {html.escape(str(item.get('sensor') or 'VIIRS'), quote=False)}")
        if item.get("count"):
            lines.append(f"🔥 {int(item['count'])} rilevamenti nell'ultimo giorno (cluster)")
    what = item.get("what")
    if what:
        lines.append(html.escape(str(what), quote=False))
    mag_u = item.get("mag_u")
    if item.get("mag") not in {None, ""} and mag_u:
        lines.append(f"Misura nel feed: {html.escape(str(item['mag']), quote=False)} {html.escape(str(mag_u), quote=False)}")
    url = str(item.get("url") or "").strip()
    if url.startswith("http"):
        label = "Apri la scheda USGS" if item.get("kind") == "quake" else "Apri la fonte"
        if item.get("kind") == "firms":
            label = "Apri NASA FIRMS"
        lines.append(f'<a href="{html.escape(url, quote=True)}">{label}</a>')
    lines.extend(
        [
            "",
            f"<i>{html.escape(str(item.get('src') or meta['src']), quote=False)}. "
            "La foto è NASA Worldview / GIBS sul punto, non un allarme.</i>",
        ]
    )
    return "\n".join(lines)


def format_calam_caption(
    *,
    key: str,
    place: str,
    item: dict[str, Any] | None,
    note: str,
    kind: str,
) -> str:
    meta = calam_meta(key)
    where = html.escape(place, quote=False)
    view = "Mappa" if kind == "map" else "Satellite"
    if item is None:
        return (
            f"🛰️ <b>VISTA SATELLITARE</b>\n"
            f"📍 <b>{where}</b>\n"
            f"{html.escape(note or 'NASA Worldview / GIBS', quote=False)}\n"
            "<i>Luogo della cartella Eventi. Non è Osservazione Terra dei satelliti.</i>"
        )
    title = html.escape(str(item.get("title") or meta["it"]), quote=False)
    dist = item.get("dist_km")
    dist_s = f"{float(dist):.0f} km da {where}" if isinstance(dist, (int, float)) else where
    return (
        f"{meta['emoji']} <b>{html.escape(str(meta['it']).upper(), quote=False)}</b>\n"
        f"<b>{title}</b>\n"
        f"📏 {dist_s} · 🕐 {_item_when_bit(item)}\n"
        f"🛰️ {view} · {html.escape(note or 'NASA Worldview / GIBS', quote=False)}"
    )


def item_button_label(key: str, item: dict[str, Any], index: int) -> str:
    if key == "quake" and isinstance(item.get("mag"), (int, float)):
        core = f"M {float(item['mag']):.1f}"
    else:
        core = str(item.get("title") or "evento")
    dist = item.get("dist_km")
    if isinstance(dist, (int, float)):
        core = f"{core} · {float(dist):.0f} km"
    label = f"{index} {core}"
    return label[:34]


async def fetch_event_view(
    client: httpx.AsyncClient,
    *,
    key: str,
    item: dict[str, Any] | None,
    place: str,
    lat: float,
    lon: float,
    kind: str = "sat",
) -> dict[str, Any]:
    meta = calam_meta(key) if item is not None else {"layer": DEFAULT_LAYER, "it": "Vista satellitare"}
    layer = str(meta.get("layer") or DEFAULT_LAYER)
    span = 5.2 if kind == "map" else 2.2
    ev_lat, ev_lon = lat, lon
    title = place
    if item is not None:
        try:
            ev_lat = float(item["lat"])
            ev_lon = float(item["lon"])
        except (TypeError, ValueError, KeyError):
            ev_lat, ev_lon = lat, lon
        title = str(item.get("title") or place)
    view = await fetch_sat_view(client, layer, ev_lat, ev_lon, place="", span=span)
    data = view.get("bytes")
    if isinstance(data, (bytes, bytearray)) and data:
        label = str(view.get("note") or "NASA Worldview / GIBS")
        view["bytes"] = stamp_target_photo(bytes(data), title, label)
    return view
