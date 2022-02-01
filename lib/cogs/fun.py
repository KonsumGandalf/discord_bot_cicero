import sqlite3
from random import choice

from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, command, BadArgument, BucketType, cooldown

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
        await conn.send('deine mum')


    @cooldown(rate=2, per=10, type=BucketType.guild)
    @command(name="fight", alias=['battle'])
    async def fight(self, ctx: sqlite3.dbapi2, fighter2: Member, *, reason: str = 'No blood'):
        """
        This is methode creates a battle request between two fighters and has to be accepted
        :param ctx: you - fight requester
        :param fighter2: user to battle against
        :param reason: reason you want to battle f.e. honor, elo
        :return:
        """
        await ctx.send(f'{ctx.author.display_name} wants to fight or die against {fighter2.mention}\n'
                       f'Reason: {reason}')

    @fight.error
    async def fight_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send('Too fast blood.')
        else:
            await ctx.send('unknown error occurred')

    """
    @command
    :name & alias calling name
    @cooldown
    :rate - number of commands to be used
    :per - time for cooldown
    """
    @command(name="animals", alias=['animal_list', 'animal'])
    @cooldown(rate=1, per=10, type=BucketType.user)
    async def animal(self, ctx, animal: str):
        if (animal := animal.lower()) in ('dog', 'cat', 'fox', 'bird', 'koala', 'panda'):
            text_url = f'https://some-random-api.ml/facts/{animal}'
            image_url = f'https://some-random-api.ml/img/{animal}'
            print(image_url)
            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]
                    print(f'{image_link=}')

                else:
                    image_link = None
                    print(f'{image_link=}')

            async with request("GET", text_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f"{animal} fact",
                                  description=data["fact"],
                                  colour=ctx.author.colour)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)

                else:
                    await ctx.send(f"API returned a {response.status} status.")

        else:
            await ctx.send("Unknown animal species.")

    """    @animal.error()
    async def fight_error(self, ctx, exc):
        pass
    """
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun')
        # await self.bot.channel.send('Cog listener added')

    @Cog.listener()
    async def on_message(self, message):
        print('cog load on_message ', message)


def setup(bot):
    bot.add_cog(Fun(bot))
    # bot.scheduler.add_job(...)
