"""Attività solare e distanze lunari da Skytime. Solo numeri live."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger("stellebot.sw")


async def kp_index(client: httpx.AsyncClient) -> dict[str, Any] | None:
    try:
        response = await client.get("https://skytime.live/api/v1/space-weather/kp")
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.info("Kp: %s", exc)
        return None
    data = payload.get("data") if isinstance(payload, dict) else None
    history = data.get("history") if isinstance(data, dict) else data
    if not isinstance(history, list) or not history:
        return None
    last = history[-1] if isinstance(history[-1], dict) else None
    return last


async def latest_flare(client: httpx.AsyncClient) -> dict[str, Any] | None:
    try:
        response = await client.get("https://skytime.live/api/v1/space-weather/xray")
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.info("X-ray: %s", exc)
        return None
    data = payload.get("data") if isinstance(payload, dict) else None
    flares = data.get("flares") if isinstance(data, dict) else None
    if not isinstance(flares, list) or not flares:
        return None
    return flares[0] if isinstance(flares[0], dict) else None


async def moon_distance_events(client: httpx.AsyncClient, year: int) -> list[dict[str, Any]]:
    try:
        response = await client.get(
            "https://skytime.live/api/v1/moon-distance",
            params={"year": year},
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.info("Moon distance: %s", exc)
        return []
    data = payload.get("data") if isinstance(payload, dict) else None
    events = data.get("events") if isinstance(data, dict) else None
    if not isinstance(events, list):
        return []
    return [row for row in events if isinstance(row, dict)]


def next_distance_event(rows: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    upcoming: list[tuple[datetime, dict[str, Any]]] = []
    for row in rows:
        raw = str(row.get("date") or "")
        if not raw:
            continue
        try:
            when = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        if when >= now:
            upcoming.append((when, row))
    upcoming.sort(key=lambda item: item[0])
    return upcoming[0][1] if upcoming else None
