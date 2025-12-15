import asyncio
import logging
from typing import List

import discord
from discord.ext import commands
import sentry_sdk

from config import Settings, load_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class GeoLiveBot(commands.Bot):
    def __init__(self, settings: Settings, extensions: List[str]) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.settings = settings
        self.extensions_to_load = extensions

    async def setup_hook(self) -> None:
        for ext in self.extensions_to_load:
            try:
                await self.load_extension(ext)
                logging.info("Loaded extension %s", ext)
            except Exception as exc:
                logging.exception("Failed to load extension %s: %s", ext, exc)
        await self.tree.sync()


def build_bot() -> GeoLiveBot:
    settings = load_settings()
    extensions = [
        "cogs.commands.weather",
        "cogs.commands.space",
        "cogs.commands.disaster",
        "cogs.auto_feed",
    ]
    return GeoLiveBot(settings, extensions)


async def main() -> None:
    bot = build_bot()
    if bot.settings.sentry_dsn:
        sentry_sdk.init(
            dsn=bot.settings.sentry_dsn,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
        )
    async with bot:
        token = bot.settings.discord_token
        if not token:
            raise RuntimeError(
                "DISCORD_TOKEN missing. Set it in .env or environment variables."
            )
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
