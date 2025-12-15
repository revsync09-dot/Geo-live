import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    discord_token: str
    weather_api_key: str
    nasa_key: str
    embed_icon_url: str = "YOUR_ICON_URL"
    colour: int = 0x00AEEF
    auto_feed_hours: int = 4
    sentry_dsn: str | None = None


def load_settings() -> Settings:
    """
    Load settings from environment variables or fall back to placeholders.
    """
    return Settings(
        discord_token=os.getenv("DISCORD_TOKEN", ""),
        weather_api_key=os.getenv("WEATHER_API_KEY", "YOUR_WEATHER_API_KEY"),
        nasa_key=os.getenv("NASA_KEY", "YOUR_NASA_KEY"),
        embed_icon_url=os.getenv("ICON_URL", "YOUR_ICON_URL"),
        sentry_dsn=os.getenv("SENTRY_DSN"),
    )


# Convenience constant for embed styling
ICON_URL = load_settings().embed_icon_url
