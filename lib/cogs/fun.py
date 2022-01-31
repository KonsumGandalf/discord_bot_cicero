from discord.ext.commands import Cog
# from discord.ext.commands import Bot
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

