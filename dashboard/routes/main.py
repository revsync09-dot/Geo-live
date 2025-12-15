from __future__ import annotations

import json
from typing import Any, Dict

from flask import Blueprint, jsonify, render_template, request, session

from dashboard.utils.storage import get_guild_config, save_guild_config

main_bp = Blueprint("main", __name__)


@main_bp.route("/dashboard")
def dashboard_view():
    user = session.get("user")
    guilds = session.get("guilds", [])
    return render_template("dashboard.html", user=user, guilds=guilds)


@main_bp.route("/guilds")
def guilds_view():
    user = session.get("user")
    guilds = session.get("guilds", [])
    return render_template("guilds.html", user=user, guilds=guilds)


@main_bp.route("/guild/<guild_id>")
def guild_settings(guild_id: str):
    user = session.get("user")
    cfg = get_guild_config(guild_id)
    location = session.get("user_location")
    return render_template(
        "guild_settings.html", user=user, guild_id=guild_id, cfg=cfg, location=location
    )


@main_bp.route("/guild/<guild_id>/save", methods=["POST"])
def guild_save(guild_id: str):
    data: Dict[str, Any] = request.get_json(force=True) or {}
    save_guild_config(guild_id, data)
    return jsonify({"success": True, "config": data})


@main_bp.route("/location/update", methods=["POST"])
def update_location():
    payload = request.get_json(force=True) or {}
    session["user_location"] = {"lat": payload.get("lat"), "lon": payload.get("lon")}
    return jsonify({"success": True})

