#!/usr/bin/env python3
"""
StelleBot — bot Telegram informativo (e un po' ironico) su oroscopo,
astrologia, pianeti, stelle e astronomia.

Tutto il contenuto "di fatto" arriva da API live. I testi fissi nel codice
sono solo interfaccia (pulsanti, etichette, messaggi di errore), mai oroscopi
o curiosità astronomiche inventate. Si naviga a pulsanti. Nel menu Telegram
restano solo /start e /aiuto.

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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update

from services.astronomy import stellarium_url, visibility_stars
from services.catalog import (
    CONSTELLATIONS,
    DEEP_SKY,
    GALAXIES,
    GIANT_STARS,
    MIRROR_QUESTIONS,
    MISSIONS,
    NEAR_STARS,
    PLANETS,
    STARS,
    by_id,
    worlds_for_mission,
)
from services.wiki import wikidata_facts, wikipedia_summary
from services.skyview import collect_marks, milky_way_hint, text_sky_map, visibility_line
from services.spaceweather import kp_index, latest_flare, moon_distance_events, next_distance_event
from services.exoplanets import (
    FILTERS,
    exoplanet_by_name,
    exoplanets_by_filter,
    habitable_candidates,
    planet_of_the_day,
    random_exoplanet,
)
from services.systems import (
    FAMOUS_HOSTS,
    format_system_tree,
    random_system,
    system_card,
    systems_by_kind,
)
from services.imagine import format_imaginary, generate_world
from services.i18n import compass_it, discovery_it, event_name_it, kp_label_it, star_it
from services.eclipses import fetch_eclipses, kind_it, next_of, parse_peak
from services.iss import fetch_iss_position, reverse_iss_place
from services.neo import near_earth_asteroids
from services.progress import (
    mission_done,
    mission_is_done,
    quiz_board,
    quiz_record,
    stone_discover,
    stone_ids,
    world_list,
    world_save,
)
from services.compat import (
    COMPAT_SLOTS,
    ELEMENTS as COMPAT_ELEMENTS,
    MINE_FILL,
    SIGNS as COMPAT_SIGNS,
    chart_element,
    chart_points,
    format_big_three,
    format_elements,
    format_overlays,
    format_point_compat,
    format_sign_compat,
    format_synastry,
    format_venus_mars,
)
from services.stones import (
    CATS,
    COLORS,
    ENVS,
    MUSEUM,
    RARITY,
    STONES,
    by_cat,
    by_color,
    by_env,
    by_id as stone_by_id,
    by_rarity,
    build_field_quiz,
    build_guess,
    build_tf,
    filter_lab,
    format_card,
    format_compare,
    format_list,
    format_section,
    museum_room,
    format_daily_oracle_card,
    oracle_spread,
    random_stone,
    search_stones,
    stone_curiosity,
    stone_of_day,
    stone_wiki_url,
)
from services.bots import parent_bot_token
from services.stonephoto import confidence_label, guess_stones, identify_from_photo, read_photo_hints
from services.weather import fetch_forecast, format_forecast
from services.earth import (
    fetch_eonet,
    fetch_quakes,
    format_earth_topic,
    format_eonet,
    format_quakes,
    geo_item,
)
from services.lenormand import (
    HINTS as LENO_HINTS,
    SPREADS as LENORMAND_SPREADS,
    draw_lenormand,
    lenormand_closer,
    pair_lines,
)
from services.oracles import (
    DECK_META,
    LUNAR_ORACLE,
    ORACLE_QUESTIONS,
    format_simple_card,
    draw_deck,
    interpret_asked_sky,
    lunar_key,
    surprise_oracle,
    yesno_from_iching_lines,
    yesno_from_rune,
    yesno_from_tarot,
)
from services.runes import draw_runes
from services.sheets import (
    build_quiz,
    catalog_item,
    countdown_it,
    daily_mission,
    format_exo_list,
    format_exoplanet,
    format_habitable,
    format_neo,
    format_sheet,
    load_sheet,
    quiz_levels_text,
    ritual_for_phase,
)
from ui.keyboards import (
    asteroid_chooser_keyboard,
    astronauts_keyboard,
    back_home_keyboard,
    blackholes_keyboard,
    cielo_keyboard,
    comets_keyboard,
    costellazioni_keyboard,
    cosmico_keyboard,
    dwarfs_keyboard,
    eventi_extra_keyboard,
    famous_asteroids_keyboard,
    domanda_keyboard,
    esplora_keyboard,
    nav_row,
    cosmo_keyboard,
    exo_keyboard,
    fav_list_keyboard,
    galaxies_keyboard,
    life_plus_keyboard,
    miss_worlds_keyboard,
    mondi_after_keyboard,
    mondi_hub_keyboard,
    mondi_list_keyboard,
    sistema_chooser_keyboard,
    sistemi_keyboard,
    sistemi_list_keyboard,
    ss_bodies_keyboard,
    all_hub_keyboard,
    astro_hub_keyboard,
    geo_after_keyboard,
    geo_events_keyboard,
    geo_hub_keyboard,
    geo_quakes_keyboard,
    cosmo_hub_keyboard,
    home_keyboard as section_home_keyboard,
    oracolo_hub_keyboard,
    iss_keyboard,
    learn_keyboard,
    lenormand_after_keyboard,
    lenormand_menu_keyboard,
    lenormand_next_keyboard,
    lenormand_ready_keyboard,
    lettura_method_keyboard,
    oracle_question_keyboard,
    meteo_keyboard,
    oracoli_keyboard,
    oracoli_mazzi_keyboard,
    oracle_surprise_after_keyboard,
    place_hub_keyboard,
    place_list_keyboard,
    sky_catalog_keyboard,
    deck_after_keyboard,
    life_keyboard,
    mission_keyboard,
    missions_keyboard,
    moons_keyboard,
    nav_cielo_keyboard,
    nav_me_keyboard,
    nav_risposte_keyboard,
    nav_universo_keyboard,
    planets_keyboard,
    probes_keyboard,
    profondo_keyboard,
    stelle_menu_keyboard,
    quiz_menu_keyboard,
    quiz_options_keyboard,
    random_after_keyboard,
    rune_after_keyboard,
    rune_cast_keyboard,
    rune_draw_keyboard,
    rune_next_keyboard,
    rune_ready_keyboard,
    satellites_keyboard,
    sheet_after_keyboard,
    sole_keyboard,
    world_asksky_keyboard,
    world_div_keyboard,
    world_plates_keyboard,
    world_quake_keyboard,
    world_terra_keyboard,
    world_volc_keyboard,
    world_water_keyboard,
    world_miss_keyboard,
    world_mondi_keyboard,
    world_self_keyboard,
    compat_advanced_keyboard,
    compat_after_keyboard,
    compat_b3_source_keyboard,
    compat_element_keyboard,
    compat_hub_keyboard,
    compat_sign_keyboard,
    world_sky_keyboard,
    world_vita_keyboard,
    world_pietre_keyboard,
    pietre_after_keyboard,
    pietre_colors_keyboard,
    pietre_envs_keyboard,
    pietre_explore_keyboard,
    pietre_games_keyboard,
    pietre_hub_keyboard,
    pietre_lab_keyboard,
    pietre_list_keyboard,
    pietre_museum_keyboard,
    pietre_oracle_keyboard,
    pietre_quiz_keyboard,
    pietre_rarity_keyboard,
    yesno_keyboard,
)
from ui.texts import (
    all_hub_text,
    astro_hub_text,
    geo_hub_text,
    cosmo_hub_text,
    domanda_text,
    esplora_text,
    home_text,
    lettura_text,
    next_bot_text,
    oracolo_hub_text,
    oracoli_text,
    rune_intro_text,
    world_asksky_text,
    world_div_text,
    world_plates_text,
    world_quake_text,
    world_terra_text,
    world_volc_text,
    world_water_text,
    world_miss_text,
    cosmo_text,
    life_plus_text,
    mondi_hub_text,
    sistemi_text,
    world_mondi_text,
    world_self_text,
    compat_advanced_text,
    compat_hub_text,
    world_sky_text,
    world_vita_text,
    world_pietre_text,
    pietre_hub_text,
)
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

# Segno usato dall'oroscopo quando l'utente non ne passa uno.
# Valori ammessi: aries, taurus, gemini, cancer, leo, virgo, libra,
# scorpio, sagittarius, capricorn, aquarius, pisces.
DEFAULT_SIGN = "libra"

# Coordinate di default per Luna e pianeti (Roma). L'Italia merita il suo cielo.
DEFAULT_LAT = 41.9028
DEFAULT_LON = 12.4964
DEFAULT_PLACE_NAME = "Roma"
DEFAULT_TZ = ZoneInfo("Europe/Rome")

# Messaggio unico quando un'API esterna non risponde.
STARS_OFFLINE = "Le stelle sono temporaneamente non raggiungibili ✨ riprova tra poco"

# Timeout HTTP verso le API esterne (secondi).
HTTP_TIMEOUT = 18.0

# Cache breve: le API chiedono di non martellarle, i dati cambiano piano.
CACHE_TTL_SECONDS = 8 * 60

# Limite Telegram per un singolo messaggio di testo / caption foto.
TELEGRAM_MAX_LEN = 3900
TELEGRAM_CAPTION_MAX = 1024

# In chat_data: ultimo messaggio del bot, da sostituire al comando successivo.
LAST_BOT_MSG_KEY = "last_bot_msg"
CIELO_LAST_KEY = "cielo_last"
MONDI_LIST_KEY = "mondi_list"
MONDI_SYS_KEY = "mondi_sys"
MONDI_LAST_KEY = "mondi_last"
MONDI_FAV_KEY = "mondi_fav"
NAV_STACK_KEY = "nav_stack"
NAV_HERE_KEY = "nav_here"
NAV_MAX = 24
NAV_SKIP_EXACT = frozenset(
    {
        "nav:back",
        "miss:ok",
        "tarot:draw",
        "tarot:mix",
        "tarot:next",
        "tarot:board",
        "iching:ready",
        "iching:throw",
        "iching:home",
        "rune:ready",
        "rune:mix",
        "rune:next",
        "rune:board",
        "leno:mix",
        "leno:next",
        "leno:board",
        "natal:calc",
        "natal:notime",
        "natal:homebtn",
        "natal:save",
        "osserva:home",
        "osserva:refresh",
        "oq:wait",
        "md:save",
        "home:menu",
    }
)
NAV_SKIP_PREFIXES = (
    "quiz:ans:",
    "rune:draw:",
    "horo:",
    "yn:",
    "natal:loc:",
    "pt:ga:",
    "pt:la:",
    "pt:g:next",
    "cp:a:",
    "cp:b:",
    "cp:loc:",
    "cp:p:",
    "cp:el:",
    "cp:src:",
)
NAV_HOME_TOKENS = frozenset({"home:menu", "osserva:home", "natal:homebtn", "iching:home"})

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
    "Ceres": ("Cerere", "☄️"),
    "Pallas": ("Pallade", "☄️"),
    "Juno": ("Giunone", "☄️"),
    "Vesta": ("Vesta", "☄️"),
    "Chiron": ("Chirone", "⚷"),
    "Lilith": ("Lilith", "🖤"),
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

WEEKDAYS_IT = (
    "lunedì",
    "martedì",
    "mercoledì",
    "giovedì",
    "venerdì",
    "sabato",
    "domenica",
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
    "Ceres": "nutrimento, cura, ciò che ti sostiene",
    "Pallas": "strategia, intelligenza, come risolvi",
    "Juno": "impegni, alleanze, ciò che tieni insieme",
    "Vesta": "fuoco sacro, concentrazione, ciò che custodisci",
    "Chiron": "ferita e dono, dove insegni ciò che hai curato",
    "Lilith": "parte selvatica, rifiuto, ciò che non si addomestica",
}

ASTEROID_HORIZONS = (
    ("Ceres", "Ceres;"),
    ("Pallas", "Pallas;"),
    ("Juno", "Juno;"),
    ("Vesta", "Vesta;"),
)
NATAL_EXTRA_ASTEROIDS = ("Chiron", "Lilith")

SHOWER_IT = {
    "Quadrantids": "Quadrantidi",
    "Lyrids": "Liridi",
    "Eta Aquariids": "Eta Aquaridi",
    "Delta Aquariids": "Delta Aquaridi",
    "Perseids": "Perseidi",
    "Draconids": "Draconidi",
    "Orionids": "Orionidi",
    "Taurids (South)": "Tauridi australi",
    "Taurids (North)": "Tauridi boreali",
    "Leonids": "Leonidi",
    "Geminids": "Geminidi",
    "Ursids": "Ursidi",
}

EVENT_KIND_IT = {
    "season_start": "stagione",
    "full_moon": "luna piena",
    "new_moon": "luna nuova",
    "ingress": "ingresso",
    "retrograde_start": "inizio retrogrado",
    "retrograde_end": "fine retrogrado",
    "eclipse_solar": "eclissi solare",
    "eclipse_lunar": "eclissi lunare",
    "season": "stagione",
    "solar-eclipse": "eclissi solare",
    "lunar-eclipse": "eclissi lunare",
    "moon-phase": "fase lunare",
    "lunar-apsis": "apside lunare",
}

OSSERVA_CITIES = (
    ("Roma", 41.9028, 12.4964),
    ("Milano", 45.4642, 9.1900),
    ("Napoli", 40.8518, 14.2681),
    ("Torino", 45.0703, 7.6869),
    ("Palermo", 38.1157, 13.3613),
    ("Firenze", 43.7696, 11.2558),
)
PLACE_IT = OSSERVA_CITIES
PLACE_WORLD = (
    ("Londra", 51.5074, -0.1278),
    ("Parigi", 48.8566, 2.3522),
    ("New York", 40.7128, -74.0060),
    ("Los Angeles", 34.0522, -118.2437),
    ("Tokyo", 35.6762, 139.6503),
    ("Pechino", 39.9042, 116.4074),
    ("Delhi", 28.6139, 77.2090),
    ("Il Cairo", 30.0444, 31.2357),
    ("Nairobi", -1.2921, 36.8219),
    ("Sydney", -33.8688, 151.2093),
    ("São Paulo", -23.5505, -46.6333),
    ("Città del Messico", 19.4326, -99.1332),
    ("Istanbul", 41.0082, 28.9784),
    ("Dubai", 25.2048, 55.2708),
    ("Mosca", 55.7558, 37.6173),
    ("Johannesburg", -26.2041, 28.0473),
)
LOC_PURPOSE_KEY = "loc_purpose"
LOC_ASK_KEY = "loc_ask"

NATAL_STATE_KEY = "natal_flow"
COMPAT_STATE_KEY = "compat_flow"
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
    cleaned = name.replace("_", " ").strip()
    mapped = MOON_PHASE_IT.get(cleaned.lower())
    if mapped:
        return mapped
    return event_name_it(cleaned)


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
    return InlineKeyboardMarkup([row, nav_row()])


def format_horoscope_when(period: str, date_value: str) -> str:
    pretty = format_date_it(date_value)
    if period == "weekly":
        return f"settimana dal {pretty}"
    return pretty


TAROT_SPREADS: dict[str, dict[str, Any]] = {
    "one": {
        "count": 1,
        "include_minor": False,
        "title": "Una carta",
        "positions": ("Adesso",),
        "hints": ("Cosa è in gioco in questo momento.",),
        "ready": "Una sola carta. Non serve una domanda: tieni in mente quello che senti.",
    },
    "three": {
        "count": 3,
        "include_minor": True,
        "title": "Tre carte",
        "positions": ("Situazione", "Ostacolo", "Direzione"),
        "hints": ("Dove sei, adesso.", "Cosa frena o confonde.", "Un passo possibile."),
        "ready": "Tre carte, una alla volta: dove sei, cosa ostacola, dove puoi andare.",
    },
    "love": {
        "count": 3,
        "include_minor": True,
        "title": "Amore",
        "positions": ("Tu", "L'altra persona", "Il rapporto"),
        "hints": ("Come stai nel legame.", "Come arriva l'altra persona.", "Cosa succede in mezzo."),
        "ready": "Tre carte sul clima del legame. Non chiedo nomi.",
    },
    "work": {
        "count": 3,
        "include_minor": True,
        "title": "Lavoro",
        "positions": ("Quadro", "Nodo", "Sviluppo"),
        "hints": ("Il lavoro com'è ora.", "Il punto che si è stretto.", "Un possibile sviluppo."),
        "ready": "Tre carte sul lavoro: il quadro, il nodo, un possibile sviluppo.",
    },
    "ask": {
        "count": 3,
        "include_minor": True,
        "title": "Tre carte",
        "positions": ("Situazione", "Ostacolo", "Direzione"),
        "hints": ("Dove sei, adesso.", "Cosa frena o confonde.", "Un passo possibile."),
        "ready": "Tre carte su quello che hai detto alle carte.",
    },
    "day": {
        "count": 1,
        "include_minor": False,
        "title": "Carta del giorno",
        "positions": ("Oggi",),
        "hints": ("Un'indicazione per le prossime ore, non un oroscopo.",),
        "ready": "Una carta per oggi. Poi la lasci andare.",
    },
    "celtic": {
        "count": 10,
        "include_minor": True,
        "title": "Croce Celtica",
        "positions": (
            "Presente",
            "Attraverso",
            "Sotto",
            "Dietro",
            "Sopra",
            "Davanti",
            "Tu",
            "Intorno",
            "Speranze",
            "Esito",
        ),
        "hints": (
            "Il cuore della cosa, ora.",
            "Cosa la attraversa o la blocca.",
            "La base, ciò che sta sotto.",
            "Quello che stai lasciando.",
            "Cosa si affaccia, in alto.",
            "Il prossimo passo visibile.",
            "Come stai tu in tutto questo.",
            "L'ambiente, gli altri.",
            "Cosa speri e cosa temi.",
            "Verso dove tende, se resti così.",
        ),
        "ready": "Dieci carte, una alla volta. Un percorso, non un paragrafo.",
    },
}

TAROT_STATE_KEY = "tarot_flow"
TAROT_HISTORY_MAX = 12
TAROT_HISTORY_PATH = Path("data/tarot_history.json")
_tarot_history_lock = asyncio.Lock()

ICHING_STATE_KEY = "iching_flow"
OSSERVA_STATE_KEY = "osserva_flow"
RUNE_STATE_KEY = "rune_flow"
QUIZ_STATE_KEY = "quiz_flow"
MIRROR_STATE_KEY = "mirror_flow"
LENO_STATE_KEY = "leno_flow"
LETTURA_STATE_KEY = "lettura_flow"
OQ_STATE_KEY = "oq_flow"
STONE_STATE_KEY = "stone_flow"
ICHING_HEX_URLS = (
    "https://raw.githubusercontent.com/jesshewitt/i-ching/main/site/data/hexagrams.json",
    "https://cdn.jsdelivr.net/gh/jesshewitt/i-ching@main/site/data/hexagrams.json",
)
ICHING_YANG = "▬▬▬▬▬▬▬"
ICHING_YIN = "▬▬▬ ▬▬▬"

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
            [_tarot_btn("🃏 Una carta", "tarot:pick:one"), _tarot_btn("🃏 Tre carte", "tarot:pick:three")],
            [_tarot_btn("❤️ Amore", "tarot:pick:love"), _tarot_btn("💼 Lavoro", "tarot:pick:work")],
            [_tarot_btn("☀️ Oggi", "tarot:pick:day"), _tarot_btn("✝️ Croce Celtica", "tarot:pick:celtic")],
            [_tarot_btn("📖 Storico", "tarot:hist")],
            nav_row(),
        ]
    )


def tarot_ready_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_tarot_btn("🃏 Mescola", "tarot:mix")],
            [_tarot_btn("✍️ Una frase, se vuoi", "tarot:phrase")],
            nav_row(),
        ]
    )


def tarot_draw_keyboard() -> InlineKeyboardMarkup:
    return tarot_ready_keyboard()


def tarot_next_keyboard(*, last: bool) -> InlineKeyboardMarkup:
    label = "✨ Il quadro" if last else "🃏 Gira la prossima"
    data = "tarot:board" if last else "tarot:next"
    return InlineKeyboardMarkup([[_tarot_btn(label, data)], nav_row()])


def tarot_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_tarot_btn("🃏 Nuova lettura", "tarot:menu"), _tarot_btn("📖 Storico", "tarot:hist")],
            nav_row(),
        ]
    )


def _tarot_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(TAROT_STATE_KEY, None)


def _tarot_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(TAROT_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[TAROT_STATE_KEY] = state
    return state


def _iching_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(ICHING_STATE_KEY, None)


def _osserva_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(OSSERVA_STATE_KEY, None)


def _rune_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(RUNE_STATE_KEY, None)


def _quiz_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(QUIZ_STATE_KEY, None)


def _mirror_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(MIRROR_STATE_KEY, None)


def _leno_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(LENO_STATE_KEY, None)


def _lettura_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(LETTURA_STATE_KEY, None)


def _oq_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(OQ_STATE_KEY, None)


def _stone_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(STONE_STATE_KEY, None)


def _stone_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(STONE_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[STONE_STATE_KEY] = state
    return state


def _leno_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(LENO_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[LENO_STATE_KEY] = state
    return state


def _lettura_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(LETTURA_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[LETTURA_STATE_KEY] = state
    return state


def _oq_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(OQ_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[OQ_STATE_KEY] = state
    return state


def _rune_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(RUNE_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[RUNE_STATE_KEY] = state
    return state


def _osserva_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(OSSERVA_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[OSSERVA_STATE_KEY] = state
    return state


def _iching_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(ICHING_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[ICHING_STATE_KEY] = state
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


def _compat_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(COMPAT_STATE_KEY, None)


def _compat_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(COMPAT_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[COMPAT_STATE_KEY] = state
    return state


def _flows_reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    _tarot_reset(context)
    _natal_reset(context)
    _compat_reset(context)
    _iching_reset(context)
    _osserva_reset(context)
    _rune_reset(context)
    _quiz_reset(context)
    _mirror_reset(context)
    _leno_reset(context)
    _lettura_reset(context)
    _oq_reset(context)
    _stone_reset(context)
    context.user_data["cielo_ask"] = False


def _nav_should_skip(token: str) -> bool:
    if not token or token in NAV_SKIP_EXACT:
        return True
    return any(token.startswith(prefix) for prefix in NAV_SKIP_PREFIXES)


def nav_clear(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[NAV_STACK_KEY] = []
    context.user_data[NAV_HERE_KEY] = "home:menu"


def nav_mark(context: ContextTypes.DEFAULT_TYPE, token: str) -> None:
    if _nav_should_skip(token):
        if token in NAV_HOME_TOKENS:
            nav_clear(context)
        return
    here = context.user_data.get(NAV_HERE_KEY)
    if here == token:
        return
    if here and here not in NAV_HOME_TOKENS:
        stack = context.user_data.get(NAV_STACK_KEY)
        if not isinstance(stack, list):
            stack = []
        if not stack or stack[-1] != here:
            stack.append(here)
        if len(stack) > NAV_MAX:
            del stack[:-NAV_MAX]
        context.user_data[NAV_STACK_KEY] = stack
    context.user_data[NAV_HERE_KEY] = token


def nav_pop(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    stack = context.user_data.get(NAV_STACK_KEY)
    if not isinstance(stack, list) or not stack:
        context.user_data[NAV_HERE_KEY] = "home:menu"
        return None
    token = stack.pop()
    context.user_data[NAV_STACK_KEY] = stack
    context.user_data[NAV_HERE_KEY] = token if token else "home:menu"
    return token if isinstance(token, str) and token else None


def _cmd_begin(context: ContextTypes.DEFAULT_TYPE, token: str) -> None:
    _flows_reset(context)
    if token not in {"home:menu", "bot:oracolo", "bot:astro", "bot:geo", "bot:cosmo", "bot:next"}:
        here = context.user_data.get(NAV_HERE_KEY)
        if here in {None, "home:menu"}:
            context.user_data[NAV_STACK_KEY] = ["home:menu"]
            context.user_data[NAV_HERE_KEY] = parent_bot_token(token)
    nav_mark(context, token)


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
            [_tarot_btn("❤️ Compatibilità", "cp:hub")],
            [_tarot_btn("☄️ Asteroidi", "natal:asteroids"), _tarot_btn("📊 Profilo", "natal:elements")],
            [_tarot_btn("🔮 Lettura", "natal:read"), _tarot_btn("👤 Il mio tema", "natal:me")],
            nav_row(),
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


async def api_sun_times(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    tz_name: str = "Europe/Rome",
) -> dict[str, Any]:
    cache_key = f"sun:{round(lat, 2)}:{round(lon, 2)}:{datetime.now(DEFAULT_TZ).date()}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(
        client,
        "https://api.sunrisesunset.io/json",
        params={
            "lat": lat,
            "lng": lon,
            "timezone": tz_name,
            "date": "today",
        },
    )
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, dict) or data.get("status") != "OK":
        raise StelleOfflineError("orari solari assenti")
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


async def api_timezone_name(client: httpx.AsyncClient, lat: float, lon: float) -> str:
    cache_key = f"tz:{round(lat, 2)}:{round(lon, 2)}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        data = await fetch_json(
            client,
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "timezone": "auto"},
        )
    except StelleOfflineError:
        return str(DEFAULT_TZ)
    tz = str((data or {}).get("timezone") or "").strip()
    return cache_set(cache_key, tz or str(DEFAULT_TZ))


def parse_horizons_lon(result: str) -> float:
    if "$$SOE" not in result or "$$EOE" not in result:
        raise StelleOfflineError("orizzonti senza tabella")
    chunk = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    for line in chunk.splitlines():
        parts = [p.strip() for p in line.split(",")]
        nums: list[float] = []
        for part in parts[1:]:
            if not part:
                continue
            try:
                nums.append(float(part))
            except ValueError:
                continue
        if nums:
            return nums[0] % 360.0
    raise StelleOfflineError("orizzonti senza longitudine")


async def api_horizons_lon(
    client: httpx.AsyncClient,
    command: str,
    when_utc: datetime,
) -> float:
    stamp = when_utc.strftime("%Y-%m-%d %H:%M")
    cache_key = f"horiz:{command}:{stamp}"
    cached = cache_get(cache_key)
    if cached is not None:
        return float(cached)
    end = when_utc + timedelta(minutes=1)
    data = await fetch_json(
        client,
        "https://ssd.jpl.nasa.gov/api/horizons.api",
        params={
            "format": "json",
            "COMMAND": command,
            "OBJ_DATA": "NO",
            "MAKE_EPHEM": "YES",
            "EPHEM_TYPE": "OBSERVER",
            "CENTER": "500@399",
            "START_TIME": f"'{stamp}'",
            "STOP_TIME": f"'{end.strftime('%Y-%m-%d %H:%M')}'",
            "STEP_SIZE": "1m",
            "QUANTITIES": "31",
            "ANG_FORMAT": "DEG",
            "CSV_FORMAT": "YES",
        },
    )
    if not isinstance(data, dict) or data.get("error"):
        raise StelleOfflineError(str((data or {}).get("error") or "orizzonti"))
    lon = parse_horizons_lon(str(data.get("result") or ""))
    return cache_set(cache_key, lon)


async def api_meteor_showers(client: httpx.AsyncClient) -> list[dict[str, Any]]:
    cache_key = f"showers:{datetime.now(DEFAULT_TZ).year}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(client, "https://skytime.live/api/v1/meteor-showers")
    showers = (data.get("data") or {}).get("showers") if isinstance(data, dict) else None
    if not isinstance(showers, list) or not showers:
        raise StelleOfflineError("sciami vuoti")
    clean = [item for item in showers if isinstance(item, dict) and item.get("name")]
    if not clean:
        raise StelleOfflineError("sciami vuoti")
    return cache_set(cache_key, clean)


async def api_skytime_events(client: httpx.AsyncClient, year: int) -> list[dict[str, Any]]:
    cache_key = f"skyev:{year}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(
        client,
        "https://skytime.live/api/v1/astronomical-events",
        params={"year": year},
    )
    events = (data.get("data") or {}).get("events") if isinstance(data, dict) else None
    if not isinstance(events, list):
        raise StelleOfflineError("eventi skytime vuoti")
    return cache_set(cache_key, [item for item in events if isinstance(item, dict)])


async def api_cosmyday_events(client: httpx.AsyncClient, days: int = 21) -> list[dict[str, Any]]:
    cache_key = f"cmev:{datetime.now(DEFAULT_TZ).date()}:{days}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    data = await fetch_json(
        client,
        "https://api.cosmyday.com/events/upcoming",
        params={"days": days, "min_importance": 40, "limit": 12},
    )
    events = data.get("events") if isinstance(data, dict) else None
    if not isinstance(events, list):
        raise StelleOfflineError("eventi cosmyday vuoti")
    return cache_set(cache_key, [item for item in events if isinstance(item, dict)])


async def api_skymap(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    when_utc: datetime | None = None,
) -> dict[str, Any]:
    place = f"{lat:.2f},{lon:.2f}"
    stamp = when_utc.strftime("%Y-%m-%dT%H:%MZ") if when_utc else "now"
    cache_key = f"skymap:{place}:{stamp}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    params: dict[str, Any] = {"format": "json"}
    if when_utc is not None:
        params["t"] = when_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    data = await fetch_json(
        client,
        f"https://skymap.sh/{quote(place, safe=',')}",
        params=params,
    )
    if not isinstance(data, dict) or data.get("error"):
        raise StelleOfflineError(str((data or {}).get("error") or "skymap"))
    return cache_set(cache_key, data)


def house_for_lon(lon: float, cusps: list[float]) -> int | None:
    if len(cusps) < 12:
        return None
    lon = float(lon) % 360.0
    for idx in range(12):
        start = float(cusps[idx]) % 360.0
        end = float(cusps[(idx + 1) % 12]) % 360.0
        if start <= end:
            if start <= lon < end:
                return idx + 1
        elif lon >= start or lon < end:
            return idx + 1
    return 12


def format_day_it(dt: datetime) -> str:
    return f"{WEEKDAYS_IT[dt.weekday()]} {dt.day} {MONTHS_IT[dt.month - 1]} {dt.year}"


def shower_it_name(name: str) -> str:
    return SHOWER_IT.get(name, name)


def shower_peak_date(shower: dict[str, Any], year: int) -> datetime | None:
    try:
        month = int(shower.get("peakMonth")) + 1
        day = int(shower.get("peakDay"))
        return datetime(year, month, day, tzinfo=DEFAULT_TZ)
    except (TypeError, ValueError):
        return None


def upcoming_showers(showers: list[dict[str, Any]], now: datetime, limit: int = 6) -> list[tuple[datetime, dict[str, Any]]]:
    today = now.date()
    dated: list[tuple[datetime, dict[str, Any]]] = []
    for shower in showers:
        peak = shower_peak_date(shower, today.year)
        if peak is None:
            continue
        if peak.date() < today:
            peak = shower_peak_date(shower, today.year + 1)
            if peak is None:
                continue
        dated.append((peak, shower))
    dated.sort(key=lambda item: item[0])
    return dated[:limit]


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
    await reply_html(update, context, STARS_OFFLINE, reply_markup=back_home_keyboard())


async def show_loading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Riusa lo stesso messaggio mentre arrivano i dati live."""
    await deliver_text(update, context, "⏳ Un attimo, sto interrogando il cielo…")


def start_text() -> str:
    return all_hub_text()


def help_text() -> str:
    default_it, default_emoji, _ = ZODIAC[DEFAULT_SIGN]
    return (
        "🪐 <b>BOTSQUAD</b>\n"
        "<i>Tre bot, un Telegram. Si naviga a pulsanti. Nel menu restano /start e /aiuto.</i>\n\n"
        "🔮 <b>ORACOLO</b> — Te stesso (oroscopo, tema natale, specchio, "
        "compatibilità), Consultazioni (tarocchi, I Ching, rune, Lenormand, "
        "sì/no, pietra del giorno) e Interroga il cielo (lettura simbolica "
        "sopra la tua città).\n"
        "🔭 <b>ASTRO</b> — osservatorio: Cielo, Meteo mondiale, Mondi, Vita, "
        "Missioni. Niente divinazione.\n"
        "🌍 <b>GEO</b> — la Terra: pietre, terremoti USGS, vulcani, oceani, "
        "placche, eventi NASA EONET.\n\n"
        f"Oroscopo: scegli il segno dai pulsanti. Se non ne indichi uno "
        f"uso {default_emoji} {default_it}. Puoi anche scrivere solo il "
        "nome del segno in chat.\n\n"
        "⬅️ <b>Indietro</b> torna al menu precedente. "
        "🏠 <b>Inizio</b> è sempre BOTSQUAD.\n"
        f"Se un'API cade: <i>{e(STARS_OFFLINE)}</i>"
    )


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


async def show_all_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nav_clear(context)
    await reply_html(update, context, all_hub_text(), reply_markup=all_hub_keyboard())


async def show_oracolo_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nav_mark(context, "bot:oracolo")
    await reply_html(update, context, oracolo_hub_text(), reply_markup=oracolo_hub_keyboard())


async def show_astro_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nav_mark(context, "bot:astro")
    await reply_html(update, context, astro_hub_text(), reply_markup=astro_hub_keyboard())


async def show_geo_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nav_mark(context, "bot:geo")
    await reply_html(update, context, geo_hub_text(), reply_markup=geo_hub_keyboard())


async def show_cosmo_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_oracolo_hub(update, context)


async def show_next_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_astro_hub(update, context)


async def on_bot_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    await query.answer()
    if action in {"oracolo", "cosmo"}:
        await show_oracolo_hub(update, context)
        return
    if action in {"astro", "next"}:
        await show_astro_hub(update, context)
        return
    if action == "geo":
        await show_geo_hub(update, context)
        return
    await show_all_hub(update, context)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await show_all_hub(update, context)
    await delete_user_command(update)


async def cmd_aiuto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:aiuto")
    await reply_html(update, context, help_text(), reply_markup=back_home_keyboard())
    await delete_user_command(update)


async def cmd_oroscopo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args) if context.args else ""
    await begin_oroscopo(update, context, raw)


