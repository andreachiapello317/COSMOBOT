"""Carta celeste PNG: stelle Hipparcos + pianeti/Luna da Astronomy Engine."""

from __future__ import annotations

import html as _html
import math
from datetime import datetime, timezone
from io import BytesIO
from typing import Any

import astronomy
from PIL import Image, ImageDraw, ImageFont

from services.moon import moon_now
from services.skycatalog import SkyFrame, constellation_segments, visible_stars

SIZE = 920
MARGIN = 78
PLANETS = (
    (astronomy.Body.Mercury, "Mercurio", (180, 180, 180)),
    (astronomy.Body.Venus, "Venere", (240, 220, 140)),
    (astronomy.Body.Mars, "Marte", (220, 110, 80)),
    (astronomy.Body.Jupiter, "Giove", (230, 190, 130)),
    (astronomy.Body.Saturn, "Saturno", (210, 190, 140)),
    (astronomy.Body.Uranus, "Urano", (140, 200, 210)),
    (astronomy.Body.Neptune, "Nettuno", (90, 130, 210)),
)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _star_color(bv: Any) -> tuple[int, int, int]:
    try:
        value = float(bv)
    except (TypeError, ValueError):
        return (230, 232, 245)
    if value < 0.0:
        return (170, 200, 255)
    if value < 0.35:
        return (220, 230, 255)
    if value < 0.7:
        return (255, 244, 214)
    if value < 1.2:
        return (255, 210, 150)
    return (255, 170, 120)


def _xy(alt: float, az: float, cx: float, cy: float, radius: float) -> tuple[float, float]:
    r = ((90.0 - alt) / 90.0) * radius
    theta = math.radians(az)
    return cx + r * math.sin(theta), cy - r * math.cos(theta)


def _clip(alt: float, az: float, cx: float, cy: float, radius: float) -> tuple[int, int] | None:
    if alt < -1:
        return None
    x, y = _xy(max(alt, 0.0), az, cx, cy, radius)
    return int(x), int(y)


