"""Ipotesi da foto: il colore letto è un vincolo, non un suggerimento.

Non è un'analisi mineralogica. Senza un colore netto non si pesca a caso.
"""

from __future__ import annotations

import random
from collections import Counter
from io import BytesIO
from typing import Any

from services.stones import COLORS, STONES

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment]

# Chiavi cromatiche: il marrone/nero/bianco di sfondo non deve vincere sul colore della pietra.
CHROMA = ("red", "orange", "yellow", "green", "blue", "purple", "pink")


def _hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    mx, mn = max(r, g, b), min(r, g, b)
    val = mx / 255.0
    sat = 0.0 if mx == 0 else (mx - mn) / mx
    delta = mx - mn
    if delta == 0:
        hue = 0.0
    elif mx == r:
        hue = ((g - b) / delta) % 6.0
    elif mx == g:
        hue = (b - r) / delta + 2.0
    else:
        hue = (r - g) / delta + 4.0
    return (hue * 60.0) % 360.0, sat, val


def _hue_key(r: int, g: int, b: int) -> str | None:
    hue, sat, val = _hsv(r, g, b)
    if val < 0.12:
        return "black"
    if sat < 0.18:
        if val > 0.88:
            return "white"
        if val < 0.28:
            return "black"
        return None
    if hue < 12 or hue >= 345:
        return "red"
    if hue < 35:
        return "orange" if val > 0.40 else "brown"
    if hue < 62:
        return "yellow"
    if hue < 165:
        return "green"
    if hue < 255:
        return "blue"
    if hue < 318:
        return "purple"
    if hue < 345:
        return "pink" if val > 0.42 else "red"
    return "red"


def _metallic(r: int, g: int, b: int) -> bool:
    hue, sat, val = _hsv(r, g, b)
    gold = 35 <= hue <= 58 and sat > 0.25 and val > 0.35
    silver = sat < 0.14 and 0.40 < val < 0.88 and abs(r - g) < 16 and abs(g - b) < 16
    return gold or silver


def _center_pixels(img: Any) -> list[tuple[int, int, int]]:
    w, h = img.size
    x0, x1 = int(w * 0.22), int(w * 0.78)
    y0, y1 = int(h * 0.22), int(h * 0.78)
    crop = img.crop((x0, y0, max(x0 + 1, x1), max(y0 + 1, y1)))
    return list(crop.getdata())


def read_photo_hints(data: bytes) -> dict[str, Any]:
    if Image is None or not data:
        return {"colors": [], "metallic": False, "ok": False}
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        img.thumbnail((160, 160))
    except Exception:
        return {"colors": [], "metallic": False, "ok": False}
    pixels = _center_pixels(img)
    if not pixels:
        return {"colors": [], "metallic": False, "ok": False}
    counts: Counter[str] = Counter()
    metal = 0
    for r, g, b in pixels:
        if _metallic(r, g, b):
            metal += 1
        key = _hue_key(r, g, b)
        if key:
            counts[key] += 1
    total = len(pixels)
    if not counts:
        return {"colors": [], "metallic": False, "ok": False}
    chroma = [(k, n) for k, n in counts.most_common() if k in CHROMA]
    # Il colore della pietra: prima un cromatico chiaro, non l'ombra o il tavolo.
    if chroma and chroma[0][1] / total >= 0.10:
        dominant = chroma[0][0]
        ranked = [dominant]
        if len(chroma) > 1 and chroma[1][1] >= chroma[0][1] * 0.85 and chroma[1][1] / total >= 0.12:
            ranked.append(chroma[1][0])
    else:
        neutral = [k for k, n in counts.most_common() if k in {"black", "white", "brown"} and n / total >= 0.20]
        ranked = neutral[:1]
    if not ranked:
        return {"colors": [], "metallic": False, "ok": False}
    return {
        "colors": ranked,
        "metallic": metal / total >= 0.18,
        "ok": True,
    }


def primary_color(stone: dict[str, Any]) -> str | None:
    for key in stone.get("colors") or ():
        if key in COLORS and key not in {"change"}:
            return key
    return None


def stone_fits_color(stone: dict[str, Any], key: str) -> bool:
    cols = tuple(stone.get("colors") or ())
    if not cols:
        return False
    head = cols[0]
    if head == key:
        return True
    # Multicolore / cangiante: il colore letto deve comparire, non un altro a caso.
    if head in {"multi", "change"}:
        return key in cols
    return False


def guess_stones(hints: dict[str, Any], n: int = 3) -> list[dict[str, Any]]:
    colors = [c for c in hints.get("colors") or [] if c in COLORS]
    if not colors:
        return []
    dominant = colors[0]
    pool = [s for s in STONES if stone_fits_color(s, dominant)]
    if hints.get("metallic"):
        metal = [s for s in pool if s.get("metallic")]
        if metal:
            pool = metal
    if not pool:
        return []
    random.shuffle(pool)
    return pool[:n]
