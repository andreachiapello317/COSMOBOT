"""Eventi di calendario: Pasqua, Natale, feste civili. Algoritmi veri, niente date inventate."""

from __future__ import annotations

import html as _html
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import astronomy

ROME = ZoneInfo("Europe/Rome")
_WEEKDAYS = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")
_MONTHS = (
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

# Capodanno lunare cinese: date civili pubblicate (non un algoritmo approssimato).
_CNY: dict[int, tuple[int, int]] = {
    2015: (2, 19),
    2016: (2, 8),
    2017: (1, 28),
    2018: (2, 16),
    2019: (2, 5),
    2020: (1, 25),
    2021: (2, 12),
    2022: (2, 1),
    2023: (1, 22),
    2024: (2, 10),
    2025: (1, 29),
    2026: (2, 17),
    2027: (2, 6),
    2028: (1, 26),
    2029: (2, 13),
    2030: (2, 3),
    2031: (1, 23),
    2032: (2, 11),
    2033: (1, 31),
    2034: (2, 19),
    2035: (2, 8),
    2036: (1, 28),
    2037: (2, 15),
    2038: (2, 4),
    2039: (1, 24),
    2040: (2, 12),
}

YEAR_MIN = 1901
YEAR_MAX = 2099


def clamp_year(year: int) -> int:
    return max(YEAR_MIN, min(YEAR_MAX, int(year)))


def easter_western(year: int) -> date:
    """Pasqua gregoriana, algoritmo di Meeus/Jones/Butcher."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = ((h + ell - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def easter_orthodox(year: int) -> date:
    """Pasqua ortodossa: computus giuliano, poi conversione al gregoriano."""
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    delta = year // 100 - year // 400 - 2
    return date(year, month, day) + timedelta(days=delta)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    add = (weekday - first.weekday()) % 7
    return first + timedelta(days=add + 7 * (n - 1))


def advent_sunday(year: int) -> date:
    """Prima domenica di Avvento: domenica tra il 27 novembre e il 3 dicembre."""
    start = date(year, 11, 27)
    return start + timedelta(days=(6 - start.weekday()) % 7)


def _ae_local(moment: astronomy.Time) -> datetime:
    utc = moment.Utc()
    if utc.tzinfo is None:
        utc = utc.replace(tzinfo=timezone.utc)
    return utc.astimezone(ROME)


def season_marks(year: int) -> list[tuple[datetime, str, str]]:
    info = astronomy.Seasons(year)
    return [
        (_ae_local(info.mar_equinox), "🌸", "Equinozio di marzo"),
        (_ae_local(info.jun_solstice), "☀️", "Solstizio di giugno"),
        (_ae_local(info.sep_equinox), "🍂", "Equinozio di settembre"),
        (_ae_local(info.dec_solstice), "❄️", "Solstizio di dicembre"),
    ]


def _event(day: date, emoji: str, title: str, note: str = "", *, kind: str) -> dict[str, object]:
    return {"date": day, "emoji": emoji, "title": title, "note": note, "kind": kind}


def events_easter(year: int) -> list[dict[str, object]]:
    west = easter_western(year)
    east = easter_orthodox(year)
    rows = [
        _event(west - timedelta(days=47), "🎭", "Martedì grasso", "47 giorni prima della Pasqua occidentale", kind="easter"),
        _event(west - timedelta(days=46), "✝️", "Mercoledì delle Ceneri", "inizio Quaresima occidentale", kind="easter"),
        _event(west - timedelta(days=7), "🌿", "Domenica delle Palme", kind="easter"),
        _event(west - timedelta(days=3), "🍷", "Giovedì santo", kind="easter"),
        _event(west - timedelta(days=2), "✝️", "Venerdì santo", kind="easter"),
        _event(west, "🐣", "Pasqua occidentale", "computus gregoriano", kind="easter"),
        _event(west + timedelta(days=1), "🧺", "Pasquetta", "lunedì dell'Angelo", kind="easter"),
        _event(west + timedelta(days=39), "☁️", "Ascensione", "39 giorni dopo Pasqua", kind="easter"),
        _event(west + timedelta(days=49), "🔥", "Pentecoste", "49 giorni dopo Pasqua", kind="easter"),
        _event(west + timedelta(days=60), "🍞", "Corpus Domini", "60 giorni dopo Pasqua", kind="easter"),
        _event(east, "☦️", "Pasqua ortodossa", "computus giuliano, data gregoriana", kind="easter"),
    ]
    return sorted(rows, key=lambda row: row["date"])  # type: ignore[arg-type, return-value]


def events_xmas(year: int) -> list[dict[str, object]]:
    rows = [
        _event(date(year, 1, 6), "⭐", "Epifania", "Befana", kind="xmas"),
        _event(date(year, 1, 7), "🎄", "Natale ortodosso", "25 dicembre giuliano", kind="xmas"),
        _event(date(year, 12, 8), "💠", "Immacolata Concezione", kind="xmas"),
        _event(advent_sunday(year), "🕯️", "Prima domenica di Avvento", kind="xmas"),
        _event(date(year, 12, 24), "🎁", "Vigilia di Natale", kind="xmas"),
        _event(date(year, 12, 25), "🎄", "Natale", kind="xmas"),
        _event(date(year, 12, 26), "🎁", "Santo Stefano", kind="xmas"),
        _event(date(year, 1, 19), "💧", "Teofania ortodossa", "6 gennaio giuliano", kind="xmas"),
    ]
    return sorted(rows, key=lambda row: row["date"])  # type: ignore[arg-type, return-value]


def events_italy(year: int) -> list[dict[str, object]]:
    west = easter_western(year)
    rows = [
        _event(date(year, 1, 1), "🎆", "Capodanno", "festa civile italiana", kind="it"),
        _event(date(year, 1, 6), "⭐", "Epifania", "festa civile italiana", kind="it"),
        _event(date(year, 3, 19), "👔", "Festa del papà", "San Giuseppe", kind="it"),
        _event(west, "🐣", "Pasqua", kind="it"),
        _event(west + timedelta(days=1), "🧺", "Lunedì dell'Angelo", "Pasquetta", kind="it"),
        _event(date(year, 4, 25), "🇮🇹", "Festa della Liberazione", kind="it"),
        _event(nth_weekday(year, 5, 6, 2), "💐", "Festa della mamma", "seconda domenica di maggio", kind="it"),
        _event(date(year, 5, 1), "🛠️", "Festa del Lavoro", kind="it"),
        _event(date(year, 6, 2), "🇮🇹", "Festa della Repubblica", kind="it"),
        _event(date(year, 8, 15), "☀️", "Ferragosto", "Assunzione", kind="it"),
        _event(date(year, 11, 1), "🕯️", "Ognissanti", kind="it"),
        _event(date(year, 12, 8), "💠", "Immacolata Concezione", kind="it"),
        _event(date(year, 12, 25), "🎄", "Natale", kind="it"),
        _event(date(year, 12, 26), "🎁", "Santo Stefano", kind="it"),
    ]
    return sorted(rows, key=lambda row: row["date"])  # type: ignore[arg-type, return-value]


def events_world(year: int) -> list[dict[str, object]]:
    rows = [
        _event(date(year, 1, 1), "🎆", "Capodanno civile", kind="world"),
        _event(date(year, 2, 14), "💌", "San Valentino", kind="world"),
        _event(date(year, 3, 8), "💜", "Giornata internazionale della donna", kind="world"),
        _event(date(year, 4, 22), "🌍", "Giornata della Terra", kind="world"),
        _event(date(year, 5, 1), "🛠️", "Primo maggio", kind="world"),
        _event(date(year, 7, 4), "🇺🇸", "Independence Day", "Stati Uniti", kind="world"),
        _event(date(year, 7, 14), "🇫🇷", "Presa della Bastiglia", "Francia", kind="world"),
        _event(date(year, 10, 3), "🇩🇪", "Giorno dell'unità tedesca", kind="world"),
        _event(date(year, 10, 24), "🕊️", "Giornata delle Nazioni Unite", kind="world"),
        _event(date(year, 10, 31), "🎃", "Halloween", kind="world"),
        _event(date(year, 11, 1), "💀", "Día de Muertos", "Messico, 1–2 novembre", kind="world"),
        _event(nth_weekday(year, 11, 3, 4), "🦃", "Thanksgiving", "quarto giovedì di novembre, USA", kind="world"),
        _event(date(year, 12, 31), "🥂", "San Silvestro", kind="world"),
    ]
    cny = _CNY.get(year)
    if cny:
        rows.append(_event(date(year, cny[0], cny[1]), "🧧", "Capodanno cinese", "data civile del calendario lunare", kind="world"))
    eq = season_marks(year)[0][0]
    rows.append(_event(eq.date(), "🌱", "Nowruz", "equinozio di marzo, Astronomy Engine", kind="world"))
    return sorted(rows, key=lambda row: row["date"])  # type: ignore[arg-type, return-value]


def events_season(year: int) -> list[dict[str, object]]:
    rows = []
    for stamp, emoji, title in season_marks(year):
        rows.append(
            _event(
                stamp.date(),
                emoji,
                title,
                stamp.strftime("%H:%M") + " Europe/Rome · Astronomy Engine",
                kind="season",
            )
        )
    return rows


def all_events(year: int) -> list[dict[str, object]]:
    seen: set[tuple[date, str]] = set()
    out: list[dict[str, object]] = []
    for group in (events_easter(year), events_xmas(year), events_italy(year), events_world(year), events_season(year)):
        for row in group:
            key = (row["date"], str(row["title"]))  # type: ignore[index]
            if key in seen:
                continue
            seen.add(key)
            out.append(row)
    return sorted(out, key=lambda row: row["date"])  # type: ignore[arg-type, return-value]


def upcoming(today: date, *, limit: int = 12) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for year in (today.year, today.year + 1):
        if YEAR_MIN <= year <= YEAR_MAX:
            rows.extend(all_events(year))
    future = [row for row in rows if row["date"] >= today]  # type: ignore[operator]
    return future[:limit]


VIEWS = {
    "next": ("📅", "PROSSIMI", "Da oggi. Scorri le pagine."),
    "easter": ("🐣", "PASQUA", "Gregoriana e ortodossa."),
    "xmas": ("🎄", "NATALE", "Latino, ortodosso, Avvento."),
    "it": ("🇮🇹", "ITALIA", "Feste civili e Pasqua."),
    "world": ("🌍", "MONDO", "Feste civili note. Scorri."),
    "season": ("☀️", "STAGIONI", "Equinozi e solstizi, ora di Roma."),
}
PAGE_SIZE = 5
_MONTHS_SHORT = ("gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic")


def _fmt_day(day: date) -> str:
    return f"{_WEEKDAYS[day.weekday()]} {day.day} {_MONTHS[day.month - 1]} {day.year}"


def _fmt_short(day: date) -> str:
    return f"{day.day} {_MONTHS_SHORT[day.month - 1]}"


def _ago(day: date, today: date) -> str:
    n = (day - today).days
    if n == 0:
        return "oggi"
    if n == 1:
        return "domani"
    if n == -1:
        return "ieri"
    if n > 0:
        return f"tra {n}g"
    return f"{-n}g fa"


def rows_for(view: str, year: int, today: date) -> list[dict[str, object]]:
    view = view if view in VIEWS else "next"
    year = clamp_year(year)
    if view == "next":
        if year == today.year:
            return upcoming(today, limit=15)
        return all_events(year)
    return {
        "easter": events_easter,
        "xmas": events_xmas,
        "it": events_italy,
        "world": events_world,
        "season": events_season,
    }[view](year)


def format_events_card(view: str, year: int, today: date, page: int = 0) -> tuple[str, int, int]:
    view = view if view in VIEWS else "next"
    year = clamp_year(year)
    emoji, title, blurb = VIEWS[view]
    rows = rows_for(view, year, today)
    head_year = "" if view == "next" and year == today.year else f" · {year}"
    if view == "season":
        lines = [
            f"{emoji} <b>STAGIONI{head_year}</b>",
            f"<i>{_html.escape(blurb)}</i>",
            "",
        ]
        for row in rows:
            day = row["date"]
            assert isinstance(day, date)
            note = str(row.get("note") or "")
            extra = f"\n{_html.escape(note)}" if note else ""
            lines.append(
                f"{row['emoji']} <b>{_html.escape(str(row['title']))}</b>\n"
                f"{_fmt_day(day)} · <i>{_ago(day, today)}</i>{extra}"
            )
        lines.extend(["", "<i>Astronomy Engine · Europe/Rome.</i>"])
        return "\n".join(lines), 0, 1
    pages = max(1, (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE) if rows else 1
    page = max(0, min(int(page), pages - 1))
    chunk = rows[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]
    lines = [
        f"{emoji} <b>{title}{head_year}</b>",
        f"<i>{_html.escape(blurb)}</i>",
        "",
    ]
    if not chunk:
        lines.append("Nessuna data in questo giro.")
    else:
        for row in chunk:
            day = row["date"]
            assert isinstance(day, date)
            lines.append(
                f"{row['emoji']} <b>{_html.escape(str(row['title']))}</b> · "
                f"{_fmt_short(day)} · <i>{_ago(day, today)}</i>"
            )
    if pages > 1:
        lines.append(f"\n<i>Pagina {page + 1}/{pages}</i>")
    return "\n".join(lines), page, pages
