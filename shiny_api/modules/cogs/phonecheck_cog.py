"""Allow PhoneCheck lookup from discord cog"""
import os
import discord
from discord import app_commands
from discord.ext import commands
import shiny_api.classes.phonecheck as pc


print(f"Importing {os.path.basename(__file__)}...")


class PhoneCheckCog(commands.Cog):
    """PhoneCheck functions"""

    def __init__(self, client: commands.Cog):
        self.client = client

    @app_commands.command(name="pc")
    @commands.has_role("Shiny")
    async def pc_lookup_command(self, context: discord.Interaction, serial_number: str):
        """Look up serial number in PhoneCheck"""
        device = pc.Device(serial_number=serial_number)
        await context.response.send_message(device)


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(PhoneCheckCog(client))
