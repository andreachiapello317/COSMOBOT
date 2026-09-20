"""Eventi di calendario per cartelle: regioni, religiose, mondo. Niente cambio anno."""

from __future__ import annotations

import calendar
import html as _html
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable
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
_MONTHS_SHORT = ("gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic")
PAGE_SIZE = 5
YEAR_MIN = 1901
YEAR_MAX = 2099

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

When = Callable[[int], date | None]


def clamp_year(year: int) -> int:
    return max(YEAR_MIN, min(YEAR_MAX, int(year)))


def easter_western(year: int) -> date:
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


def last_weekday(year: int, month: int, weekday: int) -> date:
    last = date(year, month, calendar.monthrange(year, month)[1])
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def advent_sunday(year: int) -> date:
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


def _fixed(month: int, day: int) -> When:
    return lambda year: date(year, month, day)


def _from_easter(delta: int) -> When:
    return lambda year: easter_western(year) + timedelta(days=delta)


def _cny(year: int) -> date | None:
    pair = _CNY.get(year)
    return date(year, pair[0], pair[1]) if pair else None


def _nowruz(year: int) -> date:
    return season_marks(year)[0][0].date()


def _build(year: int, specs: tuple[tuple[str, str, When], ...], kind: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for emoji, title, when in specs:
        day = when(year)
        if day is None:
            continue
        rows.append(_event(day, emoji, title, kind=kind))
    return sorted(rows, key=lambda row: row["date"])  # type: ignore[arg-type, return-value]


REGIONS: dict[str, dict[str, Any]] = {
    "it": {
        "emoji": "🇮🇹",
        "title": "ITALIA",
        "blurb": "Feste civili italiane, da oggi.",
        "specs": (
            ("🎆", "Capodanno", _fixed(1, 1)),
            ("⭐", "Epifania", _fixed(1, 6)),
            ("👔", "Festa del papà", _fixed(3, 19)),
            ("🐣", "Pasqua", _from_easter(0)),
            ("🧺", "Pasquetta", _from_easter(1)),
            ("🇮🇹", "Liberazione", _fixed(4, 25)),
            ("💐", "Festa della mamma", lambda y: nth_weekday(y, 5, 6, 2)),
            ("🛠️", "Festa del Lavoro", _fixed(5, 1)),
            ("🇮🇹", "Festa della Repubblica", _fixed(6, 2)),
            ("☀️", "Ferragosto", _fixed(8, 15)),
            ("🕯️", "Ognissanti", _fixed(11, 1)),
            ("💠", "Immacolata", _fixed(12, 8)),
            ("🎄", "Natale", _fixed(12, 25)),
            ("🎁", "Santo Stefano", _fixed(12, 26)),
        ),
    },
    "fr": {
        "emoji": "🇫🇷",
        "title": "FRANCIA",
        "blurb": "Feste civili francesi, da oggi.",
        "specs": (
            ("🎆", "Capodanno", _fixed(1, 1)),
            ("🧺", "Lundi de Pâques", _from_easter(1)),
            ("🛠️", "Fête du Travail", _fixed(5, 1)),
            ("🇫🇷", "Victoire 1945", _fixed(5, 8)),
            ("☁️", "Ascension", _from_easter(39)),
            ("🔥", "Lundi de Pentecôte", _from_easter(50)),
            ("🇫🇷", "Presa della Bastiglia", _fixed(7, 14)),
            ("☀️", "Assomption", _fixed(8, 15)),
            ("🕯️", "Toussaint", _fixed(11, 1)),
            ("🪖", "Armistizio 1918", _fixed(11, 11)),
            ("🎄", "Noël", _fixed(12, 25)),
        ),
    },
    "de": {
        "emoji": "🇩🇪",
        "title": "GERMANIA",
        "blurb": "Feste federali tedesche, da oggi.",
        "specs": (
            ("🎆", "Neujahr", _fixed(1, 1)),
            ("✝️", "Karfreitag", _from_easter(-2)),
            ("🧺", "Ostermontag", _from_easter(1)),
            ("🛠️", "Tag der Arbeit", _fixed(5, 1)),
            ("☁️", "Christi Himmelfahrt", _from_easter(39)),
            ("🔥", "Pfingstmontag", _from_easter(50)),
            ("🇩🇪", "Tag der Deutschen Einheit", _fixed(10, 3)),
            ("🎄", "Erster Weihnachtstag", _fixed(12, 25)),
            ("🎁", "Zweiter Weihnachtstag", _fixed(12, 26)),
        ),
    },
    "es": {
        "emoji": "🇪🇸",
        "title": "SPAGNA",
        "blurb": "Feste nazionali spagnole, da oggi.",
        "specs": (
            ("🎆", "Año Nuevo", _fixed(1, 1)),
            ("⭐", "Reyes", _fixed(1, 6)),
            ("✝️", "Viernes Santo", _from_easter(-2)),
            ("🛠️", "Fiesta del Trabajo", _fixed(5, 1)),
            ("☀️", "Asunción", _fixed(8, 15)),
            ("🇪🇸", "Fiesta Nacional", _fixed(10, 12)),
            ("🕯️", "Todos los Santos", _fixed(11, 1)),
            ("📜", "Día de la Constitución", _fixed(12, 6)),
            ("💠", "Inmaculada", _fixed(12, 8)),
            ("🎄", "Navidad", _fixed(12, 25)),
        ),
    },
    "uk": {
        "emoji": "🇬🇧",
        "title": "REGNO UNITO",
        "blurb": "Bank holiday inglesi, da oggi.",
        "specs": (
            ("🎆", "New Year's Day", _fixed(1, 1)),
            ("✝️", "Good Friday", _from_easter(-2)),
            ("🧺", "Easter Monday", _from_easter(1)),
            ("🌷", "Early May bank holiday", lambda y: nth_weekday(y, 5, 0, 1)),
            ("🌳", "Spring bank holiday", lambda y: last_weekday(y, 5, 0)),
            ("☀️", "Summer bank holiday", lambda y: last_weekday(y, 8, 0)),
            ("🎄", "Christmas Day", _fixed(12, 25)),
            ("🎁", "Boxing Day", _fixed(12, 26)),
        ),
    },
    "us": {
        "emoji": "🇺🇸",
        "title": "STATI UNITI",
        "blurb": "Feste federali USA, da oggi.",
        "specs": (
            ("🎆", "New Year's Day", _fixed(1, 1)),
            ("✊", "Martin Luther King Jr. Day", lambda y: nth_weekday(y, 1, 0, 3)),
            ("🇺🇸", "Presidents' Day", lambda y: nth_weekday(y, 2, 0, 3)),
            ("🌺", "Memorial Day", lambda y: last_weekday(y, 5, 0)),
            ("🇺🇸", "Independence Day", _fixed(7, 4)),
            ("🛠️", "Labor Day", lambda y: nth_weekday(y, 9, 0, 1)),
            ("🦃", "Thanksgiving", lambda y: nth_weekday(y, 11, 3, 4)),
            ("🎄", "Christmas Day", _fixed(12, 25)),
        ),
    },
}

RELIGIOUS_SPECS: tuple[tuple[str, str, When], ...] = (
    ("⭐", "Epifania", _fixed(1, 6)),
    ("🎄", "Natale ortodosso", _fixed(1, 7)),
    ("💧", "Teofania ortodossa", _fixed(1, 19)),
    ("🎭", "Martedì grasso", _from_easter(-47)),
    ("✝️", "Mercoledì delle Ceneri", _from_easter(-46)),
    ("🌿", "Domenica delle Palme", _from_easter(-7)),
    ("🍷", "Giovedì santo", _from_easter(-3)),
    ("✝️", "Venerdì santo", _from_easter(-2)),
    ("🐣", "Pasqua occidentale", _from_easter(0)),
    ("🧺", "Pasquetta", _from_easter(1)),
    ("☁️", "Ascensione", _from_easter(39)),
    ("🔥", "Pentecoste", _from_easter(49)),
    ("🍞", "Corpus Domini", _from_easter(60)),
    ("☦️", "Pasqua ortodossa", lambda y: easter_orthodox(y)),
    ("💠", "Immacolata Concezione", _fixed(12, 8)),
    ("🕯️", "Prima domenica di Avvento", advent_sunday),
    ("🎁", "Vigilia di Natale", _fixed(12, 24)),
    ("🎄", "Natale", _fixed(12, 25)),
    ("🎁", "Santo Stefano", _fixed(12, 26)),
)

WORLD_SUB: dict[str, dict[str, Any]] = {
    "love": {
        "emoji": "💌",
        "title": "AMORI",
        "blurb": "Date civili legate all'amore.",
        "specs": (
            ("💌", "San Valentino", _fixed(2, 14)),
            ("🤍", "White Day", _fixed(3, 14)),
            ("💜", "Giornata della donna", _fixed(3, 8)),
            ("💐", "Festa della mamma (IT)", lambda y: nth_weekday(y, 5, 6, 2)),
            ("💑", "Singles' Day", _fixed(11, 11)),
        ),
    },
    "fun": {
        "emoji": "😄",
        "title": "BUFFE",
        "blurb": "Date curiose, vere, non inventate.",
        "specs": (
            ("🥧", "Pi Day", _fixed(3, 14)),
            ("🃏", "Pesce d'aprile", _fixed(4, 1)),
            ("⚔️", "Star Wars Day", _fixed(5, 4)),
            ("🌌", "Towel Day", _fixed(5, 25)),
            ("🎃", "Halloween", _fixed(10, 31)),
        ),
    },
    "civil": {
        "emoji": "🕊️",
        "title": "CIVILI",
        "blurb": "Giornate internazionali e civili.",
        "specs": (
            ("🎆", "Capodanno civile", _fixed(1, 1)),
            ("🌍", "Giornata della Terra", _fixed(4, 22)),
            ("🛠️", "Primo maggio", _fixed(5, 1)),
            ("🕊️", "Giornata delle Nazioni Unite", _fixed(10, 24)),
            ("🥂", "San Silvestro", _fixed(12, 31)),
        ),
    },
    "culture": {
        "emoji": "🧧",
        "title": "CULTURE",
        "blurb": "Feste culturali con data nota.",
        "specs": (
            ("🧧", "Capodanno cinese", _cny),
            ("🌱", "Nowruz", _nowruz),
            ("💀", "Día de Muertos", _fixed(11, 1)),
            ("🦃", "Thanksgiving USA", lambda y: nth_weekday(y, 11, 3, 4)),
            ("🎄", "Natale ortodosso", _fixed(1, 7)),
        ),
    },
}

MENUS = {
    "hub": ("📅", "EVENTI", "Senza cambiare anno. Una cartella alla volta."),
    "reg": ("🗺️", "REGIONI", "Feste civili per paese. Si può aggiungere una nazione."),
    "world": ("🌍", "MONDO", "Sottosezioni. Amori, buffe, civili, culture."),
}


def events_region(key: str, year: int) -> list[dict[str, object]]:
    meta = REGIONS.get(key)
    if not meta:
        return []
    return _build(year, meta["specs"], f"r:{key}")


def events_religious(year: int) -> list[dict[str, object]]:
    return _build(year, RELIGIOUS_SPECS, "rel")


def events_world_sub(key: str, year: int) -> list[dict[str, object]]:
    meta = WORLD_SUB.get(key)
    if not meta:
        return []
    return _build(year, meta["specs"], f"w:{key}")


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


def _upcoming(today: date, builder: Callable[[int], list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for year in (today.year, today.year + 1):
        if YEAR_MIN <= year <= YEAR_MAX:
            rows.extend(builder(year))
    future = [row for row in rows if row["date"] >= today]  # type: ignore[operator]
    seen: set[str] = set()
    unique: list[dict[str, object]] = []
    for row in future:
        title = str(row.get("title") or "")
        if title in seen:
            continue
        seen.add(title)
        unique.append(row)
    return unique


def all_catalog(year: int) -> list[dict[str, object]]:
    seen: set[tuple[date, str]] = set()
    out: list[dict[str, object]] = []
    groups = [events_religious(year), events_season(year)]
    groups.extend(events_region(key, year) for key in REGIONS)
    groups.extend(events_world_sub(key, year) for key in WORLD_SUB)
    for group in groups:
        for row in group:
            key = (row["date"], str(row["title"]))  # type: ignore[index]
            if key in seen:
                continue
            seen.add(key)
            out.append(row)
    return sorted(out, key=lambda row: row["date"])  # type: ignore[arg-type, return-value]


def upcoming(today: date, *, limit: int = 12) -> list[dict[str, object]]:
    return _upcoming(today, all_catalog)[:limit]


def rows_for(view: str, today: date) -> list[dict[str, object]]:
    if view == "next":
        return upcoming(today, limit=15)
    if view == "season":
        return events_season(today.year)
    if view == "rel":
        return _upcoming(today, events_religious)
    if view.startswith("r:") and view[2:] in REGIONS:
        key = view[2:]
        return _upcoming(today, lambda year: events_region(key, year))
    if view.startswith("w:") and view[2:] in WORLD_SUB:
        key = view[2:]
        return _upcoming(today, lambda year: events_world_sub(key, year))
    return []


def _meta(view: str) -> tuple[str, str, str]:
    if view in MENUS:
        return MENUS[view]
    if view == "next":
        return "📅", "PROSSIMI", "I più vicini, da oggi. Scorri solo se sono tanti."
    if view == "season":
        return "☀️", "STAGIONI", "Equinozi e solstizi, ora di Roma."
    if view == "rel":
        return "✝️", "RELIGIOSE", "Cristiane e ortodosse, da oggi."
    if view.startswith("r:") and view[2:] in REGIONS:
        meta = REGIONS[view[2:]]
        return meta["emoji"], meta["title"], meta["blurb"]
    if view.startswith("w:") and view[2:] in WORLD_SUB:
        meta = WORLD_SUB[view[2:]]
        return meta["emoji"], meta["title"], meta["blurb"]
    return MENUS["hub"]


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


def format_events_card(view: str, year: int, today: date, page: int = 0) -> tuple[str, int, int]:
    _ = year
    if view in {"easter", "xmas"}:
        view = "rel"
    if view == "it":
        view = "r:it"
    if view not in {"hub", "reg", "world", "next", "season", "rel"} and not view.startswith(("r:", "w:")):
        view = "hub"
    emoji, title, blurb = _meta(view)
    if view in {"hub", "reg", "world"}:
        extra = ""
        if view == "hub":
            extra = (
                "🗺️ <b>REGIONI</b> — Italia, Francia, Germania…\n"
                "✝️ <b>RELIGIOSE</b> — Pasqua, Natale, Avvento\n"
                "🌍 <b>MONDO</b> — amori, buffe, civili, culture\n"
                "☀️ <b>STAGIONI</b> — equinozi e solstizi\n"
                "📅 <b>PROSSIMI</b> — i più vicini da oggi"
            )
        elif view == "reg":
            extra = "\n".join(f"{row['emoji']} <b>{row['title']}</b>" for row in REGIONS.values())
        else:
            extra = "\n".join(f"{row['emoji']} <b>{row['title']}</b> — {row['blurb']}" for row in WORLD_SUB.values())
        text = f"{emoji} <b>{title}</b>\n<i>{_html.escape(blurb)}</i>\n\n{extra}"
        return text, 0, 1
    rows = rows_for(view, today)
    if view == "season":
        lines = [f"{emoji} <b>{title}</b>", f"<i>{_html.escape(blurb)}</i>", ""]
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
    lines = [f"{emoji} <b>{title}</b>", f"<i>{_html.escape(blurb)}</i>", ""]
    if not chunk:
        lines.append("Nessuna data da oggi in poi, in questa cartella.")
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


def parent_view(view: str) -> str:
    if view.startswith("r:"):
        return "reg"
    if view.startswith("w:"):
        return "world"
    return "hub"
