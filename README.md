# GeoLive Bot

Discord bot for live weather, space, and disaster data with charts, embeds, and auto-feeds.

## Quickstart
1. Install Python 3.11+.
2. Create `.env`:
   ```
   DISCORD_TOKEN=YOUR_DISCORD_TOKEN
   WEATHER_API_KEY=YOUR_WEATHER_API_KEY
   NASA_KEY=YOUR_NASA_KEY
   ICON_URL=https://your-icon
   SENTRY_DSN=OPTIONAL_SENTRY_DSN
   ```
3. Install deps: `pip install -r requirements.txt`
4. Run: `python main.py`

## Slash Commands
- `/weather graph location:<city>` – temperature/dew point graph (today).
- `/weather now location:<city>` – current weather report (UV, AQI, icon).
- `/weather forecast location:<city>` – 3-day outlook with UV/AQI and alerts.
- `/space aurora` – NASA space weather / aurora alerts.
- `/space iss` – live ISS position.
- `/disaster quake` – realtime earthquakes with heatmap.

## Auto-Feed
Every 4h the bot posts an earthquake alert to the first text channel in each guild (`cogs/auto_feed.py`). Interval configurable via `Settings.auto_feed_hours`.

## Project Layout
- `main.py` – bot entrypoint, loads all cogs.
- `config.py` – settings and colors.
- `api_clients/` – API calls (WeatherAPI, NASA, USGS, OpenNotify).
- `graphing/` – Matplotlib graphs & heatmaps.
- `embeds/` – central embed design helpers.
- `cogs/commands/` – slash commands.
- `cogs/auto_feed.py` – auto-feed tasks.
- `Dockerfile`, `fly.toml` – Fly.io deployment.
- `dashboard/` – Flask + Tailwind premium dashboard with Discord OAuth.

## Deployment on Fly.io
```
fly launch --no-deploy
fly secrets set DISCORD_TOKEN=... WEATHER_API_KEY=... NASA_KEY=... ICON_URL=...
fly deploy
```

## Design Note
GeoLive uses a thin, minimal Apple-style embed system with a premium card layout across all commands.

## Dashboard (Flask + Tailwind)
```
cd dashboard
python -m pip install -r ../requirements.txt  # reuse Python deps incl. Flask
npm install
npm run build  # produces static/css/main.css
python app.py
```
Set `.env` with `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `REDIRECT_URI`, `FLASK_SECRET_KEY`. Login via Discord to manage guild settings and feeds; configs are stored in `data/config/<guild_id>.json`.
