"""Immagini pubbliche del suolo da NASA GIBS. Niente chiave."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any

import httpx
from PIL import Image, ImageDraw, ImageFont

GIBS_SNAPSHOT = "https://wvs.earthdata.nasa.gov/api/v1/snapshot"

GIBS_LAYER: dict[str, str] = {
    "terra": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "aqua": "MODIS_Aqua_CorrectedReflectance_TrueColor",
}

LAYER_IT = {"terra": "MODIS Terra", "aqua": "MODIS Aqua"}

# Inquadratura stretta: con 7.5° Cuneo e Berlino si sovrapponevano.
CITY_SPAN = 2.2


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


async def fetch_gibs_true_color(
    client: httpx.AsyncClient,
    layer: str,
    lat: float,
    lon: float,
    *,
    span: float = CITY_SPAN,
) -> tuple[bytes | None, str]:
    today = datetime.now(timezone.utc).date()
    for back in range(0, 4):
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
            if data[:3] == b"\xff\xd8\xff" and len(data) > 8000:
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
) -> dict[str, Any]:
    layer = GIBS_LAYER.get(key) or GIBS_LAYER["terra"]
    used = key if key in GIBS_LAYER else "terra"
    data, day = await fetch_gibs_true_color(client, layer, lat, lon)
    if data and place:
        label = day.replace("-", "/") if day else ""
        data = stamp_place_photo(data, place, f"{LAYER_IT[used]} · {label}" if label else LAYER_IT[used])
    slug = f"{used}_{lat:.2f}_{lon:.2f}_{day or 'x'}".replace("-", "m").replace(".", "p")
    return {
        "bytes": data,
        "day": day,
        "layer": used,
        "filename": f"{slug}.jpg",
        "note": f"NASA GIBS · {LAYER_IT[used]}" + (f" · {day}" if day else ""),
    }
