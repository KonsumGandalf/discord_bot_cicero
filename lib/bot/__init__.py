import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed
from discord import Intents
from discord.ext.commands import Bot as BotBase

PREFIX = '!'
OWNER_IDS = [263363960764497931]
GUILD_IDS = 810428719796977704
CHANNEL_IDS = 935848953885368340
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class CiceroBot(BotBase):
    VERSION: str | int
    TOKEN: any

    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def run(self, version='0.0.0'):
        self.VERSION = version
        with open(os.path.join(__location__, 'token.txt'), 'r', encoding='utf-8') as tokenFile:
            self.TOKEN = tokenFile.read()

        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print('connceted')

    async def on_disconnect(self):
        print('disconnceted')

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(GUILD_IDS)
            print('ready_to_read')

            channel = self.get_channel(CHANNEL_IDS)
            await channel.send('Now online!')

            embed = Embed(title='Now online', description='Cicero is willed to help you.')
            fields = [('Name', 'Value', True),
                      ('Another field', 'This is the value', False)]
            for name, value, inline_val in fields:
                embed.add_field(name=name, value=value, inline=inline_val)
            embed.set_author(name='David', icon_url=self.guild.icon_url)
            embed.set_footer(text='This is a footer!')
            await channel.send(embed=embed)
        else:
            print('bot reconnect')

    async def on_message(self, message):
        print('Message: ', message)


bot = CiceroBot()
