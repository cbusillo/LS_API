"""Allow interaction with ChatGPT from Discord"""
import platform
import discord
from discord.ext import commands
import openai
import shiny_api.modules.load_config as config
from shiny_api.modules.discord_bot import wrap_lines


class ChatGPTCog(commands.Cog):
    """Class to interact with ChatGPT"""

    def __init__(self, client: discord.Client):
        self.client = client
        self.user_threads = {}

    @commands.Cog.listener("on_message")
    async def chatgpt_listener(self, message: discord.Message):
        """if text starts with image, get an image from WALL-E"""
        await self.check_user_and_send(message)

    @commands.Cog.listener("on_message_edit")
    async def chatgpt_listener(self, _before_message: discord.Message, after_message: discord.Message):
        """if text starts with image, get an image from WALL-E"""
        await self.check_user_and_send(after_message)

    async def check_user_and_send(self, message: discord.Message):
        if message.author == self.client.user:
            return

        roles = self.client.guilds[0].me.roles
        if any("Dev" in role.name for role in roles):
            if "imagingserver" in platform.node().lower():
                return
        elif "imagingserver" not in platform.node().lower():
            return

        if self.client.user.mentioned_in(message) or not message.guild:
            await self.generate_prompt(message)

    async def generate_prompt(self, message: discord.Message):
        """Generage prompt from message and thread"""
        run_code = False
        prompt = message.content
        while self.client.user.mention in prompt:
            prompt = prompt.replace(self.client.user.mention, "").strip()

        if prompt.split()[0].lower() == "image" and len(prompt.split()) > 2:
            prompt = " ".join(prompt.split()[1:]).strip()
            async with message.channel.typing():
                await self.get_walle_image(message=message, prompt=prompt)

        elif prompt.split()[0:2] == ["py", "run"] and len(prompt.split()) > 3:
            run_code = True
            prompt = "I want you to generate python code to " + " ".join(prompt.split()[2:]).strip(
            ) + ".  Return python code only.  Do not return any explanatory text.  Do not respond with anything except the code."

        elif prompt.split()[0:2] == ["py", "generate"] and len(prompt.split()) > 3:
            run_code = False
            prompt = "I want you to generate python code to " + " ".join(prompt.split()[2:]).strip(
            ) + ".  Return python code only.  Do not return any explanatory text.  Do not respond with anything except the code."

        elif prompt.split()[0:2] == ["py", "explain"] and len(prompt.split()) > 3:
            run_code = False
            prompt = "I want you to generate python code to " + " ".join(prompt.split()[2:]).strip()

        if message.attachments and run_code is False:
            prompt = prompt + (await message.attachments[0].read()).decode("utf-8")
        if message.author.id not in self.user_threads:
            self.user_threads[message.author.id] = []
        if message.reference and message.reference.resolved.author.id == self.client.user.id:
            self.user_threads[message.author.id].append(prompt)
        else:
            self.user_threads[message.author.id] = [prompt]

        async with message.channel.typing():
            ai_response = await self.get_chatgpt_message(message=message)
            if run_code:
                ai_response = ai_response.replace("```python", "").replace("```py", "").replace("```", "").replace("`", "")
                ai_response = f'```py\nrun\n{ai_response}\n```'
            await wrap_lines(ai_response, message=message)

    async def get_walle_image(self, message: discord.Message, prompt: str):
        """Send message prompt to walle and display image"""
        print(f"Sending message: {prompt} to WALL-E")
        try:
            response = await openai.Image.acreate(
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url",
                api_key=config.OPENAI_API_KEY
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
            chat_messages = [{"role": "user", "content": each_prompt}
                             for each_prompt in self.user_threads[message.author.id]]
            # self.user_threads[message.author.id]
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=chat_messages,
                api_key=config.OPENAI_API_KEY,
            )
        except openai.error.InvalidRequestError as exception:
            await message.channel.send(str(exception))
            return
        except openai.error.RateLimitError as exception:
            await message.channel.send(str(exception))
            return
        print(f"Received response: {response['choices'][0]['message']['content']}")
        return response["choices"][0]["message"]["content"]


async def setup(client: commands.Cog):
    """Add cog"""
    await client.add_cog(ChatGPTCog(client))
