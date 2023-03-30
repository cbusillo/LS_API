"""Class to import cogs from cog dir"""
import textwrap
import logging
import discord
from discord.ext import commands
from shiny_api.modules.load_config import Config


async def start_discord_bot():
    """Create bot and run"""
    shiny_bot = commands.Bot(intents=discord.Intents.all(), command_prefix="/")
    shiny_bot.intents
    for file in Config.COG_DIR.iterdir():
        if file.suffix == ".py" and file.name != "__init__.py":
            await shiny_bot.load_extension(file.stem)
            logging.info(f"Loaded cog: {file.stem}")

    shiny_bot.run(Config.DISCORD_TOKEN)


async def wrap_reply_lines(lines: str, message: discord.Message):
    """Break up messages that are longer than 2000
    chars and send multible messages to discord"""
    if lines is None or lines == "":
        lines = "No lines to send"
    lines_list = textwrap.wrap(
        lines,
        2000 - len(message.author.mention),
        break_long_words=True,
        replace_whitespace=False,
    )
    if message.author.bot is False:
        lines_list[0] = f"{message.author.mention} {lines_list[0]}"
    for line in lines_list:
        await message.channel.send(line)
