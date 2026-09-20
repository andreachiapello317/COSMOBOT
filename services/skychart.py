"""Carta celeste PNG: stelle Hipparcos + pianeti/Luna da Astronomy Engine."""

from __future__ import annotations

import math
from datetime import datetime
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


SKY_STYLES = ("classic", "horizon", "figures", "emoji")
SKY_STYLE_LABELS = {
    "classic": "Classica",
    "horizon": "Panorama",
    "figures": "Figure",
    "emoji": "Emoji",
}


def sky_style_label(style: str) -> str:
    return SKY_STYLE_LABELS.get(style, "Classica")


def draw_horizon_chart(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> bytes:
    """Stessi oggetti della carta classica, visti come striscia azimut × altezza."""
    frame = SkyFrame(lat, lon, when)
    stars = visible_stars(frame)
    figures = constellation_segments(frame)
    width, height = 1100, 520
    ground = 70
    img = Image.new("RGB", (width, height + 64), (6, 10, 20))
    draw = ImageDraw.Draw(img)
    sky_h = height - ground
    title_font = _font(20)
    tiny = _font(13)

    def xy(alt: float, az: float) -> tuple[int, int]:
        x = int((az % 360.0) / 360.0 * width)
        y = int(sky_h - max(0.0, min(alt, 90.0)) / 90.0 * sky_h)
        return x, y

    draw.rectangle((0, 0, width, sky_h), fill=(8, 14, 28))
    draw.rectangle((0, sky_h, width, height), fill=(28, 24, 18))
    for alt in (0, 30, 60):
        y = int(sky_h - alt / 90.0 * sky_h)
        draw.line((0, y, width, y), fill=(40, 55, 80))
    for az, name in ((0, "N"), (90, "E"), (180, "S"), (270, "O")):
        x = int(az / 360.0 * width)
        draw.line((x, 0, x, height), fill=(36, 48, 70))
        draw.text((x + 6, sky_h + 8), name, fill=(220, 220, 230), font=title_font)

    for fig in figures:
        for seg in fig["segs"]:
            pts = [xy(alt, az) for alt, az in seg if alt > -1]
            if len(pts) >= 2:
                draw.line(pts, fill=(80, 105, 150), width=2)

    for star in stars:
        if star["alt"] <= 0:
            continue
        x, y = xy(star["alt"], star["az"])
        rad = max(1.0, 5.2 - float(star["mag"]))
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=_star_color(star.get("bv")))

    sun_alt, sun_az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    if sun_alt > -0.5:
        x, y = xy(sun_alt, sun_az)
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 210, 70))
    moon_alt, moon_az, _ra, _dec = frame.body_altaz(astronomy.Body.Moon)
    if moon_alt > -0.5:
        x, y = xy(moon_alt, moon_az)
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(230, 230, 210))
    for body, label, color in PLANETS:
        alt, az, _ra, _dec = frame.body_altaz(body)
        if alt <= 0:
            continue
        x, y = xy(alt, az)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color, outline=(255, 255, 255))
        draw.text((x + 7, y - 8), label, fill=color, font=tiny)

    draw.rectangle((0, height, width, height + 64), fill=(6, 10, 20))
    draw.text((20, height + 10), f"Cielo di adesso · panorama · {place}", fill=(235, 238, 245), font=title_font)
    draw.text(
        (20, height + 36),
        f"{when.strftime('%d/%m/%Y %H:%M')} · azimut da N verso E · Hipparcos + Astronomy Engine",
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


_PLANET_EMOJI = (
    (astronomy.Body.Mercury, "Mercurio", "⚪"),
    (astronomy.Body.Venus, "Venere", "🟡"),
    (astronomy.Body.Mars, "Marte", "🔴"),
    (astronomy.Body.Jupiter, "Giove", "🟠"),
    (astronomy.Body.Saturn, "Saturno", "🪐"),
    (astronomy.Body.Uranus, "Urano", "🟢"),
    (astronomy.Body.Neptune, "Nettuno", "🔵"),
)


def format_emoji_sky(
    *,
    place: str,
    lat: float,
    lon: float,
    when: datetime,
) -> str:
    """Carta in emoji native di Telegram: stessi oggetti, niente PNG."""
    frame = SkyFrame(lat, lon, when)
    stars = visible_stars(frame)
    cols, rows = 11, 9
    grid = [["·" for _ in range(cols)] for _ in range(rows)]
    mid_x, mid_y = cols // 2, rows // 2
    radius = min(mid_x, mid_y) - 0.15

    def cell(alt: float, az: float) -> tuple[int, int] | None:
        if alt <= 0:
            return None
        r = ((90.0 - alt) / 90.0) * radius
        theta = math.radians(az)
        x = int(round(mid_x + r * math.sin(theta)))
        y = int(round(mid_y - r * math.cos(theta)))
        if 0 <= x < cols and 0 <= y < rows:
            return x, y
        return None

    for star in reversed(stars):
        pos = cell(star["alt"], star["az"])
        if not pos:
            continue
        mag = float(star["mag"])
        if mag <= 0.4:
            glyph = "🌟"
        elif mag <= 1.5:
            glyph = "⭐"
        elif mag <= 2.8:
            glyph = "✨"
        else:
            glyph = "💫"
        grid[pos[1]][pos[0]] = glyph

    above: list[str] = []
    for body, name, emoji in _PLANET_EMOJI:
        alt, az, _ra, _dec = frame.body_altaz(body)
        pos = cell(alt, az)
        if pos:
            grid[pos[1]][pos[0]] = emoji
            above.append(f"{emoji} {name}")

    moon = moon_now(when)
    moon_alt, moon_az, _ra, _dec = frame.body_altaz(astronomy.Body.Moon)
    moon_emoji = str(moon.get("emoji") or "🌙")
    pos = cell(moon_alt, moon_az)
    if pos:
        grid[pos[1]][pos[0]] = moon_emoji
        above.insert(0, f"{moon_emoji} Luna")
    sun_alt, sun_az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    pos = cell(sun_alt, sun_az)
    if pos:
        grid[pos[1]][pos[0]] = "☀️"
        above.insert(0, "☀️ Sole")

    named = [star for star in stars if star.get("name") and float(star["mag"]) <= 1.8]
    named.sort(key=lambda row: float(row["mag"]))
    star_bits = [f"⭐ {row['name']}" for row in named[:6]]

    lines = ["<pre>      N"]
    for y, row in enumerate(grid):
        prefix = "O " if y == mid_y else "  "
        suffix = " E" if y == mid_y else ""
        lines.append(prefix + "".join(row) + suffix)
    lines.append("      S</pre>")
    lines.extend(
        [
            "",
            "🌟 più luminosa · ⭐ · ✨ · 💫 più debole",
            "☀️ Sole · Luna in fase · ⚪🟡🔴🟠🪐🟢🔵 pianeti",
        ]
    )
    if above:
        lines.append("Sopra l'orizzonte: " + " · ".join(above))
    if star_bits:
        lines.append("Stelle: " + " · ".join(star_bits))
    lines.append(
        f"<i>N in alto, orizzonte sul bordo. Stessi numeri della classica, "
        f"disegnati con le emoji di Telegram sopra {place}.</i>"
    )
    return "\n".join(lines)
