"""Allow LightSpped lookup from discord cog"""
import textwrap
import discord
from discord import app_commands
from discord.ext import commands
from shiny_app.classes.ls_item import Item


class LightSpeedCog(commands.Cog):
    """Lightspeed functions"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ls_price")  # type: ignore
    @app_commands.checks.has_role("Shiny")
    async def ls_price_lookup_command(self, context: discord.Interaction, search: str):
        """Look up price in Lightspeed"""
        await context.response.defer()
        items = Item.get_items_by_desciption(descriptions=search, archived=False)
        if len(items) == 0:
            await context.followup.send("No results")
            return
        message_output = ""
        for item in items:
            message_output += f"{item.description} is ${item.price}\n"

        lines = textwrap.wrap(message_output, width=2000, replace_whitespace=False, break_long_words=False)
        for line in lines:
            await context.followup.send(line)


async def setup(bot: commands.Bot):
    """Add cog"""
    await bot.add_cog(LightSpeedCog(bot))
