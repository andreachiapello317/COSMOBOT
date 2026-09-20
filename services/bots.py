"""Registro BOTSQUAD: bot nello stesso Telegram. Mondi non mescolati."""

from __future__ import annotations

from typing import Any

BOTS: tuple[dict[str, Any], ...] = (
    {
        "id": "oracolo",
        "emoji": "🔮",
        "name": "ORACOLO",
        "tag": "Te stesso, consultazioni, cielo",
        "ready": True,
        "worlds": ("self", "div", "asksky"),
    },
    {
        "id": "astro",
        "emoji": "🔭",
        "name": "ASTRO",
        "tag": "Osservatorio, meteo, mondi",
        "ready": True,
        "worlds": ("sky", "mondi"),
    },
    {
        "id": "geo",
        "emoji": "🌍",
        "name": "GEO",
        "tag": "Terra, pietre, terremoti",
        "ready": True,
        "worlds": ("terra", "pietre", "quake", "volc", "water", "plates"),
    },
    {
        "id": "calc",
        "emoji": "🧮",
        "name": "CALC",
        "tag": "Calcolatrice a pulsanti",
        "ready": True,
        "worlds": (),
    },
)

# Vecchi token: COSMO → ORACOLO, slot vuoto → ASTRO.
ALIASES = {"cosmo": "oracolo", "next": "astro"}


def canonical_bot_id(sid: str) -> str:
    return str(ALIASES.get(sid) or sid)


def bot_by_id(sid: str) -> dict[str, Any] | None:
    key = canonical_bot_id(sid)
    for row in BOTS:
        if row["id"] == key:
            return row
    return None


def ready_bots() -> list[dict[str, Any]]:
    return [row for row in BOTS if row.get("ready")]


def parent_bot_token(token: str) -> str:
    """Quale bot possiede questo schermo. Serve a Indietro e ai comandi diretti."""
    raw = str(token or "")
    if raw.startswith("bot:"):
        return f"bot:{canonical_bot_id(raw.split(':', 1)[1])}"
    oracolo = (
        "world:self",
        "world:div",
        "world:asksky",
        "loc:",
        "skyq:",
        "wx:",
        "home:cosmico",
        "home:rituale",
        "natal:",
        "cp:",
        "tarot:",
        "iching:",
        "rune:",
        "ora:",
        "leno:",
        "yn:",
        "lett:",
        "oq:",
        "home:oroscopo",
        "home:transits",
        "home:specchio",
        "home:rituale",
        "home:lettura",
        "home:oracoli",
        "home:rune",
        "home:sibille",
        "pt:ora",
        "pt:orx",
        "pt:o3",
        "pt:orcard",
    )
    if any(raw == key or raw.startswith(key) for key in oracolo):
        return "bot:oracolo"
    geo = (
        "world:pietre",
        "world:terra",
        "world:quake",
        "world:volc",
        "world:water",
        "world:plates",
        "geo:",
        "pt:",
        "home:pietre",
    )
    if any(raw == key or raw.startswith(key) for key in geo):
        return "bot:geo"
    if raw.startswith("calc:"):
        return "bot:calc"
    return "bot:astro"
