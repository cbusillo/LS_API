"""Allow interaction with ChatGPT from Discord"""
import os
import platform
import textwrap
import discord
from discord.ext import commands
import openai
import shiny_api.modules.load_config as config


print(f"Importing {os.path.basename(__file__)}...")


class ChatGPTCog(commands.Cog):
    """Class to interact with ChatGPT"""

    def __init__(self, client: commands.Cog):
        self.client = client
        self.user_threads = {}

    @commands.Cog.listener("on_message")
    async def chatgpt_listener(self, message: discord.Message):
        """if text starts with image, get an image from WALL-E"""
        if message.author == self.client.user:
            return

        roles = self.client.guilds[0].me.roles
        if any("Dev" in role.name for role in roles):
            if "secureerase" in platform.node().lower():
                return
        elif "secureerase" not in platform.node().lower():
            return

        if self.client.user.mentioned_in(message) or not message.guild:
            await self.generage_prompt(message)

    async def generage_prompt(self, message: discord.Message):
        """Generage prompt from message and thread"""
        prompt = message.content
        while self.client.user.mention in prompt:
            prompt = prompt.replace(self.client.user.mention, "").strip()

        if prompt.split()[0].lower() == "image" and len(prompt.split()) > 2:
            prompt = " ".join(prompt.split()[1:]).strip()
            async with message.channel.typing():
                await self.get_walle_image(message=message, prompt=prompt)
        if message.author.id not in self.user_threads:
            self.user_threads[message.author.id] = ""
        if message.reference and message.reference.resolved.author.id == self.client.user.id:
            self.user_threads[message.author.id] += f"\n{prompt}"
        else:
            self.user_threads[message.author.id] = prompt

        async with message.channel.typing():
            await self.get_chatgpt_message(message=message)

    async def get_walle_image(self, message: discord.Message, prompt: str):
        """Send message prompt to walle and display image"""
        print(f"Sending message: {prompt} to WALL-E")
        try:
            response = await openai.Image.acreate(
                prompt=prompt, n=1, size="1024x1024", response_format="url", api_key=config.OPENAI_API_KEY
            )
        except openai.error.InvalidRequestError as exception:
            await message.channel.send(str(exception))
            return
        except openai.error.RateLimitError as exception:
            await message.channel.send(str(exception))
            return

        image_url = response["data"][0]["url"]

        embed = discord.Embed()
        embed.set_image(url=image_url)

        # Send the message
        await message.channel.send(embed=embed)

    async def get_chatgpt_message(self, message: discord.Message):
        """Send message prompt to chatgpt and send text"""
        print(f"Sending message: {str(self.user_threads[message.author.id]).strip()}")
        try:
            response = await openai.Completion.acreate(
                engine="text-davinci-003",
                prompt=self.user_threads[message.author.id],
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0,
                top_p=1,
                api_key=config.OPENAI_API_KEY,
            )
        except openai.error.InvalidRequestError as exception:
            await message.channel.send(str(exception))
            return
        except openai.error.RateLimitError as exception:
            await message.channel.send(str(exception))
            return
        await self.wrap_lines(response["choices"][0]["text"], message=message)
        print(f"Received response: {response['choices'][0]['text']}")

    async def wrap_lines(self, lines: list[str], message: discord.Message):
        """Break up messages that are longer than 2000 chars and send multible messages to discord"""
        lines = textwrap.wrap(lines, 2000, break_long_words=False, replace_whitespace=False)
        for line in lines:
            await message.channel.send(line)


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(ChatGPTCog(client))
