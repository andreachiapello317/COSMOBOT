"""Satelliti live: TLE pubblici + SGP4. Posizioni adesso, niente orari di passaggio inventati."""

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
STARLINK_TLE_URLS = (
    "https://raw.githubusercontent.com/satvisorcom/satvisor-data/master/celestrak/tle/starlink.tle",
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
)
CACHE_TTL = 12 * 60
STARLINK_CACHE_TTL = 90 * 60

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
        "blurb": "Satelliti che fotografano il suolo. La foto è del luogo scelto in questa cartella, non del resto del bot.",
    },
    "sl": {
        "it": "Starlink",
        "emoji": "📡",
        "keys": (),
        "blurb": "Costellazione SpaceX. Posizioni da TLE + SGP4: quanti sono sopra di te adesso, non l'orario del prossimo treno.",
    },
}

_TLE_CACHE: dict[int, tuple[float, dict[str, Any]]] = {}
_STARLINK_CACHE: tuple[float, list[tuple[str, str, str]]] | None = None


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
            "Non è un passaggio sulla tua città. Non è Horizons.</i>",
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


def _parse_tle_triples(text: str) -> list[tuple[str, str, str]]:
    lines = [ln.rstrip() for ln in str(text or "").splitlines() if ln.strip()]
    out: list[tuple[str, str, str]] = []
    idx = 0
    while idx < len(lines):
        if idx + 2 < len(lines) and lines[idx + 1].startswith("1 ") and lines[idx + 2].startswith("2 "):
            out.append((lines[idx].strip(), lines[idx + 1], lines[idx + 2]))
            idx += 3
        else:
            idx += 1
    return out


def _ecef_observer(lat: float, lon: float, alt_km: float = 0.05) -> tuple[float, float, float]:
    a = 6378.137
    e2 = 6.69437999014e-3
    lat_r, lon_r = math.radians(lat), math.radians(lon)
    n = a / math.sqrt(1 - e2 * math.sin(lat_r) ** 2)
    x = (n + alt_km) * math.cos(lat_r) * math.cos(lon_r)
    y = (n + alt_km) * math.cos(lat_r) * math.sin(lon_r)
    z = (n * (1 - e2) + alt_km) * math.sin(lat_r)
    return x, y, z


def _look_angles(
    obs_xyz: tuple[float, float, float],
    obs_lat: float,
    obs_lon: float,
    sat_ecef: tuple[float, float, float],
) -> tuple[float, float, float]:
    dx = sat_ecef[0] - obs_xyz[0]
    dy = sat_ecef[1] - obs_xyz[1]
    dz = sat_ecef[2] - obs_xyz[2]
    lat_r, lon_r = math.radians(obs_lat), math.radians(obs_lon)
    slat, clat = math.sin(lat_r), math.cos(lat_r)
    slon, clon = math.sin(lon_r), math.cos(lon_r)
    east = -slon * dx + clon * dy
    north = -slat * clon * dx - slat * slon * dy + clat * dz
    up = clat * clon * dx + clat * slon * dy + slat * dz
    rng = math.sqrt(east * east + north * north + up * up)
    if rng <= 0:
        return -90.0, 0.0, 0.0
    alt = math.degrees(math.asin(max(-1.0, min(1.0, up / rng))))
    az = math.degrees(math.atan2(east, north)) % 360.0
    return alt, az, rng


def _sun_ecef_unit(when: datetime) -> tuple[float, float, float]:
    import astronomy

    utc = when.astimezone(timezone.utc)
    moment = astronomy.Time.Make(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        utc.second + utc.microsecond / 1_000_000,
    )
    vec = astronomy.GeoVector(astronomy.Body.Sun, moment, True)
    th = _gmst_rad(float(moment.ut) + 2451545.0)
    c, s = math.cos(th), math.sin(th)
    x, y, z = float(vec.x), float(vec.y), float(vec.z)
    ex, ey, ez = x * c + y * s, -x * s + y * c, z
    norm = math.sqrt(ex * ex + ey * ey + ez * ez) or 1.0
    return ex / norm, ey / norm, ez / norm


def _in_sunlight(sat_ecef: tuple[float, float, float], sun_unit: tuple[float, float, float]) -> bool:
    dot = sat_ecef[0] * sun_unit[0] + sat_ecef[1] * sun_unit[1] + sat_ecef[2] * sun_unit[2]
    if dot > 0:
        return True
    r2 = sat_ecef[0] ** 2 + sat_ecef[1] ** 2 + sat_ecef[2] ** 2
    perp2 = r2 - dot * dot
    return perp2 > 6378.137 ** 2


