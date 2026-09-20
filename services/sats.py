"""Satelliti live: TLE pubblici + SGP4. Niente passaggi sulla città, niente Starlink."""

from __future__ import annotations

import html as _html
import math
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from sgp4.api import Satrec, jday

TLE_URL = "https://tle.ivanstanojevic.me/api/tle/{norad}"
WTIA_TLE_URL = "https://api.wheretheiss.at/v1/satellites/25544/tles"
CACHE_TTL = 12 * 60

SATS: dict[str, dict[str, Any]] = {
    "iss": {
        "norad": 25544,
        "it": "ISS",
        "emoji": "🛰️",
        "hint": "Stazione spaziale internazionale",
        "source": "wtia",
    },
    "css": {
        "norad": 48274,
        "it": "Tiangong",
        "emoji": "🏠",
        "hint": "Stazione spaziale cinese (Tianhe)",
        "source": "tle",
    },
    "hst": {
        "norad": 20580,
        "it": "Hubble",
        "emoji": "🔭",
        "hint": "Telescopio spaziale Hubble",
        "source": "tle",
    },
    "terra": {
        "norad": 25994,
        "it": "Terra",
        "emoji": "🌍",
        "hint": "Osservazione Terra NASA (EOS AM-1)",
        "source": "tle",
    },
    "aqua": {
        "norad": 27424,
        "it": "Aqua",
        "emoji": "💧",
        "hint": "Osservazione Terra NASA (EOS PM-1)",
        "source": "tle",
    },
    "ld8": {
        "norad": 39084,
        "it": "Landsat 8",
        "emoji": "🛰️",
        "hint": "Mappa della Terra USGS/NASA",
        "source": "tle",
    },
    "ld9": {
        "norad": 49260,
        "it": "Landsat 9",
        "emoji": "🛰️",
        "hint": "Mappa della Terra USGS/NASA",
        "source": "tle",
    },
    "s2a": {
        "norad": 40697,
        "it": "Sentinel-2A",
        "emoji": "🛰️",
        "hint": "Copernicus, osservazione Terra",
        "source": "tle",
    },
    "n20": {
        "norad": 43013,
        "it": "NOAA-20",
        "emoji": "🌦️",
        "hint": "Meteo polare JPSS-1",
        "source": "tle",
    },
    "n21": {
        "norad": 54234,
        "it": "NOAA-21",
        "emoji": "🌦️",
        "hint": "Meteo polare JPSS-2",
        "source": "tle",
    },
    "g16": {
        "norad": 41866,
        "it": "GOES-16",
        "emoji": "🌎",
        "hint": "Meteo geostazionario, Americhe",
        "source": "tle",
    },
}

GROUPS: dict[str, dict[str, Any]] = {
    "sta": {
        "it": "Stazioni",
        "emoji": "🏠",
        "keys": ("iss", "css"),
        "blurb": "Le due stazioni abitate. ISS da Where the ISS at?; Tiangong da TLE + SGP4.",
    },
    "earth": {
        "it": "Osservazione Terra",
        "emoji": "🌍",
        "keys": ("terra", "aqua", "ld8", "ld9", "s2a"),
        "blurb": "Satelliti che fotografano il suolo. Posizione adesso, non il prossimo passaggio.",
    },
    "meteo": {
        "it": "Meteo sat",
        "emoji": "🌦️",
        "keys": ("n20", "n21", "g16"),
        "blurb": "Satelliti meteo polari e GOES-16 geostazionario. Non è il meteo di Cuneo.",
    },
}

_TLE_CACHE: dict[int, tuple[float, dict[str, Any]]] = {}


class SatError(RuntimeError):
    """TLE o SGP4 non usabili."""


def _gmst_rad(jd: float) -> float:
    t = (jd - 2451545.0) / 36525.0
    gmst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - t**3 / 38710000.0
    )
    return math.radians(gmst % 360.0)


def _ecef_to_llh(x: float, y: float, z: float) -> tuple[float, float, float]:
    a = 6378.137
    e2 = 6.69437999014e-3
    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - e2))
    for _ in range(8):
        n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        lat = math.atan2(z + e2 * n * math.sin(lat), p)
    n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    alt = p / math.cos(lat) - n
    return math.degrees(lat), math.degrees(lon), alt


def _teme_to_llh(r: tuple[float, float, float], jd: float) -> tuple[float, float, float]:
    th = _gmst_rad(jd)
    c, s = math.cos(th), math.sin(th)
    x, y, z = r
    return _ecef_to_llh(x * c + y * s, -x * s + y * c, z)


def propagate_tle(
    line1: str,
    line2: str,
    when: datetime,
) -> dict[str, Any]:
    sat = Satrec.twoline2rv(str(line1).strip(), str(line2).strip())
    utc = when.astimezone(timezone.utc)
    jd, fr = jday(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        utc.second + utc.microsecond / 1_000_000,
    )
    err, r, v = sat.sgp4(jd, fr)
    if err != 0 or r is None or v is None:
        raise SatError(f"SGP4 errore {err}")
    lat, lon, alt = _teme_to_llh((float(r[0]), float(r[1]), float(r[2])), jd + fr)
    speed = math.sqrt(float(v[0]) ** 2 + float(v[1]) ** 2 + float(v[2]) ** 2)
    revs_day = float(sat.no_kozai) * 1440.0 / (2.0 * math.pi)
    period = 1440.0 / revs_day if revs_day else None
    return {
        "lat": lat,
        "lon": lon,
        "alt_km": alt,
        "vel_kms": speed,
        "period_min": period,
        "incl_deg": math.degrees(float(sat.inclo)),
        "ecc": float(sat.ecco),
    }


