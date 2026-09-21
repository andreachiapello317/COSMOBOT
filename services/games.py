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

DICE_KINDS: dict[str, dict[str, Any]] = {
    "6": {"n": 1, "sides": 6, "it": "Un dado", "hint": "Sei facce, da 1 a 6."},
    "2": {"n": 2, "sides": 6, "it": "Due dadi", "hint": "Due dadi a sei facce. Sommo i punti."},
    "3": {"n": 3, "sides": 6, "it": "Tre dadi", "hint": "Tre dadi a sei facce. Sommo i punti."},
    "20": {"n": 1, "sides": 20, "it": "Un d20", "hint": "Venti facce, da 1 a 20."},
}


def dice_spec(kind: str) -> tuple[int, int] | None:
    meta = DICE_KINDS.get(kind)
    if meta is None:
        return None
    return int(meta["n"]), int(meta["sides"])


def dice_beat(kind: str) -> str:
    meta = DICE_KINDS.get(kind) or DICE_KINDS["6"]
    n = int(meta["n"])
    sides = int(meta["sides"])
    if sides == 20:
        return "🎲 Il d20 gira…"
    if n == 1:
        return "🎲 Il dado rotola…"
    if n == 2:
        return "🎲 I due dadi rotolano…"
    return "🎲 I dadi rotolano sul tavolo…"


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
        "direction": direction,
        "streak": streak,
        "state": {"shown": nxt, "streak": streak},
    }


def format_dice_menu() -> str:
    return (
        "🎲 <b>DADI</b>\n"
        "<i>Un lancio a caso. Non predice niente e non si vince soldi.</i>\n\n"
        "Prima scegli i dadi. Poi, quando sei pronto, lanci."
    )


def format_dice_ready(kind: str) -> str:
    meta = DICE_KINDS.get(kind) or DICE_KINDS["6"]
    title = str(meta["it"]).upper()
    return (
        f"🎲 <b>{title}</b>\n"
        f"<i>{meta['hint']} Non è un oracolo.</i>\n\n"
        "Tocca <b>Lancia</b> quando sei pronto."
    )


def format_dice(rolls: list[int], *, sides: int) -> str:
    if sides == 6:
        faces = "  ".join(f"{D6_FACE.get(n, str(n))} <b>{n}</b>" for n in rolls)
    else:
        faces = "  ".join(f"<b>{n}</b>" for n in rolls)
    total = sum(rolls)
    title = f"{len(rolls)}d{sides}"
    lines = [
        f"🎲 <b>{title.upper()}</b>",
        "<i>È uscito. Caso puro, niente predizione.</i>",
        "",
        faces,
    ]
    if len(rolls) > 1:
        extra = ""
        if sides == 6 and len(set(rolls)) == 1:
            extra = " · doppio" if len(rolls) == 2 else " · tutti uguali"
        lines.append(f"Somma: <b>{total}</b>{extra}")
    lines.extend(["", "Rilancia, oppure cambia i dadi."])
    return "\n".join(lines)


def format_coin_ready() -> str:
    return (
        "🪙 <b>MONETA</b>\n"
        "<i>Due facce, stesso peso. Non è il sì/no di ORACOLO: lì c'è una domanda, qui solo testa o croce.</i>\n\n"
        "Tocca <b>Gira</b> quando sei pronto."
    )


def format_coin(side: str) -> str:
    label = "Testa" if side == "heads" else "Croce"
    emoji = "🌕" if side == "heads" else "🌑"
    return (
        "🪙 <b>MONETA</b>\n"
        "<i>La moneta si è fermata.</i>\n\n"
        f"{emoji} <b>{label}</b>\n\n"
        "Gira di nuovo, se vuoi. Non è un verdetto."
    )


def format_rps_start(score: dict[str, int] | None = None) -> str:
    score = score or {}
    w = int(score.get("w") or 0)
    l = int(score.get("l") or 0)
    d = int(score.get("d") or 0)
    serie = f"Serie: tu {w} · io {l} · pari {d}" if (w or l or d) else "Prima mano. Serie a zero."
    return (
        "✊ <b>MORRA CINESE</b>\n"
        "<i>Sasso, carta, forbici. Niente posta, niente oracolo.</i>\n\n"
        f"{serie}\n\n"
        "Scegli la tua mano. Poi mostro la mia."
    )


def format_rps(user: str, bot: str, outcome: str, score: dict[str, int]) -> str:
    ue, un = RPS[user]
    be, bn = RPS[bot]
    mark = {
        "win": "✅ Hai vinto questa mano.",
        "lose": "❌ Questa l'ho presa io.",
        "draw": "🤝 Pareggio. Stessa mano.",
    }[outcome]
    return (
        "✊ <b>MORRA CINESE</b>\n"
        "<i>Uno, due, tre.</i>\n\n"
        f"Tu {ue} <b>{un}</b>\n"
        f"Io {be} <b>{bn}</b>\n\n"
        f"{mark}\n"
        f"Serie: tu {score.get('w', 0)} · io {score.get('l', 0)} · pari {score.get('d', 0)}\n\n"
        "Scegli per la prossima mano."
    )


