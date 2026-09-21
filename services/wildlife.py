"""Fauna: osservati recenti (iNaturalist, GBIF, eBird). Niente zoo inventato e niente tag satellitari."""

from __future__ import annotations

import html as _html
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from services.calamity import ago_it
from services.earth import haversine_km, _latlon_it

INAT_URL = "https://api.inaturalist.org/v1/observations"
GBIF_OCC = "https://api.gbif.org/v1/occurrence/search"
GBIF_SPECIES = "https://api.gbif.org/v1/species/search"
GBIF_VERN = "https://api.gbif.org/v1/species/{key}/vernacularNames"
GBIF_MATCH = "https://api.gbif.org/v1/species/match"
EBIRD_GEO = "https://api.ebird.org/v2/data/obs/geo/recent"

ANIMALIA = 1
AVES = 212
NEAR_KM = 100.0
PAGE_SIZE = 5
MAX_ITEMS = 18
INAT_DAYS = 21
INAT_POOL = 40
RECENT_DAYS = 45
BIRD_CAP = 5
_PARK_TOKENS = ("parc", "parco", "park", "riserva", "national", "mercantour")
MOVEBANK_ORG = "143650ce-d186-4a3f-b6e5-c45572dcc0a8"
INAT_HEADERS = {"User-Agent": "StelleBot/1.0 (Telegram; educational; iNaturalist observations)"}

FAUNA_VIEWS = {
    "bird": {
        "it": "Uccelli vicino",
        "emoji": "🐦",
        "blurb": "Osservazioni recenti di uccelli, non collari GPS.",
    },
    "obs": {
        "it": "Osservati recenti",
        "emoji": "🐾",
        "blurb": "Avvistamenti iNaturalist, GBIF e eBird intorno al luogo — anche i parchi vicini. Qualcuno li ha visti: non è il GPS dell'animale.",
    },
    "trk": {
        "it": "Animali tracciati",
        "emoji": "🛰️",
        "blurb": "Punti da studi con sensore/collare pubblicati. Non è un radar di tutta la fauna.",
    },
    "world": {
        "it": "Fauna nel mondo",
        "emoji": "🌍",
        "blurb": "Avvistamenti recenti nel mondo, iNaturalist. Non sono collari GPS.",
    },
    "find": {
        "it": "Cerca specie",
        "emoji": "🔎",
        "blurb": "Nome italiano o scientifico. Poi le osservazioni vicine, se ci sono.",
    },
}


class WildlifeError(RuntimeError):
    """Feed animali non usabile."""


def fauna_meta(view: str) -> dict[str, str]:
    return FAUNA_VIEWS.get(view) or FAUNA_VIEWS["obs"]


def _parse_when(raw: Any) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    if "T" not in text and len(text) >= 10:
        text = text[:10] + "T00:00:00+00:00"
    try:
        when = datetime.fromisoformat(text)
    except ValueError:
        try:
            when = datetime.fromisoformat(text[:32])
        except ValueError:
            return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when


def _compact_inat(
    item: dict[str, Any],
    *,
    origin_lat: float | None = None,
    origin_lon: float | None = None,
    kind: str = "obs",
) -> dict[str, Any] | None:
    taxon = item.get("taxon") if isinstance(item.get("taxon"), dict) else {}
    rank = str(taxon.get("rank") or "").lower()
    if rank not in {"species", "subspecies", "variety", "hybrid"}:
        return None
    name = str(taxon.get("preferred_common_name") or taxon.get("name") or "").strip()
    if not name:
        return None
    geo = item.get("geojson") if isinstance(item.get("geojson"), dict) else {}
    coords = geo.get("coordinates") if isinstance(geo.get("coordinates"), list) else []
    lat = lon = None
    if len(coords) >= 2:
        try:
            lon, lat = float(coords[0]), float(coords[1])
        except (TypeError, ValueError):
            lat = lon = None
    photo = ""
    photos = item.get("photos") if isinstance(item.get("photos"), list) else []
    if photos and isinstance(photos[0], dict):
        photo = str(photos[0].get("url") or "").replace("square", "medium")
    dist = None
    if lat is not None and lon is not None and origin_lat is not None and origin_lon is not None:
        dist = haversine_km(origin_lat, origin_lon, lat, lon)
    return {
        "kind": kind,
        "title": name,
        "sci": str(taxon.get("name") or ""),
        "taxon": taxon.get("id"),
        "place": str(item.get("place_guess") or ""),
        "when": _parse_when(item.get("time_observed_at") or item.get("observed_on")),
        "lat": lat,
        "lon": lon,
        "dist_km": dist,
        "url": str(item.get("uri") or ""),
        "photo": photo,
        "src": "iNaturalist",
        "iconic": str(taxon.get("iconic_taxon_name") or ""),
    }


