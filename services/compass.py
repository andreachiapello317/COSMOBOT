"""Bussola e GPS: misure da coordinate. Niente nord inventato."""

from __future__ import annotations

import html
import math
from datetime import datetime, timezone
from typing import Any

import httpx

from services.earth import haversine_km

CARDINAL_SHORT = (
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSO",
    "SO",
    "OSO",
    "O",
    "ONO",
    "NO",
    "NNO",
)
CARDINAL_IT = (
    "nord",
    "nord-nord-est",
    "nord-est",
    "est-nord-est",
    "est",
    "est-sud-est",
    "sud-est",
    "sud-sud-est",
    "sud",
    "sud-sud-ovest",
    "sud-ovest",
    "ovest-sud-ovest",
    "ovest",
    "ovest-nord-ovest",
    "nord-ovest",
    "nord-nord-ovest",
)


def _latlon_it(lat: float, lon: float) -> str:
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "O"
    return f"{abs(lat):.6f}° {ns}, {abs(lon):.6f}° {ew}"


def true_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def cardinal_index(deg: float) -> int:
    return int((deg + 11.25) / 22.5) % 16


def cardinal_it(deg: float) -> str:
    idx = cardinal_index(deg)
    return f"{CARDINAL_IT[idx]} ({CARDINAL_SHORT[idx]})"


def map_url(lat: float, lon: float) -> str:
    return (
        f"https://www.openstreetmap.org/?mlat={lat:.5f}&mlon={lon:.5f}"
        f"#map=14/{lat:.5f}/{lon:.5f}"
    )


def decimal_year(when: datetime | None = None) -> float:
    now = when or datetime.now(timezone.utc)
    start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    frac = (now - start).total_seconds() / (end - start).total_seconds()
    return now.year + frac


async def fetch_elevation(client: httpx.AsyncClient, lat: float, lon: float) -> float | None:
    response = await client.get(
        "https://api.open-meteo.com/v1/elevation",
        params={"latitude": f"{lat:.5f}", "longitude": f"{lon:.5f}"},
    )
    response.raise_for_status()
    data = response.json()
    rows = data.get("elevation") if isinstance(data, dict) else None
    if isinstance(rows, list) and rows:
        return float(rows[0])
    return None


async def fetch_declination(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    *,
    altitude_m: float | None = None,
) -> dict[str, float]:
    alt_km = max(0.0, float(altitude_m or 0.0) / 1000.0)
    response = await client.get(
        "https://geomag.bgs.ac.uk/web_service/GMModels/wmm/2025",
        params={
            "latitude": f"{lat:.5f}",
            "longitude": f"{lon:.5f}",
            "altitude": f"{alt_km:.3f}",
            "year": f"{decimal_year():.3f}",
            "format": "json",
        },
    )
    response.raise_for_status()
    data = response.json()
    root = data.get("geomagnetic-field-model-result") if isinstance(data, dict) else None
    field = root.get("field-value") if isinstance(root, dict) else None
    if not isinstance(field, dict):
        raise ValueError("declinazione vuota")
    dec = field.get("declination") if isinstance(field.get("declination"), dict) else {}
    inc = field.get("inclination") if isinstance(field.get("inclination"), dict) else {}
    return {
        "declination": float(dec.get("value")),
        "inclination": float(inc.get("value")),
    }


async def search_place(client: httpx.AsyncClient, query: str) -> list[dict[str, Any]]:
    """Nominatim: via e numero, non solo il centro città."""
    response = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
        },
        headers={"Accept-Language": "it"},
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        return []
    places: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            lat = float(item.get("lat"))
            lon = float(item.get("lon"))
        except (TypeError, ValueError):
            continue
        address = item.get("address") if isinstance(item.get("address"), dict) else {}
        road = " ".join(
            part
            for part in (address.get("road"), address.get("house_number"))
            if part
        )
        city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet")
        name = road or str(item.get("name") or item.get("display_name") or query)
        if city and city.lower() not in name.lower():
            name = f"{name}, {city}"
        places.append(
            {
                "name": name,
                "display": str(item.get("display_name") or name),
                "lat": lat,
                "lon": lon,
                "country": str(address.get("country") or ""),
                "kind": str(item.get("type") or item.get("class") or ""),
                "source": "OpenStreetMap",
            }
        )
    return places


async def reverse_place(client: httpx.AsyncClient, lat: float, lon: float) -> str:
    response = await client.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={"lat": f"{lat:.5f}", "lon": f"{lon:.5f}", "format": "json", "zoom": 12},
        headers={"Accept-Language": "it"},
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or data.get("error"):
        return "posizione senza etichetta"
    address = data.get("address") if isinstance(data.get("address"), dict) else {}
    bits = [
        address.get("city") or address.get("town") or address.get("village") or address.get("hamlet"),
        address.get("county") or address.get("state"),
        address.get("country"),
    ]
    label = ", ".join(str(b) for b in bits if b)
    return label or str(data.get("display_name") or "posizione senza etichetta")


