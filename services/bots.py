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
        "tag": "Osservatorio, enciclopedia, satelliti",
        "ready": True,
        "worlds": ("sky", "watch", "mondi"),
    },
    {
        "id": "geo",
        "emoji": "🌍",
        "name": "TERRA",
        "tag": "Eventi, città, fauna, pietre",
        "ready": True,
        "worlds": ("flora", "life", "fauna", "pietre"),
    },
    {
        "id": "oggi",
        "emoji": "📡",
        "name": "OGGI",
        "tag": "Mercati e notizie",
        "ready": True,
        "worlds": ("mkt", "nw"),
    },
    {
        "id": "tool",
        "emoji": "🧰",
        "name": "STRUMENTI",
        "tag": "Calcolatrice, conversioni, bussola",
        "ready": True,
        "worlds": (),
    },
    {
        "id": "quiz",
        "emoji": "🎲",
        "name": "GIOCHI",
        "tag": "Quiz e tavolo",
        "ready": True,
        "worlds": (),
    },
)

# Vecchi token: COSMO → ORACOLO, slot vuoto → ASTRO.
ALIASES = {"cosmo": "oracolo", "next": "astro", "calc": "tool", "bussola": "tool", "giochi": "quiz"}


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
    if raw.startswith(("loc:go:natev", "loc:go:life", "loc:go:fauna")):
        return "bot:geo"
    if raw.startswith(("loc:go:gps", "loc:go:compass", "loc:go:brfrom", "loc:go:brto", "loc:go:clock", "loc:go:coord")):
        return "bot:tool"
    if raw.startswith(
        ("loc:go:cielo", "loc:go:meteo", "loc:go:sole", "loc:go:osserva", "loc:go:luna", "loc:go:watch", "loc:go:terra")
    ):
        return "bot:astro"
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
        "world:natura",
        "world:flora",
        "world:fauna",
        "world:life",
        "fn:",
        "lf:",
        "world:live",
        "world:ocean",
        "world:sea",
        "world:ice",
        "geo:",
        "pt:",
        "home:pietre",
    )
    if any(raw == key or raw.startswith(key) for key in geo):
        return "bot:geo"
    if raw.startswith(("calc:", "cmp:", "tool:")):
        return "bot:tool"
    if raw.startswith(("sq:", "gm:")):
        return "bot:quiz"
    if raw.startswith("og:"):
        return "bot:oggi"
    return "bot:astro"
