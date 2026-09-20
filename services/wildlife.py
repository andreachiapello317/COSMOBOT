"""Avvistamenti animali live. iNaturalist pubblico, niente zoo inventato."""

from __future__ import annotations

import html as _html
from typing import Any

import httpx

INAT_URL = "https://api.inaturalist.org/v1/observations"


class WildlifeError(RuntimeError):
    """Feed animali non usabile."""


async def recent_animals(client: httpx.AsyncClient, *, limit: int = 8) -> list[dict[str, Any]]:
    try:
        response = await client.get(
            INAT_URL,
            params={
                "iconic_taxa": "Animalia",
                "lrank": "species",
                "order": "desc",
                "order_by": "observed_on",
                "per_page": str(max(limit * 3, 24)),
                "photos": "true",
                "locale": "it",
            },
            headers={"User-Agent": "StelleBot/1.0 (Telegram; educational; iNaturalist observations)"},
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise WildlifeError("iNaturalist non ha risposto") from exc
    rows = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise WildlifeError("iNaturalist vuoto")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in rows:
        if not isinstance(item, dict):
            continue
        taxon = item.get("taxon") if isinstance(item.get("taxon"), dict) else {}
        rank = str(taxon.get("rank") or "").lower()
        if rank not in {"species", "subspecies", "variety", "hybrid"}:
            continue
        name = str(taxon.get("preferred_common_name") or taxon.get("name") or "").strip()
        if not name or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        place = str(item.get("place_guess") or "").strip()
        when = str(item.get("observed_on") or item.get("time_observed_at") or "").strip()
        uri = str(item.get("uri") or "").strip()
        out.append({"name": name, "place": place, "when": when, "uri": uri})
        if len(out) >= limit:
            break
    if not out:
        raise WildlifeError("Nessun avvistamento in questo giro")
    return out


def format_animals_card(rows: list[dict[str, Any]]) -> str:
    lines = [
        "🐾 <b>ANIMALI LIVE</b>",
        "Avvistamenti recenti, iNaturalist. Non è un atlante e non è lo zoo.",
        "",
    ]
    for row in rows:
        name = _html.escape(str(row.get("name") or "animale"))
        place = _html.escape(str(row.get("place") or "luogo non indicato"))
        when = _html.escape(str(row.get("when") or "")[:10])
        uri = str(row.get("uri") or "")
        bit = f" · {when}" if when else ""
        if uri.startswith("http"):
            lines.append(f"🐾 <b>{name}</b> — {place}{bit}")
            lines.append(f"   <a href=\"{_html.escape(uri)}\">scheda</a>")
        else:
            lines.append(f"🐾 <b>{name}</b> — {place}{bit}")
    lines.extend(["", "<i>Fonte live: iNaturalist.org. Solo ciò che hanno pubblicato.</i>"])
    return "\n".join(lines)
