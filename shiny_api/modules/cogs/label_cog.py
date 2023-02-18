"""Allow label printing from discord cog"""
import os
import discord
from discord import app_commands
from discord.ext import commands
from shiny_api.modules.label_print import print_text


print(f"Importing {os.path.basename(__file__)}...")


class LabelCog(commands.Cog):
    """Print to label printer in config"""

    def __init__(self, client: commands.Cog):
        self.client = client

    @app_commands.command(name="label")
    @commands.has_role("Shiny")
    async def label_command(
        self, context: discord.Interaction, text: str, quantity: int = 1, date: bool = True, barcode: str = None
    ):
        """Print label"""
        await context.response.send_message(f"Printing {quantity} label with {text=} and {date=}")
        text = text.strip()

        print_text(text, quantity=quantity, print_date=date, barcode=barcode)


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(LabelCog(client))
