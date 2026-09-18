"""Prossime eclissi da Skytime (from_year / to_year)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger("stellebot.eclipses")

KIND_IT = {
    "total": "totale",
    "annular": "anulare",
    "partial": "parziale",
    "penumbral": "penombrale",
    "hybrid": "ibrida",
}


async def fetch_eclipses(client: httpx.AsyncClient, from_year: int, to_year: int) -> dict[str, list[dict[str, Any]]]:
    try:
        response = await client.get(
            "https://skytime.live/api/v1/eclipses",
            params={"from_year": from_year, "to_year": to_year},
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.info("Eclissi Skytime: %s", exc)
        return {"solar": [], "lunar": []}
    block = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(block, dict):
        return {"solar": [], "lunar": []}
    solar = [row for row in (block.get("solar") or []) if isinstance(row, dict)]
    lunar = [row for row in (block.get("lunar") or []) if isinstance(row, dict)]
    return {"solar": solar, "lunar": lunar}


def parse_peak(row: dict[str, Any]) -> datetime | None:
    raw = str(row.get("peakTime") or row.get("date") or "")
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        dt = datetime.fromisoformat(raw)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def next_of(rows: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    upcoming: list[tuple[datetime, dict[str, Any]]] = []
    for row in rows:
        when = parse_peak(row)
        if when is None:
            continue
        if when >= now:
            upcoming.append((when, row))
    upcoming.sort(key=lambda item: item[0])
    return upcoming[0][1] if upcoming else None


def kind_it(raw: str | None) -> str:
    return KIND_IT.get(str(raw or "").lower(), str(raw or "—"))
