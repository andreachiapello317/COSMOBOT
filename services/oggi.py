"""Mercati e notizie per il bot OGGI. Solo feed pubblici, niente prezzi inventati."""

from __future__ import annotations

import asyncio
import html
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import quote
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

import httpx

ROME = ZoneInfo("Europe/Rome")
UA = "StelleBot/1.0 (Telegram; educational; OGGI markets+news)"
YAHOO_UA = "Mozilla/5.0 (compatible; StelleBot/1.0; educational)"

FRANKFURTER = "https://api.frankfurter.app/latest"
COINGECKO = "https://api.coingecko.com/api/v3/simple/price"
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
GOLD_API = "https://api.gold-api.com/price/{symbol}"

PAGE_SIZE = 5
MAX_NEWS = 15
CACHE_TTL = 90.0

FX_QUOTES = ("USD", "GBP", "CHF", "JPY")
FX_LABEL = {"USD": "Dollaro USA", "GBP": "Sterlina", "CHF": "Franco svizzero", "JPY": "Yen"}

CRYPTO = (
    ("bitcoin", "Bitcoin", "BTC"),
    ("ethereum", "Ethereum", "ETH"),
    ("solana", "Solana", "SOL"),
    ("ripple", "XRP", "XRP"),
)

INDICES = (
    ("FTSEMIB.MI", "FTSE MIB", "🇮🇹"),
    ("%5EGSPC", "S&P 500", "🇺🇸"),
    ("%5EIXIC", "NASDAQ", "🇺🇸"),
    ("%5EGDAXI", "DAX", "🇩🇪"),
    ("%5EFTSE", "FTSE 100", "🇬🇧"),
)

METALS = (
    ("XAU", "Oro"),
    ("XAG", "Argento"),
    ("XPT", "Platino"),
    ("XPD", "Palladio"),
)

OILS = (
    ("CL=F", "Petrolio WTI"),
    ("BZ=F", "Petrolio Brent"),
)

NEWS_FEEDS: dict[str, dict[str, str]] = {
    "it": {
        "emoji": "🇮🇹",
        "name": "Italia",
        "source": "ANSA",
        "url": "https://www.ansa.it/sito/ansait_rss.xml",
    },
    "wo": {
        "emoji": "🌍",
        "name": "Mondo",
        "source": "ANSA Mondo",
        "url": "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
    },
    "ec": {
        "emoji": "💹",
        "name": "Economia",
        "source": "ANSA Economia",
        "url": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml",
    },
    "sc": {
        "emoji": "🔬",
        "name": "Tecnologia",
        "source": "ANSA Tecnologia",
        "url": "https://www.ansa.it/sito/notizie/tecnologia/tecnologia_rss.xml",
    },
    "gn": {
        "emoji": "📰",
        "name": "Rassegna",
        "source": "Google News Italia",
        "url": "https://news.google.com/rss?hl=it&gl=IT&ceid=IT:it",
    },
}

SEARCH_HINTS: tuple[tuple[str, str, str], ...] = (
    ("usd", "m", "fx"),
    ("dollaro", "m", "fx"),
    ("sterlina", "m", "fx"),
    ("yen", "m", "fx"),
    ("franco", "m", "fx"),
    ("eur", "m", "fx"),
    ("euro", "m", "fx"),
    ("btc", "m", "cr"),
    ("bitcoin", "m", "cr"),
    ("eth", "m", "cr"),
    ("ethereum", "m", "cr"),
    ("sol", "m", "cr"),
    ("solana", "m", "cr"),
    ("xrp", "m", "cr"),
    ("mib", "m", "ix"),
    ("ftse", "m", "ix"),
    ("nasdaq", "m", "ix"),
    ("s&p", "m", "ix"),
    ("sp500", "m", "ix"),
    ("dax", "m", "ix"),
    ("oro", "m", "mt"),
    ("gold", "m", "mt"),
    ("argento", "m", "mt"),
    ("petrolio", "m", "mt"),
    ("wti", "m", "mt"),
    ("brent", "m", "mt"),
)

_cache: dict[str, tuple[float, Any]] = {}


