from glob import glob
from typing import Optional

import discord
from discord.ext.commands import Cog, has_permissions, command
from discord import CategoryChannel

from ..db import db

PLUS_COGS = [path.split('\\')[-1][:-3] for path in glob('lib/cogs/plus/*.py')]


class CogDescription:
    def __init__(self, sql_repr, goal, description, cmd):
        self.sql_repr: str = sql_repr
        self.goal: str = goal
        self.description: str = description
        self.cmd: str = cmd
        self.more_info = f'!deploy {cmd}'


cog_list = [CogDescription("LogChannelID", "Supports moderation in cases of f.e. racism.",
                           "The assigned channel prints out messages which are edited later or deleted.", 'log'),
            CogDescription('ModChannelID', 'Center of moderation.',
                           'The assigned channel prints out messages which are edited later or deleted.',
                           'mod'),
            CogDescription('NoURLChannelIDs', 'Keeps the server clean.',
                           'The assigned channels ban all URL sent.',
                           'url'),
            CogDescription('NoIMGChannelIDs', 'Keeps the server clean.',
                           'The assigned channels prohibit all sent image like files.',
                           'img'),
            CogDescription('ReactChannelID', ' ',
                           ' ',
                           'react'),
            CogDescription('EloChannelID', ' ',
                           ' ',
                           'elo'),
            CogDescription('RolesChannelID', ' ',
                           ' ',
                           'roles'),
            ]


class Reaction(Cog):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('channel')

    @command(name='deploy')
    @has_permissions(manage_channels=True, manage_messages=True)
    async def deploy_cog(self, ctx, cog_str, channel_id: Optional[int | str], category: Optional[CategoryChannel]):
        """
        :param ctx: automatically passed
        :param cog_str: the function that should be activated
        :param channel_id: defines the channel which will manage the elo system
        if nothing is handed bot creates a category section with the channel
        :return:

        examples: !deploy 'log' 939852446019256370
                  !deploy 'elo'
        """
        await ctx.message.delete(delay=10)
        print(f'{cog_str=}')
        if cog_str == 'all':
            [await self.deploy_cog(ctx, cog.cmd, None, None) for cog in cog_list]
            return

        for channel in ctx.guild.channels:
            print(f'{channel.mention == channel_id}=')

        cog = next(cog for cog in cog_list if cog.cmd == cog_str)
        if not category:
            cat_id = db.field("SELECT BotCatID FROM Guilds WHERE GuildID = ?", ctx.guild.id)
            category = next((category for category in ctx.guild.categories if category.id == cat_id), None)

        if isinstance(channel_id, int):
            channel = self.bot.get_channel(channel_id)
        elif isinstance(channel_id, str):
            channel = next(channel for channel in ctx.guild.channels if channel.mention == channel_id)
        else:
            channel = None

        if channel is None:
            if category is None:
                category = await ctx.guild.create_category(name='cicero_bot')
                db.execute("UPDATE Guilds SET BotCatID = ? WHERE GuildID = ?", category.id, ctx.guild.id)
            channel = await ctx.guild.create_text_channel(
                name=f"{cog_str}_channel",
                category=category,
                topic=cog.description,
                reason=cog.goal
            )
        db.execute(f"UPDATE Guilds SET {cog.sql_repr} = ? WHERE GuildID = ?", channel.id, ctx.guild.id)
        db.commit()


class NoChannelError(Exception):
    def __init__(self, cog_name="default"):
        self.message = f"The Channel of {cog_name} hasn't been assigned yet.\n More Information with '!help deploy'"
        super().__init__(self.message)


def setup(bot):
    bot.add_cog(Reaction(bot))
