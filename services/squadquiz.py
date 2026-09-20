"""Quiz per ogni bot di BOTSQUAD. Domande da cataloghi e calcoli, niente fatti inventati."""

from __future__ import annotations

import random
from typing import Any

from services.calc import CONVERSIONS, convert_value, format_number, percent_of
from services.catalog import MOONS, PLANETS
from services.compat import SIGNS
from services.earth import EARTH_TOPICS, OCEANS, VOLCANOES
from services.lenormand import LENORMAND
from services.runes import ELDER_FUTHARK
from services.stones import CATS, STONES

WORLD_META: dict[str, dict[str, str]] = {
    "oracolo": {"emoji": "🔮", "name": "ORACOLO", "blurb": "Tradizione dei mazzi e dei segni. Non è una lettura."},
    "astro": {"emoji": "🔭", "name": "ASTRO", "blurb": "Catalogo e, se vuoi, domande live da Wikipedia."},
    "geo": {"emoji": "🌿", "name": "NATURA", "blurb": "Pietre, terra, vulcani, oceani. Fauna ancora no."},
    "tool": {"emoji": "🧰", "name": "STRUMENTI", "blurb": "Calcoli, cardinali, conversioni. Il risultato si può verificare."},
}

TOPICS: dict[str, tuple[tuple[str, str], ...]] = {
    "oracolo": (("segni", "♈ Segni"), ("rune", "🪶 Rune"), ("leno", "🌿 Lenormand")),
    "astro": (("solare", "☀️ Sistema solare"), ("lune", "🌑 Lune"), ("live", "📡 Enciclopedia live")),
    "geo": (("pietre", "💎 Pietre"), ("terra", "🌍 Terra"), ("volc", "🔥 Vulcani"), ("ocean", "🌊 Oceani")),
    "tool": (
        ("arit", "➕ Calcoli"),
        ("pct", "➗ Percentuali"),
        ("conv", "🔄 Conversioni"),
        ("card", "🧭 Cardinali"),
        ("dir", "📐 Direzioni"),
    ),
}


def canonical_wid(wid: str) -> str:
    return {"calc": "tool", "bussola": "tool"}.get(str(wid or ""), str(wid or ""))


def worlds() -> list[dict[str, str]]:
    return [WORLD_META[key] | {"id": key} for key in WORLD_META]


def topics_of(wid: str) -> tuple[tuple[str, str], ...]:
    return TOPICS.get(canonical_wid(wid), ())


def topic_label(wid: str, tid: str) -> str:
    for key, label in topics_of(wid):
        if key == tid:
            return label
    return tid


def _mcq(question: str, correct: str, pool: list[str], *, source: str, explain: str, wid: str, tid: str) -> dict[str, Any] | None:
    others = [item for item in pool if item != correct]
    if len(others) < 2:
        return None
    options = [correct, *random.sample(others, 2)]
    random.shuffle(options)
    return {
        "bot": wid,
        "topic": tid,
        "question": question,
        "options": options,
        "correct": options.index(correct),
        "source": source,
        "explain": explain,
        "level": wid,
    }


def _oracolo_segni() -> dict[str, Any] | None:
    key = random.choice(list(SIGNS))
    it, _em, element, mode = SIGNS[key]
    kind = random.choice(("el", "md", "name"))
    if kind == "el":
        return _mcq(
            f"Nella tradizione dei segni, di quale elemento è <b>{it}</b>?",
            element,
            ["fuoco", "terra", "aria", "acqua"],
            source="catalogo segni (tradizione)",
            explain=f"{it} è segno di {element}, modalità {mode}. È astrologia, non astronomia.",
            wid="oracolo",
            tid="segni",
        )
    if kind == "md":
        return _mcq(
            f"Nella tradizione, <b>{it}</b> è un segno…",
            mode,
            ["cardinale", "fisso", "mutabile"],
            source="catalogo segni (tradizione)",
            explain=f"{it}: modalità {mode}, elemento {element}.",
            wid="oracolo",
            tid="segni",
        )
    return _mcq(
        f"Quale segno è di <b>{element}</b> e <b>{mode}</b>?",
        it,
        [row[0] for row in SIGNS.values()],
        source="catalogo segni (tradizione)",
        explain=f"{it}: {element}, {mode}.",
        wid="oracolo",
        tid="segni",
    )


def _oracolo_rune() -> dict[str, Any] | None:
    rune = random.choice(ELDER_FUTHARK)
    others = [row["name"] for row in ELDER_FUTHARK]
    return _mcq(
        f"Nel dataset Elder Futhark, quale runa è <b>{rune['glyph']}</b> (suono {rune['phonetic']})?",
        str(rune["name"]),
        others,
        source="dataset rune locale",
        explain=f"{rune['glyph']} è {rune['name']}. I testi di significato sono simbolici.",
        wid="oracolo",
        tid="rune",
    )


