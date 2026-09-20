"""Eventi e 'stasera' da effemeridi reali. Niente calendari inventati."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import astronomy

from services.astronomy import visibility_stars
from services.moon import moon_now, next_quarters
from services.skycatalog import SkyFrame, constellation_name, constellation_segments, visible_stars
from services.skychart import eye_level
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


# Fasce diverse: non le stesse 4 stelle luminose in tutti i gradi.
_STAR_RULES = {
    "easy": {"mag_lo": -2.0, "mag_hi": 1.55, "alt": 25.0, "cap": 4, "spread": False},
    "eye": {"mag_lo": 1.45, "mag_hi": 3.45, "alt": 16.0, "cap": 8, "spread": True},
    "bino": {"mag_lo": 3.40, "mag_hi": 5.25, "alt": 10.0, "cap": 8, "spread": True},
    "full": {"mag_lo": -2.0, "mag_hi": 5.25, "alt": 0.0, "cap": 12, "spread": False},
}


def _az_sep(a: float, b: float) -> float:
    return abs(((float(a) - float(b) + 180.0) % 360.0) - 180.0)


def _pick_stars(pool: list[dict[str, Any]], cap: int, *, spread: bool) -> list[dict[str, Any]]:
    if not spread:
        return pool[:cap]
    chosen: list[dict[str, Any]] = []
    leftover: list[dict[str, Any]] = []
    for star in pool:
        if len(chosen) >= cap:
            leftover.append(star)
            continue
        if not chosen or all(_az_sep(star["az"], item["az"]) >= 22 for item in chosen):
            chosen.append(star)
        else:
            leftover.append(star)
    for star in leftover:
        if len(chosen) >= cap:
            break
        chosen.append(star)
    return chosen


def tonight_picks(
    snap: dict[str, Any],
    *,
    weather: dict[str, Any] | None = None,
    eye: str | None = None,
    frame: SkyFrame | None = None,
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

    cfg = eye_level(eye)
    key = str(eye or "full")
    rules = _STAR_RULES.get(key) or _STAR_RULES["full"]
    is_full = key == "full"
    min_alt = float(rules["alt"])
    planet_floor = {"easy": 18.0, "eye": 12.0, "bino": 5.0, "full": -0.5}.get(key, 0.0)
    planet_mag = 99.0 if is_full else float(cfg["planet"])
    picks: list[dict[str, Any]] = []
    moon = snap["moon"]
    moon_floor = 12.0 if key == "easy" else planet_floor
    if moon["alt"] > moon_floor:
        illum = moon.get("illum")
        detail = str(moon.get("phase") or "Luna")
        if isinstance(illum, (int, float)):
            detail = f"{detail} · illum. {illum:.0f}%"
        picks.append(
            {
                "kind": "moon",
                "title": "Luna",
                "emoji": moon.get("phase_emoji") or "🌙",
                "alt": moon["alt"],
                "az": moon["az"],
                "mag": None,
                "con": "",
                "stars": score(moon["alt"], None),
                "detail": detail,
            }
        )
    for row in snap["planets"]:
        if row["alt"] <= planet_floor:
            continue
        mag = row.get("mag") if isinstance(row.get("mag"), (int, float)) else None
        if mag is not None and mag > planet_mag:
            continue
        bar = score(row["alt"], mag)
        if row["name"] in {"Urano", "Nettuno"} and key in {"easy", "eye"}:
            continue
        if key == "easy" and (mag is None or mag > 1.4 or row["alt"] < 18):
            continue
        picks.append(
            {
                "kind": "planet",
                "title": row["name"],
                "emoji": row["emoji"],
                "alt": row["alt"],
                "az": row["az"],
                "mag": mag,
                "con": "",
                "stars": bar,
                "detail": f"mag {mag:.1f}" if mag is not None else "",
            }
        )
    if frame is not None:
        pool = [star for star in visible_stars(frame) if str(star.get("name") or "").strip()]
    else:
        pool = [star for star in snap.get("stars") or [] if str(star.get("name") or "").strip()]
    band: list[dict[str, Any]] = []
    for star in pool:
        mag = float(star["mag"])
        alt = float(star["alt"])
        if alt <= min_alt or mag < float(rules["mag_lo"]) or mag > float(rules["mag_hi"]):
            continue
        band.append(star)
    for star in _pick_stars(band, int(rules["cap"]), spread=bool(rules["spread"])):
        mag = float(star["mag"])
        alt = float(star["alt"])
        con = str(star.get("con") or "")
        con_it = constellation_name(con) if con else ""
        detail = f"mag {mag:.1f}"
        if con_it:
            detail = f"{con_it} · {detail}"
        picks.append(
            {
                "kind": "star",
                "title": str(star["name"]),
                "emoji": "⭐",
                "alt": alt,
                "az": float(star["az"]),
                "mag": mag,
                "con": con,
                "bv": star.get("bv"),
                "stars": score(alt, mag),
                "detail": detail,
            }
        )
    picks.sort(
        key=lambda row: (
            0 if row["kind"] in {"moon", "planet"} else 1,
            float(row["mag"]) if isinstance(row.get("mag"), (int, float)) else 9.0,
            -float(row["alt"]),
        )
    )
    return picks, emoji, sky, cloud_f


WEEKDAY_IT = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")


def human_when(when: datetime, now: datetime) -> str:
    local = when
    clock = local.strftime("%H:%M")
    wd = WEEKDAY_IT[local.weekday()]
    date = local.strftime("%d/%m")
    if local.date() == now.date():
        return f"oggi alle {clock}"
    if local.date() == (now.date() + timedelta(days=1)):
        return f"domani {wd} alle {clock}"
    days = max(0, (local.date() - now.date()).days)
    if days < 7:
        return f"{wd} {date} alle {clock} (tra {days} giorni)"
    return f"{wd} {date} alle {clock}"


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


CALC_BODIES = (
    (astronomy.Body.Moon, "Luna", "🌙"),
    *PLANET_SCAN,
)


def _ae_utc(stamp: Any) -> datetime | None:
    if stamp is None:
        return None
    raw = stamp.Utc() if hasattr(stamp, "Utc") else stamp
    if raw.tzinfo is None:
        raw = raw.replace(tzinfo=timezone.utc)
    return raw


def sky_calculations(lat: float, lon: float, when: datetime) -> dict[str, Any]:
    """Relazioni e orari da Astronomy Engine. Non è un elenco di posizioni."""
    frame = SkyFrame(lat, lon, when)
    rows: list[dict[str, Any]] = []
    for body, name, emoji in CALC_BODIES:
        alt, az, _ra, _dec = frame.body_altaz(body)
        ill = astronomy.Illumination(body, frame.moment)
        elong = astronomy.Elongation(body, frame.moment)
        rise = astronomy.SearchRiseSet(body, frame.site, astronomy.Direction.Rise, frame.moment, 1.2)
        sett = astronomy.SearchRiseSet(body, frame.site, astronomy.Direction.Set, frame.moment, 1.2)
        cul = astronomy.SearchHourAngle(body, frame.site, 0.0, frame.moment)
        transit = None
        if cul is not None and getattr(cul, "time", None) is not None:
            transit = _ae_utc(cul.time)
        rows.append(
            {
                "name": name,
                "emoji": emoji,
                "alt": float(alt),
                "az": float(az),
                "mag": float(ill.mag) if ill.mag is not None else None,
                "elong": float(elong.elongation),
                "rise": _ae_utc(rise),
                "set": _ae_utc(sett),
                "transit": transit,
            }
        )
    up = [row for row in rows if row["alt"] > 0]
    highest = max(up, key=lambda row: row["alt"]) if up else None
    bright = [row for row in up if isinstance(row.get("mag"), (int, float))]
    brightest = min(bright, key=lambda row: float(row["mag"])) if bright else None
    pairs: list[dict[str, Any]] = []
    for i, left in enumerate(up):
        for right in up[i + 1 :]:
            if {left["name"], right["name"]} == {"Urano", "Nettuno"}:
                continue
            sep = angular_sep(left["alt"], left["az"], right["alt"], right["az"])
            pairs.append({"a": left, "b": right, "sep": sep})
    pairs.sort(key=lambda item: item["sep"])
    rising = [row for row in rows if row["alt"] <= 0 and row.get("rise") is not None]
    rising.sort(key=lambda row: row["rise"])
    setting = [row for row in up if row.get("set") is not None]
    setting.sort(key=lambda row: row["set"])
    return {
        "rows": rows,
        "up": up,
        "highest": highest,
        "brightest": brightest,
        "pairs": pairs,
        "rising": rising,
        "setting": setting,
        "sun_alt": float(frame.body_altaz(astronomy.Body.Sun)[0]),
    }


def format_sky_calculations(
    *,
    place: str,
    when: datetime,
    tz: ZoneInfo,
    data: dict[str, Any],
) -> str:
    import html as _html

    from services.horizons import cardinal_long, height_it, mag_it

    def e(text: str) -> str:
        return _html.escape(text)

    local = when.astimezone(tz)
    lines = [
        f"📐 <b>CALCOLI — {e(place.upper())}</b>",
        f"📅 {e(local.strftime('%d/%m/%Y'))} · {local.strftime('%H:%M')}",
        "",
        "Non è l'elenco dei pianeti. Qui confronto i corpi tra loro: "
        "chi è più alto, chi è più luminoso, chi è vicino a chi, chi sorge dopo.",
        "",
    ]
    highest = data.get("highest")
    brightest = data.get("brightest")
    up = data.get("up") if isinstance(data.get("up"), list) else []
    if not up:
        lines.append("In questo momento Luna e pianeti sono tutti sotto l'orizzonte.")
        lines.append("")
    else:
        lines.append("🏆 <b>ADESSO, DA QUI</b>")
        if highest:
            look = f", verso {cardinal_long(highest['az'])}" if highest.get("az") is not None else ""
            lines.append(
                f"Più alto: {highest['emoji']} <b>{e(highest['name'])}</b> — "
                f"{height_it(highest['alt'])}{look}."
            )
        if brightest and brightest is not highest:
            seen = mag_it(brightest.get("mag"), up=True)
            lines.append(
                f"Più luminoso sopra: {brightest['emoji']} <b>{e(brightest['name'])}</b>"
                + (f" — {seen}." if seen else ".")
            )
        elif brightest:
            seen = mag_it(brightest.get("mag"), up=True)
            if seen:
                lines.append(f"È anche il più luminoso sopra — {seen}.")
        lines.append(f"Sopra l'orizzonte: {', '.join(row['name'] for row in up)}.")
        lines.append("")
    pairs = [item for item in (data.get("pairs") or []) if item["sep"] <= 20]
    lines.append("✨ <b>QUANTO DISTANO</b>")
    if pairs:
        lines.append("Separazione sulla volta, entrambi sopra. Sotto 20° li metto qui.")
        for item in pairs[:6]:
            a, b, sep = item["a"], item["b"], item["sep"]
            how = "quasi insieme" if sep < 3 else "vicini" if sep < 8 else "nello stesso pezzo di cielo"
            lines.append(
                f"{a['emoji']}{b['emoji']} <b>{e(a['name'])} – {e(b['name'])}</b>  "
                f"{sep:.1f}° · {how}"
            )
    else:
        lines.append("Nessuna coppia sopra è più vicina di 20°.")
    lines.append("")
    rising = data.get("rising") or []
    lines.append("⬆️ <b>PROSSIMO A SORGERE</b>")
    if rising:
        for row in rising[:5]:
            stamp = row["rise"].astimezone(tz)
            lines.append(f"{row['emoji']} <b>{e(row['name'])}</b>  {human_when(stamp, local)}")
    else:
        lines.append("Nessun corpo sotto ha un'alba nelle prossime ~28 ore.")
    lines.append("")
    setting = data.get("setting") or []
    lines.append("⬇️ <b>TRAMONTANO (SE SONO SOPRA)</b>")
    if setting:
        for row in setting[:5]:
            stamp = row["set"].astimezone(tz)
            lines.append(f"{row['emoji']} <b>{e(row['name'])}</b>  {human_when(stamp, local)}")
    else:
        lines.append("Nessun tramonto calcolato per chi è sopra.")
    lines.extend(
        [
            "",
            "<i>Astronomy Engine: altezza, magnitudine, elongazione, alba/tramonto/transito. "
            "La separazione è l'angolo sulla volta da questo luogo. Non è Horizons HTTP.</i>",
        ]
    )
    return "\n".join(lines)
