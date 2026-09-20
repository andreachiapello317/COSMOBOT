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
