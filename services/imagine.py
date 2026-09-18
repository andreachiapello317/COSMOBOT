"""Mondi immaginari etichettati come tali. Non sono schede astronomiche."""

from __future__ import annotations

import random
from typing import Any

PREFIXES = ("Nyx", "Vela", "Kora", "Isk", "Thal", "Ryn", "Asha", "Qet", "Lumen", "Voss")
SUFFIXES = ("Prime", "Minor", "Atoll", "Drift", "Well", "Gate", "Hollow", "Reach")
CLIMATES = (
    "coperto di nubi dense",
    "con ghiacci stagionali",
    "con tempeste di polvere",
    "con un oceano modellato (inventato)",
    "con anelli deboli (inventati)",
    "in rotazione sincrona, nel racconto",
)
NOTES = (
    "Pensato per una sessione di gioco, non per un paper.",
    "I numeri sono dadi, non misure TAP.",
    "Se ti serve un mondo reale, torna su /mondi e pesca l'archivio NASA.",
)


def generate_world(rng: random.Random | None = None) -> dict[str, Any]:
    rnd = rng or random.Random()
    name = f"{rnd.choice(PREFIXES)}-{rnd.randint(10, 990)} {rnd.choice(SUFFIXES)}"
    rade = round(rnd.uniform(0.6, 14.0), 2)
    eqt = rnd.randint(80, 2400)
    period = round(rnd.uniform(0.4, 480.0), 1)
    moons = rnd.randint(0, 18)
    stars = rnd.choice((1, 1, 1, 2, 3))
    return {
        "name": name,
        "kind": "imag",
        "pl_rade": rade,
        "pl_eqt": eqt,
        "pl_orbper": period,
        "moons": moons,
        "stars": stars,
        "climate": rnd.choice(CLIMATES),
        "note": rnd.choice(NOTES),
    }


def format_imaginary(world: dict[str, Any]) -> str:
    return (
        "🎲 <b>MONDO GENERATO</b>\n"
        "⚠️ <b>Non è un pianeta reale.</b> Non è nell'archivio NASA.\n\n"
        f"🪐 <b>{world.get('name')}</b>\n"
        f"⭐ Stelle nel racconto: {world.get('stars')}\n"
        f"📏 Raggio (dado): {world.get('pl_rade')} R⊕\n"
        f"🌡️ Teq (dado): {world.get('pl_eqt')} K\n"
        f"⏱️ Anno (dado): {world.get('pl_orbper')} giorni\n"
        f"🌙 Lune (dado): {world.get('moons')}\n"
        f"🌀 Clima: {world.get('climate')}\n\n"
        f"{world.get('note')}\n\n"
        "<i>Generatore locale COSMOBOT. Zero misure, zero scoperte.</i>"
    )
