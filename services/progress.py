"""Punteggi quiz e missioni del giorno: file locale, niente classifica globale."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from typing import Any

PROGRESS_PATH = Path("data/progress.json")
_lock = asyncio.Lock()


def _load() -> dict[str, Any]:
    if not PROGRESS_PATH.exists():
        return {}
    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(data: dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _user(data: dict[str, Any], user_id: int) -> dict[str, Any]:
    key = str(user_id)
    row = data.get(key)
    if not isinstance(row, dict):
        row = {"quiz": {}, "points": 0, "missions": {}}
        data[key] = row
    quiz = row.get("quiz")
    if not isinstance(quiz, dict):
        row["quiz"] = {}
    missions = row.get("missions")
    if not isinstance(missions, dict):
        row["missions"] = {}
    row.setdefault("points", 0)
    return row


async def quiz_record(user_id: int, level: str, *, ok: bool) -> dict[str, Any]:
    async with _lock:
        data = _load()
        row = _user(data, user_id)
        bucket = row["quiz"].get(level)
        if not isinstance(bucket, dict):
            bucket = {"ok": 0, "tot": 0}
        bucket["tot"] = int(bucket.get("tot") or 0) + 1
        if ok:
            bucket["ok"] = int(bucket.get("ok") or 0) + 1
            row["points"] = int(row.get("points") or 0) + {"easy": 1, "medium": 2, "hard": 3, "expert": 5}.get(level, 1)
        row["quiz"][level] = bucket
        _save(data)
        return {"quiz": row["quiz"], "points": row["points"]}


async def quiz_board(user_id: int) -> dict[str, Any]:
    async with _lock:
        row = _user(_load(), user_id)
        return {"quiz": row.get("quiz") or {}, "points": int(row.get("points") or 0)}


async def mission_done(user_id: int, day: str, mission_id: str) -> None:
    async with _lock:
        data = _load()
        row = _user(data, user_id)
        row["missions"][day] = mission_id
        _save(data)


async def mission_is_done(user_id: int, day: str | None = None) -> str | None:
    stamp = day or date.today().isoformat()
    async with _lock:
        row = _user(_load(), user_id)
        done = row.get("missions") or {}
        value = done.get(stamp)
        return str(value) if value else None
