import os
from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed, Intents, DMChannel
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase, Context, when_mentioned_or
from discord.ext.commands.errors import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown

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
IGNORE_EXCEPTION = [BadArgument, CommandNotFound]


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM Guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


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
        self.ready = False
        self.guild = None
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler(timezone='Europe/Berlin')

        db.autosave(self.scheduler)
        # bot and message obj automatically passed
        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )
        print(123)
        print(get_prefix)

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
            if not self.ready:
                await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

            else:
                await self.invoke(ctx)

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
        if isinstance(exception, CommandNotFound):
            await context.send('Command not found - enter "!help" for more instructions')
        elif hasattr(exception, 'original'):
            raise exception.original
        elif isinstance(exception, CommandOnCooldown):
            await context.send(
                f'Command {str(exception.cooldown.type).split(".")[-1]}on cooldown wait for {exception.retry_after:,.0f} seconds to limit spamming.')
        elif isinstance(exception, HTTPException):
            await context.send('Unable to send message.')
        elif isinstance(exception, BadArgument):
            await context.send('Wrong Argument is passes.')
        elif isinstance(exception, Forbidden):
            await context.send('I have no permission to execute this command.')
        elif isinstance(exception, MissingRequiredArgument):
            await context.send('At least one required argument is missing.')
        else:
            raise exception

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(GUILD_IDS)
            self.channel = self.get_channel(CHANNEL_IDS)
            self.scheduler.add_job(self.send_message, 'cron', day_of_week="mon-fri", hour='10', second='0,10,20,30')
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

            # await self.channel.send('Now online!')
            self.ready = True
        else:
            print('bot reconnect')

    async def on_message(self, message):
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                if len(message.content) < 10:
                    await message.channel.send("Please provide information longer than 10 chars.")
                else:
                    embed = Embed(title="Modmail ",
                                  colour=0x82ec0c,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=message.author.avatar_url)

                    fields = [("Member", message.author.display_name, False),
                              ("Message", message.content, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)
                    # https://youtu.be/72dXuNmqbzM?t=391
                    mod = self.get_cog('Mod')  # Mod not mod due to the class name not the file name
                    await mod.log_channel.send(embed=embed)  # ctx
                    await message.channel.send('Message forwarded to mod channel')
            else:
                await self.process_commands(message)

    async def battle_reminder(self):
        await self.channel.send('Remember to add your battle statistics')

    async def send_message(self):
        await self.channel.send('timed_send: okay lets go baby baby')


bot = CiceroBot()
