"""Home Assistant module for Shiny API."""
import os
from homeassistant_api import Client
import shiny_api.modules.load_config as config

print(f"Importing {os.path.basename(__file__)}...")


def get_homeassistant_client():
    """Get Home Assistant client"""
    client = Client(
        "http://ha.store1.logi.wiki",
        config.HOMEASSISTANT_API_KEY,
    )
    client.get_entity(entity_id="input_boolean.testing")
    print(client)
    # client.turn_on()
    return client


if __name__ == "__main__":
    get_homeassistant_client()
