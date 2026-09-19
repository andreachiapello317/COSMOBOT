"""Tastiere Inline: home a sette mondi e workflow nuovi."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.stones import CATS, COLORS, ENVS, MUSEUM, RARITY, STONES
from services.catalog import (
    ASTRONAUTS,
    BLACK_HOLES,
    COMETS,
    CONSTELLATIONS,
    DEEP_SKY,
    DWARFS,
    FAMOUS_ASTEROIDS,
    GALAXIES,
    LEARN_TOPICS,
    LIFE_TOPICS,
    MISSIONS,
    MOONS,
    PLANETS,
    PROBES,
    SATELLITES,
    STARS,
    STAR_TYPES,
)


def kb_btn(label: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=data)


def nav_row() -> list[InlineKeyboardButton]:
    return [kb_btn("⬅️ Indietro", "nav:back"), kb_btn("🏠 Inizio", "home:menu")]


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
            [kb_btn("🔮 Te stesso", "world:self"), kb_btn("🔮 Oracoli", "world:div")],
            [kb_btn("🔭 Cielo", "world:sky"), kb_btn("🪐 Mondi", "world:mondi")],
            [kb_btn("👽 Vita", "world:vita"), kb_btn("🚀 Missioni", "world:miss")],
            [kb_btn("💎 Pietre", "world:pietre"), kb_btn("✨ COSMICO", "home:cosmico")],
            [kb_btn("🎲 Casuale", "home:random"), kb_btn("🧭 Esplora", "home:esplora")],
        ]
    )


def esplora_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Te stesso", "world:self"), kb_btn("🔮 Oracoli", "world:div")],
            [kb_btn("🔭 Cielo", "world:sky"), kb_btn("🪐 Mondi", "world:mondi")],
            [kb_btn("👽 Vita", "world:vita"), kb_btn("🚀 Missioni", "world:miss")],
            [kb_btn("💎 Pietre", "world:pietre"), kb_btn("✨ COSMICO", "home:cosmico")],
            nav_row(),
        ]
    )


def world_self_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌌 Tema Natale", "natal:open"), kb_btn("🔮 Oroscopo", "home:oroscopo")],
            [kb_btn("🪐 Transiti", "home:transits"), kb_btn("❤️ Compatibilità", "cp:hub")],
            [kb_btn("🪞 Specchio", "home:specchio"), kb_btn("🌙 Rituale", "home:rituale")],
            nav_row(),
        ]
    )


def compat_hub_keyboard(*, has_natal: bool = False, has_syn: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [kb_btn("☀️ Soli", "cp:go:signs"), kb_btn("🌙 Lune", "cp:go:moon")],
        [kb_btn("♀️♂️ Venere·Marte", "cp:go:vm"), kb_btn("⬆️ Ascendenti", "cp:go:asc")],
        [kb_btn("☿️ Mercurio", "cp:go:merc"), kb_btn("🔥 Elementi", "cp:go:el")],
        [kb_btn("☀️🌙⬆️ Big Three", "cp:go:b3")],
    ]
    if has_natal:
        rows.append([kb_btn("🌌 Sinastria (due temi)", "cp:syn")])
    if has_syn:
        rows.append([kb_btn("🏠 Overlay case", "cp:ov")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def compat_sign_keyboard(prefix: str) -> InlineKeyboardMarkup:
    from services.compat import SIGNS

    buttons = [kb_btn(f"{emoji} {it}", f"{prefix}{key}") for key, (it, emoji, _el, _md) in SIGNS.items()]
    grid = _pairs(buttons)
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def compat_element_keyboard(which: str) -> InlineKeyboardMarkup:
    from services.compat import ELEMENTS

    buttons = [kb_btn(f"{em} {name}", f"cp:el:{which}:{key}") for key, (em, name) in ELEMENTS.items()]
    return InlineKeyboardMarkup(_pairs(buttons) + [nav_row()])


def compat_after_keyboard(*, has_natal: bool = False, has_syn: bool = False) -> InlineKeyboardMarkup:
    return compat_hub_keyboard(has_natal=has_natal, has_syn=has_syn)


def world_div_keyboard() -> InlineKeyboardMarkup:
    return oracoli_keyboard()


def oracoli_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🃏 Tarocchi", "tarot:menu"), kb_btn("☯️ I Ching", "iching:open")],
            [kb_btn("🪶 Rune", "home:rune"), kb_btn("🌿 Lenormand", "home:sibille")],
            [kb_btn("🧿 Archetipi", "ora:arch"), kb_btn("🐺 Animali", "ora:anim")],
            [kb_btn("🗝️ Simboli", "ora:symb"), kb_btn("🌿 Elementi", "ora:elem")],
            [kb_btn("🌙 Luna", "ora:lunar"), kb_btn("🪐 Pianeti", "ora:plan")],
            [kb_btn("🪞 Sì / No", "ora:yes"), kb_btn("🕯️ Domande", "ora:askq")],
            [kb_btn("📖 Lettura", "home:lettura"), kb_btn("💎 Pietre", "pt:ora")],
            [kb_btn("🎲 Sorprendimi", "ora:surprise")],
            nav_row(),
        ]
    )


def world_sky_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔭 Cielo adesso", "home:cielo"), kb_btn("📍 Città", "cielo:pick")],
            [kb_btn("🌙 Luna", "home:luna"), kb_btn("🪐 Pianeti", "home:pianeti")],
            [kb_btn("⭐ Stelle", "home:stelle"), kb_btn("✨ Costellazioni", "home:costellazioni")],
            [kb_btn("🌠 Eventi", "home:eventi"), kb_btn("🛰️ Oggetti", "home:profondo")],
            [kb_btn("🧊 Nani", "home:nani"), kb_btn("☄️ Comete", "home:comete")],
            [kb_btn("🌅 Alba", "home:sole"), kb_btn("🛰️ ISS", "home:iss")],
            [kb_btn("☄️ Pietre dallo spazio", "pt:cosmo")],
            nav_row(),
        ]
    )


def world_mondi_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌍 Esplora mondi", "md:hub"), kb_btn("🌌 COSMO", "md:cosmo")],
            [kb_btn("☀️ Sistema Solare", "home:sistema"), kb_btn("⭐ Sistemi stellari", "md:sys")],
            [kb_btn("🪐 Pianeta", "home:pianeta"), kb_btn("🌑 Lune", "home:lune")],
            [kb_btn("🧊 Nani", "home:nani"), kb_btn("☄️ Comete", "home:comete")],
            [kb_btn("🪨 Asteroidi", "home:asteroidi"), kb_btn("🚀 Chi è andato lì", "md:miss")],
            [kb_btn("🎲 Mondo casuale", "md:rand"), kb_btn("📌 Salvati", "md:fav")],
            [kb_btn("🕳️ Buchi neri", "home:buchineri"), kb_btn("🌌 Galassie", "home:galassia")],
            nav_row(),
        ]
    )


def world_vita_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("👽 Siamo soli?", "home:vita"), kb_btn("🪐 Esopianeta", "home:esopianeta")],
            [kb_btn("🌍 Zona abitabile", "home:abitabile"), kb_btn("🧬 E se ci fosse vita?", "md:life")],
            [kb_btn("🌍 Esplora mondi", "md:hub")],
            nav_row(),
        ]
    )


def world_miss_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🚀 Missioni", "home:missioni"), kb_btn("📡 Sonde", "home:sonde")],
            [kb_btn("🚀 Chi è andato lì", "md:miss")],
            [kb_btn("👨‍🚀 Astronauti", "home:astronauta"), kb_btn("🎓 Impara", "home:impara")],
            [kb_btn("🧩 Quiz", "home:quiz"), kb_btn("🏆 Missione", "home:missione")],
            nav_row(),
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
    return lettura_method_keyboard()


def lettura_method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🃏 Tarocchi", "lett:tarot"), kb_btn("☯️ I Ching", "lett:iching")],
            [kb_btn("🪶 Rune", "lett:rune"), kb_btn("🌿 Lenormand", "lett:leno")],
            [kb_btn("🎲 Sorprendimi", "lett:surprise")],
            nav_row(),
        ]
    )


def lenormand_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("1 carta", "leno:n:1"), kb_btn("3 carte", "leno:n:3")],
            [kb_btn("5 carte", "leno:n:5"), kb_btn("9 carte", "leno:n:9")],
            nav_row(),
        ]
    )


def yesno_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🎲 ESTRAI", "yn:go")],
            [kb_btn("🃏 Tarocco", "yn:tarot"), kb_btn("🪶 Runa", "yn:rune")],
            [kb_btn("☯️ I Ching", "yn:iching")],
            nav_row(),
        ]
    )


def oracle_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("💭 Rifletto", "oq:wait")],
            nav_row(),
        ]
    )


def deck_after_keyboard(kind: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🎲 Ancora", f"ora:{kind}")],
            nav_row(),
        ]
    )


def lenormand_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌿 Nuova pesca", "home:sibille")],
            nav_row(),
        ]
    )


def rune_ready_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[kb_btn("✨ SONO PRONTO", "rune:ready")], nav_row()])


def rune_draw_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("ᚠ 1 RUNA", "rune:draw:1"), kb_btn("ᛏ 3 RUNE", "rune:draw:3")],
            nav_row(),
        ]
    )


def rune_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🪶 Nuova lettura", "rune:new")],
            nav_row(),
        ]
    )


def iss_keyboard(map_url: str | None = None) -> InlineKeyboardMarkup:
    rows = []
    if map_url:
        rows.append([InlineKeyboardButton("🗺️ Vedi posizione", url=map_url)])
    rows.append([kb_btn("🔄 Aggiorna", "home:iss")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def cosmico_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Aggiorna", "home:cosmico")],
            nav_row(),
        ]
    )


def sole_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("📍 Roma", "sole:city:0"), kb_btn("📍 Milano", "sole:city:1")],
            [kb_btn("🔄 Aggiorna", "home:sole")],
            nav_row(),
        ]
    )


def back_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([nav_row()])


def catalog_keyboard(kind: str, rows: tuple[dict[str, str], ...], extra: list[list[InlineKeyboardButton]] | None = None) -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{item.get('emoji', '•')} {item['it']}", f"w:{kind}:{item['id']}") for item in rows]
    grid = _pairs(buttons)
    if extra:
        grid.extend(extra)
    grid.append(nav_row())
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
        "f": ("🧊 Nani", "home:nani"),
        "c": ("☄️ Comete", "home:comete"),
        "z": ("🪨 Asteroidi", "home:asteroidi"),
        "t": ("⭐ Stelle", "home:stelle"),
        "y": ("⭐ Stelle", "home:stelle"),
        "k": ("✨ Costellazioni", "home:costellazioni"),
        "o": ("🛰️ Oggetti", "home:profondo"),
    }.get(kind, ("🏠 Inizio", "home:menu"))
    return InlineKeyboardMarkup(
        [
            [kb_btn(back[0], back[1])],
            nav_row(),
        ]
    )


def asteroid_chooser_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☄️ Vicini alla Terra", "aster:neo")],
            [kb_btn("🪨 Asteroidi noti", "aster:famous")],
            [kb_btn("🌌 Nel tema natale", "aster:natal")],
            nav_row(),
        ]
    )


def quiz_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🟢 Facile", "quiz:go:easy"), kb_btn("🟡 Medio", "quiz:go:medium")],
            [kb_btn("🔴 Difficile", "quiz:go:hard"), kb_btn("☠️ Esperto", "quiz:go:expert")],
            [kb_btn("🏆 La mia classifica", "quiz:board")],
            nav_row(),
        ]
    )


def quiz_options_keyboard(n: int) -> InlineKeyboardMarkup:
    labels = ("A", "B", "C", "D")
    buttons = [kb_btn(labels[i], f"quiz:ans:{i}") for i in range(n)]
    return InlineKeyboardMarkup([buttons, [kb_btn("🧩 Altra domanda", "home:quiz")], nav_row()])


def mission_keyboard(*, done: bool) -> InlineKeyboardMarkup:
    if done:
        return InlineKeyboardMarkup(
            [
                [kb_btn("🎲 Casuale", "home:random")],
                nav_row(),
            ]
        )
    return InlineKeyboardMarkup(
        [
            [kb_btn("✅ FATTO", "miss:ok")],
            nav_row(),
        ]
    )


def random_after_keyboard(discover: str | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if discover:
        rows.append([kb_btn("🔭 Scopri", discover)])
    rows.append([kb_btn("🎲 Ancora", "home:random")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def exo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🎲 Casuale", "xp:rand"), kb_btn("🌍 Simile alla Terra", "xp:earth")],
            [kb_btn("🔥 Infernale", "xp:hell"), kb_btn("💎 Estremo", "xp:extreme")],
            [kb_btn("🌊 Oceanico (modello)", "xp:ocean"), kb_btn("🔭 Recente", "xp:recent")],
            [kb_btn("🌍 Zona abitabile", "home:abitabile"), kb_btn("🌍 Esplora mondi", "md:hub")],
            nav_row(),
        ]
    )


def mondi_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌍 Terrestri", "md:f:earth"), kb_btn("🔥 Estremi", "md:f:extreme")],
            [kb_btn("🌊 Oceanici", "md:f:ocean"), kb_btn("🧊 Ghiacciati", "md:f:ice")],
            [kb_btn("🌱 Abitabili", "md:f:hz"), kb_btn("⭐ Multi-stella", "md:f:binary")],
            [kb_btn("👽 Strani", "md:f:weird"), kb_btn("🎲 Sorprendimi", "md:rand")],
            [kb_btn("📅 Del giorno", "md:day"), kb_btn("🔥 Infernali", "md:f:hell")],
            [kb_btn("🌪️ Atmosfere", "md:f:hotjup"), kb_btn("🌀 Orbite pazze", "md:f:ecc")],
            [kb_btn("⏱️ Anno breve", "md:f:short"), kb_btn("🌑 Senza stella", "md:rogue")],
            [kb_btn("💍 Anelli (SS)", "md:rings"), kb_btn("🌙 Molte lune", "md:moons")],
            [kb_btn("🌋 Vulcanici (SS)", "md:volc"), kb_btn("🎲 Genera (finto)", "md:gen")],
            [kb_btn("⭐ Sistemi", "md:sys"), kb_btn("🧬 E se ci fosse vita?", "md:life")],
            [kb_btn("☀️ Sistema Solare", "md:ss"), kb_btn("🚀 Missioni→mondi", "md:miss")],
            [kb_btn("📌 Salvati", "md:fav"), kb_btn("🌌 COSMO", "md:cosmo")],
            nav_row(),
        ]
    )


def mondi_after_keyboard(*, has_system: bool = False, saved: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [kb_btn("🎲 Altro mondo", "md:rand"), kb_btn("📅 Del giorno", "md:day")],
    ]
    if has_system:
        rows.append([kb_btn("📖 Scopri il sistema", "md:host")])
    rows.append(
        [kb_btn("📌 Salva" if not saved else "📌 Già in lista", "md:save"), kb_btn("📌 I miei mondi", "md:fav")]
    )
    rows.append([kb_btn("🌍 Esplora mondi", "md:hub")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def mondi_list_keyboard(n: int, *, back: str = "md:hub") -> InlineKeyboardMarkup:
    buttons = [kb_btn(str(i + 1), f"md:o:{i}") for i in range(n)]
    grid = _pairs(buttons)
    grid.append([kb_btn("🌍 Esplora", back)])
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def sistemi_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☀️ Sistema Solare", "home:sistema"), kb_btn("🎲 Sistema casuale", "md:sysr")],
            [kb_btn("⭐⭐ Binari", "md:sysf:bin"), kb_btn("⭐⭐⭐ Multipli", "md:sysf:multi")],
            [kb_btn("🪐 Molti pianeti", "md:sysf:packed"), kb_btn("🌱 Con zona abitabile", "md:sysf:hzsys")],
            [kb_btn("⭐ TRAPPIST-1", "md:sy:trappist"), kb_btn("⭐ TOI-700", "md:sy:toi700")],
            [kb_btn("⭐ Kepler-90", "md:sy:k90"), kb_btn("⭐ Proxima", "md:sy:proxima")],
            [kb_btn("⭐ HR 8799", "md:sy:hr8799"), kb_btn("⭐ Kepler-186", "md:sy:k186")],
            [kb_btn("⭐ K2-18", "md:sy:k18"), kb_btn("⭐ LHS 1140", "md:sy:lhs1140")],
            nav_row(),
        ]
    )


def sistemi_list_keyboard(n: int) -> InlineKeyboardMarkup:
    buttons = [kb_btn(str(i + 1), f"md:syso:{i}") for i in range(n)]
    grid = _pairs(buttons)
    grid.append([kb_btn("⭐ Sistemi", "md:sys")])
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def sistema_chooser_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☀️ Sistema Solare", "md:ss")],
            [kb_btn("⭐ Sistemi extrasolari", "md:sys")],
            [kb_btn("⭐ TRAPPIST-1", "md:sy:trappist")],
            nav_row(),
        ]
    )


def ss_bodies_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☀️ Sole", "w:p:sun"), kb_btn("🌍 Terra", "w:p:earth")],
            [kb_btn("🌙 Luna", "w:m:moon"), kb_btn("🔴 Marte", "w:p:mars")],
            [kb_btn("🟠 Giove", "w:p:jupiter"), kb_btn("💍 Saturno", "w:p:saturn")],
            [kb_btn("🌀 Urano", "w:p:uranus"), kb_btn("🔵 Nettuno", "w:p:neptune")],
            [kb_btn("🧊 Plutone", "w:f:pluto"), kb_btn("🪨 Mercurio", "w:p:mercury")],
            [kb_btn("🌕 Venere", "w:p:venus"), kb_btn("🌙 Europa", "w:m:europa")],
            [kb_btn("🌙 Encelado", "w:m:enceladus"), kb_btn("🌙 Titano", "w:m:titan")],
            [kb_btn("🌙 Io", "w:m:io"), kb_btn("🌙 Ganimede", "w:m:ganymede")],
            [kb_btn("🌙 Callisto", "w:m:callisto"), kb_btn("☄️ Comete", "home:comete")],
            [kb_btn("🪨 Asteroidi", "home:asteroidi"), kb_btn("🧊 Nani", "home:nani")],
            nav_row(),
        ]
    )


def miss_worlds_keyboard() -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{item.get('emoji', '🚀')} {item['it']}", f"md:wm:{item['id']}") for item in MISSIONS]
    grid = _pairs(buttons)
    grid.append([kb_btn("🌍 Esplora mondi", "md:hub")])
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def life_plus_keyboard() -> InlineKeyboardMarkup:
    extra = [
        [kb_btn("🌱 Candidati HZ (modello)", "md:f:hz"), kb_btn("📡 SETI", "w:v:seti")],
        [kb_btn("🌍 Esplora mondi", "md:hub")],
    ]
    return catalog_keyboard("v", LIFE_TOPICS, extra)


def cosmo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("⭐ Stelle", "home:stelle"), kb_btn("🪐 Sistemi", "md:sys")],
            [kb_btn("🌍 Mondi", "md:hub"), kb_btn("🌌 Galassie", "home:galassia")],
            [kb_btn("🌀 Nebulose", "md:neb"), kb_btn("🕳️ Buchi neri", "home:buchineri")],
            [kb_btn("💥 Supernovae", "w:y:sn"), kb_btn("🔭 Profondo", "home:profondo")],
            nav_row(),
        ]
    )


def fav_list_keyboard(n: int) -> InlineKeyboardMarkup:
    buttons = [kb_btn(str(i + 1), f"md:fo:{i}") for i in range(n)]
    grid = _pairs(buttons)
    grid.append([kb_btn("🌍 Esplora", "md:hub")])
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def cielo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌙 Luna", "home:luna"), kb_btn("🪐 Pianeti", "cielo:planets")],
            [kb_btn("⭐ Stelle", "home:stelle"), kb_btn("☄️ Eventi", "home:eventi")],
            [kb_btn("🌌 Costellazioni", "home:costellazioni"), kb_btn("🔭 Oggetti", "home:profondo")],
            [kb_btn("📍 Città", "cielo:pick"), kb_btn("👁️ Dettaglio", "home:osserva")],
            [kb_btn("🔄 Aggiorna", "home:cielo")],
            nav_row(),
        ]
    )


def stelle_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🎲 Stella casuale", "st:rand"), kb_btn("☀️ Del giorno", "st:day")],
            [kb_btn("✨ Più luminosa ora", "st:bright"), kb_btn("👁 Visibili ora", "st:now")],
            [kb_btn("📍 Vicina", "st:near"), kb_btn("🔴 Giganti rosse", "st:rg")],
            [kb_btn("⚪ Nane bianche", "w:y:wd"), kb_btn("💠 Neutroni", "w:y:ns")],
            [kb_btn("📡 Pulsar", "w:y:pu"), kb_btn("💥 Supernovae", "w:y:sn")],
            [kb_btn("⭐ Doppie", "w:y:bi"), kb_btn("📸 Foto NASA", "st:nasa")],
            nav_row(),
        ]
    )


def costellazioni_keyboard() -> InlineKeyboardMarkup:
    extra = [
        [kb_btn("☀️ Del giorno", "co:day"), kb_btn("🎲 Casuale", "co:rand")],
        [kb_btn("👁 Visibili stasera", "co:now")],
    ]
    return catalog_keyboard("k", CONSTELLATIONS, extra)


def profondo_keyboard() -> InlineKeyboardMarkup:
    extra = [
        [kb_btn("🌌 Galassie", "home:galassia"), kb_btn("🕳️ Buchi neri", "home:buchineri")],
        [kb_btn("👽 Esopianeti", "home:esopianeta")],
    ]
    return catalog_keyboard("o", DEEP_SKY, extra)


def dwarfs_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("f", DWARFS)


def comets_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("c", COMETS)


def famous_asteroids_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("z", FAMOUS_ASTEROIDS)


def stars_pick_keyboard() -> InlineKeyboardMarkup:
    return catalog_keyboard("t", STARS)


def eventi_extra_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌑 Eclissi", "home:eclissi"), kb_btn("🌠 Sciami", "home:meteore")],
            [kb_btn("☀️ Attività solare", "ev:solar"), kb_btn("🌙 Distanza Luna", "ev:moon")],
            nav_row(),
        ]
    )


def world_pietre_keyboard() -> InlineKeyboardMarkup:
    return pietre_hub_keyboard()


def pietre_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Del giorno", "pt:day"), kb_btn("🎲 Casuale", "pt:rand")],
            [kb_btn("🔍 Cerca", "pt:find"), kb_btn("🧭 Esplora", "pt:exp")],
            [kb_btn("🔬 Laboratorio", "pt:lab"), kb_btn("✨ Oracolo", "pt:ora")],
            [kb_btn("🎒 Collezione", "pt:bag"), kb_btn("🏛️ Museo", "pt:mus")],
            [kb_btn("⚖️ Confronta", "pt:cmp"), kb_btn("🧠 Giochi", "pt:game")],
            nav_row(),
        ]
    )


def pietre_list_keyboard(rows: list, prefix: str = "pt:s:") -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{item['emoji']} {item['it']}", f"{prefix}{item['id']}") for item in rows]
    grid = _pairs(buttons)
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def pietre_after_keyboard(sid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔬 Scienza", f"pt:sc:{sid}"), kb_btn("🌋 Geologia", f"pt:sg:{sid}")],
            [kb_btn("🏺 Storia", f"pt:sh:{sid}"), kb_btn("✨ Simbolismo", f"pt:ss:{sid}")],
            [kb_btn("⛏️ Formazione", f"pt:sf:{sid}"), kb_btn("🌍 Dove", f"pt:sw:{sid}")],
            [kb_btn("💰 Valore", f"pt:sv:{sid}"), kb_btn("⚖️ Confronta", f"pt:c1:{sid}")],
            [kb_btn("🎲 Un'altra", "pt:rand"), kb_btn("🎒 Collezione", "pt:bag")],
            nav_row(),
        ]
    )


def pietre_colors_keyboard() -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{em} {name}", f"pt:col:{key}") for key, (em, name) in COLORS.items()]
    grid = _pairs(buttons)
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def pietre_envs_keyboard() -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{em} {name}", f"pt:en:{key}") for key, (em, name) in ENVS.items()]
    grid = _pairs(buttons)
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def pietre_museum_keyboard() -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{em} {name}", f"pt:mr:{key}") for key, (em, name) in MUSEUM.items()]
    grid = _pairs(buttons)
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def pietre_rarity_keyboard() -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{em} {name}", f"pt:rr:{key}") for key, (em, name) in RARITY.items()]
    grid = _pairs(buttons)
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def pietre_explore_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("💎 Gemme", "pt:k:gem"), kb_btn("🔮 Cristalli", "pt:k:cry")],
            [kb_btn("🪨 Minerali", "pt:k:min"), kb_btn("🌋 Rocce", "pt:k:rok")],
            [kb_btn("☄️ Spazio", "pt:k:spc"), kb_btn("🌈 Colore", "pt:cols")],
            [kb_btn("🧭 Ambienti", "pt:envs"), kb_btn("🏆 Rarità", "pt:rars")],
            [kb_btn("🌍 Dove", "pt:maps"), kb_btn("⛏️ Formazione", "pt:forms")],
            [kb_btn("💰 Valore", "pt:val"), kb_btn("🏺 Storia e mito", "pt:myth")],
            [kb_btn("📖 Enciclopedia", "pt:enc")],
            nav_row(),
        ]
    )


def pietre_lab_keyboard(step: str) -> InlineKeyboardMarkup:
    options = {
        "color": [(f"{em} {name}", f"pt:la:c:{key}") for key, (em, name) in COLORS.items() if key != "change"],
        "hard": [("Morbida (<4)", "pt:la:h:soft"), ("Media (4–7)", "pt:la:h:mid"), ("Dura (>7)", "pt:la:h:hard")],
        "trans": [("Trasparente", "pt:la:t:yes"), ("Opaca", "pt:la:t:no"), ("Non so", "pt:la:t:skip")],
        "metal": [("Metallica", "pt:la:m:yes"), ("Non metallica", "pt:la:m:no"), ("Non so", "pt:la:m:skip")],
        "mag": [("Magnetica", "pt:la:g:yes"), ("Non magnetica", "pt:la:g:no"), ("Non so", "pt:la:g:skip")],
        "fizz": [("Effervescente", "pt:la:f:yes"), ("Non reagisce", "pt:la:f:no"), ("Non so", "pt:la:f:skip")],
    }.get(step, [])
    grid = _pairs([kb_btn(label, data) for label, data in options])
    if step == "color":
        grid.append([kb_btn("📸 Ho una foto", "pt:photo")])
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def pietre_oracle_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Un'altra", "pt:ora"), kb_btn("🔮 Approfondisci", "pt:orx")],
            [kb_btn("🪨 3 pietre · tempo", "pt:o3t"), kb_btn("🪨 Corpo·mente·spirito", "pt:o3b")],
            [kb_btn("📖 Scheda", "pt:orcard")],
            nav_row(),
        ]
    )


def pietre_games_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🧠 Indovina la pietra", "pt:g:guess"), kb_btn("🪨 Vero o falso", "pt:g:tf")],
            [kb_btn("⚡ Quiz rapido", "pt:g:quiz")],
            [kb_btn("🌈 Dal colore", "pt:g:color"), kb_btn("🧪 Dalla formula", "pt:g:formula")],
            [kb_btn("🌋 Dall'origine", "pt:g:origin"), kb_btn("🏺 Dalla storia", "pt:g:history")],
            [kb_btn("🔬 Dalla durezza", "pt:g:mohs")],
            nav_row(),
        ]
    )


def pietre_quiz_keyboard(n: int) -> InlineKeyboardMarkup:
    labels = ("A", "B", "C", "D")
    buttons = [kb_btn(labels[i], f"pt:ga:{i}") for i in range(min(n, 4))]
    return InlineKeyboardMarkup([buttons, nav_row()])