def _tries_bar(left: int, total: int = GUESS_TRIES) -> str:
    left = max(0, min(int(left), total))
    return "●" * left + "○" * (total - left)


def _guessed_bit(guessed: list[Any]) -> str:
    nums = sorted(int(n) for n in guessed if str(n).isdigit() or isinstance(n, int))
    if not nums:
        return ""
    return "Già detti: " + ", ".join(str(n) for n in nums)


def format_guess_start(*, mid: dict[str, Any] | None = None) -> str:
    if mid and int(mid.get("tries") or 0) > 0:
        left = GUESS_TRIES - int(mid.get("tries") or 0)
        guessed = _guessed_bit(list(mid.get("guessed") or []))
        lines = [
            "🎯 <b>INDOVINA IL NUMERO</b>",
            f"<i>Sempre lo stesso, da 1 a {GUESS_MAX}. Ti dico se sei troppo alto o troppo basso.</i>",
            "",
            "Riprendiamo da dove eri.",
            f"Tentativi: {_tries_bar(left)}  ({left} restanti)",
        ]
        if guessed:
            lines.append(guessed)
        lines.extend(["", "Tocca il prossimo numero."])
        return "\n".join(lines)
    return (
        "🎯 <b>INDOVINA IL NUMERO</b>\n"
        f"<i>Ne ho scelto uno da 1 a {GUESS_MAX}. Hai {GUESS_TRIES} tentativi. "
        "Dopo ogni prova ti dico se sei troppo alto o troppo basso.</i>\n\n"
        "Primo passo: tocca un numero."
    )


def format_guess_result(result: dict[str, Any]) -> str:
    kind = result["kind"]
    value = int(result["value"])
    state = result["state"]
    left = GUESS_TRIES - int(state.get("tries") or 0)
    secret = int(state.get("secret") or 0)
    guessed = _guessed_bit(list(state.get("guessed") or []))
    if kind == "ok":
        return (
            "🎯 <b>INDOVINA IL NUMERO</b>\n\n"
            f"✅ <b>{value}</b> era quello.\n"
            f"Ci sei riuscito in {state['tries']} "
            f"{'tentativo' if state['tries'] == 1 else 'tentativi'}.\n\n"
            "Vuoi un altro numero?"
        )
    if kind == "over":
        return (
            "🎯 <b>INDOVINA IL NUMERO</b>\n\n"
            f"❌ {value} no. Tentativi finiti.\n"
            f"Era <b>{secret}</b>.\n\n"
            "Si ricomincia quando vuoi."
        )
    if kind == "repeat":
        lines = [
            "🎯 <b>INDOVINA IL NUMERO</b>",
            "",
            f"{value} l'avevi già detto. Quel tasto è spento.",
            f"Tentativi: {_tries_bar(left)}  ({left} restanti)",
        ]
        if guessed:
            lines.append(guessed)
        lines.extend(["", "Tocca un altro numero."])
        return "\n".join(lines)
    word = "più basso" if kind == "alto" else "più alto"
    lines = [
        "🎯 <b>INDOVINA IL NUMERO</b>",
        "",
        f"<b>{value}</b> è troppo {kind}. Prova un numero {word}.",
        f"Tentativi: {_tries_bar(left)}  ({left} restanti)",
    ]
    if guessed:
        lines.append(guessed)
    lines.extend(["", "Tocca il prossimo."])
    return "\n".join(lines)


def format_highlow_start(shown: int, *, streak: int = 0, mid: bool = False) -> str:
    intro = "Riprendiamo da questo numero." if mid else "Ti mostro un numero da 1 a 20. Poi indovini se il prossimo è più alto o più basso."
    serie = f"Serie: <b>{streak}</b>" if streak else "Serie a zero."
    return (
        "↕️ <b>ALTO O BASSO</b>\n"
        f"<i>{intro} Pareggio (stesso numero) non conta.</i>\n\n"
        f"Adesso: <b>{shown}</b>\n"
        f"{serie}\n\n"
        "Il prossimo sarà più alto o più basso?"
    )


def format_highlow_result(result: dict[str, Any]) -> str:
    kind = result["kind"]
    direction = str(result.get("direction") or "")
    said = "più alto" if direction == "up" else "più basso"
    mark = {
        "ok": f"✅ Giusto: era {said}.",
        "no": f"❌ No: non era {said}.",
        "tie": "▶ Stesso numero. Non conta, si continua da qui.",
    }[kind]
    follow = "Nuovo numero sul tavolo. Alto o basso?"
    if kind == "no":
        follow = "Serie a zero. Si continua da questo numero, oppure ricominci."
    return (
        "↕️ <b>ALTO O BASSO</b>\n"
        "<i>Due d20 di fila. Niente posta.</i>\n\n"
        f"Prima <b>{result['shown']}</b> → poi <b>{result['next']}</b>\n"
        f"{mark}\n"
        f"Serie: <b>{result['streak']}</b>\n\n"
        f"{follow}"
    )
