import os
import discord
from discord.ext import commands
from kivy.uix.button import Button

import shiny_api.modules.load_config as config
from shiny_api.classes.ls_item import Item
from shiny_api.modules.connect_ls import generate_ls_access

print(f"Importing {os.path.basename(__file__)}...")

COMMAND_PREFIX = "."

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.display_name} has connected to Discord!")

    channels = bot.get_all_channels()

    channel = discord.utils.get(channels, name="bot-config")

    async for message in channel.history():
        if message.content[0] == COMMAND_PREFIX:
            await message.delete()


@bot.command()
async def ls(context: commands.Context, *args):
    if context.message.content[0] == COMMAND_PREFIX:
        await context.message.delete()
    if not args:
        return
    if args[0].lower() == "price" and len(args) > 1:
        generate_ls_access()
        items = Item.get_item_by_desciption(args[1])
        for item in items:
            print(item)
            await context.channel.send(f"{item.description} is ${item.prices.item_price[0].amount}")


@bot.command()
async def best(context: commands.Context):
    await context.channel.send(f"{context.author.mention} is the best!")
    context.message.delete()


def start_bot(caller: Button):
    bot.run(config.DISCORD_TOKEN)
    caller.text = f"{caller.text.split(chr(10))[0]}\nDiscord Bot Running"
    caller.disabled = False
    caller.text = caller.text.split("\n")[0]
