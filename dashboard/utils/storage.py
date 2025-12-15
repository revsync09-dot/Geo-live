from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path("data/config")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_guild_config(guild_id: str) -> Dict[str, Any]:
    path = DATA_DIR / f"{guild_id}.json"
    if not path.exists():
        return default_config()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default_config()


def save_guild_config(guild_id: str, data: Dict[str, Any]) -> None:
    path = DATA_DIR / f"{guild_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def default_config() -> Dict[str, Any]:
    return {
        "earthquake_feed_enabled": True,
        "weather_feed_enabled": True,
        "iss_feed_enabled": False,
        "interval": 4,
        "primary_color": "#00AEEF",
        "icon_url": "",
        "banner_url": "",
        "weather_api_key": "",
        "nasa_key": "",
    }
