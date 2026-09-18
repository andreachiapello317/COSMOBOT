"""NASA NeoWs: asteroidi vicini alla Terra."""

from __future__ import annotations

import logging
import os
from datetime import date, timedelta
from typing import Any

import httpx

logger = logging.getLogger("stellebot.neo")


def _nasa_key() -> str:
    return os.getenv("NASA_API_KEY", "DEMO_KEY").strip() or "DEMO_KEY"


async def near_earth_asteroids(client: httpx.AsyncClient, days: int = 3) -> list[dict[str, Any]]:
    start = date.today()
    end = start + timedelta(days=max(1, min(days, 7)))
    try:
        response = await client.get(
            "https://api.nasa.gov/neo/rest/v1/feed",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "api_key": _nasa_key(),
            },
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.info("NeoWs: %s", exc)
        return []
    objects = payload.get("near_earth_objects") if isinstance(payload, dict) else None
    if not isinstance(objects, dict):
        return []
    rows: list[dict[str, Any]] = []
    for day, items in objects.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            approach = (item.get("close_approach_data") or [{}])[0]
            diam = ((item.get("estimated_diameter") or {}).get("meters") or {})
            miss = (approach.get("miss_distance") or {})
            vel = (approach.get("relative_velocity") or {})
            rows.append(
                {
                    "name": item.get("name") or "NEO",
                    "day": day,
                    "hazardous": bool(item.get("is_potentially_hazardous_asteroid")),
                    "diam_min": diam.get("estimated_diameter_min"),
                    "diam_max": diam.get("estimated_diameter_max"),
                    "miss_km": miss.get("kilometers"),
                    "velocity": vel.get("kilometers_per_hour"),
                }
            )
    rows.sort(key=lambda row: float(row.get("miss_km") or 1e18))
    return rows[:8]
