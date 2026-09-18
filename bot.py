#!/usr/bin/env python3
"""
StelleBot — bot Telegram informativo (e un po' ironico) su oroscopo,
astrologia, pianeti, stelle e astronomia.

Tutto il contenuto "di fatto" arriva da API live. I testi fissi nel codice
sono solo interfaccia (comandi, etichette, messaggi di errore), mai oroscopi
o curiosità astronomiche inventate.

Avvio:
  - senza WEBHOOK_URL  -> polling (sviluppo locale)
  - con WEBHOOK_URL    -> webhook (produzione su Render)
"""

from __future__ import annotations

import asyncio
import html
import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------------------------
# Configurazione facile da cambiare
# ---------------------------------------------------------------------------

# Segno usato da /oroscopo quando l'utente non ne passa uno.
# Valori ammessi: aries, taurus, gemini, cancer, leo, virgo, libra,
# scorpio, sagittarius, capricorn, aquarius, pisces.
DEFAULT_SIGN = "libra"

# Coordinate di default per Luna e pianeti (Roma). L'Italia merita il suo cielo.
DEFAULT_LAT = 41.9028
DEFAULT_LON = 12.4964
DEFAULT_PLACE_NAME = "Roma"
DEFAULT_TZ = ZoneInfo("Europe/Rome")

# Messaggio unico quando un'API esterna non risponde.
STARS_OFFLINE = "Le stelle sono temporaneamente offline ✨ riprova tra poco"

# Timeout HTTP verso le API esterne (secondi).
HTTP_TIMEOUT = 18.0

# Cache breve: le API chiedono di non martellarle, i dati cambiano piano.
CACHE_TTL_SECONDS = 8 * 60

# Limite Telegram per un singolo messaggio di testo / caption foto.
TELEGRAM_MAX_LEN = 3900
TELEGRAM_CAPTION_MAX = 1024

# In chat_data: ultimo messaggio del bot, da sostituire al comando successivo.
LAST_BOT_MSG_KEY = "last_bot_msg"

USER_AGENT = "StelleBot/1.0 (Telegram; https://github.com; educational astrology bot)"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("stellebot")


class StelleOfflineError(RuntimeError):
    """Una (o più) API live non hanno risposto in modo utilizzabile."""


# ---------------------------------------------------------------------------
# Dizionari di etichette (UI, non contenuti astronomici)
# ---------------------------------------------------------------------------

# Chiave = nome inglese API. Valore = (nome italiano, emoji, alias accettati).
ZODIAC: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "aries": ("Ariete", "♈", ("ariete", "aries")),
    "taurus": ("Toro", "♉", ("toro", "taurus")),
    "gemini": ("Gemelli", "♊", ("gemelli", "gemini")),
    "cancer": ("Cancro", "♋", ("cancro", "cancer")),
    "leo": ("Leone", "♌", ("leone", "leo")),
    "virgo": ("Vergine", "♍", ("vergine", "virgo")),
    "libra": ("Bilancia", "♎", ("bilancia", "libra")),
    "scorpio": ("Scorpione", "♏", ("scorpione", "scorpio")),
    "sagittarius": ("Sagittario", "♐", ("sagittario", "sagittarius")),
    "capricorn": ("Capricorno", "♑", ("capricorno", "capricorn", "capricorno")),
    "aquarius": ("Acquario", "♒", ("acquario", "aquarius")),
    "pisces": ("Pesci", "♓", ("pesci", "pisces")),
}

PLANET_LABELS: dict[str, tuple[str, str]] = {
    "Sun": ("Sole", "☀️"),
    "Moon": ("Luna", "🌙"),
    "Mercury": ("Mercurio", "☿️"),
    "Venus": ("Venere", "♀️"),
    "Mars": ("Marte", "♂️"),
    "Jupiter": ("Giove", "♃"),
    "Saturn": ("Saturno", "♄"),
    "Uranus": ("Urano", "♅"),
    "Neptune": ("Nettuno", "♆"),
    "Pluto": ("Plutone", "♇"),
}

MAIN_PLANETS = (
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)

MOON_PHASE_IT = {
    "new moon": "Luna nuova",
    "waxing crescent": "Luna crescente",
    "first quarter": "Primo quarto",
    "waxing gibbous": "Gibbosa crescente",
    "full moon": "Luna piena",
    "waning gibbous": "Gibbosa calante",
    "last quarter": "Ultimo quarto",
    "third quarter": "Ultimo quarto",
    "waning crescent": "Luna calante",
}

MONTHS_IT = (
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
)

DIGNITY_IT = {
    "rulership": "in domicilio",
    "domicile": "in domicilio",
    "exaltation": "in esaltazione",
    "detriment": "in esilio",
    "fall": "in caduta",
    "neutral": "in transito",
}

SIGN_ORDER = tuple(ZODIAC.keys())

HOUSE_LABELS: dict[int, str] = {
    1: "Ascendente / identità",
    2: "Risorse",
    3: "Comunicazione",
    4: "Casa e famiglia",
    5: "Creatività",
    6: "Routine",
    7: "Relazioni",
    8: "Trasformazione",
    9: "Conoscenza",
    10: "Carriera",
    11: "Comunità",
    12: "Mondo interiore",
}

ASPECT_LABELS = {
    "conjunction": ("Congiunzione", "☌"),
    "opposition": ("Opposizione", "☍"),
    "trine": ("Trigono", "△"),
    "square": ("Quadratura", "□"),
    "sextile": ("Sestile", "⚹"),
}

SIGN_ELEMENT = {
    "aries": "fuoco",
    "leo": "fuoco",
    "sagittarius": "fuoco",
    "taurus": "terra",
    "virgo": "terra",
    "capricorn": "terra",
    "gemini": "aria",
    "libra": "aria",
    "aquarius": "aria",
    "cancer": "acqua",
    "scorpio": "acqua",
    "pisces": "acqua",
}

SIGN_MODALITY = {
    "aries": "cardinale",
    "cancer": "cardinale",
    "libra": "cardinale",
    "capricorn": "cardinale",
    "taurus": "fisso",
    "leo": "fisso",
    "scorpio": "fisso",
    "aquarius": "fisso",
    "gemini": "mutabile",
    "virgo": "mutabile",
    "sagittarius": "mutabile",
    "pisces": "mutabile",
}

PLANET_ROLES = {
    "Sun": "identità e ciò che vuoi esprimere",
    "Moon": "mondo emotivo, bisogni, reazioni",
    "Mercury": "mente, parole, come ragioni",
    "Venus": "gusto, affetti, cosa ti attira",
    "Mars": "slancio, rabbia, come agisci",
    "Jupiter": "crescita, fortuna, dove allarghi",
    "Saturn": "limiti, dovere, dove maturi",
    "Uranus": "rotture, originalità, scosse",
    "Neptune": "sogni, nebbia, ispirazione",
    "Pluto": "potere, crisi, trasformazioni profonde",
}

NATAL_STATE_KEY = "natal_flow"
NATAL_PROFILE_PATH = Path("data/natal_profiles.json")
_natal_profile_lock = asyncio.Lock()

# Alias rapido: "vergine" -> "virgo"
_SIGN_ALIASES: dict[str, str] = {}
for _en, (_it, _emoji, _aliases) in ZODIAC.items():
    _SIGN_ALIASES[_en] = _en
    _SIGN_ALIASES[_it.lower()] = _en
    for _alias in _aliases:
        _SIGN_ALIASES[_alias.lower()] = _en


# ---------------------------------------------------------------------------
# Cache in memoria (processo)
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[float, Any]] = {}


def cache_get(key: str) -> Any | None:
    item = _cache.get(key)
    if not item:
        return None
    ts, value = item
    if time.monotonic() - ts > CACHE_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return value


def cache_set(key: str, value: Any) -> Any:
    _cache[key] = (time.monotonic(), value)
    return value


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _http_client(context: ContextTypes.DEFAULT_TYPE | None = None) -> httpx.AsyncClient:
    if context is not None:
        client = context.bot_data.get("http")
        if client is not None:
            return client
    raise StelleOfflineError("client HTTP non inizializzato")


async def fetch_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    """GET/POST JSON. Solleva StelleOfflineError su timeout, HTTP != 2xx, JSON rotto."""
    try:
        response = await client.request(
            method,
            url,
            params=params,
            json=json_body,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        logger.warning("Timeout API: %s", url)
        raise StelleOfflineError("timeout") from None
    except httpx.HTTPStatusError as exc:
        logger.warning("HTTP %s da %s: %s", exc.response.status_code, url, exc.response.text[:300])
        raise StelleOfflineError(f"http {exc.response.status_code}") from exc
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Errore rete/JSON su %s: %s", url, exc)
        raise StelleOfflineError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Traduzione EN -> IT (i feed NASA / CosmyDay / oroscopo arrivano in inglese)
# ---------------------------------------------------------------------------


def _split_for_translation(text: str, max_len: int = 1400) -> list[str]:
    text = text.strip()
    if len(text) <= max_len:
        return [text]
    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= max_len:
            chunks.append(remaining)
            break
        window = remaining[: max_len + 1]
        cut = max(window.rfind(". "), window.rfind(".\n"), window.rfind("? "), window.rfind("! "))
        if cut < max_len * 0.4:
            cut = window.rfind(" ")
        if cut < 1:
            cut = max_len
        chunks.append(remaining[: cut + 1].strip())
        remaining = remaining[cut + 1 :].strip()
    return [c for c in chunks if c]


async def _translate_google(client: httpx.AsyncClient, text: str) -> str | None:
    try:
        response = await client.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "en", "tl": "it", "dt": "t", "q": text},
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        parts = [part[0] for part in data[0] if part and part[0]]
        translated = "".join(parts).strip()
        return translated or None
    except Exception as exc:  # noqa: BLE001 — fallback su un altro servizio
        logger.info("Traduzione Google non disponibile: %s", exc)
        return None


async def _translate_mymemory(client: httpx.AsyncClient, text: str) -> str | None:
    try:
        data = await fetch_json(
            client,
            "https://api.mymemory.translated.net/get",
            params={"q": text[:450], "langpair": "en|it"},
        )
        translated = (data.get("responseData") or {}).get("translatedText") or ""
        translated = html.unescape(translated).strip()
        if not translated or "MYMEMORY WARNING" in translated.upper():
            return None
        return translated
    except StelleOfflineError as exc:
        logger.info("Traduzione MyMemory non disponibile: %s", exc)
        return None


async def translate_to_italian(client: httpx.AsyncClient, text: str) -> str:
    """Traduce testo inglese in italiano. Se i traduttori falliscono, restituisce l'originale."""
    clean = strip_markup(text).strip()
    if not clean:
        return ""
    cache_key = f"tr:{hash(clean)}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    pieces: list[str] = []
    for chunk in _split_for_translation(clean):
        translated = await _translate_google(client, chunk)
        if not translated:
            translated = await _translate_mymemory(client, chunk)
        pieces.append(translated or chunk)

    result = " ".join(pieces).strip()
    result = _fix_known_terms(result)
    return cache_set(cache_key, result)


# Correzioni di vocabolario astronomico: i traduttori automatici scambiano
# "quarter" lunare con il trimestre fiscale. Non sono fatti, solo etichette.
_TERM_FIXES = (
    (re.compile(r"\bprimo trimestre\b", re.IGNORECASE), "primo quarto"),
    (re.compile(r"\bsecondo trimestre\b", re.IGNORECASE), "secondo quarto"),
    (re.compile(r"\bterzo trimestre\b", re.IGNORECASE), "ultimo quarto"),
    (re.compile(r"\bultimo trimestre\b", re.IGNORECASE), "ultimo quarto"),
)