def format_gps(
    *,
    name: str,
    lat: float,
    lon: float,
    elevation_m: float | None = None,
    declination: float | None = None,
    accuracy_m: float | None = None,
    heading: float | None = None,
    source: str = "città",
) -> str:
    lines = [
        "📍 <b>POSIZIONE GPS</b>",
        f"<i>{html.escape(name, quote=False)}</i>",
        "",
        f"Coordinate: <code>{html.escape(_latlon_it(lat, lon), quote=False)}</code>",
        f"<code>{lat:.6f}, {lon:.6f}</code>",
        f'Fonte: {html.escape(source, quote=False)} · <a href="{html.escape(map_url(lat, lon), quote=True)}">Apri la mappa</a>',
    ]
    if accuracy_m is not None:
        lines.append(f"Precisione dichiarata dal telefono: circa ±{accuracy_m:.0f} m")
    if elevation_m is not None:
        lines.append(
            f"Quota del terreno: {elevation_m:.0f} m (modello Open-Meteo, non l'altimetro del telefono)"
        )
    if declination is not None:
        side = "est" if declination >= 0 else "ovest"
        lines.append(
            f"Declinazione magnetica: {abs(declination):.1f}° {side} (WMM 2025, British Geological Survey)"
        )
        lines.append(
            f"Nord magnetico: {abs(declination):.1f}° a {side} del nord geografico."
        )
    if heading is not None:
        lines.append(
            f"Il telefono indica {heading:.0f}° — {cardinal_it(heading)}. "
            "È l'orientamento del dispositivo, se Telegram lo ha mandato."
        )
    lines.extend(
        [
            "",
            "<i>Le coordinate sono geografiche (WGS84). La bussola del telefono punta al nord magnetico, non a questo numero da sola.</i>",
        ]
    )
    return "\n".join(lines)


def format_compass(
    *,
    name: str,
    lat: float,
    lon: float,
    declination: float | None = None,
    heading: float | None = None,
) -> str:
    lines = [
        "🧭 <b>BUSSOLA</b>",
        f"<i>Da {html.escape(name, quote=False)}. Nord geografico = 0°.</i>",
        "",
        "0° nord · 90° est · 180° sud · 270° ovest",
        f"Coordinate: <code>{html.escape(_latlon_it(lat, lon), quote=False)}</code>",
    ]
    if declination is not None:
        side = "est" if declination >= 0 else "ovest"
        mag_north = (0.0 - declination + 360.0) % 360.0
        lines.append("")
        lines.append(
            f"Declinazione WMM: {abs(declination):.1f}° verso {side}."
        )
        lines.append(
            f"Nord magnetico: {abs(declination):.1f}° a {side} del nord geografico "
            f"({cardinal_it(mag_north)} se la declinazione è grande)."
        )
        lines.append(
            "Se la bussola del telefono marca 0°, stai guardando il nord magnetico. "
            f"Il nord geografico è {abs(declination):.1f}° più a {'ovest' if declination >= 0 else 'est'}."
        )
    else:
        lines.append("Declinazione non arrivata. Non invento il nord magnetico.")
    if heading is not None:
        lines.append("")
        lines.append(f"Orientamento del telefono adesso: {heading:.0f}° — {cardinal_it(heading)}.")
    lines.extend(
        [
            "",
            "<i>British Geological Survey, World Magnetic Model 2025. Non è un GPS di navigazione.</i>",
        ]
    )
    return "\n".join(lines)


def format_bearing(
    *,
    origin: str,
    dest: str,
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    declination: float | None = None,
) -> str:
    dist = haversine_km(lat1, lon1, lat2, lon2)
    true = true_bearing(lat1, lon1, lat2, lon2)
    lines = [
        "🎯 <b>VERSO UN LUOGO</b>",
        f"<i>Da {html.escape(origin, quote=False)} a {html.escape(dest, quote=False)}.</i>",
        "",
        f"Distanza in linea d'aria: <b>{dist:.1f} km</b>",
        f"Direzione geografica: <b>{true:.0f}°</b> — {cardinal_it(true)}",
    ]
    if declination is not None:
        mag = (true - declination + 360.0) % 360.0
        lines.append(
            f"Sulla bussola magnetica: <b>{mag:.0f}°</b> — {cardinal_it(mag)} "
            f"(declinazione {declination:+.1f}°)."
        )
    lines.extend(
        [
            "",
            "È il primo azimut sul grande cerchio, non il percorso stradale.",
            f'<a href="{html.escape(map_url(lat2, lon2), quote=True)}">Mappa della destinazione</a>',
            "",
            "<i>Calcolo locale + WMM se la declinazione c'è. Non sostituisce un navigatore.</i>",
        ]
    )
    return "\n".join(lines)
