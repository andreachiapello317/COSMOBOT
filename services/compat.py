"""Compatibilità di Te stesso: struttura dei segni + sinastria da carte live.

I testi sui segni sono tradizione astrologica, non astronomia.
Le posizioni della sinastria arrivano da CosmyDay (Swiss Ephemeris).
Niente percentuali inventate.
"""

from __future__ import annotations

from typing import Any

SIGN_ORDER = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

# it, emoji, elemento, modalità
SIGNS: dict[str, tuple[str, str, str, str]] = {
    "aries": ("Ariete", "♈", "fuoco", "cardinale"),
    "taurus": ("Toro", "♉", "terra", "fisso"),
    "gemini": ("Gemelli", "♊", "aria", "mutabile"),
    "cancer": ("Cancro", "♋", "acqua", "cardinale"),
    "leo": ("Leone", "♌", "fuoco", "fisso"),
    "virgo": ("Vergine", "♍", "terra", "mutabile"),
    "libra": ("Bilancia", "♎", "aria", "cardinale"),
    "scorpio": ("Scorpione", "♏", "acqua", "fisso"),
    "sagittarius": ("Sagittario", "♐", "fuoco", "mutabile"),
    "capricorn": ("Capricorno", "♑", "terra", "cardinale"),
    "aquarius": ("Acquario", "♒", "aria", "fisso"),
    "pisces": ("Pesci", "♓", "acqua", "mutabile"),
}

ELEMENT_NOTE = {
    ("fuoco", "fuoco"): "Stesso elemento: stesso ritmo. La tradizione vede slancio condiviso e il rischio di troppa fiamma.",
    ("terra", "terra"): "Stesso elemento: concreto, lento a fidarsi, solido se c'è rispetto.",
    ("aria", "aria"): "Stesso elemento: parole e idee. Serve un corpo, non solo conversazione.",
    ("acqua", "acqua"): "Stesso elemento: sentire condiviso. Attenzione a fondersi senza distinguersi.",
    ("fuoco", "aria"): "Aria alimenta il fuoco: slancio e parole. Tradizione: coppia che si muove.",
    ("fuoco", "terra"): "Fuoco vuole partire, terra vuole radice. Tradizione: attrito utile se si ascoltano.",
    ("fuoco", "acqua"): "Fuoco e acqua: intensità e evaporazione. Tradizione: passione che chiede cura.",
    ("terra", "aria"): "Terra vuole prova, aria vuole spazio. Tradizione: mente e materia da accordare.",
    ("terra", "acqua"): "Terra contiene l'acqua: cura, casa, tempo. Tradizione: coppia che costruisce.",
    ("aria", "acqua"): "Aria nomina, acqua sente. Tradizione: traduzione continua tra testa e cuore.",
}

SIGN_ANGLE = {
    0: ("Congiunzione", "☌", "Stesso segno: stessa lente, stesso punto cieco."),
    1: ("Semisestile", "⚺", "30°: si sfiorano, non si sovrappongono."),
    2: ("Sestile", "⚹", "60°: dialogo relativamente facile, nella tradizione."),
    3: ("Quadratura", "□", "90°: attrito che spinge a muoversi."),
    4: ("Trigono", "△", "120°: stesso elemento, scorrimento."),
    5: ("Quincunx", "⚻", "150°: aggiustamento, poco automatico."),
    6: ("Opposizione", "☍", "180°: specchio e polarità."),
}

ASPECT_ORBS = (
    (0, "Congiunzione", "☌", 8.0),
    (60, "Sestile", "⚹", 6.0),
    (90, "Quadratura", "□", 7.0),
    (120, "Trigono", "△", 8.0),
    (180, "Opposizione", "☍", 8.0),
)

PLANET_IT = {
    "Sun": ("☀️", "Sole"),
    "Moon": ("🌙", "Luna"),
    "Mercury": ("☿️", "Mercurio"),
    "Venus": ("♀️", "Venere"),
    "Mars": ("♂️", "Marte"),
}

SYNASTRY_PAIRS = (
    ("Sun", "Sun"),
    ("Moon", "Moon"),
    ("Sun", "Moon"),
    ("Moon", "Sun"),
    ("Venus", "Mars"),
    ("Mars", "Venus"),
    ("Venus", "Venus"),
    ("Mars", "Mars"),
    ("Mercury", "Mercury"),
)


def sign_label(key: str) -> str:
    it, emoji, _el, _md = SIGNS[key]
    return f"{emoji} {it}"


def _pair_note(el_a: str, el_b: str) -> str:
    key = (el_a, el_b) if (el_a, el_b) in ELEMENT_NOTE else (el_b, el_a)
    return ELEMENT_NOTE.get(key, "Due temperamenti diversi: la tradizione li legge come lavoro, non come verdetto.")


