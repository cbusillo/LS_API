"""Allow LightSpped lookup from discord cog"""
import textwrap
import discord
from discord import app_commands
from discord.ext import commands
from shiny_api.classes.ls_item import Item


class LightSpeedCog(commands.Cog):
    """Lightspeed functions"""

    def __init__(self, client: discord.Client):
        self.client = client

    @app_commands.command(name="ls_price")
    @app_commands.checks.has_role("Shiny")
    async def ls_price_lookup_command(self, context: discord.Interaction, search: str):
        """Look up price in Lightspeed"""
        await context.response.defer()
        items = Item.get_items_by_desciption(descriptions=search)
        if len(items.item_list) == 0:
            await context.followup.send("No results")
            return
        message_output = ""
        for item in items.item_list:
            message_output += f"{item.description} is ${item.prices.item_price[0].amount}\n"

        lines = textwrap.wrap(
            message_output,
            width=2000,
            replace_whitespace=False,
            break_long_words=False)
        for line in lines:
            await context.followup.send(line)


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(LightSpeedCog(client))
