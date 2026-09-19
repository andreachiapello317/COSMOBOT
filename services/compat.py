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


def format_sign_compat(a: str, b: str) -> str:
    ia, ea, ela, mda = SIGNS[a]
    ib, eb, elb, mdb = SIGNS[b]
    diff = abs(SIGN_ORDER.index(a) - SIGN_ORDER.index(b))
    steps = min(diff % 12, 12 - (diff % 12))
    ang_name, glyph, ang_note = SIGN_ANGLE[steps]
    same_mode = "stessa modalità" if mda == mdb else f"{mda} + {mdb}"
    return "\n".join(
        [
            "❤️ <b>COMPATIBILITÀ</b>",
            f"{ea} <b>{ia}</b>  ·  {eb} <b>{ib}</b>",
            "",
            f"Elementi: {ela} + {elb}",
            _pair_note(ela, elb),
            "",
            f"Modalità: {same_mode}",
            f"Angolo tra i segni: {glyph} {ang_name} ({steps * 30}°)",
            ang_note,
            "",
            "<i>Lettura tradizionale dei segni. Non è astronomia, non è un verdetto "
            "e non assegno percentuali. Due persone sono più dei due Soli.</i>",
        ]
    )


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
