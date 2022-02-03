from datetime import datetime
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog, BucketType, command, cooldown


class Info(Cog):
    channel = None

    def __init__(self, bot):
        self.bot = bot

    @command(name='userinfo', aliases=['memberinfo', 'ui', 'mi'])
    async def user_info(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        embed = Embed(title="User information",
                      colour=target.colour,
                      timestamp=datetime.utcnow())

        fields = [("ID", target.id, False),
                  ("Name", target.display_name, True),
                  ("Bot?", target.bot, True),
                  ("Top role", target.top_role.mention, True),
                  ("Status", str(target.status).title(), True),
                  ("Activity", f'{target.activity.name}' if target.activity else 'None', True),
                  ("Created at", f'{target.created_at.strftime("%d/%m/%Y %H:%M:%S")}', True),
                  ("Boosted status", bool(target.premium_since), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await self.channel.send(embed=embed)

    @command(name='serverinfo', aliases=['guildinfo', 'si', 'gi'])
    async def server_info(self, ctx):
        embed = Embed(title="Server information",
                      colour=ctx.guild.owner.colour,
                      timestamp=datetime.utcnow())

        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        fields = [("ID", ctx.guild.id, False),
                  ("Owner", ctx.guild.owner, True),
                  ("Region", ctx.guild.region, True),
                  ("Members", len(ctx.guild.members), True),
                  ("Banned members", len(await ctx.guild.bans()), True),
                  ("Statuses of users", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
                  ("Text channels", len(ctx.guild.text_channels), True),
                  ("Voice channels", len(ctx.guild.voice_channels), True),
                  ("Invites", len(await ctx.guild.invites()), True),
                  ("Boosting status", f'Level {ctx.guild.premium_tier}', True),
                  ("Roles", " ,".join(role.mention for role in ctx.guild.roles if 'everyone' not in str(role)), False),
                  ("Categories", " ,".join(str(role) for role in ctx.guild.categories), False)]
        print("\n".join(str(rows) for rows in fields))
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await self.channel.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.channel = self.bot.get_channel(938469827272663090)
            self.bot.cogs_ready.ready_up('info')

def setup(bot):
    bot.add_cog(Info(bot))