def _fix_known_terms(text: str) -> str:
    for pattern, repl in _TERM_FIXES:
        text = pattern.sub(repl, text)
    return text


def strip_markup(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1 (\2)", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Formattazione
# ---------------------------------------------------------------------------


def e(text: Any) -> str:
    """Escape HTML per Telegram."""
    return html.escape(str(text), quote=False)


def format_date_it(value: str | None) -> str:
    if not value:
        return datetime.now(DEFAULT_TZ).strftime("%d/%m/%Y")
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, month = value.split("-")
        month_i = int(month)
        if 1 <= month_i <= 12:
            return f"{MONTHS_IT[month_i - 1]} {year}"
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%B %d, %Y", "%b %d, %Y"):
        try:
            dt = datetime.strptime(value[:19], fmt)
            return f"{dt.day} {MONTHS_IT[dt.month - 1]} {dt.year}"
        except ValueError:
            continue
    return value


def format_degree(value: float) -> str:
    deg = int(value)
    minutes = int(round((value - deg) * 60))
    if minutes == 60:
        deg += 1
        minutes = 0
    return f"{deg}°{minutes:02d}′"


def moon_phase_label(name: str | None) -> str:
    if not name:
        return "fase sconosciuta"
    return MOON_PHASE_IT.get(name.replace("_", " ").strip().lower(), name)


def sign_label(english: str | None) -> str:
    if not english:
        return "—"
    key = english.strip().lower()
    if key in ZODIAC:
        it, emoji, _ = ZODIAC[key]
        return f"{emoji} {it}"
    return english


def normalize_sign(raw: str | None) -> str | None:
    """Restituisce la chiave inglese (es. 'virgo') oppure None se non è un segno."""
    if not raw:
        return None
    cleaned = raw.strip().lower()
    cleaned = cleaned.replace("segno dello", "").replace("segno della", "")
    cleaned = cleaned.replace("segno dei", "").replace("segno ", "")
    cleaned = cleaned.replace("oroscopo di", "").replace("oroscopo", "")
    cleaned = cleaned.replace("il ", "").replace("la ", "").replace("i ", "")
    cleaned = re.sub(r"[^a-zàèéìòù]", "", cleaned)
    return _SIGN_ALIASES.get(cleaned)


def list_signs_help() -> str:
    parts = [f"{emoji} {it}" for _en, (it, emoji, _a) in ZODIAC.items()]
    return ", ".join(parts)


# Periodi oroscopo (stessi path dell'API live).
HORO_PERIODS: dict[str, dict[str, str]] = {
    "daily": {
        "it": "giornaliero",
        "title": "Oroscopo di oggi",
        "button": "📅 Giorno",
    },
    "weekly": {
        "it": "settimanale",
        "title": "Oroscopo della settimana",
        "button": "🗓 Settimana",
    },
    "monthly": {
        "it": "mensile",
        "title": "Oroscopo del mese",
        "button": "📆 Mese",
    },
}

_PERIOD_ALIASES: dict[str, str] = {
    "daily": "daily",
    "giornaliero": "daily",
    "giorno": "daily",
    "oggi": "daily",
    "day": "daily",
    "weekly": "weekly",
    "settimanale": "weekly",
    "settimana": "weekly",
    "week": "weekly",
    "monthly": "monthly",
    "mensile": "monthly",
    "mese": "monthly",
    "month": "monthly",
}

EMPTY_KEYBOARD = InlineKeyboardMarkup([])


def normalize_period(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = re.sub(r"[^a-zàèéìòù]", "", raw.strip().lower())
    return _PERIOD_ALIASES.get(cleaned)


def parse_oroscopo_query(raw: str) -> tuple[str | None, str | None, bool]:
    """Estrae (segno inglese | None se invalido, periodo | None, usato default)."""
    tokens = raw.strip().split()
    period: str | None = None
    sign_parts: list[str] = []
    for tok in tokens:
        maybe_period = normalize_period(tok)
        if maybe_period:
            period = maybe_period
        else:
            sign_parts.append(tok)
    sign_raw = " ".join(sign_parts).strip()
    used_default = not sign_raw
    if used_default:
        return DEFAULT_SIGN, period, True
    return normalize_sign(sign_raw), period, False


def oroscopo_keyboard(sign: str, selected: str | None = None) -> InlineKeyboardMarkup:
    row: list[InlineKeyboardButton] = []
    for key, meta in HORO_PERIODS.items():
        label = meta["button"]
        if selected == key:
            label = f"✓ {label}"
        row.append(InlineKeyboardButton(label, callback_data=f"horo:{sign}:{key}"))
    return InlineKeyboardMarkup([row])


def format_horoscope_when(period: str, date_value: str) -> str:
    pretty = format_date_it(date_value)
    if period == "weekly":
        return f"settimana dal {pretty}"
    return pretty


TAROT_SPREADS: dict[str, dict[str, Any]] = {
    "one": {
        "count": 1,
        "include_minor": False,
        "button": "🔹 1 carta",
        "title": "Energia del momento",
        "positions": ("Energia del momento",),
        "ritual": "Una sola carta, un'indicazione. Pensa a ciò che senti adesso.",
    },
    "three": {
        "count": 3,
        "include_minor": True,
        "button": "🔹 3 carte",
        "title": "Situazione · Ostacolo · Direzione",
        "positions": ("Situazione", "Ostacolo", "Direzione"),
        "ritual": "Tre carte: dove sei, cosa ostacola, dove puoi andare. Non serve scrivere la situazione.",
    },
    "love": {
        "count": 3,
        "include_minor": True,
        "button": "❤️ Amore",
        "title": "Tu · L'altra persona · La dinamica",
        "positions": ("Tu", "L'altra persona", "La dinamica"),
        "ritual": "Tre carte sul legame: tu, l'altra persona, la dinamica in mezzo.",
    },
    "work": {
        "count": 3,
        "include_minor": True,
        "button": "💼 Lavoro",
        "title": "Situazione · Sfida · Sviluppo",
        "positions": ("Situazione", "Sfida", "Possibile sviluppo"),
        "ritual": "Tre carte sul lavoro: il quadro, la sfida, un possibile sviluppo.",
    },
    "ask": {
        "count": 3,
        "include_minor": True,
        "button": "❓ Domanda",
        "title": "Lettura sulla tua domanda",
        "positions": ("Nocciolo", "Ostacolo", "Indicazione"),
        "ritual": "Ho la tua domanda. Concentrati su ciò che vuoi comprendere, poi pesca.",
    },
}

TAROT_STATE_KEY = "tarot_flow"
TAROT_HISTORY_MAX = 12
TAROT_HISTORY_PATH = Path("data/tarot_history.json")
_tarot_history_lock = asyncio.Lock()

MAJOR_CARD_EMOJI = {
    "the fool": "🃏",
    "the magician": "🪄",
    "the high priestess": "🔮",
    "the empress": "👑",
    "the emperor": "🏛️",
    "the hierophant": "📿",
    "the lovers": "💕",
    "the chariot": "🏇",
    "strength": "🦁",
    "the hermit": "🏮",
    "wheel of fortune": "☸️",
    "justice": "⚖️",
    "the hanged man": "🪢",
    "death": "🦋",
    "temperance": "🍷",
    "the devil": "😈",
    "the tower": "🗼",
    "the star": "⭐",
    "the moon": "🌙",
    "the sun": "☀️",
    "judgement": "📯",
    "judgment": "📯",
    "the world": "🌍",
}


def tarot_card_emoji(name: str) -> str:
    key = re.sub(r"\s+", " ", name.lower().strip())
    if key in MAJOR_CARD_EMOJI:
        return MAJOR_CARD_EMOJI[key]
    if "wand" in key:
        return "🔥"
    if "cup" in key:
        return "💧"
    if "sword" in key:
        return "⚔️"
    if "pentacle" in key or "coin" in key:
        return "🪙"
    return "🃏"


def _tarot_btn(label: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=data)


def tarot_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_tarot_btn("🔹 1 carta", "tarot:pick:one"), _tarot_btn("🔹 3 carte", "tarot:pick:three")],
            [_tarot_btn("❤️ Amore", "tarot:pick:love"), _tarot_btn("💼 Lavoro", "tarot:pick:work")],
            [_tarot_btn("❓ Domanda", "tarot:pick:ask")],
            [_tarot_btn("📖 Storico", "tarot:hist")],
        ]
    )


def tarot_draw_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_tarot_btn("🔮 PESCA LE CARTE", "tarot:draw")]])


def tarot_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_tarot_btn("🃏 Nuova lettura", "tarot:menu"), _tarot_btn("📖 Storico", "tarot:hist")]]
    )


def _tarot_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(TAROT_STATE_KEY, None)


