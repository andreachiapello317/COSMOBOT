"""Registro dei bot dentro un solo Telegram. COSMO è il primo; gli altri si aggiungono qui."""

from __future__ import annotations

from typing import Any

BOTS: tuple[dict[str, Any], ...] = (
    {
        "id": "cosmo",
        "emoji": "🌌",
        "name": "COSMO",
        "tag": "Cielo, oracoli, pietre, mondi",
        "ready": True,
    },
    {
        "id": "next",
        "emoji": "➕",
        "name": "Prossimo",
        "tag": "Un bot nuovo, i suoi mondi",
        "ready": False,
    },
)


def bot_by_id(sid: str) -> dict[str, Any] | None:
    for row in BOTS:
        if row["id"] == sid:
            return row
    return None


def ready_bots() -> list[dict[str, Any]]:
    return [row for row in BOTS if row.get("ready")]
