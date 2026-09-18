"""Wikipedia, Wikidata e NASA Images: testi e misure live, niente schede inventate."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("stellebot.wiki")

UNIT_IT = {
    "Q828224": "km",
    "Q573": "giorni",
    "Q25235": "ore",
    "Q1811": "au",
    "Q28390": "g (gravità terrestre)",
    "Q844211": "kg/m³",
    "Q613726": "×10²¹ kg",
    "Q11573": "m",
    "Q11574": "kg",
    "Q37141": "pc",
    "Q12129": "al",
    "Q3674704": "km/s",
    "Q23387": "km",
}

FACT_PROPS = (
    ("P2067", "Massa"),
    ("P2120", "Raggio"),
    ("P2045", "Gravità"),
    ("P2147", "Giorno (rotazione)"),
    ("P2146", "Anno (orbita)"),
    ("P2233", "Semiasse maggiore"),
    ("P2054", "Densità"),
    ("P2052", "Velocità di fuga"),
    ("P2583", "Distanza"),
    ("P1096", "Eccentricità"),
)


def _quantity(claim: dict[str, Any]) -> tuple[str, str] | None:
    try:
        value = claim["mainsnak"]["datavalue"]["value"]
    except (KeyError, TypeError):
        return None
    if not isinstance(value, dict) or "amount" not in value:
        return None
    amount = str(value["amount"]).lstrip("+")
    unit_id = str(value.get("unit") or "").rsplit("/", 1)[-1]
    unit = UNIT_IT.get(unit_id, "")
    return amount, unit


async def wikipedia_summary(client: httpx.AsyncClient, title: str) -> dict[str, str] | None:
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
            logger.info("Wikipedia %s/%s: %s", lang, title, exc)
            continue
        extract = str(data.get("extract") or "").strip()
        if not extract:
            continue
        thumb = ""
        if isinstance(data.get("originalimage"), dict):
            thumb = str(data["originalimage"].get("source") or "")
        elif isinstance(data.get("thumbnail"), dict):
            thumb = str(data["thumbnail"].get("source") or "")
        return {
            "title": str(data.get("title") or title),
            "extract": extract,
            "url": str((data.get("content_urls") or {}).get("desktop", {}).get("page") or ""),
            "image": thumb,
            "lang": lang,
        }
    return None


async def wikidata_facts(client: httpx.AsyncClient, qid: str) -> list[tuple[str, str]]:
    try:
        response = await client.get(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbgetentities",
                "ids": qid,
                "props": "claims",
                "format": "json",
            },
        )
        response.raise_for_status()
        claims = (((response.json().get("entities") or {}).get(qid) or {}).get("claims")) or {}
    except Exception as exc:  # noqa: BLE001
        logger.info("Wikidata %s: %s", qid, exc)
        return []
    out: list[tuple[str, str]] = []
    for prop, label in FACT_PROPS:
        rows = claims.get(prop)
        if not isinstance(rows, list) or not rows:
            continue
        parsed = _quantity(rows[0])
        if not parsed:
            continue
        amount, unit = parsed
        out.append((label, f"{amount} {unit}".strip()))
    return out


async def nasa_image(client: httpx.AsyncClient, query: str) -> dict[str, str] | None:
    try:
        response = await client.get(
            "https://images-api.nasa.gov/search",
            params={"q": query, "media_type": "image", "page_size": 5},
        )
        response.raise_for_status()
        items = ((response.json().get("collection") or {}).get("items") or [])
    except Exception as exc:  # noqa: BLE001
        logger.info("NASA images %s: %s", query, exc)
        return None
    for item in items:
        if not isinstance(item, dict):
            continue
        data = (item.get("data") or [{}])[0]
        links = item.get("links") or []
        href = ""
        for link in links:
            if isinstance(link, dict) and link.get("render") == "image":
                href = str(link.get("href") or "")
                break
        if not href and links and isinstance(links[0], dict):
            href = str(links[0].get("href") or "")
        if not href:
            continue
        return {
            "title": str(data.get("title") or query),
            "description": str(data.get("description") or "")[:500],
            "href": href,
            "nasa_id": str(data.get("nasa_id") or ""),
        }
    return None
