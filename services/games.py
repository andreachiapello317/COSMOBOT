"""Giochi da tavolo per 🎲 GIOCHI. Dadi veri, niente oracolo e niente soldi."""

from __future__ import annotations

import random
from typing import Any

D6_FACE = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
RPS = {
    "r": ("✊", "Sasso"),
    "p": ("✋", "Carta"),
    "s": ("✌️", "Forbici"),
}
RPS_BEATS = {"r": "s", "p": "r", "s": "p"}
GUESS_MAX = 20
GUESS_TRIES = 6


def roll_dice(n: int = 1, sides: int = 6) -> list[int]:
    count = max(1, min(int(n), 8))
    faces = max(2, min(int(sides), 100))
    return [random.randint(1, faces) for _ in range(count)]


def flip_coin() -> str:
    return random.choice(("heads", "tails"))


def rps_pick() -> str:
    return random.choice(list(RPS))


def rps_outcome(user: str, bot: str) -> str:
    if user == bot:
        return "draw"
    if RPS_BEATS.get(user) == bot:
        return "win"
    return "lose"


def new_guess() -> dict[str, Any]:
    return {"secret": random.randint(1, GUESS_MAX), "tries": 0, "guessed": []}


def apply_guess(state: dict[str, Any], value: int) -> dict[str, Any]:
    secret = int(state.get("secret") or 0)
    guessed = list(state.get("guessed") or [])
    if value in guessed:
        return {"kind": "repeat", "value": value, "state": state}
    guessed.append(value)
    tries = int(state.get("tries") or 0) + 1
    state = {"secret": secret, "tries": tries, "guessed": guessed}
    if value == secret:
        return {"kind": "ok", "value": value, "state": state}
    if tries >= GUESS_TRIES:
        return {"kind": "over", "value": value, "state": state}
    hint = "alto" if value > secret else "basso"
    return {"kind": hint, "value": value, "state": state}


def new_highlow() -> dict[str, Any]:
    first = random.randint(1, 20)
    return {"shown": first, "streak": 0}


def apply_highlow(state: dict[str, Any], direction: str) -> dict[str, Any]:
    shown = int(state.get("shown") or 1)
    nxt = random.randint(1, 20)
    streak = int(state.get("streak") or 0)
    if nxt == shown:
        result = "tie"
    elif (direction == "up" and nxt > shown) or (direction == "dn" and nxt < shown):
        result = "ok"
        streak += 1
    else:
        result = "no"
        streak = 0
    return {
        "kind": result,
        "shown": shown,
        "next": nxt,
        "streak": streak,
        "state": {"shown": nxt, "streak": streak},
    }


def format_dice(rolls: list[int], *, sides: int) -> str:
    if sides == 6:
        faces = "  ".join(f"{D6_FACE.get(n, str(n))} <b>{n}</b>" for n in rolls)
    else:
        faces = "  ".join(f"<b>{n}</b>" for n in rolls)
    total = sum(rolls)
    title = f"{len(rolls)}d{sides}"
    lines = [
        f"🎲 <b>{title.upper()}</b>",
        "<i>Un lancio a caso. Non è un oracolo e non si vince niente.</i>",
        "",
        faces,
    ]
    if len(rolls) > 1:
        extra = " · doppio" if sides == 6 and len(set(rolls)) == 1 else ""
        lines.append(f"Somma: <b>{total}</b>{extra}")
    return "\n".join(lines)


def format_coin(side: str) -> str:
    label = "Testa" if side == "heads" else "Croce"
    emoji = "🌕" if side == "heads" else "🌑"
    return (
        "🪙 <b>MONETA</b>\n"
        "<i>Due facce, stesso peso. Non è un sì/no di ORACOLO.</i>\n\n"
        f"{emoji} <b>{label}</b>"
    )


def format_rps(user: str, bot: str, outcome: str, score: dict[str, int]) -> str:
    ue, un = RPS[user]
    be, bn = RPS[bot]
    mark = {"win": "Hai vinto.", "lose": "Ho vinto io.", "draw": "Pareggio."}[outcome]
    return (
        "✊ <b>MORRA CINESE</b>\n"
        "<i>Sasso, carta, forbici. Niente posta.</i>\n\n"
        f"Tu {ue} <b>{un}</b>\n"
        f"Io {be} <b>{bn}</b>\n\n"
        f"{mark}\n"
        f"Serie: tu {score.get('w', 0)} · io {score.get('l', 0)} · pari {score.get('d', 0)}"
    )


def format_guess_start() -> str:
    return (
        "🎯 <b>INDOVINA</b>\n"
        f"<i>Ho in mente un numero da 1 a {GUESS_MAX}. Hai {GUESS_TRIES} tentativi.</i>\n\n"
        "Tocca un numero."
    )


def format_guess_result(result: dict[str, Any]) -> str:
    kind = result["kind"]
    value = int(result["value"])
    state = result["state"]
    left = GUESS_TRIES - int(state.get("tries") or 0)
    secret = int(state.get("secret") or 0)
    if kind == "ok":
        return (
            "🎯 <b>INDOVINA</b>\n\n"
            f"✅ <b>{value}</b> era il numero.\n"
            f"Tentativi: {state['tries']}."
        )
    if kind == "over":
        return (
            "🎯 <b>INDOVINA</b>\n\n"
            f"❌ {value} no. Tentativi finiti.\n"
            f"Era <b>{secret}</b>."
        )
    if kind == "repeat":
        return (
            "🎯 <b>INDOVINA</b>\n\n"
            f"{value} l'avevi già detto.\n"
            f"Ne restano {left}."
        )
    word = "più basso" if kind == "alto" else "più alto"
    return (
        "🎯 <b>INDOVINA</b>\n\n"
        f"{value} è troppo {kind}. Prova un numero {word}.\n"
        f"Ne restano {left}."
    )


def format_highlow_start(shown: int) -> str:
    return (
        "↕️ <b>ALTO O BASSO</b>\n"
        "<i>Esce un d20. Il prossimo sarà più alto o più basso?</i>\n\n"
        f"Adesso: <b>{shown}</b>"
    )


def format_highlow_result(result: dict[str, Any]) -> str:
    mark = {"ok": "✅ Giusto.", "no": "❌ No.", "tie": "▶ Uguale, non conta."}[result["kind"]]
    return (
        "↕️ <b>ALTO O BASSO</b>\n"
        "<i>Due d20 di fila. Pareggio = si riparte dal nuovo numero.</i>\n\n"
        f"Prima <b>{result['shown']}</b> → poi <b>{result['next']}</b>\n"
        f"{mark}\n"
        f"Serie: <b>{result['streak']}</b>"
    )
