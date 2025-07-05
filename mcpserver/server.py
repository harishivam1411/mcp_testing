import httpx
import sys
import logging
from typing import Any
from mcp.server.fastmcp import FastMCP

"""
To run the server:
uv run server.py / python server.py
"""

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP(
    name="weather",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8000,  # only used for SSE transport (set this to any port)
)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)  # Reduced timeout
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout when requesting {url}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} when requesting {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when requesting {url}: {e}")
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
    Event: {props.get('event', 'Unknown')}
    Area: {props.get('areaDesc', 'Unknown')}
    Severity: {props.get('severity', 'Unknown')}
    Description: {props.get('description', 'No description available')}
    Instructions: {props.get('instruction', 'No specific instructions provided')}
    """


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g., CA, NY)
    """
    # Validate state code
    if not state or len(state) != 2:
        return "Please provide a valid two-letter US state code (e.g., CA, NY)."

    state = state.upper()
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."

    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    try:
        forecast_url = points_data["properties"]["forecast"]
    except KeyError:
        return "Invalid response format from weather service."

    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    try:
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            forecast = f"""
                {period['name']}:
                Temperature: {period['temperature']}°{period['temperatureUnit']}
                Wind: {period['windSpeed']} {period['windDirection']}
                Forecast: {period['detailedForecast']}
                """
            forecasts.append(forecast)
        return "\n---\n".join(forecasts)
    except KeyError:
        return "Invalid forecast data format received."


# Run the server
if __name__ == "__main__":
    # Allow transport to be specified via command line argument
    transport = "sse"
    if len(sys.argv) > 1:
        transport = sys.argv[1]

    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}. Use 'stdio' or 'sse'.")