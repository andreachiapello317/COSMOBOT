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
        row = {"quiz": {}, "points": 0, "missions": {}, "worlds": []}
        data[key] = row
    quiz = row.get("quiz")
    if not isinstance(quiz, dict):
        row["quiz"] = {}
    missions = row.get("missions")
    if not isinstance(missions, dict):
        row["missions"] = {}
    worlds = row.get("worlds")
    if not isinstance(worlds, list):
        row["worlds"] = []
    stones = row.get("stones")
    if not isinstance(stones, list):
        row["stones"] = []
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


async def world_save(user_id: int, item: dict[str, Any]) -> list[dict[str, Any]]:
    name = str(item.get("name") or "").strip()
    if not name:
        return await world_list(user_id)
    async with _lock:
        data = _load()
        row = _user(data, user_id)
        worlds = [w for w in row["worlds"] if isinstance(w, dict)]
        worlds = [w for w in worlds if str(w.get("name") or "") != name]
        payload = {
            "name": name,
            "host": str(item.get("host") or ""),
            "kind": str(item.get("kind") or "exo"),
        }
        if payload["kind"] == "imag":
            src = item.get("row") if isinstance(item.get("row"), dict) else item
            for key in ("pl_rade", "pl_eqt", "pl_orbper", "moons", "stars", "climate", "note"):
                if src.get(key) is not None:
                    payload[key] = src.get(key)
        worlds.insert(0, payload)
        row["worlds"] = worlds[:20]
        _save(data)
        return list(row["worlds"])


async def world_list(user_id: int) -> list[dict[str, Any]]:
    async with _lock:
        row = _user(_load(), user_id)
        return [w for w in (row.get("worlds") or []) if isinstance(w, dict)]


async def stone_discover(user_id: int, stone_id: str) -> list[str]:
    sid = str(stone_id or "").strip()
    if not sid:
        return await stone_ids(user_id)
    async with _lock:
        data = _load()
        row = _user(data, user_id)
        known = [str(x) for x in row["stones"] if x]
        if sid not in known:
            known.append(sid)
            row["stones"] = known
            _save(data)
        return list(known)


async def stone_ids(user_id: int) -> list[str]:
    async with _lock:
        row = _user(_load(), user_id)
        return [str(x) for x in (row.get("stones") or []) if x]
