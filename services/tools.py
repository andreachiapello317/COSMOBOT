"""Attrezzi di STRUMENTI: coordinate e giorno giuliano. Algoritmi veri, niente enciclopedia."""

from __future__ import annotations

import re
from datetime import datetime, timezone

import astronomy

# Astronomy Engine: Time.ut è giorni da J2000.0, non il JD civile.
JD_J2000 = 2451545.0


def julian_of(when: datetime) -> dict[str, float]:
    utc = when.astimezone(timezone.utc)
    moment = astronomy.Time.Make(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        utc.second + utc.microsecond / 1_000_000,
    )
    jd = float(moment.ut) + JD_J2000
    return {"jd": jd, "mjd": jd - 2400000.5, "j2000": float(moment.ut)}


def parse_tool_date(text: str) -> datetime | None:
    raw = str(text or "").strip()
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            stamp = datetime.strptime(raw, fmt)
        except ValueError:
            continue
        return stamp.replace(tzinfo=timezone.utc)
    return None


def dec_to_dms(value: float, *, lat: bool) -> str:
    hemi = ("N" if value >= 0 else "S") if lat else ("E" if value >= 0 else "O")
    abs_v = abs(float(value))
    deg = int(abs_v)
    minutes_f = (abs_v - deg) * 60.0
    minutes = int(minutes_f)
    seconds = (minutes_f - minutes) * 60.0
    return f"{deg}° {minutes:02d}′ {seconds:04.1f}″ {hemi}"


def parse_coord_pair(text: str) -> tuple[float, float] | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    simple = re.match(
        r"^\s*(-?\d+(?:[.,]\d+)?)\s*[,;\s]\s*(-?\d+(?:[.,]\d+)?)\s*$",
        raw,
    )
    if simple:
        lat = float(simple.group(1).replace(",", "."))
        lon = float(simple.group(2).replace(",", "."))
        if abs(lat) <= 90 and abs(lon) <= 180:
            return lat, lon
    dms = re.findall(
        r"(-?\d+(?:[.,]\d+)?)[°\s]+(\d+(?:[.,]\d+)?)[′'\s]+(\d+(?:[.,]\d+)?)[″\"]?\s*([NSEOnseo])?",
        raw,
    )
    if len(dms) >= 2:
        def one(deg: str, minutes: str, seconds: str, hemi: str) -> float:
            value = abs(float(deg.replace(",", "."))) + float(minutes.replace(",", ".")) / 60.0 + float(
                seconds.replace(",", ".")
            ) / 3600.0
            letter = (hemi or "").upper()
            if letter in {"S", "O", "W"} or float(deg.replace(",", ".")) < 0:
                value = -value
            return value

        lat = one(*dms[0])
        lon = one(*dms[1])
        if abs(lat) <= 90 and abs(lon) <= 180:
            return lat, lon
    return None


def format_coord_card(name: str, lat: float, lon: float) -> str:
    label = name.strip() or "punto"
    return (
        f"📐 <b>COORDINATE — {label.upper()}</b>\n"
        "<i>Stessi numeri, due scritture. WGS84, niente navigatore.</i>\n\n"
        f"Decimale: <code>{lat:.6f}, {lon:.6f}</code>\n"
        f"Gradi: <code>{dec_to_dms(lat, lat=True)}</code> · "
        f"<code>{dec_to_dms(lon, lat=False)}</code>\n\n"
        "Scrivi una coppia, ad esempio <code>44.3904, 7.5483</code> "
        "oppure <code>44°23′25″ N, 7°32′54″ E</code>."
    )


def format_julian_card(when: datetime, stamp_it: str) -> str:
    row = julian_of(when)
    return (
        "📅 <b>GIORNO GIULIANO</b>\n"
        "<i>Scala continua degli astronomi. Astronomy Engine, non un calendario inventato.</i>\n\n"
        f"Istante: <b>{stamp_it}</b> (UTC)\n"
        f"JD: <code>{row['jd']:.5f}</code>\n"
        f"MJD: <code>{row['mjd']:.5f}</code>\n"
        f"Giorni da J2000: <code>{row['j2000']:.5f}</code>\n\n"
        "Scrivi una data: <code>20/09/2026</code> oppure <code>20/09/2026 22:00</code>."
    )
