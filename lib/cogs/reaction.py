from datetime import datetime, timedelta

from discord import Embed
from discord.ext.commands import Cog, has_permissions, command

from ..db import db


class Reaction(Cog):
    channel = None
    reaction_msg = None
    nationalities_dict: dict
    numbers_set: tuple
    polls = []

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

            self.numbers_set = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
                                "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

            self.channel = self.bot.get_channel(
                db.field('SELECT ReactChannelID FROM Guilds WHERE GuildID= (?)', self.bot.guild.id))
            self.reaction_msg = await self.channel.fetch_message(939474652944801833)
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

    @command(name="poll", aliases=['make_poll, mpoll'])
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx, duration: float = 24.0, question: str = "empty", *options):
        if len(options) > 10:
            await ctx.send("The maximum number of options is 10")
        else:
            embed = Embed(title='Poll',
                          description=question,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())

            fields = [(
                'Options', "\n".join([f'{self.numbers_set[idx]} {option}' for idx, option in enumerate(options)]),
                False),
                ("Instructions", "React to case a vote", False),
                ("Poll end: ", f'{(datetime.now() + timedelta(hours=duration)).strftime("%B %d %Y - %H:%M:%S")}', False)
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            message = await self.channel.send(embed=embed)

            for emoji in self.numbers_set[:len(options)]:
                await message.add_reaction(emoji=emoji)

            self.polls.append((message.channel.id, message.id))
            # interessting
            print(duration * 3600)
            self.bot.scheduler.add_job(self.complete_poll, "date",
                                       run_date=datetime.now() + timedelta(seconds=duration),
                                       args=[message.id])

    async def complete_poll(self, message_id):
        message = await self.channel.fetch_message(message_id)
        most_voted = max(message.reactions, key=lambda r: r.count)
        most_voted_count = max([ele.count for ele in message.reactions]) - 1
        print(str(message.reactions))
        most_voted_list = [self.numbers_set[idx] for idx, ele in enumerate(message.reactions) if
                           most_voted.count == ele.count]
        await self.channel.send(f"The most voted option{' is' if len(most_voted_list) <= 1 else 's are'} "
                                f"{' ,'.join(most_voted_list)} with {most_voted_count} votes")
        # self.polls.remove((self.channel, message_id))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_msg.id:
            member = self.bot.guild.get_member(payload.user_id)

            current_chosen_roles = filter(lambda ele: ele in self.nationalities_dict.values(), member.roles)
            await member.remove_roles(*current_chosen_roles, reason="New reaction assigned")

            await member.add_roles(self.nationalities_dict[payload.emoji.name], reason="Self assigned")

            if not payload.member.id == self.reaction_msg.author.id:
                await self.reaction_msg.remove_reaction(payload.emoji, member)

            """        elif payload.message_id in (poll[1] for poll in self.polls):
            message = await self.channel.fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                        and payload.member in await reaction.users().flatten()
                        and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)"""

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        print(payload.member)
        if payload.member and self.bot.ready and payload.message_id == self.reaction_msg.id:
            member = self.bot.guild.get_member(payload.user_id)
            await member.remove_roles(self.nationalities_dict[payload.emoji.name], reason="Self dismissed")


def setup(bot):
    bot.add_cog(Reaction(bot))
