"""Exception handler for discord commands"""
import os
import discord
from discord.ext import commands

print(f"Importing {os.path.basename(__file__)}...")


class ExceptionHandler(commands.Cog):
    """Exception handler for discord commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        bot.tree.error(coro=self.__dispatch_to_app_command_handler)

    async def __dispatch_to_app_command_handler(
            self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        self.bot.dispatch("app_command_error", interaction, error)

    @commands.Cog.listener("on_app_command_error")
    async def get_app_command_error(
            self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Handle app command errors"""
        await interaction.response.send_message(error)


async def setup(bot: commands.Bot):
    """setup cog"""
    await bot.add_cog(ExceptionHandler(bot))
