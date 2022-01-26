import discord

from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.command()
async def hello(ctx):
    await ctx.reply('Hello there')
    discord.Client.user

bot.run('ODEwNDMwMDM4MDgzNjMzMTUz.YCjhyg.wFP1hJqi7nl38iGRTcdJ_LLVeP0')
