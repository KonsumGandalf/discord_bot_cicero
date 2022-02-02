from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog, BucketType, command, cooldown


class Log(Cog):
    channel = None

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
    @cooldown(rate=3, per=60, type=BucketType.user)
    async def deploy(self, ctx):
        print(123)
        self.channel = ctx
        await self.channel.send('logger was deployed')

    @Cog.listener()
    async def on_user_update(self, before, after):
        if self.channel:
            if before.display_name != after.display_name:
                embed = Embed(title='Member update',
                              description='Nickname change',
                              colour=self.channel.guild.get_member(after.id).colour,
                              timestamp=datetime.utcnow())

                fields = [('Before', before.display_name, False),
                          ('After', after.display_name, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.channel.send(embed=embed)

            if before.avatar_url != after.avatar_url:
                embed = Embed(title='Member update',
                              description='Avatar change:\n-right: old\n-left:new',
                              colour=self.channel.guild.get_member(after.id).colour,
                              timestamp=datetime.utcnow())

                embed.set_thumbnail(url=before.avatar_url)
                embed.set_image(url=after.avatar_url)

                await self.channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if self.channel:
            if before.display_name != after.display_name:
                embed = Embed(title='Member update',
                              description='Nickname change',
                              colour=after.colour,
                              timestamp=datetime.utcnow())

                fields = [('Before', before.content, False),
                          ('After', after.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.channel.send(embed=embed)

            if before.roles != after.roles:
                embed = Embed(title='Member update',
                              description='Role update',
                              colour=after.colour,
                              timestamp=datetime.utcnow())

                print(before.roles)
                fields = [('Before', " ,".join([r.mention for r in before.roles if 'everyone' not in str(r)]), False),
                          ('After', " ,".join([r.mention for r in after.roles if 'everyone' not in str(r)]), False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if self.channel:
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

                    await self.channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        if self.channel:
            if not message.author.bot:
                embed = Embed(title='Message deleted:',
                              description=f'by {message.author}',
                              colour=message.author.colour,
                              timestamp=datetime.utcnow())

                embed.add_field(name='Content', value=message.content, inline=False)

                await self.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Log(bot))