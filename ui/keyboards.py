"""Tastiere Inline: home a sei mondi e workflow nuovi."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.catalog import (
    ASTRONAUTS,
    BLACK_HOLES,
    GALAXIES,
    LEARN_TOPICS,
    LIFE_TOPICS,
    MISSIONS,
    MOONS,
    PLANETS,
    PROBES,
    SATELLITES,
)


def kb_btn(label: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=data)


def _pairs(items: list[InlineKeyboardButton]) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for btn in items:
        pair.append(btn)
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    return rows


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Te stesso", "world:self"), kb_btn("☯️ Divinazione", "world:div")],
            [kb_btn("🔭 Cielo", "world:sky"), kb_btn("🪐 Mondi", "world:mondi")],
            [kb_btn("👽 Vita", "world:vita"), kb_btn("🚀 Missioni", "world:miss")],
            [kb_btn("✨ COSMICO", "home:cosmico"), kb_btn("🎲 Random", "home:random")],
            [kb_btn("🧭 Esplora", "home:esplora")],
        ]
    )


def esplora_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Te stesso", "world:self"), kb_btn("☯️ Divinazione", "world:div")],
            [kb_btn("🔭 Cielo", "world:sky"), kb_btn("🪐 Mondi", "world:mondi")],
            [kb_btn("👽 Vita", "world:vita"), kb_btn("🚀 Missioni", "world:miss")],
            [kb_btn("✨ COSMICO", "home:cosmico")],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_self_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌌 Tema Natale", "natal:open"), kb_btn("🔮 Oroscopo", "home:oroscopo")],
            [kb_btn("🪐 Transiti", "home:transits"), kb_btn("🪞 Specchio", "home:specchio")],
            [kb_btn("🌙 Rituale", "home:rituale")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_div_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🃏 Tarocchi", "tarot:menu"), kb_btn("☯️ I Ching", "iching:open")],
            [kb_btn("🪶 Rune", "home:rune"), kb_btn("🔮 Ho una domanda", "home:domanda")],
            [kb_btn("🎲 Random", "home:random")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_sky_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔭 Cielo Roma", "home:cielo"), kb_btn("👁️ Osserva", "home:osserva")],
            [kb_btn("🌙 Luna", "home:luna"), kb_btn("🌠 Meteore", "home:meteore")],
            [kb_btn("🌒 Eclissi", "home:eclissi"), kb_btn("🌅 Alba", "home:sole")],
            [kb_btn("🛰️ Satelliti", "home:satelliti"), kb_btn("🛰️ ISS", "home:iss")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_mondi_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☀️ Sistema", "home:sistema"), kb_btn("🪐 Pianeta", "home:pianeta")],
            [kb_btn("🌑 Lune", "home:lune"), kb_btn("☄️ Asteroidi", "home:asteroidi")],
            [kb_btn("🕳️ Buchi neri", "home:buchineri"), kb_btn("🌌 Galassia", "home:galassia")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_vita_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("👽 Siamo soli?", "home:vita"), kb_btn("🪐 Esopianeta", "home:esopianeta")],
            [kb_btn("🌍 Zona abitabile", "home:abitabile")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_miss_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🚀 Missioni", "home:missioni"), kb_btn("📡 Sonde", "home:sonde")],
            [kb_btn("👨‍🚀 Astronauti", "home:astronauta"), kb_btn("🎓 Impara", "home:impara")],
            [kb_btn("🧩 Quiz", "home:quiz"), kb_btn("🏆 Missione", "home:missione")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def nav_me_keyboard() -> InlineKeyboardMarkup:
    return world_self_keyboard()


def nav_risposte_keyboard() -> InlineKeyboardMarkup:
    return world_div_keyboard()


def nav_cielo_keyboard() -> InlineKeyboardMarkup:
    return world_sky_keyboard()


def nav_universo_keyboard() -> InlineKeyboardMarkup:
    return world_mondi_keyboard()


def domanda_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🃏 Tarocchi", "tarot:pick:ask"), kb_btn("☯️ I Ching", "iching:open")],
            [kb_btn("🪶 Rune", "home:rune")],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def rune_ready_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[kb_btn("✨ SONO PRONTO", "rune:ready")]])


def rune_draw_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("ᚠ 1 RUNA", "rune:draw:1"), kb_btn("ᛏ 3 RUNE", "rune:draw:3")],
        ]
    )


def rune_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🪶 Nuova lettura", "rune:new"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def iss_keyboard(map_url: str | None = None) -> InlineKeyboardMarkup:
    rows = []
    if map_url:
        rows.append([InlineKeyboardButton("🗺️ Vedi posizione", url=map_url)])
    rows.append([kb_btn("🔄 Aggiorna", "home:iss"), kb_btn("🏠 Home", "home:menu")])
    return InlineKeyboardMarkup(rows)


def cosmico_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Aggiorna", "home:cosmico"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def sole_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("📍 Roma", "sole:city:0"), kb_btn("📍 Milano", "sole:city:1")],
            [kb_btn("🔄 Aggiorna", "home:sole"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def back_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[kb_btn("🏠 Home", "home:menu")]])


def catalog_keyboard(kind: str, rows: tuple[dict[str, str], ...], extra: list[list[InlineKeyboardButton]] | None = None) -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{item.get('emoji', '•')} {item['it']}", f"w:{kind}:{item['id']}") for item in rows]
    grid = _pairs(buttons)
    if extra:
        grid.extend(extra)
    grid.append([kb_btn("🏠 Home", "home:menu")])
    return InlineKeyboardMarkup(grid)


def planets_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("p", PLANETS)


def moons_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("m", MOONS)


def galaxies_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("g", GALAXIES)


def blackholes_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("b", BLACK_HOLES)


def missions_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("n", MISSIONS)


def astronauts_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("a", ASTRONAUTS)


def learn_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("l", LEARN_TOPICS)


def life_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("v", LIFE_TOPICS)


def satellites_keyboard() -> InlineKeyboardMarkup:
    extra = [[kb_btn("🛰️ ISS adesso", "home:iss")]]
    return catalog_keyboard("s", SATELLITES, extra)


def probes_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("d", PROBES)


def sheet_after_keyboard(kind: str) -> InlineKeyboardMarkup:
    back = {
        "p": ("🪐 Pianeti", "home:pianeta"),
        "m": ("🌑 Lune", "home:lune"),
        "g": ("🌌 Galassie", "home:galassia"),
        "b": ("🕳️ Buchi neri", "home:buchineri"),
        "n": ("🚀 Missioni", "home:missioni"),
        "a": ("👨‍🚀 Astronauti", "home:astronauta"),
        "l": ("🎓 Impara", "home:impara"),
        "v": ("👽 Vita", "home:vita"),
        "s": ("🛰️ Satelliti", "home:satelliti"),
        "d": ("📡 Sonde", "home:sonde"),
        "r": ("🎲 Ancora", "home:random"),
    }.get(kind, ("🏠 Home", "home:menu"))
    return InlineKeyboardMarkup(
        [
            [kb_btn(back[0], back[1])],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def asteroid_chooser_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☄️ Vicini alla Terra", "aster:neo")],
            [kb_btn("🌌 Nel tema natale", "aster:natal")],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def quiz_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🟢 Facile", "quiz:go:easy"), kb_btn("🟡 Medio", "quiz:go:medium")],
            [kb_btn("🔴 Difficile", "quiz:go:hard"), kb_btn("☠️ Esperto", "quiz:go:expert")],
            [kb_btn("🏆 La mia classifica", "quiz:board")],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def quiz_options_keyboard(n: int) -> InlineKeyboardMarkup:
    labels = ("A", "B", "C", "D")
    buttons = [kb_btn(labels[i], f"quiz:ans:{i}") for i in range(n)]
    return InlineKeyboardMarkup([buttons, [kb_btn("🧩 Altra domanda", "home:quiz")]])


def mission_keyboard(*, done: bool) -> InlineKeyboardMarkup:
    if done:
        return InlineKeyboardMarkup(
            [
                [kb_btn("🎲 Random", "home:random"), kb_btn("🏠 Home", "home:menu")],
            ]
        )
    return InlineKeyboardMarkup(
        [
            [kb_btn("✅ FATTO", "miss:ok")],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def random_after_keyboard(discover: str | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if discover:
        rows.append([kb_btn("🔭 Scopri", discover)])
    rows.append([kb_btn("🎲 Ancora", "home:random"), kb_btn("🏠 Home", "home:menu")])
    return InlineKeyboardMarkup(rows)


def exo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🎲 Un altro esopianeta", "home:esopianeta")],
            [kb_btn("🌍 Zona abitabile", "home:abitabile")],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def cielo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("👁️ Osserva un'altra città", "home:osserva")],
            [kb_btn("🌠 Meteore", "home:meteore"), kb_btn("🌒 Eclissi", "home:eclissi")],
            [kb_btn("🔄 Aggiorna", "home:cielo"), kb_btn("🏠 Home", "home:menu")],
        ]
    )
