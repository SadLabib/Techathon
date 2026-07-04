"""!room <name> — status of one room from live data."""
import httpx

from .. import backend_client, formatting

# Accept a few friendly aliases for each room id.
ALIASES = {
    "drawing": "drawing", "draw": "drawing", "waiting": "drawing",
    "work1": "work1", "work 1": "work1", "workroom1": "work1", "w1": "work1",
    "work2": "work2", "work 2": "work2", "workroom2": "work2", "w2": "work2",
}


async def handle(name: str) -> str:
    room_id = ALIASES.get(name.strip().lower())
    if not room_id:
        return (
            "I don't know that room. Try `drawing`, `work1`, or `work2`."
        )
    try:
        room = await backend_client.get_room(room_id)
    except httpx.HTTPStatusError:
        return "I couldn't find that room on the backend."
    facts = formatting.plain_room(room)
    return await formatting.humanize(facts)