def _parse_tle_payload(data: dict[str, Any], norad: int) -> dict[str, Any]:
    line1 = str(data.get("line1") or "").strip()
    line2 = str(data.get("line2") or "").strip()
    if not line1.startswith("1 ") or not line2.startswith("2 "):
        raise SatError("TLE incompleto")
    name = str(data.get("name") or data.get("header") or f"NORAD {norad}")
    stamp = str(data.get("date") or data.get("tle_timestamp") or "")
    return {"norad": norad, "name": name, "line1": line1, "line2": line2, "date": stamp}


async def fetch_tle(client: httpx.AsyncClient, norad: int) -> dict[str, Any]:
    now = time.time()
    hit = _TLE_CACHE.get(int(norad))
    if hit and now - hit[0] < CACHE_TTL:
        return hit[1]
    try:
        response = await client.get(TLE_URL.format(norad=int(norad)))
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise SatError("TLE non valido")
        row = _parse_tle_payload(payload, int(norad))
    except Exception:
        if int(norad) != 25544:
            raise
        response = await client.get(WTIA_TLE_URL)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise SatError("TLE ISS non valido")
        row = _parse_tle_payload(payload, 25544)
    _TLE_CACHE[int(norad)] = (now, row)
    return row


async def locate_sat(
    client: httpx.AsyncClient,
    key: str,
    when: datetime,
) -> dict[str, Any]:
    meta = SATS.get(key)
    if not meta:
        raise SatError("satellite sconosciuto")
    tle = await fetch_tle(client, int(meta["norad"]))
    pos = propagate_tle(tle["line1"], tle["line2"], when)
    pos["tle_name"] = tle["name"]
    pos["tle_date"] = tle["date"]
    pos["norad"] = int(meta["norad"])
    pos["key"] = key
    return pos


def period_it(minutes: float | None) -> str:
    if not isinstance(minutes, (int, float)) or minutes <= 0:
        return ""
    if minutes >= 1000:
        hours = minutes / 60.0
        return f"orbita ogni {hours:.1f} ore (geostazionario)"
    return f"orbita ogni {minutes:.0f} min"


def format_sat_card(
    *,
    key: str,
    when: datetime,
    pos: dict[str, Any],
    over: str = "",
) -> str:
    meta = SATS[key]
    place = _html.escape(over) if over else "posizione non etichettata"
    period = period_it(pos.get("period_min") if isinstance(pos.get("period_min"), (int, float)) else None)
    tle_date = str(pos.get("tle_date") or "")
    if tle_date[:10].count("-") == 2:
        tle_bit = tle_date.replace("T", " ")[:16] + " UTC"
    else:
        tle_bit = tle_date or "epoca TLE non indicata"
    lines = [
        f"{meta['emoji']} <b>{_html.escape(str(meta['it']).upper())} — ADESSO</b>",
        _html.escape(str(meta["hint"])),
        "",
        f"📍 Sopra: <b>{place}</b>",
        f"🌍 Lat <code>{float(pos['lat']):.4f}</code> · lon <code>{float(pos['lon']):.4f}</code>",
        f"📏 Quota {float(pos['alt_km']):.0f} km",
        f"🚀 {float(pos['vel_kms']) * 3600:.0f} km/h",
    ]
    extra = []
    if period:
        extra.append(period)
    if isinstance(pos.get("incl_deg"), (int, float)):
        extra.append(f"inclinazione {float(pos['incl_deg']):.1f}°")
    if extra:
        lines.append("📐 " + " · ".join(extra))
    lines.extend(
        [
            f"🏷️ NORAD {int(pos['norad'])} · TLE {_html.escape(tle_bit)}",
            f"🕐 {when.strftime('%d/%m/%Y %H:%M')} (Europe/Rome)",
            "",
            "<i>TLE live (ivanstanojevic / CelesTrak). Posizione: SGP4, algoritmo reale. "
            "Non è un passaggio sulla tua città. Non è Horizons. Non elenco Starlink.</i>",
        ]
    )
    return "\n".join(lines)


def format_sat_group(
    *,
    group: str,
    when: datetime,
    rows: list[dict[str, Any]],
) -> str:
    meta = GROUPS[group]
    lines = [
        f"{meta['emoji']} <b>{_html.escape(str(meta['it']).upper())}</b>",
        _html.escape(str(meta["blurb"])),
        f"🕐 {when.strftime('%d/%m/%Y %H:%M')} (Europe/Rome)",
        "",
    ]
    if not rows:
        lines.append("Nessun TLE è arrivato per questo gruppo.")
    for row in rows:
        key = str(row.get("key") or "")
        sat = SATS.get(key, {})
        title = sat.get("it") or row.get("tle_name") or key
        emoji = sat.get("emoji") or "🛰️"
        if row.get("error"):
            lines.append(f"{emoji} <b>{_html.escape(str(title))}</b> — TLE non arrivato.")
            lines.append("")
            continue
        period = period_it(row.get("period_min") if isinstance(row.get("period_min"), (int, float)) else None)
        bits = [
            f"lat {float(row['lat']):.2f}°",
            f"lon {float(row['lon']):.2f}°",
            f"{float(row['alt_km']):.0f} km",
        ]
        if period:
            bits.append(period)
        lines.append(f"{emoji} <b>{_html.escape(str(title))}</b>")
        lines.append(" · ".join(bits))
        lines.append("")
    lines.append(
        "<i>Posizioni da TLE live + SGP4. I passaggi sopra una città restano fuori.</i>"
    )
    return "\n".join(lines)
