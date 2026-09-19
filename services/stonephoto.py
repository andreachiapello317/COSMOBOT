"""Ipotesi da foto: colore come vincolo, poi confronto visivo.

Non è un'analisi mineralogica. Senza un colore netto non si pesca a caso.
Le ipotesi arrivano da (1) filtro colore del catalogo, (2) somiglianza con le
miniature Wikipedia/Wikimedia delle pietre, (3) CLIP zero-shot se HF_TOKEN
è disponibile. Una foto non sostituisce durezza, striscio, densità.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import math
import os
from collections import Counter
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx

from services.stones import COLORS, STONES

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment]

logger = logging.getLogger("stellebot.stonephoto")

# Chiavi cromatiche: il marrone/nero/bianco di sfondo non deve vincere sul colore della pietra.
CHROMA = ("red", "orange", "yellow", "green", "blue", "purple", "pink")

REF_CACHE = Path("data/stone_refs.json")
REF_VERSION = 4
HUE_BINS = 18
SAT_BINS = 8
VAL_BINS = 8
SIG_LEN = HUE_BINS + SAT_BINS + VAL_BINS + 6  # hist + rgb + sat/val mean + texture

CLIP_MODEL = "openai/clip-vit-base-patch32"
CLIP_URLS = (
    f"https://router.huggingface.co/hf-inference/models/{CLIP_MODEL}",
    f"https://api-inference.huggingface.co/models/{CLIP_MODEL}",
)

_ref_lock = asyncio.Lock()

# ---------------------------------------------------------------------------
# Colore / HSV
# ---------------------------------------------------------------------------


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
        # Il legno del tavolo è spesso arancio-marrone: senza saturazione alta è sfondo.
        return "orange" if val > 0.50 and sat > 0.45 else "brown"
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
    # Ottone/oro: sat media. Un giallo saturo da gemma (citrino) non è metallico.
    gold = 36 <= hue <= 54 and 0.22 <= sat <= 0.58 and val > 0.38
    silver = sat < 0.14 and 0.40 < val < 0.88 and abs(r - g) < 16 and abs(g - b) < 16
    return gold or silver


def _center_pixels(img: Any) -> list[tuple[int, int, int]]:
    w, h = img.size
    x0, x1 = int(w * 0.28), int(w * 0.72)
    y0, y1 = int(h * 0.28), int(h * 0.72)
    crop = img.crop((x0, y0, max(x0 + 1, x1), max(y0 + 1, y1)))
    return list(crop.getdata())


def _open_rgb(data: bytes, size: int = 160) -> Any | None:
    if Image is None or not data:
        return None
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        img.thumbnail((size, size))
        return img
    except Exception:
        return None


def _is_skin(r: int, g: int, b: int) -> bool:
    hue, sat, val = _hsv(r, g, b)
    if not (8.0 <= hue <= 28.0):
        return False
    if sat < 0.14 or sat > 0.50:
        return False
    if val < 0.28 or val > 0.95:
        return False
    if r < 90 or r < g + 8:
        return False
    if g < b - 5:
        return False
    if sat > 0.46 and (r - b) > 90:
        return False
    return True


def _mean_rgb(pixels: list[tuple[int, int, int]]) -> tuple[float, float, float]:
    if not pixels:
        return (128.0, 128.0, 128.0)
    n = float(len(pixels))
    return (
        sum(p[0] for p in pixels) / n,
        sum(p[1] for p in pixels) / n,
        sum(p[2] for p in pixels) / n,
    )


def _rgb_l1(pixel: tuple[float, float, float], other: tuple[float, float, float]) -> float:
    return (
        abs(pixel[0] - other[0]) + abs(pixel[1] - other[1]) + abs(pixel[2] - other[2])
    ) / (3.0 * 255.0)


def isolate_stone(img: Any) -> tuple[list[tuple[int, int, int]], dict[str, Any]]:
    """Pixel della pietra: gli angoli sono sfondo, il centro e la saturazione pesano di più."""
    w, h = img.size
    data = list(img.getdata())
    if not data:
        return [], {"mode": "empty", "bg_keys": []}
    bx = max(2, int(w * 0.16))
    by = max(2, int(h * 0.16))
    border: list[tuple[int, int, int]] = []
    interior: list[tuple[int, int, int]] = []
    for y in range(h):
        row = y * w
        for x in range(w):
            pix = data[row + x]
            if x < bx or x >= w - bx or y < by or y >= h - by:
                border.append(pix)
            else:
                interior.append((row + x, x, y))
    if not interior:
        return _center_pixels(img), {"mode": "center", "bg_keys": []}
    bg_mean = _mean_rgb(border)
    border_keys: Counter[str] = Counter()
    border_sat = 0.0
    for r, g, b in border:
        key = _hue_key(r, g, b)
        if key:
            border_keys[key] += 1
        border_sat += _hsv(r, g, b)[1]
    border_sat /= len(border) or 1
    bg_n = sum(border_keys.values()) or 1
    bg_keys = {key for key, n in border_keys.items() if n / bg_n >= 0.18}
    # Tutto campo solo se anche il nucleo centrale è come il bordo (macro della pietra).
    core: list[tuple[int, int, int]] = []
    x0, x1 = int(w * 0.34), int(w * 0.66)
    y0, y1 = int(h * 0.34), int(h * 0.66)
    for y in range(y0, max(y0 + 1, y1)):
        row = y * w
        for x in range(x0, max(x0 + 1, x1)):
            core.append(data[row + x])
    core_mean = _mean_rgb(core)
    core_sat = sum(_hsv(*p)[1] for p in core) / (len(core) or 1)
    full_frame = _rgb_l1(bg_mean, core_mean) < 0.08 and abs(border_sat - core_sat) < 0.09
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    half = math.hypot(cx, cy) or 1.0
    scored: list[tuple[float, int, int, int]] = []
    for i, x, y in interior:
        r, g, b = data[i]
        _hue, sat, val = _hsv(r, g, b)
        center_w = math.exp(-4.4 * ((math.hypot(x - cx, y - cy) / half) ** 2))
        score = center_w * (0.22 + 0.78 * min(1.0, sat / 0.52))
        if val < 0.10:
            score *= 0.12
        if not full_frame:
            key = _hue_key(r, g, b)
            if key in bg_keys:
                score *= 0.10
            score *= 0.28 + 0.72 * min(1.0, _rgb_l1((r, g, b), bg_mean) * 2.9)
            if _is_skin(r, g, b):
                score *= 0.05
        scored.append((score, r, g, b))
    scored.sort(key=lambda row: row[0], reverse=True)
    best = scored[0][0] if scored else 0.0
    keep_n = max(48, int(len(scored) * 0.18))
    cutoff = max(best * 0.36, 0.018)
    fg = [(r, g, b) for score, r, g, b in scored[:keep_n] if score >= cutoff]
    if len(fg) < 36:
        fg = [(r, g, b) for _score, r, g, b in scored[: max(keep_n, 90)]]
    if not fg:
        fg = _center_pixels(img)
    return fg, {
        "mode": "full" if full_frame else "cutout",
        "bg_keys": sorted(bg_keys),
    }


def _vote_colors(pixels: list[tuple[int, int, int]]) -> dict[str, Any]:
    weights: Counter[str] = Counter()
    metal_w = 0.0
    total_w = 0.0
    for r, g, b in pixels:
        _hue, sat, val = _hsv(r, g, b)
        weight = 0.35 + 0.65 * sat
        if val < 0.12:
            weight *= 0.25
        total_w += weight
        if _metallic(r, g, b):
            metal_w += weight
        key = _hue_key(r, g, b)
        if key:
            weights[key] += weight
    if not weights or total_w <= 0:
        return {"colors": [], "metallic": False, "ok": False, "multi": False}
    chroma = [(key, n) for key, n in weights.most_common() if key in CHROMA]
    multi = False
    if chroma and chroma[0][1] / total_w >= 0.10:
        ranked = [chroma[0][0]]
        if (
            len(chroma) > 1
            and chroma[1][1] >= chroma[0][1] * 0.55
            and chroma[1][1] / total_w >= 0.14
        ):
            multi = True
            if chroma[1][1] >= chroma[0][1] * 0.78 and chroma[1][1] / total_w >= 0.16:
                ranked.append(chroma[1][0])
    else:
        neutral = [
            key
            for key, n in weights.most_common()
            if key in {"black", "white", "brown"} and n / total_w >= 0.22
        ]
        ranked = neutral[:1]
    if not ranked:
        return {"colors": [], "metallic": False, "ok": False, "multi": False}
    return {
        "colors": ranked,
        "metallic": metal_w / total_w >= 0.22,
        "ok": True,
        "multi": multi,
    }


def read_photo_hints(data: bytes) -> dict[str, Any]:
    img = _open_rgb(data, 220)
    if img is None:
        return {"colors": [], "metallic": False, "ok": False, "mode": "none", "bg_keys": []}
    pixels, meta = isolate_stone(img)
    if not pixels:
        return {"colors": [], "metallic": False, "ok": False, "mode": "none", "bg_keys": []}
    voted = _vote_colors(pixels)
    voted["mode"] = meta.get("mode") or "cutout"
    voted["bg_keys"] = list(meta.get("bg_keys") or [])
    return voted


def primary_color(stone: dict[str, Any]) -> str | None:
    for key in stone.get("colors") or ():
        if key in COLORS and key not in {"change"}:
            return key
    return None


def stone_color_rank(stone: dict[str, Any], key: str) -> int:
    """0 = colore principale, 1 = anche di quel colore, 2 = catch-all multi, 9 = no."""
    cols = tuple(stone.get("colors") or ())
    if not cols or key not in COLORS:
        return 9
    head = cols[0]
    if head == key:
        return 0
    if key not in cols:
        return 9
    if head == "multi":
        return 2
    return 1


def stone_fits_color(stone: dict[str, Any], key: str, *, allow_multi: bool = False) -> bool:
    rank = stone_color_rank(stone, key)
    if rank <= 1:
        return True
    return allow_multi and rank == 2


def color_pool(hints: dict[str, Any]) -> list[dict[str, Any]]:
    colors = [c for c in hints.get("colors") or [] if c in COLORS]
    if not colors:
        return []
    dominant = colors[0]
    allow_multi = bool(hints.get("multi")) or len(colors) > 1
    pool = [s for s in STONES if stone_fits_color(s, dominant, allow_multi=allow_multi)]
    if len(pool) < 2:
        extra = [
            s
            for s in STONES
            if s not in pool and stone_fits_color(s, dominant, allow_multi=True)
        ]
        pool = pool + extra
    if hints.get("metallic"):
        metal = [s for s in pool if s.get("metallic")]
        if metal:
            pool = metal
    return pool


def _color_typicality(stone: dict[str, Any], key: str) -> tuple[int, int]:
    rank = stone_color_rank(stone, key)
    extra = max(0, len([c for c in (stone.get("colors") or ()) if c not in {"multi", "change"}]) - 1)
    return (rank, extra)


def guess_stones(hints: dict[str, Any], n: int = 3) -> list[dict[str, Any]]:
    colors = [c for c in hints.get("colors") or [] if c in COLORS]
    pool = color_pool(hints)
    if not pool or not colors:
        return []
    dominant = colors[0]
    pool = sorted(pool, key=lambda s: (*_color_typicality(s, dominant), s.get("it") or ""))
    return pool[:n]


# ---------------------------------------------------------------------------
# Firma visiva (istogrammi HSV + texture)
# ---------------------------------------------------------------------------


def _hist(values: list[float], bins: int, lo: float, hi: float) -> list[float]:
    if not values:
        return [0.0] * bins
    width = (hi - lo) or 1.0
    counts = [0.0] * bins
    for raw in values:
        idx = int((raw - lo) / width * bins)
        if idx >= bins:
            idx = bins - 1
        if idx < 0:
            idx = 0
        counts[idx] += 1.0
    total = sum(counts) or 1.0
    return [c / total for c in counts]


def photo_signature(data: bytes) -> list[float] | None:
    img = _open_rgb(data, 220)
    if img is None:
        return None
    pixels, _meta = isolate_stone(img)
    if not pixels:
        return None
    return _pixels_signature(pixels)


def _pixels_signature(pixels: list[tuple[int, int, int]]) -> list[float]:
    hues: list[float] = []
    sats: list[float] = []
    vals: list[float] = []
    rs = gs = bs = 0.0
    grays: list[float] = []
    n = len(pixels) or 1
    for r, g, b in pixels:
        h, s, v = _hsv(r, g, b)
        sats.append(s)
        vals.append(v)
        if s > 0.16 and v > 0.14:
            hues.append(h)
        rs += r / 255.0
        gs += g / 255.0
        bs += b / 255.0
        grays.append((0.299 * r + 0.587 * g + 0.114 * b) / 255.0)
    hue_h = _hist(hues, HUE_BINS, 0.0, 360.0) if hues else [0.0] * HUE_BINS
    sat_h = _hist(sats, SAT_BINS, 0.0, 1.0)
    val_h = _hist(vals, VAL_BINS, 0.0, 1.0)
    mean_sat = sum(sats) / n
    mean_val = sum(vals) / n
    mean_gray = sum(grays) / n
    texture = math.sqrt(sum((g - mean_gray) ** 2 for g in grays) / n)
    return hue_h + sat_h + val_h + [rs / n, gs / n, bs / n, mean_sat, mean_val, texture]


def _bhatt(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(math.sqrt(max(a[i], 0.0) * max(b[i], 0.0)) for i in range(n))


def signature_similarity(a: list[float], b: list[float]) -> float:
    if len(a) < SIG_LEN or len(b) < SIG_LEN:
        return 0.0
    i0 = 0
    i1 = HUE_BINS
    i2 = i1 + SAT_BINS
    i3 = i2 + VAL_BINS
    hue = _bhatt(a[i0:i1], b[i0:i1])
    sat = _bhatt(a[i1:i2], b[i1:i2])
    val = _bhatt(a[i2:i3], b[i2:i3])
    rgb_l1 = sum(abs(a[i3 + k] - b[i3 + k]) for k in range(3)) / 3.0
    sat_d = abs(a[i3 + 3] - b[i3 + 3])
    val_d = abs(a[i3 + 4] - b[i3 + 4])
    tex_d = abs(a[i3 + 5] - b[i3 + 5])
    score = (
        0.46 * hue
        + 0.14 * sat
        + 0.10 * val
        + 0.16 * (1.0 - min(1.0, rgb_l1 * 2.2))
        + 0.08 * (1.0 - min(1.0, sat_d * 2.0))
        + 0.03 * (1.0 - min(1.0, val_d * 2.0))
        + 0.03 * (1.0 - min(1.0, tex_d * 4.0))
    )
    return max(0.0, min(1.0, score))


def confidence_label(score: float) -> str:
    if score >= 0.68:
        return "corrispondenza visiva buona"
    if score >= 0.48:
        return "corrispondenza media"
    if score >= 0.32:
        return "stesso colore, visivamente debole"
    return "solo vincolo di colore"


# ---------------------------------------------------------------------------
# Cache miniature Wikipedia
# ---------------------------------------------------------------------------


def _load_ref_cache() -> dict[str, Any]:
    if not REF_CACHE.exists():
        return {"version": REF_VERSION, "stones": {}}
    try:
        data = json.loads(REF_CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": REF_VERSION, "stones": {}}
    if not isinstance(data, dict) or data.get("version") != REF_VERSION:
        return {"version": REF_VERSION, "stones": {}}
    stones = data.get("stones")
    if not isinstance(stones, dict):
        data["stones"] = {}
    return data


def _save_ref_cache(data: dict[str, Any]) -> None:
    REF_CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = REF_CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    tmp.replace(REF_CACHE)


def _wiki_titles(stone: dict[str, Any]) -> list[str]:
    titles: list[str] = []
    for key in ("wiki_it", "wiki"):
        title = str(stone.get(key) or "").strip()
        if title and title not in titles:
            titles.append(title)
    return titles


def _english_name(stone: dict[str, Any]) -> str:
    raw = str(stone.get("wiki") or stone.get("it") or "").replace("_", " ")
    return raw.split("(")[0].strip() or str(stone.get("it") or "")


async def _wiki_thumb(client: httpx.AsyncClient, title: str) -> str:
    for lang in ("it", "en"):
        try:
            response = await client.get(
                f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}",
                headers={"Accept": "application/json"},
            )
            if response.status_code == 404:
                continue
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # noqa: BLE001
            logger.info("wiki thumb %s/%s: %s", lang, title, exc)
            continue
        thumb = ""
        if isinstance(data.get("thumbnail"), dict):
            thumb = str(data["thumbnail"].get("source") or "")
        if not thumb and isinstance(data.get("originalimage"), dict):
            thumb = str(data["originalimage"].get("source") or "")
        if thumb:
            return thumb
    return ""


async def _commons_thumbs(client: httpx.AsyncClient, query: str, limit: int = 3) -> list[str]:
    try:
        response = await client.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": "320",
                "format": "json",
            },
            timeout=8.0,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or {}
    except Exception as exc:  # noqa: BLE001
        logger.info("commons %s: %s", query, exc)
        return []
    urls: list[str] = []
    for page in pages.values() if isinstance(pages, dict) else []:
        infos = page.get("imageinfo") or []
        if not infos or not isinstance(infos[0], dict):
            continue
        url = str(infos[0].get("thumburl") or infos[0].get("url") or "")
        if url:
            urls.append(url)
    return urls


def _bytes_sig_color(raw: bytes) -> tuple[list[float] | None, str | None]:
    img = _open_rgb(raw, 220)
    if img is None:
        return None, None
    pixels, _meta = isolate_stone(img)
    if not pixels:
        return None, None
    voted = _vote_colors(pixels)
    color = (voted.get("colors") or [None])[0]
    return _pixels_signature(pixels), color if isinstance(color, str) else None


async def _download_image(client: httpx.AsyncClient, url: str) -> bytes:
    try:
        response = await client.get(
            url,
            headers={"Accept": "image/*,*/*;q=0.8"},
            timeout=8.0,
        )
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.info("img %s: %s", url[:80], exc)
        return b""
    payload = response.content
    if len(payload) < 80 or len(payload) > 2_500_000:
        return b""
    return payload


def _parse_cached_refs(row: Any) -> list[dict[str, Any]] | None:
    if not isinstance(row, dict):
        return None
    raw_refs = row.get("refs")
    if not isinstance(raw_refs, list) or not raw_refs:
        return None
    out: list[dict[str, Any]] = []
    for item in raw_refs:
        if not isinstance(item, dict):
            continue
        sig = item.get("sig")
        if not isinstance(sig, list) or len(sig) != SIG_LEN:
            continue
        try:
            nums = [float(x) for x in sig]
        except (TypeError, ValueError):
            continue
        color = item.get("color")
        out.append({"sig": nums, "color": color if isinstance(color, str) else None})
    return out or None


async def _stone_refs(client: httpx.AsyncClient, stone: dict[str, Any]) -> list[dict[str, Any]]:
    sid = stone["id"]
    async with _ref_lock:
        cached = _parse_cached_refs(_load_ref_cache()["stones"].get(sid))
        if cached:
            return cached
    urls: list[str] = []
    for title in _wiki_titles(stone):
        url = await _wiki_thumb(client, title)
        if url and url not in urls:
            urls.append(url)
    english = _english_name(stone)
    for query in (f"{english} mineral", f"{english} crystal"):
        for url in await _commons_thumbs(client, query, 2):
            if url not in urls:
                urls.append(url)
    refs: list[dict[str, Any]] = []
    for url in urls[:4]:
        raw = await _download_image(client, url)
        sig, color = _bytes_sig_color(raw)
        if not sig:
            continue
        refs.append({"url": url, "sig": [round(x, 5) for x in sig], "color": color})
    if refs:
        async with _ref_lock:
            cache = _load_ref_cache()
            cache["stones"][sid] = {"refs": refs}
            try:
                _save_ref_cache(cache)
            except OSError as exc:
                logger.info("cache refs: %s", exc)
    return _parse_cached_refs({"refs": refs}) or []


async def visual_scores(
    client: httpx.AsyncClient,
    photo_sig: list[float],
    pool: list[dict[str, Any]],
    user_color: str | None = None,
) -> dict[str, float]:
    sem = asyncio.Semaphore(5)

    async def one(stone: dict[str, Any]) -> tuple[str, float]:
        async with sem:
            try:
                refs = await asyncio.wait_for(_stone_refs(client, stone), timeout=14.0)
            except Exception:
                refs = []
        best = 0.0
        matched = False
        for ref in refs:
            sim = signature_similarity(photo_sig, ref["sig"])
            ref_color = ref.get("color")
            if user_color and ref_color and ref_color != user_color:
                sim *= 0.42
            else:
                matched = True
            if sim > best:
                best = sim
        if user_color and refs and not matched:
            best *= 0.65
        return stone["id"], best

    rows = await asyncio.gather(*(one(s) for s in pool))
    return {sid: score for sid, score in rows if score > 0}


# ---------------------------------------------------------------------------
# CLIP zero-shot (Hugging Face, opzionale)
# ---------------------------------------------------------------------------


def _jpeg_bytes(data: bytes, size: int = 224) -> bytes:
    img = _open_rgb(data, size)
    if img is None:
        return b""
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _clip_labels(pool: list[dict[str, Any]]) -> tuple[list[str], dict[str, str]]:
    labels: list[str] = []
    back: dict[str, str] = {}
    for stone in pool:
        it = str(stone.get("it") or "").strip()
        en = _english_name(stone)
        for label in (it, f"{en} mineral" if en else ""):
            if not label or label in back:
                continue
            back[label] = stone["id"]
            labels.append(label)
    return labels[:40], back


def _parse_clip_rows(payload: Any) -> list[tuple[str, float]]:
    rows: list[Any]
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        inner = payload.get("predictions") or payload.get("output") or payload.get("data")
        rows = inner if isinstance(inner, list) else []
    else:
        return []
    out: list[tuple[str, float]] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("class") or "").strip()
        try:
            score = float(item.get("score") or item.get("confidence") or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        if label:
            out.append((label, score))
    return out


async def clip_scores(data: bytes, pool: list[dict[str, Any]]) -> dict[str, float]:
    token = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or "").strip()
    jpeg = _jpeg_bytes(data)
    labels, back = _clip_labels(pool)
    if not jpeg or not labels:
        return {}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    b64 = base64.b64encode(jpeg).decode("ascii")
    payloads = (
        {"inputs": f"data:image/jpeg;base64,{b64}", "parameters": {"candidate_labels": labels}},
        {"inputs": {"image": f"data:image/jpeg;base64,{b64}"}, "parameters": {"candidate_labels": labels}},
        {"image": b64, "parameters": {"candidate_labels": labels}},
    )
    urls = CLIP_URLS if token else CLIP_URLS[:1]
    async with httpx.AsyncClient(timeout=httpx.Timeout(11.0, connect=6.0), follow_redirects=True) as client:
        for url in urls:
            for body in payloads:
                try:
                    response = await client.post(url, headers=headers, json=body)
                except Exception as exc:  # noqa: BLE001
                    logger.info("CLIP %s: %s", url, exc)
                    continue
                if response.status_code in {401, 403, 404}:
                    break
                if response.status_code == 503:
                    continue
                if response.status_code >= 400:
                    continue
                try:
                    parsed = _parse_clip_rows(response.json())
                except Exception:
                    parsed = []
                if not parsed:
                    continue
                scores: dict[str, float] = {}
                for label, score in parsed:
                    sid = back.get(label)
                    if not sid:
                        low = label.lower()
                        sid = next((back[k] for k in back if k.lower() == low), "")
                    if sid:
                        scores[sid] = max(scores.get(sid, 0.0), score)
                if scores:
                    return scores
    return {}


# ---------------------------------------------------------------------------
# Identificazione
# ---------------------------------------------------------------------------


def _color_prior(stone: dict[str, Any], hints: dict[str, Any]) -> float:
    colors = [c for c in hints.get("colors") or [] if c in COLORS]
    dominant = colors[0] if colors else ""
    rank = stone_color_rank(stone, dominant)
    if rank == 0:
        return 0.30
    if rank == 1:
        return 0.12
    if rank == 2:
        return 0.18 if hints.get("multi") else -0.22
    return 0.0


def _norm_prior(prior: float) -> float:
    return max(0.0, min(1.0, (prior + 0.22) / 0.52))


def _blend(
    pool: list[dict[str, Any]],
    visual: dict[str, float],
    clip: dict[str, float],
    hints: dict[str, Any],
) -> list[dict[str, Any]]:
    colors = [c for c in hints.get("colors") or [] if c in COLORS]
    dominant = colors[0] if colors else ""
    has_visual = any(v > 0.05 for v in visual.values())
    has_clip = bool(clip)
    ranked: list[dict[str, Any]] = []
    for stone in pool:
        sid = stone["id"]
        vis = visual.get(sid, 0.0)
        clp = clip.get(sid, 0.0)
        prior = _color_prior(stone, hints)
        rank = stone_color_rank(stone, dominant)
        if rank == 0:
            note = "colore tipico"
        elif rank == 2:
            note = "multicolore"
        else:
            note = "anche di questo colore"
        prior_n = _norm_prior(prior)
        if has_visual and has_clip:
            score = 0.40 * vis + 0.26 * clp + 0.34 * prior_n
            why = f"Wikipedia + CLIP · {note}"
        elif has_visual:
            score = 0.55 * vis + 0.45 * prior_n
            why = f"miniature Wikipedia · {note}"
        elif has_clip:
            score = 0.48 * (0.35 + 0.65 * clp) + 0.52 * prior_n
            why = f"CLIP · {note}"
        else:
            score = 0.22 + prior
            why = f"solo colore · {note}"
        ranked.append({"stone": stone, "score": max(0.0, min(1.0, score)), "why": why})
    ranked.sort(key=lambda row: (-float(row["score"]), row["stone"].get("it") or ""))
    return ranked


async def identify_from_photo(
    client: httpx.AsyncClient | None,
    data: bytes,
    n: int = 3,
) -> dict[str, Any]:
    hints = read_photo_hints(data)
    pool = color_pool(hints)
    empty = {
        "hints": hints,
        "guesses": [],
        "method": "none",
        "clip": False,
        "visual": False,
    }
    if not pool:
        return empty
    photo_sig = photo_signature(data)
    visual: dict[str, float] = {}
    clip: dict[str, float] = {}

    async def _visual() -> dict[str, float]:
        if client is None or photo_sig is None:
            return {}
        try:
            color = next((c for c in (hints.get("colors") or []) if c in COLORS), None)
            return await visual_scores(client, photo_sig, pool, user_color=color)
        except Exception as exc:  # noqa: BLE001
            logger.info("visual match: %s", exc)
            return {}

    async def _clip() -> dict[str, float]:
        try:
            return await clip_scores(data, pool)
        except Exception as exc:  # noqa: BLE001
            logger.info("CLIP: %s", exc)
            return {}

    try:
        visual, clip = await asyncio.wait_for(
            asyncio.gather(_visual(), _clip()),
            timeout=16.0,
        )
    except TimeoutError:
        logger.info("identify timeout: uso quello che c'è")
    ranked = _blend(pool, visual, clip, hints)
    top = ranked[:n]
    if visual and clip:
        method = "wiki+clip"
    elif visual:
        method = "wiki"
    elif clip:
        method = "clip"
    else:
        method = "color"
    return {
        "hints": hints,
        "guesses": [row["stone"] for row in top],
        "details": top,
        "method": method,
        "clip": bool(clip),
        "visual": bool(visual),
    }
