"""Turn raw snapshots into text.

`plain_*` functions build a factual summary from real numbers. `humanize`
optionally rewrites that summary in a friendly voice via the LLM — but the
*numbers always come from code*, so the bot can never invent or contradict data.
If no API key is set (or the call fails), we return the plain text unchanged.
"""
from . import config

ROOM_NAMES = {
    "drawing": "Drawing Room",
    "work1": "Work Room 1",
    "work2": "Work Room 2",
}


def _room_line(name: str, devices: list[dict]) -> str:
    on = [d for d in devices if d["status"] == "on"]
    if not on:
        return f"{name}: all off."
    fans = sum(1 for d in on if d["type"] == "fan")
    lights = sum(1 for d in on if d["type"] == "light")
    parts = []
    if fans:
        parts.append(f"{fans} fan{'s' if fans != 1 else ''} ON")
    if lights:
        parts.append(f"{lights} light{'s' if lights != 1 else ''} ON")
    return f"{name}: {', '.join(parts)}."


def plain_status(snapshot: dict) -> str:
    lines = []
    for room_id, name in ROOM_NAMES.items():
        devices = [d for d in snapshot["devices"] if d["room"] == room_id]
        lines.append(_room_line(name, devices))
    return " ".join(lines)


def plain_room(room: dict) -> str:
    return _room_line(room["roomName"], room["devices"]) + f" ({room['powerW']}W)"


def plain_usage(totals: dict) -> str:
    return (
        f"Total power right now: {totals['totalPowerW']}W. "
        f"Today's estimated usage: {totals['estimatedKWhToday']} kWh."
    )


async def humanize(facts: str) -> str:
    """Rewrite `facts` in a warm, concise voice. Falls back to `facts` on error."""
    if not config.ANTHROPIC_API_KEY:
        return facts
    try:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        msg = await client.messages.create(
            model=config.LLM_MODEL,
            max_tokens=200,
            system=(
                "You are a friendly office assistant bot. Rephrase the given "
                "facts in one or two warm, natural sentences. Do NOT change, add, "
                "or invent any numbers — only the wording. No robotic data dumps."
            ),
            messages=[{"role": "user", "content": facts}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return facts  # graceful fallback keeps the bot working offline
