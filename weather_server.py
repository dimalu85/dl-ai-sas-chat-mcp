# weather_server.py — MCP Server for Open-Meteo (no API key required)
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 71: "Light snow", 73: "Snow",
    75: "Heavy snow", 80: "Rain showers", 81: "Heavy showers", 95: "Thunderstorm",
}

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city using Open-Meteo (free, no API key)."""
    async with httpx.AsyncClient() as client:
        # 1. Geocode city → lat/lon
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        geo.raise_for_status()
        results = geo.json().get("results")
        if not results:
            return f"City '{city}' not found."
        place = results[0]
        lat, lon = place["latitude"], place["longitude"]
        name = place.get("name", city)
        country = place.get("country", "")

        # 2. Fetch current weather
        weather = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "current": "temperature_2m,wind_speed_10m,weathercode",
                "temperature_unit": "celsius",
            },
        )
        weather.raise_for_status()
        current = weather.json()["current"]

    temp   = current["temperature_2m"]
    wind   = current["wind_speed_10m"]
    code   = current["weathercode"]
    desc   = WMO_CODES.get(code, f"Weather code {code}")

    return (
        f"Current weather in {name}, {country}:\n"
        f"  Condition  : {desc}\n"
        f"  Temperature: {temp}°C\n"
        f"  Wind speed : {wind} km/h"
    )

if __name__ == "__main__":
    mcp.run()