def _tarot_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(TAROT_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[TAROT_STATE_KEY] = state
    return state


def _history_load() -> dict[str, Any]:
    if not TAROT_HISTORY_PATH.exists():
        return {}
    try:
        data = json.loads(TAROT_HISTORY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _history_save(data: dict[str, Any]) -> None:
    TAROT_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    TAROT_HISTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def tarot_history_add(user_id: int, entry: dict[str, Any]) -> None:
    async with _tarot_history_lock:
        data = _history_load()
        key = str(user_id)
        rows = data.get(key)
        if not isinstance(rows, list):
            rows = []
        rows.insert(0, entry)
        data[key] = rows[:TAROT_HISTORY_MAX]
        _history_save(data)


async def tarot_history_list(user_id: int) -> list[dict[str, Any]]:
    async with _tarot_history_lock:
        rows = _history_load().get(str(user_id), [])
    return rows if isinstance(rows, list) else []


def _natal_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(NATAL_STATE_KEY, None)


def _flows_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    _tarot_reset(context)
    _natal_reset(context)


def _natal_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(NATAL_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[NATAL_STATE_KEY] = state
    return state


def lon_to_sign(lon: float) -> tuple[str, float]:
    lon = float(lon) % 360.0
    idx = int(lon // 30) % 12
    return SIGN_ORDER[idx], lon % 30


def parse_birth_date(raw: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"\s*(\d{1,2})[./-](\d{1,2})[./-](\d{4})\s*", raw)
    if not match:
        return None
    day, month, year = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    try:
        datetime(year, month, day)
    except ValueError:
        return None
    if year < 1800 or year > datetime.now(DEFAULT_TZ).year:
        return None
    return year, month, day


def parse_birth_time(raw: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"\s*(\d{1,2})[:.](\d{2})\s*", raw)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour > 23 or minute > 59:
        return None
    return hour, minute


def format_birth_date(year: int, month: int, day: int) -> str:
    return f"{day} {MONTHS_IT[month - 1]} {year}"


def element_bar(counts: dict[str, int], key: str, width: int = 10) -> str:
    total = sum(counts.values()) or 1
    filled = min(width, round(width * counts.get(key, 0) / total))
    return "█" * filled + "░" * (width - filled)


def natal_nav_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_tarot_btn("🪐 Pianeti", "natal:planets"), _tarot_btn("🏠 Case", "natal:houses")],
            [_tarot_btn("⚡ Aspetti", "natal:aspects"), _tarot_btn("❤️ Amore", "natal:love")],
            [_tarot_btn("🔮 Lettura", "natal:read"), _tarot_btn("📊 Profilo", "natal:elements")],
            [_tarot_btn("👤 Il mio tema", "natal:me"), _tarot_btn("🏠 Home", "natal:homebtn")],
        ]
    )


def _profile_load() -> dict[str, Any]:
    if not NATAL_PROFILE_PATH.exists():
        return {}
    try:
        data = json.loads(NATAL_PROFILE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _profile_save(data: dict[str, Any]) -> None:
    NATAL_PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    NATAL_PROFILE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def natal_profile_get(user_id: int) -> dict[str, Any] | None:
    async with _natal_profile_lock:
        row = _profile_load().get(str(user_id))
    return row if isinstance(row, dict) else None


async def natal_profile_set(user_id: int, profile: dict[str, Any]) -> None:
    async with _natal_profile_lock:
        data = _profile_load()
        data[str(user_id)] = profile
        _profile_save(data)


# ---------------------------------------------------------------------------
# API live
# ---------------------------------------------------------------------------


async def api_horoscope(
    client: httpx.AsyncClient,
    sign: str,
    period: str = "daily",
) -> dict[str, Any]:
    if period not in HORO_PERIODS:
        period = "daily"
    now = datetime.now(DEFAULT_TZ)
    if period == "monthly":
        bucket = now.strftime("%Y-%m")
    elif period == "weekly":
        bucket = now.strftime("%Y-%W")
    else:
        bucket = str(now.date())
    cache_key = f"horo:{period}:{sign}:{bucket}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(
        client,
        f"https://freehoroscopeapi.com/api/v1/get-horoscope/{period}",
        params={"sign": sign},
    )
    payload = data.get("data") if isinstance(data, dict) else None
    if not isinstance(payload, dict) or not payload.get("horoscope"):
        raise StelleOfflineError("oroscopo vuoto")
    return cache_set(cache_key, payload)


async def api_tarot_draw(
    client: httpx.AsyncClient,
    *,
    count: int = 1,
    include_minor: bool = False,
) -> list[dict[str, Any]]:
    """Pesca live da freehoroscopeapi. Nessuna cache: ogni pesca è nuova."""
    params: dict[str, Any] = {"n": count}
    if include_minor:
        params["minor"] = "true"
    data = await fetch_json(
        client,
        "https://freehoroscopeapi.com/api/v1/tarot/cards/random",
        params=params,
    )
    cards = data.get("cards") if isinstance(data, dict) else None
    if not isinstance(cards, list) or not cards:
        raise StelleOfflineError("mazzo vuoto")
    return cards


async def api_moon_observatory(client: httpx.AsyncClient) -> dict[str, Any]:
    cache_key = f"moon-obs:{datetime.now(DEFAULT_TZ).date()}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(
        client,
        "https://api.sunrisesunset.io/json",
        params={
            "lat": DEFAULT_LAT,
            "lng": DEFAULT_LON,
            "timezone": "Europe/Rome",
            "date": "today",
        },
    )
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, dict) or data.get("status") != "OK":
        raise StelleOfflineError("dati lunari assenti")
    return cache_set(cache_key, results)


async def api_moon_story(client: httpx.AsyncClient) -> dict[str, Any]:
    cache_key = f"moon-story:{datetime.now(DEFAULT_TZ).date()}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(client, "https://api.cosmyday.com/content/moon")
    if not isinstance(data, dict) or not data.get("content"):
        raise StelleOfflineError("articolo luna vuoto")
    return cache_set(cache_key, data)


async def api_planets_now(client: httpx.AsyncClient) -> dict[str, Any]:
    now = datetime.now(DEFAULT_TZ)
    bucket = now.replace(minute=(now.minute // 10) * 10, second=0, microsecond=0)
    cache_key = f"natal:{bucket.isoformat(timespec='minutes')}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(
        client,
        "https://api.cosmyday.com/natal",
        method="POST",
        json_body={
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "lat": DEFAULT_LAT,
            "lon": DEFAULT_LON,
        },
    )
    planets = data.get("planets") if isinstance(data, dict) else None
    if not isinstance(planets, dict):
        raise StelleOfflineError("efemeridi vuote")
    return cache_set(cache_key, data)


async def api_geocode_place(client: httpx.AsyncClient, query: str) -> list[dict[str, Any]]:
    data = await fetch_json(
        client,
        "https://api.cosmyday.com/search-location",
        params={"q": query},
    )
    if not isinstance(data, list) or not data:
        raise StelleOfflineError("luogo non trovato")
    places: list[dict[str, Any]] = []
    for item in data[:5]:
        if not isinstance(item, dict):
            continue
        try:
            lat = float(item.get("lat"))
            lon = float(item.get("lon"))
        except (TypeError, ValueError):
            continue
        address = item.get("address") if isinstance(item.get("address"), dict) else {}
        places.append(
            {
                "name": str(item.get("name") or query),
                "display": str(item.get("display_name") or item.get("name") or query),
                "lat": lat,
                "lon": lon,
                "country": str(address.get("country") or ""),
                "kind": str(item.get("addresstype") or ""),
            }
        )
    if not places:
        raise StelleOfflineError("luogo non trovato")
    return places


async def api_natal_chart(
    client: httpx.AsyncClient,
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float,
) -> dict[str, Any]:
    data = await fetch_json(
        client,
        "https://api.cosmyday.com/natal",
        method="POST",
        json_body={
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "lat": lat,
            "lon": lon,
        },
    )
    if not isinstance(data, dict) or not isinstance(data.get("planets"), dict):
        raise StelleOfflineError("tema natale vuoto")
    return data


async def api_transit_note(client: httpx.AsyncClient) -> dict[str, Any] | None:
    cache_key = f"transit:{datetime.now(DEFAULT_TZ).date()}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        data = await fetch_json(client, "https://api.cosmyday.com/content/transit")
    except StelleOfflineError:
        return None
    if not isinstance(data, dict):
        return None
    return cache_set(cache_key, data)


def _nasa_key() -> str:
    return os.getenv("NASA_API_KEY", "DEMO_KEY").strip() or "DEMO_KEY"


async def api_apod(client: httpx.AsyncClient, *, random: bool = False) -> dict[str, Any]:
    params: dict[str, Any] = {"api_key": _nasa_key()}
    if random:
        params["count"] = 1
        cache_key = None  # una curiosità nuova ogni richiesta
    else:
        cache_key = f"apod:{datetime.now(DEFAULT_TZ).date()}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

    data = await fetch_json(
        client,
        "https://api.nasa.gov/planetary/apod",
        params=params,
    )
    if isinstance(data, list):
        if not data:
            raise StelleOfflineError("apod vuoto")
        data = data[0]
    if not isinstance(data, dict) or not data.get("title"):
        raise StelleOfflineError("apod non valido")
    if cache_key:
        return cache_set(cache_key, data)
    return data


# ---------------------------------------------------------------------------
# Telegram helpers — un solo messaggio per chat, sempre sostituito
# ---------------------------------------------------------------------------


def clip_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


async def send_typing(update: Update) -> None:
    if update.effective_chat:
        try:
            await update.effective_chat.send_action(ChatAction.TYPING)
        except TelegramError:
            pass


def _last_bot_msg(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any] | None:
    last = context.chat_data.get(LAST_BOT_MSG_KEY)
    return last if isinstance(last, dict) and "id" in last else None


def _remember_bot_msg(context: ContextTypes.DEFAULT_TYPE, message_id: int, kind: str) -> None:
    context.chat_data[LAST_BOT_MSG_KEY] = {"id": message_id, "kind": kind}


async def _delete_last_bot_msg(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    last = _last_bot_msg(context)
    if not last:
        return
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=int(last["id"]))
    except TelegramError:
        pass
    context.chat_data.pop(LAST_BOT_MSG_KEY, None)


def _is_not_modified(exc: TelegramError) -> bool:
    return "not modified" in str(exc).lower()


async def delete_user_command(update: Update) -> None:
    """Cancella il comando dell'utente dopo una risposta riuscita.

    Non tocca i tap sui bottoni (sarebbe il messaggio del bot) e ignora
    i casi in cui Telegram non ci lascia cancellare (gruppo senza privilegi).
    """
    if update.callback_query is not None:
        return
    message = update.effective_message
    if message is None:
        return
    try:
        await message.delete()
    except TelegramError as exc:
        logger.info("Comando utente non cancellato: %s", exc)


async def deliver_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    *,
    preview: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Invia un testo, oppure modifica l'ultimo messaggio del bot in questa chat."""
    chat = update.effective_chat
    if chat is None:
        return
    text = clip_text(text, TELEGRAM_MAX_LEN)
    last = _last_bot_msg(context)
    # Sempre esplicito: se ometti reply_markup Telegram lascia i bottoni vecchi.
    markup = reply_markup if reply_markup is not None else EMPTY_KEYBOARD

    if last and last.get("kind") == "text":
        try:
            await context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=int(last["id"]),
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=not preview,
                reply_markup=markup,
            )
            return
        except TelegramError as exc:
            if _is_not_modified(exc):
                return
            logger.info("Modifica testo non riuscita, sostituisco il messaggio: %s", exc)

    await _delete_last_bot_msg(context, chat.id)
    sent = await context.bot.send_message(
        chat_id=chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=not preview,
        reply_markup=markup,
    )
    _remember_bot_msg(context, sent.message_id, "text")


async def deliver_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    photo_url: str,
    caption: str,
) -> bool:
    """Sostituisce l'ultimo messaggio con una foto. False se Telegram rifiuta la foto."""
    chat = update.effective_chat
    if chat is None:
        return False
    caption = clip_text(caption, TELEGRAM_CAPTION_MAX)
    last = _last_bot_msg(context)
    media = InputMediaPhoto(media=photo_url, caption=caption, parse_mode=ParseMode.HTML)

    if last and last.get("kind") == "photo":
        try:
            await context.bot.edit_message_media(
                chat_id=chat.id,
                message_id=int(last["id"]),
                media=media,
            )
            return True
        except TelegramError as exc:
            if _is_not_modified(exc):
                return True
            logger.info("Modifica foto non riuscita, sostituisco il messaggio: %s", exc)

    await _delete_last_bot_msg(context, chat.id)
    try:
        sent = await context.bot.send_photo(
            chat_id=chat.id,
            photo=photo_url,
            caption=caption,
            parse_mode=ParseMode.HTML,
        )
    except TelegramError:
        logger.warning("Impossibile inviare la foto APOD, resto sul testo")
        return False
    _remember_bot_msg(context, sent.message_id, "photo")
    return True


