"""Thin async client over the backend REST API — the shared source of truth.

Keeping all HTTP here means the command modules never care where data comes
from; they just get plain dicts identical to what the dashboard sees.
"""
import httpx

from . import config


async def _get(path: str) -> dict:
    async with httpx.AsyncClient(base_url=config.BACKEND_URL, timeout=5.0) as client:
        resp = await client.get(path)
        resp.raise_for_status()
        return resp.json()


async def get_snapshot() -> dict:
    """Full snapshot: devices, totals, alerts, times."""
    return await _get("/api/devices")


async def get_room(room_id: str) -> dict:
    return await _get(f"/api/rooms/{room_id}")


async def get_usage() -> dict:
    return await _get("/api/usage")


async def get_alerts() -> list[dict]:
    data = await _get("/api/alerts")
    return data.get("alerts", [])
