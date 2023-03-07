"""Allow LightSpped lookup from discord cog"""
import os
import textwrap
import discord
from discord import app_commands
from discord.ext import commands
from shiny_api.modules.connect_ls import generate_ls_access
from shiny_api.classes.ls_item import Items

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
        items = Items(descriptions=search)
        if len(items.item_list) == 0:
            await context.followup.send("No results")
            return
        message_output = ""
        for item in items.item_list:
            message_output += f"{item.description} is ${item.prices.item_price[0].amount}\n"

        lines = textwrap.wrap(message_output, width=2000, replace_whitespace=False, break_long_words=False)
        for line in lines:
            await context.followup.send(line)


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(LightSpeedCog(client))
