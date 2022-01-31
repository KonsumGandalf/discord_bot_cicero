from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Member

from random import choice

import sqlite3

from setuptools.command.alias import alias

"""
Cog documentation:
https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html

Every command is marked with: commands.command() decorator.
Every listener is marked with: commands.Cog.listener() decorator.
Cogs are then registered with: Bot.add_cog() call.
Cogs are subsequently removed with: Bot.remove_cog() call.


"""


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Context:
     https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=context#discord.ext.commands.Context
     
    args
    author
    bot
    channel
    cog
    command
    command_failed
    guild
    invoked_parents
    invoked_subcommand
    invoked_with
    kwargs
    me
    message
    prefix
    subcommand_passed
    valid
    voice_client
    """

    @command(name="info", aliases=['work'])
    async def info(self, conn: sqlite3.dbapi2):
        await conn.send(f'{choice(["hello", "whats up?", "this is my win"])}'
                        f'I am made by @{choice(list(self.bot.get_all_members()))}')

    @command(name="multiply")
    async def multiply(self, conn: sqlite3.dbapi2, cal_str: str):
        await conn.send()

    @command(name="fight", alias=['battle'])
    async def fight(self, conn: sqlite3.dbapi2, fighter1: Member, fighter2: Member, *, reason: str = 'No blood'):
        await conn.send(f'{conn.author.display_name} says that '
                        f'{fighter1.mention} has to fight or die against {fighter2.mention}\n'
                        f'Reason: {reason}')


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun')
        await self.bot.channel.send('Cog listener added')

    @Cog.listener()
    async def on_message(self, message):
        print('cog load on_message ', message)



def setup(bot):
    bot.add_cog(Fun(bot))
    # bot.scheduler.add_job(...)

