"""Tastiere Inline: home a sei mondi e workflow nuovi."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
            [kb_btn("✨ COSMICO", "home:cosmico"), kb_btn("🎲 Random", "home:random")],
            [kb_btn("🧭 Esplora", "home:esplora")],
        ]
    )


def esplora_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Te stesso", "world:self"), kb_btn("🔮 Oracoli", "world:div")],
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
            [kb_btn("📖 Lettura", "home:lettura"), kb_btn("🎲 Sorprendimi", "ora:surprise")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
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
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
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
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_vita_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("👽 Siamo soli?", "home:vita"), kb_btn("🪐 Esopianeta", "home:esopianeta")],
            [kb_btn("🌍 Zona abitabile", "home:abitabile"), kb_btn("🧬 E se ci fosse vita?", "md:life")],
            [kb_btn("🌍 Esplora mondi", "md:hub")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def world_miss_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🚀 Missioni", "home:missioni"), kb_btn("📡 Sonde", "home:sonde")],
            [kb_btn("🚀 Chi è andato lì", "md:miss")],
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
    return lettura_method_keyboard()


def lettura_method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🃏 Tarocchi", "lett:tarot"), kb_btn("☯️ I Ching", "lett:iching")],
            [kb_btn("🪶 Rune", "lett:rune"), kb_btn("🌿 Lenormand", "lett:leno")],
            [kb_btn("🎲 Sorprendimi", "lett:surprise")],
            [kb_btn("🔮 Oracoli", "home:oracoli"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def lenormand_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("1 carta", "leno:n:1"), kb_btn("3 carte", "leno:n:3")],
            [kb_btn("5 carte", "leno:n:5"), kb_btn("9 carte", "leno:n:9")],
            [kb_btn("🔮 Oracoli", "home:oracoli"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def yesno_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🎲 ESTRAI", "yn:go")],
            [kb_btn("🃏 Tarocco", "yn:tarot"), kb_btn("🪶 Runa", "yn:rune")],
            [kb_btn("☯️ I Ching", "yn:iching")],
            [kb_btn("🔮 Oracoli", "home:oracoli")],
        ]
    )


def oracle_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("💭 Rifletto", "oq:wait")],
            [kb_btn("🕯️ Un'altra", "ora:askq"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def deck_after_keyboard(kind: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🎲 Ancora", f"ora:{kind}")],
            [kb_btn("🔮 Oracoli", "home:oracoli"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def lenormand_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌿 Nuova pesca", "home:sibille")],
            [kb_btn("🔮 Oracoli", "home:oracoli"), kb_btn("🏠 Home", "home:menu")],
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
        "f": ("🧊 Nani", "home:nani"),
        "c": ("☄️ Comete", "home:comete"),
        "z": ("🪨 Asteroidi", "home:asteroidi"),
        "t": ("⭐ Stelle", "home:stelle"),
        "y": ("⭐ Stelle", "home:stelle"),
        "k": ("✨ Costellazioni", "home:costellazioni"),
        "o": ("🛰️ Oggetti", "home:profondo"),
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
            [kb_btn("🪨 Asteroidi noti", "aster:famous")],
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
            [kb_btn("🎲 Casuale", "xp:rand"), kb_btn("🌍 Simile alla Terra", "xp:earth")],
            [kb_btn("🔥 Infernale", "xp:hell"), kb_btn("💎 Estremo", "xp:extreme")],
            [kb_btn("🌊 Oceanico (modello)", "xp:ocean"), kb_btn("🔭 Recente", "xp:recent")],
            [kb_btn("🌍 Zona abitabile", "home:abitabile"), kb_btn("🌍 Esplora mondi", "md:hub")],
            [kb_btn("🏠 Home", "home:menu")],
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
            [kb_btn("🪐 Mondi", "world:mondi"), kb_btn("🏠 Home", "home:menu")],
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
    rows.append([kb_btn("🌍 Esplora mondi", "md:hub"), kb_btn("🏠 Home", "home:menu")])
    return InlineKeyboardMarkup(rows)


def mondi_list_keyboard(n: int, *, back: str = "md:hub") -> InlineKeyboardMarkup:
    buttons = [kb_btn(str(i + 1), f"md:o:{i}") for i in range(n)]
    grid = _pairs(buttons)
    grid.append([kb_btn("🌍 Esplora", back), kb_btn("🏠 Home", "home:menu")])
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
            [kb_btn("🌍 Esplora mondi", "md:hub"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def sistemi_list_keyboard(n: int) -> InlineKeyboardMarkup:
    buttons = [kb_btn(str(i + 1), f"md:syso:{i}") for i in range(n)]
    grid = _pairs(buttons)
    grid.append([kb_btn("⭐ Sistemi", "md:sys"), kb_btn("🏠 Home", "home:menu")])
    return InlineKeyboardMarkup(grid)


def sistema_chooser_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☀️ Sistema Solare", "md:ss")],
            [kb_btn("⭐ Sistemi extrasolari", "md:sys")],
            [kb_btn("⭐ TRAPPIST-1", "md:sy:trappist")],
            [kb_btn("🏠 Home", "home:menu")],
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
            [kb_btn("🌍 Esplora mondi", "md:hub"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def miss_worlds_keyboard() -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{item.get('emoji', '🚀')} {item['it']}", f"md:wm:{item['id']}") for item in MISSIONS]
    grid = _pairs(buttons)
    grid.append([kb_btn("🌍 Esplora mondi", "md:hub"), kb_btn("🏠 Home", "home:menu")])
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
            [kb_btn("🪐 Mondi (reparto)", "world:mondi"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def fav_list_keyboard(n: int) -> InlineKeyboardMarkup:
    buttons = [kb_btn(str(i + 1), f"md:fo:{i}") for i in range(n)]
    grid = _pairs(buttons)
    grid.append([kb_btn("🌍 Esplora", "md:hub"), kb_btn("🏠 Home", "home:menu")])
    return InlineKeyboardMarkup(grid)


def cielo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌙 Luna", "home:luna"), kb_btn("🪐 Pianeti", "cielo:planets")],
            [kb_btn("⭐ Stelle", "home:stelle"), kb_btn("☄️ Eventi", "home:eventi")],
            [kb_btn("🌌 Costellazioni", "home:costellazioni"), kb_btn("🔭 Oggetti", "home:profondo")],
            [kb_btn("📍 Città", "cielo:pick"), kb_btn("👁️ Dettaglio", "home:osserva")],
            [kb_btn("🔄 Aggiorna", "home:cielo"), kb_btn("🏠 Home", "home:menu")],
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
            [kb_btn("🔭 Cielo", "home:cielo"), kb_btn("🏠 Home", "home:menu")],
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
            [kb_btn("🔭 Cielo", "home:cielo"), kb_btn("🏠 Home", "home:menu")],
        ]
    )