def _oracolo_leno() -> dict[str, Any] | None:
    card = random.choice(LENORMAND)
    return _mcq(
        f"Lenormand n.{card['num']}: come si chiama {card['emoji']}?",
        card["it"],
        [row["it"] for row in LENORMAND],
        source="dataset Lenormand locale",
        explain=f"Carta {card['num']}: {card['it']}. Chiavi: {card['keys']}.",
        wid="oracolo",
        tid="leno",
    )


def _astro_solare() -> dict[str, Any] | None:
    item = random.choice(PLANETS)
    kind = random.choice(("it", "en"))
    if kind == "en" and item.get("en"):
        return _mcq(
            f"Nel catalogo, come si chiama in italiano <b>{item['en']}</b>?",
            item["it"],
            [row["it"] for row in PLANETS],
            source="catalogo ASTRO",
            explain=f"{item['en']} → {item['it']}. Voce Wikipedia: {item.get('wiki_it') or item['wiki']}.",
            wid="astro",
            tid="solare",
        )
    return _mcq(
        f"Quale corpo del catalogo ha emoji {item['emoji']} e voce <b>{item.get('wiki_it') or item['wiki']}</b>?",
        item["it"],
        [row["it"] for row in PLANETS],
        source="catalogo ASTRO",
        explain=f"È {item['it']}.",
        wid="astro",
        tid="solare",
    )


def _astro_lune() -> dict[str, Any] | None:
    item = random.choice(MOONS)
    return _mcq(
        f"Quale di questi è una luna del catalogo (non un pianeta)?",
        item["it"],
        [row["it"] for row in PLANETS] + [row["it"] for row in MOONS],
        source="catalogo lune ASTRO",
        explain=f"{item['it']} è nel catalogo lune. I pianeti stanno a parte.",
        wid="astro",
        tid="lune",
    )


def _geo_pietre() -> dict[str, Any] | None:
    stone = random.choice(STONES)
    kind = random.choice(("formula", "cat", "mohs"))
    if kind == "formula" and stone.get("formula"):
        return _mcq(
            f"Qual è la formula nel catalogo di <b>{stone['it']}</b>?",
            str(stone["formula"]),
            [str(row.get("formula") or "") for row in STONES if row.get("formula")],
            source="catalogo pietre",
            explain=f"{stone['it']}: {stone['formula']}. Non è un prezzo e non è un oracolo.",
            wid="geo",
            tid="pietre",
        )
    if kind == "mohs" and stone.get("mohs"):
        return _mcq(
            f"Durezza Mohs di <b>{stone['it']}</b> nel catalogo?",
            str(stone["mohs"]),
            [str(row.get("mohs") or "") for row in STONES if row.get("mohs")],
            source="catalogo pietre",
            explain=f"{stone['it']}: Mohs {stone['mohs']}.",
            wid="geo",
            tid="pietre",
        )
    cat = CATS.get(str(stone.get("cat") or ""), ("•", stone.get("cat") or "—"))[1]
    pool = [pair[1] for pair in CATS.values()]
    return _mcq(
        f"Nel catalogo, <b>{stone['it']}</b> sta sotto quale gruppo?",
        cat,
        pool,
        source="catalogo pietre",
        explain=f"{stone['it']} è in {cat}.",
        wid="geo",
        tid="pietre",
    )


def _geo_list(rows: tuple[dict[str, str], ...], tid: str, title: str) -> dict[str, Any] | None:
    item = random.choice(rows)
    return _mcq(
        f"{title}: quale voce ha wiki <b>{item.get('wiki_it') or item.get('wiki')}</b>?",
        item["it"],
        [row["it"] for row in rows],
        source="catalogo NATURA / Wikipedia title",
        explain=f"È {item['it']}. Apro la voce, non la riscrivo.",
        wid="geo",
        tid=tid,
    )


def _math_arit() -> dict[str, Any] | None:
    a, b = random.randint(6, 40), random.randint(2, 12)
    op = random.choice(("+", "−", "×"))
    if op == "+":
        correct = a + b
        others = [a + b + 1, a + b - 1, a + b + 2, abs(a - b)]
    elif op == "−":
        correct = a - b
        others = [a - b + 1, a - b - 1, b - a, a + b]
    else:
        correct = a * b
        others = [a * b + a, a * b - b, a + b, a * (b + 1)]
    pretty = format_number(float(correct))
    pool = [format_number(float(x)) for x in others if format_number(float(x)) != pretty]
    return _mcq(
        f"Quanto fa <b>{a} {op} {b}</b>?",
        pretty,
        pool,
        source="calcolo locale",
        explain=f"{a} {op} {b} = {pretty}.",
        wid="tool",
        tid="arit",
    )


def _math_pct() -> dict[str, Any] | None:
    pct = random.choice((5, 10, 15, 20, 25, 50))
    whole = random.choice((40, 60, 80, 100, 120, 200))
    value = percent_of(float(pct), float(whole))
    pretty = format_number(value)
    others = [format_number(percent_of(float(p), float(whole))) for p in (5, 10, 15, 20, 25, 50) if p != pct]
    others.extend([format_number(float(whole - pct)), format_number(float(pct))])
    return _mcq(
        f"Quanto è il <b>{pct}%</b> di <b>{whole}</b>?",
        pretty,
        others,
        source="calcolo locale",
        explain=f"{pct}% di {whole} = {pretty}.",
        wid="tool",
        tid="pct",
    )


