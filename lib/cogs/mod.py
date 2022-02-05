from asyncio import sleep
from datetime import datetime, timedelta
from re import search
from typing import Optional

from discord import Embed, Member, Forbidden
from discord.ext.commands import Greedy, Cog, command, \
    CheckFailure, has_permissions, MissingPermissions, bot_has_permissions

from ..db import db


class Mod(Cog):
    log_channel = None
    url_not_allowed = None
    img_not_allowed = None
    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+" \
                r"[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+" \
                r"(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    def __init__(self, bot):
        self.bot = bot

    async def kick_members(self, message, targets, reason):
        for user in targets:
            if message.guild.me.top_role.position > user.top_role.position \
                    and not user.guild_permissions.administrator:

                embed = Embed(title="User kicked",
                              colour=0xDD2222,
                              timestamp=datetime.utcnow())

                embed.set_thumbnail(url=user.avatar_url)
                fields = [("Member", f"{user.name} aka. {user.display_name}", False),
                          ("Action by", message.author.display_name, False),
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
                await self.log_channel.send(f'{user.mention} could not be kicked due to higher or administrative roles')
                await user.send(f'{message.author.mention} tried to kick you.')

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_action(self, ctx, targets: Greedy[Member], *, reason: str = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")
        else:
            await self.kick_members(ctx.message, targets, reason)
            await ctx.send('Action completed.')

    @kick_action.error
    async def kick_member_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Missing permissions to perform the task.')
        else:
            await ctx.send("This shouldn't happen.")

    async def ban_members(self, message, targets, reason):
        for user in targets:
            if message.guild.me.top_role.position > user.top_role.position \
                    and not user.guild_permissions.administrator:

                embed = Embed(title="User was banned to the doom.",
                              colour=0xDD2222,
                              timestamp=datetime.utcnow())

                embed.set_thumbnail(url=user.avatar_url)
                fields = [("Member", f"{user.name} aka. {user.display_name}", False),
                          ("Action by", message.author.display_name, False),
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
                await self.log_channel.send(f'{user.mention} could not be kicked due to higher or administrative roles')
                await user.send(f'{message.author.mention} tried to kick you.')

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_action(self, ctx, targets: Greedy[Member], *, reason: str = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")
        else:
            await self.ban_members(ctx.message, targets, reason)
            await ctx.send('Action successful.')

    @ban_action.error
    async def ban_member_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Missing permissions to perform the task.')
        else:
            await ctx.send("This shouldn't happen.")

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
                deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow() - timedelta(days=14),
                                                  check=_check)

                await ctx.send(f"Deleted messages {len(deleted)}.", delete_after=5)

        else:
            await ctx.send("The limit provided is not within acceptable bounds.")

    async def mute_members(self, message, targets, time_in_sec, reason):
        unmutes = []

        for target in targets:
            if not self.muted_role in target.roles:
                if message.guild.me.top_role.position > target.top_role.position:
                    role_ids = ",".join([str(r.id) for r in target.roles])
                    end_time = datetime.utcnow() + timedelta(seconds=time_in_sec) if time_in_sec else None
                    db.execute("INSERT INTO Mutes VALUES (?, ?, ?)",
                               target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

                    await target.edit(roles=[self.muted_role])

                    embed = Embed(title="Member muted",
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", target.display_name, False),
                              ("Actioned by", message.author.display_name, False),
                              ("Duration", f"{time_in_sec:,} hour(s)" if time_in_sec else "Indefinite", False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                    if time_in_sec:
                        unmutes.append(target)

        return unmutes

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute_action(self, ctx, targets: Greedy[Member], time_in_seconds: Optional[int] = 100, *,
                          reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            unmutes = await self.mute_members(ctx.message, targets, time_in_seconds, reason)
            await ctx.send("Action ended.")

            if len(unmutes):
                await sleep(time_in_seconds)
                await self.unmute_members(ctx.guild, targets)

    @mute_action.error
    async def mute_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send('Missing permissions to perform the task.')
        else:
            await ctx.send("This shouldn't happen.")

    async def unmute_members(self, guild, targets, *, reason="Mute time expired."):
        for target in targets:
            if self.muted_role in target.roles:
                role_ids = db.field("SELECT RoleIDs FROM Mutes WHERE UserID = ?", target.id)
                roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

                db.execute("DELETE FROM Mutes WHERE UserID = ?", target.id)

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
    async def unmute_action(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments is missing.")

        else:
            await self.unmute_members(ctx.guild, targets, reason=reason)

    @unmute_action.error
    async def mute_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send('Missing permissions to perform the task.')
        else:
            await ctx.send("This shouldn't happen.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.url_not_allowed = [int(ele) for ele in
                                    db.field("SELECT NoURLChannelIDs FROM Guilds WHERE GuildID = (?)",
                                             self.bot.guild.id).split(',')]
            self.img_not_allowed = [int(ele) for ele in
                                    db.field("SELECT NoIMGChannelIDs FROM Guilds WHERE GuildID = (?)",
                                             self.bot.guild.id).split(',')]
            self.log_channel = self.bot.get_channel(
                db.field('SELECT ModChannelID FROM Guilds WHERE GuildID= (?)', self.bot.guild.id))
            self.muted_role = self.bot.guild.get_role(938902664102678529)
            self.bot.cogs_ready.ready_up('mod')

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if message.channel.id in self.url_not_allowed and search(self.url_regex, message.content):
                await message.delete()
                await message.channel.send("You can't send links in this channel", delete_after=10)

            elif (message.channel.id in self.img_not_allowed
                  and any([hasattr(a, "width") for a in message.attachments])):
                await message.delete()
                await message.channel.send("You can't send images in this channel", delete_after=10)


def setup(bot):
    bot.add_cog(Mod(bot))
