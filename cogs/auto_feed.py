from __future__ import annotations

import logging

import discord
from discord.ext import commands, tasks

from api_clients import usgs
from config import Settings
from embeds.geolive import geo_card
from embeds.style import thin
from graphing.earthquake_map import create_earthquake_map
from dashboard.utils.storage import default_config

log = logging.getLogger(__name__)


async def send_earthquake_embed(
    channel: discord.abc.Messageable,
    magnitude: float,
    place: str,
    lat: float,
    lon: float,
    depth: float,
    *,
    primary_color: int | None = None,
    icon_url: str | None = None,
) -> None:
    map_path = create_earthquake_map(lat, lon, magnitude, place)
    file = discord.File(map_path, filename="quake.png")

    embed = geo_card("GeoLive Earthquake Alert", color=primary_color, icon_url=icon_url)
    embed.add_field(name="📍 Location", value=place, inline=False)
    embed.add_field(name="🌡️ Magnitude", value=str(magnitude), inline=True)
    embed.add_field(name="📊 Depth", value=f"{depth} km", inline=True)
    embed.add_field(name="🌐 Latitude", value=str(lat), inline=True)
    embed.add_field(name="🌍 Longitude", value=str(lon), inline=True)
    embed.add_field(
        name="────────────────────────",
        value=thin("Earthquake Position Map") + "\n",
        inline=False,
    )
    embed.set_image(url="attachment://quake.png")
    embed.set_footer(text="Data source: USGS Earthquake Hazards Program")

    await channel.send(embed=embed, file=file)


class AutoFeed(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.auto_feed_task.start()

    def cog_unload(self) -> None:
        self.auto_feed_task.cancel()

    @tasks.loop(hours=4)
    async def auto_feed_task(self) -> None:
        settings: Settings = self.bot.settings  # type: ignore[attr-defined]
        try:
            quakes = await usgs.fetch_recent_earthquakes()
        except Exception as exc:
            log.error("Auto feed USGS fetch failed: %s", exc)
            return

        if not quakes:
            return

        top = quakes[0]
        lat = top.get("lat")
        lon = top.get("lon")
        mag = top.get("magnitude")
        depth = top.get("depth")
        place = top.get("place")

        if None in (lat, lon, mag):
            return

        def parse_color(val) -> int:
            if isinstance(val, int):
                return val
            if isinstance(val, str):
                cleaned = val.strip()
                if cleaned.startswith("#"):
                    cleaned = cleaned[1:]
                try:
                    return int(cleaned, 16)
                except Exception:
                    return 0x00AEEF
            return 0x00AEEF

        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if not channel.permissions_for(guild.me).send_messages:  # type: ignore[arg-type]
                    continue
                config = default_config()
                try:
                    from dashboard.utils.storage import get_guild_config
                    config = get_guild_config(str(guild.id))
                except Exception as exc:
                    log.debug("Could not load guild config %s: %s", guild.id, exc)
                if not config.get("earthquake_feed_enabled", True):
                    continue
                try:
                    await send_earthquake_embed(
                        channel,
                        mag,
                        place,
                        lat,
                        lon,
                        depth,
                        primary_color=parse_color(config.get("primary_color")),
                        icon_url=config.get("icon_url"),
                    )
                    break  # send to first channel per guild
                except discord.Forbidden:
                    continue
                except Exception as exc:
                    log.error("Auto feed send failed in %s: %s", channel, exc)
                    continue

    @auto_feed_task.before_loop
    async def before_auto_feed(self) -> None:
        settings: Settings = self.bot.settings  # type: ignore[attr-defined]
        self.auto_feed_task.change_interval(hours=settings.auto_feed_hours)
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoFeed(bot))
