"""NASA Exoplanet Archive (TAP, tabella ps)."""

from __future__ import annotations

import logging
import random
from typing import Any

import httpx

logger = logging.getLogger("stellebot.exo")

TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


async def _tap(client: httpx.AsyncClient, query: str) -> list[dict[str, Any]]:
    response = await client.get(TAP, params={"query": query, "format": "json"})
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError("TAP non-lista")
    return [row for row in data if isinstance(row, dict)]


async def random_exoplanet(client: httpx.AsyncClient) -> dict[str, Any] | None:
    try:
        rows = await _tap(
            client,
            "select top 40 pl_name,hostname,sy_dist,pl_rade,pl_eqt,discoverymethod,disc_year "
            "from ps where default_flag=1 and sy_dist is not null order by sy_dist",
        )
    except Exception as exc:  # noqa: BLE001
        logger.info("Exoplanet random: %s", exc)
        return None
    return random.choice(rows) if rows else None


COLS = "pl_name,hostname,sy_dist,pl_rade,pl_eqt,discoverymethod,disc_year"


async def exoplanets_by_filter(client: httpx.AsyncClient, kind: str, limit: int = 8) -> list[dict[str, Any]]:
    """Filtri TAP su numeri dell'archivio. I nomi dei filtri sono etichette, non prove geologiche."""
    queries = {
        "earth": (
            f"select top 20 {COLS} from ps where default_flag=1 and pl_eqt>200 and pl_eqt<280 "
            "and pl_rade>0.8 and pl_rade<1.5 and sy_dist is not null order by sy_dist"
        ),
        "hell": (
            f"select top 20 {COLS} from ps where default_flag=1 and pl_eqt>1500 "
            "and sy_dist is not null order by pl_eqt desc"
        ),
        "extreme": (
            f"select top 20 {COLS} from ps where default_flag=1 and (pl_eqt>2000 or pl_rade>12) "
            "and sy_dist is not null order by pl_eqt desc"
        ),
        "ocean": (
            f"select top 20 {COLS} from ps where default_flag=1 and pl_eqt>180 and pl_eqt<320 "
            "and pl_rade>1.8 and pl_rade<3.5 and sy_dist is not null order by sy_dist"
        ),
        "recent": (
            f"select top 20 {COLS} from ps where default_flag=1 and disc_year is not null "
            "and sy_dist is not null order by disc_year desc"
        ),
        "hz": (
            f"select top 20 {COLS} from ps where default_flag=1 and pl_eqt>180 and pl_eqt<310 "
            "and pl_rade<1.8 and sy_dist is not null order by sy_dist"
        ),
    }
    query = queries.get(kind)
    if not query:
        return []
    try:
        rows = await _tap(client, query)
        return rows[:limit]
    except Exception as exc:  # noqa: BLE001
        logger.info("Exoplanet filter %s: %s", kind, exc)
        return []


async def habitable_candidates(client: httpx.AsyncClient, limit: int = 8) -> list[dict[str, Any]]:
    """Filtro su temperatura di equilibrio e raggio: modello, non prova di vita."""
    try:
        return await exoplanets_by_filter(client, "hz", limit)
    except Exception as exc:  # noqa: BLE001
        logger.info("Exoplanet HZ: %s", exc)
        return []
