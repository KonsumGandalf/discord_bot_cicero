from datetime import datetime, timedelta
from platform import python_version
from time import time

from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType, Embed
from discord import __version__ as discord_version
from discord.ext.commands import Cog
from discord.ext.commands import command
from psutil import Process, virtual_memory
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from lib.db import db


class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

        self._message = "watching !help | {users:,} users in {guilds:,} servers"

        self.scheduler = AsyncIOScheduler(timezone='Europe/Berlin')
        self.scheduler.add_job(self.set, 'cron', day_of_week="mon-fri", hour='10', second='0')

    @property
    def message(self):
        return self._message.format(users=len(self.bot.users), guilds=len(self.bot.guilds))

    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            print(ValueError("Invalid activity type."))

        self._message = value

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)

        await self.bot.change_presence(activity=Activity(
            name=_name, type=getattr(ActivityType, _type, ActivityType.playing)
        ))

    @command(name="setactivity")
    async def set_activity_message(self, ctx, *, text: str):
        self.message = text
        await self.set()

    @command(name="ping")
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(f"Pong! DWSP latency: {self.bot.latency * 1000:,.0f} ms.")
        end = time()

        await message.edit(
            content=f"Pong! DWSP latency: {self.bot.latency * 1000:,.0f} ms. Response time: {(end - start) * 1000:,.0f} ms.")

    @command(name="stats")
    async def show_bot_stats(self, ctx):
        embed = Embed(title="Bot stats",
                      colour=ctx.author.colour,
                      thumbnail=self.bot.user.avatar_url,
                      timestamp=datetime.utcnow())

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time() - proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [
            ("Bot version", self.bot.VERSION, True),
            ("Python version", python_version(), True),
            ("discord.py version", discord_version, True),
            ("Uptime", uptime, True),
            ("CPU time", cpu_time, True),
            ("Memory usage", f"{round(mem_usage, -1)} / {round(mem_total, -2)} MiB ({round(mem_of_total, 1)}%)", True),
            ("Users", f"{self.bot.guild.member_count:,}", True)
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    def is_all_shutdown(self, ctx) -> bool:
        if not ctx.author.bot:
            return bool(db.record("SELECT UserID FROM Admins WHERE UserID == ?", ctx.author.id))
        else:
            return False

    @command(name="shutdown")
    async def shutdown(self, ctx):
        if self.is_all_shutdown(ctx):
            await ctx.send("Shutting down...")

            #with open("./data/banlist.txt", "w", encoding="utf-8") as f:
            #    f.writelines([f"{item}\n" for item in self.bot.banlist])

            db.commit()
            self.bot.scheduler.shutdown()
            await self.bot.logout()
        else:
            await ctx.send('You are not allowed to shutdown the bot!')


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("meta")


def setup(bot):
    bot.add_cog(Meta(bot))
