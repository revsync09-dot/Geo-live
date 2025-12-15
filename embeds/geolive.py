from __future__ import annotations

import discord

from config import ICON_URL
from embeds.style import thin


def _is_valid_http(url: str | None) -> bool:
    return bool(url and (url.startswith("http://") or url.startswith("https://")))


def geo_card(title: str, description: str | None = None, *, color: int | None = None, icon_url: str | None = None) -> discord.Embed:
    embed = discord.Embed(
        title=f"🌐 {thin(title)}",
        description=description,
        color=color or 0x00AEEF,
    )
    icon = icon_url or ICON_URL
    if _is_valid_http(icon):
        embed.set_thumbnail(url=icon)
    return embed
