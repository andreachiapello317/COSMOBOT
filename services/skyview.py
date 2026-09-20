"""Mappa testuale del cielo da numeri live skymap.sh. Nessuna posizione inventata."""

from __future__ import annotations

from typing import Any

from services.i18n import compass_it, star_it

PLANET_EMOJI = {
    "Sun": "☀️",
    "Moon": "🌙",
    "Mercury": "☿️",
    "Venus": "♀️",
    "Mars": "♂️",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "🧊",
}

PLANET_IT = {
    "Sun": "Sole",
    "Moon": "Luna",
    "Mercury": "Mercurio",
    "Venus": "Venere",
    "Mars": "Marte",
    "Jupiter": "Giove",
    "Saturn": "Saturno",
    "Uranus": "Urano",
    "Neptune": "Nettuno",
    "Pluto": "Plutone",
}


def _alt(item: dict[str, Any]) -> float | None:
    raw = item.get("alt")
    try:
        return float(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def _az(item: dict[str, Any]) -> float | None:
    raw = item.get("az")
    if raw is None:
        compass = str(item.get("compass") or "").upper()
        table = {
            "N": 0, "NNE": 22, "NE": 45, "ENE": 67, "E": 90, "ESE": 112,
            "SE": 135, "SSE": 157, "S": 180, "SSW": 202, "SW": 225,
            "WSW": 247, "W": 270, "WNW": 292, "NW": 315, "NNW": 337,
        }
        return float(table[compass]) if compass in table else None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _mag(item: dict[str, Any]) -> float | None:
    raw = item.get("mag")
    try:
        return float(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def collect_marks(sky: dict[str, Any]) -> list[dict[str, Any]]:
    marks: list[dict[str, Any]] = []
    moon = sky.get("moon") if isinstance(sky.get("moon"), dict) else None
    if moon:
        marks.append(
            {
                "name": "Luna",
                "emoji": "🌙",
                "alt": _alt(moon),
                "az": _az(moon),
                "compass": compass_it(str(moon.get("compass") or "")),
                "mag": None,
                "kind": "moon",
            }
        )
    for body in sky.get("bodies") or []:
        if not isinstance(body, dict) or not body.get("name"):
            continue
        raw = str(body["name"])
        marks.append(
            {
                "name": PLANET_IT.get(raw, raw),
                "emoji": PLANET_EMOJI.get(raw, "🪐"),
                "alt": _alt(body),
                "az": _az(body),
                "compass": compass_it(str(body.get("compass") or "")),
                "mag": _mag(body),
                "kind": "planet",
            }
        )
    for star in (sky.get("brightest") or [])[:6]:
        if not isinstance(star, dict) or not star.get("name"):
            continue
        marks.append(
            {
                "name": star_it(str(star["name"])),
                "emoji": "⭐",
                "alt": _alt(star),
                "az": _az(star),
                "compass": compass_it(str(star.get("compass") or "")),
                "mag": _mag(star),
                "kind": "star",
            }
        )
    return marks


def visibility_line(mark: dict[str, Any]) -> str:
    alt = mark.get("alt")
    mag = mark.get("mag")
    if alt is None:
        state = "—"
    elif alt > 0:
        eye = " 👁 visibile" if mag is None or mag <= 6.0 else " (debole)"
        state = f"↑ {alt:.0f}° {mark.get('compass') or ''}{eye}"
    else:
        state = f"↓ sotto l'orizzonte ({alt:.0f}°)"
    mag_bit = f" · magnitudine {mag:.1f}" if isinstance(mag, float) else ""
    return f"{mark['emoji']} {mark['name']} — {state}{mag_bit}"


def text_sky_map(marks: list[dict[str, Any]]) -> str:
    """Griglia 4×5 da altezza e azimut live."""
    up = [m for m in marks if isinstance(m.get("alt"), (int, float)) and m["alt"] > 0]
    down = [m for m in marks if isinstance(m.get("alt"), (int, float)) and m["alt"] <= 0]
    if not up and not down:
        return ""
    grid = [["" for _ in range(5)] for _ in range(4)]

    def row_for(alt: float) -> int:
        if alt >= 50:
            return 0
        if alt >= 28:
            return 1
        if alt >= 12:
            return 2
        return 3

    def col_for(az: float | None) -> int:
        if az is None:
            return 2
        # 0=N → colonna 2 in alto concettuale; usiamo W…E
        # col 0 ≈ W (247-312), 1 ≈ SW/NW, 2 ≈ S/N mix, 3 ≈ SE/NE, 4 ≈ E
        if 247 <= az < 312:
            return 0
        if 202 <= az < 247 or 312 <= az < 337:
            return 1
        if 157 <= az < 202 or az >= 337 or az < 22:
            return 2
        if 112 <= az < 157 or 22 <= az < 67:
            return 3
        return 4

    for mark in sorted(up, key=lambda item: -float(item["alt"])):
        r = row_for(float(mark["alt"]))
        c = col_for(mark.get("az") if isinstance(mark.get("az"), (int, float)) else None)
        label = f"{mark['emoji']}{mark['name']}"
        if not grid[r][c]:
            grid[r][c] = label
        elif len(grid[r][c]) < 18:
            grid[r][c] = grid[r][c] + " " + mark["emoji"]

    lines = ["      W          ·          E", ""]
    for row in grid:
        cells = [((cell or "·")[:16]).ljust(16) for cell in row]
        lines.append("".join(cells).rstrip())
    lines.append("──────── orizzonte ────────")
    if down:
        bits = "  ".join(f"{m['emoji']}{m['name']}↓" for m in down[:4])
        lines.append(bits)
    return "\n".join(lines)


def angular_sep_deg(
    alt1: float,
    az1: float,
    alt2: float,
    az2: float,
) -> float:
    """Separazione angolare in gradi da altezza e azimut. Geometria, non un oracolo."""
    from math import acos, cos, radians, sin

    a1, z1, a2, z2 = (radians(float(v)) for v in (alt1, az1, alt2, az2))
    cos_c = sin(a1) * sin(a2) + cos(a1) * cos(a2) * cos(z1 - z2)
    cos_c = max(-1.0, min(1.0, cos_c))
    return float(acos(cos_c) * 180.0 / 3.141592653589793)


def milky_way_hint(*, sun_alt: float | None, moon_alt: float | None, moon_illum: float | None) -> str:
    """Stima da Sole/Luna live, non un indice Bortle."""
    if sun_alt is None:
        return "Via Lattea — serve il Sole sotto l'orizzonte; dato solare assente."
    if sun_alt > -12:
        return "Via Lattea — cielo ancora chiaro: att condizionate dal Sole."
    moon_up = isinstance(moon_alt, (int, float)) and moon_alt > 0
    bright = isinstance(moon_illum, (int, float)) and moon_illum >= 60
    if moon_up and bright:
        return "Via Lattea — Luna alta e luminosa: contrasto basso (stima da fase/altezza)."
    if sun_alt <= -18 and not (moon_up and bright):
        return "Via Lattea — notte astronomica e Luna debole/assente: condizioni migliori (stima Sole/Luna)."
    return "Via Lattea — crepuscolo astronomico o Luna presente: contrasto medio (stima Sole/Luna)."
