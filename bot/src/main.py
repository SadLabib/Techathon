"""Discord bot entrypoint — slash commands with rich embeds.

Run:  python -m src.main   (from the bot/ directory)
"""
import asyncio
from datetime import datetime, timezone

import discord
from discord import app_commands

from . import alert_watcher, backend_client, config

# ---------------------------------------------------------------------------
# Bot setup — slash commands don't need message_content intent
# ---------------------------------------------------------------------------
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
GUILD = discord.Object(id=config.GUILD_ID)

# Thumbnails used in each embed
ICON_OFFICE  = "https://cdn-icons-png.flaticon.com/512/1040/1040993.png"
ICON_ROOM    = "https://cdn-icons-png.flaticon.com/512/2933/2933245.png"
ICON_POWER   = "https://cdn-icons-png.flaticon.com/512/3090/3090264.png"

ROOM_NAMES = {
    "drawing": "Drawing Room",
    "work1":   "Work Room 1",
    "work2":   "Work Room 2",
}

ROOM_EMOJI = {
    "drawing": "🎨",
    "work1":   "💼",
    "work2":   "💼",
}


# ---------------------------------------------------------------------------
# Embed builders
# ---------------------------------------------------------------------------

def _room_field_value(devices: list[dict]) -> str:
    on = [d for d in devices if d["status"] == "on"]
    fans   = sum(1 for d in on if d["type"] == "fan")
    lights = sum(1 for d in on if d["type"] == "light")
    total_w = sum(d["powerW"] for d in on)

    if not on:
        return "✅ All devices OFF"

    parts = []
    if fans:
        parts.append(f"🌀 `{fans}` fan{'s' if fans != 1 else ''} ON")
    if lights:
        parts.append(f"💡 `{lights}` light{'s' if lights != 1 else ''} ON")
    parts.append(f"⚡ `{total_w}W`")
    return "\n".join(parts)


def _alert_color(alerts: list[dict]) -> discord.Color:
    if not alerts:
        return discord.Color.from_rgb(34, 197, 94)   # green
    return discord.Color.from_rgb(251, 146, 60)       # orange


