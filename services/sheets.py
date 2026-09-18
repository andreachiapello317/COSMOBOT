"""Schede live: Wikipedia + Wikidata + NASA Images. Nessun fatto inventato."""

from __future__ import annotations

import asyncio
import html
import random
from datetime import datetime, timezone
from typing import Any

import httpx

from services.catalog import (
    ASTRONAUTS,
    BLACK_HOLES,
    COMETS,
    CONSTELLATIONS,
    DAILY_MISSIONS,
    DEEP_SKY,
    DWARFS,
    FAMOUS_ASTEROIDS,
    GALAXIES,
    LEARN_TOPICS,
    LIFE_TOPICS,
    MISSIONS,
    MOONS,
    PLANET_EXPLORE_WIKI,
    PLANETS,
    PROBES,
    QUIZ_LEVELS,
    RANDOM_OBJECTS,
    SATELLITES,
    STARS,
    STAR_TYPES,
    by_id,
)
from services.wiki import nasa_image, wikidata_facts, wikipedia_summary

CATALOGS: dict[str, tuple[dict[str, str], ...]] = {
    "p": PLANETS,
    "m": MOONS,
    "g": GALAXIES,
    "b": BLACK_HOLES,
    "n": MISSIONS,
    "a": ASTRONAUTS,
    "l": LEARN_TOPICS,
    "v": LIFE_TOPICS,
    "s": SATELLITES,
    "d": PROBES,
    "r": RANDOM_OBJECTS,
    "f": DWARFS,
    "c": COMETS,
    "z": FAMOUS_ASTEROIDS,
    "t": STARS,
    "y": STAR_TYPES,
    "k": CONSTELLATIONS,
    "o": DEEP_SKY,
}

TITLES = {
    "p": "PIANETA",
    "m": "LUNA",
    "g": "GALASSIA",
    "b": "BUCO NERO",
    "n": "MISSIONE",
    "a": "ASTRONAUTA",
    "l": "LEZIONE",
    "v": "VITA NELL'UNIVERSO",
    "s": "SATELLITE",
    "d": "SONDA",
    "r": "OGGETTO",
    "f": "PIANETA NANO",
    "c": "COMETA",
    "z": "ASTEROIDE",
    "t": "STELLA",
    "y": "TIPO STELLARE",
    "k": "COSTELLAZIONE",
    "o": "CIELO PROFONDO",
}


def e(text: Any) -> str:
    return html.escape(str(text), quote=False)


def clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


def daily_mission(now: datetime | None = None) -> dict[str, Any]:
    day = now or datetime.now(timezone.utc)
    idx = day.timetuple().tm_yday % len(DAILY_MISSIONS)
    return dict(DAILY_MISSIONS[idx])


def catalog_item(kind: str, item_id: str) -> dict[str, str] | None:
    rows = CATALOGS.get(kind)
    if not rows:
        return None
    return by_id(rows, item_id)


async def _wiki_best(client: httpx.AsyncClient, primary: str, fallback: str) -> dict[str, str] | None:
    first = await wikipedia_summary(client, primary)
    if first:
        return first
    if fallback and fallback != primary:
        return await wikipedia_summary(client, fallback)
    return None


async def _empty_list() -> list[Any]:
    return []


async def _none() -> None:
    return None


async def load_sheet(client: httpx.AsyncClient, item: dict[str, str]) -> dict[str, Any]:
    wiki_title = item.get("wiki_it") or item.get("wiki") or item.get("en") or item.get("it") or ""
    fallback = item.get("wiki") or wiki_title
    query = item.get("en") or item.get("it") or wiki_title.replace("_", " ")
    qid = item.get("qid") or ""
    wiki_task = _wiki_best(client, wiki_title, fallback)
    facts_task = wikidata_facts(client, qid) if qid else _empty_list()
    image_task = nasa_image(client, query)
    explore = PLANET_EXPLORE_WIKI.get(item.get("id") or "")
    extra_task = wikipedia_summary(client, explore) if explore else _none()
    wiki, facts, image, extra = await asyncio.gather(wiki_task, facts_task, image_task, extra_task)
    return {"wiki": wiki, "facts": facts or [], "image": image, "explore": extra}


