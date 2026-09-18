"""Aiuti astronomici: visibilità da numeri live, non da giudizi inventati."""

from __future__ import annotations


def visibility_stars(*, altitude: float | None, magnitude: float | None = None) -> str:
    """Stelle 1–5 derivate da altezza e magnitudine apparenti già calcolate."""
    if altitude is None or altitude <= 0:
        return "—"
    score = 1
    if altitude >= 10:
        score += 1
    if altitude >= 25:
        score += 1
    if magnitude is not None:
        if magnitude <= 2.0:
            score += 1
        if magnitude <= 0.5:
            score += 1
    else:
        if altitude >= 40:
            score += 1
        if altitude >= 55:
            score += 1
    score = max(1, min(5, score))
    return "⭐" * score + "☆" * (5 - score)


def stellarium_url(lat: float, lon: float) -> str:
    return f"https://stellarium-web.org/#latitude={lat:.4f}&longitude={lon:.4f}"