def _math_conv() -> dict[str, Any] | None:
    kind = random.choice(list(CONVERSIONS))
    src, dst, _mul, _add = CONVERSIONS[kind]
    raw = random.choice((1.0, 2.0, 5.0, 10.0, 20.0, 32.0, 100.0))
    if kind in {"c_f", "f_c"}:
        raw = random.choice((0.0, 10.0, 20.0, 32.0, 100.0))
    out, _s, _d = convert_value(kind, raw)
    pretty = format_number(out)
    distractors = [
        format_number(convert_value(kind, raw + 1)[0]),
        format_number(raw),
        format_number(out + 1),
        format_number(abs(out - raw)),
    ]
    return _mcq(
        f"Converti <b>{format_number(raw)} {src}</b> in <b>{dst}</b>.",
        pretty,
        distractors,
        source="fattori fissi (SI / consuetudine)",
        explain=f"{format_number(raw)} {src} = {pretty} {dst}.",
        wid="tool",
        tid="conv",
    )


def _bussola_card() -> dict[str, Any] | None:
    table = ((0, "nord"), (90, "est"), (180, "sud"), (270, "ovest"))
    deg, name = random.choice(table)
    kind = random.choice(("deg", "name"))
    if kind == "deg":
        return _mcq(
            f"Azimut geografico: quanti gradi è il <b>{name}</b>?",
            str(deg),
            ["0", "45", "90", "135", "180", "270"],
            source="convenzione 0° = nord geografico",
            explain=f"{name.capitalize()} = {deg}°. Est 90, sud 180, ovest 270.",
            wid="tool",
            tid="card",
        )
    return _mcq(
        f"L'azimut <b>{deg}°</b> (nord geografico = 0°) punta a…",
        name,
        ["nord", "est", "sud", "ovest"],
        source="convenzione 0° = nord geografico",
        explain=f"{deg}° è {name}.",
        wid="tool",
        tid="card",
    )


def _bussola_dir() -> dict[str, Any] | None:
    options = [
        (
            "La distanza di BUSSOLA «verso un luogo» è…",
            "in linea d'aria sul grande cerchio",
            [
                "il percorso stradale",
                "il tempo di cammino",
                "in linea d'aria sul grande cerchio",
                "l'altitudine GPS",
            ],
            "È il grande cerchio, non il navigatore.",
        ),
        (
            "La bussola del telefono, da sola, punta di solito al…",
            "nord magnetico",
            ["nord geografico", "nord magnetico", "nord della mappa", "est"],
            "Il nord magnetico e quello geografico differiscono della declinazione (WMM).",
        ),
        (
            "La quota in Posizione GPS arriva da…",
            "modello del terreno Open-Meteo",
            [
                "l'altimetro del telefono",
                "modello del terreno Open-Meteo",
                "un barometro inventato",
                "Wikidata",
            ],
            "Lo diciamo in scheda: non è l'altitudine GPS del telefono.",
        ),
    ]
    question, correct, pool, explain = random.choice(options)
    return _mcq(
        question,
        correct,
        pool,
        source="comportamento di STRUMENTI / Bussola",
        explain=explain,
        wid="tool",
        tid="dir",
    )


BUILDERS = {
    ("oracolo", "segni"): _oracolo_segni,
    ("oracolo", "rune"): _oracolo_rune,
    ("oracolo", "leno"): _oracolo_leno,
    ("astro", "solare"): _astro_solare,
    ("astro", "lune"): _astro_lune,
    ("geo", "pietre"): _geo_pietre,
    ("geo", "terra"): lambda: _geo_list(EARTH_TOPICS, "terra", "Terra"),
    ("geo", "volc"): lambda: _geo_list(VOLCANOES, "volc", "Vulcani"),
    ("geo", "ocean"): lambda: _geo_list(OCEANS, "ocean", "Oceani"),
    ("tool", "arit"): _math_arit,
    ("tool", "pct"): _math_pct,
    ("tool", "conv"): _math_conv,
    ("tool", "card"): _bussola_card,
    ("tool", "dir"): _bussola_dir,
    ("calc", "arit"): _math_arit,
    ("calc", "pct"): _math_pct,
    ("calc", "conv"): _math_conv,
    ("bussola", "card"): _bussola_card,
    ("bussola", "dir"): _bussola_dir,
}


def pick_local_question(wid: str, tid: str) -> dict[str, Any] | None:
    wid = canonical_wid(wid)
    builder = BUILDERS.get((wid, tid))
    if builder is None:
        return None
    for _ in range(8):
        item = builder()
        if item and len(item.get("options") or []) >= 2:
            return item
    return None
