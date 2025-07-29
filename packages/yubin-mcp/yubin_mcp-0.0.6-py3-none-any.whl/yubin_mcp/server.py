from mcp.server.fastmcp import FastMCP
import posuto
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Create MCP server instance
mcp = FastMCP("yubin-mcp")

# Tool to get address and map link from postal code
@mcp.tool()
def get_address_from_postal_code(postal_code: str) -> dict:
    """
    Get address and map link from postal code.
    """
    try:
        result = posuto.get(postal_code)
        if result:
            address = f"{result.prefecture}{result.city}{result.neighborhood}"
            map_url = f"https://www.google.com/maps/search/?api=1&query={address}"
            return {"address": address, "map_url": map_url}
        else:
            return {"error": "No matching address found."}
    except Exception as e:
        return {"error": str(e)}

# Tool to get address and map link from coordinates
@mcp.tool()
def get_address_from_coordinates(latitude: float, longitude: float) -> dict:
    """
    Get address and map link from coordinates.
    """
    try:
        geolocator = Nominatim(user_agent="yubin-mcp")
        location = geolocator.reverse((latitude, longitude), timeout=10)
        if location:
            address = location.address
            map_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
            return {"address": address, "map_url": map_url}
        else:
            return {"error": "No matching address found."}
    except GeocoderTimedOut:
        return {"error": "Geocoding service timeout occurred."}
    except Exception as e:
        return {"error": str(e)}


def main():
    mcp.run(transport="stdio")

# Start server
if __name__ == "__main__":
    main()
