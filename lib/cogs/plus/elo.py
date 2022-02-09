from datetime import datetime, timedelta
from random import randint
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog, command
from discord.ext.menus import MenuPages, ListPageSource

from lib.db import db


class LeaderBoardMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=3)

    async def write_page(self, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(title="Elo Leaderboard",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.icon_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} members.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page * self.per_page) + 1

        max_len = max([len(self.ctx.bot.guild.get_member(row[0]).display_name) for row in entries])
        fields = []
        table = ("\n".join(
            f"{idx + offset}. {self.ctx.bot.guild.get_member(entry[0]).display_name:<{max_len}}"
            f"(Elo: {entry[1]} | Level: {entry[2]})"
            for idx, entry in enumerate(entries))
        )
        print(table)

        fields.append(("Ranks", table))

        return await self.write_page(offset, fields)



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
        elo_add = randint(10, 20)
        new_lvl = int(((elo + elo_add) // 42) ** 0.55)
        db.execute(
            "UPDATE Elo SET Elo = Elo + ?, Level = ?, EloTime = ? WHERE UserID = ?"
            , elo_add, new_lvl, (datetime.utcnow() + timedelta(seconds=60)).isoformat(), msg.author.id
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
            await self.bot.check

    async def check_lvl_rewards(self, ctx, lvl):
        pass

    @command(name="leaderboard", aliases=['lb'])
    async def display_leaderboard(self, ctx):
        records = db.records("SELECT UserID, Elo, Level FROM Elo ORDER BY Elo DESC")
        menu = MenuPages(source=LeaderBoardMenu(ctx, records),
                         clear_reactions_after=False,
                         timeout=30.0)

        await menu.start(ctx)

    @command(name='level')
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record("SELECT Elo, Level FROM Elo WHERE UserID = ?", target.id)
        await ctx.send(f'The level of {target.mention} is {lvl} with {xp}')

    @command(name='rank')
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM Elo ORDER BY Elo DESC")
        await ctx.send(f'The rank of {target.mention} is {ids.index(target.id) + 1} of {len(ids)}')

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
