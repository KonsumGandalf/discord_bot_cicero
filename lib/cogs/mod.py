from datetime import datetime, timedelta
from typing import Optional
from asyncio import sleep

from discord import Embed, Member, Forbidden
from discord.ext.commands import Greedy, Cog, command,\
    CheckFailure, has_permissions, MissingPermissions, bot_has_permissions

from ..db import db

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

    async def mute_members(self, message, targets, hours, reason):
        unmutes = []

        for target in targets:
            if not self.muted_role in target.roles:
                if message.guild.me.top_role.position > target.top_role.position:
                    role_ids = ",".join([str(r.id) for r in target.roles])
                    end_time = datetime.utcnow() + timedelta(seconds=hours) if hours else None

                    db.execute("INSERT INTO mutes VALUES (?, ?, ?)",
                               target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

                    await target.edit(roles=[self.muted_role])

                    embed = Embed(title="Member muted",
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", target.display_name, False),
                              ("Actioned by", message.author.display_name, False),
                              ("Duration", f"{hours:,} hour(s)" if hours else "Indefinite", False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                    if hours:
                        unmutes.append(target)

        return unmutes

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute_command(self, ctx, targets: Greedy[Member], time_in_seconds: Optional[int], *,
                           reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            unmutes = await self.mute_members(ctx.message, targets, time_in_seconds, reason)
            await ctx.send("Action ended.")

            if len(unmutes):
                await sleep(time_in_seconds)
                await self.unmute_members(ctx.guild, targets)

    @mute_command.error
    async def mute_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send('Missing permissions to perform the task.')
        else:
            await ctx.send("This shouldn't happen.")

    async def unmute(self, ctx, targets, reason="Mute time expired."):
        for target in targets:
            if self.muted_role in target.roles:
                role_ids = db.field("SELECT RoleIDS FROM mutes WHERE UserID = ?", target.id)
                roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
                print(roles)

                db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

                await target.edit(roles=roles)

                embed = Embed(title="Member unmuted",
                              colour=0xDD2222,
                              timestamp=datetime.utcnow())

                embed.set_thumbnail(url=target.avatar_url)

                fields = [("Member", target.display_name, False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)

    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def unmute_members(self, ctx, targets: Greedy[Member], time_in_seconds: Optional[int], *,
                           reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            await self.unmute(ctx, targets, reason=reason)


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(
                db.field('SELECT ModChannelID FROM Guilds WHERE GuildID= (?)', self.bot.guild.id))
            self.muted_role = self.bot.guild.get_role(938902664102678529)
            self.bot.cogs_ready.ready_up('mod')


def setup(bot):
    bot.add_cog(Mod(bot))