def cardinal_short(az: float) -> str:
    names = ("N", "NE", "E", "SE", "S", "SO", "O", "NO")
    return names[int(((float(az) + 22.5) % 360.0) // 45)]


async def fetch_starlink_tles(client: httpx.AsyncClient) -> list[tuple[str, str, str]]:
    global _STARLINK_CACHE
    now = time.time()
    if _STARLINK_CACHE and now - _STARLINK_CACHE[0] < STARLINK_CACHE_TTL:
        return _STARLINK_CACHE[1]
    last_error: Exception | None = None
    for url in STARLINK_TLE_URLS:
        try:
            response = await client.get(url, timeout=40.0)
            response.raise_for_status()
            rows = _parse_tle_triples(response.text)
            if len(rows) >= 100:
                _STARLINK_CACHE = (now, rows)
                return rows
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        raise SatError(f"TLE Starlink non arrivati: {last_error}") from last_error
    raise SatError("TLE Starlink non arrivati")


def locate_starlink_overhead(
    tles: list[tuple[str, str, str]],
    *,
    lat: float,
    lon: float,
    when: datetime,
    min_alt: float = 10.0,
) -> dict[str, Any]:
    utc = when.astimezone(timezone.utc)
    jd, fr = jday(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        utc.second + utc.microsecond / 1_000_000,
    )
    th = _gmst_rad(jd + fr)
    c, s = math.cos(th), math.sin(th)
    obs = _ecef_observer(lat, lon)
    sun = _sun_ecef_unit(utc)
    overhead: list[dict[str, Any]] = []
    for name, line1, line2 in tles:
        try:
            sat = Satrec.twoline2rv(line1, line2)
            err, r, _v = sat.sgp4(jd, fr)
        except Exception:
            continue
        if err != 0 or r is None:
            continue
        ecef = (float(r[0]) * c + float(r[1]) * s, -float(r[0]) * s + float(r[1]) * c, float(r[2]))
        alt, az, rng = _look_angles(obs, lat, lon, ecef)
        if alt < min_alt:
            continue
        slat, slon, salt = _ecef_to_llh(*ecef)
        overhead.append(
            {
                "name": name.replace("STARLINK-", "SL-"),
                "alt": alt,
                "az": az,
                "range_km": rng,
                "lat": slat,
                "lon": slon,
                "alt_km": salt,
                "sun": _in_sunlight(ecef, sun),
            }
        )
    overhead.sort(key=lambda row: row["alt"], reverse=True)
    lit = [row for row in overhead if row["sun"]]
    return {
        "total": len(tles),
        "overhead": overhead,
        "count": len(overhead),
        "lit": len(lit),
        "high_lit": sum(1 for row in lit if row["alt"] >= 20),
    }


def format_starlink_card(
    *,
    place: str,
    when: datetime,
    sun_alt: float,
    data: dict[str, Any],
) -> str:
    night = sun_alt < -6
    rows = list(data.get("overhead") or [])
    lines = [
        f"📡 <b>STARLINK — { _html.escape(place.upper()) }</b>",
        "Posizioni adesso, da TLE + SGP4. Non è l'orario del prossimo treno di satelliti.",
        f"🕐 {when.strftime('%d/%m/%Y %H:%M')} (Europe/Rome)",
        "",
        f"In catalogo: <b>{int(data.get('total') or 0)}</b> TLE.",
        f"Sopra i 10° da qui: <b>{int(data.get('count') or 0)}</b>.",
        f"Al sole (non nell'ombra della Terra): <b>{int(data.get('lit') or 0)}</b> · "
        f"sopra i 20° e al sole: <b>{int(data.get('high_lit') or 0)}</b>.",
        "",
    ]
    if night:
        lines.append(
            "Da qui è notte. Quelli alti e al sole possono apparire come punti che si muovono; "
            "non invento l'ora esatta di un treno."
        )
    else:
        lines.append("Da qui è ancora giorno: in cielo non li vedi, ma le posizioni restano vere.")
    lines.append("")
    if rows:
        lines.append("I più alti adesso:")
        for row in rows[:5]:
            sun = " · al sole" if row.get("sun") else " · ombra"
            lines.append(
                f"📡 <b>{_html.escape(str(row['name']))}</b>  "
                f"alt {row['alt']:.0f}° {cardinal_short(row['az'])}{sun}"
            )
            lines.append(
                f"lat {row['lat']:.1f}° · lon {row['lon']:.1f}° · "
                f"{row['alt_km']:.0f} km · {row['range_km']:.0f} km da te"
            )
    else:
        lines.append("Nessuno sopra i 10° in questo istante.")
    lines.extend(
        [
            "",
            "<i>TLE: specchio CelesTrak (satvisor) o CelesTrak diretto. "
            "Altezza e azimut: geometria dal tuo luogo. Non è un passaggio calcolato in lista.</i>",
        ]
    )
    return "\n".join(lines)
