"""JPL Horizons: efemeridi observer da un luogo. Nessuna posizione inventata."""

from __future__ import annotations

import asyncio
import html
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import astronomy
import httpx

HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
CACHE_TTL = 8 * 60
LIGHT_MIN_PER_AU = 8.316746  # minuti di luce per 1 UA (c, non un'ipotesi)

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

CNST_IT = {
    "And": "Andromeda",
    "Aql": "Aquila",
    "Aqr": "Acquario",
    "Ari": "Ariete",
    "Aur": "Auriga",
    "Boo": "Boote",
    "Cnc": "Cancro",
    "CMa": "Cane Maggiore",
    "CMi": "Cane Minore",
    "Cap": "Capricorno",
    "Cas": "Cassiopea",
    "Cen": "Centauro",
    "Cep": "Cefeo",
    "Cet": "Balena",
    "CMa": "Cane Maggiore",
    "CrB": "Corona Boreale",
    "Cru": "Croce del Sud",
    "Cyg": "Cigno",
    "Dra": "Dragone",
    "Eri": "Eridano",
    "Gem": "Gemelli",
    "Her": "Ercole",
    "Hya": "Idra",
    "Leo": "Leone",
    "Lib": "Bilancia",
    "Lyr": "Lira",
    "Oph": "Ofiuco",
    "Ori": "Orione",
    "Peg": "Pegaso",
    "Per": "Perseo",
    "Psc": "Pesci",
    "Sgr": "Sagittario",
    "Sco": "Scorpione",
    "Tau": "Toro",
    "UMa": "Orsa Maggiore",
    "UMi": "Orsa Minore",
    "Vir": "Vergine",
}

PLANETS: dict[str, dict[str, str]] = {
    "sun": {"command": "10", "it": "Sole", "emoji": "☀️"},
    "mer": {"command": "199", "it": "Mercurio", "emoji": "☿️"},
    "ven": {"command": "299", "it": "Venere", "emoji": "♀️"},
    "mar": {"command": "499", "it": "Marte", "emoji": "♂️"},
    "jup": {"command": "599", "it": "Giove", "emoji": "♃"},
    "sat": {"command": "699", "it": "Saturno", "emoji": "♄"},
    "ura": {"command": "799", "it": "Urano", "emoji": "♅"},
    "nep": {"command": "899", "it": "Nettuno", "emoji": "♆"},
}

MOON_BODY: dict[str, dict[str, str]] = {
    "lun": {"command": "301", "it": "Luna", "emoji": "🌙"},
}

COMETS: dict[str, dict[str, str]] = {
    "1p": {"command": "1P;", "it": "1P/Halley", "emoji": "☄️"},
    "2p": {"command": "2P;", "it": "2P/Encke", "emoji": "☄️"},
    "9p": {"command": "9P;", "it": "9P/Tempel 1", "emoji": "☄️"},
    "12p": {"command": "12P;", "it": "12P/Pons-Brooks", "emoji": "☄️"},
    "13p": {"command": "13P;", "it": "13P/Olbers", "emoji": "☄️"},
}

ROCKS: dict[str, dict[str, str]] = {
    "cer": {"command": "1;", "it": "Cerere", "emoji": "🪨"},
    "pal": {"command": "2;", "it": "Pallade", "emoji": "🪨"},
    "jun": {"command": "3;", "it": "Giunone", "emoji": "🪨"},
    "ves": {"command": "4;", "it": "Vesta", "emoji": "🪨"},
    "apo": {"command": "99942;", "it": "Apophis", "emoji": "☄️"},
}

BODIES: dict[str, dict[str, str]] = {**PLANETS, **MOON_BODY, **ROCKS, **COMETS}

ENGINE_BODY: dict[str, astronomy.Body] = {
    "10": astronomy.Body.Sun,
    "199": astronomy.Body.Mercury,
    "299": astronomy.Body.Venus,
    "301": astronomy.Body.Moon,
    "499": astronomy.Body.Mars,
    "599": astronomy.Body.Jupiter,
    "699": astronomy.Body.Saturn,
    "799": astronomy.Body.Uranus,
    "899": astronomy.Body.Neptune,
}

