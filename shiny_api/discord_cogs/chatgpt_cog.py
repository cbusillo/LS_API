"""Allow interaction with ChatGPT from Discord"""
import platform
import discord
from discord.ext import commands
from openai import Image, openai_object, error, ChatCompletion
from shiny_api.modules.load_config import Config
from shiny_api.modules.discord_bot import wrap_reply_lines


class ChatGPTCog(commands.Cog):
    """Class to interact with ChatGPT"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_threads = {}
        self.prompt_dict = {
            "run": "I want you to generate python code to {prompt}.  Return python code only.  "
            "Do not return any explanatory text.  Do not respond with anything except the code.",
            "generate": "I want you to generate python code to {prompt}.  Return python code only."
            "Do not return any explanatory text.  Do not respond with anything except the code.",
            "explain": "I want you to generate python code to {prompt}"
        }
        self.keywords_dict = {
            "macos": "macOS is the bestOS.  Fight me!",
            " ios ": "iOS is the bestOS.  Wanna get banned?",
            "linux os": "Linux is ok, macOS is better"
        }

    @commands.Cog.listener("on_message")
    async def keyword_listener(self, message: discord.Message):
        """Listen for keywords and respond"""
        if message.author == self.bot.user:
            return
        for keyword in self.keywords_dict:
            if keyword in f" {message.clean_content.lower()} ":
                await message.channel.send(self.keywords_dict.get(keyword))

    @commands.Cog.listener("on_message")
    async def chatgpt_listener(self, message: discord.Message):
        """On new message, check user and send to ChatGPT"""
        if await self.check_user(message) is True:
            await self.generate_prompt(message)

    @commands.Cog.listener("on_message_edit")
    async def chatgpt_listener_edit(self, _before_message: discord.Message, after_message: discord.Message):
        """On message edit, check user and sent to ChatGPT"""
        if await self.check_user(after_message) is True:
            await self.generate_prompt(after_message)

    async def check_user(self, message: discord.Message) -> bool:
        """Return True if we want to send to ChatGPT"""
        if message.author == self.bot.user:
            return False

        roles = self.bot.guilds[0].me.roles
        if any("Dev" in role.name for role in roles):
            if "imagingserver" in platform.node().lower():
                return False
        elif "imagingserver" not in platform.node().lower():
            return False

        if isinstance(self.bot.user, discord.ClientUser) and self.bot.user.mentioned_in(message):
            return True
        if message.guild is None:
            return True
        return False

    async def generate_prompt(self, message: discord.Message):
        """Generage prompt from message and thread"""
        run_code = False
        prompt = message.content
        if self.bot.user is None:
            return

        while self.bot.user.mention in prompt:
            prompt = prompt.replace(self.bot.user.mention, "").strip()

        prompt_list = [each.lower() for each in prompt.split()[:3]]

        if prompt_list[0] == "image" and len(prompt_list) > 1:
            prompt = " ".join(prompt.split()[1:]).strip()
            async with message.channel.typing():
                await self.get_walle_image(message=message, prompt=prompt)

        elif prompt_list[0] == "py" and len(prompt_list) > 2:
            prompt_code = " ".join(prompt.split()[2:]).strip()
            prompt = self.prompt_dict.get(prompt_list[1], "").format(prompt=prompt_code)
            if prompt_list[1] == "run":
                run_code = True

        if message.attachments and run_code is False:
            prompt = prompt + (await message.attachments[0].read()).decode("utf-8")
        if message.author.id not in self.user_threads:
            self.user_threads[message.author.id] = []
        if (message.reference and
                isinstance(message.reference.resolved, discord.Message) and
                isinstance(message.reference.resolved.author, discord.Member) and
                message.reference.resolved.author.id == self.bot.user.id):
            self.user_threads[message.author.id].append(prompt)
        else:
            self.user_threads[message.author.id] = [prompt]

        async with message.channel.typing():
            ai_response: str = await self.get_chatgpt_message(message=message)
            if run_code:
                ai_response = ai_response.replace("```python", "").replace("```py", "").replace("```", "").replace("`", "")
                ai_response = f'```py\nrun\n{ai_response}\n```'

            await wrap_reply_lines(ai_response, message=message)

    async def get_walle_image(self, message: discord.Message, prompt: str) -> None:
        """Send message prompt to walle and display image"""
        print(f"Sending message: {prompt} to WALL-E")
        try:
            response = await Image.acreate(
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url",
                api_key=Config.OPENAI_API_KEY
            )
        except error.InvalidRequestError as exception:
            await message.channel.send(str(exception))
            return
        except error.RateLimitError as exception:
            await message.channel.send(str(exception))
            return
        if not isinstance(response, openai_object.OpenAIObject):
            return
        image_url = response["data"][0]["url"]

        embed = discord.Embed()
        embed.set_image(url=image_url)

        # Send the message
        await message.channel.send(embed=embed)

    async def get_chatgpt_message(self, message: discord.Message) -> str:
        """Send message prompt to chatgpt and send text"""
        print(f"Sending message: {str(self.user_threads[message.author.id]).strip()}")
        try:
            chat_messages = [{"role": "user", "content": each_prompt}
                             for each_prompt in self.user_threads[message.author.id]]
            # self.user_threads[message.author.id]
            response = await ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=chat_messages,
                api_key=Config.OPENAI_API_KEY,
                temperature=0.5,
            )
        except error.InvalidRequestError as exception:
            await message.channel.send(str(exception))
            return ""
        except error.RateLimitError as exception:
            await message.channel.send(str(exception))
            return ""
        if not isinstance(response, openai_object.OpenAIObject):
            return ""
        text_response = response['choices'][0]['message']['content']
        print(f"Received response: {text_response}")
        return text_response


async def setup(client: commands.Bot):
    """Add cog"""
    await client.add_cog(ChatGPTCog(client))
