from __future__ import annotations

import os
from urllib.parse import urlencode

import httpx
from flask import Blueprint, current_app, redirect, request, session, url_for

auth_bp = Blueprint("auth", __name__)

DISCORD_AUTH_BASE = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_API_BASE = "https://discord.com/api"
SCOPES = ["identify", "guilds"]


def _oauth_params() -> dict:
    return {
        "client_id": current_app.config.get("DISCORD_CLIENT_ID"),
        "client_secret": current_app.config.get("DISCORD_CLIENT_SECRET"),
        "redirect_uri": current_app.config.get("REDIRECT_URI"),
    }


@auth_bp.route("/login")
def login():
    params = {
        "client_id": current_app.config.get("DISCORD_CLIENT_ID"),
        "redirect_uri": current_app.config.get("REDIRECT_URI"),
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "prompt": "consent",
    }
    return redirect(f"{DISCORD_AUTH_BASE}?{urlencode(params)}")


@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("home"))

    token_data = _exchange_code(code)
    if not token_data:
        return redirect(url_for("home"))

    session["token"] = token_data
    session["user"] = _fetch_user(token_data["access_token"])
    session["guilds"] = _fetch_guilds(token_data["access_token"])

    return redirect(url_for("main.dashboard_view"))


def _exchange_code(code: str):
    data = {
        "client_id": current_app.config.get("DISCORD_CLIENT_ID"),
        "client_secret": current_app.config.get("DISCORD_CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": current_app.config.get("REDIRECT_URI"),
        "scope": " ".join(SCOPES),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    with httpx.Client() as client:
        resp = client.post(DISCORD_TOKEN_URL, data=data, headers=headers)
        if resp.status_code != 200:
            return None
        return resp.json()


def _fetch_user(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    with httpx.Client() as client:
        resp = client.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
        resp.raise_for_status()
        return resp.json()


def _fetch_guilds(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    with httpx.Client() as client:
        resp = client.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=headers)
        resp.raise_for_status()
        guilds = resp.json()
    manageable = [
        g for g in guilds if g.get("permissions_new") or (g.get("permissions", 0) & 0x20)
    ]
    return manageable
