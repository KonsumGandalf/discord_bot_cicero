from datetime import datetime, timedelta
from random import randint

from discord.ext.commands import Cog
from discord import Embed

from lib.db import db


class Elo(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel_id_col = "EloChannelID"

    async def process_xp(self, msg):
        elo, lvl, eloTime = db.record("SELECT Elo, Level, EloTime FROM Elo WHERE UserID = ?", msg.author.id)
        if datetime.fromisoformat(eloTime) < datetime.now():
            await self.add_xp(msg, elo, lvl)
        else:
            raise ValueError('Wrong Timestamp')

    async def add_xp(self, msg, elo, lvl):

        print('old', elo, lvl)
        elo_add = randint(10, 20)
        new_lvl = int(((elo + elo_add) // 42) ** 0.55)
        print('new', elo_add, new_lvl, msg.author.id)
        db.execute(
            "UPDATE Elo SET Elo = Elo + ?, Level = ?, EloTime = ? WHERE UserID = ?"
            , elo_add, new_lvl, (datetime.utcnow()+timedelta(seconds=60)).isoformat(), msg.author.id
        )
        if new_lvl > lvl:
            embed = Embed(title='Member rank',
                          description=msg.author.mention,
                          colour=msg.author.colour,
                          timestamp=datetime.utcnow())

            fields = [('Before', f'Level: {lvl} - Elo: {elo}', False),
                      ('After', f'Level: {new_lvl} - Elo: {elo_add}', False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            await self.bot.cicero_get_channel(msg, self.channel_id_col).send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('elo')
        # await self.bot.channel.send('Cog listener added')

    @Cog.listener()
    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_xp(msg)


def setup(bot):
    bot.add_cog(Elo(bot))
