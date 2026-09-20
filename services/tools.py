"""Attrezzi di STRUMENTI: coordinate, giorno giuliano, calendario. Algoritmi veri."""

from __future__ import annotations

import calendar
import html as _html
import re
from datetime import date, datetime, timezone

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
        "<i>Dentro Bussola. WGS84, due scritture, niente navigatore.</i>\n\n"
        f"Decimale: <code>{lat:.6f}, {lon:.6f}</code>\n"
        f"Gradi: <code>{dec_to_dms(lat, lat=True)}</code> · "
        f"<code>{dec_to_dms(lon, lat=False)}</code>\n\n"
        "Per un punto preciso scrivi <b>via e numero</b> "
        "(<code>Corso Nizza 12, Cuneo</code>) oppure le coordinate "
        "(<code>44.390400, 7.548300</code> o "
        "<code>44°23′25.4″ N, 7°32′54.0″ E</code>).\n"
        "Il tasto GPS di Telegram sul computer non funzionava: qui il punto arriva da "
        "OpenStreetMap o da numeri che scrivi tu. Sei decimali ≈ un metro."
    )


def format_julian_card(when: datetime, stamp_it: str) -> str:
    row = julian_of(when)
    return (
        "📅 <b>GIORNO GIULIANO</b>\n"
        "<i>Non è un giorno della settimana. È un contatore.</i>\n\n"
        "Gli astronomi non vogliono mesi, anni bisestili e fusi in mezzo ai calcoli. "
        "Il <b>giorno giuliano</b> (JD) è un numero continuo di giorni: "
        "JD 0 è il mezzogiorno del 1º gennaio 4713 a.C. (prolettico). "
        "Cambia di 1 ogni 24 ore; i decimali sono l'ora (0,5 = mezzanotte UTC).\n\n"
        "Il <b>MJD</b> (giorno giuliano modificato) è JD − 2 400 000,5: stesso istante, "
        "numeri più corti, e parte da mezzanotte. "
        "I <b>giorni da J2000</b> partono dal mezzogiorno del 1º gennaio 2000, "
        "l'epoca usata dalle effemeridi moderne.\n\n"
        f"Istante: <b>{stamp_it}</b> (UTC)\n"
        f"JD: <code>{row['jd']:.5f}</code>\n"
        f"MJD: <code>{row['mjd']:.5f}</code>\n"
        f"Giorni da J2000: <code>{row['j2000']:.5f}</code>\n\n"
        "<i>Astronomy Engine. Scrivi una data: <code>20/09/2026</code> "
        "oppure <code>20/09/2026 22:00</code>.</i>"
    )


_MONTHS_IT = (
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
)
_WEEKDAYS_IT = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    idx = year * 12 + (month - 1) + int(delta)
    return idx // 12, idx % 12 + 1


def format_month_calendar(year: int, month: int, today: date) -> str:
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)
    lines = ["lun mar mer gio ven sab dom"]
    for week in weeks:
        cells: list[str] = []
        for day in week:
            if day == 0:
                cells.append("  .")
                continue
            mark = "*" if today.year == year and today.month == month and today.day == day else " "
            cells.append(f"{day:2d}{mark}")
        lines.append(" ".join(cells))
    title = f"{_MONTHS_IT[month - 1]} {year}"
    return f"<b>{_html.escape(title)}</b>\n<code>{_html.escape(chr(10).join(lines))}</code>"


def weekday_it(stamp: date) -> str:
    return _WEEKDAYS_IT[stamp.weekday()]
