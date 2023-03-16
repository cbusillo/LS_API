#!/usr/bin/env python

from shiny_api.modules import discord_bot
from shiny_api.modules import load_config as config


def start_discord_bot():
    """Create bot and run"""
    shiny_bot = discord_bot.ShinyBot()
    shiny_bot.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    start_discord_bot()
