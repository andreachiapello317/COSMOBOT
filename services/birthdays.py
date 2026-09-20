"""Compleanni nel calendario civile. File locale, avviso il giorno stesso."""

from __future__ import annotations

import asyncio
import calendar
import html as _html
import json
import re
import secrets
from datetime import date
from pathlib import Path
from typing import Any

BIRTHDAY_PATH = Path("data/birthdays.json")
MAX_BIRTHDAYS = 20
_lock = asyncio.Lock()

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
_MONTH_ALIASES = {name: idx + 1 for idx, name in enumerate(_MONTHS)}
_MONTH_ALIASES.update(
    {
        "gen": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "mag": 5,
        "giu": 6,
        "lug": 7,
        "ago": 8,
        "set": 9,
        "ott": 10,
        "nov": 11,
        "dic": 12,
    }
)


def _load() -> dict[str, Any]:
    if not BIRTHDAY_PATH.exists():
        return {}
    try:
        data = json.loads(BIRTHDAY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(data: dict[str, Any]) -> None:
    BIRTHDAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    BIRTHDAY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _bucket(data: dict[str, Any], user_id: int) -> dict[str, Any]:
    key = str(int(user_id))
    row = data.get(key)
    if not isinstance(row, dict):
        row = {"chat_id": 0, "items": [], "sent": {}}
        data[key] = row
    items = row.get("items")
    if not isinstance(items, list):
        row["items"] = []
    sent = row.get("sent")
    if not isinstance(sent, dict):
        row["sent"] = {}
    row.setdefault("chat_id", 0)
    return row


def _valid_md(month: int, day: int, year: int | None) -> bool:
    if month < 1 or month > 12 or day < 1:
        return False
    if year is not None and (year < 1900 or year > date.today().year):
        return False
    last = 29 if month == 2 else calendar.monthrange(2000 if year is None else year, month)[1]
    return day <= last


def occurs_on(today: date, month: int, day: int) -> bool:
    if month == 2 and day == 29 and not calendar.isleap(today.year):
        return today.month == 2 and today.day == 28
    return today.month == month and today.day == day


def _next_on(today: date, month: int, day: int) -> date:
    year = today.year
    use_day = day
    if month == 2 and day == 29 and not calendar.isleap(year):
        use_day = 28
    try:
        candidate = date(year, month, use_day)
    except ValueError:
        candidate = date(year, month, min(use_day, calendar.monthrange(year, month)[1]))
    if candidate < today:
        year += 1
        use_day = day
        if month == 2 and day == 29 and not calendar.isleap(year):
            use_day = 28
        candidate = date(year, month, use_day)
    return candidate


def age_on(today: date, year: int | None, month: int, day: int) -> int | None:
    if year is None:
        return None
    years = today.year - year
    if (today.month, today.day) < (month, 28 if month == 2 and day == 29 and not calendar.isleap(today.year) else day):
        years -= 1
    return years if years >= 0 else None


def parse_birthday_line(text: str) -> dict[str, Any] | None:
    raw = re.sub(r"\s+", " ", str(text or "").strip())
    if not raw:
        return None
    numeric = re.search(
        r"(?P<d>\d{1,2})[/\-.](?P<m>\d{1,2})(?:[/\-.](?P<y>\d{4}))?",
        raw,
    )
    named = re.search(
        r"(?P<d>\d{1,2})\s+(?P<mon>gennaio|febbraio|marzo|aprile|maggio|giugno|"
        r"luglio|agosto|settembre|ottobre|novembre|dicembre|gen|feb|mar|apr|mag|"
        r"giu|lug|ago|set|ott|nov|dic)(?:\s+(?P<y>\d{4}))?",
        raw,
        flags=re.IGNORECASE,
    )
    hit = numeric or named
    if hit is None:
        return None
    day = int(hit.group("d"))
    if numeric:
        month = int(hit.group("m"))
        year_raw = hit.group("y")
    else:
        month = _MONTH_ALIASES[hit.group("mon").lower()]
        year_raw = hit.group("y")
    year = int(year_raw) if year_raw else None
    if not _valid_md(month, day, year):
        return None
    name = (raw[: hit.start()] + " " + raw[hit.end() :]).strip(" ,.-")
    name = re.sub(r"\s+", " ", name)
    if len(name) < 2:
        return None
    return {"name": name[:40], "day": day, "month": month, "year": year}


def format_md(month: int, day: int, year: int | None = None) -> str:
    label = f"{day} {_MONTHS[month - 1]}"
    if year:
        label = f"{label} {year}"
    return label


def format_birthdays_card(
    items: list[dict[str, Any]],
    today: date,
    *,
    prompt: str = "",
    error: str = "",
) -> str:
    lines = [
        "🎂 <b>COMPLEANNI</b>",
        "<i>Dentro il calendario. Il giorno stesso ti mando un avviso, ora italiana.</i>",
        "",
    ]
    today_rows = [row for row in items if occurs_on(today, int(row["month"]), int(row["day"]))]
    if today_rows:
        bits = []
        for row in today_rows:
            age = age_on(today, row.get("year"), int(row["month"]), int(row["day"]))
            extra = f" — {age} anni" if age is not None else ""
            bits.append(f"{_html.escape(str(row['name']))}{extra}")
        lines.append("🎉 <b>Oggi:</b> " + ", ".join(bits))
        lines.append("")
    if not items:
        lines.append("Nessun compleanno ancora. Tocca Aggiungi e scrivi nome e data.")
    else:
        upcoming = sorted(items, key=lambda row: _next_on(today, int(row["month"]), int(row["day"])))
        for row in upcoming:
            nxt = _next_on(today, int(row["month"]), int(row["day"]))
            delta = (nxt - today).days
            when = "oggi" if delta == 0 else ("domani" if delta == 1 else f"tra {delta} giorni")
            year = row.get("year")
            age = age_on(nxt, year if isinstance(year, int) else None, int(row["month"]), int(row["day"]))
            age_bit = f" · {age} anni" if age is not None else ""
            lines.append(
                f"🎂 <b>{_html.escape(str(row['name']))}</b> — "
                f"{format_md(int(row['month']), int(row['day']), year if isinstance(year, int) else None)}"
                f" · <i>{when}</i>{age_bit}"
            )
    lines.extend(
        [
            "",
            "Scrivi <code>Anna 21/03</code> oppure <code>Luca 21/03/1994</code>.",
            "29 febbraio: negli anni non bisestili avviso il 28.",
        ]
    )
    if prompt:
        lines.extend(["", _html.escape(prompt)])
    if error:
        lines.extend(["", f"⚠️ {_html.escape(error)}"])
    lines.append("<i>Un avviso al giorno, per chat. Se il bot è spento, parte appena torna su.</i>")
    return "\n".join(lines)


def format_birthday_alert(items: list[dict[str, Any]], today: date) -> str:
    lines = ["🎂 <b>COMPLEANNO</b>", "Oggi, ora italiana.", ""]
    for row in items:
        age = age_on(today, row.get("year") if isinstance(row.get("year"), int) else None, int(row["month"]), int(row["day"]))
        age_bit = f" Compie <b>{age}</b> anni." if age is not None else ""
        lines.append(f"🎉 È il compleanno di <b>{_html.escape(str(row['name']))}</b>.{age_bit}")
    return "\n".join(lines)


def month_days(items: list[dict[str, Any]], year: int, month: int) -> set[int]:
    out: set[int] = set()
    for row in items:
        if int(row["month"]) != month:
            continue
        day = int(row["day"])
        if month == 2 and day == 29 and not calendar.isleap(year):
            day = 28
        last = calendar.monthrange(year, month)[1]
        if 1 <= day <= last:
            out.add(day)
    return out


async def list_birthdays(user_id: int) -> list[dict[str, Any]]:
    async with _lock:
        row = _bucket(_load(), user_id)
        return [item for item in row["items"] if isinstance(item, dict)]


async def touch_chat(user_id: int, chat_id: int) -> None:
    async with _lock:
        data = _load()
        row = _bucket(data, user_id)
        row["chat_id"] = int(chat_id)
        _save(data)


async def add_birthday(user_id: int, chat_id: int, parsed: dict[str, Any]) -> list[dict[str, Any]]:
    async with _lock:
        data = _load()
        row = _bucket(data, user_id)
        row["chat_id"] = int(chat_id)
        items = [item for item in row["items"] if isinstance(item, dict)]
        key = (
            str(parsed["name"]).casefold(),
            int(parsed["month"]),
            int(parsed["day"]),
        )
        items = [
            item
            for item in items
            if (str(item.get("name") or "").casefold(), int(item.get("month") or 0), int(item.get("day") or 0)) != key
        ]
        items.append(
            {
                "id": secrets.token_hex(2),
                "name": str(parsed["name"]),
                "day": int(parsed["day"]),
                "month": int(parsed["month"]),
                "year": parsed.get("year"),
            }
        )
        row["items"] = items[:MAX_BIRTHDAYS]
        _save(data)
        return list(row["items"])


async def remove_birthday(user_id: int, item_id: str) -> list[dict[str, Any]]:
    async with _lock:
        data = _load()
        row = _bucket(data, user_id)
        row["items"] = [item for item in row["items"] if not (isinstance(item, dict) and str(item.get("id")) == item_id)]
        _save(data)
        return [item for item in row["items"] if isinstance(item, dict)]


async def due_alerts(today: date) -> list[dict[str, Any]]:
    stamp = today.isoformat()
    out: list[dict[str, Any]] = []
    async with _lock:
        data = _load()
        for key, row in data.items():
            if not isinstance(row, dict):
                continue
            chat_id = int(row.get("chat_id") or 0)
            if chat_id <= 0:
                continue
            sent = row.get("sent") if isinstance(row.get("sent"), dict) else {}
            already = {str(x) for x in (sent.get(stamp) or [])}
            hits = [
                item
                for item in row.get("items") or []
                if isinstance(item, dict)
                and occurs_on(today, int(item.get("month") or 0), int(item.get("day") or 0))
                and str(item.get("id") or "") not in already
            ]
            if hits:
                out.append({"user_id": int(key), "chat_id": chat_id, "items": hits})
    return out


async def mark_sent(user_id: int, today: date, item_ids: list[str]) -> None:
    stamp = today.isoformat()
    async with _lock:
        data = _load()
        row = _bucket(data, user_id)
        sent = row["sent"] if isinstance(row.get("sent"), dict) else {}
        prev = [str(x) for x in (sent.get(stamp) or [])]
        for item_id in item_ids:
            if item_id and item_id not in prev:
                prev.append(item_id)
        sent[stamp] = prev
        # tieni solo gli ultimi 8 giorni
        keep = sorted(sent.keys())[-8:]
        row["sent"] = {key: sent[key] for key in keep}
        _save(data)
