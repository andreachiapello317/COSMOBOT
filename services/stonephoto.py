"""Ipotesi da foto per il laboratorio Pietre: colore dominante + scommesse di catalogo.

Non è un'analisi mineralogica. Se l'immagine non si legge, si pesca comunque.
"""

from __future__ import annotations

import random
from collections import Counter
from io import BytesIO
from typing import Any

from services.stones import COLORS, STONES, by_color

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment]


def _hue_key(r: int, g: int, b: int) -> str | None:
    mx, mn = max(r, g, b), min(r, g, b)
    val = mx / 255.0
    sat = 0.0 if mx == 0 else (mx - mn) / mx
    if val < 0.16:
        return "black"
    if sat < 0.14:
        if val > 0.82:
            return "white"
        if val < 0.38:
            return "black"
        return "brown" if r >= g >= b and val < 0.7 else None
    # hue in [0, 1)
    delta = mx - mn
    if delta == 0:
        hue = 0.0
    elif mx == r:
        hue = ((g - b) / delta) % 6.0
    elif mx == g:
        hue = (b - r) / delta + 2.0
    else:
        hue = (r - g) / delta + 4.0
    hue = (hue * 60.0) % 360.0 / 360.0
    if hue < 0.03 or hue >= 0.95:
        return "red"
    if hue < 0.10:
        return "orange" if val > 0.35 else "brown"
    if hue < 0.18:
        return "yellow"
    if hue < 0.45:
        return "green"
    if hue < 0.57:
        return "blue"
    if hue < 0.72:
        return "purple" if sat > 0.25 else "blue"
    if hue < 0.90:
        return "pink" if val > 0.45 else "red"
    return "red"


def _metallic(r: int, g: int, b: int) -> bool:
    mx, mn = max(r, g, b), min(r, g, b)
    sat = 0.0 if mx == 0 else (mx - mn) / mx
    val = mx / 255.0
    gold = r > 140 and g > 100 and b < 110 and r >= g > b
    silver = sat < 0.18 and 0.35 < val < 0.9 and abs(r - g) < 18 and abs(g - b) < 18
    return gold or silver


def read_photo_hints(data: bytes) -> dict[str, Any]:
    if Image is None or not data:
        return {"colors": [], "metallic": False, "ok": False}
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        img.thumbnail((96, 96))
    except Exception:
        return {"colors": [], "metallic": False, "ok": False}
    counts: Counter[str] = Counter()
    metal = 0
    total = 0
    for r, g, b in img.getdata():
        total += 1
        if _metallic(r, g, b):
            metal += 1
        key = _hue_key(r, g, b)
        if key:
            counts[key] += 1
    if not total:
        return {"colors": [], "metallic": False, "ok": False}
    ranked = [key for key, n in counts.most_common(4) if n / total >= 0.08]
    if len(ranked) >= 3:
        ranked = ranked[:2] + ["multi"]
    return {
        "colors": ranked[:3],
        "metallic": metal / total >= 0.12,
        "ok": True,
    }


def guess_stones(hints: dict[str, Any], n: int = 3) -> list[dict[str, Any]]:
    colors = [c for c in hints.get("colors") or [] if c in COLORS]
    pool: list[dict[str, Any]] = []
    for key in colors:
        pool.extend(by_color(key))
    if hints.get("metallic"):
        metal = [s for s in STONES if s.get("metallic")]
        pool = metal + pool if metal else pool
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for stone in pool:
        if stone["id"] in seen:
            continue
        seen.add(stone["id"])
        unique.append(stone)
    random.shuffle(unique)
    picks = unique[:n]
    if len(picks) < n:
        rest = [s for s in STONES if s["id"] not in {p["id"] for p in picks}]
        random.shuffle(rest)
        picks.extend(rest[: n - len(picks)])
    random.shuffle(picks)
    return picks[:n]