POINT_META = {
    "signs": (
        "☀️ DUE SEGNI",
        "I due Soli: ciò che ognuno vuole essere e far vedere. "
        "È il confronto più semplice, quello da oroscopo. Non dice come dormite o come vi incontrate.",
    ),
    "moon": (
        "🌙 DUE LUNE",
        "Le due Lune: bisogni, umore, dove si torna a casa. "
        "Due Lune vicine si capiscono senza spiegare; due Lune lontane si accudiscono in modi diversi.",
    ),
    "asc": (
        "⬆️ DUE ASCENDENTI",
        "I due Ascendenti: la porta, il primo gesto, come si entra in una stanza. "
        "Non è chi siete dentro: è come vi riconoscete al primo sguardo.",
    ),
    "merc": (
        "☿️ DUE MERCURI",
        "I due Mercuri: parole, ritmo, come si discute. "
        "Utile se vi perdete nelle chat; non sostituisce Sole e Luna.",
    ),
}

B3_ROW = {
    "sun": (
        "☀️ Soli — identità",
        "Cosa volete mostrare. Due Soli dicono se la luce che cercate è la stessa.",
    ),
    "moon": (
        "🌙 Lune — casa",
        "Dove vi riposate. Due Lune dicono se vi accudite o vi spiazzate.",
    ),
    "asc": (
        "⬆️ Ascendenti — porta",
        "Come vi incontrate. Due porte dicono se il primo gesto è familiare o straniero.",
    ),
}

ELEMENTS = {
    "fuoco": ("🔥", "Fuoco"),
    "terra": ("🌍", "Terra"),
    "aria": ("💨", "Aria"),
    "acqua": ("💧", "Acqua"),
}

HOUSE_IT = {
    1: "identità / come ti incontrano",
    2: "risorse e valore",
    3: "parole e quotidianità",
    4: "casa e radici",
    5: "piacere e creatività",
    6: "cura e routine",
    7: "relazione e confronto",
    8: "intimità e crisi",
    9: "senso e orizzonte",
    10: "ruolo nel mondo",
    11: "amicizie e progetti",
    12: "invisibile e soglia",
}


def _angle(a: str, b: str) -> tuple[int, str, str, str]:
    diff = abs(SIGN_ORDER.index(a) - SIGN_ORDER.index(b))
    steps = min(diff % 12, 12 - (diff % 12))
    name, glyph, note = SIGN_ANGLE[steps]
    return steps, name, glyph, note


def format_sign_compat(a: str, b: str) -> str:
    return format_point_compat("signs", a, b)


def format_point_compat(kind: str, a: str, b: str) -> str:
    title, blurb = POINT_META.get(kind, POINT_META["signs"])
    ia, ea, ela, mda = SIGNS[a]
    ib, eb, elb, mdb = SIGNS[b]
    steps, ang_name, glyph, ang_note = _angle(a, b)
    same_mode = "stessa modalità" if mda == mdb else f"{mda} + {mdb}"
    return "\n".join(
        [
            f"❤️ <b>{title}</b>",
            f"<i>{blurb}</i>",
            "",
            f"{ea} <b>{ia}</b>  ·  {eb} <b>{ib}</b>",
            "",
            f"Elementi: {ela} + {elb}",
            _pair_note(ela, elb),
            "",
            f"Modalità: {same_mode}",
            f"Angolo: {glyph} {ang_name} ({steps * 30}°)",
            ang_note,
            "",
            "<i>Scheda di tradizione astrologica, non astronomia e non un verdetto. "
            "Niente percentuali.</i>",
        ]
    )


def format_elements(a: str, b: str) -> str:
    ea, na = ELEMENTS[a]
    eb, nb = ELEMENTS[b]
    return "\n".join(
        [
            "❤️ <b>DUE ELEMENTI</b>",
            "<i>Quattro temperamenti della tradizione: fuoco, terra, aria, acqua. "
            "Non sono due oroscopi e non sono un test di coppia.</i>",
            "",
            f"{ea} <b>{na}</b>  ·  {eb} <b>{nb}</b>",
            "",
            _pair_note(a, b),
            "",
            "<i>Schema classico, non chimica.</i>",
        ]
    )


