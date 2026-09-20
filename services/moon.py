"""Fasi lunari calcolate. Niente significati, niente enciclopedia."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import astronomy

QUARTER_IT = {
    0: ("Luna nuova", "🌑"),
    1: ("Primo quarto", "🌓"),
    2: ("Luna piena", "🌕"),
    3: ("Ultimo quarto", "🌗"),
}

# Quarti stretti (±15°). Il resto è crescente / gibbosa / calante.
_PHASE_BANDS = (
    (15.0, "Luna nuova", "🌑"),
    (75.0, "Luna crescente", "🌒"),
    (105.0, "Primo quarto", "🌓"),
    (165.0, "Gibbosa crescente", "🌔"),
    (195.0, "Luna piena", "🌕"),
    (255.0, "Gibbosa calante", "🌖"),
    (285.0, "Ultimo quarto", "🌗"),
    (345.0, "Luna calante", "🌘"),
)


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


def phase_from_angle(angle_deg: float) -> tuple[str, str]:
    deg = float(angle_deg) % 360.0
    for limit, name, emoji in _PHASE_BANDS:
        if deg < limit:
            return name, emoji
    return "Luna nuova", "🌑"


def moon_now(when: datetime) -> dict[str, Any]:
    moment = _astro_time(when)
    angle = float(astronomy.MoonPhase(moment))
    name, emoji = phase_from_angle(angle)
    illum = astronomy.Illumination(astronomy.Body.Moon, moment)
    fraction = getattr(illum, "phase_fraction", None)
    return {
        "name": name,
        "emoji": emoji,
        "angle": angle,
        "illum": float(fraction) * 100.0 if isinstance(fraction, (int, float)) else None,
    }


def next_quarters(when: datetime, count: int = 4) -> list[dict[str, Any]]:
    moment = _astro_time(when)
    found = astronomy.SearchMoonQuarter(moment)
    rows: list[dict[str, Any]] = []
    for _ in range(max(1, count)):
        label, emoji = QUARTER_IT.get(int(found.quarter), ("Quarto", "🌙"))
        stamp = found.time.Utc()
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        rows.append({"name": label, "emoji": emoji, "when": stamp})
        found = astronomy.NextMoonQuarter(found)
    return rows
