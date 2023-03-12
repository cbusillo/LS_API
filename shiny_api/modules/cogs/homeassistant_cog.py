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
        roomba = ha.Vacuum()
        status = getattr(roomba, choices)()
        await context.response.send_message(f"Vacuum is {status or choices}ing")

    @app_commands.command(name="alarm")
    @app_commands.choices(choices=get_functions(ha.Alarm))
    @commands.has_role("Shiny")
    async def arm(self, context: discord.Interaction, choices: str):
        alarm = ha.Alarm()
        status = getattr(alarm, choices)()
        await context.response.send_message(f"Alarm is {status or choices}ing")

    @app_commands.command(name="taylor_swiftly")
    @app_commands.choices(choices=get_functions(ha.TaylorSwiftly()))
    @commands.has_role("Shiny")
    async def tesla(self, context: discord.Interaction, choices: str):
        taylor = ha.TaylorSwiftly()
        status = taylor.get_functions()[choices]()
        await context.response.send_message(f"Taylor Swiftly is {status or choices}")


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(HomeAssistantCog(client))
