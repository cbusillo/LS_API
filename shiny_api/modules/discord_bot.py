"""Class to import cogs from cog dir"""
import os
import textwrap
import discord
from discord.ext import commands
import shiny_api.modules.load_config as config


class ShinyBot(commands.Bot):
    """Class to import cogs from cog dir"""

    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix="/")

    async def setup_hook(self):
        for file in os.listdir(config.COG_DIR):
            if file.endswith(".py"):
                # await self.load_extension(file)
                await self.load_extension(f"shiny_api.discord_cogs.{file[:-3]}")


def start_discord_bot():
    """Create bot and run"""
    shiny_bot = ShinyBot()
    shiny_bot.run(config.DISCORD_TOKEN)


async def wrap_reply_lines(lines: str, message: discord.Message):
    """Break up messages that are longer than 2000
    chars and send multible messages to discord"""
    if lines is None or lines == "":
        lines = "No lines to send"
    lines_list = textwrap.wrap(lines, 2000 - len(message.author.mention), break_long_words=True, replace_whitespace=False)
    if message.author.bot is False:
        lines_list[0] = f"{message.author.mention} {lines_list[0]}"
    for line in lines_list:
        await message.channel.send(line)