def format_sheet(kind: str, item: dict[str, str], payload: dict[str, Any]) -> str:
    wiki = payload.get("wiki") if isinstance(payload.get("wiki"), dict) else None
    facts = payload.get("facts") if isinstance(payload.get("facts"), list) else []
    image = payload.get("image") if isinstance(payload.get("image"), dict) else None
    explore = payload.get("explore") if isinstance(payload.get("explore"), dict) else None
    emoji = item.get("emoji") or "✨"
    name = item.get("it") or item.get("en") or "Scheda"
    lines = [f"{emoji} <b>{e(TITLES.get(kind, 'SCHEDA'))} — {e(name)}</b>", ""]
    if facts:
        lines.append("📐 <b>Misure (Wikidata)</b>")
        for label, value in facts:
            lines.append(f"• {e(label)}: <code>{e(value)}</code>")
        lines.append("")
    if kind == "k":
        lines.append(
            "✨ Mitologia, stelle principali e come trovarla stanno nella voce Wikipedia: "
            "non aggiungo istruzioni che l'API non dà."
        )
        lines.append("")
    if wiki and wiki.get("extract"):
        extract = str(wiki["extract"])
        if wiki.get("lang") == "en":
            lines.append("📖 <b>Wikipedia</b> <i>(originale inglese)</i>")
        else:
            lines.append("📖 <b>Wikipedia</b>")
        lines.append(e(clip(extract, 900)))
        if wiki.get("url"):
            lines.append(f'\n<a href="{e(wiki["url"])}">Apri la voce</a>')
        lines.append("")
    elif not facts:
        lines.append("La scheda live non è arrivata. Riprova tra poco.")
        lines.append("")
    if explore and explore.get("extract"):
        lines.append("🚀 <b>Mission che lo hanno visitato</b>")
        lines.append(e(clip(str(explore["extract"]), 420)))
        if explore.get("url"):
            lines.append(f'<a href="{e(explore["url"])}">Esplorazione (Wikipedia)</a>')
        lines.append("")
    if image and image.get("title"):
        lines.append(f"🖼️ NASA: <i>{e(clip(str(image['title']), 120))}</i>")
    lines.append("<i>Fonti live: Wikipedia, Wikidata, NASA Images. Nessun numero scritto a mano.</i>")
    return "\n".join(lines)


def format_exoplanet(row: dict[str, Any], *, habitable: bool = False) -> str:
    name = row.get("pl_name") or "Esopianeta"
    host = row.get("hostname") or "—"
    dist = row.get("sy_dist")
    rad = row.get("pl_rade")
    eqt = row.get("pl_eqt")
    method = row.get("discoverymethod") or "—"
    year = row.get("disc_year") or "—"
    try:
        dist_txt = f"~{float(dist):.1f} pc" if dist is not None else "—"
    except (TypeError, ValueError):
        dist_txt = "—"
    try:
        rad_txt = f"{float(rad):.2f} R⊕" if rad is not None else "—"
    except (TypeError, ValueError):
        rad_txt = "—"
    try:
        eqt_txt = f"{float(eqt):.0f} K" if eqt is not None else "—"
    except (TypeError, ValueError):
        eqt_txt = "—"
    kind = "terrestre (raggio < 1.8 R⊕, modello)" if habitable else "scheda archivio"
    lines = [
        f"🪐 <b>{e(name)}</b>",
        "",
        f"⭐ Stella: <b>{e(host)}</b>",
        f"📏 Distanza: {e(dist_txt)}",
        f"🌍 Raggio: {e(rad_txt)}",
        f"🌡️ Temperatura di equilibrio: {e(eqt_txt)}",
        f"🔭 Scoperta: {e(year)} · {e(method)}",
        f"🗂️ Tipo scheda: {e(kind)}",
        "",
        "🔭 <b>Perché è in elenco?</b>",
        "Perché l'archivio NASA lo classifica con questi parametri misurati o stimati.",
        "Non è una prova di oceani, atmosfere abitabili o vita.",
        "",
        "<i>Fonte live: NASA Exoplanet Archive, tabella ps, default_flag=1.</i>",
    ]
    return "\n".join(lines)


