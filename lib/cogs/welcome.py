from discord.ext.commands import Cog, command
from discord.errors import Forbidden
from random import choice

from ..db import db

class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(938197415851331695)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun')
        # await self.bot.channel.send('Cog listener added')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('welcome')

    @Cog.listener()
    async def on_member_join(self, member):
        print(member)
        db.execute("INSERT INTO Elo (UserID) VALUES (?)", member.id)
        await self.bot.get_channel(938197415851331695).send(f'{choice(["Welcome","Hello there", "Ave", "Greetings"])} '
                                f'**{member.guild.name}** {member.mention} !')
        try:
            await member.send('Headphones!')
        except Forbidden:
            pass
        await member.add_roles(member.guild.get_role(938199531957387265))


    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute(f"DELETE FROM Elo WHERE UserID = (?)", member.id)
        await self.bot.get_channel(938222644912873542).send(f'The grand {member.mention}  '
                                f'{choice(["Fucks off","leaves ", "buggers off"])} from **{member.guild.name}** !')


def setup(bot):
    bot.add_cog(Welcome(bot))
    # bot.scheduler.add_job(...)