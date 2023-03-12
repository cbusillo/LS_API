"""Homeasssistant discord cog"""
import os
from typing import Type
import discord
from discord import app_commands
from discord.ext import commands
import shiny_api.modules.homeassistant as ha

print(f"Importing {os.path.basename(__file__)}...")


class HomeAssistantCog(commands.Cog):
    """Homeassistant API plugin"""

    def __init__(self, client: commands.Cog):
        self.client = client

    @staticmethod
    def get_functions(function_name: Type[ha.HomeAssistant]):
        return [
            app_commands.Choice(name=function_choice, value=function_choice) for function_choice in function_name.get_functions()
        ]

    @app_commands.command(name="vacuum")
    @app_commands.choices(choices=get_functions(ha.Vacuum))
    @commands.has_role("Shiny")
    async def vacuum(self, context: discord.Interaction, choices: str):
        # print(await self.get_functions())
        roomba = ha.Vacuum()
        roomba_function = getattr(roomba, choices)
        roomba_function()
        await context.response.send_message(f"Vacuum is {choices}ing")

    @app_commands.command(name="alarm")
    @app_commands.choices(choices=get_functions(ha.Alarm))
    @commands.has_role("Shiny")
    async def arm(self, context: discord.Interaction, choices: str):
        # print(await self.get_functions())
        testing = ha.Alarm()
        testing_function = getattr(testing, choices)
        testing_function()
        await context.response.send_message(f"Testing is {choices}ing")

    @app_commands.command(name="tesla")
    @app_commands.choices(choices=get_functions(ha.Lock))
    @commands.has_role("Shiny")
    async def tesla(self, context: discord.Interaction, choices: str):
        # print(await self.get_functions())
        testing = ha.Lock(entity_id="taylor_swiftly_doors", location="home")
        testing_function = getattr(testing, choices)
        testing_function()
        await context.response.send_message(f"Testing is {choices}ing")


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(HomeAssistantCog(client))
