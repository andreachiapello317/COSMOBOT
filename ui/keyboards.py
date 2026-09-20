"""Tastiere Inline: home a sette mondi e workflow nuovi."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.earth import EARTH_TOPICS, GLACIERS, OCEANS, PLATES, SEAS, VOLCANOES, WATER
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


def all_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 ORACOLO", "bot:oracolo")],
            [kb_btn("🔭 ASTRO", "bot:astro")],
            [kb_btn("🌿 NATURA", "bot:geo")],
            [kb_btn("🧮 MATEMATICA", "bot:calc")],
            [kb_btn("🧭 BUSSOLA", "bot:bussola")],
            [kb_btn("📚 Aiuto", "home:aiuto")],
        ]
    )


def home_keyboard() -> InlineKeyboardMarkup:
    return all_hub_keyboard()


def esplora_keyboard() -> InlineKeyboardMarkup:
    return all_hub_keyboard()


def oracolo_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Te stesso", "world:self")],
            [kb_btn("🃏 Consultazioni", "world:div")],
            [kb_btn("🌌 Interroga il cielo", "loc:go:skyq")],
            nav_row(),
        ]
    )


def geo_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌿 Flora", "world:flora")],
            [kb_btn("🐾 Fauna", "world:fauna")],
            [kb_btn("💎 Pietre", "world:pietre")],
            nav_row(),
        ]
    )


def world_flora_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌍 Eventi", "geo:world")],
            [kb_btn("📡 Live", "world:live")],
            [kb_btn("📖 Esplora la natura", "world:natura")],
            nav_row(),
        ]
    )


def world_fauna_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            nav_row(),
        ]
    )


def world_live_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("📅 Scosse 24 ore", "geo:quake:day"), kb_btn("📆 Scosse 7 giorni", "geo:quake:week")],
            [kb_btn("⚠️ Scosse importanti", "geo:quake:sig")],
            [kb_btn("🌋 Eruzioni aperte", "geo:ev:volcanoes"), kb_btn("🌀 Cicloni e tempeste", "geo:ev:severeStorms")],
            [kb_btn("🔥 Incendi aperti", "geo:ev:wildfires"), kb_btn("🧊 Ghiaccio", "geo:ev:seaLakeIce")],
            [kb_btn("🌊 Alluvioni", "geo:ev:floods"), kb_btn("🪨 Frane", "geo:ev:landslides")],
            [kb_btn("🌵 Siccità", "geo:ev:drought"), kb_btn("📋 Tutti i fenomeni", "geo:events")],
            [kb_btn("🌿 Flora", "world:flora")],
            nav_row(),
        ]
    )


def world_natura_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌍 Terra", "world:terra"), kb_btn("🌊 Oceani", "world:ocean")],
            [kb_btn("🌊 Mari", "world:sea"), kb_btn("🔥 Vulcani", "world:volc")],
            [kb_btn("🧭 Placche", "world:plates"), kb_btn("🧊 Ghiacciai", "world:ice")],
            nav_row(),
        ]
    )


def natura_here_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Aggiorna", "geo:here")],
            [kb_btn("📍 Cambia città", "geo:city")],
            nav_row(),
        ]
    )


def natura_world_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Aggiorna", "geo:world")],
            [kb_btn("🌿 Flora", "world:flora")],
            nav_row(),
        ]
    )


def geo_quakes_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("📅 24 ore M≥4,5", "geo:quake:day"), kb_btn("📆 7 giorni M≥2,5", "geo:quake:week")],
            [kb_btn("⚠️ Significativi", "geo:quake:sig")],
            nav_row(),
        ]
    )


def geo_events_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Aperti", "geo:events"), kb_btn("🔥 Vulcani", "geo:ev:volcanoes")],
            [kb_btn("🌪️ Tempeste", "geo:ev:severeStorms"), kb_btn("🔥 Incendi", "geo:ev:wildfires")],
            [kb_btn("🧊 Ghiaccio", "geo:ev:seaLakeIce")],
            nav_row(),
        ]
    )


def geo_list_keyboard(kind: str, rows: tuple[dict[str, str], ...]) -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"{item['emoji']} {item['it']}", f"geo:s:{kind}:{item['id']}") for item in rows]
    grid = _pairs(buttons)
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def world_terra_keyboard() -> InlineKeyboardMarkup:
    return geo_list_keyboard("terra", EARTH_TOPICS)


def world_quake_keyboard() -> InlineKeyboardMarkup:
    return geo_quakes_keyboard()


def world_volc_keyboard() -> InlineKeyboardMarkup:
    return geo_list_keyboard("volc", VOLCANOES)


def world_water_keyboard() -> InlineKeyboardMarkup:
    return geo_list_keyboard("water", WATER)


def world_plates_keyboard() -> InlineKeyboardMarkup:
    return geo_list_keyboard("plate", PLATES)


def world_ocean_keyboard() -> InlineKeyboardMarkup:
    return geo_list_keyboard("ocean", OCEANS)


def world_sea_keyboard() -> InlineKeyboardMarkup:
    return geo_list_keyboard("sea", SEAS)


def world_ice_keyboard() -> InlineKeyboardMarkup:
    return geo_list_keyboard("ice", GLACIERS)


def geo_after_keyboard(kind: str) -> InlineKeyboardMarkup:
    back = {
        "terra": ("🌍 Terra", "world:terra"),
        "volc": ("🔥 Vulcani", "world:volc"),
        "water": ("🌊 Acqua", "world:water"),
        "plate": ("🧭 Placche", "world:plates"),
        "ocean": ("🌊 Oceani", "world:ocean"),
        "sea": ("🌊 Mari", "world:sea"),
        "ice": ("🧊 Ghiacciai", "world:ice"),
    }.get(kind, ("🌿 Flora", "world:flora"))
    return InlineKeyboardMarkup([[kb_btn(back[0], back[1])], nav_row()])


def astro_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔭 Cielo", "world:sky"), kb_btn("🌤️ Meteo", "loc:go:meteo")],
            [kb_btn("🚀 Esplora lo spazio", "world:mondi")],
            [kb_btn("🛰️ In orbita", "world:orbit")],
            nav_row(),
        ]
    )


def world_asksky_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌌 Interroga", "loc:go:skyq")],
            nav_row(),
        ]
    )


def place_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🇮🇹 Italia", "loc:it"), kb_btn("🌍 Mondo", "loc:wd")],
            [kb_btn("✍️ Scrivi una città", "loc:ask")],
            nav_row(),
        ]
    )


def place_list_keyboard(kind: str, cities: tuple[tuple[str, float, float], ...]) -> InlineKeyboardMarkup:
    buttons = [kb_btn(f"📍 {name}", f"loc:city:{kind}:{idx}") for idx, (name, _lat, _lon) in enumerate(cities)]
    grid = _pairs(buttons)
    grid.append([kb_btn("✍️ Altra città", "loc:ask")])
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def cosmo_hub_keyboard() -> InlineKeyboardMarkup:
    return oracolo_hub_keyboard()


def world_self_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Oroscopo", "home:oroscopo"), kb_btn("🌌 Tema natale", "natal:open")],
            [kb_btn("🪞 Specchio", "home:specchio"), kb_btn("❤️ Compatibilità", "cp:hub")],
            nav_row(),
        ]
    )


def compat_hub_keyboard(*, has_natal: bool = False, has_syn: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [kb_btn("♈ Due segni", "cp:go:signs")],
        [kb_btn("✨ Confronti avanzati", "cp:adv")],
    ]
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def compat_advanced_keyboard(*, has_natal: bool = False, has_syn: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [kb_btn("🌙 Lune", "cp:go:moon"), kb_btn("⬆️ Ascendenti", "cp:go:asc")],
        [kb_btn("♀️♂️ Venere e Marte", "cp:go:vm")],
        [kb_btn("☀️🌙⬆️ Big Three", "cp:go:b3")],
    ]
    if has_syn:
        rows.append([kb_btn("🏠 Overlay case", "cp:ov")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def compat_b3_source_keyboard(who: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("✍️ Li so già", f"cp:src:{who}:know")],
            [kb_btn("📅 Calcolali da nascita", f"cp:src:{who}:calc")],
            nav_row(),
        ]
    )


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
    rows = [
        [kb_btn("♈ Altri due segni", "cp:go:signs"), kb_btn("✨ Avanzate", "cp:adv")],
    ]
    if has_syn:
        rows.append([kb_btn("🏠 Overlay case", "cp:ov")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def world_div_keyboard() -> InlineKeyboardMarkup:
    return oracoli_keyboard()


def oracoli_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🃏 Tarocchi", "tarot:menu"), kb_btn("☯️ I Ching", "iching:open")],
            [kb_btn("🪶 Rune", "home:rune"), kb_btn("🌿 Lenormand", "home:sibille")],
            [kb_btn("🪞 Sì / No", "ora:yes"), kb_btn("💎 Pietre", "pt:ora")],
            [kb_btn("🔮 Fai scegliere all'oracolo", "ora:surprise")],
            nav_row(),
        ]
    )


def oracle_surprise_after_keyboard(open_label: str, open_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 Un altro", "ora:surprise"), kb_btn(open_label, open_data)],
            nav_row(),
        ]
    )


def oracoli_mazzi_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🧿 Archetipi", "ora:arch"), kb_btn("🐺 Animali", "ora:anim")],
            [kb_btn("🗝️ Simboli", "ora:symb"), kb_btn("🌿 Elementi", "ora:elem")],
            [kb_btn("🕯️ Una domanda", "ora:askq")],
            nav_row(),
        ]
    )


def world_sky_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌙 Luna", "sky:luna"), kb_btn("⭐ Stelle", "sky:stelle")],
            [kb_btn("🌅 Alba", "sky:alba"), kb_btn("🌇 Tramonto", "sky:tramonto")],
            [kb_btn("🌠 Eventi", "sky:eventi")],
            [kb_btn("📍 Cambia città", "sky:city")],
            nav_row(),
        ]
    )


def sky_result_keyboard(*extra: list[InlineKeyboardButton]) -> InlineKeyboardMarkup:
    rows = [list(row) for row in extra if row]
    rows.append([kb_btn("🔭 Cielo", "world:sky"), kb_btn("📍 Cambia città", "sky:city")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def math_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🧮 Calcolatrice", "calc:pad")],
            [kb_btn("➗ Percentuale", "calc:pct"), kb_btn("🔄 Conversioni", "calc:conv")],
            nav_row(),
        ]
    )


def calc_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("7", "calc:7"), kb_btn("8", "calc:8"), kb_btn("9", "calc:9"), kb_btn("÷", "calc:div")],
            [kb_btn("4", "calc:4"), kb_btn("5", "calc:5"), kb_btn("6", "calc:6"), kb_btn("×", "calc:mul")],
            [kb_btn("1", "calc:1"), kb_btn("2", "calc:2"), kb_btn("3", "calc:3"), kb_btn("−", "calc:sub")],
            [kb_btn("0", "calc:0"), kb_btn(".", "calc:dot"), kb_btn("=", "calc:eq"), kb_btn("+", "calc:add")],
            [kb_btn("C", "calc:c"), kb_btn("⌫", "calc:bs"), kb_btn("(", "calc:lp"), kb_btn(")", "calc:rp")],
            [kb_btn("🧮 Matematica", "calc:hub")],
            nav_row(),
        ]
    )


def math_percent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("20% di 150", "calc:pex:of:20:150"), kb_btn("15 su 60", "calc:pex:ratio:15:60")],
            [kb_btn("Aumenta 80 del 10%", "calc:pex:up:80:10"), kb_btn("Sconta 80 del 10%", "calc:pex:down:80:10")],
            [kb_btn("✍️ Scrivi tu", "calc:pctask")],
            nav_row(),
        ]
    )


def math_convert_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("km → miglia", "calc:cv:km_mi"), kb_btn("miglia → km", "calc:cv:mi_km")],
            [kb_btn("m → piedi", "calc:cv:m_ft"), kb_btn("piedi → m", "calc:cv:ft_m")],
            [kb_btn("kg → libbre", "calc:cv:kg_lb"), kb_btn("libbre → kg", "calc:cv:lb_kg")],
            [kb_btn("°C → °F", "calc:cv:c_f"), kb_btn("°F → °C", "calc:cv:f_c")],
            nav_row(),
        ]
    )


def compass_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("📍 Posizione GPS", "cmp:gps")],
            [kb_btn("🧭 Bussola", "cmp:needle")],
            [kb_btn("🎯 Verso un luogo", "cmp:to")],
            nav_row(),
        ]
    )


def compass_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("📍 Posizione", "cmp:gps"), kb_btn("🧭 Bussola", "cmp:needle")],
            [kb_btn("🎯 Verso un luogo", "cmp:to")],
            [kb_btn("📍 Cambia luogo", "cmp:city"), kb_btn("📡 Posizione Telegram", "cmp:share")],
            nav_row(),
        ]
    )


def meteo_span_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("Oggi e domani", "wx:d:2")],
            [kb_btn("3 giorni", "wx:d:3"), kb_btn("7 giorni", "wx:d:7")],
            [kb_btn("14 giorni", "wx:d:14")],
            [kb_btn("✍️ Scrivi i giorni", "wx:ask")],
            [kb_btn("📍 Cambia città", "loc:go:meteo")],
            nav_row(),
        ]
    )


def sky_catalog_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🛰️ Profondo", "home:profondo"), kb_btn("🧊 Nani", "home:nani")],
            [kb_btn("☄️ Comete", "home:comete"), kb_btn("☄️ Pietre dallo spazio", "pt:cosmo")],
            nav_row(),
        ]
    )


def world_mondi_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☀️ Sistema Solare", "home:sistema"), kb_btn("🌑 Lune", "home:lune")],
            [kb_btn("🧊 Pianeti nani", "home:nani"), kb_btn("☄️ Comete", "home:comete")],
            [kb_btn("🪨 Asteroidi", "home:asteroidi"), kb_btn("⭐ Stelle", "home:stelle")],
            [kb_btn("✨ Costellazioni", "home:costellazioni"), kb_btn("🌌 Galassie", "home:galassia")],
            [kb_btn("🌀 Nebulose", "md:neb"), kb_btn("🕳️ Buchi neri", "home:buchineri")],
            [kb_btn("🔭 Cielo profondo", "home:profondo"), kb_btn("🪐 Esopianeti", "md:hub")],
            [kb_btn("⭐ Sistemi", "md:sys"), kb_btn("👽 Vita", "world:vita")],
            [kb_btn("🚀 Missioni", "world:miss"), kb_btn("📡 Sonde", "home:sonde")],
            [kb_btn("🛰️ Satelliti", "home:satelliti"), kb_btn("👨‍🚀 Astronauti", "home:astronauta")],
            [kb_btn("☀️ Attività solare", "ev:solar"), kb_btn("📚 Impara", "home:impara")],
            nav_row(),
        ]
    )


def world_orbit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🛰️ ISS adesso", "home:iss"), kb_btn("👥 Chi è in orbita", "orb:crew")],
            nav_row(),
        ]
    )


def pianeti_now_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Aggiorna", "home:pianeti"), kb_btn("🪐 Schede", "home:pianeta")],
            [kb_btn("🚀 Esplora lo spazio", "world:mondi")],
            nav_row(),
        ]
    )


def world_vita_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("👽 Siamo soli?", "home:vita"), kb_btn("🪐 Esopianeta", "home:esopianeta")],
            [kb_btn("🌍 Zona abitabile", "home:abitabile"), kb_btn("🧬 E se ci fosse vita?", "md:life")],
            [kb_btn("🪐 Esopianeti", "md:hub"), kb_btn("🚀 Enciclopedia", "world:mondi")],
            nav_row(),
        ]
    )


def world_miss_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🚀 Missioni", "home:missioni"), kb_btn("📡 Sonde", "home:sonde")],
            [kb_btn("👨‍🚀 Astronauti", "home:astronauta"), kb_btn("🎓 Impara", "home:impara")],
            [kb_btn("🧩 Quiz", "home:quiz"), kb_btn("🚀 Enciclopedia", "world:mondi")],
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
            [kb_btn("🔮 Fai scegliere all'oracolo", "lett:surprise")],
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


def lenormand_ready_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌿 Mescola", "leno:mix")],
            [kb_btn("✍️ Una frase, se vuoi", "leno:phrase")],
            nav_row(),
        ]
    )


def lenormand_next_keyboard(*, last: bool) -> InlineKeyboardMarkup:
    label = "✨ Il quadro" if last else "🌿 Gira la prossima"
    data = "leno:board" if last else "leno:next"
    return InlineKeyboardMarkup([[kb_btn(label, data)], nav_row()])


def lenormand_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌿 Nuova pesca", "home:sibille")],
            nav_row(),
        ]
    )


def rune_ready_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("ᚠ 1 runa", "rune:draw:1"), kb_btn("ᛏ 3 rune", "rune:draw:3")],
            nav_row(),
        ]
    )


def rune_cast_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🪶 Scuoti il sacchetto", "rune:mix")],
            [kb_btn("✍️ Una frase, se vuoi", "rune:phrase")],
            nav_row(),
        ]
    )


def rune_draw_keyboard() -> InlineKeyboardMarkup:
    return rune_ready_keyboard()


def rune_next_keyboard(*, last: bool) -> InlineKeyboardMarkup:
    label = "✨ Il quadro" if last else "🪶 Gira la prossima"
    data = "rune:board" if last else "rune:next"
    return InlineKeyboardMarkup([[kb_btn(label, data)], nav_row()])


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
    rows.append([kb_btn("🔄 Aggiorna", "home:iss"), kb_btn("🛰️ In orbita", "world:orbit")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def cosmico_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔄 Un'altra città", "loc:go:skyq")],
            nav_row(),
        ]
    )


def sole_keyboard() -> InlineKeyboardMarkup:
    return sky_result_keyboard([kb_btn("🔄 Aggiorna", "sky:alba")])


def meteo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("Oggi e domani", "wx:d:2"), kb_btn("3 giorni", "wx:d:3")],
            [kb_btn("7 giorni", "wx:d:7"), kb_btn("14 giorni", "wx:d:14")],
            [kb_btn("✍️ Altri giorni", "wx:ask"), kb_btn("📍 Cambia città", "loc:go:meteo")],
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
        "r": ("🚀 Esplora lo spazio", "world:mondi"),
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
                [kb_btn("🚀 Missioni", "world:miss")],
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
            [kb_btn("🌍 Simile alla Terra", "xp:earth"), kb_btn("🔭 Recente", "xp:recent")],
            [kb_btn("🔥 Infernale", "xp:hell"), kb_btn("💎 Estremo", "xp:extreme")],
            [kb_btn("🌊 Oceanico (modello)", "xp:ocean"), kb_btn("🌍 Zona abitabile", "home:abitabile")],
            [kb_btn("🪐 Catalogo NASA", "md:hub"), kb_btn("🚀 Enciclopedia", "world:mondi")],
            nav_row(),
        ]
    )


def mondi_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌍 Terrestri", "md:f:earth"), kb_btn("🔥 Estremi", "md:f:extreme")],
            [kb_btn("🌊 Oceanici", "md:f:ocean"), kb_btn("🧊 Ghiacciati", "md:f:ice")],
            [kb_btn("🌱 Abitabili", "md:f:hz"), kb_btn("⭐ Multi-stella", "md:f:binary")],
            [kb_btn("👽 Strani", "md:f:weird"), kb_btn("🔥 Infernali", "md:f:hell")],
            [kb_btn("🌪️ Atmosfere", "md:f:hotjup"), kb_btn("🌀 Orbite pazze", "md:f:ecc")],
            [kb_btn("⏱️ Anno breve", "md:f:short"), kb_btn("🌑 Senza stella", "md:rogue")],
            [kb_btn("💍 Anelli (SS)", "md:rings"), kb_btn("🌙 Molte lune", "md:moons")],
            [kb_btn("🌋 Vulcanici (SS)", "md:volc"), kb_btn("🧬 E se ci fosse vita?", "md:life")],
            [kb_btn("⭐ Sistemi", "md:sys"), kb_btn("☀️ Sistema Solare", "md:ss")],
            [kb_btn("🚀 Missioni", "md:miss"), kb_btn("🚀 Enciclopedia", "world:mondi")],
            nav_row(),
        ]
    )


def mondi_after_keyboard(*, has_system: bool = False, saved: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if has_system:
        rows.append([kb_btn("📖 Scopri il sistema", "md:host")])
    rows.append([kb_btn("🪐 Altri esopianeti", "md:hub")])
    rows.append([kb_btn("🚀 Enciclopedia", "world:mondi")])
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
            [kb_btn("☀️ Sistema Solare", "home:sistema"), kb_btn("🚀 Enciclopedia", "world:mondi")],
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
            [kb_btn("🪐 Esopianeti", "md:hub"), kb_btn("🌌 Galassie", "home:galassia")],
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
    return world_sky_keyboard()


def stelle_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("☀️ Del giorno", "st:day"), kb_btn("📍 Vicina", "st:near")],
            [kb_btn("🔴 Giganti rosse", "st:rg"), kb_btn("🚀 Enciclopedia", "world:mondi")],
            [kb_btn("⚪ Nane bianche", "w:y:wd"), kb_btn("💠 Neutroni", "w:y:ns")],
            [kb_btn("📡 Pulsar", "w:y:pu"), kb_btn("💥 Supernovae", "w:y:sn")],
            [kb_btn("⭐ Doppie", "w:y:bi"), kb_btn("📸 Foto NASA", "st:nasa")],
            nav_row(),
        ]
    )


def costellazioni_keyboard() -> InlineKeyboardMarkup:
    extra = [
        [kb_btn("☀️ Del giorno", "co:day"), kb_btn("🚀 Enciclopedia", "world:mondi")],
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
            [kb_btn("🔬 Laboratorio", "pt:lab"), kb_btn("🧠 Giochi", "pt:game")],
            [kb_btn("🎒 Collezione", "pt:bag")],
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
            [kb_btn("⚖️ Confronta", f"pt:c1:{sid}"), kb_btn("🎲 Un'altra", "pt:rand")],
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
            [kb_btn("🧭 Ambienti", "pt:envs"), kb_btn("🏛️ Museo", "pt:mus")],
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
    grid.append([kb_btn("📸 Foto (centro, tavolo uniforme)", "pt:photo")])
    grid.append(nav_row())
    return InlineKeyboardMarkup(grid)


def pietre_oracle_keyboard(wiki_url: str | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if wiki_url:
        rows.append([InlineKeyboardButton("📖 Wikipedia", url=wiki_url)])
    rows.append([kb_btn("🔄 Estrai di nuovo", "pt:ora")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


def pietre_games_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🧠 Indovina", "pt:g:guess"), kb_btn("🪨 Vero o falso", "pt:g:tf")],
            [kb_btn("⚡ Quiz rapido", "pt:g:quiz")],
            nav_row(),
        ]
    )


def pietre_quiz_keyboard(n: int) -> InlineKeyboardMarkup:
    labels = ("A", "B", "C", "D")
    buttons = [kb_btn(labels[i], f"pt:ga:{i}") for i in range(min(n, 4))]
    return InlineKeyboardMarkup([buttons, nav_row()])
