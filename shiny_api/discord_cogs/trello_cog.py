"""Allow Trello interaction from discord cog"""
import discord
from discord import app_commands
from discord.ext import commands
from trello import TrelloClient
from shiny_api.modules.load_config import Config


class TrelloCog(commands.Cog):
    """Communicate to Trello"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def trello_lists_list(
            self, _: discord.Interaction,
            current: str) -> list[app_commands.Choice[str]]:
        """Get list of lists as choices"""
        trello_client = TrelloClient(api_key=Config.TRELLO_APIKEY, token=Config.TRELLO_OAUTH_TOKEN)
        inventory_board = trello_client.get_board(Config.TRELLO_INVENTORY_BOARD)
        inventory_lists = inventory_board.get_lists(list_filter="open")
        return [
            app_commands.Choice(name=trello_list.name, value=trello_list.id)
            for trello_list in inventory_lists
            if current.lower() in trello_list.name.lower()
        ]

    @app_commands.command(name="trello_add")
    @app_commands.autocomplete(trello_list=trello_lists_list)
    @app_commands.checks.has_role("Shiny")
    async def trello_add(
            self,
            context: discord.Interaction,
            card_name: str,
            trello_list: str = Config.TRELLO_LIST_DEFAULT):
        """Add card to Trello list"""
        await context.response.defer()
        trello_client = TrelloClient(api_key=Config.TRELLO_APIKEY, token=Config.TRELLO_OAUTH_TOKEN)
        inventory_board = trello_client.get_board(Config.TRELLO_INVENTORY_BOARD)
        inventory_list = inventory_board.get_list(list_id=trello_list)
        inventory_list.add_card(
            card_name,
        )
        await context.followup.send(f"Added '{card_name}' to list {inventory_list.name}")

    @app_commands.command(name="trello_list")
    @app_commands.autocomplete(trello_list=trello_lists_list)
    @app_commands.checks.has_role("Shiny")
    async def trello_list(
            self,
            context: discord.Interaction,
            trello_list: str = Config.TRELLO_LIST_DEFAULT):
        """Get cards from Trello list"""
        await context.response.defer()
        trello_client = TrelloClient(api_key=Config.TRELLO_APIKEY, token=Config.TRELLO_OAUTH_TOKEN)
        inventory_board = trello_client.get_board(Config.TRELLO_INVENTORY_BOARD)
        message_output = ""
        inventory_list = inventory_board.get_list(list_id=trello_list)
        for card in inventory_list.list_cards(card_filter="open"):
            label_text = " ".join([label.name for label in card.labels])
            if label_text:
                label_text = f" **{label_text}** "
            message_output += f"{card.name}{label_text} {card.description}\n"
        if message_output:
            await context.followup.send(message_output)
        return


async def setup(bot: commands.Bot):
    """Add cog"""
    await bot.add_cog(TrelloCog(bot))