async def reply_html(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    *,
    preview: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await deliver_text(update, context, text, preview=preview, reply_markup=reply_markup)


async def reply_offline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(update, context, STARS_OFFLINE)


async def show_loading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Riusa lo stesso messaggio mentre arrivano i dati live."""
    await deliver_text(update, context, "⏳ Un attimo, sto interrogando il cielo…")


def start_text() -> str:
    default_it, default_emoji, _ = ZODIAC[DEFAULT_SIGN]
    return (
        "✨ <b>StelleBot</b> è online.\n\n"
        "Sono un piccolo osservatorio tascabile: oroscopi del giorno, Luna, "
        "pianeti e foto NASA, tutti pescati da API live. Zero oroscopi da "
        "calendario del 2014, promesso.\n\n"
        "Tono da planetario un po' ironico, non da biglietto di San Valentino.\n\n"
        f"Se non mi dici un segno, uso {default_emoji} <b>{default_it}</b> "
        f"(costante <code>DEFAULT_SIGN</code>).\n\n"
        "<b>Comandi</b>\n"
        "• /tema — tema natale guidato (data, ora, luogo)\n"
        "• /oroscopo [segno] — poi scegli giorno, settimana o mese\n"
        "• /tarocchi — lettura guidata: 1 carta, 3 carte, amore, lavoro, domanda\n"
        "• /luna — fase lunare di oggi\n"
        "• /pianeti — dove sono i pianeti adesso\n"
        "• /apod — Astronomy Picture of the Day (NASA)\n"
        "• /stelle — una curiosità astronomica live\n"
        "• /aiuto — la mappa dei comandi\n\n"
        "Puoi anche scrivere solo il nome di un segno, tipo <i>vergine</i>.\n"
        "Ora alza lo sguardo. O almeno il pollice."
    )


def help_text() -> str:
    default_it, default_emoji, _ = ZODIAC[DEFAULT_SIGN]
    return (
        "📚 <b>Manuale di sopravvivenza cosmica</b>\n\n"
        "/start — presentazione (e un po' di pepe)\n"
        "/tema — tema natale: data, ora, luogo, poi Big Three / pianeti / case\n"
        f"/oroscopo [segno] — oroscopo live. Senza segno uso "
        f"{default_emoji} {default_it}. Poi i bottoni: giorno, settimana, mese. "
        f"Segni: {e(list_signs_help())}\n"
        "/luna — fase, illuminazione, alba/tramonto della Luna su Roma\n"
        "/tarocchi — lettura guidata (1 carta, 3 carte, amore, lavoro, domanda)\n"
        "/pianeti — posizioni attuali (efemeridi CosmyDay / Swiss Ephemeris)\n"
        "/apod — immagine (o video) astronomica del giorno, NASA\n"
        "/stelle — una scheda NASA a caso, tradotta al volo\n"
        "/aiuto — questo messaggio\n\n"
        "Scrivere solo «bilancia» o «Vergine» vale come /oroscopo.\n\n"
        "Se un'API fa i capricci sentirai: "
        f"<i>{e(STARS_OFFLINE)}</i>"
    )


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await reply_html(update, context, start_text(), reply_markup=home_keyboard())
    await delete_user_command(update)


async def cmd_aiuto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await reply_html(update, context, help_text())
    await delete_user_command(update)


async def cmd_oroscopo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args) if context.args else ""
    await begin_oroscopo(update, context, raw)


async def begin_oroscopo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raw: str,
) -> None:
    _flows_reset(context)
    sign, period, used_default = parse_oroscopo_query(raw)
    if sign is None:
        await reply_html(
            update,
            context,
            "Hmm, quel segno non è sulla ruota dello zodiaco che conosco.\n"
            f"Prova uno di questi: {e(list_signs_help())}",
        )
        return
    if period:
        await send_oroscopo_period(update, context, sign, period, used_default=used_default)
        return
    await show_oroscopo_picker(update, context, sign, used_default=used_default)


async def show_oroscopo_picker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    sign: str,
    *,
    used_default: bool,
) -> None:
    it_name, emoji, _ = ZODIAC[sign]
    text = (
        f"{emoji} <b>Oroscopo — {e(it_name)}</b>\n\n"
        "Quale cielo vuoi consultare?\n"
        "Giorno, settimana o mese: tocca un bottone, i dati arrivano live."
    )
    if used_default:
        text += (
            f"\n\n<i>Nessun segno indicato: uso {e(it_name)} "
            f"(<code>DEFAULT_SIGN</code>).</i>"
        )
    await reply_html(
        update,
        context,
        text,
        reply_markup=oroscopo_keyboard(sign),
    )
    await delete_user_command(update)


async def send_oroscopo_period(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    sign: str,
    period: str,
    *,
    used_default: bool = False,
) -> None:
    await send_typing(update)
    await show_loading(update, context)
    it_name, emoji, _ = ZODIAC[sign]
    meta = HORO_PERIODS[period]
    client = _http_client(context)

    try:
        payload = await api_horoscope(client, sign, period)
        text_en = str(payload.get("horoscope") or "")
        text_it = await translate_to_italian(client, text_en)
        when = format_horoscope_when(period, str(payload.get("date") or ""))
    except StelleOfflineError:
        logger.exception("Oroscopo %s non disponibile per %s", period, sign)
        await reply_offline(update, context)
        return

    header = f"{emoji} <b>{e(meta['title'])} — {e(it_name)}</b>\n📅 {e(when)}"
    if used_default:
        header += (
            f"\n<i>Nessun segno indicato: uso il default {e(it_name)} "
            f"(<code>DEFAULT_SIGN</code>).</i>"
        )
    body = (
        f"{header}\n\n{e(text_it)}\n\n"
        "<i>Dati live da freehoroscopeapi.com · traduzione automatica.</i>\n"
        "<i>Cambia periodo con i bottoni sotto.</i>"
    )
    await reply_html(
        update,
        context,
        body,
        reply_markup=oroscopo_keyboard(sign, selected=period),
    )
    await delete_user_command(update)


async def on_oroscopo_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    parts = query.data.split(":")
    if len(parts) != 3 or parts[0] != "horo":
        await query.answer("Bottone stanco. Riprova con /oroscopo.")
        return
    _, sign, period = parts
    if sign not in ZODIAC or period not in HORO_PERIODS:
        await query.answer("Segno o periodo sconosciuto.")
        return
    await query.answer()
    if query.message is not None:
        kind = "text" if query.message.text else "photo"
        _remember_bot_msg(context, query.message.message_id, kind)
    await send_oroscopo_period(update, context, sign, period)


async def cmd_tarocchi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args).strip().lower() if context.args else ""
    shortcut = {
        "1": "one",
        "una": "one",
        "carta": "one",
        "3": "three",
        "tre": "three",
        "amore": "love",
        "love": "love",
        "lavoro": "work",
        "work": "work",
        "domanda": "ask",
        "ask": "ask",
    }.get(raw)
    if shortcut == "ask":
        await show_tarot_ask_prompt(update, context)
    elif shortcut:
        await show_tarot_ritual(update, context, shortcut)
    else:
        await show_tarot_menu(update, context)
    await delete_user_command(update)


async def show_tarot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    text = (
        "🔮 <b>Lettura dei Tarocchi</b>\n\n"
        "Concentrati sulla domanda che vuoi portare alle carte.\n"
        "Il mazzo è live (78 carte, Rider–Waite). I significati arrivano dall'API; "
        "dritta o capovolta la decide il mazzo quando peschi.\n\n"
        "✨ <b>Scegli il tipo di lettura</b>\n"
        "🔹 <b>1 carta</b> — energia / indicazione del momento\n"
        "🔹 <b>3 carte</b> — situazione / ostacolo / direzione\n"
        "❤️ <b>Amore</b> — tu / l'altra persona / dinamica\n"
        "💼 <b>Lavoro</b> — situazione / sfida / possibile sviluppo\n"
        "❓ <b>Domanda</b> — tre carte sulla tua domanda"
    )
    await reply_html(update, context, text, reply_markup=tarot_menu_keyboard())


async def show_tarot_ask_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _tarot_state(context)
    state.clear()
    state["spread"] = "ask"
    state["awaiting_question"] = True
    text = (
        "🔮 <b>Qual è la tua domanda?</b>\n\n"
        "Scrivila in un messaggio. Resta tra te e le carte: serve solo a "
        "incorniciare i significati ufficiali, non la mando in giro."
    )
    await reply_html(update, context, text)


async def show_tarot_ritual(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    spread: str,
    *,
    question: str | None = None,
) -> None:
    if spread not in TAROT_SPREADS:
        spread = "three"
    meta = TAROT_SPREADS[spread]
    state = _tarot_state(context)
    state["spread"] = spread
    state["awaiting_question"] = False
    if question:
        state["question"] = question
    elif spread != "ask":
        state.pop("question", None)
    text = (
        f"🃏 <b>{e(meta['title'])}</b>\n\n"
        f"{e(meta['ritual'])}\n\n"
    )
    if state.get("question"):
        text += f"<b>Domanda:</b> <i>{e(state['question'])}</i>\n\n"
    text += "Quando sei pronto, premi il bottone."
    await reply_html(update, context, text, reply_markup=tarot_draw_keyboard())


async def receive_tarot_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    question: str,
) -> None:
    question = clip_text(question.strip(), 400)
    if not question:
        await reply_html(
            update,
            context,
            "Ho bisogno di una domanda scritta, anche breve. Riprova.",
        )
        return
    await show_tarot_ritual(update, context, "ask", question=question)
    await delete_user_command(update)


async def _orient_and_translate_card(
    client: httpx.AsyncClient,
    card: dict[str, Any],
    position: str,
) -> dict[str, str]:
    name_en = str(card.get("name") or "Unnamed card")
    reversed_card = bool(random.choice((False, True)))
    meaning_en = str(card.get("meaning_rev" if reversed_card else "meaning_up") or "")
    name_it = await translate_to_italian(client, name_en)
    framed = (
        f"For the position '{position}', the card {name_en} "
        f"({'reversed' if reversed_card else 'upright'}) traditionally means: {meaning_en}"
    )
    meaning_it = await translate_to_italian(client, framed) if meaning_en else "—"
    return {
        "name_en": name_en,
        "name_it": name_it,
        "position": position,
        "kind": "Arcano maggiore" if str(card.get("type") or "") == "major" else "Arcano minore",
        "reversed": "1" if reversed_card else "0",
        "emoji": tarot_card_emoji(name_en),
        "meaning_it": meaning_it,
        "meaning_en": meaning_en,
    }


async def _tarot_synthesis(client: httpx.AsyncClient, drawn: list[dict[str, str]], question: str | None) -> str:
    if not drawn:
        return ""
    if len(drawn) == 1:
        return drawn[0]["meaning_it"]
    pieces = []
    if question:
        pieces.append(f"The querent asked: {question}.")
    for item in drawn:
        orient = "reversed" if item["reversed"] == "1" else "upright"
        pieces.append(
            f"{item['position']} is {item['name_en']} ({orient}): {item['meaning_en']}"
        )
    pieces.append("Summarize these official tarot meanings as one short combined reading.")
    return await translate_to_italian(client, " ".join(pieces))


async def send_tarot_draw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _tarot_state(context)
    spread = str(state.get("spread") or "")
    if spread not in TAROT_SPREADS:
        await show_tarot_menu(update, context)
        return
    meta = TAROT_SPREADS[spread]
    question = str(state.get("question") or "").strip() or None
    await send_typing(update)
    await deliver_text(update, context, "🃏 Sto mescolando il mazzo…")
    client = _http_client(context)

    try:
        cards = await api_tarot_draw(
            client,
            count=int(meta["count"]),
            include_minor=bool(meta["include_minor"]),
        )
    except StelleOfflineError:
        logger.exception("Tarocchi: API non disponibile")
        await reply_html(
            update,
            context,
            "Le stelle sono temporaneamente offline ✨ riprova tra poco\n\n"
            "Il mazzo live non ha risposto. Puoi ritentare la pesca.",
            reply_markup=tarot_draw_keyboard(),
        )
        return

    positions: tuple[str, ...] = tuple(meta["positions"])
    drawn: list[dict[str, str]] = []
    for idx, card in enumerate(cards[: len(positions)]):
        drawn.append(await _orient_and_translate_card(client, card, positions[idx]))

    try:
        synthesis = await _tarot_synthesis(client, drawn, question)
    except StelleOfflineError:
        synthesis = " ".join(item["meaning_it"] for item in drawn)

    circles = ("①", "②", "③")
    lines = ["🃏 <b>LE TUE CARTE</b>", f"<i>{e(meta['title'])}</i>", ""]
    if question:
        lines.append(f"❓ <b>Domanda:</b> <i>{e(question)}</i>")
        lines.append("")
    for idx, item in enumerate(drawn):
        mark = circles[idx] if idx < len(circles) else f"{idx + 1}."
        rev = " — rovesciata" if item["reversed"] == "1" else ""
        lines.append(
            f"{mark} <b>{e(item['position'].upper())}</b>\n"
            f"{item['emoji']} <b>{e(item['name_it'])}</b>{e(rev)}\n"
            f"<i>{e(item['kind'])}</i>\n\n"
            f"{e(item['meaning_it'])}"
        )
        lines.append("")
    if len(drawn) > 1 and synthesis:
        lines.append("🔮 <b>Sintesi</b>")
        lines.append(e(synthesis))
        lines.append("")
    lines.append(
        "<i>Carte live da freehoroscopeapi.com · significati ufficiali tradotti. "
        "Non è un oracolo infallibile, è un mazzo con un'API.</i>"
    )

    user = update.effective_user
    if user is not None:
        await tarot_history_add(
            user.id,
            {
                "at": datetime.now(DEFAULT_TZ).isoformat(timespec="minutes"),
                "spread": spread,
                "title": meta["title"],
                "question": question,
                "cards": [
                    {
                        "name": item["name_it"],
                        "position": item["position"],
                        "reversed": item["reversed"] == "1",
                    }
                    for item in drawn
                ],
            },
        )

    await reply_html(update, context, "\n".join(lines), reply_markup=tarot_after_keyboard())


async def show_tarot_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return
    rows = await tarot_history_list(user.id)
    if not rows:
        text = (
            "📖 <b>Le tue letture</b>\n\n"
            "Ancora nessuna. Quando peschi, resta qui una traccia "
            "(sul piano free di Render può azzerarsi al riavvio)."
        )
        await reply_html(update, context, text, reply_markup=tarot_after_keyboard())
        return
    lines = ["📖 <b>Le tue letture</b>", ""]
    for row in rows:
        if not isinstance(row, dict):
            continue
        when = str(row.get("at") or "")
        try:
            dt = datetime.fromisoformat(when)
            when_it = f"{dt.day:02d}/{dt.month:02d} {dt.hour:02d}:{dt.minute:02d}"
        except ValueError:
            when_it = when[:16]
        title = str(row.get("title") or row.get("spread") or "Lettura")
        cards = row.get("cards") if isinstance(row.get("cards"), list) else []
        names = []
        for card in cards:
            if isinstance(card, dict) and card.get("name"):
                extra = " (R)" if card.get("reversed") else ""
                names.append(f"{card['name']}{extra}")
        line = f"• {e(when_it)} — {e(title)}"
        if names:
            line += f"\n  {e(', '.join(names))}"
        if row.get("question"):
            line += f"\n  <i>{e(clip_text(str(row['question']), 80))}</i>"
        lines.append(line)
    await reply_html(update, context, "\n".join(lines), reply_markup=tarot_after_keyboard())


async def on_tarot_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    if query.message is not None:
        kind = "text" if query.message.text else "photo"
        _remember_bot_msg(context, query.message.message_id, kind)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""

    if action == "menu":
        await query.answer()
        await show_tarot_menu(update, context)
        return
    if action == "hist":
        await query.answer()
        await show_tarot_history(update, context)
        return
    if action == "pick" and extra == "ask":
        await query.answer()
        await show_tarot_ask_prompt(update, context)
        return
    if action == "pick" and extra in TAROT_SPREADS:
        await query.answer()
        await show_tarot_ritual(update, context, extra)
        return
    if action == "draw":
        await query.answer("Mazzo in movimento…")
        await send_tarot_draw(update, context)
        return
    await query.answer("Bottone stanco. Riprova con /tarocchi.")


# ---------------------------------------------------------------------------
# Tema natale — workflow guidato (CosmyDay /natal + geocoding)
# ---------------------------------------------------------------------------


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_tarot_btn("🌌 Tema Natale", "natal:open"), _tarot_btn("🔮 Tarocchi", "tarot:menu")],
            [_tarot_btn("♈ Oroscopo", "home:oroscopo"), _tarot_btn("🌙 Luna", "home:luna")],
        ]
    )


def _remember_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is not None and query.message is not None:
        kind = "text" if query.message.text else "photo"
        _remember_bot_msg(context, query.message.message_id, kind)


def natal_chart_from_state(state: dict[str, Any]) -> dict[str, Any] | None:
    chart = state.get("chart")
    return chart if isinstance(chart, dict) else None


def natal_body_line(key: str, body: dict[str, Any]) -> str:
    label, emoji = PLANET_LABELS.get(key, (key, "•"))
    sign = sign_label(str(body.get("sign") or ""))
    deg = format_degree(float(body.get("degInSign") or 0))
    house = body.get("house")
    house_bit = f" · casa {int(house)}" if house else ""
    retro = " ℞" if body.get("retrograde") else ""
    return f"{emoji} <b>{e(label)}</b>  {e(sign)} {e(deg)}{house_bit}{retro}"


def natal_point_from_lon(lon: float) -> tuple[str, float, str]:
    sign, deg = lon_to_sign(lon)
    it, emoji, _ = ZODIAC[sign]
    return sign, deg, f"{emoji} {it}"


async def cmd_tema(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await natal_open(update, context)
    await delete_user_command(update)


async def natal_open(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    profile = await natal_profile_get(user.id) if user else None
    if profile:
        await show_natal_saved_profile(update, context, profile)
        return
    await show_natal_intro(update, context)


async def show_natal_intro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _natal_state(context).clear()
    text = (
        "🌌 <b>Crea il tuo Tema Natale</b>\n\n"
        "Per calcolare la carta servono tre cose, una alla volta:\n"
        "📅 data di nascita\n"
        "🕐 ora di nascita\n"
        "📍 luogo di nascita\n\n"
        "I calcoli li fa CosmyDay (Swiss Ephemeris). Tu non devi sapere niente "
        "di astrologia: inserisci i dati, il resto è automatico."
    )
    kb = InlineKeyboardMarkup([[_tarot_btn("✨ Inizia", "natal:start")]])
    await reply_html(update, context, text, reply_markup=kb)


async def show_natal_saved_profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    profile: dict[str, Any],
) -> None:
    time_txt = "sconosciuta" if profile.get("time_unknown") else f"{int(profile.get('hour', 12)):02d}:{int(profile.get('minute', 0)):02d}"
    text = (
        "👤 <b>Il mio profilo</b>\n\n"
        f"📅 {e(format_birth_date(int(profile['year']), int(profile['month']), int(profile['day'])))}\n"
        f"🕐 {e(time_txt)}\n"
        f"📍 {e(profile.get('place') or '—')}\n\n"
        "Il tema è salvato: puoi rileggerlo senza reinserire i dati."
    )
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("🔮 Rileggi il tema", "natal:reload"), _tarot_btn("🌙 Transiti", "natal:transits")],
            [_tarot_btn("✨ Nuovo tema", "natal:start"), _tarot_btn("🏠 Home", "natal:homebtn")],
        ]
    )
    await reply_html(update, context, text, reply_markup=kb)


async def ask_natal_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    state["step"] = "date"
    await reply_html(
        update,
        context,
        "📅 <b>Quando sei nato/a?</b>\n\n"
        "Scrivi la data così: <code>GG/MM/AAAA</code>\n"
        "Esempio: <code>14/08/1998</code>",
    )


async def ask_natal_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    state["step"] = "time"
    kb = InlineKeyboardMarkup([[_tarot_btn("❓ Non conosco l'ora", "natal:notime")]])
    await reply_html(
        update,
        context,
        "🕐 <b>A che ora sei nato/a?</b>\n\n"
        "Scrivi l'orario: <code>HH:MM</code>\n"
        "Esempio: <code>21:35</code>\n\n"
        "L'ora serve soprattutto per <b>Ascendente</b> e <b>case</b>. "
        "Se non la sai, si può andare avanti lo stesso — ma quelle due cose "
        "diventano poco affidabili.",
        reply_markup=kb,
    )


async def ask_natal_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    state["step"] = "place"
    await reply_html(
        update,
        context,
        "📍 <b>Dove sei nato/a?</b>\n\n"
        "Scrivi città e paese.\n"
        "Esempio: <code>Milano, Italia</code>\n\n"
        "Cerco io le coordinate. Non ti chiedo latitudine né fuso orario.",
    )


async def show_natal_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    state["step"] = "confirm"
    y, m, d = int(state["year"]), int(state["month"]), int(state["day"])
    unknown = bool(state.get("time_unknown"))
    hour, minute = int(state.get("hour") or 12), int(state.get("minute") or 0)
    place = str(state.get("place") or "—")
    time_txt = "non indicata (uso mezzogiorno)" if unknown else f"{hour:02d}:{minute:02d}"
    warn = (
        "\n\n⚠️ Senza ora di nascita, Ascendente e case potrebbero non essere affidabili."
        if unknown
        else ""
    )
    text = (
        "🔮 <b>Controlla i tuoi dati</b>\n\n"
        f"📅 {e(format_birth_date(y, m, d))}\n"
        f"🕐 {e(time_txt)}\n"
        f"📍 {e(place)}\n"
        "Sistema case: Placidus\n"
        f"{warn}\n\n"
        "Tutto corretto?"
    )
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("✅ Calcola tema natale", "natal:calc")],
            [_tarot_btn("✏️ Modifica", "natal:start")],
        ]
    )
    await reply_html(update, context, text, reply_markup=kb)


async def receive_natal_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> bool:
    state = context.user_data.get(NATAL_STATE_KEY)
    if not isinstance(state, dict):
        return False
    step = state.get("step")
    if step == "date":
        parsed = parse_birth_date(text)
        if not parsed:
            await reply_html(
                update,
                context,
                "Questa data non torna. Usa <code>GG/MM/AAAA</code>, tipo <code>14/08/1998</code>.",
            )
            return True
        state["year"], state["month"], state["day"] = parsed
        await delete_user_command(update)
        await ask_natal_time(update, context)
        return True
    if step == "time":
        parsed = parse_birth_time(text)
        if not parsed:
            await reply_html(
                update,
                context,
                "Orario non valido. Usa <code>HH:MM</code>, tipo <code>21:35</code>.",
                reply_markup=InlineKeyboardMarkup([[_tarot_btn("❓ Non conosco l'ora", "natal:notime")]]),
            )
            return True
        state["hour"], state["minute"] = parsed
        state["time_unknown"] = False
        await delete_user_command(update)
        await ask_natal_place(update, context)
        return True
    if step == "place":
        await send_typing(update)
        await deliver_text(update, context, "📍 Cerco il luogo sulle mappe…")
        client = _http_client(context)
        try:
            places = await api_geocode_place(client, text)
        except StelleOfflineError:
            await reply_html(
                update,
                context,
                "Non trovo quel luogo. Prova con città e paese, tipo <code>Milano, Italia</code>.",
            )
            return True
        state["places"] = places
        await delete_user_command(update)
        if len(places) == 1:
            _apply_natal_place(state, places[0])
            await show_natal_confirm(update, context)
            return True
        rows = []
        for idx, place in enumerate(places[:4]):
            label = clip_text(str(place["display"]), 40)
            rows.append([_tarot_btn(f"📍 {label}", f"natal:loc:{idx}")])
        await reply_html(
            update,
            context,
            "Ho trovato più luoghi. Quale è il tuo?",
            reply_markup=InlineKeyboardMarkup(rows),
        )
        return True
    return False


def _apply_natal_place(state: dict[str, Any], place: dict[str, Any]) -> None:
    state["place"] = place.get("display")
    state["lat"] = place.get("lat")
    state["lon"] = place.get("lon")
    state["place_name"] = place.get("name")
    state["step"] = "confirm"


async def calculate_natal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    needed = ("year", "month", "day", "lat", "lon")
    if any(k not in state for k in needed):
        await show_natal_intro(update, context)
        return
    await send_typing(update)
    await deliver_text(update, context, "🌌 Sto calcolando la carta (Swiss Ephemeris)…")
    hour = int(state.get("hour") or 12)
    minute = int(state.get("minute") or 0)
    client = _http_client(context)
    try:
        chart = await api_natal_chart(
            client,
            year=int(state["year"]),
            month=int(state["month"]),
            day=int(state["day"]),
            hour=hour,
            minute=minute,
            lat=float(state["lat"]),
            lon=float(state["lon"]),
        )
    except StelleOfflineError:
        logger.exception("Tema natale: calcolo non disponibile")
        await reply_html(
            update,
            context,
            STARS_OFFLINE + "\n\nPuoi ritentare il calcolo.",
            reply_markup=InlineKeyboardMarkup([[_tarot_btn("🔁 Riprova", "natal:calc")]]),
        )
        return
    state["chart"] = chart
    state["step"] = "done"
    await show_natal_big_three(update, context)


async def reload_saved_natal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    profile = await natal_profile_get(user.id) if user else None
    if not profile:
        await show_natal_intro(update, context)
        return
    state = _natal_state(context)
    state.clear()
    state.update(
        {
            "year": profile["year"],
            "month": profile["month"],
            "day": profile["day"],
            "hour": profile.get("hour", 12),
            "minute": profile.get("minute", 0),
            "time_unknown": profile.get("time_unknown", False),
            "place": profile.get("place"),
            "lat": profile.get("lat"),
            "lon": profile.get("lon"),
            "step": "confirm",
        }
    )
    await calculate_natal(update, context)


async def show_natal_big_three(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    chart = natal_chart_from_state(state)
    if not chart:
        await show_natal_intro(update, context)
        return
    planets = chart.get("planets") or {}
    sun = planets.get("Sun") or {}
    moon = planets.get("Moon") or {}
    asc_sign, asc_deg, asc_label = natal_point_from_lon(float(chart.get("ascendant") or 0))
    unknown = bool(state.get("time_unknown"))
    warn = "\n⚠️ Ora mancante: l'Ascendente è indicativo (calcolato a mezzogiorno).\n" if unknown else "\n"
    text = (
        "🌌 <b>IL TUO BIG THREE</b>\n\n"
        f"☀️ <b>Sole in {e(sign_label(str(sun.get('sign') or '')))}</b>\n"
        f"<i>La tua identità, ciò che vuoi esprimere.</i>\n\n"
        f"🌙 <b>Luna in {e(sign_label(str(moon.get('sign') or '')))}</b>\n"
        f"<i>Il tuo mondo emotivo, bisogni e reazioni.</i>\n\n"
        f"⬆️ <b>Ascendente in {e(asc_label)}</b> {e(format_degree(asc_deg))}\n"
        f"<i>Come ti presenti e affronti ciò che incontri.</i>"
        f"{warn}\n"
        "━━━━━━━━━━━━━\n"
        "✨ Ora possiamo entrare nel dettaglio."
    )
    await reply_html(update, context, text, reply_markup=natal_nav_keyboard())


async def show_natal_planets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chart = natal_chart_from_state(_natal_state(context))
    if not chart:
        await show_natal_intro(update, context)
        return
    planets = chart.get("planets") or {}
    lines = ["🪐 <b>I tuoi pianeti</b>", "Tocca un pianeta per la scheda.", ""]
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for key in MAIN_PLANETS:
        body = planets.get(key)
        if not isinstance(body, dict):
            continue
        lines.append(natal_body_line(key, body))
        label, emoji = PLANET_LABELS[key]
        pair.append(_tarot_btn(f"{emoji} {label}", f"natal:p:{key}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([_tarot_btn("⬅️ Big Three", "natal:big")])
    await reply_html(update, context, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def show_natal_planet(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> None:
    chart = natal_chart_from_state(_natal_state(context))
    if not chart or key not in PLANET_LABELS:
        await show_natal_planets(update, context)
        return
    body = (chart.get("planets") or {}).get(key)
    if not isinstance(body, dict):
        await show_natal_planets(update, context)
        return
    label, emoji = PLANET_LABELS[key]
    role = PLANET_ROLES.get(key, "")
    house = int(body.get("house") or 0)
    house_name = HOUSE_LABELS.get(house, "")
    dignity = DIGNITY_IT.get(str(body.get("dignity") or "").lower(), "")
    client = _http_client(context)
    prompt = (
        f"In a natal chart, {label} is in {body.get('sign')} in house {house} "
        f"({house_name}). Dignity: {body.get('dignity')}. "
        f"{label} is associated with {role}. "
        f"Write 4 short Italian-ready sentences explaining this placement only from these facts, "
        f"curious and light, not romantic."
    )
    try:
        blurb = await translate_to_italian(client, prompt)
    except StelleOfflineError:
        blurb = f"{label} in {sign_label(str(body.get('sign')))} in casa {house}."
    text = (
        f"{emoji} <b>{e(label)} in {e(sign_label(str(body.get('sign') or '')))}</b>"
        f"{f' — casa {house}' if house else ''}\n"
        f"<i>{e(role)}</i>\n"
        f"{e(format_degree(float(body.get('degInSign') or 0)))}"
        f"{' · ' + e(dignity) if dignity else ''}"
        f"{' · retrogrado' if body.get('retrograde') else ''}\n\n"
        f"{e(blurb)}\n\n"
        f"<i>Dati live CosmyDay · casa {house}: {e(house_name)}</i>"
    )
    kb = InlineKeyboardMarkup([[_tarot_btn("⬅️ Pianeti", "natal:planets"), _tarot_btn("🌌 Big Three", "natal:big")]])
    await reply_html(update, context, text, reply_markup=kb)


async def show_natal_houses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chart = natal_chart_from_state(_natal_state(context))
    if not chart:
        await show_natal_intro(update, context)
        return
    planets = chart.get("planets") or {}
    occupants: dict[int, list[str]] = {i: [] for i in range(1, 13)}
    for key in MAIN_PLANETS:
        body = planets.get(key)
        if isinstance(body, dict) and body.get("house"):
            occupants[int(body["house"])].append(PLANET_LABELS[key][1] + " " + PLANET_LABELS[key][0])
    lines = ["🏠 <b>Le 12 case</b>", "Tocca una casa per vedere chi c'è dentro.", ""]
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for num, title in HOUSE_LABELS.items():
        inside = ", ".join(occupants[num]) or "vuota"
        lines.append(f"<b>{num}</b> — {e(title)}\n   {e(inside)}")
        pair.append(_tarot_btn(str(num), f"natal:h:{num}"))
        if len(pair) == 4:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([_tarot_btn("⬅️ Big Three", "natal:big")])
    await reply_html(update, context, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def show_natal_house(update: Update, context: ContextTypes.DEFAULT_TYPE, num: int) -> None:
    chart = natal_chart_from_state(_natal_state(context))
    if not chart or num < 1 or num > 12:
        await show_natal_houses(update, context)
        return
    cusps = chart.get("cusps") or []
    cusp_lon = float(cusps[num - 1]) if len(cusps) >= num else 0.0
    sign, deg, label = natal_point_from_lon(cusp_lon)
    planets = chart.get("planets") or {}
    inside = []
    for key in MAIN_PLANETS:
        body = planets.get(key)
        if isinstance(body, dict) and int(body.get("house") or 0) == num:
            inside.append(natal_body_line(key, body))
    text = (
        f"🏠 <b>Casa {num} — {e(HOUSE_LABELS[num])}</b>\n"
        f"Cuspide in {e(label)} {e(format_degree(deg))}\n\n"
    )
    text += "\n".join(inside) if inside else "Nessun pianeta principale in questa casa."
    kb = InlineKeyboardMarkup([[_tarot_btn("⬅️ Case", "natal:houses"), _tarot_btn("🌌 Big Three", "natal:big")]])
    await reply_html(update, context, text, reply_markup=kb)


async def show_natal_aspects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chart = natal_chart_from_state(_natal_state(context))
    if not chart:
        await show_natal_intro(update, context)
        return
    aspects = chart.get("aspects") if isinstance(chart.get("aspects"), list) else []
    main = set(MAIN_PLANETS)
    lines = ["⚡ <b>Aspetti principali</b>", "Calcolati dall'API (orb e tipo live).", ""]
    shown = 0
    for asp in aspects:
        if not isinstance(asp, dict):
            continue
        a, b = str(asp.get("a") or ""), str(asp.get("b") or "")
        kind = str(asp.get("type") or "")
        if a not in main or b not in main or kind not in ASPECT_LABELS:
            continue
        try:
            orb = abs(float(asp.get("delta") or 0))
        except (TypeError, ValueError):
            orb = 0.0
        if orb > 8:
            continue
        it_name, glyph = ASPECT_LABELS[kind]
        ea, la = PLANET_LABELS[a]
        eb, lb = PLANET_LABELS[b]
        lines.append(f"{ea} {e(la)} {glyph} {eb} {e(lb)}\n{e(it_name)} — orb {orb:.1f}°")
        shown += 1
        if shown >= 10:
            break
    if shown == 0:
        lines.append("Nessun aspetto stretto tra i pianeti principali.")
    await reply_html(update, context, "\n".join(lines), reply_markup=natal_nav_keyboard())


async def show_natal_love(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chart = natal_chart_from_state(_natal_state(context))
    if not chart:
        await show_natal_intro(update, context)
        return
    planets = chart.get("planets") or {}
    lines = ["❤️ <b>Amore nel tema</b>", "Venere, Marte, Luna e casa 7 — dati live.", ""]
    for key in ("Venus", "Mars", "Moon"):
        body = planets.get(key)
        if isinstance(body, dict):
            lines.append(natal_body_line(key, body))
            lines.append(f"<i>{e(PLANET_ROLES[key])}</i>")
            lines.append("")
    seventh = []
    for key in MAIN_PLANETS:
        body = planets.get(key)
        if isinstance(body, dict) and int(body.get("house") or 0) == 7:
            seventh.append(PLANET_LABELS[key][0])
    lines.append("🏠 <b>Casa 7</b> — relazioni")
    lines.append(", ".join(seventh) if seventh else "Nessun pianeta principale in casa 7.")
    await reply_html(update, context, "\n".join(lines), reply_markup=natal_nav_keyboard())


async def show_natal_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    chart = natal_chart_from_state(state)
    if not chart:
        await show_natal_intro(update, context)
        return
    planets = chart.get("planets") or {}
    sun = planets.get("Sun") or {}
    moon = planets.get("Moon") or {}
    asc_sign, _asc_deg, asc_label = natal_point_from_lon(float(chart.get("ascendant") or 0))
    facts = [
        f"Sun in {sun.get('sign')} house {sun.get('house')}",
        f"Moon in {moon.get('sign')} house {moon.get('house')}",
        f"Ascendant in {asc_sign}",
    ]
    for key in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        body = planets.get(key)
        if isinstance(body, dict):
            facts.append(f"{key} in {body.get('sign')} house {body.get('house')}")
    prompt = (
        "Write a natal-chart reading in a curious light Italian-ready tone using ONLY these live placements: "
        + "; ".join(facts)
        + ". Four short paragraphs: identity, emotions, style of meeting the world, a connecting thread. "
        "Do not invent extra planets."
    )
    client = _http_client(context)
    try:
        reading = await translate_to_italian(client, prompt)
    except StelleOfflineError:
        reading = (
            f"Sole in {sign_label(str(sun.get('sign')))}, "
            f"Luna in {sign_label(str(moon.get('sign')))}, "
            f"Ascendente {asc_label}."
        )
    text = (
        "🔮 <b>La tua carta racconta</b>\n\n"
        f"{e(reading)}\n\n"
        "<i>Interpretazione costruita sulle posizioni CosmyDay, non inventata a caso. "
        "Non è un verdetto: è una mappa.</i>"
    )
    if user and not await natal_profile_get(user.id):
        extra_row = [_tarot_btn("💾 Salva il tema", "natal:save")]
        kb = natal_nav_keyboard()
        rows = [list(row) for row in kb.inline_keyboard]
        rows.insert(0, extra_row)
        await reply_html(update, context, text, reply_markup=InlineKeyboardMarkup(rows))
        return
    await reply_html(update, context, text, reply_markup=natal_nav_keyboard())


async def show_natal_elements(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chart = natal_chart_from_state(_natal_state(context))
    if not chart:
        await show_natal_intro(update, context)
        return
    planets = chart.get("planets") or {}
    elements = {"fuoco": 0, "terra": 0, "aria": 0, "acqua": 0}
    modes = {"cardinale": 0, "fisso": 0, "mutabile": 0}
    for key in MAIN_PLANETS:
        body = planets.get(key)
        if not isinstance(body, dict):
            continue
        sign = str(body.get("sign") or "").lower()
        el = SIGN_ELEMENT.get(sign)
        md = SIGN_MODALITY.get(sign)
        if el:
            elements[el] += 1
        if md:
            modes[md] += 1
    asc_sign, _, _ = natal_point_from_lon(float(chart.get("ascendant") or 0))
    if SIGN_ELEMENT.get(asc_sign):
        elements[SIGN_ELEMENT[asc_sign]] += 1
    if SIGN_MODALITY.get(asc_sign):
        modes[SIGN_MODALITY[asc_sign]] += 1
    text = (
        "📊 <b>Il tuo profilo</b>\n"
        "<i>Conteggio Sole–Plutone + Ascendente, dai dati live.</i>\n\n"
        f"🔥 Fuoco   {element_bar(elements, 'fuoco')} {elements['fuoco']}\n"
        f"🌍 Terra   {element_bar(elements, 'terra')} {elements['terra']}\n"
        f"💨 Aria    {element_bar(elements, 'aria')} {elements['aria']}\n"
        f"💧 Acqua   {element_bar(elements, 'acqua')} {elements['acqua']}\n\n"
        f"CARDINALE  {element_bar(modes, 'cardinale')} {modes['cardinale']}\n"
        f"FISSO      {element_bar(modes, 'fisso')} {modes['fisso']}\n"
        f"MUTABILE   {element_bar(modes, 'mutabile')} {modes['mutabile']}"
    )
    await reply_html(update, context, text, reply_markup=natal_nav_keyboard())


async def save_natal_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    state = _natal_state(context)
    if user is None or "year" not in state:
        await show_natal_intro(update, context)
        return
    await natal_profile_set(
        user.id,
        {
            "year": state["year"],
            "month": state["month"],
            "day": state["day"],
            "hour": state.get("hour", 12),
            "minute": state.get("minute", 0),
            "time_unknown": bool(state.get("time_unknown")),
            "place": state.get("place"),
            "lat": state.get("lat"),
            "lon": state.get("lon"),
            "saved_at": datetime.now(DEFAULT_TZ).isoformat(timespec="minutes"),
        },
    )
    await reply_html(
        update,
        context,
        "💾 Tema salvato. La prossima volta /tema apre il tuo profilo.",
        reply_markup=natal_nav_keyboard(),
    )


async def show_natal_transits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    profile = await natal_profile_get(user.id) if user else None
    state = _natal_state(context)
    if profile and "lat" in profile:
        natal_src = profile
    elif "lat" in state:
        natal_src = state
    else:
        await show_natal_intro(update, context)
        return
    await send_typing(update)
    await deliver_text(update, context, "🌙 Confronto il cielo di oggi con la tua carta…")
    client = _http_client(context)
    try:
        today = await api_planets_now(client)
        if "chart" not in state:
            state.update(
                {
                    "year": natal_src["year"],
                    "month": natal_src["month"],
                    "day": natal_src["day"],
                    "hour": natal_src.get("hour", 12),
                    "minute": natal_src.get("minute", 0),
                    "lat": natal_src["lat"],
                    "lon": natal_src["lon"],
                    "place": natal_src.get("place"),
                    "time_unknown": natal_src.get("time_unknown", False),
                }
            )
            state["chart"] = await api_natal_chart(
                client,
                year=int(natal_src["year"]),
                month=int(natal_src["month"]),
                day=int(natal_src["day"]),
                hour=int(natal_src.get("hour") or 12),
                minute=int(natal_src.get("minute") or 0),
                lat=float(natal_src["lat"]),
                lon=float(natal_src["lon"]),
            )
    except StelleOfflineError:
        await reply_offline(update, context)
        return
    natal_planets = (state.get("chart") or {}).get("planets") or {}
    now_planets = today.get("planets") or {}
    lines = [
        "🌙 <b>Transiti di oggi</b>",
        "Cielo attuale (Roma, ora) rispetto al tuo tema.",
        "",
    ]
    for key in MAIN_PLANETS:
        now_b = now_planets.get(key)
        nat_b = natal_planets.get(key)
        if not isinstance(now_b, dict) or not isinstance(nat_b, dict):
            continue
        label, emoji = PLANET_LABELS[key]
        same = str(now_b.get("sign")) == str(nat_b.get("sign"))
        mark = " · stesso segno del natale" if same else ""
        lines.append(
            f"{emoji} <b>{e(label)}</b> oggi {e(sign_label(str(now_b.get('sign'))))} "
            f"(natale: {e(sign_label(str(nat_b.get('sign'))))}){mark}"
        )
    await reply_html(update, context, "\n".join(lines), reply_markup=natal_nav_keyboard())


async def on_natal_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""

    if action == "open":
        await query.answer()
        await natal_open(update, context)
        return
    if action == "homebtn":
        await query.answer()
        _flows_reset(context)
        await reply_html(update, context, start_text(), reply_markup=home_keyboard())
        return
    if action == "start":
        await query.answer()
        _natal_state(context).clear()
        await ask_natal_date(update, context)
        return
    if action == "notime":
        await query.answer()
        state = _natal_state(context)
        state["hour"], state["minute"] = 12, 0
        state["time_unknown"] = True
        await ask_natal_place(update, context)
        return
    if action == "loc" and extra.isdigit():
        await query.answer()
        places = _natal_state(context).get("places") or []
        idx = int(extra)
        if 0 <= idx < len(places):
            _apply_natal_place(_natal_state(context), places[idx])
            await show_natal_confirm(update, context)
        return
    if action == "calc":
        await query.answer("Calcolo in corso…")
        await calculate_natal(update, context)
        return
    if action == "big":
        await query.answer()
        await show_natal_big_three(update, context)
        return
    if action == "planets":
        await query.answer()
        await show_natal_planets(update, context)
        return
    if action == "p" and extra:
        await query.answer()
        await show_natal_planet(update, context, extra)
        return
    if action == "houses":
        await query.answer()
        await show_natal_houses(update, context)
        return
    if action == "h" and extra.isdigit():
        await query.answer()
        await show_natal_house(update, context, int(extra))
        return
    if action == "aspects":
        await query.answer()
        await show_natal_aspects(update, context)
        return
    if action == "love":
        await query.answer()
        await show_natal_love(update, context)
        return
    if action == "read":
        await query.answer("Sto componendo la lettura…")
        await show_natal_reading(update, context)
        return
    if action == "elements":
        await query.answer()
        await show_natal_elements(update, context)
        return
    if action == "save":
        await query.answer("Salvato")
        await save_natal_profile(update, context)
        return
    if action == "me":
        await query.answer()
        await natal_open(update, context)
        return
    if action == "reload":
        await query.answer("Ricalcolo…")
        await reload_saved_natal(update, context)
        return
    if action == "transits":
        await query.answer()
        await show_natal_transits(update, context)
        return
    await query.answer("Bottone stanco. Riprova con /tema.")


async def on_home_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    if action == "oroscopo":
        await query.answer()
        await begin_oroscopo(update, context, "")
        return
    if action == "luna":
        await query.answer()
        await cmd_luna(update, context)
        return
    await query.answer()


async def cmd_luna(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await send_typing(update)
    await show_loading(update, context)
    client = _http_client(context)

    obs_res, story_res = await asyncio.gather(
        api_moon_observatory(client),
        api_moon_story(client),
        return_exceptions=True,
    )

    obs = obs_res if isinstance(obs_res, dict) else None
    story = story_res if isinstance(story_res, dict) else None
    if obs is None and story is None:
        logger.error("Luna: entrambe le API sono fallite: %s / %s", obs_res, story_res)
        await reply_offline(update, context)
        return

    lines: list[str] = ["🌙 <b>La Luna, stasera (dati live)</b>"]
    phase_name = None
    illumination = None
    date_it = format_date_it(None)

    if obs:
        date_it = format_date_it(str(obs.get("date") or ""))
        phase_name = obs.get("moon_phase")
        illumination = obs.get("moon_illumination")
        lines.append(f"📍 Cielo calcolato su {e(DEFAULT_PLACE_NAME)} · {e(date_it)}")
        lines.append(f"🔭 Fase: <b>{e(moon_phase_label(str(phase_name)))}</b>")
        if illumination is not None:
            try:
                lines.append(f"💡 Illuminazione: <b>{float(illumination):.0f}%</b>")
            except (TypeError, ValueError):
                pass
        if obs.get("moonrise"):
            lines.append(f"⬆️ Moonrise: {e(obs['moonrise'])}")
        if obs.get("moonset"):
            lines.append(f"⬇️ Moonset: {e(obs['moonset'])}")
        lines.append(
            f"☀️ Sole: alba {e(obs.get('sunrise') or '—')} · "
            f"tramonto {e(obs.get('sunset') or '—')}"
        )

    if story and isinstance(story.get("moon"), dict):
        moon_meta = story["moon"]
        if not phase_name:
            phase_name = moon_meta.get("phase_name") or moon_meta.get("phase")
            lines.append(f"🔭 Fase: <b>{e(moon_phase_label(str(phase_name)))}</b>")
        if moon_meta.get("sign"):
            lines.append(
                f"♈ La Luna transita in {e(sign_label(str(moon_meta['sign'])))} "
                f"({e(format_degree(float(moon_meta.get('degree') or 0)))})"
            )

    lines.append("")
    if story and story.get("content"):
        try:
            meaning = await translate_to_italian(client, str(story["content"]))
        except StelleOfflineError:
            meaning = str(story["content"])
        lines.append("🧠 <b>Cosa significa, in soldoni</b>")
        lines.append(e(meaning))
    else:
        lines.append(
            "🧠 L'articolo interpretativo non è arrivato, ma i numeri sopra "
            "sono veri: la Luna non ha bisogno del copywriter per esistere."
        )

    lines.append("")
    lines.append(
        "<i>Fonti live: sunrisesunset.io (osservazione) e CosmyDay "
        "(fase + testo del giorno).</i>"
    )
    await reply_html(update, context, "\n".join(lines))
    await delete_user_command(update)


async def cmd_pianeti(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await send_typing(update)
    await show_loading(update, context)
    client = _http_client(context)
    now = datetime.now(DEFAULT_TZ)

    try:
        natal = await api_planets_now(client)
    except StelleOfflineError:
        logger.exception("Pianeti: efemeridi non disponibili")
        await reply_offline(update, context)
        return

    planets = natal.get("planets") or {}
    lines = [
        "🪐 <b>Pianeti in questo momento</b>",
        f"📍 Cielo sopra {e(DEFAULT_PLACE_NAME)} · "
        f"{now.strftime('%d/%m/%Y %H:%M')} (Europe/Rome)",
        "",
    ]

    retro_names: list[str] = []
    for key in MAIN_PLANETS:
        body = planets.get(key)
        if not isinstance(body, dict):
            continue
        label, emoji = PLANET_LABELS[key]
        sign = sign_label(str(body.get("sign") or ""))
        deg = format_degree(float(body.get("degInSign") or 0))
        retro = bool(body.get("retrograde"))
        dignity = DIGNITY_IT.get(str(body.get("dignity") or "").lower(), "")
        extra_bits = []
        if retro:
            extra_bits.append("℞ retrogrado")
            retro_names.append(label)
        if dignity and dignity != "in transito":
            extra_bits.append(dignity)
        extra = f" · {', '.join(extra_bits)}" if extra_bits else ""
        lines.append(f"{emoji} <b>{e(label)}</b> — {e(sign)} {e(deg)}{e(extra)}")

    # Nota divertente costruita sui dati live (retrogradi + transito del giorno).
    lines.append("")
    if retro_names:
        joined = ", ".join(retro_names)
        lines.append(
            f"😏 <b>Nota dal vivo:</b> {e(joined)} "
            f"{'sta' if len(retro_names) == 1 else 'stanno'} facendo retromarcia. "
            "In astronomia è prospettiva; in astrologia è il momento in cui "
            "l'universo preme Ctrl+Z."
        )
    else:
        lines.append(
            "😏 <b>Nota dal vivo:</b> nessuno dei pianeti principali è retrogrado "
            "in questo istante. Raro come trovare il telecomando al primo colpo."
        )

    transit = await api_transit_note(client)
    if transit and transit.get("content"):
        snippet = str(transit["content"]).strip().split("\n")
        snippet_en = " ".join(s.strip() for s in snippet if s.strip())[:700]
        try:
            snippet_it = await translate_to_italian(client, snippet_en)
        except StelleOfflineError:
            snippet_it = snippet_en
        lines.append("")
        lines.append("🗞️ <b>Bollettino dei transiti (live)</b>")
        lines.append(e(snippet_it))

    lines.append("")
    lines.append(
        "<i>Efemeridi live: CosmyDay API (Swiss Ephemeris / NASA JPL DE431). "
        "Posizioni tropicali.</i>"
    )
    await reply_html(update, context, "\n".join(lines))
    await delete_user_command(update)


async def _deliver_apod(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    item: dict[str, Any],
    *,
    intro: str,
) -> None:
    client = _http_client(context)
    title = str(item.get("title") or "Senza titolo")
    explanation = str(item.get("explanation") or "")
    media_type = str(item.get("media_type") or "image").lower()
    url = str(item.get("url") or item.get("hdurl") or "")
    date_it = format_date_it(str(item.get("date") or ""))
    copyright_ = str(item.get("copyright") or "").strip()

    title_it = await translate_to_italian(client, title)
    expl_it = await translate_to_italian(client, explanation) if explanation else ""

    is_video = media_type == "video" or "youtube" in url.lower() or "vimeo" in url.lower()

    header_bits = [
        intro,
        f"🖼️ <b>{e(title_it)}</b>",
        f"📅 {e(date_it)} · NASA APOD",
    ]
    if is_video:
        header_bits.append(
            "🎬 <b>Oggi la NASA ha mandato un video</b>, non una foto. "
            "Apri il link (il bot non può proiettarlo sul soffitto, ci abbiamo provato)."
        )
    if copyright_:
        header_bits.append(f"© {e(copyright_.replace(chr(10), ', '))}")

    text_body = "\n".join(header_bits)
    if expl_it:
        text_body += f"\n\n{e(expl_it)}"
    if url:
        text_body += f"\n\n🔗 {e(url)}"
    text_body += "\n\n<i>Fonte live: api.nasa.gov/planetary/apod</i>"

    can_send_photo = (
        not is_video
        and media_type == "image"
        and url
        and url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
    )
    if can_send_photo:
        caption_bits = [
            intro,
            f"🖼️ <b>{e(title_it)}</b>",
            f"📅 {e(date_it)} · NASA APOD",
        ]
        if copyright_:
            caption_bits.append(f"© {e(copyright_.replace(chr(10), ', '))}")
        caption = "\n".join(caption_bits)
        extra = ""
        if expl_it:
            extra += f"\n\n{e(expl_it)}"
        if url:
            extra += f"\n\n🔗 {e(url)}"
        room = TELEGRAM_CAPTION_MAX - len(caption)
        if room > 40 and extra:
            caption += clip_text(extra, room)
        if await deliver_photo(update, context, url, caption):
            return

    await reply_html(update, context, text_body, preview=True)


async def cmd_apod(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await send_typing(update)
    await show_loading(update, context)
    client = _http_client(context)
    try:
        item = await api_apod(client, random=False)
        await _deliver_apod(
            update,
            context,
            item,
            intro="🔭 <b>Astronomy Picture of the Day</b>",
        )
        await delete_user_command(update)
    except StelleOfflineError:
        logger.exception("APOD odierno non disponibile")
        await reply_offline(update, context)


async def cmd_stelle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await send_typing(update)
    await show_loading(update, context)
    client = _http_client(context)
    try:
        item = await api_apod(client, random=True)
        await _deliver_apod(
            update,
            context,
            item,
            intro=(
                "⭐ <b>Una scheda dal catalogo NASA, pescata a caso</b>\n"
                "<i>Niente barzellette sul Big Bang: i fatti sono quelli della foto.</i>"
            ),
        )
        await delete_user_command(update)
    except StelleOfflineError:
        logger.exception("Curiosità APOD random non disponibile")
        await reply_offline(update, context)


async def on_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Domanda tarocchi in corso, oppure un segno trattato come /oroscopo."""
    message = update.effective_message
    if message is None or not message.text:
        return
    text = message.text.strip()
    if await receive_natal_text(update, context, text):
        return
    state = context.user_data.get(TAROT_STATE_KEY)
    if isinstance(state, dict) and state.get("awaiting_question"):
        await receive_tarot_question(update, context, text)
        return
    sign, period, _used_default = parse_oroscopo_query(text)
    if sign is not None and (normalize_sign(text) or period):
        await begin_oroscopo(update, context, text)
        return
    # In un gruppo non rispondiamo a ogni chiacchiera: solo in chat privata.
    chat = update.effective_chat
    if chat is not None and chat.type != "private":
        return
    await reply_html(
        update,
        context,
        "Ho letto il messaggio, ma non è un segno zodiacale né un comando.\n"
        "Scrivi ad esempio <i>vergine</i>, oppure /oroscopo bilancia, oppure /tarocchi.",
    )


async def on_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "Quel comando non è nella mappa celeste. Prova /aiuto prima che Mercurio "
        "faccia di nuovo il furbo.",
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Errore non gestito: %s", context.error)
    if isinstance(update, Update):
        try:
            await reply_offline(update, context)
        except TelegramError:
            pass


# ---------------------------------------------------------------------------
# Bootstrap Application (polling + webhook)
# ---------------------------------------------------------------------------


async def post_init(application: Application) -> None:
    application.bot_data["http"] = httpx.AsyncClient(
        timeout=httpx.Timeout(HTTP_TIMEOUT, connect=10.0),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        follow_redirects=True,
    )
    try:
        await application.bot.set_my_commands(
            [
                BotCommand("start", "Presentazione del bot"),
                BotCommand("tema", "Tema natale guidato"),
                BotCommand("oroscopo", "Oroscopo: giorno, settimana o mese"),
                BotCommand("tarocchi", "Lettura guidata dei tarocchi"),
                BotCommand("luna", "Fase lunare di oggi"),
                BotCommand("pianeti", "Posizioni attuali dei pianeti"),
                BotCommand("apod", "Foto NASA del giorno"),
                BotCommand("stelle", "Curiosità astronomica live"),
                BotCommand("aiuto", "Elenco comandi"),
            ]
        )
    except TelegramError as exc:
        logger.warning("Impossibile impostare i comandi del menu: %s", exc)
    logger.info("StelleBot inizializzato")


async def post_shutdown(application: Application) -> None:
    client = application.bot_data.get("http")
    if isinstance(client, httpx.AsyncClient):
        await client.aclose()
        logger.info("Client HTTP chiuso")


def build_application(token: str) -> Application:
    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler(["tema", "natale", "temanatale"], cmd_tema))
    application.add_handler(CommandHandler("oroscopo", cmd_oroscopo))
    application.add_handler(CommandHandler(["tarocchi", "tarot", "tarocco"], cmd_tarocchi))
    application.add_handler(CommandHandler("luna", cmd_luna))
    application.add_handler(CommandHandler("pianeti", cmd_pianeti))
    application.add_handler(CommandHandler("apod", cmd_apod))
    application.add_handler(CommandHandler("stelle", cmd_stelle))
    application.add_handler(CommandHandler(["aiuto", "help"], cmd_aiuto))
    application.add_handler(CallbackQueryHandler(on_oroscopo_period, pattern=r"^horo:"))
    application.add_handler(CallbackQueryHandler(on_tarot_action, pattern=r"^tarot:"))
    application.add_handler(CallbackQueryHandler(on_natal_action, pattern=r"^natal:"))
    application.add_handler(CallbackQueryHandler(on_home_action, pattern=r"^home:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_plain_text))
    application.add_handler(MessageHandler(filters.COMMAND, on_unknown_command))
    application.add_error_handler(on_error)
    return application


def main() -> None:
    load_dotenv()

    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        logger.error("Manca TELEGRAM_BOT_TOKEN. Copia .env.example in .env e inserisci il token.")
        sys.exit(1)

    if DEFAULT_SIGN not in ZODIAC:
        logger.error("DEFAULT_SIGN=%r non è un segno valido. Usa una chiave inglese: %s", DEFAULT_SIGN, ", ".join(ZODIAC))
        sys.exit(1)

    application = build_application(token)
    webhook_url = (os.getenv("WEBHOOK_URL") or "").strip()

    if webhook_url:
        # Produzione (Render): Telegram chiama il nostro HTTPS, niente polling.
        port = int(os.getenv("PORT") or "10000")
        url_path = (os.getenv("WEBHOOK_PATH") or "webhook").strip().strip("/")
        secret = (os.getenv("WEBHOOK_SECRET") or "").strip() or None
        public_url = f"{webhook_url.rstrip('/')}/{url_path}"

        logger.info("Avvio in modalità WEBHOOK su porta %s → %s", port, public_url)
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=url_path,
            webhook_url=public_url,
            secret_token=secret,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
    else:
        # Sviluppo locale: long polling. Non impostare WEBHOOK_URL.
        logger.info("Avvio in modalità POLLING (nessun WEBHOOK_URL)")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )


if __name__ == "__main__":
    main()
