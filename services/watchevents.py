"""Eventi e 'stasera' da effemeridi reali. Niente calendari inventati."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import astronomy

from services.astronomy import visibility_stars
from services.moon import moon_now, next_quarters
from services.skycatalog import SkyFrame, constellation_segments, visible_stars
from services.weather import wmo_label

PLANET_SCAN = (
    (astronomy.Body.Mercury, "Mercurio", "☿️"),
    (astronomy.Body.Venus, "Venere", "♀️"),
    (astronomy.Body.Mars, "Marte", "♂️"),
    (astronomy.Body.Jupiter, "Giove", "♃"),
    (astronomy.Body.Saturn, "Saturno", "♄"),
    (astronomy.Body.Uranus, "Urano", "♅"),
    (astronomy.Body.Neptune, "Nettuno", "♆"),
)


def angular_sep(alt1: float, az1: float, alt2: float, az2: float) -> float:
    a1, z1 = math.radians(alt1), math.radians(az1)
    a2, z2 = math.radians(alt2), math.radians(az2)
    cos = math.sin(a1) * math.sin(a2) + math.cos(a1) * math.cos(a2) * math.cos(z1 - z2)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def _body_row(frame: SkyFrame, body: astronomy.Body, name: str, emoji: str) -> dict[str, Any]:
    alt, az, ra, dec = frame.body_altaz(body)
    ill = astronomy.Illumination(body, frame.moment)
    elong = astronomy.Elongation(body, frame.moment)
    return {
        "name": name,
        "emoji": emoji,
        "alt": alt,
        "az": az,
        "ra": ra,
        "dec": dec,
        "mag": float(ill.mag) if ill.mag is not None else None,
        "elong": float(elong.elongation),
    }


def snapshot(lat: float, lon: float, when: datetime) -> dict[str, Any]:
    frame = SkyFrame(lat, lon, when)
    sun_alt, sun_az, _ra, _dec = frame.body_altaz(astronomy.Body.Sun)
    moon = _body_row(frame, astronomy.Body.Moon, "Luna", "🌙")
    phase = moon_now(when)
    moon["phase"] = phase.get("name")
    moon["phase_emoji"] = phase.get("emoji")
    moon["illum"] = phase.get("illum")
    planets = [_body_row(frame, body, name, emoji) for body, name, emoji in PLANET_SCAN]
    return {
        "sun_alt": sun_alt,
        "sun_az": sun_az,
        "moon": moon,
        "planets": planets,
        "stars": visible_stars(frame, limit=16),
        "figures": [fig for fig in constellation_segments(frame) if fig["alt"] > 20][:8],
        "night": sun_alt < -0.5,
    }


def tonight_picks(
    snap: dict[str, Any],
    *,
    weather: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], str, str, float | None]:
    current = weather.get("current") if isinstance(weather, dict) and isinstance(weather.get("current"), dict) else {}
    emoji, sky = wmo_label(current.get("weather_code"))
    try:
        cloud_f = float(current["cloud_cover"]) if current.get("cloud_cover") is not None else None
    except (TypeError, ValueError):
        cloud_f = None

    def score(alt: float, mag: float | None) -> str:
        bar = visibility_stars(altitude=alt, magnitude=mag)
        pts = bar.count("⭐")
        if cloud_f is not None and cloud_f >= 80:
            pts = max(1, pts - 2)
        elif cloud_f is not None and cloud_f >= 50:
            pts = max(1, pts - 1)
        return "⭐" * pts + "☆" * (5 - pts)

    picks: list[dict[str, Any]] = []
    moon = snap["moon"]
    if moon["alt"] > 0:
        illum = moon.get("illum")
        detail = str(moon.get("phase") or "Luna")
        if isinstance(illum, (int, float)):
            detail = f"{detail} · illum. {illum:.0f}%"
        picks.append(
            {
                "title": "Luna",
                "emoji": moon.get("phase_emoji") or "🌙",
                "alt": moon["alt"],
                "az": moon["az"],
                "stars": score(moon["alt"], None),
                "detail": detail,
            }
        )
    for row in snap["planets"]:
        if row["alt"] <= 8:
            continue
        mag = row.get("mag") if isinstance(row.get("mag"), (int, float)) else None
        bar = score(row["alt"], mag)
        if bar.count("⭐") < 2 and row["name"] in {"Urano", "Nettuno"}:
            continue
        picks.append(
            {
                "title": row["name"],
                "emoji": row["emoji"],
                "alt": row["alt"],
                "az": row["az"],
                "stars": bar,
                "detail": f"mag {mag:.1f}" if mag is not None else "",
            }
        )
    for fig in snap["figures"][:3]:
        picks.append(
            {
                "title": fig["name"],
                "emoji": "⭐",
                "alt": fig["alt"],
                "az": None,
                "stars": score(fig["alt"], 2.0),
                "detail": "figura sopra l'orizzonte",
            }
        )
    picks.sort(key=lambda row: (-str(row["stars"]).count("⭐"), -float(row["alt"])))
    return picks[:8], emoji, sky, cloud_f


def upcoming_events(lat: float, lon: float, when: datetime, tz: ZoneInfo) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for row in next_quarters(when, 4):
        stamp = row["when"].astimezone(tz)
        events.append(
            {
                "id": f"q:{stamp.date().isoformat()}",
                "kind": "luna",
                "title": row["name"],
                "emoji": row["emoji"],
                "when": stamp,
                "detail": "Quarto lunare (Astronomy Engine).",
                "bodies": ["Luna"],
            }
        )
    start = astronomy.Time.Make(when.year, when.month, when.day, when.hour, when.minute, when.second)
    try:
        eclipse = astronomy.SearchLunarEclipse(start)
        for _ in range(2):
            peak = eclipse.peak.Utc()
            if peak.tzinfo is None:
                peak = peak.replace(tzinfo=timezone.utc)
            peak = peak.astimezone(tz)
            frame = SkyFrame(lat, lon, peak)
            moon_alt, _az, _ra, _dec = frame.body_altaz(astronomy.Body.Moon)
            sun_alt, _saz, _sra, _sdec = frame.body_altaz(astronomy.Body.Sun)
            kind = {
                "Penumbral": "penombrale",
                "Partial": "parziale",
                "Total": "totale",
                "Annular": "anulare",
            }.get(getattr(eclipse.kind, "name", ""), "lunare")
            if moon_alt > 0 and sun_alt < 0:
                events.append(
                    {
                        "id": f"ecl:{peak.date().isoformat()}",
                        "kind": "eclissi",
                        "title": f"Eclissi lunare {kind}",
                        "emoji": "🌕",
                        "when": peak,
                        "detail": f"Da qui la Luna è sopra ({moon_alt:.0f}°) e il Sole sotto al picco.",
                        "bodies": ["Luna"],
                        "alt": moon_alt,
                    }
                )
            eclipse = astronomy.NextLunarEclipse(eclipse.peak)
    except Exception:
        pass

    seen: set[str] = set()
    cursor = when.astimezone(timezone.utc)
    for step in range(0, 14 * 4):
        instant = cursor + timedelta(hours=6 * step)
        frame = SkyFrame(lat, lon, instant)
        bodies = [_body_row(frame, astronomy.Body.Moon, "Luna", "🌙")]
        bodies.extend(_body_row(frame, body, name, emoji) for body, name, emoji in PLANET_SCAN)
        up = [item for item in bodies if item["alt"] > 0]
        for i, left in enumerate(up):
            for right in up[i + 1 :]:
                if {left["name"], right["name"]} == {"Urano", "Nettuno"}:
                    continue
                sep = angular_sep(left["alt"], left["az"], right["alt"], right["az"])
                if sep > 6:
                    continue
                pair = f"{min(left['name'], right['name'])}-{max(left['name'], right['name'])}"
                if pair in seen:
                    continue
                seen.add(pair)
                local = instant.astimezone(tz)
                events.append(
                    {
                        "id": f"c:{pair}:{local.date()}",
                        "kind": "cong",
                        "title": f"Congiunzione {left['name']}–{right['name']}",
                        "emoji": "✨",
                        "when": local,
                        "detail": f"Separazione {sep:.1f}° sulla volta, entrambi sopra l'orizzonte.",
                        "bodies": [left["name"], right["name"]],
                        "alt": left["alt"],
                        "az": left["az"],
                        "sep": sep,
                    }
                )
        for row in bodies:
            if row["name"] == "Luna":
                continue
            elong = row.get("elong")
            if not (isinstance(elong, (int, float)) and elong >= 172 and row["alt"] > 0):
                continue
            key = f"opp-{row['name']}"
            if key in seen:
                continue
            seen.add(key)
            local = instant.astimezone(tz)
            events.append(
                {
                    "id": f"o:{row['name']}:{local.date()}",
                    "kind": "opp",
                    "title": f"Opposizione di {row['name']}",
                    "emoji": row["emoji"],
                    "when": local,
                    "detail": f"Elongazione solare {elong:.0f}°. {row['name']} è sopra ({row['alt']:.0f}°).",
                    "bodies": [row["name"]],
                    "alt": row["alt"],
                    "az": row["az"],
                }
            )
    events.sort(key=lambda row: row["when"])
    return events[:12]