async def fetch_inat_obs(
    client: httpx.AsyncClient,
    *,
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float = NEAR_KM,
    days: int | None = None,
    limit: int = MAX_ITEMS,
    kind: str = "obs",
    iconic: str = "Animalia",
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "iconic_taxa": iconic,
        "lrank": "species",
        "order": "desc",
        "order_by": "observed_on",
        "per_page": str(max(limit * 3, 30)),
        "photos": "true",
        "locale": "it",
        "captive": "false",
    }
    if lat is not None and lon is not None:
        params["lat"] = f"{lat:.4f}"
        params["lng"] = f"{lon:.4f}"
        params["radius"] = f"{min(500.0, max(1.0, radius_km)):.0f}"
    if days is not None:
        params["d1"] = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    try:
        response = await client.get(INAT_URL, params=params, headers=INAT_HEADERS)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise WildlifeError("iNaturalist non ha risposto") from exc
    rows = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise WildlifeError("iNaturalist vuoto")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in rows:
        if not isinstance(item, dict):
            continue
        packed = _compact_inat(item, origin_lat=lat, origin_lon=lon, kind=kind)
        if packed is None:
            continue
        key = str(packed.get("sci") or packed.get("title") or "").casefold()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(packed)
        if len(out) >= limit:
            break
    return out


async def recent_animals(client: httpx.AsyncClient, *, limit: int = 8) -> list[dict[str, Any]]:
    out = await fetch_inat_obs(client, limit=limit, kind="world")
    if not out:
        raise WildlifeError("Nessun avvistamento in questo giro")
    return out


def format_animals_card(rows: list[dict[str, Any]]) -> str:
    return format_fauna_list(view="world", place="mondo", items=rows, page=0)


def _photo_of(occ: dict[str, Any]) -> str:
    media = occ.get("media") if isinstance(occ.get("media"), list) else []
    for item in media:
        if not isinstance(item, dict):
            continue
        if str(item.get("type") or "") != "StillImage":
            continue
        url = str(item.get("identifier") or item.get("references") or "")
        if url.startswith("http"):
            return url
    return ""


def _compact_occ(
    occ: dict[str, Any],
    *,
    origin_lat: float,
    origin_lon: float,
    kind: str,
    src: str,
) -> dict[str, Any] | None:
    try:
        lat = float(occ.get("decimalLatitude"))
        lon = float(occ.get("decimalLongitude"))
    except (TypeError, ValueError):
        return None
    sci = str(occ.get("species") or occ.get("scientificName") or "").strip()
    title = str(occ.get("vernacularName") or sci or "animale").strip()
    when = _parse_when(occ.get("eventDate") or occ.get("dateIdentified"))
    return {
        "kind": kind,
        "title": title,
        "sci": sci,
        "taxon": occ.get("taxonKey") or occ.get("speciesKey"),
        "place": str(occ.get("locality") or occ.get("stateProvince") or occ.get("country") or ""),
        "when": when,
        "lat": lat,
        "lon": lon,
        "dist_km": haversine_km(origin_lat, origin_lon, lat, lon),
        "url": f"https://www.gbif.org/occurrence/{occ.get('key')}" if occ.get("key") else "",
        "photo": _photo_of(occ),
        "src": src,
        "dataset": str(occ.get("datasetName") or ""),
    }


async def _vernacular_it(client: httpx.AsyncClient, taxon: Any, sci: str) -> str:
    if taxon in {None, ""}:
        return ""
    try:
        response = await client.get(GBIF_VERN.format(key=int(taxon)), params={"limit": 40})
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("results") if isinstance(payload, dict) else []
    except Exception:
        rows = []
    if not isinstance(rows, list):
        rows = []
    for lang in ("ita", "it"):
        for row in rows:
            if not isinstance(row, dict):
                continue
            if str(row.get("language") or "").lower() not in {lang}:
                continue
            name = str(row.get("vernacularName") or "").strip()
            if name:
                return name
    try:
        response = await client.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": sci, "locale": "it", "rank": "species"},
        )
        response.raise_for_status()
        results = response.json().get("results") if isinstance(response.json(), dict) else []
        if results and isinstance(results[0], dict):
            return str(results[0].get("preferred_common_name") or "").strip()
    except Exception:
        return ""
    return ""