def format_exo_list(rows: list[dict[str, Any]], *, title: str, blurb: str) -> str:
    lines = [f"<b>{title}</b>", "", blurb, ""]
    if not rows:
        lines.append("L'archivio non ha risposto, o il filtro non ha restituito righe.")
        return "\n".join(lines)
    for row in rows:
        name = row.get("pl_name") or "—"
        host = row.get("hostname") or "—"
        dist = row.get("sy_dist")
        eqt = row.get("pl_eqt")
        rad = row.get("pl_rade")
        try:
            dist_txt = f"{float(dist):.1f} pc" if dist is not None else "—"
        except (TypeError, ValueError):
            dist_txt = "—"
        try:
            eqt_txt = f"{float(eqt):.0f} K" if eqt is not None else "—"
        except (TypeError, ValueError):
            eqt_txt = "—"
        try:
            rad_txt = f"{float(rad):.2f} R⊕" if rad is not None else "—"
        except (TypeError, ValueError):
            rad_txt = "—"
        lines.append(f"🪐 <b>{e(name)}</b> · {e(host)}")
        lines.append(f"   {e(dist_txt)} · {e(rad_txt)} · Teq {e(eqt_txt)}")
    lines.extend(["", "<i>Filtro TAP live. Numeri dell'archivio, non geologia confermata.</i>"])
    return "\n".join(lines)


def format_habitable(rows: list[dict[str, Any]]) -> str:
    return format_exo_list(
        rows,
        title="🌍 PIANETI NELLA ZONA ABITABILE",
        blurb=(
            "Questi mondi hanno <b>temperatura di equilibrio</b> tra 180 e 310 K "
            "e raggio sotto 1.8 R⊕, secondo i modelli dell'archivio NASA. "
            "Caratteristiche orbitali compatibili con la <b>presenza potenziale</b> "
            "di acqua liquida — non una dichiarazione di vita."
        ),
    )


def format_neo(rows: list[dict[str, Any]]) -> str:
    lines = [
        "☄️ <b>ASTEROIDI VICINI ALLA TERRA</b>",
        "",
        "Passaggi nei prossimi giorni (NASA NeoWs). Distanza = miss distance al massimo avvicinamento.",
        "",
    ]
    if not rows:
        lines.append("NeoWs non ha restituito oggetti, o la chiave NASA è in tetto.")
        return "\n".join(lines)
    for row in rows:
        name = row.get("name") or "NEO"
        flag = " ⚠️ PHA" if row.get("hazardous") else ""
        try:
            dmin = float(row["diam_min"]) if row.get("diam_min") is not None else None
            dmax = float(row["diam_max"]) if row.get("diam_max") is not None else None
            diam = f"{dmin:.0f}–{dmax:.0f} m" if dmin is not None and dmax is not None else "—"
        except (TypeError, ValueError):
            diam = "—"
        try:
            miss = float(row["miss_km"])
            miss_txt = f"{miss:,.0f} km".replace(",", ".")
        except (TypeError, ValueError):
            miss_txt = "—"
        try:
            vel = float(row["velocity"])
            vel_txt = f"{vel:,.0f} km/h".replace(",", ".")
        except (TypeError, ValueError):
            vel_txt = "—"
        lines.append(f"🪨 <b>{e(name)}</b>{flag}")
        lines.append(f"   {e(row.get('day') or '—')} · Ø {e(diam)}")
        lines.append(f"   distanza {e(miss_txt)} · {e(vel_txt)}")
    lines.extend(["", "<i>PHA = potentially hazardous asteroid nel catalogo NASA, non un allarme.</i>"])
    return "\n".join(lines)


def countdown_it(when: datetime, now: datetime) -> str:
    delta = when - now
    if delta.total_seconds() < 0:
        return "già avvenuta"
    days = delta.days
    hours = delta.seconds // 3600
    if days >= 30:
        months = days // 30
        rest = days % 30
        return f"{months} mesi e {rest} giorni"
    if days >= 1:
        return f"{days} giorni e {hours} ore"
    minutes = (delta.seconds % 3600) // 60
    return f"{hours} ore e {minutes} minuti"


def ritual_for_phase(phase: str) -> tuple[str, str, str]:
    key = phase.lower()
    if "new" in key:
        return ("🌑 Nuova Luna", "intenzione", "Scrivi una intenzione in una riga. Non deve essere un voto: è un segno che dai a te stesso.")
    if "full" in key:
        return ("🌕 Luna piena", "riflessione / rilascio", "Cosa puoi lasciare stasera, anche solo a voce? La Luna piena qui è un gancio simbolico, non un effetto misurato.")
    if "waning" in key or "last" in key or "third" in key:
        return ("🌘 Luna calante", "chiusura", "Chiudi una cosa piccola: un tab, una chat, una scusa. Rituale di chiusura, non astronomia.")
    if "waxing" in key or "first" in key:
        return ("🌒 Luna crescente", "coltivare", "Scegli una abitudine minuta da ripetere fino alla prossima fase. Simbolo, non prova scientifica.")
    return ("🌙 Luna", "presenza", "Esci un minuto e guarda il cielo, se puoi. Basta questo.")


