from discord.ext.commands import Cog

from ..db import db


class Reaction(Cog):
    channel_id = None
    reaction_msg = None
    nationalities_dict: dict

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.nationalities_dict = {
                '🇦🇹': self.bot.guild.get_role(939498957174866010),
                '🇩🇪': self.bot.guild.get_role(939498561194823711),
                '🇧🇪': self.bot.guild.get_role(939498709379579927),
                '🇬🇪': self.bot.guild.get_role(939498828107759657),
            }

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

            current_chosen_roles = filter(lambda ele: ele in self.nationalities_dict.values(), member.roles)
            await member.remove_roles(*current_chosen_roles, reason="New reaction assigned")

            await member.add_roles(self.nationalities_dict[payload.emoji.name], reason="Self assigned")

            await self.reaction_msg.remove_reaction(payload.emoji, member)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.member and self.bot.ready and payload.message_id == self.reaction_msg.id:
            member = self.bot.guild.get_member(payload.user_id)
            await member.remove_roles(self.nationalities_dict[payload.emoji.name], reason="Self dismissed")


def setup(bot):
    bot.add_cog(Reaction(bot))
