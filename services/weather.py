"""Meteo mondiale via Open-Meteo. Numeri live, nessuna previsione inventata."""

from __future__ import annotations

from typing import Any

import httpx

WMO_IT: dict[int, tuple[str, str]] = {
    0: ("☀️", "Sereno"),
    1: ("🌤️", "Prevalentemente sereno"),
    2: ("⛅", "Parzialmente nuvoloso"),
    3: ("☁️", "Coperto"),
    45: ("🌫️", "Nebbia"),
    48: ("🌫️", "Nebbia con brina"),
    51: ("🌦️", "Pioviggine debole"),
    53: ("🌦️", "Pioviggine"),
    55: ("🌧️", "Pioviggine intensa"),
    56: ("🌧️", "Pioviggine gelata debole"),
    57: ("🌧️", "Pioviggine gelata"),
    61: ("🌧️", "Pioggia debole"),
    63: ("🌧️", "Pioggia"),
    65: ("🌧️", "Pioggia intensa"),
    66: ("🌧️", "Pioggia gelata debole"),
    67: ("🌧️", "Pioggia gelata"),
    71: ("🌨️", "Neve debole"),
    73: ("🌨️", "Neve"),
    75: ("❄️", "Neve intensa"),
    77: ("🌨️", "Grani di neve"),
    80: ("🌦️", "Rovesci deboli"),
    81: ("🌧️", "Rovesci"),
    82: ("⛈️", "Rovesci violenti"),
    85: ("🌨️", "Rovesci di neve deboli"),
    86: ("❄️", "Rovesci di neve"),
    95: ("⛈️", "Temporale"),
    96: ("⛈️", "Temporale con grandine"),
    99: ("⛈️", "Temporale con grandine forte"),
}

WEEKDAY_IT = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")


def wmo_label(code: int | None) -> tuple[str, str]:
    try:
        key = int(code) if code is not None else -1
    except (TypeError, ValueError):
        return ("🌡️", "Tempo non classificato")
    return WMO_IT.get(key, ("🌡️", f"Codice WMO {key}"))


def _num(value: Any, digits: int = 0) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    if digits <= 0:
        return str(int(round(number)))
    return f"{number:.{digits}f}"


def _day_label(iso: str) -> str:
    raw = str(iso or "")[:10]
    try:
        year, month, day = (int(part) for part in raw.split("-"))
        from datetime import date

        when = date(year, month, day)
        return f"{WEEKDAY_IT[when.weekday()]} {day:02d}/{month:02d}"
    except (TypeError, ValueError):
        return raw or "—"


def parse_forecast_request(text: str, *, today: Any = None) -> dict[str, Any]:
    """Quanti o quali giorni. Vuoto = oggi e domani. Non inventa il tempo, solo la finestra."""
    from datetime import date, timedelta

    if today is None:
        today = date.today()
    raw = " ".join(str(text or "").strip().lower().split())
    compact = (
        raw.replace("à", "a")
        .replace("è", "e")
        .replace("é", "e")
        .replace("ì", "i")
        .replace("ò", "o")
        .replace("ù", "u")
    )
    if not compact or compact in {"oggi e domani", "oggi+domani", "default"}:
        return {"days": 2, "indices": [0, 1], "label": "oggi e domani"}
    if compact in {"oggi", "adesso", "ora"}:
        return {"days": 1, "indices": [0], "label": "oggi"}
    if compact in {"domani"}:
        return {"days": 2, "indices": [1], "label": "domani"}
    if compact in {"settimana", "una settimana", "7 giorni", "sette giorni"}:
        return {"days": 7, "indices": list(range(7)), "label": "7 giorni"}
    if compact in {"due settimane", "14 giorni", "quattordici giorni"}:
        return {"days": 14, "indices": list(range(14)), "label": "14 giorni"}

    import re

    number = re.search(r"\b(\d{1,2})\b", compact)
    if number and ("giorn" in compact or compact == number.group(1)):
        count = max(1, min(16, int(number.group(1))))
        return {"days": count, "indices": list(range(count)), "label": f"{count} giorni"}

    names = {
        "lunedi": 0,
        "lun": 0,
        "martedi": 1,
        "mar": 1,
        "mercoledi": 2,
        "mer": 2,
        "giovedi": 3,
        "gio": 3,
        "venerdi": 4,
        "ven": 4,
        "sabato": 5,
        "sab": 5,
        "domenica": 6,
        "dom": 6,
    }
    found: list[int] = []
    for token in re.findall(r"[a-z]+", compact):
        if token in names and names[token] not in found:
            found.append(names[token])
    if "da" in compact and "a" in compact and len(found) >= 2:
        start, end = found[0], found[1]
        found = []
        day = start
        for _ in range(7):
            found.append(day)
            if day == end:
                break
            day = (day + 1) % 7
    if found:
        indices: list[int] = []
        for offset in range(14):
            if (today + timedelta(days=offset)).weekday() in found:
                indices.append(offset)
        if not indices:
            indices = [0, 1]
        days = max(indices) + 1
        label = " e ".join(WEEKDAY_IT[d] for d in found)
        return {"days": days, "indices": indices, "label": label}

    return {"days": 2, "indices": [0, 1], "label": "oggi e domani"}


