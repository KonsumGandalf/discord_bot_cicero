import json
from datetime import datetime
from typing import Optional

from discord import Embed, Member, Role
from discord.colour import Colour
from discord.ext.commands import Cog, has_permissions, command

from lib.db import db

class Roles(Cog):
    roles_dict: dict = {}
    message_list: list = []

    def __init__(self, bot):
        self.bot = bot
        self.numbers_set = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
                            "6⃣", "7⃣", "8⃣", "9⃣", "🔟")
        self.channel_id_col = "RolesChannelID"


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print(await self.bot.guild.edit_role_positions(positions={}))
            self.bot.cogs_ready.ready_up('roles')
        # await self.bot.channel.send('Cog listener added')

    async def assign_role(self, ctx, name, colour=Colour.magenta(),
                          hoist=True, mentionable=True, reason='automatic'):
        await ctx.send(f'{type(Colour.random())=} and {Colour.random()}')
        role = await self.bot.guild.create_role(name=name, colour=Colour.random(),
                                                hoist=hoist, mentionable=mentionable, reason=reason)
        await ctx.author.add_roles(role, reason='automatic')

    @has_permissions(manage_guild=True)
    @command(name="create_role", aliases=['crole'])
    async def create_role_command(self, ctx, name="empty", **role_options):
        if len(name) < 4:
            await self.bot.cicero_get_channel(ctx, self.channel_id_col).send(
                "Provide a role name longer than 4 Characters.")
        else:
            await self.assign_role(ctx, name, role_options)
            # await ctx.author.add_roles(new_role, reason='automatic')

    @has_permissions(manage_guild=True)
    @command(name="role_automate", aliases=['automatic_role', 'role_embed'])
    async def role_automate(self, ctx, heading: str = "empty", *role_options):
        if len(role_options) > 10:
            await ctx.send("The maximum number of roles is 10")
        else:
            embed = Embed(title='Role management',
                          description=heading,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())

            roles_assign_list = [await self.bot.guild.create_role(name=role, colour=Colour.random())
                                 for role in role_options]

            fields = [('Roles',
                       "\n".join([f'{self.numbers_set[idx]} {option}' for idx, option in enumerate(roles_assign_list)]),
                       False),
                      ("Instructions", "React to chose roles", False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            message = await self.bot.cicero_get_channel(ctx, self.channel_id_col).send(embed=embed)

            for idx, emoji in enumerate(self.numbers_set[:len(role_options)]):
                await message.add_reaction(emoji=emoji)
                self.roles_dict[emoji] = roles_assign_list[idx]

            print(self.roles_dict)

            self.message_list.append(message)

    @has_permissions(manage_roles=True)
    @command(name="create_ladder_roles", aliases = ['deploy_ladder'])
    async def role_automate(self, ctx, role_below: str):
        """"""
        """positions = {}
        for role in ctx.guild.roles:
            positions[role.name] = role.position"""
        if not db.field("SELECT LadderActive FROM Guilds WHERE GuildID = (?)", ctx.guild.id):
            if str(role_below[2]) == '&':
                position_below = next(role.position for role in ctx.guild.roles if role.mention == role_below)
            elif str(role_below[2]) == '!':
                # the api inserts to the mention in members an '!' for roles this is not the case
                position_below = next(user.top_role.position for user in ctx.guild.members
                                      if user.mention == role_below[:2] + role_below[3:])
            else:
                await ctx.send('Role was not found please specify. More instructions with !help role_automate')
                return
            with open('data/roles/predefined.json') as roles:
                roles_json_list = json.load(roles)['roles']

            positions = {}
            for role_json in roles_json_list:
                role = await ctx.guild.create_role(name=role_json['Name'], colour=int(f"0x{role_json['Colour']}", base=16),
                                                        hoist=True, mentionable=True, reason=role_json['Ratio'])
                positions[role] = position_below - 1

            await self.bot.guild.edit_role_positions(positions=positions)

            for role in ctx.guild.roles:
                print(role.position, role)

            embed = Embed(title='Role update',
                          description=f'The roles for the ladder were introduced by {ctx.author.mention}.',
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())

            fields = [('Roles',
                       "\n".join([f'{role.mention} - contains {roles_json_list[idx]["Ratio"]}'
                                  for idx, role in enumerate(positions)]),
                       False),
                      ("Instructions", "Start playing games to climb the ladder and become the new champion", False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            db.execute("UPDATE Guilds SET LadderActive = ? WHERE GuildID = ?", 1, ctx.guild.id)
            db.commit()
            await self.bot.cicero_get_channel(ctx, self.channel_id_col).send(embed=embed)
        else:
            await ctx.send('The ladder system was already implemented. To reset it: !reset_ladder')


"""    @Cog.listener()
async def on_raw_reaction_add(self, payload):
    current_message = [ele for ele in self.message_list if payload.message_id == ele.id][0]
    if self.bot.ready and not payload.member.bot and current_message:
        member = self.bot.guild.get_member(payload.user_id)

        # current_chosen_roles = filter(lambda emoji: self.bot.guild.get_role(emoji) in self.numbers_set, member.roles)
        # await member.remove_roles(*current_chosen_roles, reason="New reaction assigned")

        await member.add_roles(self.roles_dict[payload.emoji.name], reason="Self assigned")

        if not [reaction for reaction in self.message_list if payload.member.id == reaction.author.id]:
            await current_message.remove_reaction(payload.emoji, member)"""


@Cog.listener()
async def on_message(self, msg):
    if not msg.author.bot:
        pass


def setup(bot):
    bot.add_cog(Roles(bot))