def _build_status_embed(snapshot: dict) -> discord.Embed:
    alerts = snapshot.get("alerts", [])
    totals = snapshot["totals"]
    devices = snapshot["devices"]
    sim_time = snapshot.get("simTime", "—")

    color = _alert_color(alerts)
    embed = discord.Embed(
        title="🏢  Office Energy Monitor",
        description=f"**Live snapshot** • Office time `{sim_time}`",
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_thumbnail(url=ICON_OFFICE)

    # One field per room
    for room_id, name in ROOM_NAMES.items():
        room_devices = [d for d in devices if d["room"] == room_id]
        value = _room_field_value(room_devices)
        embed.add_field(
            name=f"{ROOM_EMOJI[room_id]}  {name}",
            value=value,
            inline=True,
        )

    # Power summary
    embed.add_field(name="\u200b", value="\u200b", inline=False)   # spacer
    embed.add_field(
        name="⚡  Total Power",
        value=f"**`{totals['totalPowerW']} W`**",
        inline=True,
    )
    embed.add_field(
        name="📊  Est. Today",
        value=f"**`{totals['estimatedKWhToday']} kWh`**",
        inline=True,
    )

    # Active alerts
    if alerts:
        recent = alerts[:3]
        alert_lines = "\n".join(f"⚠️ {a['message']}" for a in recent)
        embed.add_field(name="🚨  Active Alerts", value=alert_lines, inline=False)

    embed.set_footer(text="Office Energy Monitor  •  /status")
    return embed


def _build_room_embed(room: dict) -> discord.Embed:
    room_id   = room["room"]
    room_name = room["roomName"]
    devices   = room["devices"]
    power_w   = room["powerW"]
    sim_time  = room.get("simTime", "—")

    on_devices = [d for d in devices if d["status"] == "on"]
    color = discord.Color.from_rgb(34, 197, 94) if not on_devices else discord.Color.from_rgb(99, 179, 237)

    embed = discord.Embed(
        title=f"{ROOM_EMOJI.get(room_id, '🏠')}  {room_name}",
        description=f"Live device status • Office time `{sim_time}`",
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_thumbnail(url=ICON_ROOM)

    fans   = [d for d in devices if d["type"] == "fan"]
    lights = [d for d in devices if d["type"] == "light"]

    def device_status_line(d: dict) -> str:
        icon = "🟢" if d["status"] == "on" else "⚫"
        power = f"`{d['powerW']}W`" if d["status"] == "on" else "`0W`"
        return f"{icon} **{d['label']}** — {power}"

    embed.add_field(
        name="🌀  Fans",
        value="\n".join(device_status_line(d) for d in fans) or "None",
        inline=True,
    )
    embed.add_field(
        name="💡  Lights",
        value="\n".join(device_status_line(d) for d in lights) or "None",
        inline=True,
    )
    embed.add_field(
        name="⚡  Room Power",
        value=f"**`{power_w} W`**",
        inline=False,
    )
    embed.set_footer(text=f"Office Energy Monitor  •  /room {room_id}")
    return embed


def _build_usage_embed(totals: dict) -> discord.Embed:
    total_w = totals["totalPowerW"]
    kwh     = totals["estimatedKWhToday"]

    # Color: green < 500W, orange < 1000W, red >= 1000W
    if total_w < 500:
        color = discord.Color.from_rgb(34, 197, 94)
    elif total_w < 1000:
        color = discord.Color.from_rgb(251, 146, 60)
    else:
        color = discord.Color.from_rgb(239, 68, 68)

    per_room: dict = totals.get("perRoomW", {})

    embed = discord.Embed(
        title="⚡  Power Usage",
        description="Real-time energy consumption across the office",
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_thumbnail(url=ICON_POWER)

    embed.add_field(
        name="🔌  Total Right Now",
        value=f"**`{total_w} W`**",
        inline=True,
    )
    embed.add_field(
        name="📊  Est. Usage Today",
        value=f"**`{kwh} kWh`**",
        inline=True,
    )

    if per_room:
        embed.add_field(name="\u200b", value="\u200b", inline=False)  # spacer
        for room_id, name in ROOM_NAMES.items():
            w = per_room.get(room_id, 0)
            bar_filled = int((w / max(total_w, 1)) * 10)
            bar = "█" * bar_filled + "░" * (10 - bar_filled)
            embed.add_field(
                name=f"{ROOM_EMOJI[room_id]}  {name}",
                value=f"`{bar}` **{w}W**",
                inline=False,
            )

    embed.set_footer(text="Office Energy Monitor  •  /usage")
    return embed


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    tree.copy_global_to(guild=GUILD)
    await tree.sync(guild=GUILD)
    print(f"Slash commands synced to guild {config.GUILD_ID}.")
    asyncio.create_task(alert_watcher.watch(bot))


@tree.command(name="status", description="Full office device & power status", guild=GUILD)
async def status_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        snapshot = await backend_client.get_snapshot()
        embed = _build_status_embed(snapshot)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Backend Unavailable",
            description=f"Could not reach the backend.\n```{e}```",
            color=discord.Color.red(),
        )
    await interaction.followup.send(embed=embed)


@tree.command(name="room", description="Status of a specific room", guild=GUILD)
@app_commands.describe(name="Room name: drawing, work1, or work2")
async def room_cmd(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    ALIASES = {
        "drawing": "drawing", "draw": "drawing",
        "work1": "work1", "w1": "work1",
        "work2": "work2", "w2": "work2",
    }
    room_id = ALIASES.get(name.strip().lower())
    if not room_id:
        embed = discord.Embed(
            title="❓ Unknown Room",
            description="Try `drawing`, `work1`, or `work2`.",
            color=discord.Color.orange(),
        )
        await interaction.followup.send(embed=embed)
        return
    try:
        room = await backend_client.get_room(room_id)
        embed = _build_room_embed(room)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Backend Unavailable",
            description=f"```{e}```",
            color=discord.Color.red(),
        )
    await interaction.followup.send(embed=embed)


@tree.command(name="usage", description="Total power usage and estimated kWh today", guild=GUILD)
async def usage_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        totals = await backend_client.get_usage()
        embed = _build_usage_embed(totals)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Backend Unavailable",
            description=f"```{e}```",
            color=discord.Color.red(),
        )
    await interaction.followup.send(embed=embed)


def main():
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN is not set.")
    bot.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