async def begin_oroscopo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raw: str,
) -> None:
    _cmd_begin(context, "home:oroscopo")
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
        await query.answer("Bottone stanco. Torna a Inizio e tocca di nuovo.")
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
    nav_mark(context, "tarot:menu")
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
        "giorno": "day",
        "day": "day",
        "celtica": "celtic",
        "croce": "celtic",
        "celtic": "celtic",
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
        "🃏 <b>TAROCCHI</b>\n"
        "<i>Mazzo live, Rider–Waite. Scegli come pescare. Non serve una domanda.</i>\n\n"
        "🃏 Una · 🃏 Tre · ❤️ Amore · 💼 Lavoro · ☀️ Oggi\n"
        "✝️ Croce Celtica — dieci carte, una alla volta."
    )
    await reply_html(update, context, text, reply_markup=tarot_menu_keyboard())


async def show_tarot_ask_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _tarot_state(context)
    if not state.get("spread"):
        state["spread"] = "three"
    state["awaiting_question"] = True
    await reply_html(
        update,
        context,
        "🃏 <b>Una frase alle carte</b>\n"
        "<i>Non è un esame e non è obbligatoria.</i>\n\n"
        "Se vuoi, scrivi una riga. Serve solo a te, per ricordare il clima. "
        "Poi mescoliamo lo stesso.",
        reply_markup=InlineKeyboardMarkup(
            [[_tarot_btn("🃏 Meglio senza", "tarot:mix")], nav_row()]
        ),
    )


async def show_tarot_ritual(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    spread: str,
    *,
    question: str | None = None,
) -> None:
    await show_tarot_ready(update, context, spread, phrase=question)


async def show_tarot_ready(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    spread: str,
    *,
    phrase: str | None = None,
) -> None:
    if spread not in TAROT_SPREADS:
        spread = "three"
    if spread == "ask":
        spread = "three"
    meta = TAROT_SPREADS[spread]
    state = _tarot_state(context)
    keep_phrase = str(state.get("question") or "").strip()
    state.clear()
    state["spread"] = spread
    state["step"] = "ready"
    state["awaiting_question"] = False
    if phrase:
        state["question"] = clip_text(phrase, 400)
    elif keep_phrase:
        state["question"] = keep_phrase
    text = (
        f"🃏 <b>{e(meta['title'])}</b>\n"
        f"<i>{e(meta['ready'])}</i>\n\n"
        f"{int(meta['count'])} carte. Le giriamo una alla volta."
    )
    if state.get("question"):
        text += f"\n\nHai detto: <i>«{e(state['question'])}»</i>"
    await reply_html(update, context, text, reply_markup=tarot_ready_keyboard())


async def receive_tarot_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    question: str,
) -> None:
    phrase = clip_text(question.strip(), 400)
    if not phrase:
        await reply_html(update, context, "Una riga basta. Oppure tocca Mescola, senza frase.")
        return
    spread = str(_tarot_state(context).get("spread") or "three")
    await show_tarot_ready(update, context, spread, phrase=phrase)
    await delete_user_command(update)


async def _tarot_localize_card(
    client: httpx.AsyncClient,
    card: dict[str, Any],
    *,
    reversed_card: bool,
    position: str,
    hint: str,
) -> dict[str, str]:
    name_en = str(card.get("name") or "Carta")
    meaning_en = str(card.get("meaning_rev" if reversed_card else "meaning_up") or "")
    name_it = await translate_to_italian(client, name_en)
    meaning_it = await translate_to_italian(client, meaning_en) if meaning_en else "—"
    return {
        "name_en": name_en,
        "name_it": name_it,
        "position": position,
        "hint": hint,
        "kind": "arcano maggiore" if str(card.get("type") or "") == "major" else "arcano minore",
        "reversed": "1" if reversed_card else "0",
        "emoji": tarot_card_emoji(name_en),
        "meaning_it": first_sentences(meaning_it, 2, 240) or "—",
        "meaning_en": meaning_en,
    }


def _format_tarot_card(item: dict[str, str], *, idx: int, total: int) -> str:
    rev = "rovesciata" if item["reversed"] == "1" else "diritta"
    return (
        f"🃏 <b>{e(item['position'])}</b>  ·  {idx}/{total}\n"
        f"{item['emoji']} <b>{e(item['name_it'])}</b>\n"
        f"<i>{e(rev)} · {e(item['kind'])}</i>\n\n"
        f"{e(item.get('hint') or '')}\n\n"
        f"{e(item['meaning_it'])}"
    )


async def start_tarot_mix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _tarot_state(context)
    spread = str(state.get("spread") or "")
    if spread not in TAROT_SPREADS:
        await show_tarot_menu(update, context)
        return
    meta = TAROT_SPREADS[spread]
    state["awaiting_question"] = False
    await send_typing(update)
    await deliver_text(update, context, "🃏 Apro il mazzo…")
    await asyncio.sleep(0.35)
    await deliver_text(update, context, "🃏 Mescolando…")
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
            "Il mazzo live non ha risposto. Riprova a mescolare.",
            reply_markup=tarot_ready_keyboard(),
        )
        return
    need = int(meta["count"])
    cards = list(cards[:need])
    if len(cards) < need:
        await reply_html(
            update,
            context,
            "Il mazzo ha dato poche carte. Riprova a mescolare.",
            reply_markup=tarot_ready_keyboard(),
        )
        return
    state["raw"] = cards
    state["orients"] = [bool(random.choice((False, True))) for _ in cards]
    state["shown"] = []
    state["index"] = 0
    state["step"] = "reveal"
    await asyncio.sleep(0.3)
    await deliver_text(update, context, "🃏 Taglio il mazzo…")
    await asyncio.sleep(0.28)
    await reveal_tarot_card(update, context)


async def reveal_tarot_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _tarot_state(context)
    spread = str(state.get("spread") or "")
    meta = TAROT_SPREADS.get(spread)
    raw = state.get("raw") if isinstance(state.get("raw"), list) else []
    orients = state.get("orients") if isinstance(state.get("orients"), list) else []
    shown = state.setdefault("shown", [])
    if not isinstance(shown, list):
        shown = []
        state["shown"] = shown
    if not meta or not raw:
        await show_tarot_menu(update, context)
        return
    idx = int(state.get("index") or 0)
    if idx < 0 or idx >= len(raw):
        await show_tarot_quadro(update, context)
        return
    positions = tuple(meta["positions"])
    hints = tuple(meta.get("hints") or ())
    client = _http_client(context)
    await send_typing(update)
    item = await _tarot_localize_card(
        client,
        raw[idx] if isinstance(raw[idx], dict) else {},
        reversed_card=bool(orients[idx]) if idx < len(orients) else False,
        position=str(positions[idx] if idx < len(positions) else f"Carta {idx + 1}"),
        hint=str(hints[idx] if idx < len(hints) else ""),
    )
    shown.append(item)
    state["index"] = idx + 1
    total = int(meta["count"])
    left = total - (idx + 1)
    text = _format_tarot_card(item, idx=idx + 1, total=total)
    if left:
        text += f"\n\n<i>Restano {left} carte. Girale quando vuoi.</i>"
    else:
        text += "\n\n<i>Ultima carta. Poi il quadro e l'interpretazione.</i>"
    await reply_html(update, context, text, reply_markup=tarot_next_keyboard(last=left == 0))


def interpret_tarot(shown: list[Any], spread: str, phrase: str = "") -> str:
    cards = [item for item in shown if isinstance(item, dict)]
    if not cards:
        return "Il mazzo non ha lasciato carte da leggere."

    def _orient(item: dict[str, Any]) -> str:
        return "rovesciata" if item.get("reversed") == "1" else "diritta"

    def _name(item: dict[str, Any]) -> str:
        return str(item.get("name_it") or "Carta")

    def _pos(item: dict[str, Any]) -> str:
        return str(item.get("position") or "Carta")

    def _mean(item: dict[str, Any], limit: int = 120) -> str:
        raw = str(item.get("meaning_it") or "").strip()
        if not raw or raw == "—":
            raw = str(item.get("hint") or "").strip()
        return first_sentences(raw, 1, limit)

    if len(cards) == 1:
        item = cards[0]
        return (
            f"È uscita {_name(item)} {_orient(item)}, in {_pos(item)}. "
            f"{_mean(item, 180)} "
            "Tienila come clima di queste ore, non come verdetto."
        )

    if spread == "celtic" and len(cards) >= 6:
        presente, attraverso, esito = cards[0], cards[1], cards[-1]
        bits = [
            f"Il presente è {_name(presente)} {_orient(presente)}: {_mean(presente, 110)}",
            f"Attraverso passa {_name(attraverso)} {_orient(attraverso)}: {_mean(attraverso, 110)}",
        ]
        if len(cards) > 6:
            tu = cards[6]
            bits.append(f"Tu, in questo quadro, sei {_name(tu)} {_orient(tu)}: {_mean(tu, 100)}")
        bits.append(
            f"L'esito verso cui tende è {_name(esito)} {_orient(esito)}: {_mean(esito, 110)}"
        )
        rev = sum(1 for card in cards if card.get("reversed") == "1")
        if rev:
            bits.append(
                f"{rev} carte sono rovesciate: la tradizione le legge come tema interno "
                "o in ritardo, non come sfortuna."
            )
        bits.append("Dieci carte, un percorso. Non un destino chiuso.")
        return clip_text(" ".join(bits), 1200)

    pieces = [
        f"In {_pos(item)} è uscita {_name(item)} {_orient(item)}: {_mean(item, 120)}"
        for item in cards
    ]
    last = cards[-1]
    if spread == "love":
        closer = (
            f"Il rapporto si legge nella terza carta: {_name(last)}. "
            "È il clima del legame, non una sentenza su di voi."
        )
    elif spread == "work":
        closer = (
            f"Lo sviluppo guarda {_name(last)}. "
            "Il passo da tenere è l'ultima carta, non il nodo."
        )
    else:
        closer = (
            f"Si parte da {_name(cards[0])} e si arriva a {_name(last)}. "
            "L'ultima carta è il passo da guardare."
        )
    rev = sum(1 for card in cards if card.get("reversed") == "1")
    if rev == 1:
        closer += (
            " Una carta è rovesciata: la tradizione la legge come tema interno "
            "o in ritardo, non come sfortuna."
        )
    elif rev > 1:
        closer += (
            f" {rev} carte sono rovesciate: la tradizione le legge come tema interno "
            "o in ritardo, non come sfortuna."
        )
    if phrase:
        closer += " Rileggi quello che hai detto alle carte alla luce di queste uscite."
    return clip_text(" ".join(pieces) + " " + closer, 1200)


async def show_tarot_quadro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _tarot_state(context)
    spread = str(state.get("spread") or "")
    meta = TAROT_SPREADS.get(spread) or TAROT_SPREADS["three"]
    shown = state.get("shown") if isinstance(state.get("shown"), list) else []
    if not shown:
        await show_tarot_menu(update, context)
        return
    lines = [
        f"🃏 <b>{e(meta['title'])}</b>",
        "<i>Il quadro: i nomi, poi cosa dicono insieme.</i>",
        "",
    ]
    phrase = str(state.get("question") or "").strip()
    if phrase:
        lines.append(f"Hai detto: <i>«{e(phrase)}»</i>")
        lines.append("")
    for idx, item in enumerate(shown, start=1):
        if not isinstance(item, dict):
            continue
        rev = "R" if item.get("reversed") == "1" else "D"
        lines.append(
            f"{idx}. {e(str(item.get('position') or ''))} — "
            f"{item.get('emoji') or '🃏'} {e(str(item.get('name_it') or 'Carta'))} ({rev})"
        )
    lines.extend(
        [
            "",
            "✨ <b>IN PRATICA</b>",
            e(interpret_tarot(shown, spread, phrase)),
            "",
            "<i>D = diritta, R = rovesciata. Un mazzo live, non un verdetto.</i>",
        ]
    )
    user = update.effective_user
    if user is not None:
        await tarot_history_add(
            user.id,
            {
                "at": datetime.now(DEFAULT_TZ).isoformat(timespec="minutes"),
                "spread": spread,
                "title": meta["title"],
                "question": phrase or None,
                "cards": [
                    {
                        "name": item.get("name_it"),
                        "position": item.get("position"),
                        "reversed": item.get("reversed") == "1",
                    }
                    for item in shown
                    if isinstance(item, dict)
                ],
            },
        )
    state["step"] = "done"
    await reply_html(update, context, "\n".join(lines), reply_markup=tarot_after_keyboard())


async def send_tarot_draw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fai scegliere all'oracolo e vecchio bottone pesca: parte il mescolo."""
    await start_tarot_mix(update, context)


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
    if action == "phrase":
        await query.answer()
        await show_tarot_ask_prompt(update, context)
        return
    if action == "pick" and extra in TAROT_SPREADS:
        await query.answer()
        await show_tarot_ready(update, context, extra)
        return
    if action in {"draw", "mix"}:
        await query.answer("Mescolando…")
        await start_tarot_mix(update, context)
        return
    if action == "next":
        await query.answer()
        await reveal_tarot_card(update, context)
        return
    if action == "board":
        await query.answer()
        await show_tarot_quadro(update, context)
        return
    await query.answer("Bottone stanco. Torna a Inizio e tocca di nuovo.")


# ---------------------------------------------------------------------------
# I Ching — domanda → rituale → sei lanci → esagramma → linee mutevoli
# Testi Wilhelm 1924 da JSON pubblico; le monete si lanciano qui (3 monete).
# ---------------------------------------------------------------------------


def iching_ready_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_tarot_btn("✨ SONO PRONTO", "iching:ready")], nav_row()])


def iching_throw_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_tarot_btn("🪙 LANCIA LE MONETE", "iching:throw")], nav_row()])


def iching_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_tarot_btn("☯️ Nuova consultazione", "iching:new")],
            nav_row(),
        ]
    )


def throw_iching_coins() -> int:
    """Tre monete: testa=3, croce=2 → 6/7/8/9 (metodo classico)."""
    return sum(3 if random.random() < 0.5 else 2 for _ in range(3))


def cast_iching_lines() -> list[int]:
    """Sei linee dal basso verso l'alto, come nella tradizione."""
    return [throw_iching_coins() for _ in range(6)]


def lines_to_value(lines: list[int], *, transformed: bool = False) -> str:
    bits: list[str] = []
    for number in lines:
        yang = number in (7, 9)
        if transformed and number in (6, 9):
            yang = not yang
        bits.append("7" if yang else "8")
    return "".join(reversed(bits))


def changing_line_numbers(lines: list[int]) -> list[int]:
    return [idx + 1 for idx, number in enumerate(lines) if number in (6, 9)]


def render_hexagram(lines: list[int]) -> str:
    rows: list[str] = []
    for number in reversed(lines):
        rows.append(ICHING_YANG if number in (7, 9) else ICHING_YIN)
    return "\n".join(rows)


def hex_short_name(ename: str) -> str:
    cleaned = re.sub(r"\s*\([^)]*\)\s*", " ", ename).strip()
    return re.sub(r"\s+", " ", cleaned) or ename


def first_sentences(text: str, count: int = 1, limit: int = 280) -> str:
    compact = re.sub(r"\s+", " ", (text or "").strip())
    if not compact:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", compact)
    out = " ".join(parts[: max(1, count)]).strip()
    return clip_text(out, limit)


def clean_line_oracle(raw: str) -> str:
    text = (raw or "").strip()
    text = re.sub(r"^A (nine|six)[^\n]*means:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^When all lines are (nines|sixes), this means:\s*", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def it_changing_sentence(nums: list[int]) -> str:
    labels = [f"{n}ª" for n in nums]
    if not labels:
        return "Non ci sono linee mutevoli: l'esagramma si legge così com'è."
    if len(labels) == 1:
        return f"La {labels[0]} linea è mutevole."
    if len(labels) == 2:
        return f"La {labels[0]} e la {labels[1]} linea sono mutevoli."
    *rest, last = labels
    return "La " + ", la ".join(rest) + f" e la {last} linea sono mutevoli."


def _index_hexagrams(raw: Any) -> dict[str, dict[int | str, dict[str, Any]]]:
    if not isinstance(raw, list):
        raise StelleOfflineError("libro I Ching non valido")
    by_id: dict[int, dict[str, Any]] = {}
    by_value: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            hid = int(item.get("id") or 0)
        except (TypeError, ValueError):
            continue
        value = str(item.get("value") or "").strip()
        if hid < 1 or hid > 64 or len(value) != 6:
            continue
        by_id[hid] = item
        by_value[value] = item
    if len(by_id) < 64:
        raise StelleOfflineError("libro I Ching incompleto")
    return {"by_id": by_id, "by_value": by_value}


async def api_iching_book(
    client: httpx.AsyncClient,
    context: ContextTypes.DEFAULT_TYPE | None = None,
) -> dict[str, dict[int | str, dict[str, Any]]]:
    if context is not None:
        cached = context.bot_data.get("iching_book")
        if isinstance(cached, dict) and cached.get("by_id"):
            return cached
    last_error: Exception | None = None
    for url in ICHING_HEX_URLS:
        try:
            raw = await fetch_json(client, url)
            book = _index_hexagrams(raw)
            if context is not None:
                context.bot_data["iching_book"] = book
            return book
        except StelleOfflineError as exc:
            last_error = exc
            logger.warning("I Ching: fonte %s non disponibile: %s", url, exc)
    raise StelleOfflineError("libro I Ching offline") from last_error


def hex_from_lines(
    book: dict[str, dict[int | str, dict[str, Any]]],
    lines: list[int],
    *,
    transformed: bool = False,
) -> dict[str, Any]:
    value = lines_to_value(lines, transformed=transformed)
    item = book["by_value"].get(value)
    if not isinstance(item, dict):
        raise StelleOfflineError("esagramma non trovato nel libro")
    return item


def changing_oracles(hexagram: dict[str, Any], lines: list[int]) -> list[dict[str, str]]:
    raw_lines = hexagram.get("lines")
    if not isinstance(raw_lines, list):
        raw_lines = []
    out: list[dict[str, str]] = []
    changing = changing_line_numbers(lines)
    for num in changing:
        text = ""
        if num - 1 < len(raw_lines):
            text = clean_line_oracle(str(raw_lines[num - 1] or ""))
        if text:
            out.append({"n": str(num), "text": text})
    if len(changing) == 6 and len(raw_lines) > 6:
        extra = clean_line_oracle(str(raw_lines[6] or ""))
        if extra:
            out.append({"n": "tutte", "text": extra})
    return out


def build_iching_reading_en(
    question: str,
    primary: dict[str, Any],
    changing: list[dict[str, str]],
    transformed: dict[str, Any] | None,
) -> str:
    name = hex_short_name(str(primary.get("ename") or "Hexagram"))
    hid = int(primary.get("id") or 0)
    theme = first_sentences(str(primary.get("commentary") or ""), 1, 320)
    judgment = first_sentences(str(primary.get("judgment") or ""), 3, 360)
    pieces = [
        f'The question is: "{question}".',
        f"The I Ching answers with hexagram {hid} — {name}.",
    ]
    if theme:
        pieces.append(theme)
    if judgment:
        pieces.append(f"The Judgment says: {judgment}")
    if changing:
        pieces.append("The situation is not static. These changing lines speak:")
        for item in changing:
            label = "All lines together" if item["n"] == "tutte" else f"Line {item['n']}"
            pieces.append(f"{label}: {item['text']}")
        if transformed is not None:
            tname = hex_short_name(str(transformed.get("ename") or "Hexagram"))
            tid = int(transformed.get("id") or 0)
            tjud = first_sentences(str(transformed.get("judgment") or ""), 3, 320)
            pieces.append(
                f"The original hexagram describes the present situation. "
                f"After the changing lines it becomes hexagram {tid} — {tname}, "
                f"the symbolic direction indicated by the change."
            )
            if tjud:
                pieces.append(f"Its Judgment: {tjud}")
    else:
        pieces.append(
            "There are no changing lines. The hexagram is read as a still image of the situation."
        )
    return " ".join(pieces)


async def _iching_blank() -> str:
    return ""


def iching_final_en(primary: dict[str, Any], transformed: dict[str, Any] | None) -> str:
    source = transformed if transformed is not None else primary
    image = first_sentences(str(source.get("image") or ""), 2, 280)
    if image:
        return image
    return first_sentences(str(source.get("judgment") or ""), 2, 240)


async def cmd_iching(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "iching:open")
    await show_iching_intro(update, context)
    await delete_user_command(update)


async def show_iching_intro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _iching_state(context)
    state.clear()
    state["step"] = "intro"
    text = (
        "☯️ <b>I CHING</b>\n\n"
        "L'I Ching può essere usato come strumento di riflessione sulla "
        "situazione che stai vivendo.\n\n"
        "Pensa a una domanda precisa.\n\n"
        "Non deve essere necessariamente una domanda con risposta sì/no.\n\n"
        "Quando hai formulato la domanda, premi il pulsante."
    )
    await reply_html(update, context, text, reply_markup=iching_ready_keyboard())


async def show_iching_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _iching_state(context)
    state["step"] = "ask"
    state.pop("question", None)
    text = (
        "☯️ <b>Qual è la tua domanda?</b>\n\n"
        "Scrivila in un messaggio.\n\n"
        "Esempio:\n"
        "<i>Cosa dovrei comprendere della situazione che sto vivendo?</i>"
    )
    await reply_html(update, context, text, reply_markup=InlineKeyboardMarkup([nav_row()]))


async def show_iching_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _iching_state(context)
    question = str(state.get("question") or "").strip()
    if not question:
        await show_iching_ask(update, context)
        return
    state["step"] = "confirm"
    text = (
        "☯️ <b>La tua domanda</b>\n\n"
        f"<i>«{e(question)}»</i>\n\n"
        "Concentrati ancora qualche secondo.\n\n"
        "Quando sei pronto, lanceremo le monete."
    )
    await reply_html(update, context, text, reply_markup=iching_throw_keyboard())


async def receive_iching_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    question: str,
) -> None:
    question = clip_text(question.strip(), 400)
    if len(question) < 8:
        await reply_html(
            update,
            context,
            "☯️ Serve una domanda un po' più chiara, anche una sola frase.\n"
            "Esempio: <i>Cosa dovrei comprendere della situazione che sto vivendo?</i>",
        )
        return
    state = _iching_state(context)
    state["question"] = question
    await show_iching_confirm(update, context)
    await delete_user_command(update)


async def send_iching_cast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _iching_state(context)
    question = str(state.get("question") or "").strip()
    if not question:
        await show_iching_ask(update, context)
        return
    state["step"] = "throw"
    lines = cast_iching_lines()
    state["lines"] = lines

    await send_typing(update)
    animate = bool(state.pop("animate", True))
    if animate:
        progress = ["☯️ <b>I sei lanci</b>", "", "Le linee si costruiscono dal basso verso l'alto.", ""]
        await deliver_text(update, context, "\n".join(progress + ["🪙 Le monete sono in mano…"]))
        for idx in range(1, 7):
            progress.append(f"🪙 Lancio {idx}...")
            await asyncio.sleep(0.38)
            await deliver_text(update, context, "\n".join(progress))
        await asyncio.sleep(0.25)
        await deliver_text(update, context, "📖 Apro il libro dei mutamenti…")
    else:
        await deliver_text(update, context, "☯️ Lancio le monete e apro il libro…")
    client = _http_client(context)
    try:
        book = await api_iching_book(client, context)
        primary = hex_from_lines(book, lines)
        changing_nums = changing_line_numbers(lines)
        transformed = hex_from_lines(book, lines, transformed=True) if changing_nums else None
        if transformed is not None and int(transformed.get("id") or 0) == int(primary.get("id") or 0):
            transformed = None
        oracles = changing_oracles(primary, lines)
        name_en = hex_short_name(str(primary.get("ename") or "Hexagram"))
        tname_en = hex_short_name(str((transformed or {}).get("ename") or "Hexagram"))
        judgment_en = first_sentences(str(primary.get("judgment") or ""), 3, 400)
        tjud_en = first_sentences(str((transformed or {}).get("judgment") or ""), 3, 360) if transformed else ""
        name_it, tname_it, judgment_it, tjud_it = await asyncio.gather(
            translate_to_italian(client, name_en),
            translate_to_italian(client, tname_en) if transformed else _iching_blank(),
            translate_to_italian(client, judgment_en) if judgment_en else _iching_blank(),
            translate_to_italian(client, tjud_en) if tjud_en else _iching_blank(),
        )
        now_text = first_sentences(judgment_it, 2, 260)
        toward_text = first_sentences(tjud_it, 2, 220) if tjud_it else ""
        line_notes: list[tuple[str, str]] = []
        for item in oracles:
            raw = str(item.get("text") or "")
            label = "tutte" if item.get("n") == "tutte" else f"{item.get('n')}ª"
            if not raw:
                continue
            note_it = first_sentences(await translate_to_italian(client, raw), 1, 180)
            if note_it:
                line_notes.append((label, note_it))
        pratica = iching_in_pratica(
            name_it or name_en,
            now_text,
            (tname_it or tname_en) if transformed else "",
            toward_text,
            changing_nums,
        )
    except StelleOfflineError:
        logger.exception("I Ching: libro o traduzione non disponibili")
        await reply_html(
            update,
            context,
            "Le stelle sono temporaneamente non raggiungibili ✨ riprova tra poco\n\n"
            "Il libro dei mutamenti non ha risposto. Puoi rilanciare le monete.",
            reply_markup=iching_throw_keyboard(),
        )
        return

    primary_id = int(primary.get("id") or 0)
    transformed_id = int(transformed.get("id") or 0) if transformed else 0
    text = format_iching_result(
        question=question,
        lines=lines,
        primary_id=primary_id,
        primary_name=name_it or name_en,
        changing=changing_nums,
        line_notes=line_notes,
        transformed_id=transformed_id,
        transformed_name=(tname_it or tname_en) if transformed else "",
        now_text=now_text,
        toward_text=toward_text,
        pratica=pratica,
    )
    state["step"] = "done"
    await reply_html(update, context, text, reply_markup=iching_after_keyboard())


def iching_in_pratica(
    name: str,
    now_text: str,
    toward_name: str,
    toward_text: str,
    changing: list[int],
) -> str:
    now = first_sentences(now_text, 1, 180)
    if toward_name and toward_text:
        return (
            f"Ora sei in {name}. Il libro non si ferma lì: le linee mutevoli "
            f"indicano un passaggio verso {toward_name}. "
            f"{first_sentences(toward_text, 1, 180)}"
        )
    if changing:
        extra = f" {now}" if now else ""
        return (
            f"{name} è in movimento.{extra} "
            "Le linee che cambiano dicono dove si incrina, non il destino."
        )
    extra = f" {now}" if now else ""
    return f"{name} sta fermo: niente linee mutevoli.{extra} Si legge così, senza trasformazione."


def format_iching_result(
    *,
    question: str,
    lines: list[int],
    primary_id: int,
    primary_name: str,
    changing: list[int],
    line_notes: list[tuple[str, str]],
    transformed_id: int,
    transformed_name: str,
    now_text: str,
    toward_text: str,
    pratica: str,
) -> str:
    graphic = render_hexagram(lines)
    blocks = [
        "☯️ <b>I CHING</b>",
        f"<b>{primary_id} · {e(primary_name)}</b>",
        "",
        f"Hai detto: <i>«{e(question)}»</i>",
        "",
        e(graphic),
        "",
        "📍 <b>ORA</b>",
        e(now_text or it_changing_sentence(changing)),
    ]
    if line_notes:
        blocks.extend(["", "🔄 <b>SI MUOVE</b>", e(it_changing_sentence(changing))])
        for label, note in line_notes:
            blocks.append(f"• {e(label)} — {e(note)}")
    if transformed_id and transformed_name:
        blocks.extend(
            [
                "",
                f"➡️ <b>VERSO</b> {transformed_id} · {e(transformed_name)}",
                e(toward_text or "La situazione cambia volto."),
            ]
        )
    blocks.extend(
        [
            "",
            "✨ <b>IN PRATICA</b>",
            e(pratica),
            "",
            "<i>Wilhelm 1924, tradotto. Specchio, non verdetto.</i>",
        ]
    )
    return "\n".join(blocks)


async def on_iching_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""

    if action in {"open", "new"}:
        await query.answer()
        _flows_reset(context)
        await show_iching_intro(update, context)
        return
    if action == "ready":
        await query.answer()
        await show_iching_ask(update, context)
        return
    if action == "throw":
        await query.answer("Le monete cadono…")
        await send_iching_cast(update, context)
        return
    if action == "home":
        await query.answer()
        _flows_reset(context)
        await reply_html(update, context, start_text(), reply_markup=home_keyboard())
        return
        await query.answer("Bottone stanco. Torna a Inizio e tocca di nuovo.")


# ---------------------------------------------------------------------------
# Tema natale — workflow guidato (CosmyDay /natal + geocoding)
# ---------------------------------------------------------------------------


def home_keyboard() -> InlineKeyboardMarkup:
    return section_home_keyboard()


def _remember_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is not None and query.message is not None:
        kind = "text" if query.message.text else "photo"
        _remember_bot_msg(context, query.message.message_id, kind)
    if query is not None and query.data:
        nav_mark(context, query.data)


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
    _cmd_begin(context, "natal:open")
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
    kb = InlineKeyboardMarkup([[_tarot_btn("✨ Inizia", "natal:start")], nav_row()])
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
            [_tarot_btn("❤️ Compatibilità", "cp:hub")],
            [_tarot_btn("✨ Nuovo tema", "natal:start")],
            nav_row(),
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
        reply_markup=InlineKeyboardMarkup([nav_row()]),
    )


async def ask_natal_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _natal_state(context)
    state["step"] = "time"
    kb = InlineKeyboardMarkup([[_tarot_btn("❓ Non conosco l'ora", "natal:notime")], nav_row()])
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
        reply_markup=InlineKeyboardMarkup([nav_row()]),
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
            nav_row(),
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
                reply_markup=InlineKeyboardMarkup([[_tarot_btn("❓ Non conosco l'ora", "natal:notime")], nav_row()]),
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
        rows.append(nav_row())
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
            reply_markup=InlineKeyboardMarkup([[_tarot_btn("🔁 Riprova", "natal:calc")], nav_row()]),
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
    rows.append(nav_row())
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
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("⬅️ Pianeti", "natal:planets"), _tarot_btn("🌌 Big Three", "natal:big")],
            nav_row(),
        ]
    )
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
    rows.append(nav_row())
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
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("⬅️ Case", "natal:houses"), _tarot_btn("🌌 Big Three", "natal:big")],
            nav_row(),
        ]
    )
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
        "💾 Tema salvato. La prossima volta: ORACOLO → Te stesso → Tema natale.",
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
    if action == "asteroids":
        await query.answer("Cerco gli asteroidi…")
        await show_natal_asteroids(update, context)
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
        await query.answer("Bottone stanco. Torna a Inizio e tocca di nuovo.")


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
        await show_place_picker(update, context, "luna")
        return
    if action == "spazio":
        await query.answer()
        await send_spazio(update, context)
        return
    if action == "meteore":
        await query.answer()
        await send_meteore(update, context)
        return
    if action == "osserva":
        await query.answer()
        await show_place_picker(update, context, "osserva")
        return
    if action == "cielo":
        await query.answer()
        name, lat, lon = _cielo_place(context)
        if name == DEFAULT_PLACE_NAME and not context.user_data.get(CIELO_LAST_KEY):
            await show_place_picker(update, context, "cielo")
            return
        await send_cielo(update, context, name=name, lat=lat, lon=lon)
        return
    if action == "pianeta":
        await query.answer()
        await show_pianeta_menu(update, context)
        return
    if action == "mondi":
        await query.answer()
        await show_mondi_hub(update, context)
        return
    if action == "cosmo":
        await query.answer()
        await show_cosmo(update, context)
        return
    if action == "lune":
        await query.answer()
        await show_lune_menu(update, context)
        return
    if action == "sistema":
        await query.answer()
        await show_sistema(update, context)
        return
    if action == "buchineri":
        await query.answer()
        await show_buchineri_menu(update, context)
        return
    if action == "galassia":
        await query.answer()
        await show_galassia_menu(update, context)
        return
    if action == "eclissi":
        await query.answer()
        await send_eclissi(update, context)
        return
    if action == "missioni":
        await query.answer()
        await show_missioni_menu(update, context)
        return
    if action == "astronauta":
        await query.answer()
        await show_astronauta_menu(update, context)
        return
    if action == "satelliti":
        await query.answer()
        await show_satelliti_menu(update, context)
        return
    if action == "sonde":
        await query.answer()
        await show_sonde_menu(update, context)
        return
    if action == "impara":
        await query.answer()
        await show_impara_menu(update, context)
        return
    if action == "quiz":
        await query.answer()
        await show_quiz_menu(update, context)
        return
    if action == "esopianeta":
        await query.answer()
        await show_esopianeta_menu(update, context)
        return
    if action == "nani":
        await query.answer()
        await show_nani_menu(update, context)
        return
    if action == "comete":
        await query.answer()
        await show_comete_menu(update, context)
        return
    if action == "costellazioni":
        await query.answer()
        await show_costellazioni_menu(update, context)
        return
    if action == "profondo":
        await query.answer()
        await show_profondo_menu(update, context)
        return
    if action == "abitabile":
        await query.answer()
        await send_abitabile(update, context)
        return
    if action == "vita":
        await query.answer()
        await show_vita_menu(update, context)
        return
    if action == "specchio":
        await query.answer()
        await show_specchio(update, context)
        return
    if action == "rituale":
        await query.answer()
        await send_rituale(update, context)
        return
    if action == "compat":
        await query.answer()
        await show_compat_hub(update, context)
        return
    if action == "random":
        await query.answer()
        await send_random(update, context)
        return
    if action == "missione":
        await query.answer()
        await send_missione(update, context)
        return
    if action == "oracoli":
        await query.answer()
        await show_oracoli_hub(update, context)
        return
    if action == "sibille":
        await query.answer()
        await show_lenormand_menu(update, context)
        return
    if action == "lettura":
        await query.answer()
        await show_lettura_ask(update, context)
        return
    if action == "menu":
        await query.answer()
        _flows_reset(context)
        nav_clear(context)
        await reply_html(update, context, start_text(), reply_markup=home_keyboard())
        return
    if action == "esplora":
        await query.answer()
        await reply_html(update, context, esplora_text(), reply_markup=esplora_keyboard())
        return
    if action == "transits":
        await query.answer()
        await show_natal_transits(update, context)
        return
    if action == "rune":
        await query.answer()
        await show_rune_intro(update, context)
        return
    if action == "domanda":
        await query.answer()
        await show_domanda(update, context)
        return
    if action == "iss":
        await query.answer()
        await send_iss(update, context)
        return
    if action == "cosmico":
        await query.answer()
        await send_cosmico(update, context)
        return
    if action == "sole":
        await query.answer()
        last = context.user_data.get(CIELO_LAST_KEY)
        if isinstance(last, dict) and last.get("lat") is not None:
            await send_sole(
                update,
                context,
                name=str(last.get("name") or DEFAULT_PLACE_NAME),
                lat=float(last["lat"]),
                lon=float(last["lon"]),
            )
            return
        await show_place_picker(update, context, "sole")
        return
    if action == "eventi":
        await query.answer()
        await send_eventi(update, context)
        return
    if action == "asteroidi":
        await query.answer()
        await show_asteroid_chooser(update, context)
        return
    if action == "pianeti":
        await query.answer()
        await cmd_pianeti(update, context)
        return
    if action == "apod":
        await query.answer()
        await cmd_apod(update, context)
        return
    if action == "stelle":
        await query.answer()
        await show_stelle_menu(update, context)
        return
    if action == "aiuto":
        await query.answer()
        _cmd_begin(context, "home:aiuto")
        await reply_html(update, context, help_text(), reply_markup=back_home_keyboard())
        return
    await query.answer()


