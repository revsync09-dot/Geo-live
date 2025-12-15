from __future__ import annotations

from typing import Any, Dict, List

import httpx

USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"


async def fetch_recent_earthquakes() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(USGS_FEED)
        resp.raise_for_status()
        payload = resp.json()
    features = payload.get("features", [])
    quakes: List[Dict[str, Any]] = []
    for item in features:
        props = item.get("properties", {})
        geometry = item.get("geometry", {})
        coords = geometry.get("coordinates", [None, None, None])
        quakes.append(
            {
                "place": props.get("place", "Unknown"),
                "magnitude": props.get("mag", "N/A"),
                "time": props.get("time"),
                "url": props.get("url"),
                "lon": coords[0],
                "lat": coords[1],
                "depth": coords[2],
            }
        )
    return quakes
