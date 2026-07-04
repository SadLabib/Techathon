"""Discord bot entrypoint — wires the commands and alert watcher together.

Run:  python -m src.main   (from the bot/ directory)
"""
import discord
from discord.ext import commands as discord_commands

from . import alert_watcher, config
from .commands import room, status, usage

intents = discord.Intents.default()
intents.message_content = True  # required to read !commands

bot = discord_commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(alert_watcher.watch(bot))


@bot.command(name="status")
async def status_cmd(ctx):
    await ctx.send(await status.handle())


@bot.command(name="room")
async def room_cmd(ctx, *, name: str = ""):
    if not name:
        await ctx.send("Usage: `!room <name>` (e.g. `!room work1`)")
        return
    await ctx.send(await room.handle(name))


@bot.command(name="usage")
async def usage_cmd(ctx):
    await ctx.send(await usage.handle())


def main():
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN is not set. Copy .env.example to .env.")
    bot.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
