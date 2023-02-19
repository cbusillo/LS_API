"""Sync cogs to discord to enable /commands"""
import asyncio
import importlib.metadata
import os
import platform
import luddite
import discord
from discord.ext import commands
from discord import app_commands

print(f"Importing {os.path.basename(__file__)}...")

BOT_CHANNEL = 1073943829192912936


class SetupCog(commands.Cog):
    """Add anything related to setting up bot here"""

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        super().__init__()

    @commands.command(name="sync")
    async def sync_command(self, context: commands.Context) -> None:
        """Add slash commands to Discord guid"""
        if platform.node().lower() == "secureerase":
            await context.defer()
            if importlib.metadata.version("shiny_api") != luddite.get_version_pypi("shiny_api"):
                os._exit(1)  # pylint: disable=protected-access
            await asyncio.sleep(2)

        try:
            await context.message.delete()
            await self.check_server()
        except discord.errors.NotFound:
            print("Not able to delete message")
            return

    @app_commands.command(name="clear")
    @app_commands.choices(
        scope=[
            app_commands.Choice(name="Bot", value="bot"),
            app_commands.Choice(name="All", value="all"),
        ]
    )
    async def clear_command(self, context: discord.Interaction, scope: str) -> None:
        """Clear all or bot messages in bot-config"""
        if context.channel.id != BOT_CHANNEL:
            await context.channel.send("Cannot use in this channel")
            return
        temp_message = await context.channel.send(f"Clearing messages from {scope}")
        await context.response.defer()
        if scope == "bot":
            async for message in context.channel.history():
                if message.author == context.client.user and message != temp_message:
                    await message.delete()
        elif scope == "all":
            async for message in context.channel.history():
                if message != temp_message:
                    await message.delete()
        await temp_message.delete()

    @commands.Cog.listener("on_ready")
    async def shiny_bot_connect(self):
        """Print console message that bot is connected"""
        print(f"{self.client.user.display_name} has connected to Discord!")

    @commands.Cog.listener("on_ready")
    async def set_dev_rol(self):
        """Add dev role to activate bot if run from dev machine"""
        await self.check_server()

    async def check_server(self):
        """Set bot role and sync commands"""
        self.client.tree.copy_global_to(guild=self.client.guilds[0])
        synced = await self.client.tree.sync(guild=self.client.guilds[0])
        await self.client.get_channel(BOT_CHANNEL).send(f"Synced {len(synced)} commands from {platform.node()}.")
        role = discord.utils.get(self.client.guilds[0].roles, name="Dev")
        bot_member = discord.utils.get(self.client.get_all_members(), name="Doug Bot")
        if platform.node().lower() == "secureerase":
            print("Switching to Prod")
            await bot_member.remove_roles(role)
        else:
            print("Switching to Dev")
            await bot_member.add_roles(role)


async def setup(client: commands.Bot):
    """Run the Setup cog"""
    await client.add_cog(SetupCog(client))