def draw_sky_chart(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> bytes:
    frame = SkyFrame(lat, lon, when)
    stars = visible_stars(frame)
    figures = constellation_segments(frame)
    img = Image.new("RGB", (SIZE, SIZE + 70), (8, 12, 22))
    draw = ImageDraw.Draw(img)
    cx = cy = SIZE / 2
    radius = SIZE / 2 - MARGIN
    title_font = _font(22)
    small = _font(15)
    tiny = _font(13)

    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(10, 16, 32),
        outline=(70, 90, 130),
        width=2,
    )
    for alt in (0, 30, 60):
        r = ((90.0 - alt) / 90.0) * radius
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(40, 55, 85))
        if alt:
            draw.text((cx + 6, cy - r - 12), f"{alt}°", fill=(90, 110, 150), font=tiny)
    for az in range(0, 360, 45):
        x, y = _xy(0, az, cx, cy, radius)
        draw.line((cx, cy, x, y), fill=(32, 44, 70), width=1)

    labels = (("N", 0), ("E", 90), ("S", 180), ("O", 270))
    for text, az in labels:
        x, y = _xy(-8, az, cx, cy, radius)
        box = draw.textbbox((0, 0), text, font=title_font)
        draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2), text, fill=(200, 210, 230), font=title_font)

    for fig in figures:
        for seg in fig["segs"]:
            pts: list[tuple[int, int]] = []
            for alt, az in seg:
                point = _clip(alt, az, cx, cy, radius)
                if point:
                    pts.append(point)
            if len(pts) >= 2:
                draw.line(pts, fill=(70, 95, 140), width=1)
        vis = [p for seg in fig["segs"] for p in seg if p[0] > 12]
        if vis and fig["alt"] > 25:
            mid_alt = sum(p[0] for p in vis) / len(vis)
            mid_az = sum(p[1] for p in vis) / len(vis)
            pos = _clip(mid_alt, mid_az, cx, cy, radius)
            if pos:
                draw.text((pos[0] + 3, pos[1] + 3), fig["name"], fill=(130, 155, 190), font=tiny)

    for star in stars:
        pos = _clip(star["alt"], star["az"], cx, cy, radius)
        if not pos:
            continue
        mag = float(star["mag"])
        rad = max(1.0, 5.6 - mag)
        color = _star_color(star.get("bv"))
        draw.ellipse(
            (pos[0] - rad, pos[1] - rad, pos[0] + rad, pos[1] + rad),
            fill=color,
        )
        if star["name"] and mag <= 1.6:
            draw.text((pos[0] + 5, pos[1] - 7), star["name"], fill=(220, 225, 235), font=tiny)

    sun_alt, sun_az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    if sun_alt > -0.5:
        pos = _clip(sun_alt, sun_az, cx, cy, radius)
        if pos:
            draw.ellipse((pos[0] - 10, pos[1] - 10, pos[0] + 10, pos[1] + 10), fill=(255, 210, 70))
            draw.text((pos[0] + 12, pos[1] - 8), "Sole", fill=(255, 220, 120), font=small)

    moon_alt, moon_az, _ra, _dec = frame.body_altaz(astronomy.Body.Moon)
    if moon_alt > -0.5:
        pos = _clip(moon_alt, moon_az, cx, cy, radius)
        if pos:
            phase = moon_now(frame.when)
            draw.ellipse((pos[0] - 8, pos[1] - 8, pos[0] + 8, pos[1] + 8), fill=(230, 230, 210))
            illum = phase.get("illum")
            if isinstance(illum, (int, float)) and illum < 95:
                shift = int(8 * (1 - illum / 100.0))
                draw.ellipse(
                    (pos[0] - 8 + shift, pos[1] - 8, pos[0] + 8 + shift, pos[1] + 8),
                    fill=(10, 16, 32),
                )
            draw.text((pos[0] + 11, pos[1] - 8), "Luna", fill=(230, 230, 200), font=small)

    for body, label, color in PLANETS:
        alt, az, _ra, _dec = frame.body_altaz(body)
        if alt <= 0:
            continue
        pos = _clip(alt, az, cx, cy, radius)
        if not pos:
            continue
        draw.ellipse((pos[0] - 5, pos[1] - 5, pos[0] + 5, pos[1] + 5), fill=color, outline=(255, 255, 255))
        draw.text((pos[0] + 7, pos[1] - 8), label, fill=color, font=small)

    local = when
    draw.rectangle((0, SIZE, SIZE, SIZE + 70), fill=(8, 12, 22))
    draw.text((24, SIZE + 10), f"Cielo di adesso · {place}", fill=(235, 238, 245), font=title_font)
    draw.text(
        (24, SIZE + 38),
        f"{local.strftime('%d/%m/%Y %H:%M')} · N in alto · stelle Hipparcos · pianeti Astronomy Engine",
        fill=(150, 165, 190),
        font=tiny,
    )
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


SKY_STYLES = ("classic", "figures", "atlas")
SKY_STYLE_LABELS = {
    "classic": "Classica",
    "figures": "Figure",
    "atlas": "Atlante",
}


def sky_style_label(style: str) -> str:
    return SKY_STYLE_LABELS.get(style, "Classica")


EMOJI_PLANETS = (
    (astronomy.Body.Mercury, "Mercurio", "☿"),
    (astronomy.Body.Venus, "Venere", "♀"),
    (astronomy.Body.Mars, "Marte", "♂"),
    (astronomy.Body.Jupiter, "Giove", "♃"),
    (astronomy.Body.Saturn, "Saturno", "🪐"),
    (astronomy.Body.Uranus, "Urano", "♅"),
    (astronomy.Body.Neptune, "Nettuno", "♆"),
)
_ZODIAC_MARK = {
    "Ari": "♈",
    "Tau": "♉",
    "Gem": "♊",
    "Cnc": "♋",
    "Leo": "♌",
    "Vir": "♍",
    "Lib": "♎",
    "Sco": "♏",
    "Sgr": "♐",
    "Cap": "♑",
    "Aqr": "♒",
    "Psc": "♓",
}
_STAR_PRI = {" ": 0, "·": 1, "─": 2, "│": 2, "╱": 2, "╲": 2, "✦": 3, "⭐": 4, "✨": 5}


