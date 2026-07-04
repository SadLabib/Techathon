"""Bonus: poll the backend for new alerts and post them to a Discord channel.

Tracks alert ids we've already announced so each alert is posted once.
"""
import asyncio

from . import backend_client, config

_POLL_SECONDS = 10


async def watch(bot) -> None:
    """Run forever: fetch alerts, post any we haven't seen to the alert channel."""
    if not config.ALERT_CHANNEL_ID:
        return  # feature disabled if no channel configured

    seen: set[str] = set()
    await bot.wait_until_ready()
    channel = bot.get_channel(int(config.ALERT_CHANNEL_ID))

    # Prime `seen` with existing alerts so we don't spam history on startup.
    try:
        for alert in await backend_client.get_alerts():
            seen.add(alert["id"])
    except Exception:
        pass

    while not bot.is_closed():
        try:
            for alert in await backend_client.get_alerts():
                if alert["id"] not in seen:
                    seen.add(alert["id"])
                    if channel is not None:
                        await channel.send(f"⚠️ {alert['message']}")
        except Exception:
            pass  # keep the loop alive through transient backend hiccups
        await asyncio.sleep(_POLL_SECONDS)