async def build_quiz(client: httpx.AsyncClient, level: str) -> dict[str, Any] | None:
    if level == "easy":
        item = random.choice(PLANETS)
        wiki = await _wiki_best(client, item.get("wiki_it") or item["wiki"], item["wiki"])
        if not wiki or not wiki.get("extract"):
            return None
        sentence = clip(str(wiki["extract"]).replace(item["it"], "questo mondo").replace(item["en"], "questo mondo"), 280)
        options = [item["it"]]
        others = [p["it"] for p in PLANETS if p["id"] != item["id"]]
        options.extend(random.sample(others, 2))
        random.shuffle(options)
        return {
            "level": level,
            "question": f"Di quale pianeta parla Wikipedia?\n\n<i>{e(sentence)}</i>",
            "options": options,
            "correct": options.index(item["it"]),
            "source": "Wikipedia",
        }
    if level == "medium":
        packed: list[tuple[dict[str, str], list[tuple[str, str]]]] = []
        sample = random.sample(list(PLANETS), k=min(4, len(PLANETS)))
        results = await asyncio.gather(*[wikidata_facts(client, p["qid"]) for p in sample])
        for planet, facts in zip(sample, results):
            if facts:
                packed.append((planet, facts))
        if len(packed) < 2:
            return None
        planet, facts = random.choice(packed)
        label, value = random.choice(facts)
        distractors = []
        for other, ofacts in packed:
            if other["id"] == planet["id"]:
                continue
            for olabel, oval in ofacts:
                if olabel == label and oval != value:
                    distractors.append(oval)
        if len(distractors) < 2:
            distractors.extend(f"{other['it']}" for other, _ in packed if other["id"] != planet["id"])
        options = [value]
        for item in distractors:
            if item not in options:
                options.append(item)
            if len(options) == 3:
                break
        if len(options) < 3:
            return None
        random.shuffle(options)
        return {
            "level": level,
            "question": f"Wikidata: qual è <b>{e(label)}</b> di <b>{e(planet['it'])}</b>?",
            "options": options,
            "correct": options.index(value),
            "source": f"Wikidata {planet['qid']}",
        }
    if level == "hard":
        pool = list(MOONS) + list(GALAXIES) + list(MISSIONS)
        item = random.choice(pool)
        wiki = await _wiki_best(client, item.get("wiki_it") or item["wiki"], item["wiki"])
        if not wiki or not wiki.get("extract"):
            return None
        sentence = clip(str(wiki["extract"]).replace(item["it"], "questo oggetto").replace(item.get("en") or "", "questo oggetto"), 280)
        options = [item["it"]]
        others = [x["it"] for x in pool if x["id"] != item["id"]]
        options.extend(random.sample(others, 2))
        random.shuffle(options)
        return {
            "level": level,
            "question": f"Wikipedia, livello difficile. Cos'è?\n\n<i>{e(sentence)}</i>",
            "options": options,
            "correct": options.index(item["it"]),
            "source": "Wikipedia",
        }
    from services.exoplanets import habitable_candidates, random_exoplanet

    rows = await habitable_candidates(client, limit=12)
    if len(rows) < 3:
        one = await random_exoplanet(client)
        rows = [one] if one else []
        extra = await habitable_candidates(client, limit=8)
        rows.extend(extra)
    rows = [r for r in rows if r.get("pl_name") and r.get("hostname")]
    if len(rows) < 3:
        return None
    target = random.choice(rows)
    host = str(target["hostname"])
    options = [host]
    for row in rows:
        name = str(row.get("hostname") or "")
        if name and name not in options:
            options.append(name)
        if len(options) == 3:
            break
    if len(options) < 3:
        return None
    random.shuffle(options)
    return {
        "level": "expert",
        "question": f"☠️ NASA Archive: quale stella ospita <b>{e(target['pl_name'])}</b>?",
        "options": options,
        "correct": options.index(host),
        "source": "NASA Exoplanet Archive (ps)",
    }


def quiz_levels_text() -> str:
    lines = [
        "🧩 <b>QUIZ</b>",
        "",
        "Domande costruite al volo da Wikipedia, Wikidata o dall'archivio esopianeti.",
        "Niente domande inventate. Classifica solo tua.",
        "",
    ]
    for key, label, hint in QUIZ_LEVELS:
        lines.append(f"{label} — {hint}")
    return "\n".join(lines)