def _grid_cell(alt: float, az: float, cols: int, rows: int) -> tuple[int, int] | None:
    if alt <= 0:
        return None
    radius = min(cols, rows) / 2.0 - 0.7
    r = ((90.0 - alt) / 90.0) * radius
    theta = math.radians(az)
    x = (cols - 1) / 2.0 + r * math.sin(theta)
    y = (rows - 1) / 2.0 - r * math.cos(theta)
    ix, iy = int(round(x)), int(round(y))
    if 0 <= ix < cols and 0 <= iy < rows:
        return ix, iy
    return None


def _bresenham(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    x, y = x0, y0
    while True:
        cells.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return cells


def _line_glyph(x0: int, y0: int, x1: int, y1: int) -> str:
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) >= 2 * max(1, abs(dy)):
        return "─"
    if abs(dy) >= 2 * max(1, abs(dx)):
        return "│"
    if dx * dy > 0:
        return "╲"
    return "╱"


def _put(grid: list[list[str]], x: int, y: int, glyph: str, *, force: bool = False) -> None:
    if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
        return
    current = grid[y][x]
    if force or _STAR_PRI.get(glyph, 9) >= _STAR_PRI.get(current, 0):
        if current in {"☀️", "🌙", "🪐", "☿", "♀", "♂", "♃", "♄", "♅", "♆"} and not force:
            return
        if current in {"✨", "⭐"} and glyph in {"✦", "·", "─", "│", "╱", "╲"}:
            return
        grid[y][x] = glyph


