"""discord Python cog"""
import os
import sys
from subprocess import Popen, PIPE
import discord
from discord.ext import commands
from shiny_api.modules.discord_bot import wrap_reply_lines


class DiscordPyCog(commands.Cog):
    """Run Python from Discord"""

    def __init__(self, client: discord.Client):
        self.client = client

    @commands.Cog.listener("on_message")
    async def python_listener(self, message: discord.Message):
        await self.post_python(message)

    @commands.Cog.listener("on_message_edit")
    async def python_listener_edit(self, _before_message: discord.Message, after_message: discord.Message):
        await self.post_python(after_message)

    async def post_python(self, message: discord.Message):
        # if not any("Shiny" == role.name for role in message.author.roles) and message.author != self.client.user:
        #     return
        # if message.author == self.client.user:
        #     return
        if '```py\nrun' not in message.content:
            return

        code_result, code_error = await self.run_python(message)

        await wrap_reply_lines(f"Results:\n {code_result}", message=message)
        if code_error:
            await wrap_reply_lines(f"Errors:\n {code_error}", message=message)

    async def run_python(self, message: discord.Message) -> tuple:
        """Run python code"""
        if message.attachments:
            message_code = str(await message.attachments[0].read())
        else:
            message_code = message.content.split('```py\nrun')[1].split('```')[0]

        keywords = ['.secret_client.json', '.secret.json', 'exec(', 'eval(', 'open(', 'os.', 'sys.', '.load_config', 'subprocess.']

        if "Shiny" in [role.name for role in message.author.roles]:
            keywords = []
        if any("Shiny" in [role.name for role in mention.roles] for mention in message.mentions):
            keywords = []

        for word in keywords:
            message_code = message_code.replace(word, '***')

        popen = Popen(['gtimeout', '15', sys.executable, '-'], stderr=PIPE, stdout=PIPE, stdin=PIPE, cwd=os.getcwd())
        code_result, code_error = popen.communicate(bytes(message_code, encoding="utf-8"))
        code_result = code_result.decode("utf8")
        code_error = code_error.decode("utf8")
        return code_result, code_error


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(DiscordPyCog(client))