async def cmd_luna(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:luna")
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
            lines.append(f"⬆️ Alba della Luna: {e(obs['moonrise'])}")
        if obs.get("moonset"):
            lines.append(f"⬇️ Tramonto della Luna: {e(obs['moonset'])}")
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
    await reply_html(update, context, "\n".join(lines), reply_markup=back_home_keyboard())
    await delete_user_command(update)


async def cmd_pianeti(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:pianeti")
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
    await reply_html(update, context, "\n".join(lines), reply_markup=back_home_keyboard())
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
    text_body += "\n\n<i>Fonte live: foto astronomica del giorno della NASA</i>"

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
    _cmd_begin(context, "home:apod")
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
    _cmd_begin(context, "home:stelle")
    await show_stelle_menu(update, context)
    await delete_user_command(update)


async def send_stelle_nasa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    except StelleOfflineError:
        logger.exception("Curiosità APOD random non disponibile")
        await reply_offline(update, context)


# ---------------------------------------------------------------------------
# Asteroidi, meteore, spazio, osserva
# ---------------------------------------------------------------------------


def astronomy_after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_tarot_btn("🔭 Osserva", "home:osserva"), _tarot_btn("🌠 Meteore", "home:meteore")],
            [_tarot_btn("🌌 Spazio", "home:spazio")],
            nav_row(),
        ]
    )


def osserva_picker_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for idx, (name, _lat, _lon) in enumerate(OSSERVA_CITIES):
        pair.append(_tarot_btn(f"📍 {name}", f"osserva:city:{idx}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([_tarot_btn("✍️ Altra città", "osserva:ask")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


async def natal_source_for_asteroids(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> dict[str, Any] | None:
    state = _natal_state(context)
    if state.get("year") and state.get("lat") is not None:
        return state
    user = update.effective_user
    profile = await natal_profile_get(user.id) if user else None
    if profile and profile.get("lat") is not None:
        state.update(profile)
        return state
    return None


async def show_asteroids_need_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "☄️ <b>Asteroidi nel tema natale</b>\n\n"
        "Per piazzare Cerere, Vesta, Pallade e Giunone serve la tua carta: "
        "data, ora e luogo di nascita.\n\n"
        "Crea il tema, poi torno qui con le posizioni live da NASA Horizons."
    )
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("✨ Crea il tema", "natal:start")],
            nav_row(),
        ]
    )
    await reply_html(update, context, text, reply_markup=kb)


async def cmd_asteroidi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _tarot_reset(context)
    _iching_reset(context)
    _osserva_reset(context)
    nav_mark(context, "home:asteroidi")
    await show_asteroid_chooser(update, context)
    await delete_user_command(update)


async def show_asteroid_chooser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "☄️ <b>ASTEROIDI</b>\n\n"
        "Tre porte, tre fonti.\n\n"
        "☄️ <b>Vicini alla Terra</b> — NASA NeoWs, passaggi dei prossimi giorni.\n"
        "🪨 <b>Asteroidi noti</b> — Vesta, Pallade, Igea, Eros, Bennu, Psyche (Wikipedia).\n"
        "🌌 <b>Nel tema natale</b> — Cerere, Vesta, Pallade, Giunone dalle effemeridi JPL."
    )
    await reply_html(update, context, text, reply_markup=asteroid_chooser_keyboard())


async def show_natal_asteroids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    source = await natal_source_for_asteroids(update, context)
    if source is None:
        await show_asteroids_need_chart(update, context)
        return
    await send_typing(update)
    await deliver_text(
        update,
        context,
        "☄️ Interrogo le effemeridi JPL per Cerere, Vesta, Pallade e Giunone…",
    )
    client = _http_client(context)
    try:
        tz_name = await api_timezone_name(client, float(source["lat"]), float(source["lon"]))
        try:
            birth_tz = ZoneInfo(tz_name)
        except Exception:
            birth_tz = DEFAULT_TZ
        local = datetime(
            int(source["year"]),
            int(source["month"]),
            int(source["day"]),
            int(source.get("hour") or 12),
            int(source.get("minute") or 0),
            tzinfo=birth_tz,
        )
        when_utc = local.astimezone(timezone.utc)
        chart = natal_chart_from_state(_natal_state(context))
        if not chart:
            chart = await api_natal_chart(
                client,
                year=int(source["year"]),
                month=int(source["month"]),
                day=int(source["day"]),
                hour=int(source.get("hour") or 12),
                minute=int(source.get("minute") or 0),
                lat=float(source["lat"]),
                lon=float(source["lon"]),
            )
            _natal_state(context)["chart"] = chart
        cusps = [float(x) for x in (chart.get("cusps") or []) if x is not None]
        planets = chart.get("planets") if isinstance(chart.get("planets"), dict) else {}

        async def one(name: str, command: str) -> tuple[str, float | None]:
            try:
                return name, await api_horizons_lon(client, command, when_utc)
            except StelleOfflineError:
                logger.warning("Horizons non disponibile per %s", name)
                return name, None

        fetched = await asyncio.gather(
            *[one(name, command) for name, command in ASTEROID_HORIZONS]
        )
    except StelleOfflineError:
        logger.exception("Asteroidi: calcolo non disponibile")
        await reply_offline(update, context)
        return

    rows: list[str] = []
    facts: list[str] = []
    for name, lon in fetched:
        if lon is None:
            continue
        sign, deg, _ = natal_point_from_lon(lon)
        house = house_for_lon(lon, cusps)
        label, emoji = PLANET_LABELS[name]
        house_bit = f" · casa {house}" if house else ""
        role = PLANET_ROLES.get(name, "")
        rows.append(
            f"{emoji} <b>{e(label)}</b>  {e(sign_label(sign))} {e(format_degree(deg))}"
            f"{house_bit}\n<i>{e(role)}</i>"
        )
        facts.append(f"{name} in {sign} house {house or '?'}")

    extras: list[str] = []
    for key in NATAL_EXTRA_ASTEROIDS:
        body = planets.get(key) if isinstance(planets, dict) else None
        if isinstance(body, dict):
            extras.append(natal_body_line(key, body))
            facts.append(f"{key} in {body.get('sign')} house {body.get('house')}")

    if not rows and not extras:
        await reply_offline(update, context)
        return

    place = str(source.get("place") or DEFAULT_PLACE_NAME)
    unknown = bool(source.get("time_unknown"))
    time_txt = "mezzogiorno (ora sconosciuta)" if unknown else local.strftime("%H:%M")
    reading = ""
    if facts:
        prompt = (
            "In one short Italian-ready paragraph, read these natal asteroid placements "
            "without adding extra bodies: " + "; ".join(facts) + "."
        )
        try:
            reading = await translate_to_italian(client, prompt)
        except StelleOfflineError:
            reading = ""

    lines = [
        "☄️ <b>Asteroidi nel tema natale</b>",
        f"📅 {e(format_birth_date(int(source['year']), int(source['month']), int(source['day'])))} "
        f"· {e(time_txt)}",
        f"📍 {e(place)}",
        "",
    ]
    if rows:
        lines.extend(rows)
        lines.append("")
    if extras:
        lines.append("✨ <b>Anche nel tema (CosmyDay)</b>")
        lines.extend(extras)
        lines.append("")
    if reading:
        lines.append("🔮 <b>In sintesi</b>")
        lines.append(e(clip_text(reading, 700)))
        lines.append("")
    lines.append(
        "<i>Cerere, Pallade, Giunone, Vesta: longitudini geocentriche NASA JPL Horizons. "
        "Case Placidus da CosmyDay. Chirone e Lilith arrivano dallo stesso tema.</i>"
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=natal_nav_keyboard())


async def cmd_meteore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:meteore")
    await send_meteore(update, context)
    await delete_user_command(update)


async def send_meteore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🌠 Guardo il calendario degli sciami…")
    client = _http_client(context)
    try:
        showers = await api_meteor_showers(client)
    except StelleOfflineError:
        logger.exception("Sciami meteorici non disponibili")
        await reply_offline(update, context)
        return
    now = datetime.now(DEFAULT_TZ)
    upcoming = upcoming_showers(showers, now, limit=6)
    if not upcoming:
        await reply_offline(update, context)
        return
    peak, nxt = upcoming[0]
    nxt_name = shower_it_name(str(nxt.get("name") or "Sciame"))
    zhr = nxt.get("zhr")
    try:
        zhr_txt = f"Fino a ~{int(zhr)} meteore/ora"
    except (TypeError, ValueError):
        zhr_txt = "Tasso orario non indicato"
    desc_en = str(nxt.get("description") or "").strip()
    parent = str(nxt.get("parentBody") or "").strip()
    radiant = str(nxt.get("radiant") or "").strip()
    extra_en = " ".join(part for part in (desc_en, f"Parent body: {parent}." if parent else "", f"Radiant: {radiant}." if radiant else "") if part)
    extra_it = await translate_to_italian(client, extra_en) if extra_en else ""
    delta = (peak.date() - now.date()).days
    when = "oggi" if delta == 0 else ("domani" if delta == 1 else f"tra {delta} giorni")

    lines = [
        "🌠 <b>PROSSIMI SCIAMI METEORICI</b>",
        "",
        "🌠 <b>PROSSIMO EVENTO</b>",
        "",
        f"<b>{e(nxt_name)}</b>",
        f"Picco: {peak.day} {MONTHS_IT[peak.month - 1]}",
        e(zhr_txt),
        f"<i>{e(when)}</i>",
    ]
    if extra_it:
        lines.extend(["", e(clip_text(extra_it, 420))])
    lines.extend(["", "──────────────", "", "📅 <b>In arrivo</b>", ""])
    for when_dt, shower in upcoming[1:]:
        name = shower_it_name(str(shower.get("name") or "Sciame"))
        try:
            rate = f" · ~{int(shower.get('zhr'))}/ora"
        except (TypeError, ValueError):
            rate = ""
        days = (when_dt.date() - now.date()).days
        lines.append(
            f"🌠 <b>{e(name)}</b> — {when_dt.day} {MONTHS_IT[when_dt.month - 1]}"
            f"{e(rate)} · tra {days} giorni"
        )
    lines.extend(
        [
            "",
            "<i>Calendario live Skytime (picchi annuali). I tassi sono ZHR teorici: "
            "luna, inquinamento luminoso e orario cambiano ciò che vedi davvero.</i>",
        ]
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=astronomy_after_keyboard())


async def cmd_spazio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:spazio")
    await send_spazio(update, context)
    await delete_user_command(update)


def _parse_event_date(raw: Any) -> datetime | None:
    if not raw:
        return None
    text = str(raw).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        text = text + "T00:00:00+00:00"
    elif text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=DEFAULT_TZ)
    return dt.astimezone(DEFAULT_TZ)


async def send_spazio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🌌 Raccolgo Luna, pianeti, eventi e sciami…")
    client = _http_client(context)
    now = datetime.now(DEFAULT_TZ)
    moon_res, planets_res, cmev_res, skyev_res, showers_res, skymap_res = await asyncio.gather(
        api_moon_observatory(client),
        api_planets_now(client),
        api_cosmyday_events(client, 21),
        api_skytime_events(client, now.year),
        api_meteor_showers(client),
        api_skymap(client, DEFAULT_LAT, DEFAULT_LON),
        return_exceptions=True,
    )

    moon = moon_res if isinstance(moon_res, dict) else None
    planets_data = planets_res if isinstance(planets_res, dict) else None
    cmev = cmev_res if isinstance(cmev_res, list) else []
    skyev = skyev_res if isinstance(skyev_res, list) else []
    showers = showers_res if isinstance(showers_res, list) else []
    sky = skymap_res if isinstance(skymap_res, dict) else None
    if not any((moon, planets_data, cmev, skyev, showers, sky)):
        await reply_offline(update, context)
        return

    lines = [
        "🌌 <b>COSA SUCCEDE OGGI NELLO SPAZIO</b>",
        f"📅 {e(format_day_it(now))}",
        "",
        "🌙 <b>Luna</b>",
    ]
    if moon:
        lines.append(f"{e(moon_phase_label(str(moon.get('moon_phase') or '')))}")
        try:
            lines.append(f"Illuminazione {float(moon.get('moon_illumination') or 0):.0f}%")
        except (TypeError, ValueError):
            pass
        if moon.get("moonrise") or moon.get("moonset"):
            lines.append(
                f"Alba {e(moon.get('moonrise') or '—')} · tramonto {e(moon.get('moonset') or '—')}"
            )
    else:
        lines.append("Dati lunari non arrivati.")

    lines.extend(["", "🪐 <b>Pianeti</b>"])
    planets = (planets_data or {}).get("planets") or {}
    shown = 0
    for key in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        body = planets.get(key)
        if not isinstance(body, dict):
            continue
        label, emoji = PLANET_LABELS[key]
        retro = " ℞" if body.get("retrograde") else ""
        lines.append(f"{emoji} {e(label)} in {e(sign_label(str(body.get('sign') or '')))}{retro}")
        shown += 1
    if not shown:
        lines.append("Efemeridi non arrivate.")

    lines.extend(["", "☄️ <b>Eventi</b>"])
    event_bits: list[str] = []
    for item in cmev[:4]:
        when = _parse_event_date(item.get("date"))
        headline = str(item.get("headline") or item.get("short") or "").strip()
        if not headline:
            continue
        try:
            headline = await translate_to_italian(client, headline)
        except StelleOfflineError:
            headline = event_name_it(headline)
        kind = EVENT_KIND_IT.get(str(item.get("kind") or ""), "")
        day = f"{when.day} {MONTHS_IT[when.month - 1]}" if when else ""
        event_bits.append(f"• {e(day + ' · ' if day else '')}{e(headline)}" + (f" <i>({e(kind)})</i>" if kind else ""))
    horizon = now + timedelta(days=10)
    for item in skyev:
        kind = str(item.get("type") or "")
        if kind not in {"season", "solar-eclipse", "lunar-eclipse"}:
            continue
        when = _parse_event_date(item.get("date"))
        if when is None or when < now - timedelta(hours=12) or when > horizon:
            continue
        name = event_name_it(str(item.get("name") or kind))
        label = EVENT_KIND_IT.get(kind, kind)
        event_bits.append(
            f"• {when.day} {MONTHS_IT[when.month - 1]} · {e(name)} <i>({e(label)})</i>"
        )
    if event_bits:
        lines.extend(event_bits[:5])
    else:
        lines.append("Nessun appuntamento grosso nei prossimi giorni.")

    lines.extend(["", "🌠 <b>Sciami meteorici</b>"])
    upcoming = upcoming_showers(showers, now, limit=1) if showers else []
    if upcoming:
        peak, nxt = upcoming[0]
        try:
            rate = f" · fino a ~{int(nxt.get('zhr'))}/ora"
        except (TypeError, ValueError):
            rate = ""
        lines.append(
            f"{e(shower_it_name(str(nxt.get('name') or 'Sciame')))} — picco "
            f"{peak.day} {MONTHS_IT[peak.month - 1]}{e(rate)}"
        )
    else:
        lines.append("Calendario sciami non disponibile.")

    lines.extend(["", "🔭 <b>Eventi osservabili</b>", f"📍 {e(DEFAULT_PLACE_NAME)} · adesso"])
    if sky:
        moon_info = sky.get("moon") if isinstance(sky.get("moon"), dict) else {}
        if moon_info:
            alt = moon_info.get("alt")
            where = "sopra l'orizzonte" if isinstance(alt, (int, float)) and alt > 0 else "sotto l'orizzonte"
            lines.append(
                f"🌙 Luna {e(moon_phase_label(str(moon_info.get('phase') or '')))}, "
                f"{e(where)}"
            )
        bodies = sky.get("bodies") if isinstance(sky.get("bodies"), list) else []
        visible = [b for b in bodies if isinstance(b, dict) and b.get("name")]
        if visible:
            bits = []
            for body in visible[:4]:
                name = str(body.get("name"))
                label, emoji = PLANET_LABELS.get(name, (name, "🪐"))
                compass = compass_it(str(body.get("compass") or ""))
                try:
                    alt = f"{float(body.get('alt')):.0f}°"
                except (TypeError, ValueError):
                    alt = ""
                bits.append(f"{emoji} {label} {alt} {compass}".strip())
            lines.append(" · ".join(bits))
        aster = sky.get("asterisms") if isinstance(sky.get("asterisms"), list) else []
        if aster:
            names = ", ".join(str(a) for a in aster[:5])
            names_it = await translate_to_italian(client, names)
            lines.append(f"⭐ {e(names_it)}")
    else:
        lines.append("Mappa del cielo non arrivata.")

    lines.extend(
        [
            "",
            "<i>Fonti live: orari del Sole e della Luna, CosmyDay, Skytime, mappa del cielo. "
            "Il briefing è astronomico, non un oroscopo.</i>",
        ]
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=astronomy_after_keyboard())


async def cmd_osserva(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:osserva")
    await show_osserva_picker(update, context)
    await delete_user_command(update)


async def cmd_cielo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:cielo")
    raw = " ".join(context.args) if context.args else ""
    if raw:
        await receive_cielo_city(update, context, raw)
    else:
        await send_cielo(update, context)
    await delete_user_command(update)


async def show_osserva_picker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _osserva_state(context)
    state.clear()
    state["step"] = "pick"
    text = (
        "🔭 <b>COSA POSSO VEDERE STASERA?</b>\n\n"
        "Scegli una città. Uso posizione, data e ora per Luna, pianeti "
        "e costellazioni sopra l'orizzonte.\n\n"
        "Oppure scrivi un'altra città in un messaggio."
    )
    await reply_html(update, context, text, reply_markup=osserva_picker_keyboard())


async def show_osserva_ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _osserva_state(context)
    state["step"] = "ask"
    await reply_html(
        update,
        context,
        "🔭 <b>Da dove guardi?</b>\n\n"
        "Scrivi città e paese.\n"
        "Esempio: <code>Bologna, Italia</code>",
        reply_markup=InlineKeyboardMarkup([nav_row()]),
    )


async def receive_osserva_city(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> None:
    await send_typing(update)
    await deliver_text(update, context, "📍 Cerco la città…")
    client = _http_client(context)
    try:
        places = await api_geocode_place(client, text)
    except StelleOfflineError:
        await reply_html(
            update,
            context,
            "Non trovo quel luogo. Prova con città e paese, tipo <code>Bologna, Italia</code>.",
            reply_markup=osserva_picker_keyboard(),
        )
        return
    place = places[0]
    _osserva_state(context)["step"] = "pick"
    await delete_user_command(update)
    await send_osserva(
        update,
        context,
        name=str(place.get("name") or text),
        lat=float(place["lat"]),
        lon=float(place["lon"]),
    )


async def send_osserva(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    name: str,
    lat: float,
    lon: float,
) -> None:
    await send_typing(update)
    await deliver_text(update, context, f"🔭 Guardo il cielo sopra {name}…")
    client = _http_client(context)
    try:
        tz_name = await api_timezone_name(client, lat, lon)
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = DEFAULT_TZ
        now_local = datetime.now(tz)
        sky = await api_skymap(client, lat, lon)
        sun_alt = sky.get("sun_alt")
        if isinstance(sun_alt, (int, float)) and sun_alt > -6:
            tonight = now_local.replace(hour=22, minute=0, second=0, microsecond=0)
            if now_local < tonight:
                sky = await api_skymap(client, lat, lon, when_utc=tonight.astimezone(timezone.utc))
                now_local = tonight
    except StelleOfflineError:
        logger.exception("Osserva: mappa del cielo non disponibile")
        await reply_html(
            update,
            context,
            "Le stelle sono temporaneamente non raggiungibili ✨ riprova tra poco\n\n"
            "La mappa del cielo non ha risposto. Puoi cambiare città.",
            reply_markup=osserva_picker_keyboard(),
        )
        return

    when_raw = str(sky.get("when_local") or "")
    when_dt = _parse_event_date(when_raw) or now_local
    moon_info = sky.get("moon") if isinstance(sky.get("moon"), dict) else {}
    bodies = [b for b in (sky.get("bodies") or []) if isinstance(b, dict)]
    brightest = [b for b in (sky.get("brightest") or []) if isinstance(b, dict)]
    asterisms = [str(a) for a in (sky.get("asterisms") or []) if a]

    lines = [
        "🔭 <b>COSA POSSO VEDERE STASERA?</b>",
        "",
        f"📍 <b>{e(name)}</b>",
        f"🕐 {when_dt.strftime('%H:%M')} · {e(format_day_it(when_dt))}",
        "",
        "🌙 <b>Luna</b>",
    ]
    if moon_info:
        alt = moon_info.get("alt")
        up = isinstance(alt, (int, float)) and alt > 0
        where = "sopra l'orizzonte" if up else "sotto l'orizzonte"
        illum = moon_info.get("illum")
        illum_bit = ""
        try:
            if illum is not None:
                illum_bit = f", {int(illum)}% illuminata"
        except (TypeError, ValueError):
            pass
        compass = f" verso {compass_it(str(moon_info.get('compass')))}" if moon_info.get("compass") and up else ""
        alt_f = float(alt) if isinstance(alt, (int, float)) else None
        alt_bit = f" ({alt_f:.0f}°)" if up and alt_f is not None else ""
        stars = visibility_stars(altitude=alt_f if up else 0.0, magnitude=None)
        lines.append(
            f"{e(moon_phase_label(str(moon_info.get('phase') or '')))}{e(illum_bit)}, "
            f"{e(where)}{e(alt_bit)}{e(compass)}  {stars}"
        )
    else:
        lines.append("Nessun dato lunare in questa mappa.")

    sun_block = ""
    try:
        sun = await api_sun_times(client, lat, lon, tz_name)
        if sun.get("moonrise") or sun.get("sunset"):
            sun_block = (
                f"🌅 Tramonto {e(sun.get('sunset') or '—')} · "
                f"🌙 alba della Luna {e(sun.get('moonrise') or '—')} · "
                f"tramonto {e(sun.get('moonset') or '—')}"
            )
    except StelleOfflineError:
        sun_block = ""
    if sun_block:
        lines.append(sun_block)

    lines.extend(["", "🪐 <b>Pianeti</b>"])
    if bodies:
        for body in bodies:
            raw = str(body.get("name") or "")
            label, emoji = PLANET_LABELS.get(raw, (raw, "🪐"))
            try:
                alt_f = float(body.get("alt"))
                alt = f"{alt_f:.0f}°"
            except (TypeError, ValueError):
                alt_f = None
                alt = "—"
            compass = compass_it(str(body.get("compass") or ""))
            mag = body.get("mag")
            mag_f: float | None
            try:
                mag_f = float(mag) if mag is not None else None
            except (TypeError, ValueError):
                mag_f = None
            mag_bit = f" · magnitudine {mag_f:.1f}" if mag_f is not None else ""
            stars = visibility_stars(altitude=alt_f, magnitude=mag_f)
            lines.append(
                f"{emoji} <b>{e(label)}</b> — {e(alt)} {e(compass)}{e(mag_bit)}  {stars}"
            )
    else:
        lines.append("Nessun pianeta sopra l'orizzonte in questo momento.")

    lines.extend(["", "⭐ <b>Costellazioni</b>"])
    if asterisms:
        names_it = await translate_to_italian(client, ", ".join(asterisms[:8]))
        lines.append(e(names_it))
    else:
        lines.append("Nessun asterismo segnalato in questa ora.")
    if brightest:
        lines.append("")
        lines.append("✨ <b>Stelle più luminose</b>")
        for star in brightest[:5]:
            try:
                alt = f"{float(star.get('alt')):.0f}°"
            except (TypeError, ValueError):
                alt = "—"
            lines.append(
                f"• {e(star_it(str(star.get('name') or 'stella')))} — {e(alt)} {e(compass_it(str(star.get('compass') or '')))}"
            )

    stars_up = sky.get("stars_up")
    if isinstance(stars_up, int):
        lines.append("")
        lines.append(f"<i>{stars_up} stelle sopra l'orizzonte in questa mappa.</i>")
    lines.extend(
        [
            "",
            "<i>Mappa live del cielo (posizione, data e ora). "
            "Se è ancora giorno, passo alle 22:00 locali.</i>",
        ]
    )
    state = _osserva_state(context)
    state["last"] = {"name": name, "lat": lat, "lon": lon}
    map_url = stellarium_url(lat, lon)
    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌌 Mappa del cielo", url=map_url)],
            [_tarot_btn("🔭 Aggiorna", "osserva:refresh"), _tarot_btn("📍 Città", "osserva:open")],
            nav_row(),
        ]
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=kb)


async def on_osserva_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""
    if action == "home":
        await query.answer()
        _flows_reset(context)
        await reply_html(update, context, start_text(), reply_markup=home_keyboard())
        return
    if action in {"open", "pick"}:
        await query.answer()
        await show_osserva_picker(update, context)
        return
    if action == "ask":
        await query.answer()
        await show_osserva_ask_city(update, context)
        return
    if action == "city" and extra.isdigit():
        idx = int(extra)
        if 0 <= idx < len(OSSERVA_CITIES):
            name, lat, lon = OSSERVA_CITIES[idx]
            await query.answer(name)
            await send_osserva(update, context, name=name, lat=lat, lon=lon)
            return
    if action == "refresh":
        last = _osserva_state(context).get("last")
        if isinstance(last, dict) and last.get("lat") is not None:
            await query.answer("Aggiorno…")
            await send_osserva(
                update,
                context,
                name=str(last.get("name") or DEFAULT_PLACE_NAME),
                lat=float(last["lat"]),
                lon=float(last["lon"]),
            )
            return
        await query.answer()
        await show_osserva_picker(update, context)
        return
        await query.answer("Bottone stanco. Torna a Inizio e tocca di nuovo.")


async def show_rune_intro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _rune_state(context)
    state.clear()
    state["step"] = "intro"
    await reply_html(update, context, rune_intro_text(), reply_markup=rune_ready_keyboard())


async def cmd_rune(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:rune")
    await show_rune_intro(update, context)
    await delete_user_command(update)


RUNE_SLOTS = {
    1: (("Adesso", "Cosa è in gioco."),),
    3: (
        ("Situazione", "Dove sei, adesso."),
        ("Ostacolo", "Cosa frena o confonde."),
        ("Direzione", "Un passo possibile."),
    ),
}


def rune_closer(drawn: list[dict[str, str]]) -> str:
    if not drawn:
        return ""
    if len(drawn) == 1:
        piece = drawn[0]
        orient = "capovolta" if piece["orientation"] == "reversed" else "diritta"
        meaning = first_sentences(str(piece.get("meaning") or ""), 1, 160)
        extra = f" {meaning}" if meaning else ""
        return (
            f"{piece['name']} ({orient}).{extra} "
            "Tienila come clima di adesso, non come ordine."
        )
    labels = ("Situazione", "Ostacolo", "Direzione")
    bits = []
    for idx, piece in enumerate(drawn[:3]):
        meaning = first_sentences(str(piece.get("meaning") or ""), 1, 110)
        bits.append(f"{labels[idx]} — {piece['name']}: {meaning}")
    bits.append("Il passo da guardare è la terza runa.")
    return " ".join(bits)


async def show_rune_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _rune_state(context)
    state["step"] = "ask"
    state["awaiting"] = True
    await reply_html(
        update,
        context,
        "🪶 <b>Una frase alle rune</b>\n"
        "<i>Non è obbligatoria.</i>\n\n"
        "Se vuoi, scrivi una riga. Poi scuotiamo il sacchetto lo stesso.",
        reply_markup=InlineKeyboardMarkup(
            [[_tarot_btn("🪶 Meglio senza", "rune:mix")], nav_row()]
        ),
    )


async def show_rune_cast(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int) -> None:
    state = _rune_state(context)
    state["count"] = 1 if count != 3 else 3
    state["step"] = "ready"
    state["awaiting"] = False
    n = int(state["count"])
    phrase = str(state.get("question") or "").strip()
    text = (
        f"🪶 <b>{'Una runa' if n == 1 else 'Tre rune'}</b>\n"
        "<i>Le giriamo una alla volta. Non serve una domanda.</i>"
    )
    if phrase:
        text += f"\n\nHai detto: <i>«{e(phrase)}»</i>"
    await reply_html(update, context, text, reply_markup=rune_cast_keyboard())


async def receive_rune_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    question: str,
) -> None:
    phrase = clip_text(question.strip(), 400)
    if not phrase:
        await reply_html(update, context, "Una riga basta. Oppure scuoti, senza frase.")
        return
    state = _rune_state(context)
    state["question"] = phrase
    state["awaiting"] = False
    count = int(state.get("count") or 0)
    if count in {1, 3}:
        await show_rune_cast(update, context, count)
    else:
        state["step"] = "pick"
        await reply_html(
            update,
            context,
            f"🪶 Hai detto: <i>«{e(phrase)}»</i>\n\nUna runa o tre?",
            reply_markup=rune_ready_keyboard(),
        )
    await delete_user_command(update)


async def start_rune_mix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _rune_state(context)
    count = int(state.get("count") or 0)
    if count not in {1, 3}:
        await show_rune_intro(update, context)
        return
    state["awaiting"] = False
    await send_typing(update)
    await deliver_text(update, context, "🪶 Metto la mano nel sacchetto…")
    await asyncio.sleep(0.35)
    await deliver_text(update, context, "🪶 Scuoto…")
    drawn = draw_runes(count)
    state["drawn"] = drawn
    state["index"] = 0
    state["step"] = "reveal"
    await asyncio.sleep(0.28)
    await reveal_rune(update, context)


