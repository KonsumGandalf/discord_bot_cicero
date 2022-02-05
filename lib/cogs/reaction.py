from discord.ext.commands import Cog

class Reaction(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('reaction')

    """
    just reactions to message since the bot has be running
    """

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print(f"{user.display_name} reacted with {reaction.emoji}")

    @Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print(f"{user.display_name} remove the reaction of {reaction.emoji}")

    """
    RAW is actually faster - for all
    """
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = self.bot.guild.get_member(payload.user_id)
        print(f"{member.display_name} reacted with {payload.emoji}")

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        print(f"{payload.member.display_name} remove the reaction of {payload.emoji}")


def setup(bot):
    bot.add_cog(Reaction(bot))