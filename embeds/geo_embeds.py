from __future__ import annotations

import discord

from config import Settings


def _is_valid_http(url: str | None) -> bool:
    return bool(url and (url.startswith("http://") or url.startswith("https://")))


def _is_valid_image_url(url: str | None) -> bool:
    return bool(
        url
        and (
            url.startswith("http://")
            or url.startswith("https://")
            or url.startswith("attachment://")
        )
    )


def base_embed(settings: Settings, title: str, description: str, banner_url: str | None = None) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=settings.colour)
    if _is_valid_http(settings.embed_icon_url):
        embed.set_thumbnail(url=settings.embed_icon_url)
    if banner_url and _is_valid_image_url(banner_url):
        embed.set_image(url=banner_url)
    embed.set_footer(text="GeoLive • Data from WeatherAPI, NASA, USGS, OpenNotify")
    return embed
