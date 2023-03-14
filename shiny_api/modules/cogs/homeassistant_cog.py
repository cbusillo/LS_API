"""Homeasssistant discord cog"""
import os
from typing import Type
import discord
from discord import app_commands
from discord.ext import commands
import shiny_api.classes.homeassistant as ha

print(f"Importing {os.path.basename(__file__)}...")


class HomeAssistantCog(commands.Cog):
    """Homeassistant API plugin"""

    def __init__(self, client: commands.Cog):
        self.client = client

    @staticmethod
    def get_functions(function_name: Type[ha.HomeAssistant] | ha.TaylorSwiftly):
        """Get all functions from a class"""
        return [
            app_commands.Choice(name=function_choice, value=function_choice)
            for function_choice in function_name.get_functions()
        ]

    @app_commands.command(name="vacuum")
    @app_commands.choices(choices=get_functions(ha.Vacuum))
    @app_commands.checks.has_role("Shiny")
    async def vacuum(self, context: discord.Interaction, choices: str):
        """Vacuum commands"""
        roomba = ha.Vacuum()
        status = getattr(roomba, choices)()
        await context.response.send_message(f"Vacuum is {status or choices}")

    @app_commands.command(name="alarm")
    @app_commands.choices(choices=get_functions(ha.Alarm))
    @app_commands.checks.has_role("Shiny")
    async def alarm(self, context: discord.Interaction, choices: str):
        """Alarm commands"""
        alarm = ha.Alarm()
        status = getattr(alarm, choices)()
        await context.response.send_message(f"Alarm is {status or choices}")

    @app_commands.command(name="taylor_swiftly")
    @app_commands.choices(choices=get_functions(ha.TaylorSwiftly()))
    @app_commands.checks.has_role("Shiny")
    async def tesla(self, context: discord.Interaction, choices: str):
        """Tesla commands"""
        taylor = ha.TaylorSwiftly()
        status = taylor.get_functions()[choices]()
        await context.response.send_message(
            f"Taylor Swiftly {choices.split()[1]} is {status or choices}"
        )


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(HomeAssistantCog(client))
