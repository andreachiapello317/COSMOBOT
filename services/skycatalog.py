"""Catalogo Hipparcos (stelle mag ≤ 5.2) e figure IAU. Non è Horizons."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import astronomy

CATALOG_PATH = Path(__file__).resolve().parent / "data" / "skycatalog.json"


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data.get("stars"):
        raise ValueError("catalogo stelle assente")
    return data


def constellation_name(code: str) -> str:
    cons = load_catalog().get("cons") if isinstance(load_catalog().get("cons"), dict) else {}
    key = str(code or "").strip()
    return str(cons.get(key) or key)


def ra_hours(ra_deg: float) -> float:
    deg = float(ra_deg) % 360.0
    if deg < 0:
        deg += 360.0
    return deg / 15.0


def astro_time(when: datetime) -> astronomy.Time:
    utc = when.astimezone(timezone.utc)
    return astronomy.Time.Make(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        utc.second + utc.microsecond / 1_000_000,
    )


class SkyFrame:
    """Un istante + un luogo: da RA/DEC a altezza/azimut."""

    def __init__(self, lat: float, lon: float, when: datetime):
        self.lat = float(lat)
        self.lon = float(lon)
        self.when = when.astimezone(timezone.utc)
        self.moment = astro_time(self.when)
        self.site = astronomy.Observer(self.lat, self.lon, 0.05)
        gast = float(astronomy.SiderealTime(self.moment))
        self.lst = gast + self.lon / 15.0
        self._lat_r = math.radians(self.lat)

    def altaz(self, ra_deg: float, dec_deg: float) -> tuple[float, float]:
        ha = math.radians((self.lst - ra_hours(ra_deg)) * 15.0)
        dec = math.radians(float(dec_deg))
        sin_alt = math.sin(dec) * math.sin(self._lat_r) + math.cos(dec) * math.cos(self._lat_r) * math.cos(ha)
        sin_alt = max(-1.0, min(1.0, sin_alt))
        alt = math.asin(sin_alt)
        az = math.atan2(
            -math.sin(ha),
            math.tan(dec) * math.cos(self._lat_r) - math.cos(ha) * math.sin(self._lat_r),
        )
        return math.degrees(alt), math.degrees(az) % 360.0

    def body_altaz(self, body: astronomy.Body) -> tuple[float, float, float, float]:
        eq = astronomy.Equator(body, self.moment, self.site, True, True)
        hor = astronomy.Horizon(self.moment, self.site, eq.ra, eq.dec, astronomy.Refraction.Normal)
        return float(hor.altitude), float(hor.azimuth), float(eq.ra), float(eq.dec)


def visible_stars(frame: SkyFrame, *, limit: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in load_catalog()["stars"]:
        ra, dec, mag = float(item[0]), float(item[1]), float(item[2])
        extra = item[3] if len(item) > 3 and isinstance(item[3], dict) else {}
        alt, az = frame.altaz(ra, dec)
        if alt <= 0:
            continue
        rows.append(
            {
                "ra": ra,
                "dec": dec,
                "mag": mag,
                "alt": alt,
                "az": az,
                "name": str(extra.get("n") or ""),
                "con": str(extra.get("c") or ""),
                "bv": extra.get("bv"),
            }
        )
    rows.sort(key=lambda row: row["mag"])
    if limit is not None:
        return rows[:limit]
    return rows


def constellation_segments(frame: SkyFrame) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for fig in load_catalog().get("lines") or []:
        cid = str(fig.get("id") or "")
        segs: list[list[tuple[float, float]]] = []
        alts: list[float] = []
        for seg in fig.get("s") or []:
            pts: list[tuple[float, float]] = []
            for point in seg:
                if len(point) < 2:
                    continue
                alt, az = frame.altaz(float(point[0]), float(point[1]))
                pts.append((alt, az))
                if alt > 0:
                    alts.append(alt)
            if len(pts) >= 2:
                segs.append(pts)
        if not segs or not alts:
            continue
        out.append({"id": cid, "name": constellation_name(cid), "segs": segs, "alt": max(alts)})
    out.sort(key=lambda row: row["alt"], reverse=True)
    return out
