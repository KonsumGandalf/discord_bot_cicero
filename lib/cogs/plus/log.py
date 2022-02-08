from datetime import datetime
from inspect import currentframe, getframeinfo

from discord import Embed, Message
from discord.ext.commands import Cog, BucketType, command, cooldown, has_permissions

from lib.cogs.channel import NoChannelError
from lib.db import db

frameinfo = getframeinfo(currentframe())


# from os.path import basename basename(__file__)


class Log(Cog):
    def __init__(self, bot):
        self.bot = bot
        """
        self.bot.get_channel(938382234136764436) not possible here -> result: NoneType
        """

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('log')

    @command(name='deploy_logger')
    @has_permissions(manage_guild=True)
    @cooldown(rate=3, per=60, type=BucketType.user)
    async def deploy(self, ctx):
        db.execute("UPDATE Guilds SET LogChannelID = ? WHERE GuildID = ?", ctx.channel.id, ctx.guild.id)
        channel = ctx
        await channel.send('logger was deployed')

    @Cog.listener()
    async def on_user_update(self, before, after):
        channel = self.bot.cicero_get_channel(before, "LogChannelID")
        if before.display_name != after.display_name:
            embed = Embed(title='Member update',
                          description='Nickname change',
                          colour=channel.guild.get_member(after.id).colour,
                          timestamp=datetime.utcnow())

            fields = [('Before', before.display_name, False),
                      ('After', after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(title='Member update',
                          description='Avatar change:\n-right: old\n-left:new',
                          colour=channel.guild.get_member(after.id).colour,
                          timestamp=datetime.utcnow())

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.cicero_get_channel(before, "LogChannelID")
        if before.display_name != after.display_name:
            embed = Embed(title='Member update',
                          description='Nickname change',
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            fields = [('Before', before.display_name, False),
                      ('After', after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await channel.send(embed=embed)

        if before.roles != after.roles and len(before.roles) > 1:
            embed = Embed(title='Member update',
                          description='Role update',
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            fields = [('Before', " ,".join([r.mention for r in before.roles if 'everyone' not in str(r)]), False),
                      ('After', " ,".join([r.mention for r in after.roles if 'everyone' not in str(r)]), False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        channel = self.bot.cicero_get_channel(before, "LogChannelID")
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(title='Message edit',
                              author=after.author,
                              colour=after.author.colour,
                              timestamp=datetime.utcnow())

                fields = [('Previous Message', before.content, False),
                          ('Edited Message', after.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.cicero_get_channel(message, "LogChannelID")
        if not message.author.bot:
            print('reacted to: ', message)
            embed = Embed(title='Message deleted:',
                          description=f'by {message.author}',
                          colour=message.author.colour,
                          timestamp=datetime.utcnow())

            embed.add_field(name='Content', value=message.content, inline=False)

            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Log(bot))
