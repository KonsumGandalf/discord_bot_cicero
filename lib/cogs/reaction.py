from discord.ext.commands import Cog

from ..db import db


class Reaction(Cog):
    channel_id = None
    reaction_msg = None

    def __init__(self, bot):
        self.bot = bot
        self.nationalities_dict = {
            '🇦🇹': self.bot.guild.get_role(939498957174866010),
            '🇩🇪': self.bot.guild.get_role(939498561194823711),
            '🇧🇪': self.bot.guild.get_role(939498709379579927),
            '🇬🇪': self.bot.guild.get_role(939498828107759657),
        }

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.channel_id = db.field('SELECT ReactChannelID FROM Guilds WHERE GuildID= (?)', self.bot.guild.id)
            self.reaction_msg = await self.bot.get_channel(self.channel_id).fetch_message(939474652944801833)
            print(self.reaction_msg)
            self.bot.cogs_ready.ready_up('reaction')

    """
    just reactions to message since the bot has be running -> unnecessary with raw implemented

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print(f"{user.display_name} reacted with {reaction.emoji}")

    @Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print(f"{user.display_name} remove the reaction of {reaction.emoji}")

    """

    """
    RAW is actually faster - for all
    """

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_msg.id:
            member = self.bot.guild.get_member(payload.user_id)
            role = self.bot.guild.get_role(self.nationalities_dict[payload.emoji.name])

            current_chosen_roles = filter(lambda ele: ele in self.nationalities_dict.keys(), member.roles)
            await member.remove_roles(*current_chosen_roles)

            await member.add_roles(role, reason="Self assigned")

            await self.reaction_msg.remove_reaction(member, payload.emoji)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_msg.id:
            member = self.bot.guild.get_member(payload.user_id)
            role = self.bot.guild.get_role(self.nationalities_dict[payload.emoji.name])
            await member.remove_roles(role, reason="Self assigned")


def setup(bot):
    bot.add_cog(Reaction(bot))
