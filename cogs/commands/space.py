from __future__ import annotations

import datetime as dt

import discord
from discord import app_commands
from discord.ext import commands

from api_clients import nasa, opennotify
from embeds.geolive import geo_card
from embeds.style import thin


class Space(commands.GroupCog, name="space"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="aurora", description="Show current space weather alerts.")
    async def aurora(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        try:
            notifications = await nasa.fetch_space_weather(self.bot.settings.nasa_key)  # type: ignore[attr-defined]
        except Exception as exc:
            await interaction.followup.send(f"Could not load NASA data: {exc}", ephemeral=True)
            return

        description = "\n\n".join(nasa.format_notification(item) for item in notifications) or "No current alerts."
        embed = geo_card("GeoLive Space Weather")
        embed.add_field(name="────────────────────────", value=thin("Solar & Aurora activity"), inline=False)
        embed.add_field(name="Alerts", value=description[:1000], inline=False)
        embed.set_footer(text="Data source: NASA DONKI")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="iss", description="Show the current ISS position.")
    async def iss(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        try:
            pos = await opennotify.fetch_iss_position()
        except Exception as exc:
            await interaction.followup.send(f"Could not load ISS data: {exc}", ephemeral=True)
            return

        ts = pos.get("timestamp")
        ts_text = dt.datetime.utcfromtimestamp(ts).strftime("%H:%M:%S UTC") if ts else "N/A"
        embed = geo_card("GeoLive ISS Position")
        embed.add_field(name="🌐 Latitude", value=str(pos.get("latitude")), inline=True)
        embed.add_field(name="🌍 Longitude", value=str(pos.get("longitude")), inline=True)
        embed.add_field(name="⏱ Time", value=ts_text, inline=True)
        embed.add_field(name="────────────────────────", value=thin("Real-time ISS tracking"), inline=False)
        embed.set_footer(text="Data source: Open Notify")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Space(bot))
