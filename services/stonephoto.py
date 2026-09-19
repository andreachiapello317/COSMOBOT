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
REF_VERSION = 2
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
    # Ottone/oro: sat media. Un giallo saturo da gemma (citrino) non è metallico.
    gold = 36 <= hue <= 54 and 0.22 <= sat <= 0.58 and val > 0.38
    silver = sat < 0.14 and 0.40 < val < 0.88 and abs(r - g) < 16 and abs(g - b) < 16
    return gold or silver


def _center_pixels(img: Any) -> list[tuple[int, int, int]]:
    w, h = img.size
    x0, x1 = int(w * 0.22), int(w * 0.78)
    y0, y1 = int(h * 0.22), int(h * 0.78)
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


def read_photo_hints(data: bytes) -> dict[str, Any]:
    img = _open_rgb(data, 160)
    if img is None:
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


def color_pool(hints: dict[str, Any]) -> list[dict[str, Any]]:
    colors = [c for c in hints.get("colors") or [] if c in COLORS]
    if not colors:
        return []
    dominant = colors[0]
    pool = [s for s in STONES if stone_fits_color(s, dominant)]
    if hints.get("metallic"):
        metal = [s for s in pool if s.get("metallic")]
        if metal:
            pool = metal
    return pool


def _color_typicality(stone: dict[str, Any], key: str) -> tuple[int, int]:
    cols = [c for c in (stone.get("colors") or ()) if c not in {"multi", "change"}]
    extra = max(0, len(cols) - 1)
    head = 0 if (stone.get("colors") or (None,))[0] == key else 1
    return (head, extra)


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
    img = _open_rgb(data, 192)
    if img is None:
        return None
    pixels = _center_pixels(img)
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


async def _stone_ref_signature(client: httpx.AsyncClient, stone: dict[str, Any]) -> list[float] | None:
    sid = stone["id"]
    async with _ref_lock:
        cache = _load_ref_cache()
        row = cache["stones"].get(sid)
        if isinstance(row, dict):
            sig = row.get("sig")
            if isinstance(sig, list) and len(sig) == SIG_LEN:
                try:
                    return [float(x) for x in sig]
                except (TypeError, ValueError):
                    pass
    url = ""
    for title in _wiki_titles(stone):
        url = await _wiki_thumb(client, title)
        if url:
            break
    if not url:
        return None
    raw = await _download_image(client, url)
    sig = photo_signature(raw)
    if not sig:
        return None
    async with _ref_lock:
        cache = _load_ref_cache()
        cache["stones"][sid] = {"url": url, "sig": [round(x, 5) for x in sig]}
        try:
            _save_ref_cache(cache)
        except OSError as exc:
            logger.info("cache refs: %s", exc)
    return sig


async def visual_scores(
    client: httpx.AsyncClient,
    photo_sig: list[float],
    pool: list[dict[str, Any]],
) -> dict[str, float]:
    sem = asyncio.Semaphore(6)

    async def one(stone: dict[str, Any]) -> tuple[str, float]:
        async with sem:
            try:
                ref = await asyncio.wait_for(_stone_ref_signature(client, stone), timeout=9.0)
            except Exception:
                ref = None
        if not ref:
            return stone["id"], 0.0
        return stone["id"], signature_similarity(photo_sig, ref)

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
        if has_visual and has_clip:
            score = 0.55 * vis + 0.45 * clp
            why = "miniature Wikipedia + CLIP"
        elif has_visual:
            score = vis
            why = "miniature Wikipedia"
        elif has_clip:
            score = 0.35 + 0.65 * clp
            why = "modello visivo CLIP"
        else:
            typ = _color_typicality(stone, dominant)
            score = 0.22 - 0.04 * typ[0] - 0.03 * typ[1]
            why = "solo colore del catalogo"
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
            return await visual_scores(client, photo_sig, pool)
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