async def _name_items(client: httpx.AsyncClient, items: list[dict[str, Any]]) -> None:
    seen: dict[str, str] = {}
    for item in items[:8]:
        sci = str(item.get("sci") or "")
        if not sci:
            continue
        if sci in seen:
            if seen[sci]:
                item["title"] = seen[sci]
            continue
        label = await _vernacular_it(client, item.get("taxon"), sci)
        seen[sci] = label
        if label:
            item["title"] = label


async def fetch_gbif_near(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    *,
    taxon_key: int = ANIMALIA,
    radius_km: float = NEAR_KM,
    days: int = RECENT_DAYS,
    limit: int = MAX_ITEMS,
    kind: str = "obs",
    extra: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    start = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    end = datetime.now(timezone.utc).date().isoformat()
    params: dict[str, Any] = {
        "taxonKey": taxon_key,
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
        "geoDistance": f"{lat:.4f},{lon:.4f},{radius_km:.0f}km",
        "eventDate": f"{start},{end}",
        "limit": limit,
    }
    if extra:
        params.update(extra)
    response = await client.get(GBIF_OCC, params=params)
    response.raise_for_status()
    data = response.json()
    rows = data.get("results") if isinstance(data, dict) else []
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for occ in rows or []:
        if not isinstance(occ, dict):
            continue
        item = _compact_occ(occ, origin_lat=lat, origin_lon=lon, kind=kind, src="GBIF")
        if item is None:
            continue
        key = str(item.get("sci") or item.get("title"))
        if key.casefold() in seen:
            continue
        seen.add(key.casefold())
        items.append(item)
    await _name_items(client, items)
    items.sort(key=lambda row: float(row.get("dist_km") or 0))
    return items


async def fetch_ebird_near(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    *,
    radius_km: float = NEAR_KM,
) -> list[dict[str, Any]] | None:
    key = str(os.environ.get("EBIRD_API_KEY") or "").strip()
    if not key:
        return None
    response = await client.get(
        EBIRD_GEO,
        params={"lat": f"{lat:.4f}", "lng": f"{lon:.4f}", "dist": f"{min(50, radius_km):.0f}", "back": 14},
        headers={"X-eBirdApiToken": key},
    )
    if response.status_code >= 400:
        return None
    rows = response.json()
    if not isinstance(rows, list):
        return None
    items: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            ev_lat = float(row.get("lat"))
            ev_lon = float(row.get("lng"))
        except (TypeError, ValueError):
            continue
        items.append(
            {
                "kind": "bird",
                "title": str(row.get("comName") or row.get("sciName") or "uccello"),
                "sci": str(row.get("sciName") or ""),
                "place": str(row.get("locName") or ""),
                "when": _parse_when(row.get("obsDt")),
                "lat": ev_lat,
                "lon": ev_lon,
                "dist_km": haversine_km(lat, lon, ev_lat, ev_lon),
                "url": "",
                "photo": "",
                "src": "eBird",
                "count": row.get("howMany"),
            }
        )
        if len(items) >= MAX_ITEMS:
            break
    items.sort(key=lambda row: float(row.get("dist_km") or 0))
    return items


async def fetch_tracked(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
) -> tuple[list[dict[str, Any]], str]:
    note = (
        "Movebank non apre i live feed senza permesso. "
        "Mostro punti di studi con collare/sensore già pubblicati su GBIF, se ci sono."
    )
    near = await fetch_gbif_near(
        client,
        lat,
        lon,
        taxon_key=ANIMALIA,
        radius_km=300.0,
        days=400,
        limit=12,
        kind="trk",
        extra={"publishingOrg": MOVEBANK_ORG},
    )
    if near:
        return near, note
    response = await client.get(
        GBIF_OCC,
        params={
            "q": "movebank",
            "hasCoordinate": "true",
            "hasGeospatialIssue": "false",
            "eventDate": (
                f"{(datetime.now(timezone.utc) - timedelta(days=400)).date().isoformat()},"
                f"{datetime.now(timezone.utc).date().isoformat()}"
            ),
            "limit": 12,
        },
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("results") if isinstance(payload, dict) else []
    items: list[dict[str, Any]] = []
    for occ in rows or []:
        if not isinstance(occ, dict):
            continue
        item = _compact_occ(occ, origin_lat=lat, origin_lon=lon, kind="trk", src="GBIF / studio pubblicato")
        if item is not None:
            items.append(item)
    await _name_items(client, items)
    if not items:
        note = (
            "Nessun animale con collare GPS pubblico vicino a questo luogo, "
            "e GBIF non ha dato studi Movebank scaricabili adesso. Non invento i tracciati."
        )
    return items[:MAX_ITEMS], note


def _sci_key(item: dict[str, Any]) -> str:
    return str(item.get("sci") or item.get("title") or "").strip().casefold()


def _when_sort(item: dict[str, Any]) -> float:
    when = item.get("when")
    if isinstance(when, datetime):
        return when.timestamp()
    if isinstance(when, str):
        parsed = _parse_when(when)
        return parsed.timestamp() if parsed else 0.0
    return 0.0


def _parkish(item: dict[str, Any]) -> bool:
    place = str(item.get("place") or "").casefold()
    return any(token in place for token in _PARK_TOKENS)


def _is_bird(item: dict[str, Any]) -> bool:
    if str(item.get("kind") or "") == "bird":
        return True
    return str(item.get("iconic") or "").casefold() == "aves"


def _rank_near(item: dict[str, Any]) -> float:
    dist = float(item.get("dist_km") or 9999)
    when = _when_sort(item)
    age_days = 40.0
    if when:
        age_days = max(0.0, (datetime.now(timezone.utc).timestamp() - when) / 86400.0)
    score = dist + age_days * 2.0
    if _parkish(item):
        score -= 22.0
    return score


def _merge_recent(*batches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for batch in batches:
        for item in batch:
            key = _sci_key(item)
            if not key:
                continue
            prev = seen.get(key)
            if prev is None:
                seen[key] = dict(item)
                order.append(key)
                continue
            cand = dict(item)
            prev_when = _when_sort(prev)
            cand_when = _when_sort(cand)
            if cand_when > prev_when:
                keep = cand
            elif cand_when < prev_when:
                keep = prev
            else:
                prev_d = float(prev.get("dist_km") or 99999)
                cand_d = float(cand.get("dist_km") or 99999)
                keep = dict(cand if cand_d < prev_d else prev)
            if not keep.get("place"):
                keep["place"] = prev.get("place") or cand.get("place")
            if not keep.get("photo"):
                keep["photo"] = prev.get("photo") or cand.get("photo")
            seen[key] = keep
    items = [seen[key] for key in order]
    birds = [row for row in items if _is_bird(row)]
    others = [row for row in items if not _is_bird(row)]
    birds.sort(key=_rank_near)
    others.sort(key=_rank_near)
    mixed = others + birds[:BIRD_CAP]
    mixed.sort(key=_rank_near)
    return mixed[:MAX_ITEMS]


async def fetch_recent_observed(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
) -> tuple[list[dict[str, Any]], str]:
    try:
        inat = await fetch_inat_obs(
            client, lat=lat, lon=lon, radius_km=NEAR_KM, days=INAT_DAYS, limit=INAT_POOL, kind="obs"
        )
    except WildlifeError:
        inat = []
    try:
        mammals = await fetch_inat_obs(
            client,
            lat=lat,
            lon=lon,
            radius_km=NEAR_KM,
            days=INAT_DAYS,
            limit=12,
            kind="obs",
            iconic="Mammalia",
        )
    except WildlifeError:
        mammals = []
    try:
        observed = await fetch_gbif_near(client, lat, lon, taxon_key=ANIMALIA, kind="obs")
    except Exception:
        observed = []
    aves = []
    try:
        aves = await fetch_gbif_near(client, lat, lon, taxon_key=AVES, kind="bird")
    except Exception:
        aves = []
    birds = await fetch_ebird_near(client, lat, lon, radius_km=min(50.0, NEAR_KM))
    extras: list[str] = []
    if inat or mammals:
        extras.append(f"iNaturalist {INAT_DAYS} giorni, raggio {NEAR_KM:.0f} km.")
    if birds:
        extras.append("Uccelli anche da eBird.")
    elif aves:
        extras.append("Qualche uccello da GBIF.")
    items = _merge_recent(mammals, inat, observed, birds or [], aves)
    if not items:
        extras.append("Nessun avvistamento in questo giro. Non invento animali.")
    return items, " ".join(extras)


async def search_species(client: httpx.AsyncClient, query: str) -> dict[str, Any] | None:
    q = str(query or "").strip()
    if len(q) < 2:
        return None
    try:
        matched = await client.get(GBIF_MATCH, params={"name": q, "verbose": False})
        matched.raise_for_status()
        data = matched.json()
        if isinstance(data, dict) and data.get("usageKey") and str(data.get("status") or "") in {"ACCEPTED", "SYNONYM", ""}:
            if str(data.get("kingdom") or "").lower() in {"animalia", "metazoa", ""}:
                return {
                    "key": int(data["usageKey"]),
                    "sci": str(data.get("canonicalName") or data.get("scientificName") or q),
                    "title": str(data.get("canonicalName") or q),
                }
    except Exception:
        pass
    for params in (
        {"q": q, "qField": "VERNACULAR", "rank": "SPECIES", "limit": 8},
        {"q": q, "rank": "SPECIES", "status": "ACCEPTED", "limit": 8},
    ):
        try:
            response = await client.get(GBIF_SPECIES, params=params)
            response.raise_for_status()
            rows = response.json().get("results") if isinstance(response.json(), dict) else []
        except Exception:
            rows = []
        for row in rows or []:
            if not isinstance(row, dict) or not row.get("key"):
                continue
            kingdom = str(row.get("kingdom") or "").lower()
            if kingdom and kingdom not in {"animalia", "metazoa"}:
                continue
            sci = str(row.get("canonicalName") or row.get("scientificName") or q)
            key = int(row["nubKey"] or row["key"]) if row.get("nubKey") or row.get("key") else int(row["key"])
            try:
                matched = await client.get(GBIF_MATCH, params={"name": sci})
                packed = matched.json()
                if isinstance(packed, dict) and packed.get("usageKey"):
                    key = int(packed["usageKey"])
                    sci = str(packed.get("canonicalName") or sci)
            except Exception:
                pass
            return {
                "key": key,
                "sci": sci,
                "title": str(row.get("vernacularName") or sci),
            }
    return None


def dump_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items[:MAX_ITEMS]:
        row = dict(item)
        when = row.get("when")
        if isinstance(when, datetime):
            row["when"] = when.astimezone(timezone.utc).isoformat()
        out.append(row)
    return out


def stored_items(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    items: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        if isinstance(row.get("when"), str):
            row["when"] = _parse_when(row["when"])
        items.append(row)
    return items


def _when_bit(item: dict[str, Any]) -> str:
    when = item.get("when")
    if isinstance(when, datetime):
        return ago_it(when)
    if isinstance(when, str):
        parsed = _parse_when(when)
        return ago_it(parsed) if parsed else "—"
    return "—"


_ICONIC_EMOJI = {
    "mammalia": "🦌",
    "aves": "🐦",
    "reptilia": "🦎",
    "amphibia": "🐸",
    "insecta": "🐛",
    "arachnida": "🕷️",
    "mollusca": "🐌",
    "actinopterygii": "🐟",
}


def item_emoji(item: dict[str, Any]) -> str:
    iconic = str(item.get("iconic") or "").casefold()
    kind = str(item.get("kind") or "obs")
    if kind == "bird" or iconic == "aves":
        return "🐦"
    if kind == "world":
        return "🌍"
    return _ICONIC_EMOJI.get(iconic, "🐾")


def format_fauna_hub(*, place: str) -> str:
    where = _html.escape(place, quote=False)
    return "\n".join(
        [
            "🐾 <b>FAUNA</b>",
            f"📍 <b>{where.upper()}</b>",
            "",
            "🐾 <b>Osservati recenti</b> — iNaturalist, GBIF e eBird intorno al luogo. Un umano li ha visti (anche al parco accanto).",
            "🌍 <b>Fauna nel mondo</b> — avvistamenti iNaturalist appena pubblicati.",
            "",
            "<i>Non è uno zoo e non è un allarme. Se il feed è vuoto, non invento avvistamenti.</i>",
        ]
    )


def format_fauna_list(
    *,
    view: str,
    place: str,
    items: list[dict[str, Any]],
    page: int,
    extra: str = "",
) -> str:
    meta = fauna_meta(view)
    where = _html.escape(place, quote=False)
    lines = [
        f"{meta['emoji']} <b>{_html.escape(meta['it'].upper(), quote=False)}</b>",
        (
            "🌍 Ultime osservazioni pubblicate"
            if view == "world"
            else f"📍 {where} · raggio {NEAR_KM:.0f} km · {INAT_DAYS} giorni"
        ),
        f"<i>{_html.escape(meta['blurb'], quote=False)}</i>",
    ]
    if extra:
        lines.append(f"<i>{_html.escape(extra, quote=False)}</i>")
    lines.append("")
    if not items:
        lines.append("Nessun avvistamento in questo filtro.")
        lines.append("Non invento animali.")
        lines.append("")
        lines.append("<i>iNaturalist / GBIF / eBird. Osservazione ≠ posizione GPS dell'animale.</i>")
        return "\n".join(lines)
    start = page * PAGE_SIZE
    chunk = items[start : start + PAGE_SIZE]
    for idx, item in enumerate(chunk, start=start + 1):
        title = _html.escape(str(item.get("title") or "animale"), quote=False)
        dist = item.get("dist_km")
        dist_s = f"{float(dist):.1f} km" if isinstance(dist, (int, float)) else "—"
        lines.append(f"{idx}. {item_emoji(item)} <b>{title}</b>")
        bits = [f"🕐 {_when_bit(item)}"]
        if view != "world" and isinstance(dist, (int, float)):
            bits.insert(0, f"📏 {dist_s}")
        place_bit = str(item.get("place") or "")
        if place_bit:
            bits.append(_html.escape(place_bit, quote=False))
        lines.append(" · ".join(bits))
        sci = str(item.get("sci") or "")
        if sci and sci.casefold() != str(item.get("title") or "").casefold():
            lines.append(f"<i>{_html.escape(sci, quote=False)}</i>")
        lines.append("")
    leftover = max(0, len(items) - start - len(chunk))
    if leftover:
        lines.append(f"<i>Altri {leftover} in pagine successive.</i>")
        lines.append("")
    lines.append(
        "<i>iNaturalist / GBIF / eBird. Osservazione di un umano, non la posizione live dell'animale.</i>"
    )
    return "\n".join(lines)


def format_fauna_detail(*, place: str, item: dict[str, Any], view: str = "") -> str:
    title = _html.escape(str(item.get("title") or "Animale"), quote=False)
    sci = _html.escape(str(item.get("sci") or ""), quote=False)
    where = _html.escape(place, quote=False)
    dist = item.get("dist_km")
    found = str(item.get("place") or "").strip()
    try:
        coord = _latlon_it(float(item["lat"]), float(item["lon"]))
    except (TypeError, ValueError, KeyError):
        coord = "—"
    kind = str(item.get("kind") or "obs")
    worldish = view == "world" or kind == "world"
    if worldish:
        live = "Avvistamento iNaturalist nel mondo. Il posto è dove è stato visto."
    else:
        live = "Osservazione recente di un umano. Non è la posizione GPS dell'animale."
    dist_line = ""
    if not worldish and isinstance(dist, (int, float)):
        dist_line = f"📏 {float(dist):.1f} km da {where}"
    found_line = _html.escape(found, quote=False)
    lines = [
        f"🐾 <b>{title}</b>",
        f"<i>{sci}</i>" if sci else "",
        f"📍 {found_line}" if found_line else "",
        f"📍 {coord}" if coord != "—" else "",
        dist_line,
        f"🕐 {_when_bit(item)}",
        _html.escape(live, quote=False),
    ]
    url = str(item.get("url") or "")
    if url.startswith("http"):
        lines.append(f'<a href="{_html.escape(url, quote=True)}">Apri la scheda</a>')
    src = str(item.get("src") or "GBIF")
    ds = str(item.get("dataset") or "")
    lines.extend(
        [
            "",
            f"<i>{_html.escape(src, quote=False)}"
            + (f" · {_html.escape(ds, quote=False)}" if ds else "")
            + ". Foto e nomi della fonte, se arrivano.</i>",
        ]
    )
    return "\n".join(line for line in lines if line)


def item_button_label(item: dict[str, Any], index: int, *, world: bool = False) -> str:
    title = str(item.get("title") or "animale")
    kind = str(item.get("kind") or "")
    dist = item.get("dist_km")
    found = str(item.get("place") or "").strip()
    if world or kind == "world":
        if found:
            title = f"{title} · {found}"
    else:
        park = found.split(",")[0].strip() if found else ""
        if park and _parkish({"place": found}):
            title = f"{title} · {park}"
        elif isinstance(dist, (int, float)):
            title = f"{title} · {float(dist):.0f} km"
    return f"{index} {item_emoji(item)} {title}"[:34]