_cache: dict[str, tuple[float, Any]] = {}
_gate = asyncio.Semaphore(2)


class HorizonsError(RuntimeError):
    """Horizons non ha dato una tabella usabile."""


def _cache_get(key: str) -> Any | None:
    item = _cache.get(key)
    if not item:
        return None
    ts, value = item
    if time.monotonic() - ts > CACHE_TTL:
        _cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: Any) -> Any:
    _cache[key] = (time.monotonic(), value)
    return value


def _num(raw: str | None) -> float | None:
    text = str(raw or "").replace("n.a.", "").strip()
    if not text or text in {"n.a", "n/a"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_horizons_when(raw: str) -> datetime | None:
    match = re.search(r"(\d{4})-([A-Za-z]{3})-(\d{2})\s+(\d{2}):(\d{2})", raw or "")
    if not match:
        return None
    month = MONTHS.get(match.group(2))
    if month is None:
        return None
    try:
        return datetime(
            int(match.group(1)),
            month,
            int(match.group(3)),
            int(match.group(4)),
            int(match.group(5)),
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None


def _header_index(names: list[str], *needles: str) -> int | None:
    for idx, name in enumerate(names):
        key = name.lower()
        if all(n.lower() in key for n in needles):
            return idx
    return None


def parse_observer_rows(result: str) -> list[dict[str, Any]]:
    if "$$SOE" not in result or "$$EOE" not in result:
        raise HorizonsError("tabella Horizons vuota")
    before, rest = result.split("$$SOE", 1)
    body, _ = rest.split("$$EOE", 1)
    header: list[str] = []
    for line in reversed(before.splitlines()):
        if "," in line and "Date" in line:
            header = [p.strip() for p in line.strip().rstrip(",").split(",")]
            break
    rows: list[dict[str, Any]] = []
    azi_i = _header_index(header, "azi")
    elev_i = _header_index(header, "elev")
    mag_i = _header_index(header, "apmag")
    illu_i = _header_index(header, "illu")
    diam_i = _header_index(header, "ang-diam") or _header_index(header, "ang")
    delta_i = None
    for idx, name in enumerate(header):
        if name.strip().lower() == "delta":
            delta_i = idx
            break
    elong_i = _header_index(header, "s-o-t")
    phase_i = _header_index(header, "s-t-o")
    cnst_i = _header_index(header, "cnst")
    r_i = None
    deldot_i = None
    for idx, name in enumerate(header):
        key = name.strip().lower()
        if key == "r":
            r_i = idx
        elif key == "deldot":
            deldot_i = idx
    for line in body.splitlines():
        raw = line.strip().rstrip(",")
        if not raw:
            continue
        parts = [p.strip() for p in raw.split(",")]
        if len(parts) < 4:
            continue
        when = parse_horizons_when(parts[0])
        lead = ""
        for part in parts:
            if part in {"/L", "/T", "/*", "/?"}:
                lead = part
                break
        event = ""
        if len(parts) > 2 and parts[2] in {"r", "t", "s", "e"}:
            event = parts[2]
        row = {
            "when": when,
            "solar": parts[1] if len(parts) > 1 else "",
            "event": event or (parts[2] if len(parts) > 2 else ""),
            "az": _num(parts[azi_i]) if azi_i is not None and azi_i < len(parts) else _num(parts[3] if len(parts) > 3 else None),
            "alt": _num(parts[elev_i]) if elev_i is not None and elev_i < len(parts) else _num(parts[4] if len(parts) > 4 else None),
            "mag": _num(parts[mag_i]) if mag_i is not None and mag_i < len(parts) else None,
            "illum": _num(parts[illu_i]) if illu_i is not None and illu_i < len(parts) else None,
            "ang_diam": _num(parts[diam_i]) if diam_i is not None and diam_i < len(parts) else None,
            "delta_au": _num(parts[delta_i]) if delta_i is not None and delta_i < len(parts) else None,
            "r_au": _num(parts[r_i]) if r_i is not None and r_i < len(parts) else None,
            "deldot": _num(parts[deldot_i]) if deldot_i is not None and deldot_i < len(parts) else None,
            "elong": _num(parts[elong_i]) if elong_i is not None and elong_i < len(parts) else None,
            "phase": _num(parts[phase_i]) if phase_i is not None and phase_i < len(parts) else None,
            "lead": lead,
            "cnst": parts[cnst_i] if cnst_i is not None and cnst_i < len(parts) else "",
        }
        rows.append(row)
    if not rows:
        raise HorizonsError("nessuna riga Horizons")
    return rows


def target_name(result: str) -> str:
    match = re.search(r"Target body name:\s+(.+?)\s+\{", result)
    if match:
        return match.group(1).strip()
    return ""


def _local(when: datetime | None, tz: ZoneInfo) -> str:
    if when is None:
        return "—"
    return when.astimezone(tz).strftime("%H:%M")


def cnst_it(code: str) -> str:
    key = str(code or "").strip()
    if not key:
        return ""
    return CNST_IT.get(key, key)


CARD_SHORT = ("N", "NE", "E", "SE", "S", "SO", "O", "NO")
CARD_LONG = ("nord", "nord-est", "est", "sud-est", "sud", "sud-ovest", "ovest", "nord-ovest")
AU_KM = 149597870.7


def cardinal_from_az(az: float | None) -> str:
    if az is None:
        return ""
    idx = int((az + 22.5) % 360 // 45)
    return CARD_SHORT[idx]


def cardinal_long(az: float | None) -> str:
    if az is None:
        return ""
    idx = int((az + 22.5) % 360 // 45)
    return CARD_LONG[idx]


def _lead_it(code: str) -> str:
    if code == "/L":
        return "cielo del mattino: sorge prima del Sole"
    if code == "/T":
        return "cielo della sera: tramonta dopo il Sole"
    return ""


def _side(alt: float | None) -> str:
    if alt is None:
        return "posizione non arrivata"
    return "sopra l'orizzonte" if alt > 0 else "sotto l'orizzonte"


def height_it(alt: float | None) -> str:
    if alt is None:
        return "altezza non arrivata"
    if alt < 0:
        return f"sotto l'orizzonte ({alt:.0f}°)"
    if alt < 15:
        return f"basso sull'orizzonte ({alt:.0f}°)"
    if alt < 40:
        return f"a mezza altezza ({alt:.0f}°)"
    return f"alto in cielo ({alt:.0f}°)"


def mag_it(mag: float | None, *, up: bool) -> str:
    if mag is None:
        return ""
    if mag <= 2:
        how = "luminoso: in cielo buio si prende a occhio nudo"
    elif mag <= 4.5:
        how = "in cielo buio si vede a occhio nudo"
    elif mag <= 8:
        how = "serve un binocolo"
    else:
        how = "solo telescopio"
    if not up:
        how = how + ", quando sarà sopra"
    return f"{how} (mag {mag:.1f})"


def dist_it(delta_au: float) -> str:
    km = float(delta_au) * AU_KM
    if km < 2_000_000:
        near = f"{km / 1000:.0f} mila km"
    elif km < 1_000_000_000:
        near = f"{km / 1_000_000:.1f} milioni di km"
    else:
        near = f"{km / 1_000_000_000:.2f} miliardi di km"
    return f"{near} ({delta_au:.3f} UA)"


def light_it(delta_au: float) -> str:
    minutes = float(delta_au) * LIGHT_MIN_PER_AU
    if minutes >= 60:
        return f"la luce ci mette {minutes / 60:.1f} ore"
    return f"la luce ci mette {minutes:.1f} minuti"


def elong_it(elong: float | None, lead: str) -> str:
    if elong is None:
        return _lead_it(lead)
    if elong < 15:
        where = "ancora attaccato al Sole, visibile solo nel crepuscolo"
    elif elong < 45:
        where = "non lontano dal Sole"
    elif elong < 90:
        where = "abbastanza lontano dal Sole"
    else:
        where = "lontano dal Sole, cielo buio"
    extra = _lead_it(lead)
    return f"{where} (elongazione {elong:.0f}°)" + (f" · {extra}" if extra else "")


def motion_it(deldot: float | None) -> str:
    """Horizons dà deldot in UA/giorno. Fuori da 0.00005–0.15 è una colonna sbagliata."""
    if deldot is None:
        return ""
    value = float(deldot)
    if abs(value) < 0.00005 or abs(value) > 0.15:
        return ""
    km_s = value * AU_KM / 86400.0
    if value < 0:
        return f"si avvicina (~{abs(km_s):.1f} km/s)"
    return f"si allontana (~{km_s:.1f} km/s)"


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _astro_time(when: datetime) -> astronomy.Time:
    utc = when.astimezone(timezone.utc)
    return astronomy.Time.Make(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        utc.second + utc.microsecond / 1_000_000,
    )


def _round_when(when: datetime) -> datetime:
    utc = when.astimezone(timezone.utc)
    return utc.replace(minute=(utc.minute // 5) * 5, second=0, microsecond=0)


def _helio_au(body: astronomy.Body, moment: astronomy.Time) -> float | None:
    try:
        vec = astronomy.HelioVector(body, moment)
        return (float(vec.x) ** 2 + float(vec.y) ** 2 + float(vec.z) ** 2) ** 0.5
    except Exception:
        return None


def observer_from_engine(command: str, lat: float, lon: float, when: datetime, *, elev_km: float = 0.05) -> dict[str, Any]:
    body = ENGINE_BODY.get(command)
    if body is None:
        raise HorizonsError("niente calcolo locale per questo corpo")
    moment = _astro_time(when)
    site = astronomy.Observer(lat, lon, elev_km)
    eq = astronomy.Equator(body, moment, site, True, True)
    hor = astronomy.Horizon(moment, site, eq.ra, eq.dec, astronomy.Refraction.Normal)
    ill = astronomy.Illumination(body, moment)
    elong = astronomy.Elongation(body, moment)
    cnst = astronomy.Constellation(eq.ra, eq.dec)
    vis = str(getattr(elong, "visibility", "") or "")
    lead = "/L" if "Morning" in vis else "/T" if "Evening" in vis else ""
    fraction = getattr(ill, "phase_fraction", None)
    return {
        "when": when.astimezone(timezone.utc),
        "az": float(hor.azimuth),
        "alt": float(hor.altitude),
        "ra": float(eq.ra),
        "dec": float(eq.dec),
        "mag": float(ill.mag) if ill.mag is not None else None,
        "illum": float(fraction) * 100.0 if isinstance(fraction, (int, float)) else None,
        "delta_au": float(eq.dist),
        "r_au": _helio_au(body, moment),
        "elong": float(elong.elongation),
        "phase": float(getattr(ill, "phase_angle", 0.0) or 0.0),
        "lead": lead,
        "cnst": str(getattr(cnst, "symbol", "") or ""),
        "target": body.name,
        "command": command,
        "source": "engine",
    }


def rts_from_engine(command: str, lat: float, lon: float, day: datetime, *, elev_km: float = 0.05) -> list[dict[str, Any]]:
    body = ENGINE_BODY.get(command)
    if body is None:
        raise HorizonsError("niente orari locali per questo corpo")
    start = day.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    moment = _astro_time(start)
    site = astronomy.Observer(lat, lon, elev_km)
    rows: list[dict[str, Any]] = []
    rise = astronomy.SearchRiseSet(body, site, astronomy.Direction.Rise, moment, 1.2)
    sett = astronomy.SearchRiseSet(body, site, astronomy.Direction.Set, moment, 1.2)
    cul = astronomy.SearchHourAngle(body, site, 0.0, moment)
    if rise is not None:
        stamp = rise.Utc().replace(tzinfo=timezone.utc)
        rows.append({"when": stamp, "event": "r", "source": "engine"})
    if cul is not None and getattr(cul, "time", None) is not None:
        stamp = cul.time.Utc().replace(tzinfo=timezone.utc)
        rows.append({"when": stamp, "event": "t", "alt": float(cul.hor.altitude), "source": "engine"})
    if sett is not None:
        stamp = sett.Utc().replace(tzinfo=timezone.utc)
        rows.append({"when": stamp, "event": "s", "source": "engine"})
    rows.sort(key=lambda row: row["when"])
    return rows


async def fetch_horizons(
    client: httpx.AsyncClient,
    *,
    command: str,
    params: dict[str, str],
) -> str:
    payload = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        **params,
    }
    last: Exception | None = None
    for attempt in range(2):
        try:
            response = await client.get(HORIZONS_URL, params=payload)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise HorizonsError("risposta Horizons non valida")
            if data.get("error"):
                raise HorizonsError(str(data.get("error")))
            result = str(data.get("result") or "")
            if "$$SOE" not in result:
                raise HorizonsError(result.strip()[:180] or "Horizons senza tabella")
            return result
        except (httpx.HTTPError, ValueError, HorizonsError) as exc:
            last = exc
            if attempt == 0:
                await asyncio.sleep(0.6)
    raise HorizonsError(str(last) if last else "Horizons offline")


async def fetch_observer(
    client: httpx.AsyncClient,
    command: str,
    lat: float,
    lon: float,
    when: datetime,
    *,
    elev_km: float = 0.05,
) -> dict[str, Any]:
    rounded = _round_when(when)
    stamp = rounded.strftime("%Y-%m-%d %H:%M")
    cache_key = f"obs:{command}:{round(lat, 3)}:{round(lon, 3)}:{stamp}"
    cached = _cache_get(cache_key)
    if isinstance(cached, dict):
        return cached
    end = rounded + timedelta(minutes=1)
    try:
        async with _gate:
            result = await fetch_horizons(
                client,
                command=command,
                params={
                    "EPHEM_TYPE": "OBSERVER",
                    "CENTER": "'coord@399'",
                    "COORD_TYPE": "GEODETIC",
                    "SITE_COORD": f"'{lon:.4f},{lat:.4f},{elev_km:.3f}'",
                    "START_TIME": f"'{stamp}'",
                    "STOP_TIME": f"'{end.strftime('%Y-%m-%d %H:%M')}'",
                    "STEP_SIZE": "1m",
                    "QUANTITIES": "'4,9,10,13,19,20,23,24,29'",
                    "ANG_FORMAT": "DEG",
                    "CSV_FORMAT": "YES",
                    "CAL_FORMAT": "CAL",
                },
            )
        row = parse_observer_rows(result)[0]
        row["target"] = target_name(result)
        row["command"] = command
        row["source"] = "horizons"
        if command in ENGINE_BODY:
            extra = observer_from_engine(command, lat, lon, rounded, elev_km=elev_km)
            row.setdefault("ra", extra.get("ra"))
            row.setdefault("dec", extra.get("dec"))
            row.setdefault("r_au", extra.get("r_au"))
        return _cache_set(cache_key, row)
    except HorizonsError:
        row = observer_from_engine(command, lat, lon, rounded, elev_km=elev_km)
        return _cache_set(cache_key, row)


async def fetch_rts(
    client: httpx.AsyncClient,
    command: str,
    lat: float,
    lon: float,
    day: datetime,
    *,
    elev_km: float = 0.05,
) -> list[dict[str, Any]]:
    start = day.astimezone(timezone.utc).strftime("%Y-%m-%d")
    stop = (day.astimezone(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    cache_key = f"rts:{command}:{round(lat, 3)}:{round(lon, 3)}:{start}"
    cached = _cache_get(cache_key)
    if isinstance(cached, list):
        return cached
    try:
        async with _gate:
            result = await fetch_horizons(
                client,
                command=command,
                params={
                    "EPHEM_TYPE": "OBSERVER",
                    "CENTER": "'coord@399'",
                    "COORD_TYPE": "GEODETIC",
                    "SITE_COORD": f"'{lon:.4f},{lat:.4f},{elev_km:.3f}'",
                    "START_TIME": f"'{start}'",
                    "STOP_TIME": f"'{stop}'",
                    "STEP_SIZE": "'1m'",
                    "QUANTITIES": "'4'",
                    "ANG_FORMAT": "DEG",
                    "CSV_FORMAT": "YES",
                    "R_T_S_ONLY": "YES",
                },
            )
        rows = parse_observer_rows(result)
        for row in rows:
            row["source"] = "horizons"
        return _cache_set(cache_key, rows)
    except HorizonsError:
        rows = rts_from_engine(command, lat, lon, day, elev_km=elev_km)
        return _cache_set(cache_key, rows)


async def fetch_group(
    client: httpx.AsyncClient,
    keys: dict[str, dict[str, str]],
    lat: float,
    lon: float,
    when: datetime,
) -> list[tuple[str, dict[str, Any] | None]]:
    async def one(key: str) -> tuple[str, dict[str, Any] | None]:
        try:
            return key, await fetch_observer(client, keys[key]["command"], lat, lon, when)
        except HorizonsError:
            return key, None

    return await asyncio.gather(*[one(key) for key in keys])


def _e(text: str) -> str:
    return html.escape(text)


def _sort_items(
    items: list[tuple[str, dict[str, Any] | None]],
) -> list[tuple[str, dict[str, Any] | None]]:
    def key(pair: tuple[str, dict[str, Any] | None]) -> tuple[int, float, float]:
        _name, row = pair
        if row is None:
            return (2, 99.0, 0.0)
        alt = row.get("alt")
        mag = row.get("mag")
        up = 0 if isinstance(alt, (int, float)) and alt > 0 else 1
        brightness = float(mag) if isinstance(mag, (int, float)) else 99.0
        height = -float(alt) if isinstance(alt, (int, float)) else 0.0
        return (up, brightness, height)

    return sorted(items, key=key)


def format_observer_list(
    *,
    title: str,
    place: str,
    when: datetime,
    tz: ZoneInfo,
    items: list[tuple[str, dict[str, Any] | None]],
    catalog: dict[str, dict[str, str]],
    note: str,
) -> str:
    local = when.astimezone(tz)
    lines = [
        f"{title} — {_e(place.upper())}",
        f"📅 {_e(local.strftime('%d/%m/%Y'))} · {local.strftime('%H:%M')} ora locale",
        "",
        "Dal tuo punto: dove sta, verso dove guardare, se è facile. "
        "Tocca un nome per la scheda completa.",
        "",
    ]
    used_engine = False
    above: list[str] = []
    below: list[str] = []
    missing: list[str] = []
    for key, row in _sort_items(items):
        meta = catalog[key]
        if row is None:
            missing.append(f"{meta['emoji']} <b>{_e(meta['it'])}</b> — Horizons non ha risposto.")
            continue
        if row.get("source") == "engine":
            used_engine = True
        alt = row.get("alt")
        block = _pretty_row(meta, row)
        if isinstance(alt, (int, float)) and alt > 0:
            above.append(block)
        else:
            below.append(block)
    if above:
        lines.append("⬆️ <b>SOPRA DI TE ADESSO</b>")
        lines.append("")
        lines.extend(above)
    if below:
        lines.append("⬇️ <b>SOTTO L'ORIZZONTE</b>")
        lines.append("Ora non si vedono. Resta utile sapere se tornano al mattino o alla sera.")
        lines.append("")
        lines.extend(below)
    if missing:
        lines.append("⚠️ <b>SENZA DATI</b>")
        lines.extend(missing)
        lines.append("")
    if not above and not below and not missing:
        lines.append("Nessun corpo è arrivato. Riprova tra un minuto.")
    elif above:
        names = []
        for key, row in _sort_items(items):
            if row and isinstance(row.get("alt"), (int, float)) and row["alt"] > 0:
                names.append(catalog[key]["it"])
        lines.append(f"Sopra adesso: {', '.join(names)}.")
    if used_engine:
        note = note + " Qualche riga è calcolata in locale (Astronomy Engine)."
    lines.extend(["", f"<i>{_e(note)}</i>"])
    return "\n".join(lines)


def _pretty_row(meta: dict[str, str], row: dict[str, Any]) -> str:
    alt = row.get("alt") if isinstance(row.get("alt"), (int, float)) else None
    az = row.get("az") if isinstance(row.get("az"), (int, float)) else None
    mag = row.get("mag") if isinstance(row.get("mag"), (int, float)) else None
    up = alt is not None and alt > 0
    look = f", verso {cardinal_long(az)}" if az is not None else ""
    sentence = f"{meta['emoji']} <b>{_e(meta['it'])}</b> — {height_it(alt)}{look}."
    bits: list[str] = []
    is_sun = meta.get("it") == "Sole" or meta.get("command") == "10"
    seen = "" if is_sun else mag_it(mag, up=up)
    if seen:
        bits.append(seen)
    cnst = cnst_it(str(row.get("cnst") or ""))
    if cnst:
        bits.append(f"in {cnst}")
    elong = row.get("elong") if isinstance(row.get("elong"), (int, float)) else None
    sun = "" if is_sun else elong_it(elong, str(row.get("lead") or ""))
    if sun:
        bits.append(sun)
    extra = "\n" + " · ".join(bits) if bits else ""
    return sentence + extra + "\n"


def format_distances(
    *,
    place: str,
    when: datetime,
    tz: ZoneInfo,
    items: list[tuple[str, dict[str, Any] | None]],
    catalog: dict[str, dict[str, str]],
) -> str:
    local = when.astimezone(tz)
    lines = [
        f"📏 <b>QUANTO SONO LONTANI — {_e(place.upper())}</b>",
        f"📅 {_e(local.strftime('%d/%m/%Y'))} · {local.strftime('%H:%M')}",
        "",
        "Distanza in linea d'aria da te, non dal Sole. Dal più vicino al più lontano.",
        "",
    ]
    ranked: list[tuple[float, str]] = []
    for key, row in items:
        meta = catalog[key]
        if row is None or not isinstance(row.get("delta_au"), (int, float)):
            lines.append(f"{meta['emoji']} {meta['it']} — distanza non arrivata")
            continue
        delta = float(row["delta_au"])
        move = motion_it(row.get("deldot") if isinstance(row.get("deldot"), (int, float)) else None)
        ranked.append(
            (
                delta,
                f"{meta['emoji']} <b>{_e(meta['it'])}</b>\n"
                f"{dist_it(delta)} · {light_it(delta)}"
                + (f" · {move}" if move else ""),
            )
        )
    ranked.sort(key=lambda item: item[0])
    for _delta, text in ranked:
        lines.append(text)
        lines.append("")
    lines.append(
        "<i>JPL Horizons, quantità 20 (delta). "
        "1 UA = distanza media Terra–Sole. I minuti di luce sono 8,32 × UA.</i>"
    )
    return "\n".join(lines)


def format_rts_list(
    *,
    place: str,
    tz: ZoneInfo,
    items: list[tuple[str, list[dict[str, Any]] | None]],
    catalog: dict[str, dict[str, str]],
) -> str:
    lines = [
        f"⬆️ <b>QUANDO SORGONO E TRAMONTANO — {_e(place.upper())}</b>",
        "Orari di oggi da questa città: sorge, passa più alto, tramonta.",
        "",
    ]
    labels = {"r": "sorge", "t": "più alto", "s": "tramonta"}
    any_ok = False
    for key, rows in items:
        meta = catalog[key]
        if not rows:
            lines.append(f"{meta['emoji']} <b>{_e(meta['it'])}</b> — orari non arrivati")
            continue
        any_ok = True
        bits: list[str] = []
        for row in rows:
            ev = str(row.get("event") or "")
            if ev not in labels:
                continue
            bits.append(f"{labels[ev]} {_local(row.get('when'), tz)}")
        if bits:
            lines.append(f"{meta['emoji']} <b>{_e(meta['it'])}</b>\n" + " · ".join(bits))
        else:
            lines.append(
                f"{meta['emoji']} <b>{_e(meta['it'])}</b> — "
                "in queste 24 ore non sorge né tramonta (resta sotto o resta sopra)."
            )
        lines.append("")
    if not any_ok:
        lines.append("Niente orari per questo giorno.")
    lines.extend(
        [
            "<i>Horizons R_T_S_ONLY, orizzonte geometrico. "
            "Basso sull'orizzonte può restare invisibile anche se è «sopra».</i>",
        ]
    )
    return "\n".join(lines)


def format_body_card(
    *,
    meta: dict[str, str],
    place: str,
    when: datetime,
    tz: ZoneInfo,
    row: dict[str, Any],
) -> str:
    local = when.astimezone(tz)
    alt = row.get("alt") if isinstance(row.get("alt"), (int, float)) else None
    az = row.get("az") if isinstance(row.get("az"), (int, float)) else None
    mag = row.get("mag") if isinstance(row.get("mag"), (int, float)) else None
    delta = row.get("delta_au") if isinstance(row.get("delta_au"), (int, float)) else None
    r_au = row.get("r_au") if isinstance(row.get("r_au"), (int, float)) else None
    illum = row.get("illum") if isinstance(row.get("illum"), (int, float)) else None
    elong = row.get("elong") if isinstance(row.get("elong"), (int, float)) else None
    phase = row.get("phase") if isinstance(row.get("phase"), (int, float)) else None
    diam = row.get("ang_diam") if isinstance(row.get("ang_diam"), (int, float)) else None
    deldot = row.get("deldot") if isinstance(row.get("deldot"), (int, float)) else None
    cnst = cnst_it(str(row.get("cnst") or ""))
    target = str(row.get("target") or meta["it"])
    up = alt is not None and alt > 0
    look = f", verso {cardinal_long(az)}" if az is not None else ""
    is_sun = meta.get("it") == "Sole" or meta.get("command") == "10"
    lines = [
        f"{meta['emoji']} <b>{_e(meta['it'].upper())} — {_e(place.upper())}</b>",
        f"<i>{_e(target)}</i>",
        f"📅 {_e(local.strftime('%d/%m/%Y'))} · {local.strftime('%H:%M')}",
        "",
        f"{_cap(height_it(alt))}{look}.",
    ]
    seen = "" if is_sun else mag_it(mag, up=up)
    if seen:
        lines.append(_cap(seen) + ".")
    if cnst:
        lines.append(f"Si trova nella costellazione {cnst}.")
    sun = "" if is_sun else elong_it(elong, str(row.get("lead") or ""))
    if sun:
        lines.append(_cap(sun) + ".")
    lines.append("")
    if delta is not None:
        move = motion_it(deldot)
        lines.append(f"📏 Da te: {dist_it(delta)} · {light_it(delta)}" + (f" · {move}" if move else ""))
    if r_au is not None and meta.get("it") != "Sole":
        lines.append(f"☀️ Dal Sole: {dist_it(r_au)}")
    if isinstance(illum, (int, float)):
        lines.append(f"🌕 Disco illuminato dal Sole: {illum:.0f}%")
    if isinstance(diam, (int, float)) and diam > 0:
        lines.append(f"📐 Quanto appare grande: {diam:.1f} secondi d'arco")
    if isinstance(phase, (int, float)):
        lines.append(f"Angolo Sole–oggetto–tu: {phase:.0f}°")
    ra = row.get("ra")
    dec = row.get("dec")
    if isinstance(ra, (int, float)) and isinstance(dec, (int, float)):
        hours = int(ra)
        mins = int(abs(ra - hours) * 60)
        lines.append("")
        lines.append(
            f"Coordinate per puntare: RA {hours:02d}h {mins:02d}m · DEC {dec:+.1f}°"
        )
    if isinstance(alt, (int, float)) and isinstance(az, (int, float)):
        lines.append(f"Altezza {alt:.1f}° · azimut {az:.0f}° ({cardinal_from_az(az)})")
    src = "JPL Horizons" if row.get("source") == "horizons" else "calcolo locale (Astronomy Engine)"
    lines.extend(
        [
            "",
            f"<i>{src}, dal tuo punto. "
            "La magnitudine dice quanto è luminoso, non se il meteo te lo lascia vedere.</i>",
        ]
    )
    return "\n".join(lines)
