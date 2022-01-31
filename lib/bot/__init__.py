import os
from glob import glob
from asyncio import sleep

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from discord import Embed, File, Intents
from discord.ext.commands import Bot as BotBase, Context
from discord.ext.commands import CommandNotFound

from ..db import db

PREFIX = '!'
OWNER_IDS = [263363960764497931]
GUILD_IDS = 810428719796977704
CHANNEL_IDS = 935848953885368340
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

COGS = [path.split('\\')[-1][:-3] for path in glob('lib/cogs/*.py')]
# split: 'lib/cogs\\fun.py' => 'fun.py'
# [-1][:-3]: 'fun.py' => fun

class Ready(object):
    """
    Python docs:
    setattr(x, 'foobar', 123) is equivalent to x.foobar = 123.
    """

    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)
            # sets all cogs to not ready

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'cog: {cog} ready')

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class CiceroBot(BotBase):
    VERSION: str | int
    TOKEN: any
    channel: any

    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler(timezone='Europe/Berlin')

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f'lib.cogs.{cog}')
            print(f'{cog} cog loaded')

    def run(self, version='0.0.0'):
        self.VERSION = version

        self.setup()

        with open(os.path.join(__location__, 'token.txt'), 'r', encoding='utf-8') as tokenFile:
            self.TOKEN = tokenFile.read()

        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send('Wait cooldown 10 seconds')


    async def on_connect(self):
        print('connected')

    async def on_disconnect(self):
        print('disconnected')

    async def on_error(self, event_method, *args, **kwargs):
        if event_method == 'on_command_error':
            error_channel = args[0]
            await error_channel.send('Something went wrong.')
        await self.channel.send('General Error occurred')
        raise

    async def on_command_error(self, context, exception):
        if isinstance(context, CommandNotFound):
            pass
        elif hasattr(exception, 'original'):
            raise exception.original

        else:
            raise exception

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(GUILD_IDS)
            self.channel = self.get_channel(CHANNEL_IDS)
            self.scheduler.add_job(self.send_message, 'cron',  day_of_week="mon-fri", hour='10', second='0,10,20,30')
            self.scheduler.start()
            print('__init__ on ready')


            """embed = Embed(title='Now online', description='Cicero is willed to help you.')
            fields = [('Name', 'Value', True),
                      ('Another field', 'This is the value', False)]
            for name, value, inline_val in fields:
                embed.add_field(name=name, value=value, inline=inline_val)
            embed.set_author(name='David', icon_url=self.guild.icon_url)
            embed.set_footer(text='This is a footer!')
            await channel.send(embed=embed)

            await channel.send(files=[File('./data/images/gold.png')])"""
            while not self.cogs_ready.all_ready():
                print('wait')
                await sleep(0.5)

            await self.channel.send('Now online!')
            self.ready = True
        else:
            print('bot reconnect')

    async def on_message(self, message):
        if message.author.bot:
            pass
        elif not message.author.bot:
            await self.process_commands(message)

    async def battle_reminder(self):
        await self.channel.send('Remember to add your battle statistics')

    async def send_message(self):
        await self.channel.send('timed_send: okay lets go baby baby')

bot = CiceroBot()
