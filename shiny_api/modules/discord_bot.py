"""Class to import cogs from cog dir"""
import os
import discord
from discord.ext import commands
import shiny_api.modules.load_config as config

print(f"Importing {os.path.basename(__file__)}...")


class ShinyBot(commands.Bot):
    """Class to import cogs from cog dir"""

    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix="/")

    async def setup_hook(self):
        for file in os.listdir(config.COG_DIR):
            if file.endswith(".py"):
                # await self.load_extension(file)
                await self.load_extension(f"shiny_api.modules.cogs.{file[:-3]}")


def start_discord_bot():
    """Create bot and run"""
    shiny_bot = ShinyBot()
    shiny_bot.run(config.DISCORD_TOKEN)
