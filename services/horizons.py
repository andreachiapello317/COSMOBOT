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


def cardinal_from_az(az: float | None) -> str:
    if az is None:
        return ""
    names = ("N", "NE", "E", "SE", "S", "SO", "O", "NO")
    idx = int((az + 22.5) % 360 // 45)
    return names[idx]


def _lead_it(code: str) -> str:
    if code == "/L":
        return "sorge prima del Sole (cielo del mattino)"
    if code == "/T":
        return "tramonta dopo il Sole (cielo della sera)"
    return ""


def _side(alt: float | None) -> str:
    if alt is None:
        return "—"
    return "↑ sopra" if alt > 0 else "↓ sotto"


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
                    "QUANTITIES": "'4,9,10,13,20,23,24,29'",
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
        "Posizioni dal luogo che hai dato. Horizons se risponde, altrimenti calcolo locale.",
        "",
    ]
    up = 0
    used_engine = False
    for key, row in items:
        meta = catalog[key]
        if row is None:
            lines.append(f"{meta['emoji']} <b>{_e(meta['it'])}</b>  <i>niente dati adesso</i>")
            continue
        if row.get("source") == "engine":
            used_engine = True
        alt = row.get("alt")
        if isinstance(alt, (int, float)) and alt > 0:
            up += 1
        lines.append(_pretty_row(meta, row))
        lines.append("")
    if not any(row for _key, row in items):
        lines.append("Nessun corpo è arrivato. Riprova tra un minuto.")
    else:
        lines.append(f"Sopra l'orizzonte adesso: {up}.")
    if used_engine:
        note = note + " Qualche riga è calcolata in locale (Astronomy Engine)."
    lines.extend(["", f"<i>{_e(note)}</i>"])
    return "\n".join(lines)


