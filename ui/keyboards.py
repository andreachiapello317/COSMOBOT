"""Tastiere Inline della home a sezioni e dei nuovi workflow."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def kb_btn(label: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=data)


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌌 Tema Natale", "natal:open"), kb_btn("🔮 Oroscopo", "home:oroscopo")],
            [kb_btn("🪐 Transiti", "home:transits")],
            [kb_btn("🃏 Tarocchi", "tarot:menu"), kb_btn("☯️ I Ching", "iching:open")],
            [kb_btn("🪶 Rune", "home:rune"), kb_btn("🔮 Ho una domanda", "home:domanda")],
            [kb_btn("🌙 Luna", "home:luna"), kb_btn("🪐 Pianeti", "home:pianeti")],
            [kb_btn("🛰️ ISS", "home:iss"), kb_btn("🔭 Cosa osservare", "home:osserva")],
            [kb_btn("📸 NASA APOD", "home:apod"), kb_btn("⭐ Stelle", "home:stelle")],
            [kb_btn("☀️ Sole", "home:sole"), kb_btn("🌠 Eventi", "home:eventi")],
            [kb_btn("✨ COSMICO", "home:cosmico"), kb_btn("🧭 Esplora", "home:esplora")],
        ]
    )


def esplora_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🔮 ME", "nav:me"), kb_btn("🃏 RISPOSTE", "nav:risposte")],
            [kb_btn("🌙 CIELO", "nav:cielo"), kb_btn("🚀 UNIVERSO", "nav:universo")],
            [kb_btn("✨ COSMICO", "home:cosmico")],
            [kb_btn("🏠 Home", "home:menu")],
        ]
    )


def nav_me_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌌 Tema Natale", "natal:open"), kb_btn("🪐 Transiti", "home:transits")],
            [kb_btn("🔮 Oroscopo", "home:oroscopo"), kb_btn("☄️ Asteroidi", "home:asteroidi")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def nav_risposte_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🃏 Tarocchi", "tarot:menu"), kb_btn("☯️ I Ching", "iching:open")],
            [kb_btn("🪶 Rune", "home:rune"), kb_btn("🔮 Ho una domanda", "home:domanda")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def nav_cielo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("🌙 Luna", "home:luna"), kb_btn("🪐 Pianeti", "home:pianeti")],
            [kb_btn("🔭 Osserva", "home:osserva"), kb_btn("🌠 Eventi", "home:eventi")],
            [kb_btn("🛰️ ISS", "home:iss"), kb_btn("☀️ Sole", "home:sole")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


def nav_universo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [kb_btn("📸 NASA APOD", "home:apod"), kb_btn("⭐ Stelle", "home:stelle")],
            [kb_btn("✨ Cosmico", "home:cosmico")],
            [kb_btn("🧭 Esplora", "home:esplora"), kb_btn("🏠 Home", "home:menu")],
        ]
    )


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
