from __future__ import annotations

import datetime as dt

import discord
from discord import app_commands
from discord.ext import commands

from api_clients import weatherapi
from embeds.geolive import geo_card
from embeds.style import thin
from graphing.weather_graph import create_weather_graph


def _is_valid_http(url: str | None) -> bool:
    return bool(url and (url.startswith("http://") or url.startswith("https://")))


class Weather(commands.GroupCog, name="weather"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="graph", description="Show temperature/dew point graph for today.")
    async def graph(self, interaction: discord.Interaction, location: str) -> None:
        await interaction.response.defer()

        try:
            today = dt.date.today().isoformat()
            history = await weatherapi.get_weather_history(location, today)
        except Exception as exc:
            await interaction.followup.send(f"Could not load data: {exc}", ephemeral=True)
            return

        graph_path = create_weather_graph(
            history["times"],
            history["temps"],
            history["dewpoints"],
            location.title(),
        )
        file = discord.File(graph_path, filename="graph.png")

        embed = geo_card("GeoLive Weather Graph")
        embed.add_field(name="📍 Location", value=location.title(), inline=False)
        embed.add_field(name="📅 Date", value=str(today), inline=True)
        embed.add_field(
            name="────────────────────────",
            value=thin("Temperature / Dew Point today"),
            inline=False,
        )
        embed.set_image(url="attachment://graph.png")
        embed.set_footer(text="Data source: WeatherAPI.com")

        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="now", description="Show current weather.")
    async def now(self, interaction: discord.Interaction, location: str) -> None:
        await interaction.response.defer()

        try:
            current = await weatherapi.get_current_weather(location)
        except Exception as exc:
            await interaction.followup.send(f"Could not load data: {exc}", ephemeral=True)
            return

        embed = geo_card("GeoLive Weather Report")
        icon_url = current.get("icon")
        if icon_url and icon_url.startswith("//"):
            icon_url = f"https:{icon_url}"

        embed.add_field(name="📍 Location", value=f"{current.get('city')}, {current.get('country')}", inline=False)
        embed.add_field(name="🌡 Temperature", value=f"{current.get('temp_c')}°C", inline=True)
        embed.add_field(name="💧 Humidity", value=f"{current.get('humidity')}%", inline=True)
        embed.add_field(name="🌬 Wind", value=f"{current.get('wind_kph')} kph", inline=True)
        embed.add_field(name="🌡 Dew Point", value=f"{current.get('dewpoint_c')}°C", inline=True)
        embed.add_field(
            name="────────────────────────",
            value=thin("Current conditions"),
            inline=False,
        )
        embed.add_field(name="Condition", value=current.get("condition", "N/A"), inline=False)

        if _is_valid_http(icon_url):
            embed.set_image(url=icon_url)

        embed.set_footer(text="Data source: WeatherAPI.com")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="forecast", description="Show 3-day forecast with UV and air quality.")
    async def forecast(self, interaction: discord.Interaction, location: str) -> None:
        await interaction.response.defer()

        try:
            forecast = await weatherapi.get_forecast(location, days=3)
        except Exception as exc:
            await interaction.followup.send(f"Could not load forecast: {exc}", ephemeral=True)
            return

        embed = geo_card("GeoLive Weather Forecast")
        embed.add_field(name="📍 Location", value=location.title(), inline=False)
        embed.add_field(
            name="────────────────────────",
            value=thin("3-day outlook with UV & AQI"),
            inline=False,
        )

        for day in forecast.get("days", []):
            title = f"{day.get('date')} • {day.get('condition', 'Weather')}"
            values = (
                f"Avg: {day.get('avg_temp_c')}°C | Max: {day.get('max_temp_c')}°C | Min: {day.get('min_temp_c')}°C\n"
                f"UV: {day.get('uv')} | PM2.5: {day.get('aqi_pm2_5')} | PM10: {day.get('aqi_pm10')}"
            )
            embed.add_field(name=title, value=values, inline=False)

        alerts = forecast.get("alerts", [])
        if alerts:
            alert_texts = []
            for alert in alerts[:3]:
                alert_texts.append(f"• {alert.get('event')} ({alert.get('severity', 'N/A')})")
            embed.add_field(
                name="⚠️ Alerts",
                value="\n".join(alert_texts),
                inline=False,
            )

        embed.set_footer(text="Data source: WeatherAPI.com")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Weather(bot))
