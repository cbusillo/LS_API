"""Allow LightSpped lookup from discord cog"""
import os
import discord
from discord import app_commands
from discord.ext import commands
from shiny_api.modules.connect_ls import generate_ls_access
from shiny_api.classes.ls_item import Item

print(f"Importing {os.path.basename(__file__)}...")


class LightSpeedCog(commands.Cog):
    """Lightspeed functions"""

    def __init__(self, client: commands.Cog):
        self.client = client

    @app_commands.command(name="ls_price")
    @commands.has_role("Shiny")
    async def ls_price_lookup_command(self, context: discord.Interaction, search: str):
        """Look up price in Lightspeed"""
        await context.response.defer()
        generate_ls_access()
        items = Item.get_item_by_desciption(search)
        if items is None:
            await context.followup.send("No results")
            return
        message_output = ""
        for item in items:
            message_output += f"{item.description} is ${item.prices.item_price[0].amount}\n"

        await context.followup.send(message_output)


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(LightSpeedCog(client))
