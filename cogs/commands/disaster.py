from __future__ import annotations

import datetime as dt

import discord
from discord import app_commands
from discord.ext import commands

from api_clients import usgs
from embeds.geolive import geo_card
from embeds.style import thin
from graphing.heatmap import world_heatmap


class Disaster(commands.GroupCog, name="disaster"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="quake", description="Show the latest earthquakes.")
    async def quake(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        try:
            quakes = await usgs.fetch_recent_earthquakes()
        except Exception as exc:
            await interaction.followup.send(f"Could not load USGS data: {exc}", ephemeral=True)
            return

        if not quakes:
            await interaction.followup.send("No recent earthquakes found.", ephemeral=True)
            return

        top = quakes[0]
        ts = top.get("time")
        time_text = (
            dt.datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M UTC")
            if ts
            else "N/A"
        )

        points = [{"lat": q.get("lat"), "lon": q.get("lon"), "value": q.get("magnitude", 0)} for q in quakes[:20]]
        heatmap_path = world_heatmap(points, "Latest Earthquakes")
        file = discord.File(heatmap_path, filename=heatmap_path.name)

        embed = geo_card("GeoLive Earthquake Report")
        embed.add_field(name="📍 Location", value=top.get("place", "Unknown"), inline=False)
        embed.add_field(name="🌡 Magnitude", value=str(top.get("magnitude")), inline=True)
        embed.add_field(name="📊 Depth", value=f"{top.get('depth')} km", inline=True)
        embed.add_field(name="⏱ Time (UTC)", value=time_text, inline=True)
        embed.add_field(name="🌐 Latitude", value=str(top.get("lat")), inline=True)
        embed.add_field(name="🌍 Longitude", value=str(top.get("lon")), inline=True)
        embed.add_field(name="────────────────────────", value=thin("Heatmap of latest events"), inline=False)
        embed.set_image(url=f"attachment://{heatmap_path.name}")
        embed.set_footer(text="Data source: USGS Earthquake Hazards Program")

        for quake in quakes[:5]:
            embed.add_field(
                name=f"M {quake.get('magnitude', 'N/A')} | {quake.get('place', 'Unknown')}",
                value=f"Lat: {quake.get('lat')} Lon: {quake.get('lon')} Depth: {quake.get('depth')} km",
                inline=False,
            )

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Disaster(bot))
