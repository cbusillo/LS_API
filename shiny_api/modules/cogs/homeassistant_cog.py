"""TEMPLATE discord cog"""
import os
import discord
from discord import app_commands
from discord.ext import commands

print(f"Importing {os.path.basename(__file__)}...")


class HomeAssistantCog(commands.Cog):
    """Homeassistant API plugin"""

    def __init__(self, client: commands.Cog):
        self.client = client

    @app_commands.command(name="TEMPLATE")
    @commands.has_role("Shiny")
    async def TEMPLATE_lookup_command(self, context: discord.Interaction, serial_number: str):
        """Look up serial number in Sickw"""

        await context.response.send_message("TEMPLATE")


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(HomeAssistantCog(client))