def format_venus_mars(av: str, am: str, bv: str, bm: str) -> str:
    lines = [
        "❤️ <b>VENERE E MARTE</b>",
        "<i>Scheda dell'attrazione, nella tradizione: Venere è il gusto, Marte lo slancio. "
        "Non è una previsione sessuale e non è un punteggio.</i>",
        "",
    ]
    pairs = (
        ("Tua Venere · Marte altra", av, bm),
        ("Tuo Marte · Venere altra", am, bv),
        ("Due Veneri (gusto)", av, bv),
        ("Due Marti (ritmo)", am, bm),
    )
    for title, a, b in pairs:
        ia, ea, ela, _m = SIGNS[a]
        ib, eb, elb, _n = SIGNS[b]
        steps, ang_name, glyph, _note = _angle(a, b)
        lines.append(f"<b>{title}</b>")
        lines.append(f"{ea} {ia}  ·  {eb} {ib}")
        lines.append(f"{ela}+{elb} · {glyph} {ang_name} ({steps * 30}°)")
        lines.append(_pair_note(ela, elb))
        lines.append("")
    lines.append("<i>Quattro incroci tradizionali. Due persone restano più di quattro segni.</i>")
    return "\n".join(lines)


def format_big_three(
    asun: str,
    amoon: str,
    aasc: str,
    bsun: str,
    bmoon: str,
    basc: str,
) -> str:
    lines = [
        "❤️ <b>BIG THREE</b>",
        "<i>Sole, Luna e Ascendente di due persone. Tre porte: identità, casa, primo incontro. "
        "Chi li ha fatti calcolare usa data, ora e luogo (Swiss Ephemeris). Non è un verdetto.</i>",
        "",
    ]
    rows = (
        ("sun", asun, bsun),
        ("moon", amoon, bmoon),
        ("asc", aasc, basc),
    )
    for kind, a, b in rows:
        title, note = B3_ROW[kind]
        ia, ea, ela, _m = SIGNS[a]
        ib, eb, elb, _n = SIGNS[b]
        steps, ang_name, glyph, ang_note = _angle(a, b)
        lines.append(f"<b>{title}</b>")
        lines.append(f"<i>{note}</i>")
        lines.append(f"{ea} {ia}  ·  {eb} {ib}")
        lines.append(f"{ela}+{elb} · {glyph} {ang_name} ({steps * 30}°)")
        lines.append(ang_note)
        lines.append("")
    lines.append("<i>Due carte vive, tre confronti. Niente percentuali.</i>")
    return "\n".join(lines)