def _visible_bodies(frame: SkyFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sun_alt, sun_az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    rows.append({"kind": "sun", "name": "Sole", "glyph": "☀️", "alt": sun_alt, "az": sun_az, "mag": -26.7})
    moon = moon_now(frame.when)
    moon_alt, moon_az, _ra, _dec = frame.body_altaz(astronomy.Body.Moon)
    rows.append(
        {
            "kind": "moon",
            "name": str(moon.get("name") or "Luna"),
            "glyph": str(moon.get("emoji") or "🌙"),
            "alt": moon_alt,
            "az": moon_az,
            "mag": None,
            "illum": moon.get("illum"),
        }
    )
    for body, name, glyph in EMOJI_PLANETS:
        alt, az, _ra, _dec = frame.body_altaz(body)
        rows.append({"kind": "planet", "name": name, "glyph": glyph, "alt": alt, "az": az, "mag": None})
    return rows


def format_emoji_planetarium(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> str:
    """Planetario testuale: pochi oggetti, linee, nomi. Non una griglia piena."""
    place = _html.escape(place)
    frame = SkyFrame(lat, lon, when)
    cols, rows = 25, 14
    grid = [[" " for _ in range(cols)] for _ in range(rows)]
    catalog = visible_stars(frame)
    stars = [star for star in catalog if float(star["mag"]) <= 3.4][:22]
    faint = [star for star in catalog if 3.4 < float(star["mag"]) <= 3.9][:18]
    figures = constellation_segments(frame)
    bodies = [row for row in _visible_bodies(frame) if row["alt"] > 0]

    for fig in figures[:10]:
        for seg in fig["segs"]:
            cells: list[tuple[int, int]] = []
            for alt, az in seg:
                pos = _grid_cell(alt, az, cols, rows)
                if pos:
                    cells.append(pos)
            for (x0, y0), (x1, y1) in zip(cells, cells[1:]):
                path = _bresenham(x0, y0, x1, y1)
                if 2 <= len(path) <= 6:
                    mark = _line_glyph(x0, y0, x1, y1)
                    for x, y in path[1:-1]:
                        _put(grid, x, y, mark)

    for star in reversed(stars):
        pos = _grid_cell(star["alt"], star["az"], cols, rows)
        if not pos:
            continue
        mag = float(star["mag"])
        glyph = "✨" if mag <= 0.4 else "⭐" if mag <= 1.5 else "✦" if mag <= 2.6 else "·"
        _put(grid, pos[0], pos[1], glyph)
    for star in faint:
        pos = _grid_cell(star["alt"], star["az"], cols, rows)
        if pos and grid[pos[1]][pos[0]] == " ":
            grid[pos[1]][pos[0]] = "·"

    for body in bodies:
        pos = _grid_cell(body["alt"], body["az"], cols, rows)
        if pos:
            _put(grid, pos[0], pos[1], str(body["glyph"]), force=True)

    named: list[str] = []
    free = {" ", "·", "─", "│", "╱", "╲"}

    def _can_write(x: int, y: int, label: str) -> bool:
        if y < 0 or y >= rows or x < 0 or x + len(label) > cols:
            return False
        return all(grid[y][x + i] in free for i in range(len(label)))

    for fig in figures:
        if fig["alt"] < 28 or len(named) >= 5:
            continue
        vis = [p for seg in fig["segs"] for p in seg if p[0] > 12]
        if len(vis) < 3:
            continue
        mid_alt = sum(p[0] for p in vis) / len(vis)
        mid_az = sum(p[1] for p in vis) / len(vis)
        pos = _grid_cell(mid_alt, mid_az, cols, rows)
        if not pos:
            named.append(fig["name"])
            continue
        mark = _ZODIAC_MARK.get(str(fig.get("id") or ""), "")
        label = f"{mark}{fig['name']}".upper()
        x, y = pos
        slot = None
        for dy, dx in ((0, 0), (-1, 0), (1, 0), (0, -2), (0, 2), (-1, -2)):
            nx, ny = x + dx, y + dy
            if nx + len(label) > cols:
                nx = max(0, cols - len(label))
            if _can_write(nx, ny, label):
                slot = (nx, ny)
                break
        if slot:
            nx, ny = slot
            for i, ch in enumerate(label):
                grid[ny][nx + i] = ch
        named.append(fig["name"])

    zenith = _grid_cell(89.5, 0, cols, rows)
    if zenith and grid[zenith[1]][zenith[0]] == " ":
        grid[zenith[1]][zenith[0]] = "+"

    lines = ["".join(row).rstrip() for row in grid]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    compass = ["     ─────────", "        N", "     O  +  E", "        S"]
    on_map = "   ".join(f"{row['glyph']} {row['name']}" for row in bodies)
    above = " · ".join(named[:6])
    return "\n".join(
        [
            f"🌌 <b>CIELO DI ADESSO</b>",
            f"📍 {place} · {when.strftime('%d/%m %H:%M')}",
            "",
            "<pre>" + "\n".join(lines + [""] + compass) + "</pre>",
            "",
            on_map or "Nessun pianeta sopra l'orizzonte.",
            f"Figure: {above}" if above else "",
            "",
            "✨ più luminosa · ⭐ · ✦ · · più debole",
            "<i>N in alto. Hipparcos + Astronomy Engine. Planetario in chat, non la PNG.</i>",
        ]
    ).replace("\n\n\n", "\n\n")


def format_sky_listing(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> str:
    """Elenco numerico degli oggetti sopra l'orizzonte."""
    place = _html.escape(place)
    frame = SkyFrame(lat, lon, when)
    stars = visible_stars(frame, limit=12)
    figures = [fig["name"] for fig in constellation_segments(frame) if fig["alt"] > 20][:8]
    lines = [
        f"📜 <b>OGGETTI SOPRA — {place.upper()}</b>",
        f"{when.strftime('%d/%m/%Y %H:%M')}",
        "",
        "☀️ <b>SOLE, LUNA, PIANETI</b>",
    ]
    bodies = _visible_bodies(frame)
    bodies.sort(key=lambda row: row["alt"], reverse=True)
    any_up = False
    for row in bodies:
        if row["alt"] <= 0:
            continue
        any_up = True
        extra = ""
        if isinstance(row.get("illum"), (int, float)):
            extra = f" · ill. {row['illum']:.0f}%"
        lines.append(
            f"{row['glyph']} {row['name']}  alt {row['alt']:.0f}° · az {row['az']:.0f}°{extra}"
        )
    if not any_up:
        lines.append("<i>Sole, Luna e pianeti sono tutti sotto l'orizzonte.</i>")
    lines.extend(["", "⭐ <b>STELLE PIÙ LUMINOSE</b>"])
    if stars:
        for star in stars:
            label = _html.escape(str(star["name"] or f"mag {star['mag']:.1f}"))
            lines.append(
                f"⭐ {label}  mag {star['mag']:.1f} · alt {star['alt']:.0f}° · az {star['az']:.0f}°"
            )
    else:
        lines.append("<i>Nessuna stella del catalogo è sopra.</i>")
    if figures:
        lines.extend(["", "✨ <b>FIGURE ALTE</b>", " · ".join(_html.escape(n) for n in figures)])
    lines.extend(
        [
            "",
            "<i>Altezza e azimut da Astronomy Engine. Stelle Hipparcos mag ≤ 5.2. "
            "Non è Horizons.</i>",
        ]
    )
    return "\n".join(lines)


def format_emoji_sky(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> str:
    return format_emoji_planetarium(place=place, lat=lat, lon=lon, when=when)


def _wrap_ra(ra_deg: float, center: float) -> float:
    return ((float(ra_deg) - float(center) + 540.0) % 360.0) - 180.0


def draw_atlas_chart(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> bytes:
    """Carta equatoriale da atlante: RA cresce a sinistra, griglia in ore e gradi."""
    from services.skycatalog import constellation_name, load_catalog

    frame = SkyFrame(lat, lon, when)
    center = (frame.lst * 15.0) % 360.0
    ra_half = 90.0
    dec_lo = max(-80.0, lat - 88.0)
    dec_hi = min(88.0, lat + 88.0)
    width, height, footer = 1180, 720, 68
    left, right, top, bottom = 58, 24, 28, 28
    img = Image.new("RGB", (width, height + footer), (7, 9, 14))
    draw = ImageDraw.Draw(img)
    title_font = _font(20)
    small = _font(14)
    tiny = _font(12)
    plot_w = width - left - right
    plot_h = height - top - bottom

    def xy(ra_deg: float, dec_deg: float) -> tuple[float, float] | None:
        wrapped = _wrap_ra(ra_deg, center)
        if abs(wrapped) > ra_half + 2 or dec_deg < dec_lo - 2 or dec_deg > dec_hi + 2:
            return None
        x = left + (0.5 - wrapped / (2 * ra_half)) * plot_w
        y = top + (dec_hi - dec_deg) / (dec_hi - dec_lo) * plot_h
        return x, y

    draw.rectangle((left, top, left + plot_w, top + plot_h), fill=(9, 12, 20), outline=(70, 88, 118))
    for dec in range(int(math.floor(dec_lo / 10.0) * 10), int(dec_hi) + 1, 10):
        a = xy(center - ra_half, dec)
        b = xy(center + ra_half, dec)
        if not a or not b:
            continue
        color = (90, 110, 145) if dec == 0 else (32, 42, 62)
        draw.line((a[0], a[1], b[0], b[1]), fill=color, width=2 if dec == 0 else 1)
        draw.text((10, a[1] - 7), f"{dec:+d}°", fill=(150, 165, 190), font=tiny)
    for hour in range(-6, 7):
        ra = (center + hour * 15.0) % 360.0
        a = xy(ra, dec_lo)
        b = xy(ra, dec_hi)
        if not a or not b:
            continue
        draw.line((a[0], top, b[0], top + plot_h), fill=(32, 42, 62))
        label = f"{int((ra / 15.0) % 24):02d}h"
        draw.text((b[0] - 12, 8), label, fill=(150, 165, 190), font=tiny)

    rot = astronomy.Rotation_ECL_EQJ()
    ecl: list[tuple[float, float]] = []
    for lon_deg in range(0, 361, 2):
        vec = astronomy.VectorFromSphere(astronomy.Spherical(0.0, float(lon_deg), 1.0), frame.moment)
        eq = astronomy.EquatorFromVector(astronomy.RotateVector(rot, vec))
        point = xy(float(eq.ra) * 15.0, float(eq.dec))
        if point:
            ecl.append(point)
        elif len(ecl) >= 2:
            draw.line(ecl, fill=(150, 120, 60), width=2)
            ecl = []
    if len(ecl) >= 2:
        draw.line(ecl, fill=(150, 120, 60), width=2)

    catalog = load_catalog()
    for fig in catalog.get("lines") or []:
        name = constellation_name(str(fig.get("id") or ""))
        named = False
        for seg in fig.get("s") or []:
            pts: list[tuple[float, float]] = []
            for point in seg:
                if len(point) < 2:
                    continue
                ra, dec = float(point[0]), float(point[1])
                alt, _az = frame.altaz(ra, dec)
                mapped = xy(ra, dec)
                if mapped and alt > -2:
                    pts.append(mapped)
            if len(pts) >= 2:
                chunk = [pts[0]]
                for prev, cur in zip(pts, pts[1:]):
                    if abs(cur[0] - prev[0]) > plot_w * 0.45:
                        if len(chunk) >= 2:
                            draw.line(chunk, fill=(72, 96, 132), width=1)
                        chunk = [cur]
                    else:
                        chunk.append(cur)
                if len(chunk) >= 2:
                    draw.line(chunk, fill=(72, 96, 132), width=1)
                if not named:
                    mid = pts[len(pts) // 2]
                    draw.text((mid[0] + 3, mid[1] + 2), name, fill=(140, 160, 190), font=tiny)
                    named = True

    for item in catalog["stars"]:
        ra, dec, mag = float(item[0]), float(item[1]), float(item[2])
        extra = item[3] if len(item) > 3 and isinstance(item[3], dict) else {}
        alt, _az = frame.altaz(ra, dec)
        if alt <= 0:
            continue
        pos = xy(ra, dec)
        if not pos:
            continue
        rad = 3.4 if mag < 0.2 else 2.6 if mag < 1.2 else 1.8 if mag < 2.4 else 1.2 if mag < 3.6 else 0.8
        x, y = pos
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=_star_color(extra.get("bv")))
        name = str(extra.get("n") or "")
        if name and mag <= 1.5:
            draw.text((x + 5, y - 7), name, fill=(220, 226, 236), font=tiny)

    for body, label, color in (
        (astronomy.Body.Sun, "Sole", (255, 214, 90)),
        (astronomy.Body.Moon, "Luna", (230, 230, 214)),
        *PLANETS,
    ):
        alt, _az, ra_h, dec = frame.body_altaz(body)
        if alt <= -0.5:
            continue
        pos = xy(float(ra_h) * 15.0, float(dec))
        if not pos:
            continue
        x, y = pos
        rad = 8 if body == astronomy.Body.Sun else 6 if body == astronomy.Body.Moon else 4
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=color, outline=(240, 240, 245))
        draw.text((x + rad + 3, y - 8), label, fill=color, font=small)

    draw.rectangle((0, height, width, height + footer), fill=(7, 9, 14))
    draw.text((20, height + 8), f"Cielo di adesso · atlante equatoriale · {place}", fill=(235, 238, 245), font=title_font)
    draw.text(
        (20, height + 36),
        f"{when.strftime('%d/%m/%Y %H:%M')} · RA a sinistra · equatore e eclittica · Hipparcos + Astronomy Engine",
        fill=(150, 165, 190),
        font=tiny,
    )
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def draw_figure_chart(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> bytes:
    """Stesso zenit della classica, ma solo le figure delle costellazioni."""
    frame = SkyFrame(lat, lon, when)
    stars = [star for star in visible_stars(frame) if float(star["mag"]) <= 4.2]
    figures = constellation_segments(frame)
    img = Image.new("RGB", (SIZE, SIZE + 70), (4, 6, 14))
    draw = ImageDraw.Draw(img)
    cx = cy = SIZE / 2
    radius = SIZE / 2 - MARGIN
    title_font = _font(22)
    small = _font(16)
    tiny = _font(14)

    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(6, 10, 22),
        outline=(90, 120, 170),
        width=3,
    )
    labels = (("N", 0), ("E", 90), ("S", 180), ("O", 270))
    for text, az in labels:
        x, y = _xy(-8, az, cx, cy, radius)
        box = draw.textbbox((0, 0), text, font=title_font)
        draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2), text, fill=(220, 230, 245), font=title_font)

    for fig in figures:
        for seg in fig["segs"]:
            pts: list[tuple[int, int]] = []
            for alt, az in seg:
                point = _clip(alt, az, cx, cy, radius)
                if point:
                    pts.append(point)
            if len(pts) >= 2:
                draw.line(pts, fill=(110, 150, 210), width=3)
        vis = [p for seg in fig["segs"] for p in seg if p[0] > 8]
        if vis and fig["alt"] > 18:
            mid_alt = sum(p[0] for p in vis) / len(vis)
            mid_az = sum(p[1] for p in vis) / len(vis)
            pos = _clip(mid_alt, mid_az, cx, cy, radius)
            if pos:
                draw.text((pos[0] + 4, pos[1] + 2), fig["name"], fill=(180, 205, 235), font=small)

    for star in stars:
        pos = _clip(star["alt"], star["az"], cx, cy, radius)
        if not pos:
            continue
        mag = float(star["mag"])
        rad = max(1.2, 5.8 - mag)
        draw.ellipse(
            (pos[0] - rad, pos[1] - rad, pos[0] + rad, pos[1] + rad),
            fill=_star_color(star.get("bv")),
        )
        if star["name"] and mag <= 1.8:
            draw.text((pos[0] + 6, pos[1] - 8), star["name"], fill=(240, 242, 250), font=tiny)

    for body, label, color in PLANETS:
        alt, az, _ra, _dec = frame.body_altaz(body)
        if alt <= 0:
            continue
        pos = _clip(alt, az, cx, cy, radius)
        if not pos:
            continue
        draw.ellipse((pos[0] - 6, pos[1] - 6, pos[0] + 6, pos[1] + 6), fill=color, outline=(255, 255, 255))
        draw.text((pos[0] + 8, pos[1] - 9), label, fill=color, font=small)

    moon_alt, moon_az, _ra, _dec = frame.body_altaz(astronomy.Body.Moon)
    if moon_alt > -0.5:
        pos = _clip(moon_alt, moon_az, cx, cy, radius)
        if pos:
            draw.ellipse((pos[0] - 8, pos[1] - 8, pos[0] + 8, pos[1] + 8), fill=(230, 230, 210))
            draw.text((pos[0] + 11, pos[1] - 8), "Luna", fill=(230, 230, 200), font=small)
    sun_alt, sun_az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    if sun_alt > -0.5:
        pos = _clip(sun_alt, sun_az, cx, cy, radius)
        if pos:
            draw.ellipse((pos[0] - 10, pos[1] - 10, pos[0] + 10, pos[1] + 10), fill=(255, 210, 70))
            draw.text((pos[0] + 12, pos[1] - 8), "Sole", fill=(255, 220, 120), font=small)

    draw.rectangle((0, SIZE, SIZE, SIZE + 70), fill=(4, 6, 14))
    draw.text((24, SIZE + 10), f"Cielo di adesso · figure · {place}", fill=(235, 238, 245), font=title_font)
    draw.text(
        (24, SIZE + 38),
        f"{when.strftime('%d/%m/%Y %H:%M')} · N in alto · costellazioni IAU · Hipparcos",
        fill=(150, 165, 190),
        font=tiny,
    )
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _season_it(when: datetime, lat: float) -> tuple[str, str]:
    north = lat >= 0
    names = (
        ("primavera", "estate", "autunno", "inverno")
        if north
        else ("autunno", "inverno", "primavera", "estate")
    )
    info = astronomy.Seasons(when.year)
    marks = (
        (info.mar_equinox, names[0], "equinozio di marzo"),
        (info.jun_solstice, names[1], "solstizio di giugno"),
        (info.sep_equinox, names[2], "equinozio di settembre"),
        (info.dec_solstice, names[3], "solstizio di dicembre"),
    )
    now = when.astimezone(timezone.utc)
    current = names[3]
    nxt_name = marks[0][2]
    nxt_when = marks[0][0]
    for idx, (stamp, season, label) in enumerate(marks):
        utc = stamp.Utc()
        if utc.tzinfo is None:
            utc = utc.replace(tzinfo=timezone.utc)
        if now >= utc:
            current = season
            nxt = marks[(idx + 1) % 4]
            nxt_name, nxt_when = nxt[2], nxt[0]
    nxt_utc = nxt_when.Utc()
    if nxt_utc.tzinfo is None:
        nxt_utc = nxt_utc.replace(tzinfo=timezone.utc)
    if nxt_utc < now:
        nxt = astronomy.Seasons(when.year + 1).mar_equinox
        nxt_utc = nxt.Utc()
        if nxt_utc.tzinfo is None:
            nxt_utc = nxt_utc.replace(tzinfo=timezone.utc)
        nxt_name = "equinozio di marzo"
    return current, f"{nxt_name} il {nxt_utc.day:02d}/{nxt_utc.month:02d}"


def format_cielo_terra(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
    daylight: str = "",
) -> str:
    """Il pianeta sotto i piedi: numeri, non l'enciclopedia di NATURA."""
    place = _html.escape(place)
    frame = SkyFrame(lat, lon, when)
    sun_alt, _az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    moon = moon_now(when)
    au = float(astronomy.HelioDistance(astronomy.Body.Earth, frame.moment))
    moon_vec = astronomy.GeoVector(astronomy.Body.Moon, frame.moment, True)
    moon_km = math.sqrt(moon_vec.x**2 + moon_vec.y**2 + moon_vec.z**2) * float(astronomy.KM_PER_AU)
    season, nxt = _season_it(when, lat)
    hemi = "boreale" if lat >= 0 else "australe"
    sky = "giorno" if sun_alt > 0 else "notte"
    day_bit = f" · luce {daylight}" if daylight else ""
    return "\n".join(
        [
            f"🌍 <b>TERRA — {place.upper()}</b>",
            f"{when.strftime('%d/%m/%Y %H:%M')}",
            "",
            f"📍 {lat:.4f}°, {lon:.4f}° · emisfero {hemi}",
            f"{'☀️' if sun_alt > 0 else '🌌'} Adesso è <b>{sky}</b>{day_bit}",
            f"☀️ Sole a {sun_alt:+.0f}° sull'orizzonte",
            f"🌿 Stagione astronomica: <b>{season}</b> · prossimo {nxt}",
            f"☀️ Distanza dal Sole: <b>{au:.4f} au</b>",
            f"{moon.get('emoji') or '🌙'} Distanza dalla Luna: <b>{int(round(moon_km)):,}".replace(",", ".") + " km</b>",
            "",
            "<i>Astronomy Engine. Non è l'enciclopedia di 🌿 NATURA e non è un GPS.</i>",
        ]
    )


def format_sun_moon_earth(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> str:
    """Schema Sole–Terra–Luna con emoji Telegram. Niente griglia di stelle."""
    place = _html.escape(place)
    frame = SkyFrame(lat, lon, when)
    moon = moon_now(when)
    sun_alt, _sun_az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    moon_alt, _moon_az, _mra, _mdec = frame.body_altaz(astronomy.Body.Moon)
    moon_emoji = str(moon.get("emoji") or "🌙")
    cols, rows = 11, 7
    grid = [[" " for _ in range(cols)] for _ in range(rows)]
    earth = (2, 3)
    sun = (0, 3)
    angle = math.radians(180.0 + float(moon.get("angle") or 0.0))
    mx = int(round(earth[0] + 3 * math.cos(angle)))
    my = int(round(earth[1] - 3 * math.sin(angle)))
    mx = max(0, min(cols - 1, mx))
    my = max(0, min(rows - 1, my))
    if (mx, my) == sun:
        mx, my = earth[0] - 1, earth[1]
    if (mx, my) == earth:
        mx = min(cols - 1, earth[0] + 1)
    grid[sun[1]][sun[0]] = "☀️"
    grid[earth[1]][earth[0]] = "🌍"
    grid[my][mx] = moon_emoji
    for x in range(sun[0] + 1, earth[0]):
        if grid[3][x] == " ":
            grid[3][x] = "·"
    pre = ["<pre>"]
    for row in grid:
        text = "".join(row).rstrip()
        if text.strip():
            pre.append(text)
    pre.append("</pre>")
    sun_side = "sopra l'orizzonte" if sun_alt > 0 else "sotto l'orizzonte"
    moon_side = "sopra l'orizzonte" if moon_alt > 0 else "sotto l'orizzonte"
    illum = moon.get("illum")
    illum_s = f"{illum:.0f}%" if isinstance(illum, (int, float)) else "—"
    return "\n".join(
        [
            f"☀️🌙🌍 <b>SOLE, LUNA, TERRA — {place.upper()}</b>",
            f"{when.strftime('%d/%m/%Y %H:%M')}",
            "",
            *pre,
            "",
            f"☀️ Sole · {sun_side} · altezza {sun_alt:+.0f}°",
            f"🌍 Terra · {place} · {'giorno' if sun_alt > 0 else 'notte'}",
            f"{moon_emoji} Luna · {moon.get('name') or 'fase'} · illuminata {illum_s} · {moon_side}",
            "",
            "<i>Vista dal nord dell'eclittica: il Sole sta a sinistra, la Luna gira intorno alla Terra. "
            "Fase e altezze da Astronomy Engine. Solo emoji di Telegram.</i>",
        ]
    )