def _e(text: str) -> str:
    return html.escape(str(text or ""), quote=False)


def _get(key: str) -> Any | None:
    item = _cache.get(key)
    if not item:
        return None
    ts, value = item
    if time.monotonic() - ts > CACHE_TTL:
        _cache.pop(key, None)
        return None
    return value


def _set(key: str, value: Any) -> Any:
    _cache[key] = (time.monotonic(), value)
    return value


def _headers(*, yahoo: bool = False) -> dict[str, str]:
    return {
        "User-Agent": YAHOO_UA if yahoo else UA,
        "Accept": "application/json, application/xml, text/xml, */*",
    }


def _fmt_num(value: float, *, digits: int = 2) -> str:
    if abs(value) >= 1000:
        text = f"{value:,.2f}"
    else:
        text = f"{value:.{digits}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_change(pct: float | None) -> str:
    if pct is None:
        return "—"
    arrow = "▲" if pct > 0 else "▼" if pct < 0 else "▶"
    return f"{arrow} {pct:+.2f}%".replace(".", ",")


def _when(ts: datetime | None) -> str:
    if ts is None:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(ROME).strftime("%d/%m %H:%M")


def resolve_search(query: str) -> str | None:
    blob = (query or "").strip().lower()
    if len(blob) < 2:
        return None
    for needle, _kind, key in SEARCH_HINTS:
        if needle in blob:
            return key
    return None


async def fetch_fx(client: httpx.AsyncClient) -> dict[str, Any]:
    cached = _get("fx")
    if cached is not None:
        return cached
    response = await client.get(
        FRANKFURTER,
        params={"from": "EUR", "to": ",".join(FX_QUOTES)},
        headers=_headers(),
    )
    response.raise_for_status()
    payload = response.json()
    rates = payload.get("rates") if isinstance(payload, dict) else None
    if not isinstance(rates, dict):
        raise ValueError("frankfurter")
    rows = []
    for code in FX_QUOTES:
        raw = rates.get(code)
        if raw is None:
            continue
        value = float(raw)
        rows.append({"code": code, "name": FX_LABEL[code], "per_eur": value, "eur_per": 1.0 / value})
    data = {"date": str(payload.get("date") or ""), "rows": rows}
    return _set("fx", data)


