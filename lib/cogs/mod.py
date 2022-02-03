from datetime import datetime, timedelta
from typing import Optional

from discord import Embed, Member, Forbidden
from discord.ext.commands import Greedy, Cog, command, has_permissions, MissingPermissions, bot_has_permissions


class Mod(Cog):
    log_channel = None

    def __init__(self, bot):
        self.bot = bot

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_members(self, ctx, targets: Greedy[Member], *, reason: str = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")
        else:
            print('recognized')
            if self.log_channel:
                for user in targets:
                    if ctx.guild.me.top_role.position > user.top_role.position \
                            and not user.guild_permissions.administrator:

                        embed = Embed(title="User kicked",
                                      colour=0xDD2222,
                                      timestamp=datetime.utcnow())

                        embed.set_thumbnail(url=user.avatar_url)
                        fields = [("Member", f"{user.name} aka. {user.display_name}", False),
                                  ("Action by", ctx.author.display_name, False),
                                  ("Reason", reason, False)]

                        for name, value, inline in fields:
                            embed.add_field(name=name, value=value, inline=inline)
                        try:
                            await user.send(embed=embed)
                            await user.send('Now u need some milk!')
                        except Forbidden:
                            print('Embed not sendable.')

                        await self.log_channel.send(embed=embed)
                        await user.kick(reason=reason)
                    else:
                        await ctx.send(f'{user.mention} could not be kicked due to higher or administrative roles')
                        await user.send(f'{ctx.author.mention} tried to kick you.')
                await ctx.send('Action completed.')

    @kick_members.error
    async def kick_member_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Missing permissions to perform the task.')
        else:
            await ctx.send("This shouldn't happen.")

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_members(self, ctx, targets: Greedy[Member], *, reason: str = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")
        else:
            if self.log_channel:
                for user in targets:
                    if ctx.guild.me.top_role.position > user.top_role.position \
                            and not user.guild_permissions.administrator:

                        embed = Embed(title="User was banned to the doom.",
                                      colour=0xDD2222,
                                      timestamp=datetime.utcnow())

                        embed.set_thumbnail(url=user.avatar_url)
                        fields = [("Member", f"{user.name} aka. {user.display_name}", False),
                                  ("Action by", ctx.author.display_name, False),
                                  ("Reason", reason, False)]

                        for name, value, inline in fields:
                            embed.add_field(name=name, value=value, inline=inline)

                        try:
                            await user.send(embed=embed)
                            await user.send('Now u need some milk!')
                        except Forbidden:
                            print('Embed not sendable.')

                        await self.log_channel.send(embed=embed)
                        await user.ban(reason=reason)

                    else:
                        await ctx.send(f'{user.mention} could not be kicked due to higher or administrative roles')
                        await user.send(f'{ctx.author.mention} tried to kick you.')
                await ctx.send('Action successful.')

    @ban_members.error
    async def ban_member_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Missing permissions to perform the task.')
        else:
            await ctx.send("This shouldn't happen.")\


    @command(name="clear", aliases=["purge"])
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 5):
        print(f'{limit=}\n{targets=}')
        def _check(message):
            # if no targets True | else list of authors
            return not len(targets) or message.author in targets
        if 0 < limit <= 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14),
                                                  check=_check)

                await ctx.send(f"Deleted messages {len(deleted)}.", delete_after=5)

        else:
            await ctx.send("The limit provided is not within acceptable bounds.")


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(938469827272663090)
            self.bot.cogs_ready.ready_up('mod')


def setup(bot):
    bot.add_cog(Mod(bot))
