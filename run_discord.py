#!/usr/bin/env python3.11
"""File to run discord bot""" ""
from shiny_app.modules import discord_bot
from shiny_app.classes.config import Config


def start_discord_bot():
    """Create bot and run"""
    shiny_bot = discord_bot.ShinyBot()
    shiny_bot.run(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    start_discord_bot()