async def fetch_crypto(client: httpx.AsyncClient) -> list[dict[str, Any]]:
    cached = _get("cr")
    if cached is not None:
        return cached
    ids = ",".join(item[0] for item in CRYPTO)
    response = await client.get(
        COINGECKO,
        params={"ids": ids, "vs_currencies": "eur,usd", "include_24hr_change": "true"},
        headers=_headers(),
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("coingecko")
    rows = []
    for cid, name, ticker in CRYPTO:
        block = payload.get(cid)
        if not isinstance(block, dict) or block.get("eur") is None:
            continue
        rows.append(
            {
                "id": cid,
                "name": name,
                "ticker": ticker,
                "eur": float(block["eur"]),
                "usd": float(block.get("usd") or 0),
                "chg": float(block["eur_24h_change"]) if block.get("eur_24h_change") is not None else None,
            }
        )
    return _set("cr", rows)


async def _yahoo_quote(client: httpx.AsyncClient, symbol: str) -> dict[str, Any] | None:
    url = YAHOO_CHART.format(symbol=symbol)
    response = await client.get(
        url,
        params={"interval": "1d", "range": "5d"},
        headers=_headers(yahoo=True),
    )
    response.raise_for_status()
    payload = response.json()
    chart = payload.get("chart") if isinstance(payload, dict) else None
    results = chart.get("result") if isinstance(chart, dict) else None
    if not isinstance(results, list) or not results:
        return None
    meta = results[0].get("meta") if isinstance(results[0], dict) else None
    if not isinstance(meta, dict) or meta.get("regularMarketPrice") is None:
        return None
    price = float(meta["regularMarketPrice"])
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    prev_f = float(prev) if prev is not None else None
    chg = ((price - prev_f) / prev_f * 100.0) if prev_f else None
    when = None
    raw_ts = meta.get("regularMarketTime")
    if raw_ts:
        when = datetime.fromtimestamp(int(raw_ts), tz=timezone.utc)
    return {
        "symbol": str(meta.get("symbol") or symbol),
        "name": str(meta.get("shortName") or meta.get("longName") or symbol),
        "currency": str(meta.get("currency") or ""),
        "price": price,
        "chg": chg,
        "when": when,
    }


async def fetch_indices(client: httpx.AsyncClient) -> list[dict[str, Any]]:
    cached = _get("ix")
    if cached is not None:
        return cached

    async def one(symbol: str, name: str, flag: str) -> dict[str, Any] | None:
        try:
            quote = await _yahoo_quote(client, symbol)
        except Exception:
            return None
        if quote is None:
            return None
        quote["label"] = name
        quote["flag"] = flag
        return quote

    fetched = await asyncio.gather(*(one(symbol, name, flag) for symbol, name, flag in INDICES))
    rows = [row for row in fetched if row]
    return _set("ix", rows)


async def fetch_metals(client: httpx.AsyncClient) -> dict[str, list[dict[str, Any]]]:
    cached = _get("mt")
    if cached is not None:
        return cached
    async def spot(symbol: str, name: str) -> dict[str, Any] | None:
        try:
            response = await client.get(GOLD_API.format(symbol=symbol), headers=_headers())
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return None
        if not isinstance(payload, dict) or payload.get("price") is None:
            return None
        when = None
        raw = str(payload.get("updatedAt") or "")
        if raw:
            try:
                when = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                when = None
        return {
            "symbol": symbol,
            "name": name,
            "price": float(payload["price"]),
            "currency": str(payload.get("currency") or "USD"),
            "when": when,
        }

    async def oil(symbol: str, name: str) -> dict[str, Any] | None:
        try:
            row = await _yahoo_quote(client, quote(symbol, safe=""))
        except Exception:
            return None
        if row is None:
            return None
        row["label"] = name
        return row

    fetched_spots = await asyncio.gather(*(spot(symbol, name) for symbol, name in METALS))
    fetched_oils = await asyncio.gather(*(oil(symbol, name) for symbol, name in OILS))
    spots = [row for row in fetched_spots if row]
    oils = [row for row in fetched_oils if row]
    data = {"spots": spots, "oils": oils}
    return _set("mt", data)


def _parse_rss(xml_text: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, Any]] = []
    for node in root.findall("./channel/item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        if not title or not link:
            continue
        when = None
        raw = (node.findtext("pubDate") or "").strip()
        if raw:
            try:
                when = parsedate_to_datetime(raw)
            except (TypeError, ValueError):
                when = None
        source = (node.findtext("source") or "").strip()
        items.append({"title": title, "link": link, "when": when, "source": source})
        if len(items) >= MAX_NEWS:
            break
    return items


async def fetch_news(client: httpx.AsyncClient, key: str) -> list[dict[str, Any]]:
    meta = NEWS_FEEDS.get(key)
    if meta is None:
        return []
    cache_key = f"nw:{key}"
    cached = _get(cache_key)
    if cached is not None:
        return cached
    response = await client.get(meta["url"], headers=_headers())
    response.raise_for_status()
    rows = _parse_rss(response.text)
    return _set(cache_key, rows)


def format_fx(data: dict[str, Any]) -> str:
    lines = [
        "💱 <b>VALUTE</b>",
        "<i>Tassi di riferimento BCE via Frankfurter. Non è un prezzo di sportello.</i>",
        "",
    ]
    day = data.get("date") or ""
    if day:
        lines.append(f"📅 Riferimento { _e(day) }")
        lines.append("")
    for row in data.get("rows") or []:
        lines.append(
            f"💶 1 EUR = <b>{_fmt_num(row['per_eur'], digits=4)}</b> {row['code']} · {_e(row['name'])}"
        )
        lines.append(f"   1 {row['code']} = {_fmt_num(row['eur_per'], digits=4)} EUR")
        lines.append("")
    if len(lines) <= 5:
        lines.append("Frankfurter non ha risposto. Non invento i cambi.")
    else:
        lines.append("<i>European Central Bank, aggiornamento feriale.</i>")
    return "\n".join(lines).strip()


def format_crypto(rows: list[dict[str, Any]]) -> str:
    lines = [
        "🪙 <b>CRYPTO</b>",
        "<i>CoinGecko, prezzi medi di mercato. Non è un exchange e non è un consiglio.</i>",
        "",
    ]
    for row in rows:
        lines.append(
            f"{row['ticker']} <b>{_e(row['name'])}</b>  {_fmt_change(row.get('chg'))}"
        )
        lines.append(f"   {_fmt_num(row['eur'])} EUR · {_fmt_num(row['usd'])} USD")
        lines.append("")
    if not rows:
        lines.append("CoinGecko non ha risposto. Non invento le quotazioni.")
    else:
        lines.append("<i>Variazione sulle 24 ore, in euro.</i>")
    return "\n".join(lines).strip()


def format_indices(rows: list[dict[str, Any]]) -> str:
    lines = [
        "📈 <b>INDICI</b>",
        "<i>Yahoo Finance chart. Quotazione dell'indice, non un listino certificato.</i>",
        "",
    ]
    for row in rows:
        cur = row.get("currency") or ""
        when = _when(row.get("when"))
        extra = f" · {when}" if when else ""
        lines.append(
            f"{row.get('flag') or '📈'} <b>{_e(row.get('label') or row['name'])}</b>  {_fmt_change(row.get('chg'))}"
        )
        lines.append(f"   {_fmt_num(row['price'])} {cur}{extra}")
        lines.append("")
    if not rows:
        lines.append("Yahoo non ha risposto. Non invento gli indici.")
    return "\n".join(lines).strip()


def format_metals(data: dict[str, list[dict[str, Any]]]) -> str:
    lines = [
        "🥇 <b>MATERIE</b>",
        "<i>Metalli: gold-api.com (USD/oncia). Petrolio: future Yahoo. Non è un ordine di borsa.</i>",
        "",
    ]
    for row in data.get("spots") or []:
        when = _when(row.get("when"))
        extra = f" · {when}" if when else ""
        lines.append(f"⚪ <b>{_e(row['name'])}</b> ({row['symbol']})")
        lines.append(f"   {_fmt_num(row['price'])} {row['currency']}/oz{extra}")
        lines.append("")
    for row in data.get("oils") or []:
        when = _when(row.get("when"))
        extra = f" · {when}" if when else ""
        lines.append(
            f"🛢️ <b>{_e(row.get('label') or row['name'])}</b>  {_fmt_change(row.get('chg'))}"
        )
        lines.append(f"   {_fmt_num(row['price'])} {row.get('currency') or 'USD'}{extra}")
        lines.append("")
    if len(lines) <= 4:
        lines.append("I feed materie non rispondono. Non invento i prezzi.")
    return "\n".join(lines).strip()


def format_news(key: str, rows: list[dict[str, Any]], *, page: int = 0) -> str:
    meta = NEWS_FEEDS.get(key) or {"emoji": "📰", "name": "Notizie", "source": "RSS"}
    total = len(rows)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE) if total else 1
    page = max(0, min(page, pages - 1))
    chunk = rows[page * PAGE_SIZE : page * PAGE_SIZE + PAGE_SIZE]
    lines = [
        f"{meta['emoji']} <b>{_e(meta['name']).upper()}</b>",
        f"<i>Titoli RSS di { _e(meta['source']) }. Non li scriviamo noi e non sono un verdetto.</i>",
        "",
    ]
    if not chunk:
        lines.append("Il feed è vuoto o non risponde. Non invento le notizie.")
        return "\n".join(lines)
    for idx, item in enumerate(chunk, start=page * PAGE_SIZE + 1):
        when = _when(item.get("when"))
        src = item.get("source") or ""
        bits = [bit for bit in (when, src) if bit]
        lines.append(f"{idx}. {_e(item['title'])}")
        if bits:
            lines.append(f"   {' · '.join(_e(bit) for bit in bits)}")
        lines.append("")
    lines.append(f"<i>Pagina {page + 1}/{pages}. Tocca un titolo per aprire la fonte.</i>")
    return "\n".join(lines).strip()


def news_page_count(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 1
    return max(1, (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE)