async def fetch_forecast(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    *,
    forecast_days: int = 2,
) -> dict[str, Any]:
    days = max(1, min(16, int(forecast_days)))
    response = await client.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "weather_code,wind_speed_10m,wind_direction_10m,precipitation"
            ),
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
            ),
            "forecast_days": days,
            "timezone": "auto",
        },
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or not isinstance(data.get("current"), dict):
        raise ValueError("meteo vuoto")
    return data


def format_forecast(
    data: dict[str, Any],
    *,
    name: str,
    days: int = 2,
    indices: list[int] | None = None,
    label: str = "oggi e domani",
) -> str:
    current = data.get("current") if isinstance(data.get("current"), dict) else {}
    daily = data.get("daily") if isinstance(data.get("daily"), dict) else {}
    emoji, sky = wmo_label(current.get("weather_code"))
    tz = str(data.get("timezone") or "—")
    lines = [
        f"🌤️ <b>METEO — {name.upper()}</b>",
        f"<i>Open-Meteo · fuso {tz} · {label}</i>",
        "",
        "🌡️ <b>ADESSO</b>",
        f"{emoji} {sky}",
        f"Temperatura {_num(current.get('temperature_2m'))} °C "
        f"(percepita {_num(current.get('apparent_temperature'))} °C)",
        f"Umidità {_num(current.get('relative_humidity_2m'))} % · "
        f"vento {_num(current.get('wind_speed_10m'))} km/h "
        f"({_num(current.get('wind_direction_10m'))}°)",
        f"Precipitazioni {_num(current.get('precipitation'), 1)} mm",
        "",
        f"📅 <b>{label.upper()}</b>",
    ]
    dates = daily.get("time") if isinstance(daily.get("time"), list) else []
    codes = daily.get("weather_code") if isinstance(daily.get("weather_code"), list) else []
    tmax = daily.get("temperature_2m_max") if isinstance(daily.get("temperature_2m_max"), list) else []
    tmin = daily.get("temperature_2m_min") if isinstance(daily.get("temperature_2m_min"), list) else []
    rain = daily.get("precipitation_sum") if isinstance(daily.get("precipitation_sum"), list) else []
    pop = (
        daily.get("precipitation_probability_max")
        if isinstance(daily.get("precipitation_probability_max"), list)
        else []
    )
    picks = indices if indices is not None else list(range(max(1, min(16, days))))
    shown = 0
    for idx in picks:
        if idx < 0 or idx >= len(dates):
            continue
        day = dates[idx]
        em, sky_day = wmo_label(codes[idx] if idx < len(codes) else None)
        hi = _num(tmax[idx] if idx < len(tmax) else None)
        lo = _num(tmin[idx] if idx < len(tmin) else None)
        mm = _num(rain[idx] if idx < len(rain) else None, 1)
        chance = _num(pop[idx] if idx < len(pop) else None)
        lines.append(
            f"{em} <b>{_day_label(str(day))}</b> — {sky_day}\n"
            f"   {lo} / {hi} °C · pioggia {mm} mm · {chance} %"
        )
        shown += 1
    if shown == 0:
        lines.append("<i>Nessun giorno in questa finestra.</i>")
    lines.extend(
        [
            "",
            "<i>Modello Open-Meteo (WMO). Non è un oracolo e non è una previsione astrologica.</i>",
        ]
    )
    return "\n".join(lines)
