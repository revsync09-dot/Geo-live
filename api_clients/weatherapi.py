from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx

CURRENT_URL = "https://api.weatherapi.com/v1/current.json"
HISTORY_URL = "https://api.weatherapi.com/v1/history.json"
FORECAST_URL = "https://api.weatherapi.com/v1/forecast.json"


class WeatherAPIError(Exception):
    pass


def _get_api_key() -> str:
    key = os.getenv("WEATHER_API_KEY")
    if not key:
        raise WeatherAPIError("WEATHER_API_KEY missing (set in .env).")
    return key


async def _get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise WeatherAPIError(f"WeatherAPI request failed: {resp.text}")
        return resp.json()


async def get_current_weather(location: str) -> Dict[str, Any]:
    key = _get_api_key()
    params = {"key": key, "q": location, "aqi": "yes"}
    data = await _get_json(CURRENT_URL, params)
    current = data.get("current", {})
    location_info = data.get("location", {})
    return {
        "temp_c": current.get("temp_c"),
        "dewpoint_c": current.get("dewpoint_c"),
        "humidity": current.get("humidity"),
        "wind_kph": current.get("wind_kph"),
        "uv": current.get("uv"),
        "condition": current.get("condition", {}).get("text"),
        "icon": current.get("condition", {}).get("icon"),
        "country": location_info.get("country"),
        "region": location_info.get("region"),
        "city": location_info.get("name"),
        "aqi_pm2_5": current.get("air_quality", {}).get("pm2_5"),
        "aqi_pm10": current.get("air_quality", {}).get("pm10"),
    }


async def get_weather_history(location: str, date: str) -> Dict[str, List[Any]]:
    key = _get_api_key()
    params = {"key": key, "q": location, "dt": date}
    payload = await _get_json(HISTORY_URL, params)
    forecastday = payload.get("forecast", {}).get("forecastday", [])
    if not forecastday:
        raise WeatherAPIError("No historical data found.")
    hours = forecastday[0].get("hour", [])
    times = [h.get("time", "") for h in hours]
    temps = [h.get("temp_c") for h in hours]
    dewpoints = [h.get("dewpoint_c") for h in hours]
    return {"times": times, "temps": temps, "dewpoints": dewpoints}


async def get_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    key = _get_api_key()
    params = {"key": key, "q": location, "days": days, "aqi": "yes", "alerts": "yes"}
    payload = await _get_json(FORECAST_URL, params)
    forecast_days = []
    for day in payload.get("forecast", {}).get("forecastday", []):
        forecast_days.append(
            {
                "date": day.get("date"),
                "avg_temp_c": day.get("day", {}).get("avgtemp_c"),
                "max_temp_c": day.get("day", {}).get("maxtemp_c"),
                "min_temp_c": day.get("day", {}).get("mintemp_c"),
                "uv": day.get("day", {}).get("uv"),
                "condition": day.get("day", {}).get("condition", {}).get("text"),
                "icon": day.get("day", {}).get("condition", {}).get("icon"),
                "aqi_pm2_5": day.get("day", {}).get("air_quality", {}).get("pm2_5"),
                "aqi_pm10": day.get("day", {}).get("air_quality", {}).get("pm10"),
            }
        )
    alerts = payload.get("alerts", {}).get("alert", [])
    return {"days": forecast_days, "alerts": alerts}