async def reveal_rune(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _rune_state(context)
    drawn = state.get("drawn") if isinstance(state.get("drawn"), list) else []
    idx = int(state.get("index") or 0)
    if not drawn or idx >= len(drawn):
        await show_rune_quadro(update, context)
        return
    piece = drawn[idx]
    slots = RUNE_SLOTS.get(len(drawn)) or RUNE_SLOTS[1]
    pos, hint = slots[idx] if idx < len(slots) else (f"Runa {idx + 1}", "")
    orient = "capovolta" if piece["orientation"] == "reversed" else "diritta"
    left = len(drawn) - idx - 1
    text = (
        f"🪶 <b>{e(pos)}</b>  ·  {idx + 1}/{len(drawn)}\n"
        f"{piece['glyph']} <b>{e(piece['name'])}</b>\n"
        f"<i>{e(orient)}</i>\n\n"
        f"{e(hint)}\n\n"
        f"{e(first_sentences(piece['meaning'], 2, 240))}"
    )
    if left:
        text += f"\n\n<i>Restano {left} rune.</i>"
    else:
        text += "\n\n<i>Ultima runa. Poi il quadro e l'interpretazione.</i>"
    state["index"] = idx + 1
    await reply_html(update, context, text, reply_markup=rune_next_keyboard(last=left == 0))


async def show_rune_quadro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _rune_state(context)
    drawn = state.get("drawn") if isinstance(state.get("drawn"), list) else []
    if not drawn:
        await show_rune_intro(update, context)
        return
    phrase = str(state.get("question") or "").strip()
    slots = RUNE_SLOTS.get(len(drawn)) or RUNE_SLOTS[1]
    lines = [
        "🪶 <b>IL QUADRO</b>",
        "<i>I nomi, poi cosa dicono insieme.</i>",
        "",
    ]
    if phrase:
        lines.append(f"Hai detto: <i>«{e(phrase)}»</i>")
        lines.append("")
    for idx, piece in enumerate(drawn):
        pos = slots[idx][0] if idx < len(slots) else f"Runa {idx + 1}"
        orient = "R" if piece["orientation"] == "reversed" else "D"
        lines.append(f"{idx + 1}. {e(pos)} — {piece['glyph']} {e(piece['name'])} ({orient})")
    lines.extend(["", "✨ <b>IN PRATICA</b>", e(rune_closer(drawn)), "", "<i>Elder Futhark. Specchio, non ordine.</i>"])
    state["step"] = "done"
    await reply_html(update, context, "\n".join(lines), reply_markup=rune_after_keyboard())


async def send_rune_draw(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int) -> None:
    await show_rune_cast(update, context, count)


async def on_rune_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""
    if action in {"new", "open"}:
        await query.answer()
        _rune_reset(context)
        await show_rune_intro(update, context)
        return
    if action == "ready":
        await query.answer()
        await show_rune_intro(update, context)
        return
    if action == "phrase":
        await query.answer()
        await show_rune_ask(update, context)
        return
    if action == "draw" and extra in {"1", "3"}:
        await query.answer()
        await show_rune_cast(update, context, int(extra))
        return
    if action == "mix":
        await query.answer("Scuoto…")
        await start_rune_mix(update, context)
        return
    if action == "next":
        await query.answer()
        await reveal_rune(update, context)
        return
    if action == "board":
        await query.answer()
        await show_rune_quadro(update, context)
        return
    await query.answer("Bottone stanco. Torna a Inizio e tocca di nuovo.")


async def show_domanda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_lettura_ask(update, context)


async def cmd_domanda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_lettura(update, context)


async def cmd_esplora(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _flows_reset(context)
    await show_all_hub(update, context)
    await delete_user_command(update)


async def resume_nav(update: Update, context: ContextTypes.DEFAULT_TYPE, token: str) -> None:
    if not token or token in NAV_HOME_TOKENS:
        nav_clear(context)
        await reply_html(update, context, start_text(), reply_markup=home_keyboard())
        return
    prefix, _, rest = token.partition(":")
    action, _, extra = rest.partition(":")

    worlds = {
        "self": (world_self_text, world_self_keyboard),
        "div": (world_div_text, world_div_keyboard),
        "asksky": (world_asksky_text, world_asksky_keyboard),
        "sky": (world_sky_text, world_sky_keyboard),
        "mondi": (world_mondi_text, world_mondi_keyboard),
        "vita": (world_vita_text, world_vita_keyboard),
        "miss": (world_miss_text, world_miss_keyboard),
        "pietre": (world_pietre_text, world_pietre_keyboard),
        "terra": (world_terra_text, world_terra_keyboard),
        "quake": (world_quake_text, world_quake_keyboard),
        "volc": (world_volc_text, world_volc_keyboard),
        "water": (world_water_text, world_water_keyboard),
        "plates": (world_plates_text, world_plates_keyboard),
    }
    if prefix == "bot":
        if action in {"oracolo", "cosmo"}:
            await show_oracolo_hub(update, context)
            return
        if action in {"astro", "next"}:
            await show_astro_hub(update, context)
            return
        if action == "geo":
            await show_geo_hub(update, context)
            return
        await show_all_hub(update, context)
        return
    if prefix == "geo":
        await dispatch_geo(update, context, token)
        return
    if prefix == "world" and action in worlds:
        text_fn, kb_fn = worlds[action]
        await reply_html(update, context, text_fn(), reply_markup=kb_fn())
        return
    if prefix == "nav":
        pages = {
            "me": (world_self_text, nav_me_keyboard),
            "risposte": (world_div_text, nav_risposte_keyboard),
            "cielo": (world_sky_text, nav_cielo_keyboard),
            "universo": (world_mondi_text, nav_universo_keyboard),
        }
        page = pages.get(action)
        if page:
            text_fn, kb_fn = page
            await reply_html(update, context, text_fn(), reply_markup=kb_fn())
            return
    if prefix == "w" and action and extra:
        await send_wiki_sheet(update, context, action, extra)
        return
    if prefix == "tarot":
        if action == "menu":
            await show_tarot_menu(update, context)
            return
        if action == "hist":
            await show_tarot_history(update, context)
            return
        if action == "pick" and extra in TAROT_SPREADS:
            await show_tarot_ready(update, context, extra)
            return
        if action == "board":
            await show_tarot_quadro(update, context)
            return
        if action in {"mix", "draw", "next", "phrase"}:
            spread = str(_tarot_state(context).get("spread") or "three")
            await show_tarot_ready(update, context, spread)
            return
    if prefix == "iching":
        if action in {"open", "new"}:
            await show_iching_intro(update, context)
            return
    if prefix == "natal":
        natal_pages = {
            "open": natal_open,
            "start": ask_natal_date,
            "big": show_natal_big_three,
            "planets": show_natal_planets,
            "houses": show_natal_houses,
            "aspects": show_natal_aspects,
            "love": show_natal_love,
            "asteroids": show_natal_asteroids,
            "read": show_natal_reading,
            "elements": show_natal_elements,
            "me": natal_open,
            "reload": reload_saved_natal,
            "transits": show_natal_transits,
        }
        fn = natal_pages.get(action)
        if fn:
            await fn(update, context)
            return
        if action == "p" and extra:
            await show_natal_planet(update, context, extra)
            return
        if action == "h" and extra.isdigit():
            await show_natal_house(update, context, int(extra))
            return
    if prefix == "osserva":
        if action in {"open", "pick"}:
            await show_osserva_picker(update, context)
            return
        if action == "ask":
            await show_osserva_ask_city(update, context)
            return
        if action == "city" and extra.isdigit():
            idx = int(extra)
            if 0 <= idx < len(OSSERVA_CITIES):
                name, lat, lon = OSSERVA_CITIES[idx]
                await send_osserva(update, context, name=name, lat=lat, lon=lon)
                return
    if prefix == "cielo":
        if action == "pick":
            await show_cielo_picker(update, context)
            return
        if action == "ask":
            context.user_data["cielo_ask"] = True
            await reply_html(
                update,
                context,
                "📍 <b>Da dove guardi?</b>\n\nScrivi città e paese.\nEsempio: <code>Bologna, Italia</code>",
                reply_markup=cielo_picker_keyboard(),
            )
            return
        if action == "city" and extra.isdigit():
            idx = int(extra)
            if 0 <= idx < len(OSSERVA_CITIES):
                name, lat, lon = OSSERVA_CITIES[idx]
                await send_cielo(update, context, name=name, lat=lat, lon=lon)
                return
        if action == "planets":
            name, lat, lon = _cielo_place(context)
            await send_osserva(update, context, name=name, lat=lat, lon=lon)
            return
    if prefix == "st":
        if action == "rand":
            await send_random_star(update, context)
            return
        if action == "day":
            await send_star_of_day(update, context)
            return
        if action == "bright":
            await send_stars_now(update, context, brightest_only=True)
            return
        if action == "now":
            await send_stars_now(update, context)
            return
        if action == "near":
            await send_near_or_giants(update, context, NEAR_STARS)
            return
        if action == "rg":
            await send_near_or_giants(update, context, GIANT_STARS)
            return
        if action == "nasa":
            await send_stelle_nasa(update, context)
            return
    if prefix == "co":
        if action == "day":
            item = CONSTELLATIONS[datetime.now(DEFAULT_TZ).timetuple().tm_yday % len(CONSTELLATIONS)]
            await send_wiki_sheet(update, context, "k", item["id"])
            return
        if action == "rand":
            await send_wiki_sheet(update, context, "k", random.choice(CONSTELLATIONS)["id"])
            return
        if action == "now":
            await send_constellations_now(update, context)
            return
    if prefix == "ev":
        if action == "solar":
            await send_solar_activity(update, context)
            return
        if action == "moon":
            await send_moon_distance(update, context)
            return
    if prefix == "xp" and action in {"rand", "earth", "hell", "extreme", "ocean", "recent", "hz"}:
        await send_exo_filter(update, context, action)
        return
    if prefix == "aster":
        if action == "neo":
            await send_neo_asteroids(update, context)
            return
        if action == "natal":
            await show_natal_asteroids(update, context)
            return
        if action == "famous":
            await show_famous_asteroids(update, context)
            return
    if prefix == "quiz":
        if action == "go" and extra:
            await send_quiz_question(update, context, extra)
            return
        if action == "board":
            await send_quiz_board(update, context)
            return
    if prefix == "ora":
        if action in {"arch", "anim", "symb", "elem", "plan"}:
            await send_deck_card(update, context, action)
            return
        if action == "lunar":
            await send_lunar_oracle(update, context)
            return
        if action == "yes":
            await reply_html(
                update,
                context,
                "🪞 <b>DOMANDA SÌ / NO</b>\n\n"
                "Pensa alla domanda. Non serve scriverla.\n"
                "Pesco un tarocco, una runa o un I Ching e ti do un'inclinazione simbolica.\n"
                "Non è un verdetto.",
                reply_markup=yesno_keyboard(),
            )
            return
        if action == "askq":
            await show_oracle_question(update, context)
            return
        if action == "surprise":
            await send_oracle_surprise(update, context)
            return
    if prefix == "leno":
        await show_lenormand_menu(update, context)
        return
    if prefix == "lett":
        await show_lettura_methods(update, context)
        return
    if prefix == "rune":
        if action == "new":
            await show_rune_intro(update, context)
            return
        await show_rune_intro(update, context)
        return
    if prefix == "sole":
        await send_sole(update, context)
        return
    if prefix == "md":
        if action == "hub":
            await show_mondi_hub(update, context)
            return
        if action == "cosmo":
            await show_cosmo(update, context)
            return
        if action == "sys":
            await show_sistemi_menu(update, context)
            return
        if action == "life":
            await reply_html(update, context, life_plus_text(), reply_markup=life_plus_keyboard())
            return
        if action == "ss":
            await reply_html(
                update,
                context,
                "🛰️ <b>MONDI DEL SISTEMA SOLARE</b>\n\n"
                "Atmosfera, gravità, giorno e anno: solo se Wikidata li ha.\n"
                "Curiosità = estratto Wikipedia, non un copione.",
                reply_markup=ss_bodies_keyboard(),
            )
            return
        if action == "miss":
            await reply_html(
                update,
                context,
                "🚀 <b>CHI È ANDATO LÌ?</b>\n\n"
                "Missione → corpi del catalogo. Poi la voce Wikipedia per scoperte e immagini.",
                reply_markup=miss_worlds_keyboard(),
            )
            return
        if action == "neb":
            await send_nebulae(update, context)
            return
        if action == "rand":
            await send_mondi_random(update, context)
            return
        if action == "day":
            await send_mondi_day(update, context)
            return
        if action == "gen":
            world = generate_world()
            _mondi_remember(context, world, kind="imag")
            await reply_html(update, context, format_imaginary(world), reply_markup=mondi_after_keyboard())
            return
        if action == "rogue":
            client = _http_client(context)
            rows = await exoplanets_by_filter(client, "rogue", limit=8)
            if rows:
                context.user_data[MONDI_LIST_KEY] = rows
                text = format_exo_list(
                    rows,
                    title="🌑 Senza stella (righe senza stella ospite)",
                    blurb="Se l'archivio non ha una stella ospite. Altrimenti non invento pianeti erranti.",
                )
                await reply_html(update, context, text, reply_markup=mondi_list_keyboard(len(rows)))
                return
            await send_wiki_sheet(update, context, "v", "rogue")
            return
        if action == "volc":
            await send_wiki_sheet(update, context, "m", "io")
            return
        if action == "rings":
            await reply_html(
                update,
                context,
                "💍 <b>MONDI CON ANELLI</b>\n\n"
                "Nel Sistema Solare le schede sono Saturno e Urano (anelli noti, voce Wikipedia).\n"
                "Gli anelli extrasolari non sono un campo dell'archivio: non li segno io.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [_tarot_btn("💍 Saturno", "w:p:saturn"), _tarot_btn("🌀 Urano", "w:p:uranus")],
                        [_tarot_btn("🌍 Esplora", "md:hub")],
                        nav_row(),
                    ]
                ),
            )
            return
        if action == "moons":
            await reply_html(
                update,
                context,
                "🌙 <b>MOLTE LUNE</b>\n\n"
                "Giove e Saturno nel Sistema Solare. "
                "Le lune extrasolari quasi non esistono nell'archivio: non ne fabbrico.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [_tarot_btn("🟠 Giove", "w:p:jupiter"), _tarot_btn("💍 Saturno", "w:p:saturn")],
                        [_tarot_btn("🌑 Catalogo lune", "home:lune")],
                        [_tarot_btn("🌍 Esplora", "md:hub")],
                        nav_row(),
                    ]
                ),
            )
            return
        if action == "f" and extra in FILTERS:
            await send_mondi_filter(update, context, extra)
            return
        if action == "o" and extra.isdigit():
            rows = context.user_data.get(MONDI_LIST_KEY)
            idx = int(extra)
            if isinstance(rows, list) and 0 <= idx < len(rows):
                await send_mondi_world(update, context, rows[idx])
                return
            await show_mondi_hub(update, context)
            return
        if action == "sysf" and extra:
            await send_systems_kind(update, context, extra)
            return
        if action == "sysr":
            client = _http_client(context)
            card = await random_system(client)
            if card is None:
                await show_sistemi_menu(update, context)
                return
            planets = card.get("planets") if isinstance(card.get("planets"), list) else []
            context.user_data[MONDI_LIST_KEY] = planets
            await reply_html(
                update,
                context,
                format_system_tree(card),
                reply_markup=mondi_list_keyboard(min(len(planets), 8), back="md:sys") if planets else sistemi_keyboard(),
            )
            return
        if action == "syso" and extra.isdigit():
            rows = context.user_data.get(MONDI_SYS_KEY)
            idx = int(extra)
            if isinstance(rows, list) and 0 <= idx < len(rows):
                host = str(rows[idx].get("hostname") or "")
                await send_system_card(update, context, host)
                return
            await show_sistemi_menu(update, context)
            return
        if action == "sy" and extra in FAMOUS_HOSTS:
            await send_system_card(update, context, FAMOUS_HOSTS[extra])
            return
        if action == "fav":
            user = update.effective_user
            favs = await world_list(user.id) if user else []
            context.user_data[MONDI_FAV_KEY] = favs
            if not favs:
                await reply_html(
                    update,
                    context,
                    "📌 <b>I TUOI MONDI</b>\n\nAncora vuota. Apri una scheda e tocca Salva.",
                    reply_markup=mondi_hub_keyboard(),
                )
                return
            lines = ["📌 <b>I TUOI MONDI</b>", "", "Solo tuoi, sul server. Tocca un numero.", ""]
            for idx, item in enumerate(favs, start=1):
                tag = "generato" if item.get("kind") == "imag" else "archivio"
                lines.append(f"{idx}. {e(item.get('name') or '—')} <i>({tag})</i>")
            await reply_html(update, context, "\n".join(lines), reply_markup=fav_list_keyboard(len(favs)))
            return
        if action == "fo" and extra.isdigit():
            favs = context.user_data.get(MONDI_FAV_KEY)
            idx = int(extra)
            if isinstance(favs, list) and 0 <= idx < len(favs):
                item = favs[idx]
                if item.get("kind") == "imag":
                    await reply_html(
                        update,
                        context,
                        format_imaginary(
                            item
                            if item.get("pl_rade")
                            else {
                                "name": item.get("name"),
                                "kind": "imag",
                                "note": "Salvato come nome. Rigenera per nuovi dadi.",
                                "climate": "—",
                                "stars": "—",
                                "pl_rade": "—",
                                "pl_eqt": "—",
                                "pl_orbper": "—",
                                "moons": "—",
                            }
                        ),
                        reply_markup=mondi_after_keyboard(),
                    )
                    return
                client = _http_client(context)
                row = await exoplanet_by_name(client, str(item.get("name") or ""))
                if row:
                    await send_mondi_world(update, context, row)
                    return
            await show_mondi_hub(update, context)
            return
        if action == "wm" and extra:
            await send_mission_worlds(update, context, extra)
            return
    if prefix == "pt":
        await dispatch_pietre(update, context, token)
        return
    if prefix == "cp":
        await dispatch_compat(update, context, token)
        return
    if prefix == "home":
        await _resume_home(update, context, action)
        return
    await reply_html(update, context, start_text(), reply_markup=home_keyboard())


