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


async def fetch_forecast(client: httpx.AsyncClient, lat: float, lon: float) -> dict[str, Any]:
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
            "forecast_days": 7,
            "timezone": "auto",
        },
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or not isinstance(data.get("current"), dict):
        raise ValueError("meteo vuoto")
    return data


def format_forecast(data: dict[str, Any], *, name: str) -> str:
    current = data.get("current") if isinstance(data.get("current"), dict) else {}
    daily = data.get("daily") if isinstance(data.get("daily"), dict) else {}
    emoji, sky = wmo_label(current.get("weather_code"))
    tz = str(data.get("timezone") or "—")
    lines = [
        f"🌤️ <b>METEO — {name.upper()}</b>",
        f"<i>Open-Meteo · fuso {tz}</i>",
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
        "📅 <b>PROSSIMI 7 GIORNI</b>",
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
    for idx, day in enumerate(dates[:7]):
        em, label = wmo_label(codes[idx] if idx < len(codes) else None)
        hi = _num(tmax[idx] if idx < len(tmax) else None)
        lo = _num(tmin[idx] if idx < len(tmin) else None)
        mm = _num(rain[idx] if idx < len(rain) else None, 1)
        chance = _num(pop[idx] if idx < len(pop) else None)
        lines.append(
            f"{em} <b>{_day_label(str(day))}</b> — {label}\n"
            f"   {lo} / {hi} °C · pioggia {mm} mm · {chance} %"
        )
    lines.extend(
        [
            "",
            "<i>Modello Open-Meteo (WMO). Non è un oracolo e non è una previsione astrologica.</i>",
        ]
    )
    return "\n".join(lines)
