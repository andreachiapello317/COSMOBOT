"""Etichette italiane per token che arrivano in inglese dalle API. Non inventa misure."""

from __future__ import annotations

import re

COMPASS_IT = {
    "N": "Nord",
    "NNE": "Nord-nord-est",
    "NE": "Nord-est",
    "ENE": "Est-nord-est",
    "E": "Est",
    "ESE": "Est-sud-est",
    "SE": "Sud-est",
    "SSE": "Sud-sud-est",
    "S": "Sud",
    "SSW": "Sud-sud-ovest",
    "SW": "Sud-ovest",
    "WSW": "Ovest-sud-ovest",
    "W": "Ovest",
    "WNW": "Ovest-nord-ovest",
    "NW": "Nord-ovest",
    "NNW": "Nord-nord-ovest",
}

STAR_IT = {
    "sirius": "Sirio",
    "vega": "Vega",
    "betelgeuse": "Betelgeuse",
    "rigel": "Rigel",
    "polaris": "Stella Polare",
    "capella": "Capella",
    "altair": "Altair",
    "aldebaran": "Aldebaran",
    "antares": "Antares",
    "arcturus": "Arcturo",
    "deneb": "Deneb",
    "canopus": "Canopo",
    "procyon": "Procione",
    "spica": "Spica",
    "fomalhaut": "Fomalhaut",
    "pollux": "Polluce",
    "castor": "Castore",
    "regulus": "Regolo",
    "bellatrix": "Bellatrix",
    "proxima centauri": "Proxima Centauri",
}

DISCOVERY_IT = {
    "transit": "Transito",
    "radial velocity": "Velocità radiale",
    "imaging": "Immagine diretta",
    "microlensing": "Microlensing",
    "eclipse timing variations": "Variazioni dei tempi di eclisse",
    "transit timing variations": "Variazioni dei tempi di transito",
    "orbital brightness modulation": "Modulazione di luminosità",
    "pulsar timing": "Tempi di pulsar",
    "astrometry": "Astrometria",
    "disk kinematics": "Cinematica del disco",
}

KP_IT = {
    "quiet": "Calmo",
    "unsettled": "Instabile",
    "active": "Attivo",
    "minor storm": "Tempesta minore",
    "major storm": "Tempesta maggiore",
    "severe storm": "Tempesta grave",
    "extreme storm": "Tempesta estrema",
}

_EVENT_PHRASES = (
    ("September Equinox", "Equinozio di settembre"),
    ("March Equinox", "Equinozio di marzo"),
    ("June Solstice", "Solstizio di giugno"),
    ("December Solstice", "Solstizio di dicembre"),
    ("Autumnal Equinox", "Equinozio d'autunno"),
    ("Vernal Equinox", "Equinozio di primavera"),
    ("Summer Solstice", "Solstizio d'estate"),
    ("Winter Solstice", "Solstizio d'inverno"),
    ("Solar Eclipse", "Eclissi solare"),
    ("Lunar Eclipse", "Eclissi lunare"),
    ("Blue Moon", "Luna blu"),
    ("Super Moon", "Superluna"),
    ("Supermoon", "Superluna"),
    ("Full Moon", "Luna piena"),
    ("New Moon", "Luna nuova"),
    ("First Quarter", "Primo quarto"),
    ("Last Quarter", "Ultimo quarto"),
    ("Third Quarter", "Ultimo quarto"),
    ("Penumbral", "Penombrale"),
    ("Annular", "Anulare"),
    ("Partial", "Parziale"),
    ("Hybrid", "Ibrida"),
    ("Total", "Totale"),
)


def compass_it(raw: str | None) -> str:
    token = str(raw or "").strip().upper()
    if not token:
        return ""
    if token in COMPASS_IT:
        return COMPASS_IT[token]
    return " ".join(COMPASS_IT.get(part, part) for part in token.replace("-", " ").split())


def star_it(raw: str | None) -> str:
    name = str(raw or "").strip()
    if not name:
        return "—"
    return STAR_IT.get(name.lower(), name)


def discovery_it(raw: str | None) -> str:
    text = str(raw or "").strip()
    if not text or text == "—":
        return "—"
    return DISCOVERY_IT.get(text.lower(), text)


def kp_label_it(raw: str | None) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    return KP_IT.get(text.lower(), text)


def event_name_it(raw: str | None) -> str:
    text = str(raw or "").strip()
    if not text:
        return "—"
    out = text
    for english, italian in _EVENT_PHRASES:
        out = re.sub(re.escape(english), italian, out, flags=re.IGNORECASE)
    return out
