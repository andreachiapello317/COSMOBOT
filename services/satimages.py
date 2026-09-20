"""Immagini NASA Worldview / GIBS. Snapshot pubblico, niente chiave."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any

import httpx
from PIL import Image, ImageDraw, ImageFont

GIBS_SNAPSHOT = "https://wvs.earthdata.nasa.gov/api/v1/snapshot"

# Strati Worldview. Niente WRAP=DAY: GIBS risponde XML.
GIBS: dict[str, dict[str, Any]] = {
    "vii": {
        "layers": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
        "it": "VIIRS colore vero",
        "btn": "VIIRS",
        "emoji": "✨",
        "look": 4,
    },
    "terra": {
        "layers": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "it": "MODIS Terra",
        "btn": "Terra",
        "emoji": "🌍",
        "look": 4,
    },
    "false": {
        "layers": "MODIS_Terra_CorrectedReflectance_Bands721",
        "it": "Falso colore 7-2-1",
        "btn": "Falso",
        "emoji": "🎨",
        "look": 4,
    },
    "night": {
        "layers": "VIIRS_SNPP_DayNightBand_ENCC",
        "it": "Luci notturne",
        "btn": "Notti",
        "emoji": "🌃",
        "look": 7,
    },
    "fire": {
        "layers": "MODIS_Terra_CorrectedReflectance_TrueColor,MODIS_Combined_Thermal_Anomalies_All",
        "it": "Incendi (anomalie termiche)",
        "btn": "Fuochi",
        "emoji": "🔥",
        "look": 4,
    },
}

GIBS_LAYER = {key: str(row["layers"]) for key, row in GIBS.items()}
LAYER_IT = {key: str(row["it"]) for key, row in GIBS.items()}
LAYER_KEYS = tuple(GIBS)
DEFAULT_LAYER = "vii"

SPAN_STEPS = (1.0, 2.2, 5.2)
SPAN_IT = ("città", "zona", "regione")
CITY_SPAN = SPAN_STEPS[1]


def layer_meta(key: str) -> dict[str, Any]:
    return GIBS.get(key) or GIBS[DEFAULT_LAYER]


def _bbox(lat: float, lon: float, span: float = CITY_SPAN) -> str:
    south = max(-85.0, lat - span * 0.55)
    north = min(85.0, lat + span * 0.55)
    west = max(-180.0, lon - span)
    east = min(180.0, lon + span)
    return f"{south:.4f},{west:.4f},{north:.4f},{east:.4f}"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def stamp_place_photo(data: bytes, place: str, when: str) -> bytes:
    img = Image.open(BytesIO(data)).convert("RGB")
    draw = ImageDraw.Draw(img)
    title = str(place or "luogo").strip()[:42]
    bar_h = 44
    draw.rectangle((0, img.height - bar_h, img.width, img.height), fill=(8, 12, 20))
    draw.text((12, img.height - 36), title, fill=(235, 238, 245), font=_font(20))
    draw.text((12, img.height - 18), when, fill=(160, 175, 195), font=_font(13))
    out = BytesIO()
    img.save(out, format="JPEG", quality=88, optimize=True)
    return out.getvalue()


def stamp_target_photo(data: bytes, place: str, when: str) -> bytes:
    img = Image.open(BytesIO(data)).convert("RGB")
    draw = ImageDraw.Draw(img)
    cx, cy = img.width // 2, img.height // 2
    r = 14
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(230, 60, 50), width=3)
    draw.line((cx, cy - 22, cx, cy + 22), fill=(230, 60, 50), width=2)
    draw.line((cx - 22, cy, cx + 22, cy), fill=(230, 60, 50), width=2)
    title = str(place or "evento").strip()[:42]
    bar_h = 44
    draw.rectangle((0, img.height - bar_h, img.width, img.height), fill=(8, 12, 20))
    draw.text((12, img.height - 36), title, fill=(235, 238, 245), font=_font(20))
    draw.text((12, img.height - 18), when, fill=(160, 175, 195), font=_font(13))
    out = BytesIO()
    img.save(out, format="JPEG", quality=88, optimize=True)
    return out.getvalue()


def _is_jpeg(data: bytes) -> bool:
    return data[:3] == b"\xff\xd8\xff" and len(data) > 8000 and not data.lstrip().startswith(b"<")


async def fetch_gibs_true_color(
    client: httpx.AsyncClient,
    layer: str,
    lat: float,
    lon: float,
    *,
    span: float = CITY_SPAN,
    look: int = 4,
) -> tuple[bytes | None, str]:
    today = datetime.now(timezone.utc).date()
    for back in range(0, max(2, int(look) + 1)):
        day = today - timedelta(days=back)
        try:
            response = await client.get(
                GIBS_SNAPSHOT,
                params={
                    "REQUEST": "GetSnapshot",
                    "LAYERS": f"{layer},Coastlines,Reference_Features",
                    "CRS": "EPSG:4326",
                    "TIME": day.isoformat(),
                    "BBOX": _bbox(lat, lon, span),
                    "FORMAT": "image/jpeg",
                    "WIDTH": "800",
                    "HEIGHT": "600",
                },
            )
            response.raise_for_status()
            data = response.content
            if _is_jpeg(data):
                return data, day.isoformat()
        except Exception:
            continue
    return None, ""


async def fetch_sat_view(
    client: httpx.AsyncClient,
    key: str,
    lat: float,
    lon: float,
    *,
    place: str = "",
    span: float = CITY_SPAN,
) -> dict[str, Any]:
    if key == "aqua":
        key = DEFAULT_LAYER
    meta = layer_meta(key)
    used = key if key in GIBS else DEFAULT_LAYER
    data, day = await fetch_gibs_true_color(
        client,
        str(meta["layers"]),
        lat,
        lon,
        span=span,
        look=int(meta.get("look") or 4),
    )
    if data and place:
        label = day.replace("-", "/") if day else ""
        data = stamp_place_photo(data, place, f"{meta['it']} · {label}" if label else str(meta["it"]))
    slug = f"{used}_{lat:.2f}_{lon:.2f}_{span:.1f}_{day or 'x'}".replace("-", "m").replace(".", "p")
    return {
        "bytes": data,
        "day": day,
        "layer": used,
        "filename": f"{slug}.jpg",
        "note": f"NASA Worldview / GIBS · {meta['it']}" + (f" · {day}" if day else ""),
    }
