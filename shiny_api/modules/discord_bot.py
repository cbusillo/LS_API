import os
import discord
import textwrap
from discord.ext import commands
from kivy.uix.button import Button
from trello import TrelloClient
import openai

import shiny_api.modules.load_config as config
from shiny_api.classes.ls_item import Item
from shiny_api.modules.connect_ls import generate_ls_access


print(f"Importing {os.path.basename(__file__)}...")

COMMAND_PREFIX = "."
TRELLO_INVENTORY_BOARD = "61697cfbd3529050685f9e3a"
TRELLO_INVENYORY_LISTS = {
    "pt": "61697d01d1c4463bc0fa066c",
    "tonia": "63e501ce9f4577e014f46f00",
    "ebay": "616af4a1b42d5e6af2222605",
    "china": "63cd686b0de2bc0082b20499",
}


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
        if message.content is None or len(message.content) == 0:
            break
        if message.content[0] == COMMAND_PREFIX:
            await message.delete()


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or not message.guild:
        prompt = message.content.replace(bot.user.mention, "").strip()
        engine = "text-davinci-003"
        if prompt.split()[0].lower() == "code":
            engine = "code-davinci-002"
            prompt = " ".join(prompt.split()[1:]).strip()

        if prompt.split()[0].lower() == "image":
            image_engine = "image-alpha-001"
            prompt = " ".join(prompt.split()[1:]).strip()
            async with message.channel.typing():
                await get_walle_image(message=message, engine=image_engine, prompt=prompt)
        async with message.channel.typing():
            await get_chatgpt_message(message=message, engine=engine, prompt=prompt)

    await bot.process_commands(message)
    if message.content is None or len(message.content) == 0:
        return
    if message.content[0] == COMMAND_PREFIX:
        # await message.delete()
        pass


async def get_walle_image(message: discord.Message, prompt: str, engine: str):
    print(f"Sending message: {prompt} to {engine}")
    try:
        response = await openai.Image.acreate(
            prompt=prompt, n=1, size="1024x1024", response_format="url", api_key=config.OPENAI_API_KEY
        )
    except openai.error.InvalidRequestError as exception:
        await message.channel.send(str(exception))
        return

    image_url = response["data"][0]["url"]

    embed = discord.Embed()
    embed.set_image(url=image_url)

    # Send the message
    await message.channel.send(embed=embed)


async def get_chatgpt_message(message: discord.Message, engine: str, prompt: str):
    print(f"Sending message: {prompt} to {engine}")
    try:
        response = await openai.Completion.acreate(
            engine=engine,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.8,
            api_key=config.OPENAI_API_KEY,
        )
    except openai.error.InvalidRequestError as exception:
        await message.channel.send(str(exception))
        return
    await wrap_lines(response["choices"][0]["text"], message=message)
    print(f"Received response: {response['choices'][0]['text']}")


async def wrap_lines(lines: list[str], message: discord.Message):
    lines = textwrap.wrap(lines, 2000, break_long_words=False, replace_whitespace=False)
    for line in lines:
        await message.channel.send(line)


@bot.command()
async def ls(context: commands.Context, *args):
    if len(args) == 0 or args is None:
        return
    if args[0].lower() == "price" and len(args) > 1:
        generate_ls_access()
        items = Item.get_item_by_desciption(args[1:])
        if items is None:
            await context.channel.send("No results")
            return
        message_output = ""
        for item in items:
            message_output += f"{item.description} is ${item.prices.item_price[0].amount}\n"

        await context.channel.send(message_output)


@bot.command()
async def trello(context: commands.Context, *args):
    if args is None or len(args) == 0:
        await trello_list_cards(TRELLO_INVENYORY_LISTS["pt"], context=context)
        return

    if len(args) > 1:
        if args[0].lower() == "list":
            if args[1].lower() not in TRELLO_INVENYORY_LISTS:
                return
            await trello_list_cards(list_id=TRELLO_INVENYORY_LISTS[args[1].lower()], context=context)
            return
        if args[0].lower() == "add":
            list_name = "pt"
            card_name = " ".join(args[1:])
            if args[1].lower() in TRELLO_INVENYORY_LISTS:
                list_name = args[1].lower()
            if len(args) > 2:
                card_name = " ".join(args[2:])
            await trello_add_card(list_id=TRELLO_INVENYORY_LISTS[list_name], card_name=card_name)


async def trello_add_card(list_id: int, card_name: str):
    client = TrelloClient(api_key=config.TRELLO_APIKEY, token=config.TRELLO_OAUTH_TOKEN)
    inventory_board = client.get_board(TRELLO_INVENTORY_BOARD)
    inventory_list = inventory_board.get_list(list_id=list_id)
    inventory_list.add_card(card_name)


async def trello_list_cards(list_id: int, context: commands.Context):
    client = TrelloClient(api_key=config.TRELLO_APIKEY, token=config.TRELLO_OAUTH_TOKEN)
    inventory_board = client.get_board(TRELLO_INVENTORY_BOARD)
    message_output = ""
    inventory_list = inventory_board.get_list(list_id=list_id)
    for card in inventory_list.list_cards(card_filter="open"):
        label_text = " ".join([label.name for label in card.labels])
        if label_text:
            label_text = f" **{label_text}** "
        message_output += f"{card.name}{label_text} {card.description}\n"
    if message_output:
        await context.channel.send(message_output)
    return


@bot.command()
async def clear(context: commands.Context, *args):
    if args[0].lower() == "bot":
        async for message in context.channel.history():
            if message.author == bot.user and message.id != context.message.id:
                await message.delete()


@bot.command()
async def best(context: commands.Context, *args):
    if args is None:
        await context.channel.send(f"{context.author.mention} is the best!")
        return
    users = bot.get_all_members()
    for user in users:
        if " ".join(args).lower() in user.name.lower():
            await context.channel.send(f"{user.mention} is the best!")


def start_bot(caller: Button):
    bot.run(config.DISCORD_TOKEN)
    caller.text = f"{caller.text.split(chr(10))[0]}\nDiscord Bot Running"
    caller.disabled = False
    caller.text = caller.text.split("\n")[0]
