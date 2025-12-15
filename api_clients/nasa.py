from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

import httpx

DONKI_NOTIFICATIONS = "https://api.nasa.gov/DONKI/notifications"


async def fetch_space_weather(api_key: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch recent space weather notifications (solar flares, aurora watches, etc.).
    """
    params = {"type": "all", "api_key": api_key}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(DONKI_NOTIFICATIONS, params=params)
        resp.raise_for_status()
        data = resp.json()
    sorted_items = sorted(
        data, key=lambda item: item.get("messageIssueTime", ""), reverse=True
    )
    return sorted_items[:limit]


def format_notification(item: Dict[str, Any]) -> str:
    issued = item.get("messageIssueTime")
    try:
        issued_dt = dt.datetime.fromisoformat(issued.replace("Z", "+00:00"))
        issued_text = issued_dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        issued_text = issued or "N/A"
    return f"{item.get('messageType', 'Info')}: {item.get('messageBody', 'N/A')[:300]}...\nIssued: {issued_text}"
