"""Immagini pubbliche dei satelliti Terra/meteo. NASA GIBS e NOAA, niente chiave."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

GIBS_SNAPSHOT = "https://wvs.earthdata.nasa.gov/api/v1/snapshot"
GOES16_DISK = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/678x678.jpg"

GIBS_LAYER: dict[str, str] = {
    "terra": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "aqua": "MODIS_Aqua_CorrectedReflectance_TrueColor",
    "n20": "VIIRS_NOAA20_CorrectedReflectance_TrueColor",
    "n21": "VIIRS_NOAA21_CorrectedReflectance_TrueColor",
    "ld8": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "ld9": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "s2a": "MODIS_Terra_CorrectedReflectance_TrueColor",
}

LAYER_NOTE: dict[str, str] = {
    "terra": "NASA GIBS · MODIS Terra, vero colore del giorno (o di ieri).",
    "aqua": "NASA GIBS · MODIS Aqua, vero colore del giorno (o di ieri).",
    "n20": "NASA GIBS · VIIRS NOAA-20, vero colore del giorno (o di ieri).",
    "n21": "NASA GIBS · VIIRS NOAA-21, vero colore del giorno (o di ieri).",
    "g16": "NOAA · GOES-16 GeoColor, disco delle Americhe, aggiornato di continuo.",
    "ld8": "Landsat 8 fa foto ad alta risoluzione; anteprima pubblica: MODIS Terra sullo stesso punto.",
    "ld9": "Landsat 9 fa foto ad alta risoluzione; anteprima pubblica: MODIS Terra sullo stesso punto.",
    "s2a": "Sentinel-2A fa foto ad alta risoluzione; anteprima pubblica: MODIS Terra sullo stesso punto.",
}


def _bbox(lat: float, lon: float, span: float = 7.5) -> str:
    south = max(-85.0, lat - span * 0.6)
    north = min(85.0, lat + span * 0.6)
    west = max(-180.0, lon - span)
    east = min(180.0, lon + span)
    return f"{south:.3f},{west:.3f},{north:.3f},{east:.3f}"


async def fetch_gibs_true_color(
    client: httpx.AsyncClient,
    layer: str,
    lat: float,
    lon: float,
    *,
    span: float = 7.5,
) -> bytes | None:
    today = datetime.now(timezone.utc).date()
    for day in (today, today - timedelta(days=1)):
        try:
            response = await client.get(
                GIBS_SNAPSHOT,
                params={
                    "REQUEST": "GetSnapshot",
                    "LAYERS": f"{layer},Coastlines",
                    "CRS": "EPSG:4326",
                    "TIME": day.isoformat(),
                    "BBOX": _bbox(lat, lon, span),
                    "FORMAT": "image/jpeg",
                    "WIDTH": "720",
                    "HEIGHT": "540",
                },
            )
            response.raise_for_status()
            data = response.content
            if data[:3] == b"\xff\xd8\xff" and len(data) > 4000:
                return data
        except Exception:
            continue
    return None


async def fetch_goes16_disk(client: httpx.AsyncClient) -> bytes | None:
    try:
        response = await client.get(GOES16_DISK)
        response.raise_for_status()
        data = response.content
        if data[:3] == b"\xff\xd8\xff" and len(data) > 4000:
            return data
    except Exception:
        return None
    return None


async def fetch_sat_view(
    client: httpx.AsyncClient,
    key: str,
    lat: float,
    lon: float,
) -> dict[str, Any]:
    note = LAYER_NOTE.get(key, "Immagine pubblica del giorno.")
    if key == "g16":
        data = await fetch_goes16_disk(client)
        return {"bytes": data, "note": note, "filename": "goes16.jpg"}
    layer = GIBS_LAYER.get(key)
    if not layer:
        return {"bytes": None, "note": "", "filename": "sat.jpg"}
    data = await fetch_gibs_true_color(client, layer, lat, lon)
    return {"bytes": data, "note": note, "filename": f"{key}.jpg"}
