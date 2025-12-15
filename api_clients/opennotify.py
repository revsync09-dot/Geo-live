from __future__ import annotations

from typing import Any, Dict

import httpx

ISS_NOW_URL = "http://api.open-notify.org/iss-now.json"


async def fetch_iss_position() -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(ISS_NOW_URL)
        resp.raise_for_status()
        payload = resp.json()
    position = payload.get("iss_position", {})
    return {
        "latitude": position.get("latitude"),
        "longitude": position.get("longitude"),
        "timestamp": payload.get("timestamp"),
    }