def chart_points(chart: dict[str, Any]) -> dict[str, str]:
    planets = chart.get("planets") if isinstance(chart.get("planets"), dict) else {}
    out: dict[str, str] = {}
    for key, dest in (("Sun", "sun"), ("Moon", "moon"), ("Venus", "venus"), ("Mars", "mars"), ("Mercury", "merc")):
        body = planets.get(key)
        if not isinstance(body, dict):
            continue
        sign = str(body.get("sign") or "").lower()
        if sign in SIGNS:
            out[dest] = sign
    try:
        lon = float(chart.get("ascendant") or 0) % 360.0
        out["asc"] = SIGN_ORDER[int(lon // 30) % 12]
    except (TypeError, ValueError):
        pass
    return out


def chart_element(chart: dict[str, Any]) -> str | None:
    planets = chart.get("planets") if isinstance(chart.get("planets"), dict) else {}
    counts = {key: 0 for key in ELEMENTS}
    for key in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        body = planets.get(key)
        if not isinstance(body, dict):
            continue
        meta = SIGNS.get(str(body.get("sign") or "").lower())
        if meta:
            counts[meta[2]] += 1
    if not any(counts.values()):
        return None
    return max(counts, key=counts.get)


def _house_for_lon(lon: float, cusps: list[float]) -> int | None:
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
    return None


def format_overlays(chart_a: dict[str, Any], chart_b: dict[str, Any]) -> str:
    cusps = chart_a.get("cusps") or []
    try:
        cusps_f = [float(x) for x in cusps[:12]]
    except (TypeError, ValueError):
        cusps_f = []
    pb = chart_b.get("planets") if isinstance(chart_b.get("planets"), dict) else {}
    lines = [
        "❤️ <b>OVERLAY DELLE CASE</b>",
        "<i>I pianeti dell'altra carta cadono nelle tue case (cuspidi Placidus live). "
        "Dice dove l'altra persona ti tocca, non se siete destinati.</i>",
        "",
    ]
    shown = 0
    for key, (emoji, label) in PLANET_IT.items():
        lon = body_lon(pb.get(key))
        house = _house_for_lon(lon, cusps_f) if lon is not None else None
        if house is None:
            continue
        lines.append(f"{emoji} <b>{label}</b> dell'altra → casa {house} ({HOUSE_IT[house]})")
        shown += 1
    if shown == 0:
        lines.append("Non ho abbastanza cuspidi per l'overlay. Riprova la sinastria con ora e luogo.")
    lines.extend(
        [
            "",
            "<i>Overlay da efemeridi e case Placidus. Tradizione, non un verdetto.</i>",
        ]
    )
    return "\n".join(lines)


COMPAT_SLOTS = {
    "signs": (("a", "il tuo Sole"), ("b", "il Sole dell'altra persona")),
    "moon": (("a", "la tua Luna"), ("b", "la Luna dell'altra persona")),
    "asc": (("a", "il tuo Ascendente"), ("b", "l'Ascendente dell'altra")),
    "merc": (("a", "il tuo Mercurio"), ("b", "il Mercurio dell'altra")),
    "vm": (
        ("av", "la tua Venere"),
        ("am", "il tuo Marte"),
        ("bv", "la Venere dell'altra"),
        ("bm", "il Marte dell'altra"),
    ),
    "b3": (
        ("as", "il tuo Sole"),
        ("am", "la tua Luna"),
        ("aa", "il tuo Ascendente"),
        ("bs", "il Sole dell'altra"),
        ("bm", "la Luna dell'altra"),
        ("ba", "l'Ascendente dell'altra"),
    ),
}

MINE_FILL = {
    "signs": {"a": "sun"},
    "moon": {"a": "moon"},
    "asc": {"a": "asc"},
    "merc": {"a": "merc"},
    "vm": {"av": "venus", "am": "mars"},
    "b3": {"as": "sun", "am": "moon", "aa": "asc"},
}


def body_lon(body: dict[str, Any] | None) -> float | None:
    if not isinstance(body, dict):
        return None
    sign = str(body.get("sign") or "").lower()
    if sign not in SIGNS:
        return None
    try:
        deg = float(body.get("degInSign") or 0)
    except (TypeError, ValueError):
        deg = 0.0
    return SIGN_ORDER.index(sign) * 30.0 + deg


def _delta(a: float, b: float) -> float:
    raw = abs((a - b) % 360.0)
    return min(raw, 360.0 - raw)


def _aspect(delta: float) -> tuple[str, str, float] | None:
    for exact, name, glyph, orb in ASPECT_ORBS:
        off = abs(delta - exact)
        if off <= orb:
            return name, glyph, off
    return None


def format_synastry(
    chart_a: dict[str, Any],
    chart_b: dict[str, Any],
    *,
    name_a: str,
    name_b: str,
) -> str:
    pa = chart_a.get("planets") if isinstance(chart_a.get("planets"), dict) else {}
    pb = chart_b.get("planets") if isinstance(chart_b.get("planets"), dict) else {}
    lines = [
        "❤️ <b>SINASTRIA</b>",
        f"<b>Tu</b> — {name_a}",
        f"<b>Altra persona</b> — {name_b}",
        "",
        "Posizioni live (CosmyDay / Swiss Ephemeris).",
        "",
    ]
    for key in ("Sun", "Moon", "Venus", "Mars"):
        ba, bb = pa.get(key), pb.get(key)
        if not isinstance(ba, dict) or not isinstance(bb, dict):
            continue
        emoji, label = PLANET_IT[key]
        sa = str(ba.get("sign") or "")
        sb = str(bb.get("sign") or "")
        meta_a = SIGNS.get(sa.lower())
        meta_b = SIGNS.get(sb.lower())
        la = f"{meta_a[1]} {meta_a[0]}" if meta_a else sa
        lb = f"{meta_b[1]} {meta_b[0]}" if meta_b else sb
        lines.append(f"{emoji} <b>{label}</b>  tu {la}  ·  altra {lb}")
    lines.extend(
        [
            "",
            "⚡ <b>Aspetti tra le due carte</b>",
            "Ricostruiti da segno + grado, orb come nel tema.",
        ]
    )
    shown = 0
    for ka, kb in SYNASTRY_PAIRS:
        lon_a, lon_b = body_lon(pa.get(ka)), body_lon(pb.get(kb))
        if lon_a is None or lon_b is None:
            continue
        hit = _aspect(_delta(lon_a, lon_b))
        if not hit:
            continue
        name, glyph, orb = hit
        ea, la = PLANET_IT[ka]
        eb, lb = PLANET_IT[kb]
        lines.append(f"{ea} {la} (tu) {glyph} {eb} {lb} (altra) — {name}, orb {orb:.1f}°")
        shown += 1
        if shown >= 8:
            break
    if shown == 0:
        lines.append("Nessun aspetto stretto tra Sole, Luna, Mercurio, Venere, Marte.")
    lines.extend(
        [
            "",
            "<i>Sinastria da efemeridi live, letta in chiave tradizionale. "
            "Non è una previsione e non sostituisce due persone che si parlano.</i>",
        ]
    )
    return "\n".join(lines)
