"""NASA Exoplanet Archive (TAP, tabella ps). Filtri numerici, non geologia."""

from __future__ import annotations

import logging
import random
from typing import Any

import httpx

logger = logging.getLogger("stellebot.exo")

TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

COLS = (
    "pl_name,hostname,sy_dist,pl_rade,pl_bmasse,pl_eqt,pl_orbper,pl_orbeccen,"
    "pl_orbsmax,sy_snum,sy_pnum,st_teff,discoverymethod,disc_year,ra,dec"
)


def sql_str(value: str) -> str:
    return value.replace("'", "''")


async def _tap(client: httpx.AsyncClient, query: str) -> list[dict[str, Any]]:
    response = await client.get(TAP, params={"query": query, "format": "json"})
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError("TAP non-lista")
    return [row for row in data if isinstance(row, dict)]


def classify_radius(rade: Any) -> str:
    try:
        value = float(rade)
    except (TypeError, ValueError):
        return "tipo sconosciuto (manca il raggio in archivio)"
    if value < 1.8:
        return "terrestre (modello: raggio < 1.8 R⊕)"
    if value < 4:
        return "mondo volatile / mini-Nettuno (modello raggio)"
    if value < 8:
        return "Nettuno (modello raggio)"
    return "gigante (modello raggio)"


FILTERS: dict[str, tuple[str, str, str]] = {
    # kind: (where-clause, order, label-it)
    "earth": (
        "pl_eqt>200 and pl_eqt<280 and pl_rade>0.8 and pl_rade<1.5 and sy_dist is not null",
        "sy_dist",
        "simili alla Terra (raggio/Teq)",
    ),
    "hell": (
        "pl_eqt>1500 and sy_dist is not null",
        "pl_eqt desc",
        "infernali (Teq alta)",
    ),
    "extreme": (
        "(pl_eqt>2000 or pl_rade>12) and sy_dist is not null",
        "pl_eqt desc",
        "estremi (Teq o raggio)",
    ),
    "ocean": (
        "pl_eqt>180 and pl_eqt<320 and pl_rade>1.8 and pl_rade<3.5 and sy_dist is not null",
        "sy_dist",
        "oceanici (modello raggio/Teq, non oceano confermato)",
    ),
    "ice": (
        "pl_eqt<200 and pl_eqt is not null and sy_dist is not null",
        "pl_eqt",
        "ghiacciati (Teq bassa)",
    ),
    "hotjup": (
        "pl_rade>8 and pl_orbper<10 and sy_dist is not null",
        "pl_orbper",
        "atmosfere estreme (gigante + anno breve: stima da archivio, non spettro)",
    ),
    "ecc": (
        "pl_orbeccen>0.5 and sy_dist is not null",
        "pl_orbeccen desc",
        "orbite eccentriche",
    ),
    "short": (
        "pl_orbper<1 and pl_orbper is not null and sy_dist is not null",
        "pl_orbper",
        "anno più corto di un giorno terrestre",
    ),
    "binary": (
        "sy_snum>=2 and sy_dist is not null",
        "sy_dist",
        "più di una stella nel sistema",
    ),
    "weird": (
        "((pl_orbeccen>0.4 and pl_eqt>800) or pl_rade>15) and sy_dist is not null",
        "pl_eqt desc",
        "condizioni assurde (eccentricità+Teq o raggio enorme)",
    ),
    "recent": (
        "disc_year is not null and sy_dist is not null",
        "disc_year desc",
        "scoperti di recente",
    ),
    "hz": (
        "pl_eqt>180 and pl_eqt<310 and pl_rade<1.8 and sy_dist is not null",
        "sy_dist",
        "zona abitabile (modello Teq/raggio)",
    ),
    "rogue": (
        "(hostname is null or sy_snum=0)",
        "pl_name",
        "senza stella (righe senza stella ospite)",
    ),
}


async def random_exoplanet(client: httpx.AsyncClient) -> dict[str, Any] | None:
    try:
        rows = await _tap(
            client,
            f"select top 50 {COLS} from ps where default_flag=1 and sy_dist is not null "
            "order by sy_dist",
        )
    except Exception as exc:  # noqa: BLE001
        logger.info("Exoplanet random: %s", exc)
        return None
    return random.choice(rows) if rows else None


async def exoplanets_by_filter(client: httpx.AsyncClient, kind: str, limit: int = 8) -> list[dict[str, Any]]:
    """Filtri TAP su numeri dell'archivio. I nomi dei filtri sono etichette, non prove geologiche."""
    spec = FILTERS.get(kind)
    if not spec:
        return []
    where, order, _label = spec
    query = (
        f"select top 20 {COLS} from ps where default_flag=1 and {where} order by {order}"
    )
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


async def planet_of_the_day(client: httpx.AsyncClient, day_index: int) -> dict[str, Any] | None:
    try:
        rows = await _tap(
            client,
            f"select top 80 {COLS} from ps where default_flag=1 and sy_dist is not null "
            "order by pl_name",
        )
    except Exception as exc:  # noqa: BLE001
        logger.info("Planet of day: %s", exc)
        return None
    if not rows:
        return None
    return rows[day_index % len(rows)]


async def exoplanet_by_name(client: httpx.AsyncClient, name: str) -> dict[str, Any] | None:
    try:
        rows = await _tap(
            client,
            f"select top 1 {COLS} from ps where default_flag=1 and pl_name='{sql_str(name)}'",
        )
    except Exception as exc:  # noqa: BLE001
        logger.info("Exoplanet by name: %s", exc)
        return None
    return rows[0] if rows else None
