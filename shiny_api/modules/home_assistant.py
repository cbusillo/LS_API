"""Home Assistant module for Shiny API."""
import os
from homeassistant_api import Client

print(f"Importing {os.path.basename(__file__)}...")


async def get_homeassistant_client():
    """Get Home Assistant client"""
    client = Client(
        url="https://homeassistant.local",
        token="",
        verify_ssl=False,
    )
    return client


if __name__ == "__main__":
    get_homeassistant_client()