def _pretty_row(meta: dict[str, str], row: dict[str, Any]) -> str:
    alt = row.get("alt")
    az = row.get("az")
    mag = row.get("mag")
    delta = row.get("delta_au")
    elong = row.get("elong")
    illum = row.get("illum")
    cnst = cnst_it(str(row.get("cnst") or ""))
    head = f"{meta['emoji']} <b>{_e(meta['it'])}</b>  {_side(alt if isinstance(alt, (int, float)) else None)}"
    bits: list[str] = []
    if isinstance(alt, (int, float)):
        card = cardinal_from_az(az if isinstance(az, (int, float)) else None)
        az_bit = f", az {az:.0f}° {card}" if isinstance(az, (int, float)) else ""
        bits.append(f"altezza {alt:.0f}°{az_bit}")
    if isinstance(mag, (int, float)):
        bits.append(f"mag {mag:.1f}")
    if isinstance(delta, (int, float)):
        bits.append(f"{delta:.3f} UA")
    if isinstance(illum, (int, float)):
        bits.append(f"illum. {illum:.0f}%")
    if isinstance(elong, (int, float)):
        lead = _lead_it(str(row.get("lead") or ""))
        bits.append(f"elongazione {elong:.0f}°" + (f", {lead}" if lead else ""))
    if cnst:
        bits.append(f"in {cnst}")
    return head + ("\n" + " · ".join(bits) if bits else "")


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
        f"📏 <b>DISTANZE — {_e(place.upper())}</b>",
        f"📅 {_e(local.strftime('%d/%m/%Y'))} · {local.strftime('%H:%M')}",
        "",
        "Delta Horizons (UA dal tuo punto). I minuti di luce sono 8,32 × UA: conversione, non un'altra misura.",
        "",
    ]
    ranked: list[tuple[float, str]] = []
    for key, row in items:
        meta = catalog[key]
        if row is None or not isinstance(row.get("delta_au"), (int, float)):
            lines.append(f"{meta['emoji']} {meta['it']} — niente distanza adesso")
            continue
        delta = float(row["delta_au"])
        minutes = delta * LIGHT_MIN_PER_AU
        if minutes >= 60:
            light = f"{minutes / 60:.2f} h di luce"
        else:
            light = f"{minutes:.1f} min di luce"
        ranked.append((delta, f"{meta['emoji']} <b>{_e(meta['it'])}</b>  {delta:.3f} UA · {light}"))
    ranked.sort(key=lambda item: item[0])
    lines.extend(text for _delta, text in ranked)
    lines.extend(
        [
            "",
            "<i>JPL Horizons observer table, quantità 20 (delta). "
            "Non è la distanza dal Sole: è dal luogo che hai dato.</i>",
        ]
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
        f"⬆️ <b>ALBA E TRAMONTO DEI PIANETI — {_e(place.upper())}</b>",
        "Orari Horizons rise / transit / set, convertiti nell'ora della città.",
        "",
    ]
    labels = {"r": "alba", "t": "transito", "s": "tramonto"}
    any_ok = False
    for key, rows in items:
        meta = catalog[key]
        if not rows:
            lines.append(f"{meta['emoji']} <b>{_e(meta['it'])}</b>  <i>niente orari adesso</i>")
            continue
        any_ok = True
        bits: list[str] = []
        for row in rows:
            ev = str(row.get("event") or "")
            if ev not in labels:
                continue
            bits.append(f"{labels[ev]} {_local(row.get('when'), tz)}")
        lines.append(f"{meta['emoji']} <b>{_e(meta['it'])}</b>  " + (" · ".join(bits) if bits else "nessun evento RTS in 24 h"))
    if not any_ok:
        lines.append("Niente alba/tramonto dei pianeti per questo giorno.")
    lines.extend(
        [
            "",
            "<i>R_T_S_ONLY di Horizons, orizzonte geometrico del luogo. "
            "Un pianeta basso può restare invisibile anche se è 'sopra'.</i>",
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
    alt = row.get("alt")
    az = row.get("az")
    mag = row.get("mag")
    delta = row.get("delta_au")
    illum = row.get("illum")
    elong = row.get("elong")
    phase = row.get("phase")
    diam = row.get("ang_diam")
    cnst = cnst_it(str(row.get("cnst") or ""))
    target = str(row.get("target") or meta["it"])
    lines = [
        f"{meta['emoji']} <b>{_e(meta['it'].upper())} — {_e(place.upper())}</b>",
        f"<i>{_e(target)}</i>",
        f"📅 {_e(local.strftime('%d/%m/%Y'))} · {local.strftime('%H:%M')}",
        "",
        f"{_side(alt if isinstance(alt, (int, float)) else None)}",
    ]
    if isinstance(alt, (int, float)):
        card = cardinal_from_az(az if isinstance(az, (int, float)) else None)
        az_bit = f" · azimut {az:.1f}° {card}" if isinstance(az, (int, float)) else ""
        lines.append(f"Altezza {alt:.1f}°{az_bit}")
    ra = row.get("ra")
    dec = row.get("dec")
    if isinstance(ra, (int, float)) and isinstance(dec, (int, float)):
        hours = int(ra)
        mins = int(abs(ra - hours) * 60)
        lines.append(f"RA {hours:02d}h {mins:02d}m · DEC {dec:+.2f}°")
    visible = "sì" if isinstance(alt, (int, float)) and alt > 0 else "no"
    lines.append(f"Sopra l'orizzonte: {visible}")
    if isinstance(mag, (int, float)):
        lines.append(f"Magnitudine apparente {mag:.2f}")
    if isinstance(illum, (int, float)):
        lines.append(f"Disco illuminato {illum:.1f}%")
    if isinstance(delta, (int, float)):
        minutes = delta * LIGHT_MIN_PER_AU
        light = f"{minutes / 60:.2f} h" if minutes >= 60 else f"{minutes:.1f} min"
        lines.append(f"Distanza {delta:.4f} UA · luce {light}")
    if isinstance(diam, (int, float)):
        lines.append(f"Diametro apparente {diam:.2f}″")
    if isinstance(elong, (int, float)):
        lead = _lead_it(str(row.get("lead") or ""))
        lines.append(f"Elongazione solare {elong:.1f}°" + (f" · {lead}" if lead else ""))
    if isinstance(phase, (int, float)):
        lines.append(f"Angolo di fase {phase:.1f}°")
    if cnst:
        lines.append(f"Costellazione (IAU): {cnst}")
    lines.extend(
        [
            "",
            "<i>JPL Horizons, efemeride observer da queste coordinate. "
            "Non dico se lo vedi a occhio nudo: serve cielo buio e meteo, che qui non misuro.</i>",
        ]
    )
    return "\n".join(lines)
