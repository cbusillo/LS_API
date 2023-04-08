"""discord Python cog"""
import os
import sys
from subprocess import Popen, PIPE
import discord
from discord.ext import commands
from shiny_api.modules.discord_bot import wrap_reply_lines


class DiscordPyCog(commands.Cog):
    """Run Python from Discord"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def python_listener(self, message: discord.Message):
        """listen for messages call check for python"""
        await self.post_python(message)

    @commands.Cog.listener("on_message_edit")
    async def python_listener_edit(self, _before_message: discord.Message, after_message: discord.Message):
        """listen for message edits call check for python"""
        await self.post_python(after_message)

    async def post_python(self, message: discord.Message):
        """Check for python code and run"""
        if "```py\nrun" not in message.content:
            return

        code_result, code_error = await self.run_python(message)

        await wrap_reply_lines(f"Results:\n{code_result}", message=message)
        if code_error:
            await wrap_reply_lines(f"Errors:\n{code_error}", message=message)

    async def run_python(self, message: discord.Message) -> tuple:
        """Run python code"""
        if message.attachments:
            message_code = str(await message.attachments[0].read())
        else:
            message_code = message.content.split("```py\nrun")[1].split("```")[0]

        keywords = [
            "secret_client.json",
            "secret.json",
            "exec(",
            "eval(",
            "open(",
            "os.",
            "sys.",
            ".load_config",
            "subprocess.",
            "key",
            "token",
        ]

        is_shiny = False

        if isinstance(message.author, discord.User):
            return "", ""

        if "Shiny" in [role.name for role in message.author.roles]:
            is_shiny = True
        if any(
            "Shiny" in [role.name for role in mention.roles] for mention in message.mentions if isinstance(mention, discord.Member)
        ):
            is_shiny = True

        if any(keyword in message_code.lower() for keyword in keywords) and is_shiny is False:
            return "Contains protected keywords", ""

        popen = Popen(["gtimeout", "15", sys.executable, "-"], stderr=PIPE, stdout=PIPE, stdin=PIPE, cwd=os.getcwd())
        code_result, code_error = popen.communicate(bytes(message_code, encoding="utf-8"))
        return code_result.decode("utf8"), code_error.decode("utf8")


async def setup(bot: commands.Bot):
    """Add cog"""
    await bot.add_cog(DiscordPyCog(bot))