async def _resume_home(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    if action == "oroscopo":
        await begin_oroscopo(update, context, "")
        return
    if action == "luna":
        await show_place_picker(update, context, "luna")
        return
    if action == "spazio":
        await send_spazio(update, context)
        return
    if action == "meteore":
        await send_meteore(update, context)
        return
    if action == "osserva":
        await show_place_picker(update, context, "osserva")
        return
    if action == "cielo":
        last = context.user_data.get(CIELO_LAST_KEY)
        if isinstance(last, dict) and last.get("lat") is not None:
            await send_cielo(
                update,
                context,
                name=str(last.get("name") or DEFAULT_PLACE_NAME),
                lat=float(last["lat"]),
                lon=float(last["lon"]),
            )
            return
        await show_place_picker(update, context, "cielo")
        return
    if action == "pianeta":
        await show_pianeta_menu(update, context)
        return
    if action == "mondi":
        await show_mondi_hub(update, context)
        return
    if action == "cosmo":
        await show_cosmo(update, context)
        return
    if action == "lune":
        await show_lune_menu(update, context)
        return
    if action == "sistema":
        await show_sistema(update, context)
        return
    if action == "buchineri":
        await show_buchineri_menu(update, context)
        return
    if action == "galassia":
        await show_galassia_menu(update, context)
        return
    if action == "eclissi":
        await send_eclissi(update, context)
        return
    if action == "missioni":
        await show_missioni_menu(update, context)
        return
    if action == "astronauta":
        await show_astronauta_menu(update, context)
        return
    if action == "satelliti":
        await show_satelliti_menu(update, context)
        return
    if action == "sonde":
        await show_sonde_menu(update, context)
        return
    if action == "impara":
        await show_impara_menu(update, context)
        return
    if action == "quiz":
        await show_quiz_menu(update, context)
        return
    if action == "esopianeta":
        await show_esopianeta_menu(update, context)
        return
    if action == "nani":
        await show_nani_menu(update, context)
        return
    if action == "comete":
        await show_comete_menu(update, context)
        return
    if action == "costellazioni":
        await show_costellazioni_menu(update, context)
        return
    if action == "profondo":
        await show_profondo_menu(update, context)
        return
    if action == "abitabile":
        await send_abitabile(update, context)
        return
    if action == "vita":
        await show_vita_menu(update, context)
        return
    if action == "specchio":
        await show_specchio(update, context)
        return
    if action == "rituale":
        await send_rituale(update, context)
        return
    if action == "compat":
        await show_compat_hub(update, context)
        return
    if action == "random":
        await send_random(update, context)
        return
    if action == "missione":
        await send_missione(update, context)
        return
    if action == "oracoli":
        await show_oracoli_hub(update, context)
        return
    if action == "sibille":
        await show_lenormand_menu(update, context)
        return
    if action == "lettura":
        await show_lettura_ask(update, context)
        return
    if action == "esplora":
        await reply_html(update, context, esplora_text(), reply_markup=esplora_keyboard())
        return
    if action == "transits":
        await show_natal_transits(update, context)
        return
    if action == "rune":
        await show_rune_intro(update, context)
        return
    if action == "domanda":
        await show_domanda(update, context)
        return
    if action == "iss":
        await send_iss(update, context)
        return
    if action == "cosmico":
        await send_cosmico(update, context)
        return
    if action == "sole":
        last = context.user_data.get(CIELO_LAST_KEY)
        if isinstance(last, dict) and last.get("lat") is not None:
            await send_sole(
                update,
                context,
                name=str(last.get("name") or DEFAULT_PLACE_NAME),
                lat=float(last["lat"]),
                lon=float(last["lon"]),
            )
            return
        await show_place_picker(update, context, "sole")
        return
    if action == "eventi":
        await send_eventi(update, context)
        return
    if action == "asteroidi":
        await show_asteroid_chooser(update, context)
        return
    if action == "pianeti":
        await cmd_pianeti(update, context)
        return
    if action == "apod":
        await cmd_apod(update, context)
        return
    if action == "stelle":
        await show_stelle_menu(update, context)
        return
    if action == "pietre":
        await show_pietre_hub(update, context)
        return
    if action == "aiuto":
        nav_mark(context, "home:aiuto")
        await reply_html(update, context, help_text(), reply_markup=back_home_keyboard())
        return
    await reply_html(update, context, start_text(), reply_markup=home_keyboard())


async def on_nav_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    action = query.data.split(":")[1] if ":" in query.data else ""
    if action == "back":
        await query.answer()
        if query.message is not None:
            kind = "text" if query.message.text else "photo"
            _remember_bot_msg(context, query.message.message_id, kind)
        token = nav_pop(context)
        if not token:
            nav_clear(context)
            await reply_html(update, context, start_text(), reply_markup=home_keyboard())
            return
        await resume_nav(update, context, token)
        return
    _remember_from_callback(update, context)
    await query.answer()
    if action == "me":
        await reply_html(update, context, world_self_text(), reply_markup=nav_me_keyboard())
        return
    if action == "risposte":
        await reply_html(update, context, world_div_text(), reply_markup=nav_risposte_keyboard())
        return
    if action == "cielo":
        await reply_html(update, context, world_sky_text(), reply_markup=nav_cielo_keyboard())
        return
    if action == "universo":
        await reply_html(update, context, world_mondi_text(), reply_markup=nav_universo_keyboard())
        return


async def cmd_iss(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:iss")
    await send_iss(update, context)
    await delete_user_command(update)


async def send_iss(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🛰️ Cerco la Stazione Spaziale…")
    client = _http_client(context)
    try:
        data = await fetch_iss_position(client)
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        geo = await reverse_iss_place(client, lat, lon)
    except Exception:
        logger.exception("ISS non disponibile")
        await reply_html(
            update,
            context,
            "Le stelle sono temporaneamente non raggiungibili ✨ riprova tra poco\n\n"
            "La posizione ISS non è arrivata.",
            reply_markup=iss_keyboard(),
        )
        return
    when = datetime.fromtimestamp(int(data.get("timestamp") or 0), tz=timezone.utc).astimezone(DEFAULT_TZ)
    try:
        velocity = float(data.get("velocity") or 0)
        vel_txt = f"{velocity:,.0f} km/h".replace(",", ".")
    except (TypeError, ValueError):
        vel_txt = "—"
    try:
        alt = f"{float(data.get('altitude') or 0):.0f} km"
    except (TypeError, ValueError):
        alt = "—"
    vis = str(data.get("visibility") or "")
    vis_it = {"daylight": "al sole", "eclipsed": "in ombra terrestre", "visible": "visibile"}.get(vis, vis or "—")
    lines = [
        "🛰️ <b>INTERNATIONAL SPACE STATION</b>",
        "",
        f"📍 Sopra: <b>{e(geo['place'])}</b>",
        f"🌍 Latitudine: <code>{lat:.4f}</code>",
        f"🌍 Longitudine: <code>{lon:.4f}</code>",
        f"🚀 Velocità: {e(vel_txt)}",
        f"📏 Altitudine: {e(alt)}",
        f"👁️ Visibilità geometrica: {e(vis_it)}",
        f"🕐 {when.strftime('%d/%m/%Y %H:%M')} (Europe/Rome)",
        "",
        "<i>Posizione live Where the ISS at? (NORAD 25544). "
        "Il prossimo passaggio sopra una città richiede un servizio passi a parte: "
        "qui non lo invento.</i>",
    ]
    await reply_html(update, context, "\n".join(lines), reply_markup=iss_keyboard(geo.get("map_url")))


async def cmd_cosmico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:cosmico")
    await send_cosmico(update, context)
    await delete_user_command(update)


async def send_cosmico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vecchio COSMICO di ASTRO: ora è Interroga il cielo, e chiede la città."""
    await show_place_picker(update, context, "skyq")


async def cmd_sole(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:sole")
    await show_place_picker(update, context, "sole")
    await delete_user_command(update)


async def send_sole(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    name: str = DEFAULT_PLACE_NAME,
    lat: float = DEFAULT_LAT,
    lon: float = DEFAULT_LON,
) -> None:
    await send_typing(update)
    await deliver_text(update, context, f"☀️ Calcolo alba e tramonto su {name}…")
    client = _http_client(context)
    try:
        tz_name = await api_timezone_name(client, lat, lon)
        sun = await api_sun_times(client, lat, lon, tz_name)
    except StelleOfflineError:
        logger.exception("Sole non disponibile")
        await reply_offline(update, context)
        return
    lines = [
        f"☀️ <b>SOLE — {e(name.upper())}</b>",
        f"📅 {e(format_day_it(datetime.now(DEFAULT_TZ)))}",
        "",
        f"🌅 Alba       {e(sun.get('sunrise') or '—')}",
        f"☀️ Mezzogiorno {e(sun.get('solar_noon') or '—')}",
        f"🌇 Tramonto   {e(sun.get('sunset') or '—')}",
        f"☀️ Durata giorno  {e(sun.get('daylight') or sun.get('day_length') or '—')}",
        "",
        f"🌄 Crepuscolo civile  {e(sun.get('dawn') or '—')} → {e(sun.get('dusk') or '—')}",
        f"🌌 Crepuscolo astronomico  {e(sun.get('first_light') or '—')} → {e(sun.get('last_light') or '—')}",
        "",
        f"🌙 Alba della Luna {e(sun.get('moonrise') or '—')} · tramonto {e(sun.get('moonset') or '—')}",
        "",
        "<i>Orari live sunrisesunset.io per queste coordinate. "
        "first_light / last_light = crepuscolo astronomico dell'API.</i>",
    ]
    await reply_html(update, context, "\n".join(lines), reply_markup=sole_keyboard())


async def cmd_eventi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:eventi")
    await send_eventi(update, context)
    await delete_user_command(update)


async def send_eventi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🌠 Apro il calendario del cielo…")
    client = _http_client(context)
    now = datetime.now(DEFAULT_TZ)
    cmev_res, skyev_res, showers_res = await asyncio.gather(
        api_cosmyday_events(client, 40),
        api_skytime_events(client, now.year),
        api_meteor_showers(client),
        return_exceptions=True,
    )
    rows: list[tuple[datetime, str]] = []
    pending_en: list[tuple[datetime, str]] = []
    if isinstance(cmev_res, list):
        for item in cmev_res:
            when = _parse_event_date(item.get("date"))
            headline = str(item.get("headline") or "").strip()
            if when and headline:
                pending_en.append((when, headline))
    if pending_en:
        try:
            blob = await translate_to_italian(client, " || ".join(h for _w, h in pending_en[:12]))
            parts = [p.strip() for p in blob.split("||")]
        except StelleOfflineError:
            parts = []
        for idx, (when, original) in enumerate(pending_en[:12]):
            text = parts[idx] if idx < len(parts) and parts[idx] else event_name_it(original)
            rows.append((when, f"✨ {text}"))
    if isinstance(skyev_res, list):
        for item in skyev_res:
            kind = str(item.get("type") or "")
            if kind not in {"season", "solar-eclipse", "lunar-eclipse", "moon-phase"}:
                continue
            when = _parse_event_date(item.get("date"))
            if when is None or when < now - timedelta(hours=12):
                continue
            name = event_name_it(str(item.get("name") or kind))
            icon = {"season": "🌠", "solar-eclipse": "☀️", "lunar-eclipse": "🌕", "moon-phase": "🌙"}.get(kind, "✨")
            rows.append((when, f"{icon} {name}"))
    if isinstance(showers_res, list):
        for when, shower in upcoming_showers(showers_res, now, limit=4):
            zhr = shower.get("zhr")
            extra = f" · ~{int(zhr)}/ora" if isinstance(zhr, (int, float)) else ""
            rows.append((when, f"☄️ {shower_it_name(str(shower.get('name')))}{extra}"))
    rows.sort(key=lambda item: item[0])
    seen: set[str] = set()
    lines = ["🌠 <b>PROSSIMI EVENTI</b>", ""]
    count = 0
    for when, label in rows:
        key = f"{when.date()}:{label}"
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"{when.day:02d} {MONTHS_IT[when.month - 1][:3].upper()} — {e(label)}")
        count += 1
        if count >= 10:
            break
    if count == 0:
        await reply_offline(update, context)
        return
    lines.extend(["", "<i>Fonti live: CosmyDay, Skytime. Date calcolate, non copiate a mano.</i>"])
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("🌠 Sciami", "home:meteore"), _tarot_btn("🌑 Eclissi", "home:eclissi")],
            [_tarot_btn("☀️ Attività solare", "ev:solar"), _tarot_btn("🌙 Distanza Luna", "ev:moon")],
            nav_row(),
        ]
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=kb)


async def cmd_transiti(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _tarot_reset(context)
    _iching_reset(context)
    _osserva_reset(context)
    _rune_reset(context)
    nav_mark(context, "home:transits")
    await show_natal_transits(update, context)
    await delete_user_command(update)


async def on_sole_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    extra = query.data.split(":")[2] if query.data.count(":") >= 2 else ""
    if extra == "0":
        await query.answer("Roma")
        await send_sole(update, context, name="Roma", lat=41.9028, lon=12.4964)
        return
    if extra == "1":
        await query.answer("Milano")
        await send_sole(update, context, name="Milano", lat=45.4642, lon=9.1900)
        return
    await query.answer()


# ---------------------------------------------------------------------------
# Sette mondi: schede, cielo Roma, quiz, vita, random, missione, pietre
# ---------------------------------------------------------------------------


def _quiz_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(QUIZ_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[QUIZ_STATE_KEY] = state
    return state


def _mirror_state(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    state = context.user_data.get(MIRROR_STATE_KEY)
    if not isinstance(state, dict):
        state = {}
        context.user_data[MIRROR_STATE_KEY] = state
    return state


async def on_world_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    await query.answer()
    pages = {
        "self": (world_self_text, world_self_keyboard),
        "div": (world_div_text, world_div_keyboard),
        "asksky": (world_asksky_text, world_asksky_keyboard),
        "sky": (world_sky_text, world_sky_keyboard),
        "mondi": (world_mondi_text, world_mondi_keyboard),
        "vita": (world_vita_text, world_vita_keyboard),
        "miss": (world_miss_text, world_miss_keyboard),
        "pietre": (world_pietre_text, world_pietre_keyboard),
        "terra": (world_terra_text, world_terra_keyboard),
        "quake": (world_quake_text, world_quake_keyboard),
        "volc": (world_volc_text, world_volc_keyboard),
        "water": (world_water_text, world_water_keyboard),
        "plates": (world_plates_text, world_plates_keyboard),
    }
    page = pages.get(action)
    if page is None:
        return
    text_fn, kb_fn = page
    await reply_html(update, context, text_fn(), reply_markup=kb_fn())


async def show_pianeta_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🪐 <b>PIANETA</b>\n\n"
        "Scegli un mondo. Masse, diametro, gravità, giorno e anno arrivano da Wikidata.\n"
        "Il testo da Wikipedia. Le missioni che lo hanno visitato, se c'è una voce, dalla stessa fonte.",
        reply_markup=planets_keyboard(),
    )


async def show_lune_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🌑 <b>LUNE DEL SISTEMA SOLARE</b>\n\n"
        "Europa, Titano, Encelado e le altre. Scheda live, niente schede copiate a mano.",
        reply_markup=moons_keyboard(),
    )


async def show_sistema(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "☀️ <b>SISTEMA SOLARE</b>\n\n"
        "☀️ Sole\n🪨 Mercurio\n🌕 Venere\n🌍 Terra\n🔴 Marte\n"
        "🟠 Giove\n🪐 Saturno\n🌀 Urano\n🔵 Nettuno\n\n"
        "Tocca un mondo per la scheda live. I numeri non sono scritti nel bot.",
        reply_markup=planets_keyboard(),
    )


async def show_buchineri_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🕳️ <b>BUCHI NERI</b>\n\n"
        "Cos'è un buco nero lo dice Wikipedia. Poi tre oggetti: "
        "Sagittarius A* (supermassiccio al centro della Via Lattea), "
        "M87* e Cygnus X-1. Immagini NASA se l'archivio risponde.",
        reply_markup=blackholes_keyboard(),
    )


async def show_galassia_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🌌 Confronto le distanze su Wikidata…")
    client = _http_client(context)
    facts_rows = await asyncio.gather(*[wikidata_facts(client, g["qid"]) for g in GALAXIES])
    lines = [
        "🌌 <b>GALASSIE</b>",
        "",
        "Confronto distanze/misure dove Wikidata ha un numero. Tocca per la scheda.",
        "",
    ]
    for galaxy, facts in zip(GALAXIES, facts_rows):
        dist = next((value for label, value in facts if label == "Distanza"), "—")
        lines.append(f"{galaxy['emoji']} <b>{e(galaxy['it'])}</b> — {e(dist)}")
    lines.extend(["", "<i>Distanze live Wikidata (P2583). Non sono stime scritte a mano.</i>"])
    await reply_html(update, context, "\n".join(lines), reply_markup=galaxies_keyboard())


async def show_missioni_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🚀 <b>MISSIONI SPAZIALI</b>\n\n"
        "Artemis, James Webb, Europa Clipper, JUICE, Voyager e le altre.\n"
        "Ogni missione ha la propria scheda Wikipedia.",
        reply_markup=missions_keyboard(),
    )


async def show_astronauta_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "👨‍🚀 <b>ASTRONAUTI</b>\n\n"
        "Schede storiche da Wikipedia. Niente aneddoti scritti a mano.",
        reply_markup=astronauts_keyboard(),
    )


async def show_satelliti_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🛰️ <b>SATELLITI</b>\n\n"
        "Telescopi e piattaforme. Per la ISS c'è la posizione live.\n"
        "I passaggi osservabili sopra una città non li invento: manca un'API passi gratuita affidabile.",
        reply_markup=satellites_keyboard(),
    )


async def show_sonde_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "📡 <b>SONDE</b>\n\n"
        "Voyager, New Horizons, Cassini, Juno, JUICE, Europa Clipper.",
        reply_markup=probes_keyboard(),
    )


async def show_impara_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🎓 <b>IMPARA LO SPAZIO</b>\n\n"
        "🌍 Sistema Solare\n⭐ Stelle\n🕳️ Buchi neri\n"
        "🌌 Galassie\n🚀 Missioni\n👽 Esopianeti\n\n"
        "Ogni argomento è una mini-lezione: il riassunto Wikipedia, non un capitolo inventato.",
        reply_markup=learn_keyboard(),
    )


async def show_vita_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "👽 <b>SIAMO SOLI?</b>\n\n"
        "Non rispondiamo. Mostriamo come si cerca.\n\n"
        "🔬 Come cerchiamo la vita?\n"
        "🌊 Oceani sotto il ghiaccio\n"
        "🪐 Esopianeti\n"
        "📡 SETI\n"
        "🧫 Firme biologiche\n\n"
        "Contenuti scientifici da Wikipedia. Le ipotesi restano ipotesi.",
        reply_markup=life_keyboard(),
    )


async def send_wiki_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str, item_id: str) -> None:
    item = catalog_item(kind, item_id)
    if item is None:
        await reply_html(update, context, "Scheda non in catalogo.", reply_markup=sheet_after_keyboard(kind))
        return
    await send_typing(update)
    await deliver_text(update, context, f"{item.get('emoji', '✨')} Apro la scheda di {item.get('it')}…")
    client = _http_client(context)
    payload = await load_sheet(client, item)
    wiki = payload.get("wiki") if isinstance(payload.get("wiki"), dict) else None
    if wiki and wiki.get("lang") == "en" and wiki.get("extract"):
        try:
            wiki["extract"] = await translate_to_italian(client, str(wiki["extract"]))
            payload["wiki"] = wiki
        except StelleOfflineError:
            pass
    explore = payload.get("explore") if isinstance(payload.get("explore"), dict) else None
    if explore and explore.get("extract"):
        try:
            explore["extract"] = await translate_to_italian(client, str(explore["extract"]))
            payload["explore"] = explore
        except StelleOfflineError:
            pass
    image = payload.get("image") if isinstance(payload.get("image"), dict) else None
    if image and image.get("title"):
        try:
            image["title"] = await translate_to_italian(client, str(image["title"]))
            payload["image"] = image
        except StelleOfflineError:
            pass
    text = format_sheet(kind, item, payload)
    await reply_html(update, context, text, reply_markup=sheet_after_keyboard(kind), preview=True)


async def on_sheet_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    if len(parts) < 3:
        await query.answer()
        return
    await query.answer("Apro la scheda…")
    await send_wiki_sheet(update, context, parts[1], parts[2])


def _cielo_place(context: ContextTypes.DEFAULT_TYPE) -> tuple[str, float, float]:
    last = context.user_data.get(CIELO_LAST_KEY)
    if isinstance(last, dict) and last.get("lat") is not None:
        return (
            str(last.get("name") or DEFAULT_PLACE_NAME),
            float(last["lat"]),
            float(last["lon"]),
        )
    osserva = context.user_data.get(OSSERVA_STATE_KEY)
    if isinstance(osserva, dict):
        prev = osserva.get("last")
        if isinstance(prev, dict) and prev.get("lat") is not None:
            return (
                str(prev.get("name") or DEFAULT_PLACE_NAME),
                float(prev["lat"]),
                float(prev["lon"]),
            )
    return DEFAULT_PLACE_NAME, DEFAULT_LAT, DEFAULT_LON


def _remember_cielo_place(context: ContextTypes.DEFAULT_TYPE, name: str, lat: float, lon: float) -> None:
    context.user_data[CIELO_LAST_KEY] = {"name": name, "lat": lat, "lon": lon}


def _place_pool(kind: str) -> tuple[tuple[str, float, float], ...]:
    return PLACE_IT if kind == "it" else PLACE_WORLD


def _loc_purpose(context: ContextTypes.DEFAULT_TYPE) -> str:
    return str(context.user_data.get(LOC_PURPOSE_KEY) or "cielo")


async def show_place_picker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    purpose: str,
    *,
    step: str = "hub",
) -> None:
    context.user_data[LOC_PURPOSE_KEY] = purpose
    context.user_data[LOC_ASK_KEY] = True
    context.user_data["cielo_ask"] = False
    titles = {
        "cielo": "Da dove osservi il cielo?",
        "sole": "Da dove calcolare alba e tramonto?",
        "meteo": "Di quale città vuoi il meteo?",
        "osserva": "Da dove osservi i pianeti?",
        "skyq": "Da dove interroghi il cielo?",
        "luna": "Da dove calcolare alba e tramonto della Luna?",
    }
    prompt = titles.get(purpose, "In quale città ti trovi?")
    if step == "it":
        text = f"📍 <b>ITALIA</b>\n\n{e(prompt)}"
        markup = place_list_keyboard("it", PLACE_IT)
    elif step == "wd":
        text = f"📍 <b>MONDO</b>\n\n{e(prompt)}"
        markup = place_list_keyboard("wd", PLACE_WORLD)
    else:
        text = (
            f"📍 <b>DOVE TI TROVI?</b>\n\n"
            f"{e(prompt)}\n\n"
            "Italia, una città del mondo, oppure scrivila: vale qualsiasi luogo."
        )
        markup = place_hub_keyboard()
    await reply_html(update, context, text, reply_markup=markup)


async def apply_place(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    name: str,
    lat: float,
    lon: float,
) -> None:
    context.user_data[LOC_ASK_KEY] = False
    context.user_data["cielo_ask"] = False
    _remember_cielo_place(context, name, lat, lon)
    purpose = _loc_purpose(context)
    if purpose == "sole":
        await send_sole(update, context, name=name, lat=lat, lon=lon)
        return
    if purpose == "meteo":
        await send_weather(update, context, name=name, lat=lat, lon=lon)
        return
    if purpose == "osserva":
        await send_osserva(update, context, name=name, lat=lat, lon=lon)
        return
    if purpose == "skyq":
        await send_sky_oracle(update, context, name=name, lat=lat, lon=lon)
        return
    if purpose == "luna":
        await send_luna_here(update, context, name=name, lat=lat, lon=lon)
        return
    await send_cielo(update, context, name=name, lat=lat, lon=lon)


async def receive_place_city(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    await send_typing(update)
    await deliver_text(update, context, "📍 Cerco la città…")
    client = _http_client(context)
    try:
        places = await api_geocode_place(client, text)
    except StelleOfflineError:
        await reply_html(
            update,
            context,
            "Non trovo quel luogo. Prova <code>Bologna, Italia</code> o <code>Tokyo, Giappone</code>.",
            reply_markup=place_hub_keyboard(),
        )
        return
    place = places[0]
    await delete_user_command(update)
    await apply_place(
        update,
        context,
        name=str(place.get("name") or text),
        lat=float(place["lat"]),
        lon=float(place["lon"]),
    )


async def on_wx_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    last = context.user_data.get(CIELO_LAST_KEY)
    if not isinstance(last, dict) or last.get("lat") is None:
        await query.answer()
        purpose = "luna" if action == "luna" else "meteo"
        await show_place_picker(update, context, purpose)
        return
    name = str(last.get("name") or DEFAULT_PLACE_NAME)
    lat = float(last["lat"])
    lon = float(last["lon"])
    await query.answer()
    if action == "luna":
        await send_luna_here(update, context, name=name, lat=lat, lon=lon)
        return
    await send_weather(update, context, name=name, lat=lat, lon=lon)


async def on_loc_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""
    extra2 = parts[3] if len(parts) > 3 else ""
    if action == "go" and extra:
        await query.answer()
        await show_place_picker(update, context, extra)
        return
    if action in {"it", "wd"}:
        await query.answer()
        await show_place_picker(update, context, _loc_purpose(context), step=action)
        return
    if action == "ask":
        await query.answer()
        context.user_data[LOC_ASK_KEY] = True
        await reply_html(
            update,
            context,
            "📍 <b>Scrivi la città</b>\n\n"
            "Città e paese. Esempio: <code>Lisbona, Portogallo</code>, "
            "<code>Buenos Aires</code>, <code>Osaka, Giappone</code>.",
            reply_markup=place_hub_keyboard(),
        )
        return
    if action == "city" and extra in {"it", "wd"} and extra2.isdigit():
        pool = _place_pool(extra)
        idx = int(extra2)
        if 0 <= idx < len(pool):
            name, lat, lon = pool[idx]
            await query.answer(name)
            await apply_place(update, context, name, lat, lon)
            return
    await query.answer()


async def send_weather(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    name: str,
    lat: float,
    lon: float,
) -> None:
    _remember_cielo_place(context, name, lat, lon)
    await send_typing(update)
    await deliver_text(update, context, f"🌤️ Scarico il meteo di {name}…")
    client = _http_client(context)
    try:
        data = await fetch_forecast(client, lat, lon)
    except Exception:
        logger.exception("Meteo Open-Meteo non disponibile")
        await reply_offline(update, context)
        return
    await reply_html(update, context, format_forecast(data, name=name), reply_markup=meteo_keyboard())


async def send_sky_oracle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    name: str,
    lat: float,
    lon: float,
) -> None:
    _remember_cielo_place(context, name, lat, lon)
    await send_typing(update)
    await deliver_text(update, context, f"🌌 Interrogo il cielo sopra {name}…")
    client = _http_client(context)
    now = datetime.now(DEFAULT_TZ)
    try:
        tz_name = await api_timezone_name(client, lat, lon)
    except StelleOfflineError:
        tz_name = str(DEFAULT_TZ)
    sky_res, sun_res, card_res, moon_res = await asyncio.gather(
        api_skymap(client, lat, lon),
        api_sun_times(client, lat, lon, tz_name),
        api_tarot_draw(client, count=1, include_minor=False),
        api_moon_observatory(client),
        return_exceptions=True,
    )
    phase_raw = ""
    if isinstance(moon_res, dict):
        phase_raw = str(moon_res.get("moon_phase") or "")
    phase = moon_phase_label(phase_raw) if phase_raw else ""
    pack = LUNAR_ORACLE[lunar_key(phase_raw)] if phase_raw else {}
    visible: list[tuple[str, str]] = []
    night = True
    if isinstance(sky_res, dict):
        bodies = [b for b in (sky_res.get("bodies") or []) if isinstance(b, dict)]
        for body in bodies:
            raw = str(body.get("name") or "")
            if not raw:
                continue
            label, _emoji = PLANET_LABELS.get(raw, (raw, "🪐"))
            visible.append((raw, label))
        try:
            sun_alt = float(sky_res.get("sun_alt")) if sky_res.get("sun_alt") is not None else None
        except (TypeError, ValueError):
            sun_alt = None
        if sun_alt is not None:
            night = sun_alt < 0
    card_name = ""
    if isinstance(card_res, list) and card_res:
        name_en = str((card_res[0] or {}).get("name") or "")
        if name_en:
            try:
                card_name = await translate_to_italian(client, name_en)
            except StelleOfflineError:
                card_name = name_en
    reading = interpret_asked_sky(
        place=name,
        phase_label=phase,
        phase_message=str(pack.get("message") or ""),
        visible=visible,
        night=night,
        card_name=card_name,
    )
    lines = [
        "🌌 <b>INTERROGA IL CIELO</b>",
        f"📍 {e(name)} · {e(format_day_it(now))}",
        "",
        "🔭 <b>SOPRA DI TE</b>",
    ]
    if phase:
        lines.append(f"🌙 {e(phase)}")
    if isinstance(sun_res, dict):
        lines.append(
            f"☀️ Alba {e(sun_res.get('sunrise') or '—')} · tramonto {e(sun_res.get('sunset') or '—')}"
        )
    if visible:
        shown = []
        for raw, label in visible[:6]:
            emoji = PLANET_LABELS.get(raw, (label, "🪐"))[1]
            shown.append(f"{emoji} {label}")
        lines.append("In vista: " + ", ".join(shown))
    else:
        lines.append("<i>Nessun pianeta sopra l'orizzonte in questo istante.</i>")
    if card_name:
        lines.extend(["", f"🃏 Segno pescato: <b>{e(card_name)}</b>"])
    lines.extend(
        [
            "",
            "✨ <b>IN PRATICA</b>",
            e(reading),
            "",
            "<i>Altezza e orari sono astronomia. La lettura è folklore, non un effetto dimostrato.</i>",
        ]
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=cosmico_keyboard())


async def send_luna_here(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    name: str,
    lat: float,
    lon: float,
) -> None:
    _remember_cielo_place(context, name, lat, lon)
    await send_typing(update)
    client = _http_client(context)
    try:
        tz_name = await api_timezone_name(client, lat, lon)
        sun = await api_sun_times(client, lat, lon, tz_name)
        sky = await api_skymap(client, lat, lon)
    except StelleOfflineError:
        await reply_offline(update, context)
        return
    moon = sky.get("moon") if isinstance(sky, dict) and isinstance(sky.get("moon"), dict) else {}
    illum = moon.get("illum")
    try:
        illum_s = f"{float(illum):.0f}%" if illum is not None else "—"
    except (TypeError, ValueError):
        illum_s = "—"
    lines = [
        f"🌙 <b>LA LUNA — {e(name.upper())}</b>",
        f"📅 {e(format_day_it(datetime.now(DEFAULT_TZ)))}",
        "",
        f"💡 Illuminazione (mappa live): <b>{e(illum_s)}</b>",
        f"⬆️ Alba {e(sun.get('moonrise') or '—')} · ⬇️ tramonto {e(sun.get('moonset') or '—')}",
        f"☀️ Sole: alba {e(sun.get('sunrise') or '—')} · tramonto {e(sun.get('sunset') or '—')}",
        "",
        "<i>Orari sunrisesunset.io e illuminazione dalla mappa. "
        "Per l'oracolo della fase, sta in 🔮 ORACOLO → Interroga il cielo.</i>",
    ]
    await reply_html(
        update,
        context,
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(
            [
                [_tarot_btn("📍 Cambia città", "loc:go:luna"), _tarot_btn("🔄 Aggiorna", "wx:luna")],
                nav_row(),
            ]
        ),
    )


async def send_cielo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    name: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> None:
    if name is None or lat is None or lon is None:
        name, lat, lon = _cielo_place(context)
    _remember_cielo_place(context, name, lat, lon)
    await send_typing(update)
    await deliver_text(update, context, f"🔭 Cosa si vede adesso sopra {name}…")
    client = _http_client(context)
    try:
        tz_name = await api_timezone_name(client, lat, lon)
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = DEFAULT_TZ
        now = datetime.now(tz)
        sky_res, sun_res, showers_res = await asyncio.gather(
            api_skymap(client, lat, lon),
            api_sun_times(client, lat, lon, tz_name),
            api_meteor_showers(client),
            return_exceptions=True,
        )
    except StelleOfflineError:
        await reply_offline(update, context)
        return

    lines = [
        "🌌 <b>IL CIELO DI OGGI</b>",
        f"📍 {e(name)}",
        f"🕘 {now.strftime('%H:%M')} · {e(format_day_it(now))}",
        "",
    ]
    marks: list[dict[str, Any]] = []
    if isinstance(sky_res, dict):
        marks = collect_marks(sky_res)
        chart = text_sky_map(marks)
        if chart:
            lines.append("🔭 <b>Cosa guardare adesso</b>")
            lines.append(f"<pre>{e(chart)}</pre>")
            lines.append("")
        for mark in marks[:8]:
            lines.append(visibility_line(mark))
        moon = sky_res.get("moon") if isinstance(sky_res.get("moon"), dict) else {}
        sun_alt = sky_res.get("sun_alt")
        moon_alt = moon.get("alt") if moon else None
        moon_illum = moon.get("illum") if moon else None
        try:
            sun_alt_f = float(sun_alt) if sun_alt is not None else None
        except (TypeError, ValueError):
            sun_alt_f = None
        try:
            moon_alt_f = float(moon_alt) if moon_alt is not None else None
        except (TypeError, ValueError):
            moon_alt_f = None
        try:
            moon_illum_f = float(moon_illum) if moon_illum is not None else None
        except (TypeError, ValueError):
            moon_illum_f = None
        lines.append("")
        lines.append(milky_way_hint(sun_alt=sun_alt_f, moon_alt=moon_alt_f, moon_illum=moon_illum_f))
        asterisms = [str(a) for a in (sky_res.get("asterisms") or []) if a]
        if asterisms:
            try:
                names_it = await translate_to_italian(client, ", ".join(asterisms[:6]))
            except StelleOfflineError:
                names_it = ", ".join(asterisms[:6])
            lines.append(f"✨ Costellazioni in mappa: {e(names_it)}")
    else:
        lines.append("<i>Mappa del cielo non disponibile</i>")

    if isinstance(sun_res, dict):
        lines.append("")
        lines.append(
            f"🌅 Sole tramonta {e(sun_res.get('sunset') or '—')} · "
            f"⏰ Luna sorge {e(sun_res.get('moonrise') or '—')} · "
            f"tramonta {e(sun_res.get('moonset') or '—')}"
        )
        if sun_res.get("sunrise"):
            lines.append(
                f"☀️ Sole sorge {e(sun_res.get('sunrise'))} · "
                f"durata {e(sun_res.get('daylight') or sun_res.get('day_length') or '—')}"
            )

    lines.append("")
    if isinstance(showers_res, list):
        upcoming = upcoming_showers(showers_res, datetime.now(DEFAULT_TZ), limit=1)
        if upcoming:
            when, shower = upcoming[0]
            lines.append(
                f"☄️ Prossimo sciame — {e(shower_it_name(str(shower.get('name'))))} "
                f"({e(format_date_it(when.isoformat()))})"
            )
        else:
            lines.append("☄️ Prossimo evento — nessun sciame in calendario vicino")
    else:
        lines.append("☄️ Calendario sciami non disponibile")

    lines.extend(
        [
            "",
            "↑ sopra · ↓ sotto · 👁 mag ≤ 6 (soglia applicata al dato live)",
            "<i>Mappa del cielo, orari del Sole e della Luna, Skytime. Nessuna posizione scritta a mano.</i>",
        ]
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=cielo_keyboard())


def cielo_picker_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for idx, (city, _lat, _lon) in enumerate(OSSERVA_CITIES):
        pair.append(_tarot_btn(f"📍 {city}", f"cielo:city:{idx}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([_tarot_btn("✍️ Altra città", "cielo:ask")])
    rows.append(nav_row())
    return InlineKeyboardMarkup(rows)


async def show_cielo_picker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_place_picker(update, context, "cielo")


async def receive_cielo_city(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    await send_typing(update)
    await deliver_text(update, context, "📍 Cerco la città…")
    client = _http_client(context)
    try:
        places = await api_geocode_place(client, text)
    except StelleOfflineError:
        await reply_html(
            update,
            context,
            "Non trovo quel luogo. Prova <code>Bologna, Italia</code>.",
            reply_markup=cielo_picker_keyboard(),
        )
        return
    place = places[0]
    context.user_data["cielo_ask"] = False
    await delete_user_command(update)
    await send_cielo(
        update,
        context,
        name=str(place.get("name") or text),
        lat=float(place["lat"]),
        lon=float(place["lon"]),
    )


async def show_stelle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "⭐ <b>STELLE</b>\n\n"
        "Schede Wikipedia/Wikidata, oppure il cielo live sopra di te.\n"
        "La foto NASA resta un bottone a parte: non mescolo catalogo e APOD.",
        reply_markup=stelle_menu_keyboard(),
    )


async def send_stars_now(update: Update, context: ContextTypes.DEFAULT_TYPE, *, brightest_only: bool = False) -> None:
    name, lat, lon = _cielo_place(context)
    await send_typing(update)
    client = _http_client(context)
    try:
        sky = await api_skymap(client, lat, lon)
    except StelleOfflineError:
        await reply_offline(update, context)
        return
    stars = [s for s in (sky.get("brightest") or []) if isinstance(s, dict) and s.get("name")]
    if not stars:
        await reply_html(update, context, "Nessuna stella luminosa in questa mappa.", reply_markup=stelle_menu_keyboard())
        return
    if brightest_only:
        top = stars[0]
        match = next(
            (
                s
                for s in STARS
                if s["en"].lower() == str(top["name"]).lower() or s["it"].lower() == str(top["name"]).lower()
            ),
            None,
        )
        if match:
            await send_wiki_sheet(update, context, "t", match["id"])
            return
        lines = [
            "✨ <b>STELLA PIÙ LUMINOSA ORA</b>",
            f"📍 {e(name)}",
            visibility_line(
                {
                    "name": star_it(str(top["name"])),
                    "emoji": "⭐",
                    "alt": top.get("alt"),
                    "az": top.get("az"),
                    "compass": compass_it(str(top.get("compass") or "")),
                    "mag": top.get("mag"),
                }
            ),
        ]
        await reply_html(update, context, "\n".join(lines), reply_markup=stelle_menu_keyboard())
        return
    lines = [f"👁 <b>STELLE VISIBILI ORA</b>", f"📍 {e(name)}", ""]
    for star in stars[:8]:
        lines.append(
            visibility_line(
                {
                    "name": star_it(str(star["name"])),
                    "emoji": "⭐",
                    "alt": star.get("alt"),
                    "az": star.get("az"),
                    "compass": compass_it(str(star.get("compass") or "")),
                    "mag": star.get("mag"),
                }
            )
        )
    lines.append("")
    lines.append("<i>Elenco delle stelle più luminose dalla mappa live. Tocca una scheda dal menu per Wikipedia.</i>")
    await reply_html(update, context, "\n".join(lines), reply_markup=stelle_menu_keyboard())


async def send_star_of_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = STARS[datetime.now(DEFAULT_TZ).timetuple().tm_yday % len(STARS)]
    await send_wiki_sheet(update, context, "t", item["id"])


async def send_random_star(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = random.choice(STARS)
    await send_wiki_sheet(update, context, "t", item["id"])


async def send_near_or_giants(update: Update, context: ContextTypes.DEFAULT_TYPE, ids: tuple[str, ...]) -> None:
    lines = ["⭐ <b>SELEZIONE</b>", "Tocca per la scheda live.", ""]
    buttons = []
    for sid in ids:
        item = by_id(STARS, sid)
        if not item:
            continue
        lines.append(f"{item['emoji']} {item['it']}")
        buttons.append(_tarot_btn(f"{item['emoji']} {item['it']}", f"w:t:{item['id']}"))
    rows = []
    pair: list[InlineKeyboardButton] = []
    for btn in buttons:
        pair.append(btn)
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([_tarot_btn("⭐ Stelle", "home:stelle")])
    rows.append(nav_row())
    await reply_html(update, context, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def show_costellazioni_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "✨ <b>COSTELLAZIONI</b>\n\n"
        "Schede Wikipedia (mitologia inclusa nella voce).\n"
        "Visibili stasera = asterismi nella mappa del cielo della tua città.",
        reply_markup=costellazioni_keyboard(),
    )


async def send_constellations_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name, lat, lon = _cielo_place(context)
    await send_typing(update)
    client = _http_client(context)
    try:
        sky = await api_skymap(client, lat, lon)
    except StelleOfflineError:
        await reply_offline(update, context)
        return
    asterisms = [str(a) for a in (sky.get("asterisms") or []) if a]
    if not asterisms:
        await reply_html(update, context, "Nessun asterismo in questa ora.", reply_markup=costellazioni_keyboard())
        return
    try:
        names_it = await translate_to_italian(client, ", ".join(asterisms[:10]))
    except StelleOfflineError:
        names_it = ", ".join(asterisms[:10])
    await reply_html(
        update,
        context,
        f"👁 <b>IN MAPPA STASERA</b>\n📍 {e(name)}\n\n{e(names_it)}\n\n"
        "<i>Nomi dalla mappa live. Apri una scheda per storia e stelle principali.</i>",
        reply_markup=costellazioni_keyboard(),
    )


async def show_profondo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🛰️ <b>CIELO PROFONDO</b>\n\n"
        "Messier, nebulose, ammassi, quasar, supernovae. "
        "Poi galassie, buchi neri, esopianeti.",
        reply_markup=profondo_keyboard(),
    )


async def show_nani_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🧊 <b>PIANETI NANI</b>\n\nPlutone, Cerere, Eris, Haumea, Makemake.\n"
        "Schede Wikipedia + misure Wikidata.",
        reply_markup=dwarfs_keyboard(),
    )


async def show_comete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "☄️ <b>COMETE</b>\n\n"
        "Una selezione con voce Wikipedia. "
        "JPL Horizons cataloga migliaia di comete: qui non invento effemeridi che l'API pubblica non mi dà in blocco.",
        reply_markup=comets_keyboard(),
    )


async def send_solar_activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    client = _http_client(context)
    kp, flare = await asyncio.gather(kp_index(client), latest_flare(client))
    lines = ["☀️ <b>ATTIVITÀ SOLARE</b>", ""]
    if kp:
        lines.append(f"Kp: <b>{e(kp.get('kp'))}</b> · {e(kp_label_it(str(kp.get('label') or '')))}")
    else:
        lines.append("Indice Kp non arrivato.")
    if flare:
        lines.append(
            f"Ultimo brillamento in raggi X: {e(flare.get('maxClass') or '—')} "
            f"({e(flare.get('maxTime') or flare.get('beginTime') or '')})"
        )
    else:
        lines.append("Brillamenti in raggi X non arrivati.")
    lines.extend(["", "<i>Skytime e NOAA. Non è una previsione di aurore sulla tua città.</i>"])
    await reply_html(update, context, "\n".join(lines), reply_markup=eventi_extra_keyboard())


async def send_moon_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    client = _http_client(context)
    now = datetime.now(timezone.utc)
    rows = await moon_distance_events(client, now.year)
    nxt = next_distance_event(rows, now)
    if nxt is None:
        await reply_offline(update, context)
        return
    when = nxt.get("date") or ""
    kind = str(nxt.get("kind") or "")
    kind_it = {"perigee": "perigeo (più vicina)", "apogee": "apogeo (più lontana)"}.get(kind, kind)
    try:
        dist = f"{float(nxt['distanceKm']):,.0f} km".replace(",", ".")
    except (TypeError, ValueError, KeyError):
        dist = "—"
    text = (
        "🌙 <b>DISTANZA DELLA LUNA</b>\n\n"
        f"Prossimo {e(kind_it)}: {e(when)}\n"
        f"Distanza: <code>{e(dist)}</code>\n\n"
        "Una superluna è un plenilunio vicino al perigeo. "
        "Qui do le date di distanza; la fase piena sta in /eclissi e /eventi. "
        "Non unisco i due se l'API non li marca insieme."
    )
    await reply_html(update, context, text, reply_markup=eventi_extra_keyboard())


async def show_esopianeta_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "👽 <b>ESOPIANETI</b>\n\n"
        "Archivio NASA, tabella ps. I filtri sono numerici:\n"
        "🌍 raggio/Teq simili alla Terra\n"
        "🔥 Teq molto alta\n"
        "💎 raggio o temperatura estremi\n"
        "🌊 raggio 1.8–3.5 R⊕ in fascia Teq — <b>modello</b>, non oceano confermato\n"
        "🔭 ordinati per anno di scoperta\n\n"
        "Oltre 6000 mondi confermati nell'archivio: ne pesco un sottoinsieme live.",
        reply_markup=exo_keyboard(),
    )


async def send_exo_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🪐 Interrogo l'archivio NASA…")
    client = _http_client(context)
    if kind == "rand":
        row = await random_exoplanet(client)
        if row is None:
            await reply_offline(update, context)
            return
        await reply_html(update, context, format_exoplanet(row), reply_markup=exo_keyboard())
        return
    rows = await exoplanets_by_filter(client, kind, limit=8)
    titles = {
        "earth": "🌍 Candidati simili alla Terra (raggio/Teq)",
        "hell": "🔥 Teq molto alta",
        "extreme": "💎 Estremi (Teq o raggio)",
        "ocean": "🌊 Raggio 1.8–3.5 R⊕ in fascia Teq — modello, non oceano",
        "recent": "🔭 Scoperti di recente (anno archivio)",
        "hz": "🌍 Zona abitabile (modello)",
    }
    blurbs = {
        "earth": "Filtro archivio: raggio 0.8–1.5 R⊕ e Teq 200–280 K. Similitudine numerica, non analoghi confermati.",
        "hell": "Filtro archivio: Teq sopra 1500 K. Mondi caldi secondo il modello, non una geologia infernale visitata.",
        "extreme": "Filtro archivio: Teq sopra 2000 K oppure raggio sopra 12 R⊕.",
        "ocean": "Filtro archivio: raggio 1.8–3.5 R⊕ e Teq 180–320 K. Fascia usata nei modelli per mondi ricchi di volatili — non oceani confermati.",
        "recent": "Filtro archivio: ordinati per anno di scoperta.",
        "hz": "Filtro archivio: Teq 180–310 K e raggio sotto 1.8 R⊕. Modello orbitale, non vita.",
    }
    if not rows:
        await reply_offline(update, context)
        return
    text = format_exo_list(
        rows,
        title=titles.get(kind, "Esopianeti"),
        blurb=blurbs.get(kind, "Filtro live sull'archivio NASA."),
    )
    await reply_html(update, context, text, reply_markup=exo_keyboard())


async def on_cielo_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""
    if action == "cat":
        await query.answer()
        await reply_html(
            update,
            context,
            "📚 <b>CATALOGHI</b>\n"
            "<i>Oggetti del sistema e del cielo profondo, da Wikipedia.</i>\n\n"
            "Nani, comete, profondo e pietre dallo spazio. Non un dump JPL.",
            reply_markup=sky_catalog_keyboard(),
        )
        return
    if action == "pick":
        await query.answer()
        await show_cielo_picker(update, context)
        return
    if action == "ask":
        await query.answer()
        _osserva_reset(context)
        context.user_data["cielo_ask"] = True
        await reply_html(
            update,
            context,
            "📍 <b>Da dove guardi?</b>\n\n"
            "Scrivi città e paese.\n"
            "Esempio: <code>Bologna, Italia</code>",
            reply_markup=cielo_picker_keyboard(),
        )
        return
    if action == "city":
        try:
            idx = int(extra)
        except ValueError:
            await query.answer()
            return
        if 0 <= idx < len(OSSERVA_CITIES):
            name, lat, lon = OSSERVA_CITIES[idx]
            await query.answer(name)
            context.user_data["cielo_ask"] = False
            await send_cielo(update, context, name=name, lat=lat, lon=lon)
            return
        await query.answer()
        return
    if action == "planets":
        await query.answer()
        name, lat, lon = _cielo_place(context)
        await send_osserva(update, context, name=name, lat=lat, lon=lon)
        return
    await query.answer()


async def on_st_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    if action == "rand":
        await query.answer()
        await send_random_star(update, context)
        return
    if action == "day":
        await query.answer()
        await send_star_of_day(update, context)
        return
    if action == "bright":
        await query.answer("Mappa…")
        await send_stars_now(update, context, brightest_only=True)
        return
    if action == "now":
        await query.answer("Mappa…")
        await send_stars_now(update, context)
        return
    if action == "near":
        await query.answer()
        await send_near_or_giants(update, context, NEAR_STARS)
        return
    if action == "rg":
        await query.answer()
        await send_near_or_giants(update, context, GIANT_STARS)
        return
    if action == "nasa":
        await query.answer("Archivio NASA…")
        await send_stelle_nasa(update, context)
        return
    await query.answer()


async def on_co_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    if action == "day":
        await query.answer()
        item = CONSTELLATIONS[datetime.now(DEFAULT_TZ).timetuple().tm_yday % len(CONSTELLATIONS)]
        await send_wiki_sheet(update, context, "k", item["id"])
        return
    if action == "rand":
        await query.answer()
        item = random.choice(CONSTELLATIONS)
        await send_wiki_sheet(update, context, "k", item["id"])
        return
    if action == "now":
        await query.answer("Mappa…")
        await send_constellations_now(update, context)
        return
    await query.answer()


async def on_ev_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    if action == "solar":
        await query.answer("Cielo…")
        await send_solar_activity(update, context)
        return
    if action == "moon":
        await query.answer("Cielo…")
        await send_moon_distance(update, context)
        return
    await query.answer()


async def on_xp_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    kind = query.data.split(":")[1] if ":" in query.data else ""
    if kind in {"rand", "earth", "hell", "extreme", "ocean", "recent", "hz"}:
        await query.answer("Archivio NASA…")
        await send_exo_filter(update, context, kind)
        return
    await query.answer()


def _mondi_remember(context: ContextTypes.DEFAULT_TYPE, row: dict[str, Any], *, kind: str = "exo") -> None:
    context.user_data[MONDI_LAST_KEY] = {
        "name": str(row.get("pl_name") or row.get("name") or ""),
        "host": str(row.get("hostname") or row.get("host") or ""),
        "kind": kind,
        "row": row,
    }


async def show_mondi_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(update, context, mondi_hub_text(), reply_markup=mondi_hub_keyboard())


async def show_cosmo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(update, context, cosmo_text(), reply_markup=cosmo_keyboard())


async def show_sistemi_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(update, context, sistemi_text(), reply_markup=sistemi_keyboard())


async def show_sistema_chooser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "☀️ <b>SISTEMA</b>\n\n"
        "Il Sistema Solare resta le schede Wikidata.\n"
        "I sistemi extrasolari sono alberi dell'archivio NASA: solo i pianeti che elenca.",
        reply_markup=sistema_chooser_keyboard(),
    )


async def send_mondi_world(update: Update, context: ContextTypes.DEFAULT_TYPE, row: dict[str, Any]) -> None:
    _mondi_remember(context, row, kind="exo")
    await reply_html(
        update,
        context,
        format_exoplanet(row),
        reply_markup=mondi_after_keyboard(has_system=bool(row.get("hostname"))),
    )


async def send_mondi_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🪐 Interrogo l'archivio NASA…")
    client = _http_client(context)
    rows = await exoplanets_by_filter(client, kind, limit=8)
    if not rows:
        await reply_offline(update, context)
        return
    context.user_data[MONDI_LIST_KEY] = rows
    spec = FILTERS.get(kind)
    label = spec[2] if spec else kind
    numbered = []
    for idx, row in enumerate(rows, start=1):
        clone = dict(row)
        clone["pl_name"] = f"{idx}. {row.get('pl_name') or '—'}"
        numbered.append(clone)
    text = format_exo_list(
        numbered,
        title=f"🌍 {label}",
        blurb="Tocca un numero per la scheda. I filtri sono ricerche nell'archivio, non geologia.",
    )
    await reply_html(update, context, text, reply_markup=mondi_list_keyboard(len(rows)))


async def send_mondi_random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🎲 Pesco un mondo reale dall'archivio…")
    client = _http_client(context)
    row = await random_exoplanet(client)
    if row is None:
        await reply_offline(update, context)
        return
    header = "🌌 <b>HAI SCOPERTO UN NUOVO MONDO</b>\n<i>Nuovo per questa chat, non una scoperta NASA tua.</i>\n\n"
    _mondi_remember(context, row, kind="exo")
    await reply_html(
        update,
        context,
        header + format_exoplanet(row),
        reply_markup=mondi_after_keyboard(has_system=bool(row.get("hostname"))),
    )


async def send_mondi_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    client = _http_client(context)
    row = await planet_of_the_day(client, datetime.now(DEFAULT_TZ).timetuple().tm_yday)
    if row is None:
        await reply_offline(update, context)
        return
    await send_mondi_world(update, context, row)


async def send_system_card(update: Update, context: ContextTypes.DEFAULT_TYPE, host: str) -> None:
    await send_typing(update)
    await deliver_text(update, context, f"⭐ Apro il sistema {host}…")
    client = _http_client(context)
    card = await system_card(client, host)
    if card is None:
        await reply_offline(update, context)
        return
    planets = card.get("planets") if isinstance(card.get("planets"), list) else []
    if planets:
        context.user_data[MONDI_LIST_KEY] = planets
        _mondi_remember(context, planets[0], kind="exo")
    await reply_html(
        update,
        context,
        format_system_tree(card),
        reply_markup=mondi_list_keyboard(min(len(planets), 8), back="md:sys") if planets else sistemi_keyboard(),
    )


async def send_systems_kind(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    await send_typing(update)
    await deliver_text(update, context, "⭐ Cerco sistemi nell'archivio…")
    client = _http_client(context)
    rows = await systems_by_kind(client, kind, limit=8)
    if not rows:
        await reply_offline(update, context)
        return
    context.user_data[MONDI_SYS_KEY] = rows
    titles = {
        "bin": "⭐⭐ Sistemi binari (due stelle)",
        "multi": "⭐⭐⭐ Sistemi multipli (tre o più stelle)",
        "packed": "🪐 Sistemi con molti pianeti (almeno sei)",
        "hzsys": "🌱 Sistemi con un candidato in zona abitabile (modello)",
        "near": "⭐ Sistemi vicini",
    }
    lines = [f"<b>{titles.get(kind, 'Sistemi')}</b>", "", "Tocca un numero per l'albero del sistema.", ""]
    for idx, row in enumerate(rows, start=1):
        host = row.get("hostname") or "—"
        dist = row.get("sy_dist")
        try:
            dist_txt = f"{float(dist):.1f} pc" if dist is not None else "—"
        except (TypeError, ValueError):
            dist_txt = "—"
        lines.append(
            f"{idx}. <b>{e(host)}</b> · {e(dist_txt)} · "
            f"stelle {e(row.get('sy_snum') if row.get('sy_snum') is not None else '—')} · "
            f"pianeti {e(row.get('sy_pnum') if row.get('sy_pnum') is not None else '—')}"
        )
    await reply_html(update, context, "\n".join(lines), reply_markup=sistemi_list_keyboard(len(rows)))


async def send_mission_worlds(update: Update, context: ContextTypes.DEFAULT_TYPE, mission_id: str) -> None:
    item = by_id(MISSIONS, mission_id)
    if item is None:
        await reply_html(update, context, "Missione non in catalogo.", reply_markup=miss_worlds_keyboard())
        return
    targets = worlds_for_mission(mission_id)
    lines = [
        f"{item.get('emoji', '🚀')} <b>{e(item['it'])} → MONDI</b>",
        "",
        "Collegamenti di catalogo: corpi per cui abbiamo una scheda Wikipedia.",
        "Le scoperte stanno nella voce della missione, non le riassumo a mano.",
        "",
    ]
    buttons: list[InlineKeyboardButton] = []
    if not targets:
        lines.append("Nessun corpo di catalogo agganciato. Apro comunque la scheda missione.")
    for kind, item_id in targets:
        target = catalog_item(kind, item_id)
        if not target:
            continue
        lines.append(f"{target.get('emoji', '•')} {target['it']}")
        buttons.append(_tarot_btn(f"{target.get('emoji', '•')} {target['it']}", f"w:{kind}:{item_id}"))
    rows = []
    pair: list[InlineKeyboardButton] = []
    for btn in buttons:
        pair.append(btn)
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([_tarot_btn("📖 Scheda missione", f"w:n:{mission_id}")])
    rows.append([_tarot_btn("🚀 Altre missioni", "md:miss")])
    rows.append(nav_row())
    await reply_html(update, context, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def send_nebulae(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    neb_ids = {"m42", "m57", "m1", "pillars"}
    items = [item for item in DEEP_SKY if item["id"] in neb_ids]
    buttons = [_tarot_btn(f"{item['emoji']} {item['it']}", f"w:o:{item['id']}") for item in items]
    rows = []
    pair: list[InlineKeyboardButton] = []
    for btn in buttons:
        pair.append(btn)
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([_tarot_btn("🌌 COSMO", "md:cosmo")])
    rows.append(nav_row())
    await reply_html(
        update,
        context,
        "🌀 <b>NEBULOSE</b>\n\nSchede Wikipedia del catalogo profondo. Niente foto inventate.",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def on_md_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""

    if action == "hub":
        await query.answer()
        await show_mondi_hub(update, context)
        return
    if action == "cosmo":
        await query.answer()
        await show_cosmo(update, context)
        return
    if action == "sys":
        await query.answer()
        await show_sistemi_menu(update, context)
        return
    if action == "life":
        await query.answer()
        await reply_html(update, context, life_plus_text(), reply_markup=life_plus_keyboard())
        return
    if action == "ss":
        await query.answer()
        await reply_html(
            update,
            context,
            "🛰️ <b>MONDI DEL SISTEMA SOLARE</b>\n\n"
            "Atmosfera, gravità, giorno e anno: solo se Wikidata li ha.\n"
            "Curiosità = estratto Wikipedia, non un copione.",
            reply_markup=ss_bodies_keyboard(),
        )
        return
    if action == "miss":
        await query.answer()
        await reply_html(
            update,
            context,
            "🚀 <b>CHI È ANDATO LÌ?</b>\n\n"
            "Missione → corpi del catalogo. Poi la voce Wikipedia per scoperte e immagini.",
            reply_markup=miss_worlds_keyboard(),
        )
        return
    if action == "neb":
        await query.answer()
        await send_nebulae(update, context)
        return
    if action == "rand":
        await query.answer("Archivio NASA…")
        await send_mondi_random(update, context)
        return
    if action == "day":
        await query.answer()
        await send_mondi_day(update, context)
        return
    if action == "gen":
        await query.answer()
        world = generate_world()
        _mondi_remember(context, world, kind="imag")
        await reply_html(update, context, format_imaginary(world), reply_markup=mondi_after_keyboard())
        return
    if action == "rogue":
        await query.answer("Archivio…")
        client = _http_client(context)
        rows = await exoplanets_by_filter(client, "rogue", limit=8)
        if rows:
            context.user_data[MONDI_LIST_KEY] = rows
            text = format_exo_list(
                rows,
                title="🌑 Senza stella (righe senza stella ospite)",
                blurb="Se l'archivio non ha una stella ospite. Altrimenti non invento pianeti erranti.",
            )
            await reply_html(update, context, text, reply_markup=mondi_list_keyboard(len(rows)))
            return
        await send_wiki_sheet(update, context, "v", "rogue")
        return
    if action == "volc":
        await query.answer()
        await send_wiki_sheet(update, context, "m", "io")
        return
    if action == "rings":
        await query.answer()
        await reply_html(
            update,
            context,
            "💍 <b>MONDI CON ANELLI</b>\n\n"
            "Nel Sistema Solare le schede sono Saturno e Urano (anelli noti, voce Wikipedia).\n"
            "Gli anelli extrasolari non sono un campo dell'archivio: non li segno io.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [_tarot_btn("💍 Saturno", "w:p:saturn"), _tarot_btn("🌀 Urano", "w:p:uranus")],
                    [_tarot_btn("🌍 Esplora", "md:hub")],
                    nav_row(),
                ]
            ),
        )
        return
    if action == "moons":
        await query.answer()
        await reply_html(
            update,
            context,
            "🌙 <b>MOLTE LUNE</b>\n\n"
            "Giove e Saturno nel Sistema Solare. "
            "Le lune extrasolari quasi non esistono nell'archivio: non ne fabbrico.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [_tarot_btn("🟠 Giove", "w:p:jupiter"), _tarot_btn("💍 Saturno", "w:p:saturn")],
                    [_tarot_btn("🌑 Catalogo lune", "home:lune")],
                    [_tarot_btn("🌍 Esplora", "md:hub")],
                    nav_row(),
                ]
            ),
        )
        return
    if action == "f" and extra in FILTERS:
        await query.answer("Archivio NASA…")
        await send_mondi_filter(update, context, extra)
        return
    if action == "o":
        try:
            idx = int(extra)
        except ValueError:
            await query.answer()
            return
        rows = context.user_data.get(MONDI_LIST_KEY)
        if not isinstance(rows, list) or not (0 <= idx < len(rows)):
            await query.answer("Lista scaduta")
            await show_mondi_hub(update, context)
            return
        await query.answer()
        await send_mondi_world(update, context, rows[idx])
        return
    if action == "sysf" and extra:
        await query.answer("Archivio…")
        await send_systems_kind(update, context, extra)
        return
    if action == "sysr":
        await query.answer("Archivio…")
        client = _http_client(context)
        card = await random_system(client)
        if card is None:
            await reply_offline(update, context)
            return
        planets = card.get("planets") if isinstance(card.get("planets"), list) else []
        context.user_data[MONDI_LIST_KEY] = planets
        await reply_html(
            update,
            context,
            format_system_tree(card),
            reply_markup=mondi_list_keyboard(min(len(planets), 8), back="md:sys") if planets else sistemi_keyboard(),
        )
        return
    if action == "syso":
        try:
            idx = int(extra)
        except ValueError:
            await query.answer()
            return
        rows = context.user_data.get(MONDI_SYS_KEY)
        if not isinstance(rows, list) or not (0 <= idx < len(rows)):
            await query.answer("Lista scaduta")
            await show_sistemi_menu(update, context)
            return
        host = str(rows[idx].get("hostname") or "")
        await query.answer(host)
        await send_system_card(update, context, host)
        return
    if action == "sy" and extra in FAMOUS_HOSTS:
        await query.answer(FAMOUS_HOSTS[extra])
        await send_system_card(update, context, FAMOUS_HOSTS[extra])
        return
    if action == "host":
        last = context.user_data.get(MONDI_LAST_KEY)
        host = ""
        if isinstance(last, dict):
            host = str(last.get("host") or "")
        if not host:
            await query.answer("Nessun sistema")
            await show_sistemi_menu(update, context)
            return
        await query.answer(host)
        await send_system_card(update, context, host)
        return
    if action == "save":
        last = context.user_data.get(MONDI_LAST_KEY)
        user = update.effective_user
        if not isinstance(last, dict) or not last.get("name") or user is None:
            await query.answer("Niente da salvare")
            return
        await world_save(user.id, last)
        await query.answer("Salvato")
        await reply_html(
            update,
            context,
            f"📌 Salvato <b>{e(last.get('name'))}</b> nella tua lista (max 20, file locale).",
            reply_markup=mondi_after_keyboard(has_system=bool(last.get("host")), saved=True),
        )
        return
    if action == "fav":
        user = update.effective_user
        if user is None:
            await query.answer()
            return
        favs = await world_list(user.id)
        context.user_data[MONDI_FAV_KEY] = favs
        await query.answer()
        if not favs:
            await reply_html(
                update,
                context,
                "📌 <b>I TUOI MONDI</b>\n\nAncora vuota. Apri una scheda e tocca Salva.",
                reply_markup=mondi_hub_keyboard(),
            )
            return
        lines = ["📌 <b>I TUOI MONDI</b>", "", "Solo tuoi, sul server. Tocca un numero.", ""]
        for idx, item in enumerate(favs, start=1):
            tag = "generato" if item.get("kind") == "imag" else "archivio"
            lines.append(f"{idx}. {e(item.get('name') or '—')} <i>({tag})</i>")
        await reply_html(update, context, "\n".join(lines), reply_markup=fav_list_keyboard(len(favs)))
        return
    if action == "fo":
        try:
            idx = int(extra)
        except ValueError:
            await query.answer()
            return
        favs = context.user_data.get(MONDI_FAV_KEY)
        if not isinstance(favs, list) or not (0 <= idx < len(favs)):
            await query.answer("Lista scaduta")
            return
        item = favs[idx]
        await query.answer()
        if item.get("kind") == "imag":
            await reply_html(
                update,
                context,
                format_imaginary(item if item.get("pl_rade") else {"name": item.get("name"), "kind": "imag", "note": "Salvato come nome. Rigenera per nuovi dadi.", "climate": "—", "stars": "—", "pl_rade": "—", "pl_eqt": "—", "pl_orbper": "—", "moons": "—"}),
                reply_markup=mondi_after_keyboard(),
            )
            return
        client = _http_client(context)
        row = await exoplanet_by_name(client, str(item.get("name") or ""))
        if row is None:
            await reply_offline(update, context)
            return
        await send_mondi_world(update, context, row)
        return
    if action == "wm" and extra:
        await query.answer()
        await send_mission_worlds(update, context, extra)
        return
    await query.answer()


async def send_eclissi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🌒 Cerco le prossime eclissi…")
    client = _http_client(context)
    now = datetime.now(timezone.utc)
    year = now.year
    data = await fetch_eclipses(client, year, year + 2)
    solar = next_of(data.get("solar") or [], now)
    lunar = next_of(data.get("lunar") or [], now)
    if solar is None and lunar is None:
        await reply_offline(update, context)
        return
    lines = ["🌒 <b>ECLISSI</b>", ""]
    if solar:
        when = parse_peak(solar)
        when_txt = when.astimezone(DEFAULT_TZ).strftime("%d/%m/%Y %H:%M") if when else str(solar.get("date"))
        count = countdown_it(when, now) if when else "—"
        lat, lon = solar.get("latitude"), solar.get("longitude")
        where = "picco calcolato (lat/lon Skytime)"
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            geo = await reverse_iss_place(client, float(lat), float(lon))
            where = geo.get("place") or where
            lines.append("☀️ <b>Prossima eclissi solare</b>")
            lines.append(f"{e(kind_it(str(solar.get('kind'))))} · {e(when_txt)} (Rome)")
            lines.append(f"📍 Picco vicino a: {e(where)}")
            lines.append(f"⏱️ Countdown: {e(count)}")
            lines.append("<i>Il picco è un punto, non l'intera fascia di visibilità.</i>")
        else:
            lines.append("☀️ <b>Prossima eclissi solare</b>")
            lines.append(f"{e(kind_it(str(solar.get('kind'))))} · {e(when_txt)}")
            lines.append(f"⏱️ Countdown: {e(count)}")
    else:
        lines.append("☀️ Nessuna eclissi solare nel range richiesto.")
    lines.append("")
    if lunar:
        when = parse_peak(lunar)
        when_txt = when.astimezone(DEFAULT_TZ).strftime("%d/%m/%Y %H:%M") if when else str(lunar.get("date"))
        count = countdown_it(when, now) if when else "—"
        lines.append("🌕 <b>Prossima eclissi lunare</b>")
        lines.append(f"{e(kind_it(str(lunar.get('kind'))))} · {e(when_txt)} (Rome)")
        lines.append(f"⏱️ Countdown: {e(count)}")
        lines.append("Visibile da gran parte del lato notturno della Terra al momento del picco.")
    else:
        lines.append("🌕 Nessuna eclissi lunare nel range richiesto.")
    lines.extend(["", "<i>Fonte live: calendario eclissi Skytime.</i>"])
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("🔭 Cielo Roma", "home:cielo")],
            nav_row(),
        ]
    )
    await reply_html(update, context, "\n".join(lines), reply_markup=kb)


async def send_neo_asteroids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "☄️ Interrogo NASA NeoWs…")
    client = _http_client(context)
    rows = await near_earth_asteroids(client, days=3)
    if not rows:
        await reply_offline(update, context)
        return
    await reply_html(update, context, format_neo(rows), reply_markup=asteroid_chooser_keyboard())


async def on_aster_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    if action == "neo":
        await query.answer("Asteroidi vicini…")
        await send_neo_asteroids(update, context)
        return
    if action == "natal":
        await query.answer("Effemeridi…")
        await show_natal_asteroids(update, context)
        return
    if action == "famous":
        await query.answer()
        await show_famous_asteroids(update, context)
        return
    await query.answer()


async def show_famous_asteroids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "🪨 <b>ASTEROIDI NOTI</b>\n\n"
        "Schede Wikipedia + misure Wikidata.\n"
        "Non è il catalogo JPL da 1,5 milioni di oggetti: è una selezione con voce pubblica.",
        reply_markup=famous_asteroids_keyboard(),
    )


async def show_quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _quiz_reset(context)
    user = update.effective_user
    board = await quiz_board(user.id) if user else {"points": 0, "quiz": {}}
    extra = f"\n\n🏆 I tuoi punti: <b>{int(board.get('points') or 0)}</b>"
    await reply_html(update, context, quiz_levels_text() + extra, reply_markup=quiz_menu_keyboard())


async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, level: str) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🧩 Costruisco la domanda dalle fonti live…")
    client = _http_client(context)
    quiz = await build_quiz(client, level)
    if quiz is None:
        await reply_html(
            update,
            context,
            "Non sono riuscito a costruire una domanda live. Riprova: le API devono rispondere.",
            reply_markup=quiz_menu_keyboard(),
        )
        return
    _quiz_state(context).update(quiz)
    labels = ("A", "B", "C", "D")
    lines = [f"🧩 <b>QUIZ · {e(level)}</b>", "", quiz["question"], ""]
    for idx, option in enumerate(quiz["options"]):
        lines.append(f"{labels[idx]}) {e(option)}")
    lines.extend(["", f"<i>Fonte: {e(quiz.get('source') or 'live')}</i>"])
    await reply_html(
        update,
        context,
        "\n".join(lines),
        reply_markup=quiz_options_keyboard(len(quiz["options"])),
    )


async def send_quiz_board(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return
    board = await quiz_board(user.id)
    quiz = board.get("quiz") if isinstance(board.get("quiz"), dict) else {}
    labels = {"easy": "🟢 Facile", "medium": "🟡 Medio", "hard": "🔴 Difficile", "expert": "☠️ Esperto"}
    lines = ["🏆 <b>LA TUA CLASSIFICA</b>", "", "Solo tua. Nessuna gara globale.", ""]
    for key, label in labels.items():
        bucket = quiz.get(key) if isinstance(quiz.get(key), dict) else {}
        ok = int(bucket.get("ok") or 0)
        tot = int(bucket.get("tot") or 0)
        lines.append(f"{label}  {ok}/{tot}")
    lines.extend(["", f"Punti: <b>{int(board.get('points') or 0)}</b>"])
    await reply_html(update, context, "\n".join(lines), reply_markup=quiz_menu_keyboard())


async def on_quiz_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""
    if action == "go" and extra:
        await query.answer()
        await send_quiz_question(update, context, extra)
        return
    if action == "board":
        await query.answer()
        await send_quiz_board(update, context)
        return
    if action == "ans":
        state = _quiz_state(context)
        options = state.get("options")
        if not isinstance(options, list) or state.get("correct") is None:
            await query.answer("Domanda scaduta")
            await show_quiz_menu(update, context)
            return
        try:
            chosen = int(extra)
        except ValueError:
            await query.answer()
            return
        correct = int(state["correct"])
        ok = chosen == correct
        user = update.effective_user
        if user:
            await quiz_record(user.id, str(state.get("level") or "easy"), ok=ok)
        await query.answer("Giusto!" if ok else "Sbagliato")
        mark = "✅ Giusto." if ok else f"❌ Era {options[correct]}."
        text = (
            f"🧩 <b>QUIZ</b>\n\n{mark}\n"
            f"Fonte: {e(state.get('source') or 'live')}\n\n"
            "Un'altra, o la classifica?"
        )
        _quiz_reset(context)
        await reply_html(update, context, text, reply_markup=quiz_menu_keyboard())
        return
    await query.answer()


async def send_esopianeta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🪐 Pesco un esopianeta dall'archivio NASA…")
    client = _http_client(context)
    row = await random_exoplanet(client)
    if row is None:
        await reply_offline(update, context)
        return
    await reply_html(update, context, format_exoplanet(row), reply_markup=exo_keyboard())


async def send_abitabile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🌍 Filtro i candidati in zona abitabile…")
    client = _http_client(context)
    rows = await habitable_candidates(client, limit=8)
    if not rows:
        await reply_offline(update, context)
        return
    await reply_html(update, context, format_habitable(rows), reply_markup=exo_keyboard())


async def show_specchio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = random.choice(MIRROR_QUESTIONS)
    state = _mirror_state(context)
    state.clear()
    state["step"] = "ask"
    state["question"] = question
    await reply_html(
        update,
        context,
        "🪞 <b>SPECCHIO</b>\n\n"
        f"<b>{e(question)}</b>\n\n"
        "Rispondi in un messaggio. Poi ti rimando una riflessione.\n"
        "<i>Pratica simbolica, non un oracolo e non un dato astronomico.</i>",
        reply_markup=InlineKeyboardMarkup([nav_row()]),
    )


async def receive_mirror_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> None:
    state = _mirror_state(context)
    question = str(state.get("question") or "")
    _mirror_reset(context)
    words = len(text.split())
    reflection = (
        "Hai messo in parole qualcosa che prima stava solo dentro.\n"
        f"La domanda era: <i>{e(question)}</i>\n\n"
        f"La tua risposta tiene insieme {words} parole. "
        "Rileggi. Cosa resta se togli la prima frase?\n\n"
        "<i>Non è una predizione. È uno specchio.</i>"
    )
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("🪞 Un'altra domanda", "home:specchio")],
            nav_row(),
        ]
    )
    await reply_html(update, context, "🪞 <b>SPECCHIO</b>\n\n" + reflection, reply_markup=kb)
    await delete_user_command(update)


async def send_rituale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    client = _http_client(context)
    try:
        moon = await api_moon_observatory(client)
        phase = str(moon.get("moon_phase") or "")
    except StelleOfflineError:
        phase = ""
    title, verb, body = ritual_for_phase(phase)
    label = moon_phase_label(phase) if phase else "fase non arrivata"
    text = (
        f"🌙 <b>RITUALE · {e(title)}</b>\n\n"
        f"Fase live: <b>{e(label)}</b>\n"
        f"Pratica: <b>{e(verb)}</b>\n\n"
        f"{e(body)}\n\n"
        "<i>È un gesto simbolico, non un effetto scientificamente dimostrato.</i>"
    )
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("🌙 Luna", "ora:lunar"), _tarot_btn("🌌 Interroga", "loc:go:skyq")],
            nav_row(),
        ]
    )
    await reply_html(update, context, text, reply_markup=kb)


async def send_random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🎲 Pesco nel sacco…")
    client = _http_client(context)
    kind = random.choice(("object", "planet", "mission", "moon", "exo"))
    discover = None
    if kind == "planet":
        item = random.choice(PLANETS)
        body = f"🪐 Pianeta\n\n{item['emoji']} <b>{e(item['it'])}</b>"
        discover = f"w:p:{item['id']}"
    elif kind == "mission":
        from services.catalog import MISSIONS

        item = random.choice(MISSIONS)
        body = f"🚀 Missione\n\n{item['emoji']} <b>{e(item['it'])}</b>"
        discover = f"w:n:{item['id']}"
    elif kind == "moon":
        try:
            story = await api_moon_story(client)
            title = str(story.get("content") or story.get("title") or "Curiosità lunare")
            title_it = await translate_to_italian(client, first_sentences(title, 1, 220))
        except Exception:
            title_it = "una nota lunare (fonte non disponibile)"
        body = f"🌙 Curiosità lunare\n\n<b>{e(title_it)}</b>"
        discover = "home:luna"
    elif kind == "exo":
        row = await random_exoplanet(client)
        if row and row.get("pl_name"):
            body = f"🪐 Esopianeta\n\n<b>{e(row['pl_name'])}</b>\nStella {e(row.get('hostname') or '—')}"
            discover = "home:esopianeta"
        else:
            body = "🪐 Esopianeta\n\nArchivio non disponibile."
    else:
        from services.catalog import RANDOM_OBJECTS

        item = random.choice(RANDOM_OBJECTS)
        body = f"🌌 Oggetto astronomico\n\n{item['emoji']} <b>{e(item['it'])}</b>"
        discover = f"w:r:{item['id']}"
    text = f"🎲 <b>OGGI HAI TROVATO…</b>\n\n{body}\n\n<i>Pesca dal catalogo ASTRO. Scopri apre la scheda.</i>"
    await reply_html(update, context, text, reply_markup=random_after_keyboard(discover))


async def send_missione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(DEFAULT_TZ)
    mission = daily_mission(now)
    user = update.effective_user
    done_id = await mission_is_done(user.id, now.date().isoformat()) if user else None
    done = done_id == mission.get("id")
    stars = "⭐" * int(mission.get("diff") or 1)
    if done:
        text = (
            "🏆 <b>MISSIONE COMPLETATA!</b>\n\n"
            f"{e(mission.get('title'))}\n"
            f"🔭 Difficoltà: {stars}\n"
            "Torna domani per la prossima."
        )
    else:
        text = (
            "🚀 <b>MISSIONE DEL GIORNO</b>\n\n"
            f"{e(mission.get('title'))}\n\n"
            f"🔭 Difficoltà: {stars}\n"
            f"⏱️ Tempo: {e(mission.get('mins'))} min\n\n"
            f"💡 {e(mission.get('hint'))}\n\n"
            "Quando l'hai fatto, tocca ✅ FATTO."
        )
    await reply_html(update, context, text, reply_markup=mission_keyboard(done=done))


async def on_miss_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    _remember_from_callback(update, context)
    user = update.effective_user
    if user is None:
        await query.answer()
        return
    now = datetime.now(DEFAULT_TZ)
    mission = daily_mission(now)
    await mission_done(user.id, now.date().isoformat(), str(mission.get("id")))
    await query.answer("Fatto.")
    await send_missione(update, context)


async def cmd_pianeta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:pianeta")
    await show_pianeta_menu(update, context)
    await delete_user_command(update)


async def cmd_lune(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:lune")
    await show_lune_menu(update, context)
    await delete_user_command(update)


async def cmd_sistema(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:sistema")
    await show_sistema_chooser(update, context)
    await delete_user_command(update)


async def cmd_buchineri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:buchineri")
    await show_buchineri_menu(update, context)
    await delete_user_command(update)


async def cmd_galassia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:galassia")
    await show_galassia_menu(update, context)
    await delete_user_command(update)


async def cmd_eclissi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:eclissi")
    await send_eclissi(update, context)
    await delete_user_command(update)


async def cmd_missioni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:missioni")
    await show_missioni_menu(update, context)
    await delete_user_command(update)


async def cmd_astronauta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:astronauta")
    await show_astronauta_menu(update, context)
    await delete_user_command(update)


async def cmd_satelliti(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:satelliti")
    await show_satelliti_menu(update, context)
    await delete_user_command(update)


async def cmd_sonde(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:sonde")
    await show_sonde_menu(update, context)
    await delete_user_command(update)


async def cmd_impara(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:impara")
    await show_impara_menu(update, context)
    await delete_user_command(update)


async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:quiz")
    await show_quiz_menu(update, context)
    await delete_user_command(update)


async def cmd_esopianeta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:esopianeta")
    await show_esopianeta_menu(update, context)
    await delete_user_command(update)


async def cmd_costellazioni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:costellazioni")
    await show_costellazioni_menu(update, context)
    await delete_user_command(update)


async def cmd_nani(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:nani")
    await show_nani_menu(update, context)
    await delete_user_command(update)


async def cmd_comete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:comete")
    await show_comete_menu(update, context)
    await delete_user_command(update)


async def cmd_profondo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:profondo")
    await show_profondo_menu(update, context)
    await delete_user_command(update)


async def cmd_mondi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "md:hub")
    await show_mondi_hub(update, context)
    await delete_user_command(update)


async def cmd_cosmo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "md:cosmo")
    await show_cosmo(update, context)
    await delete_user_command(update)


async def cmd_sistemi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "md:sys")
    await show_sistemi_menu(update, context)
    await delete_user_command(update)


async def cmd_abitabile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:abitabile")
    await send_abitabile(update, context)
    await delete_user_command(update)


async def cmd_vita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:vita")
    await show_vita_menu(update, context)
    await delete_user_command(update)


async def cmd_specchio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:specchio")
    await show_specchio(update, context)
    await delete_user_command(update)


async def cmd_rituale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:rituale")
    await send_rituale(update, context)
    await delete_user_command(update)


async def cmd_random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:random")
    await send_random(update, context)
    await delete_user_command(update)


async def cmd_missione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:missione")
    await send_missione(update, context)
    await delete_user_command(update)


async def send_rune_surprise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    drawn = draw_runes(1)
    rune = drawn[0]
    orient = "capovolta" if rune["orientation"] == "reversed" else "diritta"
    text = (
        "🔮 <b>L'ORACOLO HA SCELTO · RUNE</b>\n"
        f"{rune['glyph']} <b>{e(rune['name'])}</b> · {e(orient)}\n\n"
        f"{e(first_sentences(rune['meaning'], 2, 240))}\n\n"
        f"✨ <b>IN PRATICA</b>\n{e(rune_closer(drawn))}"
    )
    await reply_html(
        update,
        context,
        text,
        reply_markup=oracle_surprise_after_keyboard("🪶 Rituale", "home:rune"),
    )


async def send_oracle_surprise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pick = surprise_oracle()
    await send_typing(update)
    await deliver_text(update, context, "🔮 Lascio scegliere all'oracolo…")
    if pick == "tarot":
        state = _tarot_state(context)
        state.clear()
        state["spread"] = "day"
        await send_tarot_draw(update, context)
        return
    if pick == "iching":
        state = _iching_state(context)
        state.clear()
        state["question"] = "Cosa serve comprendere in questo momento?"
        state["animate"] = False
        await send_iching_cast(update, context)
        return
    if pick == "rune":
        await send_rune_surprise(update, context)
        return
    if pick == "leno":
        _leno_state(context).pop("question", None)
        await send_lenormand_draw(update, context, "1")
        return
    if pick == "yes":
        await send_yesno(update, context)
        return
    await send_stone_oracle(update, context)


async def show_oracoli_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(update, context, oracoli_text(), reply_markup=oracoli_keyboard())


async def cmd_oracoli(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:oracoli")
    await show_oracoli_hub(update, context)
    await delete_user_command(update)


async def show_lenormand_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _leno_state(context)
    state["step"] = "pick"
    phrase = str(state.get("question") or "").strip()
    extra = f"\n\nHai detto: <i>«{e(phrase)}»</i>" if phrase else ""
    await reply_html(
        update,
        context,
        "🌿 <b>LENORMAND</b>\n"
        "<i>36 sibille. Una alla volta. Non serve una domanda.</i>\n\n"
        "1, 3, 5 o 9 carte. Alla fine: il quadro e l'esito."
        f"{extra}",
        reply_markup=lenormand_menu_keyboard(),
    )


async def cmd_sibille(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:sibille")
    await show_lenormand_menu(update, context)
    await delete_user_command(update)


async def show_leno_ready(update: Update, context: ContextTypes.DEFAULT_TYPE, n: str) -> None:
    meta = LENORMAND_SPREADS.get(n)
    if meta is None:
        await show_lenormand_menu(update, context)
        return
    state = _leno_state(context)
    state["n"] = n
    state["step"] = "ready"
    phrase = str(state.get("question") or _lettura_state(context).get("question") or "").strip()
    if phrase:
        state["question"] = phrase
    text = (
        f"🌿 <b>{e(meta['title'])}</b>\n"
        f"<i>{int(meta['count'])} carte, una alla volta.</i>"
    )
    if phrase:
        text += f"\n\nHai detto: <i>«{e(phrase)}»</i>"
    await reply_html(update, context, text, reply_markup=lenormand_ready_keyboard())


async def show_leno_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _leno_state(context)["step"] = "ask"
    await reply_html(
        update,
        context,
        "🌿 <b>Una frase alle sibille</b>\n"
        "<i>Non è obbligatoria.</i>\n\n"
        "Se vuoi, scrivi una riga. Poi mescoliamo lo stesso.",
        reply_markup=InlineKeyboardMarkup(
            [[_tarot_btn("🌿 Meglio senza", "leno:mix")], nav_row()]
        ),
    )


async def start_leno_mix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _leno_state(context)
    n = str(state.get("n") or "")
    meta = LENORMAND_SPREADS.get(n)
    if meta is None:
        await show_lenormand_menu(update, context)
        return
    await send_typing(update)
    await deliver_text(update, context, "🌿 Mescolando le sibille…")
    await asyncio.sleep(0.35)
    drawn = draw_lenormand(int(meta["count"]))
    state["drawn"] = drawn
    state["index"] = 0
    state["step"] = "reveal"
    await deliver_text(update, context, "🌿 Taglio…")
    await asyncio.sleep(0.25)
    await reveal_leno(update, context)


async def reveal_leno(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _leno_state(context)
    n = str(state.get("n") or "")
    meta = LENORMAND_SPREADS.get(n)
    drawn = state.get("drawn") if isinstance(state.get("drawn"), list) else []
    idx = int(state.get("index") or 0)
    if not meta or not drawn or idx >= len(drawn):
        await show_leno_quadro(update, context)
        return
    card = drawn[idx]
    positions = tuple(meta["positions"])
    hints = LENO_HINTS.get(n) or ()
    pos = positions[idx] if idx < len(positions) else f"Carta {idx + 1}"
    hint = hints[idx] if idx < len(hints) else ""
    left = len(drawn) - idx - 1
    text = (
        f"🌿 <b>{e(pos)}</b>  ·  {idx + 1}/{len(drawn)}\n"
        f"{card['emoji']} <b>{e(card['it'])}</b>\n"
        f"<i>{e(card['keys'])}</i>\n\n"
        f"{e(hint)}\n\n"
        f"{e(first_sentences(card['meaning'], 2, 240))}"
    )
    if left:
        text += f"\n\n<i>Restano {left} carte.</i>"
    else:
        text += "\n\n<i>Ultima carta. Poi il quadro: da dove parti, dove arrivi.</i>"
    state["index"] = idx + 1
    await reply_html(update, context, text, reply_markup=lenormand_next_keyboard(last=left == 0))


async def show_leno_quadro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _leno_state(context)
    n = str(state.get("n") or "")
    meta = LENORMAND_SPREADS.get(n)
    drawn = state.get("drawn") if isinstance(state.get("drawn"), list) else []
    if not meta or not drawn:
        await show_lenormand_menu(update, context)
        return
    phrase = str(state.get("question") or "").strip()
    positions = tuple(meta["positions"])
    lines = [
        f"🌿 <b>{e(meta['title'])}</b>",
        "<i>I nomi, poi cosa dicono insieme.</i>",
        "",
    ]
    if phrase:
        lines.append(f"Hai detto: <i>«{e(phrase)}»</i>")
        lines.append("")
    for idx, card in enumerate(drawn):
        pos = positions[idx] if idx < len(positions) else f"Carta {idx + 1}"
        lines.append(f"{idx + 1}. {e(pos)} — {card['emoji']} {e(card['it'])}")
    pairs = pair_lines(drawn, limit=2)
    if pairs:
        lines.extend(["", "🔗 <b>VICINE</b>", *pairs])
    lines.extend(
        [
            "",
            "✨ <b>IN PRATICA</b>",
            e(lenormand_closer(drawn)),
            "",
            "<i>Petit Lenormand. Specchio, non verdetto.</i>",
        ]
    )
    state["step"] = "done"
    await reply_html(update, context, "\n".join(lines), reply_markup=lenormand_after_keyboard())


async def send_lenormand_draw(update: Update, context: ContextTypes.DEFAULT_TYPE, n: str) -> None:
    await show_leno_ready(update, context, n)


async def send_deck_card(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    cards = draw_deck(kind, 1)
    meta = DECK_META.get(kind)
    if not cards or meta is None:
        await show_oracoli_hub(update, context)
        return
    emoji, title, hint = meta
    body = format_simple_card(cards[0], kind=kind)
    text = (
        f"{emoji} <b>{e(title)}</b>\n"
        f"<i>{e(hint)}</i>\n\n"
        f"{body}\n\n"
        "<i>Mazzo originale COSMOBOT. Lettura simbolica, non previsione certa.</i>"
    )
    await reply_html(update, context, text, reply_markup=deck_after_keyboard(kind))


async def send_lunar_oracle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_typing(update)
    client = _http_client(context)
    try:
        moon = await api_moon_observatory(client)
        phase = str(moon.get("moon_phase") or "")
    except StelleOfflineError:
        phase = ""
    pack = LUNAR_ORACLE[lunar_key(phase)]
    label = moon_phase_label(phase) if phase else "fase non arrivata"
    extra = draw_deck("arch", 1)
    extra_bit = ""
    if extra:
        card = extra[0]
        extra_bit = f"\n\n🧿 Carta del ciclo: {card['emoji']} <b>{e(card['it'])}</b>\n{e(card['message'])}"
    text = (
        f"🌙 <b>ORACOLO LUNARE</b>\n\n"
        f"Fase live: <b>{e(label)}</b>\n"
        f"{pack['title']} → <b>{e(pack['verb'])}</b>\n\n"
        f"🔮 {e(pack['message'])}\n\n"
        f"💭 {e(pack['question'])}"
        f"{extra_bit}\n\n"
        "<i>La fase è astronomica (API). Il messaggio è simbolico, non un effetto dimostrato.</i>"
    )
    await reply_html(update, context, text, reply_markup=deck_after_keyboard("lunar"))


def _yesno_pratica(lean: str) -> str:
    if lean == "yes":
        return (
            "L'inclinazione è sì. Non è un permesso di chiudere gli occhi: "
            "è un via libera a quello che già vedi, se ci stai."
        )
    if lean == "no":
        return (
            "L'inclinazione è no. Non è una condanna: è un invito a non forzare, "
            "o a riformulare la domanda."
        )
    return (
        "Non è ancora sì o no. Aspetta un segno più chiaro, "
        "o cambia la domanda: l'oracolo qui resta in bilico."
    )


async def send_yesno(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str | None = None) -> None:
    method = method or random.choice(("tarot", "rune", "iching"))
    await send_typing(update)
    result: dict[str, str]
    if method == "tarot":
        client = _http_client(context)
        try:
            cards = await api_tarot_draw(client, count=1, include_minor=False)
            name_en = str((cards[0] or {}).get("name") or "Carta")
            name_it = await translate_to_italian(client, name_en)
        except StelleOfflineError:
            await reply_offline(update, context)
            return
        reversed_card = bool(random.choice((False, True)))
        result = yesno_from_tarot(reversed_card, name_it)
    elif method == "iching":
        result = yesno_from_iching_lines(cast_iching_lines())
    else:
        result = yesno_from_rune()
    icon = {"yes": "✅", "no": "❌", "maybe": "〰️"}.get(result["lean"], "🔮")
    text = (
        "🪞 <b>DOMANDA SÌ / NO</b>\n\n"
        f"Strumento: {e(result['method'])}\n"
        f"{icon} <b>{e(result['label'])}</b>\n\n"
        f"{e(result['detail'])}\n\n"
        "✨ <b>IN PRATICA</b>\n"
        f"{e(_yesno_pratica(result.get('lean') or ''))}\n\n"
        "<i>Non è una previsione certa. È una lettura simbolica: "
        "un'inclinazione, non un verdetto.</i>"
    )
    await reply_html(update, context, text, reply_markup=yesno_keyboard())


async def show_oracle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = random.choice(ORACLE_QUESTIONS)
    state = _oq_state(context)
    state.clear()
    state["step"] = "idle"
    state["question"] = question
    await reply_html(
        update,
        context,
        "🕯️ <b>DOMANDA PER TE</b>\n\n"
        f"<b>{e(question)}</b>\n\n"
        "Non usa carte. Se vuoi, tocca 💭 e rispondi in un messaggio.",
        reply_markup=oracle_question_keyboard(),
    )


async def receive_oq_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    state = _oq_state(context)
    question = str(state.get("question") or "")
    _oq_reset(context)
    words = len(text.split())
    body = (
        "🕯️ <b>ORACOLO DELLE DOMANDE</b>\n\n"
        f"La domanda era: <i>{e(question)}</i>\n\n"
        f"Hai risposto in {words} parole. Rileggi. "
        "Cosa resta se togli la giustificazione?\n\n"
        "<i>Non è un oracolo che predice. È una domanda che ti tiene fermo.</i>"
    )
    kb = InlineKeyboardMarkup(
        [
            [_tarot_btn("🕯️ Un'altra", "ora:askq")],
            nav_row(),
        ]
    )
    await reply_html(update, context, body, reply_markup=kb)
    await delete_user_command(update)


async def show_lettura_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _lettura_state(context)
    state.clear()
    state["step"] = "ask"
    await reply_html(update, context, lettura_text(), reply_markup=InlineKeyboardMarkup([nav_row()]))


async def show_lettura_methods(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _lettura_state(context)
    question = str(state.get("question") or "").strip()
    state["step"] = "pick"
    await reply_html(
        update,
        context,
        "🔮 <b>SCEGLI IL METODO</b>\n\n"
        f"<i>«{e(question)}»</i>\n\n"
        "🃏 Tarocchi · ☯️ I Ching · 🪶 Rune · 🌿 Lenormand\n"
        "🔮 Fai scegliere all'oracolo — scelgo io lo strumento e avvio il rituale.",
        reply_markup=lettura_method_keyboard(),
    )


async def start_lettura_method(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str) -> None:
    question = str(_lettura_state(context).get("question") or "").strip()
    if not question:
        await show_lettura_ask(update, context)
        return
    if method == "surprise":
        method = random.choice(("tarot", "iching", "rune", "leno"))
    if method == "tarot":
        await show_tarot_ready(update, context, "three", phrase=question)
        return
    if method == "iching":
        state = _iching_state(context)
        state.clear()
        state["question"] = question
        await show_iching_confirm(update, context)
        return
    if method == "rune":
        state = _rune_state(context)
        state.clear()
        state["question"] = question
        state["step"] = "draw"
        await reply_html(
            update,
            context,
            f"🪶 <b>La tua domanda</b>\n\n<i>«{e(question)}»</i>\n\nQuante rune vuoi estrarre?",
            reply_markup=rune_draw_keyboard(),
        )
        return
    if method == "leno":
        state = _leno_state(context)
        state.clear()
        state["question"] = question
        await show_lenormand_menu(update, context)
        return
    await show_lettura_methods(update, context)


async def cmd_lettura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "home:lettura")
    raw = " ".join(context.args).strip() if context.args else ""
    if raw:
        _lettura_state(context)["question"] = clip_text(raw, 400)
        await show_lettura_methods(update, context)
    else:
        await show_lettura_ask(update, context)
    await delete_user_command(update)


async def on_ora_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    action = query.data.split(":")[1] if ":" in query.data else ""
    await query.answer()
    if action == "mazzi":
        await reply_html(
            update,
            context,
            "🧿 <b>MAZZI</b>\n"
            "<i>Carte nostre, lettura simbolica. Non sono astronomia.</i>",
            reply_markup=oracoli_mazzi_keyboard(),
        )
        return
    if action == "arch":
        await send_deck_card(update, context, "arch")
        return
    if action == "anim":
        await send_deck_card(update, context, "anim")
        return
    if action == "symb":
        await send_deck_card(update, context, "symb")
        return
    if action == "elem":
        await send_deck_card(update, context, "elem")
        return
    if action == "plan":
        await send_deck_card(update, context, "plan")
        return
    if action == "lunar":
        await send_lunar_oracle(update, context)
        return
    if action == "yes":
        await reply_html(
            update,
            context,
            "🪞 <b>DOMANDA SÌ / NO</b>\n\n"
            "Pensa alla domanda. Non serve scriverla.\n"
            "Pesco un tarocco, una runa o un I Ching e ti do un'inclinazione simbolica.\n"
            "Non è un verdetto.",
            reply_markup=yesno_keyboard(),
        )
        return
    if action == "askq":
        await show_oracle_question(update, context)
        return
    if action == "surprise":
        await send_oracle_surprise(update, context)
        return


async def on_leno_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""
    if extra in LENORMAND_SPREADS:
        await query.answer()
        await show_leno_ready(update, context, extra)
        return
    if action == "mix":
        await query.answer("Mescolando…")
        await start_leno_mix(update, context)
        return
    if action == "next":
        await query.answer()
        await reveal_leno(update, context)
        return
    if action == "board":
        await query.answer()
        await show_leno_quadro(update, context)
        return
    if action == "phrase":
        await query.answer()
        await show_leno_phrase(update, context)
        return
    await query.answer()
    await show_lenormand_menu(update, context)


async def on_yn_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    extra = query.data.split(":")[1] if ":" in query.data else "go"
    await query.answer("Estraggo…")
    method = None if extra == "go" else extra
    await send_yesno(update, context, method)


async def on_oq_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    _remember_from_callback(update, context)
    await query.answer()
    state = _oq_state(context)
    state["step"] = "ask"
    await reply_html(
        update,
        context,
        "🕯️ <b>Rispondi in un messaggio</b>\n\n"
        f"<i>{e(state.get('question') or '')}</i>",
    )


async def on_lett_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    extra = query.data.split(":")[1] if ":" in query.data else ""
    await query.answer()
    await start_lettura_method(update, context, extra)


async def cmd_sino(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:yes")
    await reply_html(
        update,
        context,
        "🪞 <b>DOMANDA SÌ / NO</b>\n\nPensa alla domanda. Poi estrai.",
        reply_markup=yesno_keyboard(),
    )
    await delete_user_command(update)


async def cmd_archetipi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:arch")
    await send_deck_card(update, context, "arch")
    await delete_user_command(update)


async def cmd_animali(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:anim")
    await send_deck_card(update, context, "anim")
    await delete_user_command(update)


async def cmd_simboli(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:symb")
    await send_deck_card(update, context, "symb")
    await delete_user_command(update)


async def cmd_elementi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:elem")
    await send_deck_card(update, context, "elem")
    await delete_user_command(update)


async def cmd_oracoloplanetario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:plan")
    await send_deck_card(update, context, "plan")
    await delete_user_command(update)


async def cmd_oracololunare(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:lunar")
    await send_lunar_oracle(update, context)
    await delete_user_command(update)


async def cmd_oracolodande(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "ora:askq")
    await show_oracle_question(update, context)
    await delete_user_command(update)


async def show_pietre_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(update, context, pietre_hub_text(), reply_markup=pietre_hub_keyboard())


async def send_stone_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE, sid: str) -> None:
    stone = stone_by_id(sid)
    if stone is None:
        await reply_html(update, context, "Questa pietra non è in catalogo.", reply_markup=pietre_hub_keyboard())
        return
    _stone_state(context)["last"] = sid
    user = update.effective_user
    if user:
        await stone_discover(user.id, sid)
    await reply_html(update, context, format_card(stone), reply_markup=pietre_after_keyboard(sid))


async def send_stone_list(update: Update, context: ContextTypes.DEFAULT_TYPE, rows: list, title: str, blurb: str) -> None:
    await reply_html(update, context, format_list(rows, title, blurb), reply_markup=pietre_list_keyboard(rows[:40]))


async def send_stone_oracle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(DEFAULT_TZ)
    stone = stone_of_day(now)
    _stone_state(context)["last"] = stone["id"]
    user = update.effective_user
    if user:
        await stone_discover(user.id, stone["id"])
    wiki_url = stone_wiki_url(stone)
    curiosity = stone_curiosity(stone)
    try:
        wiki = await wikipedia_summary(
            _http_client(context),
            str(stone.get("wiki_it") or stone.get("wiki") or stone.get("it") or ""),
        )
    except Exception:
        wiki = None
    if wiki:
        if wiki.get("extract"):
            curiosity = stone_curiosity(stone, str(wiki["extract"]))
        if wiki.get("url"):
            wiki_url = str(wiki["url"])
    day_label = now.strftime("%d/%m/%Y")
    text = format_daily_oracle_card(stone, day_label=day_label, curiosity=curiosity)
    await reply_html(update, context, text, reply_markup=pietre_oracle_keyboard(wiki_url))


async def send_stone_spread(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    rows = oracle_spread(kind)
    title = "Corpo · Mente · Spirito" if kind == "body" else "Passato · Presente · Direzione"
    lines = ["✨ <b>TRE PIETRE</b>", title, "", "<i>Lettura simbolica, non un verdetto.</i>", ""]
    for row in rows:
        stone = row["stone"]
        lines.append(
            f"🪨 <b>{e(row['label'])}</b> — {stone['emoji']} {e(stone['it'])}\n"
            f"<i>{e(stone['oracle_sym'])}</i> · {e(stone['oracle_q'])}"
        )
        lines.append("")
    _stone_state(context)["last"] = rows[1]["stone"]["id"]
    user = update.effective_user
    if user:
        for row in rows:
            await stone_discover(user.id, row["stone"]["id"])
    await reply_html(update, context, "\n".join(lines), reply_markup=pietre_oracle_keyboard())


async def send_stone_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    if kind == "guess":
        quiz = build_guess()
    elif kind == "tf":
        quiz = build_tf()
    elif kind == "quiz":
        quiz = build_guess()
        _stone_state(context)["qleft"] = 9
        _stone_state(context)["qok"] = 0
    else:
        quiz = build_field_quiz(kind)
    if not quiz:
        await reply_html(update, context, "Non ho costruito la domanda.", reply_markup=pietre_games_keyboard())
        return
    _stone_state(context)["quiz"] = quiz
    if kind == "guess":
        prompt = "🧠 <b>INDOVINA LA PIETRA</b>\n\n" + "\n".join(f"• {e(c)}" for c in quiz["clues"])
    elif kind == "tf":
        prompt = "🪨 <b>VERO O FALSO</b>\n\n" + e(quiz.get("prompt") or "")
    else:
        prompt = "🧩 <b>QUIZ</b>\n\n" + str(quiz.get("prompt") or "🧠 <b>INDOVINA LA PIETRA</b>\n\n" + "\n".join(f"• {e(c)}" for c in quiz.get("clues") or []))
    labels = ("A", "B", "C", "D")
    opts = quiz["options"]
    lines = [prompt, ""]
    for i, opt in enumerate(opts):
        lines.append(f"{labels[i]}) {e(str(opt))}")
    await reply_html(update, context, "\n".join(lines), reply_markup=pietre_quiz_keyboard(len(opts)))


async def show_pietre_lab(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str | None = None) -> None:
    state = _stone_state(context)
    if step is None:
        state["lab"] = {}
        step = "color"
    state["lab_step"] = step
    state["photo"] = True
    prompts = {
        "color": (
            "🔬 <b>IDENTIFICA LA PIETRA</b>\n"
            "<i>Restringo il catalogo dal colore o da una foto. Non è un laboratorio.</i>\n\n"
            "Che colore è, soprattutto?\n"
            "Oppure una foto: pietra al centro, su un tavolo di colore uniforme."
        ),
        "hard": (
            "🔬 <b>DUREZZA</b>\n"
            "<i>Unghia, vetro, acciaio: una scala, non un verdetto.</i>\n\n"
            "Quanto è dura? (unghia ~2, vetro ~5,5, acciaio ~6–7, corindone 9)"
        ),
        "trans": "🔬 <b>TRASPARENZA</b>\n<i>La luce passa, o si ferma.</i>\n\nLascia passare la luce?",
        "metal": "🔬 <b>LUCENTEZZA</b>\n<i>Brilla come metallo, o no.</i>\n\nHa lucentezza metallica?",
        "mag": "🔬 <b>MAGNETISMO</b>\n<i>Poche pietre attirano la calamita.</i>\n\nAttira una calamita?",
        "fizz": (
            "🔬 <b>ACIDO</b>\n"
            "<i>Come un calcare, se reagisce. Non provare acidi su gemme.</i>\n\n"
            "Fa effervescenza con acido?"
        ),
    }
    await reply_html(
        update,
        context,
        prompts.get(step, prompts["color"])
        + "\n\n<i>Restringo il catalogo. Non sostituisce un'analisi di laboratorio.</i>",
        reply_markup=pietre_lab_keyboard(step),
    )


async def finish_pietre_lab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answers = _stone_state(context).get("lab") if isinstance(_stone_state(context).get("lab"), dict) else {}
    rows = filter_lab(answers)
    blurb = (
        "Possibili corrispondenze nel catalogo COSMOBOT. "
        "Una foto o un quiz non sostituiscono durezza, striscio e densità misurati."
    )
    await send_stone_list(update, context, rows, "🔬 <b>POSSIBILI MINERALI</b>", blurb)


async def show_pietre_bag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    known = set(await stone_ids(user.id) if user else [])
    total = len(STONES)
    shown = [s for s in STONES if s["id"] in known]
    lines = ["🎒 <b>LA MIA COLLEZIONE</b>", "", f"💎 {len(shown)} / {total} scoperte", ""]
    if not shown:
        lines.append("Ancora vuota. 🎲 Casuale o 🔮 del giorno scoprono una pietra.")
        await reply_html(update, context, "\n".join(lines), reply_markup=pietre_hub_keyboard())
        return
    for stone in shown:
        rem, rname = RARITY[stone["rarity"]]
        lines.append(f"{stone['emoji']} {stone['it']}  {rem} {rname}")
    missing = total - len(shown)
    if missing:
        lines.append(f"\n… e {missing} ancora da scoprire.")
    await reply_html(update, context, "\n".join(lines), reply_markup=pietre_list_keyboard(shown[:40]))


async def dispatch_pietre(update: Update, context: ContextTypes.DEFAULT_TYPE, token: str) -> None:
    parts = token.split(":")
    action = parts[1] if len(parts) > 1 else "hub"
    extra = parts[2] if len(parts) > 2 else ""
    extra2 = parts[3] if len(parts) > 3 else ""
    if action != "find":
        _stone_state(context)["search"] = False
    if action not in {"photo", "lab"}:
        _stone_state(context)["photo"] = False

    if action in {"hub", ""}:
        await show_pietre_hub(update, context)
        return
    if action == "day":
        stone = stone_of_day(datetime.now(DEFAULT_TZ))
        await send_stone_sheet(update, context, stone["id"])
        return
    if action == "rand":
        user = update.effective_user
        known = await stone_ids(user.id) if user else []
        stone = random_stone(prefer_undiscovered=known)
        await send_stone_sheet(update, context, stone["id"])
        return
    if action == "find":
        _stone_state(context)["search"] = True
        await reply_html(
            update,
            context,
            "🔍 <b>CERCA UNA PIETRA</b>\n\n"
            "Scrivi il nome, la formula o un colore.\n"
            "Esempio: <code>ametista</code>, <code>SiO2</code>, <code>malachite</code>.",
            reply_markup=InlineKeyboardMarkup([nav_row()]),
        )
        return
    if action == "exp":
        await reply_html(update, context, "🧭 <b>ESPLORA</b>\n\nTipo, colore, ambiente, rarità di catalogo.", reply_markup=pietre_explore_keyboard())
        return
    if action == "k" and extra in CATS:
        em, name = CATS[extra]
        await send_stone_list(update, context, by_cat(extra), f"{em} <b>{name.upper()}</b>", "Schede del catalogo, non un dump Mindat.")
        return
    if action == "cols":
        await reply_html(update, context, "🌈 <b>CERCA PER COLORE</b>\n\nIl colore in natura varia: è una porta, non una diagnosi.", reply_markup=pietre_colors_keyboard())
        return
    if action == "col" and extra in COLORS:
        em, name = COLORS[extra]
        await send_stone_list(update, context, by_color(extra), f"{em} <b>{name.upper()}</b>", "Pietre del catalogo con questo colore tipico.")
        return
    if action == "envs":
        await reply_html(update, context, "🧭 <b>AMBIENTI</b>\n\nOgni ambiente → pietre tipiche del catalogo.", reply_markup=pietre_envs_keyboard())
        return
    if action == "en" and extra in ENVS:
        em, name = ENVS[extra]
        await send_stone_list(update, context, by_env(extra), f"{em} <b>{name.upper()}</b>", "Non è una mappa di cave da scavo: sono ambienti geologici noti.")
        return
    if action == "rars":
        await reply_html(update, context, "🏆 <b>RARITÀ DI CATALOGO</b>\n\nNon è un prezzo. È quanto compare nel nostro universo Pietre.", reply_markup=pietre_rarity_keyboard())
        return
    if action == "rr" and extra in RARITY:
        em, name = RARITY[extra]
        await send_stone_list(update, context, by_rarity(extra), f"{em} <b>{name.upper()}</b>", "Rarità narrativa di catalogo, non quotazione.")
        return
    if action == "maps":
        await reply_html(
            update,
            context,
            "🌍 <b>DOVE SI TROVANO</b>\n\n"
            "Apri una scheda e tocca 🌍 Dove, oppure cerca un nome.\n"
            "Le località sono giacimenti noti, non un invito a scavare.",
            reply_markup=pietre_explore_keyboard(),
        )
        return
    if action == "forms":
        await reply_html(
            update,
            context,
            "⛏️ <b>COME SI FORMANO</b>\n\n"
            "🌋 Magmatico — dal fuso (basalto, olivina, granito)\n"
            "💧 Idrotermale — fluidi caldi (quarzo, ametista, fluorite)\n"
            "🔥 Metamorfico — pressione e temperatura (marmo, granato, cianite)\n"
            "🌊 Sedimentario / evaporitico — depositi (calcare, sale, gesso)\n"
            "☄️ Impatto / spazio — meteoriti e tettiti\n\n"
            "Apri una pietra e tocca ⛏️ Formazione per la timeline.",
            reply_markup=pietre_explore_keyboard(),
        )
        return
    if action == "enc":
        lines = ["📖 <b>ENCICLOPEDIA</b>", f"{len(STONES)} schede. Tocca una categoria.", ""]
        for key, (em, name) in CATS.items():
            lines.append(f"{em} {name} — {len(by_cat(key))}")
        await reply_html(update, context, "\n".join(lines), reply_markup=pietre_explore_keyboard())
        return
    if action == "val":
        await reply_html(
            update,
            context,
            "💰 <b>GEMME E VALORE</b>\n\n"
            "Per una gemma reale contano colore, purezza, taglio, caratura, trattamenti, provenienza.\n"
            "COSMOBOT non inventa un prezzo. Apri una gemma e tocca 💰 Valore.",
            reply_markup=pietre_list_keyboard(by_cat("gem")),
        )
        return
    if action == "myth":
        rows = [s for s in STONES if s.get("ancient")]
        await send_stone_list(
            update,
            context,
            rows,
            "🏺 <b>STORIA E MITO</b>",
            "Civiltà e folklore. Il simbolismo, nella scheda, sta sotto una riga a parte.",
        )
        return
    if action == "lab":
        await show_pietre_lab(update, context)
        return
    if action == "photo":
        _stone_state(context)["photo"] = True
        await reply_html(
            update,
            context,
            "📸 <b>FOTO</b>\n"
            "<i>Confronto colore e miniature Wikipedia. Cinque ipotesi, non un'analisi.</i>\n\n"
            "Mandami adesso la foto della pietra.\n"
            "Mettila <b>al centro</b>, su un <b>tavolo di colore uniforme</b> "
            "(un solo colore, senza venature, tovaglia a disegno o mani in mezzo).\n"
            "Ti do cinque ipotesi dal catalogo. Una foto <b>non</b> sostituisce "
            "durezza, striscio e densità.",
            reply_markup=InlineKeyboardMarkup([[_tarot_btn("🔬 Laboratorio", "pt:lab")], nav_row()]),
        )
        return
    if action == "ora":
        await send_stone_oracle(update, context)
        return
    if action in {"orx", "orcard", "o3t", "o3b"}:
        await send_stone_oracle(update, context)
        return
    if action == "bag":
        await show_pietre_bag(update, context)
        return
    if action == "mus":
        await reply_html(update, context, "🏛️ <b>MUSEO COSMOBOT</b>\n\nSale permanenti. Ogni sala è un filtro del catalogo.", reply_markup=pietre_museum_keyboard())
        return
    if action == "mr" and extra in MUSEUM:
        em, name = MUSEUM[extra]
        await send_stone_list(update, context, museum_room(extra), f"🏛️ <b>{name.upper()}</b>", "Sala del museo: stesse schede, altra porta.")
        return
    if action == "cosmo":
        await send_stone_list(
            update,
            context,
            by_cat("spc"),
            "☄️ <b>PIETRE DALLO SPAZIO</b>",
            "Meteoriti, vetri da impatto, frammenti lunari e marziani identificati. "
            "Si collega al cielo: origine extraterrestre o da impatto, non un oracolo.",
        )
        return
    if action == "game":
        await reply_html(update, context, "🧠 <b>GIOCHI</b>\n\nDomande costruite sul catalogo. Se sbagli, la scheda è lì.", reply_markup=pietre_games_keyboard())
        return
    if action == "g" and extra:
        await send_stone_quiz(update, context, "guess" if extra == "next" else extra)
        return
    if action == "cmp":
        await reply_html(update, context, "⚖️ <b>CONFRONTA</b>\n\nScegli la prima pietra.", reply_markup=pietre_list_keyboard(list(STONES)[:40], prefix="pt:c1:"))
        return
    if action == "c1" and extra:
        await reply_html(
            update,
            context,
            f"⚖️ Prima pietra: <b>{e((stone_by_id(extra) or {}).get('it') or extra)}</b>\nScegli la seconda.",
            reply_markup=pietre_list_keyboard([s for s in STONES if s["id"] != extra][:40], prefix=f"pt:c2:{extra}:"),
        )
        return
    if action == "c2" and extra and extra2:
        a, b = stone_by_id(extra), stone_by_id(extra2)
        if a and b:
            await reply_html(update, context, format_compare(a, b), reply_markup=InlineKeyboardMarkup([[_tarot_btn("⚖️ Altro confronto", "pt:cmp")], nav_row()]))
            return
    if action == "s" and extra:
        await send_stone_sheet(update, context, extra)
        return
    if action in {"sc", "sg", "sh", "ss", "sf", "sw", "sv"} and extra:
        stone = stone_by_id(extra)
        if stone:
            extract = None
            if action == "sc":
                try:
                    wiki = await wikipedia_summary(
                        _http_client(context),
                        str(stone.get("wiki_it") or stone.get("wiki") or ""),
                    )
                    if wiki and wiki.get("extract"):
                        extract = clip_text(str(wiki["extract"]), 700)
                except Exception:
                    extract = None
            await reply_html(
                update,
                context,
                format_section(stone, action, wiki_extract=extract),
                reply_markup=pietre_after_keyboard(extra),
                preview=bool(extract),
            )
            return
    await show_pietre_hub(update, context)


async def on_pt_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""
    extra2 = parts[3] if len(parts) > 3 else ""

    if action == "la":
        await query.answer()
        if query.message is not None:
            _remember_bot_msg(context, query.message.message_id, "text" if query.message.text else "photo")
        lab = _stone_state(context).setdefault("lab", {})
        if not isinstance(lab, dict):
            lab = {}
            _stone_state(context)["lab"] = lab
        kind, value = extra, extra2
        if kind == "c" and value:
            lab["color"] = value
            await show_pietre_lab(update, context, "hard")
            return
        if kind == "h" and value:
            lab["hard"] = value
            await show_pietre_lab(update, context, "trans")
            return
        if kind == "t":
            if value in {"yes", "no"}:
                lab["trans"] = value
            await show_pietre_lab(update, context, "metal")
            return
        if kind == "m":
            if value == "yes":
                lab["metal"] = True
            elif value == "no":
                lab["metal"] = False
            await show_pietre_lab(update, context, "mag")
            return
        if kind == "g":
            if value == "yes":
                lab["mag"] = True
            elif value == "no":
                lab["mag"] = False
            await show_pietre_lab(update, context, "fizz")
            return
        if kind == "f":
            if value == "yes":
                lab["fizz"] = True
            elif value == "no":
                lab["fizz"] = False
            await finish_pietre_lab(update, context)
            return
        await show_pietre_lab(update, context)
        return

    if action == "ga" and extra.isdigit():
        await query.answer()
        if query.message is not None:
            _remember_bot_msg(context, query.message.message_id, "text" if query.message.text else "photo")
        quiz = _stone_state(context).get("quiz")
        if not isinstance(quiz, dict):
            await send_stone_quiz(update, context, "guess")
            return
        idx = int(extra)
        ok = idx == int(quiz.get("answer") or 0)
        stone = stone_by_id(str(quiz.get("id") or ""))
        mark = "Esatto." if ok else "No."
        more = ""
        left = _stone_state(context).get("qleft")
        if isinstance(left, int) and left >= 0:
            if ok:
                _stone_state(context)["qok"] = int(_stone_state(context).get("qok") or 0) + 1
            if left > 0:
                _stone_state(context)["qleft"] = left - 1
                more = f"\nQuiz rapido: ancora {left} domande."
                await reply_html(
                    update,
                    context,
                    f"{'✅' if ok else '❌'} {mark}{more}",
                    reply_markup=InlineKeyboardMarkup([[_tarot_btn("➡️ Prossima", "pt:g:next")], nav_row()]),
                )
                return
            score = int(_stone_state(context).get("qok") or 0)
            _stone_state(context).pop("qleft", None)
            await reply_html(
                update,
                context,
                f"{'✅' if ok else '❌'} {mark}\n\n⚡ Quiz finito: <b>{score}/10</b>",
                reply_markup=pietre_games_keyboard(),
            )
            return
        text = f"{'✅' if ok else '❌'} <b>{mark}</b>"
        if stone:
            text += f"\n\n{stone['emoji']} {e(stone['it'])} · {e(stone['formula'])}"
        await reply_html(update, context, text, reply_markup=pietre_after_keyboard(stone["id"]) if stone else pietre_games_keyboard())
        return

    _remember_from_callback(update, context)
    await query.answer()
    await dispatch_pietre(update, context, query.data)


async def receive_pietre_search(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    _stone_state(context)["search"] = False
    hits = search_stones(text)
    await delete_user_command(update)
    if not hits:
        await reply_html(
            update,
            context,
            f"Nessuna pietra per «{e(text)}». Prova ametista, pirite, ossidiana, condrite…",
            reply_markup=pietre_hub_keyboard(),
        )
        return
    if len(hits) == 1:
        await send_stone_sheet(update, context, hits[0]["id"])
        return
    await send_stone_list(update, context, hits, "🔍 <b>RISULTATI</b>", f"Ricerca: {e(text)}")


def _pietre_accepts_photo(context: ContextTypes.DEFAULT_TYPE) -> bool:
    state = context.user_data.get(STONE_STATE_KEY)
    if isinstance(state, dict) and (state.get("photo") or state.get("lab") is not None or state.get("last")):
        return True
    here = str(context.user_data.get(NAV_HERE_KEY) or "")
    return here.startswith("pt:")


async def on_pietre_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or not message.photo:
        return
    chat = update.effective_chat
    if not _pietre_accepts_photo(context):
        if chat is None or chat.type != "private":
            return
        # in privato, se non siamo in Pietre, non rubo la foto
        return
    state = _stone_state(context)
    state["photo"] = True
    await delete_user_command(update)
    await send_typing(update)
    await deliver_text(update, context, "📸 Confronto la foto con le miniature Wikipedia del catalogo…")
    hints: dict[str, Any] = {"colors": [], "metallic": False, "ok": False}
    details: list[dict[str, Any]] = []
    method = "none"
    try:
        from io import BytesIO

        tg_file = await context.bot.get_file(message.photo[-1].file_id)
        buf = BytesIO()
        await tg_file.download_to_memory(buf)
        raw = buf.getvalue()
        hints = read_photo_hints(raw)
        try:
            client = _http_client(context)
        except StelleOfflineError:
            client = None
        identified = await identify_from_photo(client, raw, n=5)
        hints = identified.get("hints") or hints
        details = list(identified.get("details") or [])
        method = str(identified.get("method") or "none")
    except Exception:
        details = []
        method = "none"
    if not details:
        fallback = guess_stones(hints, n=5)
        if fallback:
            details = [
                {"stone": stone, "score": 0.22, "why": "solo colore del catalogo"}
                for stone in fallback
            ]
            method = "color"
    guesses = [row["stone"] for row in details if isinstance(row, dict) and row.get("stone")]
    color_keys = [c for c in (hints.get("colors") or []) if c in COLORS]
    if color_keys:
        state.setdefault("lab", {})
        if isinstance(state["lab"], dict):
            state["lab"]["color"] = color_keys[0]
    if guesses:
        state["last"] = guesses[0]["id"]
        user = update.effective_user
        if user:
            for stone in guesses:
                await stone_discover(user.id, stone["id"])
    color_bits = [f"{COLORS[key][0]} {COLORS[key][1]}" for key in color_keys]
    if hints.get("metallic") and color_keys:
        color_bits.append("tono metallico")
    if not color_keys or not guesses:
        await reply_html(
            update,
            context,
            "📸 Non ho isolato un colore netto della pietra "
            "(sfondo troppo simile, ombra o foto troppo larga).\n"
            "Scegli tu il colore: da lì restringo il catalogo. "
            "Non pesco pietre di un altro colore.",
            reply_markup=pietre_lab_keyboard("color"),
        )
        return
    seen = ", ".join(color_bits)
    if method == "wiki+clip":
        how = "Confronto: miniature Wikipedia + modello visivo CLIP."
    elif method == "wiki":
        how = "Confronto: miniature Wikipedia delle pietre dello stesso colore."
    elif method == "clip":
        how = "Confronto: modello visivo CLIP, sul catalogo già filtrato per colore."
    else:
        how = "Le miniature Wikipedia non hanno risposto: resto sul colore tipico, senza pescare a caso."
    lines = [
        "📸 <b>IPOTESI DA FOTO</b>",
        f"Colore della pietra: <b>{e(seen)}</b> — sfondo escluso, vincolo non suggerimento.",
        "Prima le pietre tipicamente di quel colore. Le multicolori (fluorite…) solo se la foto è zonata.",
        how,
        "",
    ]
    for i, row in enumerate(details, start=1):
        stone = row["stone"]
        rem, rname = RARITY[stone["rarity"]]
        why = str(row.get("why") or "catalogo")
        label = confidence_label(float(row.get("score") or 0.0))
        lines.append(f"{i}. {stone['emoji']} <b>{e(stone['it'])}</b> · {e(stone['color'])} · {rem} {rname}")
        lines.append(f"   <i>{e(label)} · {e(why)}</i>")
    lines.extend(
        [
            "",
            "Il nome resta un'ipotesi: una foto non sostituisce durezza, striscio e densità.",
        ]
    )
    rows = [[_tarot_btn(f"{s['emoji']} {s['it']}", f"pt:s:{s['id']}")] for s in guesses]
    rows.append([_tarot_btn("🔬 Continua il laboratorio", "pt:lab"), _tarot_btn("📸 Un'altra foto", "pt:photo")])
    rows.append(nav_row())
    await reply_html(update, context, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def cmd_pietre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _cmd_begin(context, "pt:hub")
    await show_pietre_hub(update, context)
    await delete_user_command(update)


async def cmd_pietra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args).strip() if context.args else ""
    _cmd_begin(context, "pt:ora")
    if raw:
        hits = search_stones(raw)
        if hits:
            await send_stone_sheet(update, context, hits[0]["id"])
            await delete_user_command(update)
            return
    await send_stone_oracle(update, context)
    await delete_user_command(update)


async def _compat_has_natal(update: Update) -> bool:
    user = update.effective_user
    if not user:
        return False
    profile = await natal_profile_get(user.id)
    return bool(profile and profile.get("lat") is not None)


async def _compat_my_sun(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    chart = natal_chart_from_state(_natal_state(context))
    if chart:
        sun = (chart.get("planets") or {}).get("Sun")
        if isinstance(sun, dict):
            key = str(sun.get("sign") or "").lower()
            if key in COMPAT_SIGNS:
                return key
    user = update.effective_user
    profile = await natal_profile_get(user.id) if user else None
    if not profile or profile.get("lat") is None:
        return None
    client = _http_client(context)
    try:
        chart = await api_natal_chart(
            client,
            year=int(profile["year"]),
            month=int(profile["month"]),
            day=int(profile["day"]),
            hour=int(profile.get("hour") or 12),
            minute=int(profile.get("minute") or 0),
            lat=float(profile["lat"]),
            lon=float(profile["lon"]),
        )
    except StelleOfflineError:
        return None
    _natal_state(context).update({"chart": chart, **{k: profile.get(k) for k in ("year", "month", "day", "hour", "minute", "lat", "lon", "place")}})
    sun = (chart.get("planets") or {}).get("Sun")
    if isinstance(sun, dict):
        key = str(sun.get("sign") or "").lower()
        if key in COMPAT_SIGNS:
            return key
    return None


async def _compat_kb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    state = _compat_state(context)
    two_charts = isinstance(state.get("chart_a"), dict) and isinstance(state.get("chart_b"), dict)
    return compat_after_keyboard(
        has_natal=await _compat_has_natal(update),
        has_syn=two_charts,
    )


async def _compat_my_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any] | None:
    chart = natal_chart_from_state(_natal_state(context))
    if chart:
        return chart
    if await _compat_my_sun(update, context):
        return natal_chart_from_state(_natal_state(context))
    return None


async def show_compat_hub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    has_natal = await _compat_has_natal(update)
    has_syn = isinstance(_compat_state(context).get("chart_b"), dict)
    await reply_html(
        update,
        context,
        compat_hub_text(has_natal=has_natal, has_syn=has_syn),
        reply_markup=compat_hub_keyboard(has_natal=has_natal, has_syn=has_syn),
    )


async def show_compat_advanced(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    has_natal = await _compat_has_natal(update)
    state = _compat_state(context)
    has_syn = isinstance(state.get("chart_a"), dict) and isinstance(state.get("chart_b"), dict)
    await reply_html(
        update,
        context,
        compat_advanced_text(has_natal=has_natal, has_syn=has_syn),
        reply_markup=compat_advanced_keyboard(has_natal=has_natal, has_syn=has_syn),
    )


async def start_compat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str) -> None:
    state = _compat_state(context)
    state["mode"] = mode
    state["picks"] = {}
    state["step"] = None
    state["source"] = {}
    state["who"] = "a"
    for key in ("chart_a", "chart_b", "year", "month", "day", "hour", "minute", "lat", "lon", "place", "places", "time_unknown"):
        state.pop(key, None)
    if mode == "b3":
        await show_compat_b3_source(update, context, "a")
        return
    if mode == "el":
        chart = await _compat_my_chart(update, context)
        mine = chart_element(chart) if chart else None
        if mine:
            state["picks"] = {"a": mine}
            await show_compat_element_pick(update, context, "b")
            return
        await show_compat_element_pick(update, context, "a")
        return
    slots = COMPAT_SLOTS.get(mode)
    if not slots:
        await show_compat_hub(update, context)
        return
    chart = await _compat_my_chart(update, context)
    points = chart_points(chart) if chart else {}
    picks = state["picks"]
    for slot, dest in MINE_FILL.get(mode, {}).items():
        if dest in points:
            picks[slot] = points[dest]
    await show_compat_slot(update, context)


B3_PERSON_SLOTS = {
    "a": (("as", "il Sole"), ("am", "la Luna"), ("aa", "l'Ascendente")),
    "b": (("bs", "il Sole"), ("bm", "la Luna"), ("ba", "l'Ascendente")),
}
B3_POINT_MAP = {
    "a": {"sun": "as", "moon": "am", "asc": "aa"},
    "b": {"sun": "bs", "moon": "bm", "asc": "ba"},
}


def _compat_who_label(who: str) -> str:
    return "prima persona" if who == "a" else "seconda persona"


async def show_compat_b3_source(update: Update, context: ContextTypes.DEFAULT_TYPE, who: str) -> None:
    state = _compat_state(context)
    state["mode"] = "b3"
    state["who"] = who
    state["step"] = None
    person = _compat_who_label(who)
    await reply_html(
        update,
        context,
        "❤️ <b>BIG THREE</b>\n"
        f"<i>{person}</i>\n\n"
        "Conosci già Sole, Luna e Ascendente, o li calcolo da data, ora e luogo di nascita?",
        reply_markup=compat_b3_source_keyboard(who),
    )


async def show_compat_b3_signs(update: Update, context: ContextTypes.DEFAULT_TYPE, who: str) -> None:
    state = _compat_state(context)
    state["mode"] = "b3"
    state["who"] = who
    slots = B3_PERSON_SLOTS[who]
    picks = state.setdefault("picks", {})
    nxt = next((slot for slot, _label in slots if slot not in picks), None)
    if nxt is None:
        if who == "a":
            await show_compat_b3_source(update, context, "b")
            return
        await finish_compat_mode(update, context)
        return
    label = dict(slots)[nxt]
    person = _compat_who_label(who)
    text = f"❤️ <b>BIG THREE</b>\n<i>{person} — segni che conosci.</i>\n\nScegli {label}."
    filled = ", ".join(
        f"{COMPAT_SIGNS[v][1]} {COMPAT_SIGNS[v][0]}" for slot, v in picks.items() if slot in dict(slots) and v in COMPAT_SIGNS
    )
    if filled:
        text += f"\nGià scelti: {filled}"
    await reply_html(update, context, text, reply_markup=compat_sign_keyboard(f"cp:p:{nxt}:"))


async def compute_compat_b3_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _compat_state(context)
    who = str(state.get("who") or "a")
    if state.get("lat") is None or state.get("year") is None:
        await ask_compat_birth_place(update, context)
        return
    await send_typing(update)
    await deliver_text(update, context, "❤️ Calcolo Sole, Luna e Ascendente (Swiss Ephemeris)…")
    client = _http_client(context)
    try:
        chart = await api_natal_chart(
            client,
            year=int(state["year"]),
            month=int(state["month"]),
            day=int(state["day"]),
            hour=int(state.get("hour") or 12),
            minute=int(state.get("minute") or 0),
            lat=float(state["lat"]),
            lon=float(state["lon"]),
        )
    except StelleOfflineError:
        await reply_offline(update, context)
        return
    points = chart_points(chart)
    picks = state.setdefault("picks", {})
    mapping = B3_POINT_MAP[who]
    for src, dest in mapping.items():
        if src in points:
            picks[dest] = points[src]
    state[f"chart_{who}"] = chart
    state[f"place_{who}"] = state.get("place")
    state["step"] = None
    for key in ("year", "month", "day", "hour", "minute", "lat", "lon", "place", "places", "time_unknown"):
        state.pop(key, None)
    if not all(picks.get(dest) in COMPAT_SIGNS for dest in mapping.values()):
        await reply_html(
            update,
            context,
            "❤️ Non ho trovato Sole, Luna e Ascendente su quella nascita. "
            "Riprova a calcolarli, oppure sceglili a mano.",
            reply_markup=compat_b3_source_keyboard(who),
        )
        return
    if who == "a":
        await show_compat_b3_source(update, context, "b")
        return
    await finish_compat_mode(update, context)


async def show_compat_slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _compat_state(context)
    mode = str(state.get("mode") or "signs")
    slots = COMPAT_SLOTS.get(mode) or COMPAT_SLOTS["signs"]
    picks = state.setdefault("picks", {})
    nxt = next((slot for slot, _label in slots if slot not in picks), None)
    if nxt is None:
        await finish_compat_mode(update, context)
        return
    label = dict(slots)[nxt]
    intros = {
        "signs": ("DUE SEGNI", "I due Soli: identità, ciò che ognuno vuole esprimere."),
        "moon": ("DUE LUNE", "Come vi sentite e di cosa avete bisogno."),
        "asc": ("DUE ASCENDENTI", "Come vi presentate e vi incontrate."),
        "merc": ("DUE MERCURI", "Come parlate e discutete."),
        "vm": ("VENERE E MARTE", "Gusto e slancio: un segno alla volta."),
        "b3": ("BIG THREE", "Sole, Luna, Ascendente: tre porte, non un verdetto."),
    }
    title, intro = intros.get(mode, ("COMPATIBILITÀ", "Scegli un segno."))
    text = f"❤️ <b>{title}</b>\n<i>{intro}</i>\n\nScegli {label}."
    if picks:
        filled = ", ".join(f"{COMPAT_SIGNS[v][1]} {COMPAT_SIGNS[v][0]}" for v in picks.values() if v in COMPAT_SIGNS)
        if filled:
            text += f"\nGià scelti: {filled}"
    await reply_html(update, context, text, reply_markup=compat_sign_keyboard(f"cp:p:{nxt}:"))


async def show_compat_element_pick(update: Update, context: ContextTypes.DEFAULT_TYPE, which: str) -> None:
    title = "il tuo elemento" if which == "a" else "l'elemento dell'altra persona"
    await reply_html(
        update,
        context,
        f"❤️ <b>DUE ELEMENTI</b>\n\nScegli {title}.",
        reply_markup=compat_element_keyboard(which),
    )


async def show_compat_pick(update: Update, context: ContextTypes.DEFAULT_TYPE, which: str) -> None:
    _compat_state(context)["mode"] = "signs"
    if which == "a":
        _compat_state(context)["picks"] = {}
    await show_compat_slot(update, context)


POINT_KINDS = frozenset({"signs", "moon", "asc", "merc"})


async def finish_compat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _compat_state(context)
    mode = str(state.get("mode") or "signs")
    picks = state.get("picks") if isinstance(state.get("picks"), dict) else {}
    kb = await _compat_kb(update, context)
    if mode == "el" and picks.get("a") in COMPAT_ELEMENTS and picks.get("b") in COMPAT_ELEMENTS:
        await reply_html(update, context, format_elements(picks["a"], picks["b"]), reply_markup=kb)
        return
    if mode == "vm" and all(picks.get(k) in COMPAT_SIGNS for k in ("av", "am", "bv", "bm")):
        await reply_html(update, context, format_venus_mars(picks["av"], picks["am"], picks["bv"], picks["bm"]), reply_markup=kb)
        return
    if mode == "b3" and all(picks.get(k) in COMPAT_SIGNS for k in ("as", "am", "aa", "bs", "bm", "ba")):
        await reply_html(
            update,
            context,
            format_big_three(picks["as"], picks["am"], picks["aa"], picks["bs"], picks["bm"], picks["ba"]),
            reply_markup=kb,
        )
        return
    if mode in POINT_KINDS and picks.get("a") in COMPAT_SIGNS and picks.get("b") in COMPAT_SIGNS:
        await reply_html(update, context, format_point_compat(mode, picks["a"], picks["b"]), reply_markup=kb)
        return
    await show_compat_hub(update, context)


async def send_compat_signs(update: Update, context: ContextTypes.DEFAULT_TYPE, a: str, b: str) -> None:
    _compat_state(context).update({"mode": "signs", "picks": {"a": a, "b": b}, "step": None})
    await finish_compat_mode(update, context)


async def send_compat_overlay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _compat_state(context)
    chart_a = state.get("chart_a")
    chart_b = state.get("chart_b")
    if not isinstance(chart_a, dict) or not isinstance(chart_b, dict):
        await show_compat_hub(update, context)
        return
    await reply_html(update, context, format_overlays(chart_a, chart_b), reply_markup=await _compat_kb(update, context))


async def ask_compat_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _compat_state(context)
    state["step"] = "date"
    person = _compat_who_label(str(state.get("who") or "a"))
    title = "BIG THREE" if state.get("mode") == "b3" else "SINASTRIA"
    await reply_html(
        update,
        context,
        f"❤️ <b>{title}</b>\n"
        f"<i>{person} — li calcolo dalla nascita.</i>\n\n"
        "📅 Data di nascita: <code>GG/MM/AAAA</code>",
        reply_markup=InlineKeyboardMarkup([nav_row()]),
    )


async def ask_compat_birth_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _compat_state(context)
    state["step"] = "time"
    person = _compat_who_label(str(state.get("who") or "a"))
    await reply_html(
        update,
        context,
        f"🕐 Ora di nascita della {person}: <code>HH:MM</code>\n"
        "Se non la sai, l'Ascendente sarà solo indicativo (uso mezzogiorno).",
        reply_markup=InlineKeyboardMarkup([[_tarot_btn("❓ Non conosco l'ora", "cp:notime")], nav_row()]),
    )


async def ask_compat_birth_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _compat_state(context)
    state["step"] = "place"
    person = _compat_who_label(str(state.get("who") or "a"))
    await reply_html(
        update,
        context,
        f"📍 Luogo di nascita della {person}.\nEsempio: <code>Roma, Italia</code>",
        reply_markup=InlineKeyboardMarkup([nav_row()]),
    )


async def ask_compat_other_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _compat_state(context)["who"] = "b"
    await ask_compat_birth_date(update, context)


async def ask_compat_other_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ask_compat_birth_time(update, context)


async def ask_compat_other_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ask_compat_birth_place(update, context)


async def _compat_after_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _compat_state(context).get("mode") == "b3":
        await compute_compat_b3_person(update, context)
        return
    await send_compat_synastry(update, context)


async def send_compat_synastry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    profile = await natal_profile_get(user.id) if user else None
    other = _compat_state(context)
    if not profile or other.get("lat") is None:
        await show_compat_hub(update, context)
        return
    await send_typing(update)
    await deliver_text(update, context, "❤️ Confronto le due carte (Swiss Ephemeris)…")
    client = _http_client(context)
    try:
        chart_a = natal_chart_from_state(_natal_state(context))
        if not chart_a:
            chart_a = await api_natal_chart(
                client,
                year=int(profile["year"]),
                month=int(profile["month"]),
                day=int(profile["day"]),
                hour=int(profile.get("hour") or 12),
                minute=int(profile.get("minute") or 0),
                lat=float(profile["lat"]),
                lon=float(profile["lon"]),
            )
            _natal_state(context)["chart"] = chart_a
        chart_b = await api_natal_chart(
            client,
            year=int(other["year"]),
            month=int(other["month"]),
            day=int(other["day"]),
            hour=int(other.get("hour") or 12),
            minute=int(other.get("minute") or 0),
            lat=float(other["lat"]),
            lon=float(other["lon"]),
        )
    except StelleOfflineError:
        await reply_offline(update, context)
        return
    other["step"] = None
    other["chart_b"] = chart_b
    name_a = str(profile.get("place") or "il tuo tema")
    name_b = str(other.get("place") or "l'altra carta")
    await reply_html(
        update,
        context,
        format_synastry(chart_a, chart_b, name_a=name_a, name_b=name_b),
        reply_markup=await _compat_kb(update, context),
    )


async def dispatch_compat(update: Update, context: ContextTypes.DEFAULT_TYPE, token: str) -> None:
    parts = token.split(":")
    action = parts[1] if len(parts) > 1 else "hub"
    extra = parts[2] if len(parts) > 2 else ""
    extra2 = parts[3] if len(parts) > 3 else ""
    if action not in {"a", "b", "loc", "notime", "p", "el"}:
        _compat_state(context)["step"] = None
    if action in {"hub", ""}:
        await show_compat_hub(update, context)
        return
    if action == "adv":
        await show_compat_advanced(update, context)
        return
    if action == "go" and extra in {*COMPAT_SLOTS, "el"}:
        await start_compat_mode(update, context, extra)
        return
    if action == "signs":
        await start_compat_mode(update, context, "signs")
        return
    if action == "src" and extra in {"a", "b"} and extra2 in {"know", "calc"}:
        state = _compat_state(context)
        state["mode"] = "b3"
        state["who"] = extra
        state.setdefault("source", {})[extra] = extra2
        for slot, _label in B3_PERSON_SLOTS[extra]:
            state.setdefault("picks", {}).pop(slot, None)
        state.pop(f"chart_{extra}", None)
        if extra2 == "know":
            await show_compat_b3_signs(update, context, extra)
            return
        await ask_compat_birth_date(update, context)
        return
    if action == "p" and extra2 in COMPAT_SIGNS:
        _compat_state(context).setdefault("picks", {})[extra] = extra2
        if _compat_state(context).get("mode") == "b3":
            who = "a" if extra in {"as", "am", "aa"} else "b"
            await show_compat_b3_signs(update, context, who)
            return
        await show_compat_slot(update, context)
        return
    if action == "el" and extra2 in COMPAT_ELEMENTS:
        picks = _compat_state(context).setdefault("picks", {})
        picks[extra] = extra2
        _compat_state(context)["mode"] = "el"
        if extra == "a":
            await show_compat_element_pick(update, context, "b")
            return
        await finish_compat_mode(update, context)
        return
    if action == "a" and extra in COMPAT_SIGNS:
        _compat_state(context)["mode"] = "signs"
        _compat_state(context)["picks"] = {"a": extra}
        await show_compat_slot(update, context)
        return
    if action == "b" and extra in COMPAT_SIGNS:
        _compat_state(context)["mode"] = "signs"
        picks = _compat_state(context).setdefault("picks", {})
        picks["b"] = extra
        await finish_compat_mode(update, context)
        return
    if action == "syn":
        if not await _compat_has_natal(update):
            await show_compat_hub(update, context)
            return
        await ask_compat_other_date(update, context)
        return
    if action == "ov":
        await send_compat_overlay(update, context)
        return
    if action == "notime":
        state = _compat_state(context)
        state["hour"], state["minute"] = 12, 0
        state["time_unknown"] = True
        await ask_compat_birth_place(update, context)
        return
    if action == "loc" and extra.isdigit():
        places = _compat_state(context).get("places")
        if isinstance(places, list) and 0 <= int(extra) < len(places):
            place = places[int(extra)]
            _compat_state(context)["place"] = place.get("display")
            _compat_state(context)["lat"] = place.get("lat")
            _compat_state(context)["lon"] = place.get("lon")
            await _compat_after_place(update, context)
            return
        await ask_compat_birth_place(update, context)
        return
    await show_compat_hub(update, context)


async def on_cp_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    await query.answer()
    await dispatch_compat(update, context, query.data)


async def receive_compat_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    state = context.user_data.get(COMPAT_STATE_KEY)
    if not isinstance(state, dict):
        return False
    step = state.get("step")
    if step == "date":
        parsed = parse_birth_date(text)
        if not parsed:
            await reply_html(update, context, "Data non valida. Usa <code>GG/MM/AAAA</code>.")
            return True
        state["year"], state["month"], state["day"] = parsed
        await delete_user_command(update)
        await ask_compat_birth_time(update, context)
        return True
    if step == "time":
        parsed = parse_birth_time(text)
        if not parsed:
            await reply_html(
                update,
                context,
                "Orario non valido. Usa <code>HH:MM</code>.",
                reply_markup=InlineKeyboardMarkup([[_tarot_btn("❓ Non conosco l'ora", "cp:notime")], nav_row()]),
            )
            return True
        state["hour"], state["minute"] = parsed
        state["time_unknown"] = False
        await delete_user_command(update)
        await ask_compat_birth_place(update, context)
        return True
    if step == "place":
        await send_typing(update)
        await deliver_text(update, context, "📍 Cerco il luogo…")
        try:
            places = await api_geocode_place(_http_client(context), text)
        except StelleOfflineError:
            await reply_html(update, context, "Luogo non trovato. Prova <code>Milano, Italia</code>.")
            return True
        state["places"] = places
        await delete_user_command(update)
        if len(places) == 1:
            state["place"] = places[0].get("display")
            state["lat"] = places[0].get("lat")
            state["lon"] = places[0].get("lon")
            await _compat_after_place(update, context)
            return True
        rows = [[_tarot_btn(clip_text(str(p["display"]), 40), f"cp:loc:{idx}")] for idx, p in enumerate(places[:4])]
        rows.append(nav_row())
        await reply_html(update, context, "Ho trovato più luoghi. Quale?", reply_markup=InlineKeyboardMarkup(rows))
        return True
    return False


async def cmd_compatibilita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args).strip() if context.args else ""
    _cmd_begin(context, "cp:hub")
    if raw:
        parts = raw.replace(" e ", " ").replace("+", " ").split()
        signs = [normalize_sign(p) for p in parts]
        signs = [s for s in signs if s]
        if len(signs) >= 2:
            await send_compat_signs(update, context, signs[0], signs[1])
            await delete_user_command(update)
            return
        if len(signs) == 1:
            _compat_state(context)["a"] = signs[0]
            await show_compat_pick(update, context, "b")
            await delete_user_command(update)
            return
    await show_compat_hub(update, context)
    await delete_user_command(update)


async def on_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Domanda tarocchi in corso, oppure un segno trattato come oroscopo."""
    message = update.effective_message
    if message is None or not message.text:
        return
    text = message.text.strip()
    stone = context.user_data.get(STONE_STATE_KEY)
    if context.user_data.get(LOC_ASK_KEY):
        await receive_place_city(update, context, text)
        return
    if isinstance(stone, dict) and stone.get("search"):
        await receive_pietre_search(update, context, text)
        return
    if await receive_compat_text(update, context, text):
        return
    if await receive_natal_text(update, context, text):
        return
    oq = context.user_data.get(OQ_STATE_KEY)
    if isinstance(oq, dict) and oq.get("step") == "ask":
        await receive_oq_answer(update, context, text)
        return
    lettura = context.user_data.get(LETTURA_STATE_KEY)
    if isinstance(lettura, dict) and lettura.get("step") == "ask":
        question = clip_text(text, 400)
        if len(question) < 6:
            await reply_html(update, context, "📖 Serve una frase un po' più chiara. Riprova.")
            return
        _lettura_state(context)["question"] = question
        await show_lettura_methods(update, context)
        await delete_user_command(update)
        return
    mirror = context.user_data.get(MIRROR_STATE_KEY)
    if isinstance(mirror, dict) and mirror.get("step") == "ask":
        await receive_mirror_answer(update, context, text)
        return
    rune = context.user_data.get(RUNE_STATE_KEY)
    if isinstance(rune, dict) and rune.get("step") == "ask":
        await receive_rune_question(update, context, text)
        return
    leno = context.user_data.get(LENO_STATE_KEY)
    if isinstance(leno, dict) and leno.get("step") == "ask":
        phrase = clip_text(text.strip(), 400)
        if not phrase:
            await reply_html(update, context, "Una riga basta. Oppure mescola, senza frase.")
            return
        leno["question"] = phrase
        await show_leno_ready(update, context, str(leno.get("n") or "3"))
        await delete_user_command(update)
        return
    if context.user_data.get("cielo_ask"):
        await receive_cielo_city(update, context, text)
        return
    osserva = context.user_data.get(OSSERVA_STATE_KEY)
    if isinstance(osserva, dict) and osserva.get("step") in {"ask", "pick"}:
        await receive_osserva_city(update, context, text)
        return
    iching = context.user_data.get(ICHING_STATE_KEY)
    if isinstance(iching, dict) and iching.get("step") == "ask":
        await receive_iching_question(update, context, text)
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
        "Ho letto il messaggio, ma non è un segno zodiacale.\n"
        "Scrivi un segno (es. <i>vergine</i>) per l'oroscopo, "
        "oppure tocca i pulsanti: 🔮 ORACOLO, 🔭 ASTRO o 🌍 GEO.",
        reply_markup=all_hub_keyboard(),
    )


async def on_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply_html(
        update,
        context,
        "I comandi scritti non ci sono più: qui si va a pulsanti.\n"
        "Tocca 🔮 ORACOLO, 🔭 ASTRO o 🌍 GEO, oppure 📚 Aiuto.",
        reply_markup=all_hub_keyboard(),
    )
    await delete_user_command(update)


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
                BotCommand("start", "BOTSQUAD — i bot"),
                BotCommand("aiuto", "Come si usa"),
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


async def send_geo_quakes(update: Update, context: ContextTypes.DEFAULT_TYPE, feed: str) -> None:
    if feed not in {"day", "week", "sig"}:
        feed = "day"
    await send_typing(update)
    await deliver_text(update, context, "🌋 Scarico il catalogo USGS…")
    try:
        data = await fetch_quakes(_http_client(context), feed)
    except Exception:
        logger.exception("USGS terremoti non disponibile")
        await reply_offline(update, context)
        return
    await reply_html(update, context, format_quakes(data, feed=feed), reply_markup=geo_quakes_keyboard())


async def send_geo_events(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str | None = None) -> None:
    await send_typing(update)
    await deliver_text(update, context, "🌪️ Apro NASA EONET…")
    client = _http_client(context)
    try:
        data = await fetch_eonet(client, limit=12, category=category)
    except Exception:
        logger.exception("EONET non disponibile")
        await reply_offline(update, context)
        return
    events = data.get("events") if isinstance(data.get("events"), list) else []
    titles = [str(ev.get("title") or "") for ev in events[:8] if isinstance(ev, dict) and ev.get("title")]
    if titles:
        try:
            blob = await translate_to_italian(client, " || ".join(titles))
            parts = [p.strip() for p in blob.split("||")]
            idx = 0
            for ev in events[:8]:
                if not isinstance(ev, dict) or not ev.get("title"):
                    continue
                if idx < len(parts) and parts[idx]:
                    ev["title"] = parts[idx]
                idx += 1
        except StelleOfflineError:
            pass
    await reply_html(update, context, format_eonet(data, category=category), reply_markup=geo_events_keyboard())


async def send_earth_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str, sid: str) -> None:
    item = geo_item(kind, sid)
    if item is None:
        await reply_html(update, context, "Questa scheda non è in catalogo GEO.", reply_markup=geo_hub_keyboard())
        return
    await send_typing(update)
    await deliver_text(update, context, f"{item.get('emoji') or '🌍'} Apro la voce di {item['it']}…")
    client = _http_client(context)
    title = str(item.get("wiki_it") or item.get("wiki") or item["it"])
    wiki = await wikipedia_summary(client, title)
    if (not wiki or not wiki.get("extract")) and item.get("wiki") and item.get("wiki") != title:
        wiki = await wikipedia_summary(client, str(item["wiki"]))
    extract = None
    url = None
    if wiki:
        extract = str(wiki.get("extract") or "").strip() or None
        url = str(wiki.get("url") or "") or None
        if extract and wiki.get("lang") == "en":
            try:
                extract = await translate_to_italian(client, extract)
            except StelleOfflineError:
                pass
        if extract:
            extract = clip_text(extract, 900)
    facts: list[tuple[str, str]] = []
    qid = str(item.get("qid") or "")
    if qid:
        try:
            facts = await wikidata_facts(client, qid)
        except Exception:
            facts = []
    text = format_earth_topic(item, extract=extract, facts=facts, url=url)
    await reply_html(update, context, text, reply_markup=geo_after_keyboard(kind), preview=True)


async def dispatch_geo(update: Update, context: ContextTypes.DEFAULT_TYPE, token: str) -> None:
    parts = token.split(":")
    action = parts[1] if len(parts) > 1 else "hub"
    extra = parts[2] if len(parts) > 2 else ""
    extra2 = parts[3] if len(parts) > 3 else ""
    if action in {"hub", ""}:
        await show_geo_hub(update, context)
        return
    if action == "quake":
        await send_geo_quakes(update, context, extra or "day")
        return
    if action == "events":
        await send_geo_events(update, context)
        return
    if action == "ev":
        await send_geo_events(update, context, extra or None)
        return
    if action == "s" and extra and extra2:
        await send_earth_topic(update, context, extra, extra2)
        return
    await show_geo_hub(update, context)


async def on_geo_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or not query.data:
        return
    _remember_from_callback(update, context)
    await query.answer()
    await dispatch_geo(update, context, query.data)


def build_application(token: str) -> Application:
    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler(["aiuto", "help"], cmd_aiuto))
    application.add_handler(CallbackQueryHandler(on_oroscopo_period, pattern=r"^horo:"))
    application.add_handler(CallbackQueryHandler(on_tarot_action, pattern=r"^tarot:"))
    application.add_handler(CallbackQueryHandler(on_iching_action, pattern=r"^iching:"))
    application.add_handler(CallbackQueryHandler(on_natal_action, pattern=r"^natal:"))
    application.add_handler(CallbackQueryHandler(on_osserva_action, pattern=r"^osserva:"))
    application.add_handler(CallbackQueryHandler(on_rune_action, pattern=r"^rune:"))
    application.add_handler(CallbackQueryHandler(on_nav_action, pattern=r"^nav:"))
    application.add_handler(CallbackQueryHandler(on_sole_action, pattern=r"^sole:"))
    application.add_handler(CallbackQueryHandler(on_ora_action, pattern=r"^ora:"))
    application.add_handler(CallbackQueryHandler(on_leno_action, pattern=r"^leno:"))
    application.add_handler(CallbackQueryHandler(on_yn_action, pattern=r"^yn:"))
    application.add_handler(CallbackQueryHandler(on_oq_action, pattern=r"^oq:"))
    application.add_handler(CallbackQueryHandler(on_lett_action, pattern=r"^lett:"))
    application.add_handler(CallbackQueryHandler(on_bot_action, pattern=r"^bot:"))
    application.add_handler(CallbackQueryHandler(on_geo_action, pattern=r"^geo:"))
    application.add_handler(CallbackQueryHandler(on_world_action, pattern=r"^world:"))
    application.add_handler(CallbackQueryHandler(on_sheet_action, pattern=r"^w:"))
    application.add_handler(CallbackQueryHandler(on_aster_action, pattern=r"^aster:"))
    application.add_handler(CallbackQueryHandler(on_quiz_action, pattern=r"^quiz:"))
    application.add_handler(CallbackQueryHandler(on_miss_action, pattern=r"^miss:"))
    application.add_handler(CallbackQueryHandler(on_home_action, pattern=r"^home:"))
    application.add_handler(CallbackQueryHandler(on_cielo_action, pattern=r"^cielo:"))
    application.add_handler(CallbackQueryHandler(on_loc_action, pattern=r"^loc:"))
    application.add_handler(CallbackQueryHandler(on_wx_action, pattern=r"^wx:"))
    application.add_handler(CallbackQueryHandler(on_st_action, pattern=r"^st:"))
    application.add_handler(CallbackQueryHandler(on_co_action, pattern=r"^co:"))
    application.add_handler(CallbackQueryHandler(on_ev_action, pattern=r"^ev:"))
    application.add_handler(CallbackQueryHandler(on_xp_action, pattern=r"^xp:"))
    application.add_handler(CallbackQueryHandler(on_md_action, pattern=r"^md:"))
    application.add_handler(CallbackQueryHandler(on_pt_action, pattern=r"^pt:"))
    application.add_handler(CallbackQueryHandler(on_cp_action, pattern=r"^cp:"))
    application.add_handler(MessageHandler(filters.PHOTO, on_pietre_photo))
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
