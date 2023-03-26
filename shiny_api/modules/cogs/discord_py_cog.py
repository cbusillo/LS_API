"""discord Python cog"""
import os
import sys
from subprocess import Popen, PIPE
import discord
from discord.ext import commands


class DiscordPyCog(commands.Cog):
    """Run Python from Discord"""

    def __init__(self, client: commands.Cog):
        self.client = client

    @commands.Cog.listener("on_message")
    async def python_listener(self, message: discord.Message):
        await self.post_python(message)

    @commands.Cog.listener("on_message_edit")
    async def python_listener_edit(self, _before_message: discord.Message, after_message: discord.Message):
        print("Update")
        await self.post_python(after_message)

    async def post_python(self, message: discord.Message):
        if not any("Shiny" in role.name for role in message.author.roles):
            return
        print(os.getcwd())
        if message.author == self.client.user:
            return
        if '```py\nrun' not in message.content:
            return

        code_result, code_error = await self.run_python(message)

        await message.channel.send(f"Results:\n {code_result}")
        if code_error:
            await message.channel.send(f"Errors:\n {code_error}")

    async def run_python(self, message: discord.Message) -> tuple:
        """Run python code"""
        if message.attachments:
            message_code = await message.attachments[0].read()
        else:
            message_code = message.content.split('```py\nrun')[1].split('```')[0]
            message_code = bytes(message_code, encoding="utf8")

        popen = Popen([sys.executable, '-'], stderr=PIPE, stdout=PIPE, stdin=PIPE, cwd=os.getcwd())
        code_result, code_error = popen.communicate(message_code)
        code_result = code_result.decode("utf8")
        code_error = code_error.decode("utf8")
        return code_result, code_error


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(DiscordPyCog(client))
