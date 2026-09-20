"""Attrezzi di STRUMENTI: coordinate, ora e calendario civile. Algoritmi veri."""

from __future__ import annotations

import calendar
import html as _html
import re
from datetime import date, datetime, timezone
from io import BytesIO

import astronomy
from PIL import Image, ImageDraw, ImageFont

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


_CAL_HEAD = ("Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom")
_CAL_COL = 4


def format_month_calendar(year: int, month: int, today: date) -> str:
    """Griglia ASCII di riserva. La carta vera è draw_month_calendar."""
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    weeks = cal.monthdayscalendar(year, month)
    heads = "|" + "".join(f"{head:>{_CAL_COL}}" for head in _CAL_HEAD)
    rule = "|" + "".join(f"{'---':>{_CAL_COL}}" for _ in _CAL_HEAD)
    lines = [heads, rule]
    for week in weeks:
        cells = ["|"]
        for day in week:
            if day == 0:
                cells.append(" " * _CAL_COL)
            elif today.year == year and today.month == month and today.day == day:
                cells.append(f"[{day:2d}]")
            else:
                cells.append(f"{day:{_CAL_COL}d}")
        lines.append("".join(cells))
    title = f"{_MONTHS_IT[month - 1]} {year}"
    return f"<b>{_html.escape(title)}</b>\n<pre>{_html.escape(chr(10).join(lines))}</pre>"


def _cal_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf")
        if bold
        else ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")
    )
    for name in names:
        for folder in (
            "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts/truetype/liberation",
        ):
            try:
                return ImageFont.truetype(f"{folder}/{name}", size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_month_calendar(
    year: int,
    month: int,
    today: date,
    clock: datetime | None = None,
    marks: set[int] | None = None,
) -> bytes:
    """Ora grande + mese civile a colonne. Lunedì in testa, oggi nel riquadro."""
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    weeks = cal.monthdayscalendar(year, month)
    cols, rows = 7, len(weeks)
    left = 28
    clock_h = 118 if clock is not None else 0
    top = 92 + clock_h
    width, height = 720, top + 56 + rows * 72 + 28
    cell_w = (width - left * 2) / cols
    cell_h = 68
    img = Image.new("RGB", (width, height), (10, 12, 20))
    draw = ImageDraw.Draw(img)
    clock_font = _cal_font(56, bold=True)
    title_font = _cal_font(28, bold=True)
    head_font = _cal_font(18, bold=True)
    day_font = _cal_font(26, bold=True)
    if clock is not None:
        stamp = clock.strftime("%H:%M:%S")
        cb = draw.textbbox((0, 0), stamp, font=clock_font)
        draw.text(((width - (cb[2] - cb[0])) / 2, 18), stamp, fill=(245, 248, 255), font=clock_font)
        dayline = f"{_WEEKDAYS_IT[clock.weekday()]} {clock.strftime('%d/%m/%Y')}"
        db = draw.textbbox((0, 0), dayline, font=head_font)
        draw.text(((width - (db[2] - db[0])) / 2, 82), dayline, fill=(168, 178, 198), font=head_font)
    title = f"{_MONTHS_IT[month - 1]} {year}"
    box = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (box[2] - box[0])) / 2, 22 + clock_h), title, fill=(236, 239, 247), font=title_font)
    for idx, head in enumerate(_CAL_HEAD):
        x = left + idx * cell_w
        hb = draw.textbbox((0, 0), head, font=head_font)
        draw.text(
            (x + (cell_w - (hb[2] - hb[0])) / 2, top - 28),
            head,
            fill=(168, 178, 198) if idx < 5 else (214, 168, 120),
            font=head_font,
        )
    for r, week in enumerate(weeks):
        for c, day in enumerate(week):
            x0 = left + c * cell_w
            y0 = top + r * cell_h
            x1, y1 = x0 + cell_w - 8, y0 + cell_h - 8
            if day == 0:
                continue
            is_today = today.year == year and today.month == month and today.day == day
            is_bday = bool(marks) and day in marks
            if is_today:
                draw.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=(52, 92, 168))
            elif is_bday:
                draw.rounded_rectangle((x0, y0, x1, y1), radius=14, outline=(214, 140, 90), width=3)
            if is_today and is_bday:
                draw.ellipse((x1 - 16, y0 + 6, x1 - 6, y0 + 16), fill=(230, 168, 96))
            label = str(day)
            db = draw.textbbox((0, 0), label, font=day_font)
            tw, th = db[2] - db[0], db[3] - db[1]
            fill = (245, 247, 252) if is_today else ((210, 214, 226) if c < 5 else (230, 186, 140))
            draw.text((x0 + (cell_w - 8 - tw) / 2, y0 + (cell_h - 8 - th) / 2 - 2), label, fill=fill, font=day_font)
    out = BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def weekday_it(stamp: date) -> str:
    return _WEEKDAYS_IT[stamp.weekday()]
