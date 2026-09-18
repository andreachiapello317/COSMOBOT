"""Sistemi stellari dall'archivio NASA (TAP ps). Nessun albero inventato."""

from __future__ import annotations

import logging
import random
from typing import Any

import httpx

from services.exoplanets import COLS, _tap, classify_radius, sql_str

logger = logging.getLogger("stellebot.sys")

FAMOUS_HOSTS: dict[str, str] = {
    "trappist": "TRAPPIST-1",
    "toi700": "TOI-700",
    "k90": "Kepler-90",
    "proxima": "Proxima Centauri",
    "hr8799": "HR 8799",
    "k186": "Kepler-186",
    "k18": "K2-18",
    "lhs1140": "LHS 1140",
}


async def planets_of_host(client: httpx.AsyncClient, host: str) -> list[dict[str, Any]]:
    try:
        rows = await _tap(
            client,
            f"select top 20 {COLS} from ps where default_flag=1 "
            f"and hostname='{sql_str(host)}' order by pl_orbsmax",
        )
    except Exception as exc:  # noqa: BLE001
        logger.info("System %s: %s", host, exc)
        return []
    if rows:
        return rows
    try:
        return await _tap(
            client,
            f"select top 20 {COLS} from ps where default_flag=1 "
            f"and hostname='{sql_str(host)}' order by pl_name",
        )
    except Exception as exc:  # noqa: BLE001
        logger.info("System fallback %s: %s", host, exc)
        return []


async def system_card(client: httpx.AsyncClient, host: str) -> dict[str, Any] | None:
    planets = await planets_of_host(client, host)
    if not planets:
        return None
    first = planets[0]
    return {
        "host": host,
        "planets": planets,
        "sy_snum": first.get("sy_snum"),
        "sy_pnum": first.get("sy_pnum"),
        "sy_dist": first.get("sy_dist"),
        "st_teff": first.get("st_teff"),
    }


def _unique_hosts(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        host = str(row.get("hostname") or "").strip()
        if not host or host in seen:
            continue
        seen.add(host)
        out.append(row)
        if len(out) >= limit:
            break
    return out


async def systems_by_kind(client: httpx.AsyncClient, kind: str, limit: int = 8) -> list[dict[str, Any]]:
    queries = {
        "bin": (
            "select top 40 hostname,sy_snum,sy_pnum,sy_dist,st_teff from ps "
            "where default_flag=1 and sy_snum=2 and sy_dist is not null order by sy_dist"
        ),
        "multi": (
            "select top 40 hostname,sy_snum,sy_pnum,sy_dist,st_teff from ps "
            "where default_flag=1 and sy_snum>=3 and sy_dist is not null order by sy_dist"
        ),
        "packed": (
            "select top 40 hostname,sy_snum,sy_pnum,sy_dist,st_teff from ps "
            "where default_flag=1 and sy_pnum>=6 and sy_dist is not null order by sy_pnum desc"
        ),
        "hzsys": (
            "select top 40 hostname,sy_snum,sy_pnum,sy_dist,st_teff,pl_name,pl_eqt,pl_rade from ps "
            "where default_flag=1 and pl_eqt>180 and pl_eqt<310 and pl_rade<1.8 "
            "and sy_dist is not null order by sy_dist"
        ),
        "near": (
            "select top 40 hostname,sy_snum,sy_pnum,sy_dist,st_teff from ps "
            "where default_flag=1 and sy_pnum>=2 and sy_dist is not null order by sy_dist"
        ),
    }
    query = queries.get(kind)
    if not query:
        return []
    try:
        rows = await _tap(client, query)
    except Exception as exc:  # noqa: BLE001
        logger.info("Systems %s: %s", kind, exc)
        return []
    return _unique_hosts(rows, limit)


async def random_system(client: httpx.AsyncClient) -> dict[str, Any] | None:
    rows = await systems_by_kind(client, "near", limit=20)
    if not rows:
        return None
    pick = random.choice(rows)
    host = str(pick.get("hostname") or "")
    return await system_card(client, host) if host else None


def planet_glyph(row: dict[str, Any]) -> str:
    try:
        rade = float(row["pl_rade"]) if row.get("pl_rade") is not None else None
        eqt = float(row["pl_eqt"]) if row.get("pl_eqt") is not None else None
    except (TypeError, ValueError):
        return "🪐"
    if rade is not None and rade < 1.8 and eqt is not None and 180 <= eqt <= 310:
        return "🌍"
    if eqt is not None and eqt > 1200:
        return "🔥"
    if eqt is not None and eqt < 180:
        return "🧊"
    if rade is not None and rade > 8:
        return "🪐"
    return "🪐"


def format_system_tree(card: dict[str, Any]) -> str:
    host = str(card.get("host") or "Sistema")
    planets = card.get("planets") if isinstance(card.get("planets"), list) else []
    dist = card.get("sy_dist")
    try:
        dist_txt = f"{float(dist):.1f} pc" if dist is not None else "—"
    except (TypeError, ValueError):
        dist_txt = "—"
    stars = card.get("sy_snum")
    nplan = card.get("sy_pnum") or len(planets)
    teff = card.get("st_teff")
    try:
        teff_txt = f"{float(teff):.0f} K" if teff is not None else "—"
    except (TypeError, ValueError):
        teff_txt = "—"
    lines = [
        f"⭐ <b>{host}</b>",
        f"☀️ Stelle nel sistema (TAP): {stars if stars is not None else '—'}",
        f"🪐 Pianeti catalogati: {nplan} · distanza {dist_txt}",
        f"🌡️ Teff stella: {teff_txt}",
        "",
        "☀️ Stella",
    ]
    for idx, row in enumerate(planets):
        name = row.get("pl_name") or "—"
        glyph = planet_glyph(row)
        kind = classify_radius(row.get("pl_rade"))
        try:
            eqt = f"{float(row['pl_eqt']):.0f} K" if row.get("pl_eqt") is not None else "—"
        except (TypeError, ValueError):
            eqt = "—"
        try:
            rade = f"{float(row['pl_rade']):.2f} R⊕" if row.get("pl_rade") is not None else "—"
        except (TypeError, ValueError):
            rade = "—"
        branch = "└──" if idx == len(planets) - 1 else "├──"
        lines.append(f"{branch} {glyph} {name} · {rade} · {eqt}")
        lines.append(f"    {kind}")
    lines.extend(
        [
            "",
            "🌍 = raggio < 1.8 R⊕ e Teq 180–310 K (filtro modello).",
            "<i>Albero dall'archivio NASA, default_flag=1. Nessun pianeta aggiunto a mano.</i>",
        ]
    )
    return "\n".join(lines)
