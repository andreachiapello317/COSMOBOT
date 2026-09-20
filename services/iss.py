"""Posizione ISS da API pubbliche, senza chiave."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("stellebot.iss")

ISS_NORAD_ID = 25544
WTIA_URL = f"https://api.wheretheiss.at/v1/satellites/{ISS_NORAD_ID}"


OPEN_NOTIFY_ASTROS = "http://api.open-notify.org/astros.json"


async def fetch_people_in_space(client: httpx.AsyncClient) -> dict[str, Any]:
    """Equipaggio in orbita da Open Notify. Solleva se il payload non è usabile."""
    response = await client.get(OPEN_NOTIFY_ASTROS)
    response.raise_for_status()
    data = response.json()
    people = data.get("people") if isinstance(data, dict) else None
    if not isinstance(people, list):
        raise ValueError("equipaggio vuoto")
    clean = [p for p in people if isinstance(p, dict) and p.get("name")]
    if not clean:
        raise ValueError("equipaggio vuoto")
    return {"people": clean, "number": data.get("number", len(clean))}


async def fetch_iss_position(client: httpx.AsyncClient) -> dict[str, Any]:
    """Posizione, velocità e timestamp. Solleva httpx.HTTPError / ValueError."""
    response = await client.get(WTIA_URL)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or data.get("latitude") is None:
        raise ValueError("payload ISS non valido")
    return data


async def reverse_iss_place(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
) -> dict[str, str]:
    """Localizzazione best-effort. Mare / oceano: niente nome inventato."""
    place = ""
    map_url = f"https://www.openstreetmap.org/?mlat={lat:.4f}&mlon={lon:.4f}#map=4/{lat:.4f}/{lon:.4f}"
    try:
        wtia = await client.get(f"https://api.wheretheiss.at/v1/coordinates/{lat},{lon}")
        wtia.raise_for_status()
        payload = wtia.json()
        if isinstance(payload, dict):
            if payload.get("map_url"):
                map_url = str(payload["map_url"])
            code = str(payload.get("country_code") or "").strip()
            tz = str(payload.get("timezone_id") or "").strip()
            if code and code not in {"??", "None"}:
                place = code
            elif tz:
                place = f"acque internazionali ({tz})"
            else:
                place = "acque internazionali"
    except Exception as exc:  # noqa: BLE001 — fallback Nominatim
        logger.info("WTIA coordinates non disponibile: %s", exc)

    try:
        geo = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 5},
        )
        geo.raise_for_status()
        payload = geo.json()
        if isinstance(payload, dict) and not payload.get("error"):
            address = payload.get("address") if isinstance(payload.get("address"), dict) else {}
            bits = [
                address.get("ocean") or address.get("sea"),
                address.get("country"),
                address.get("state"),
                payload.get("display_name"),
            ]
            label = next((str(b) for b in bits if b), "")
            if label:
                place = label.split(",")[0].strip()
    except Exception as exc:  # noqa: BLE001 — la posizione resta comunque valida
        logger.info("Nominatim reverse ISS non disponibile: %s", exc)

    return {"place": place or "posizione non etichettata", "map_url": map_url}
