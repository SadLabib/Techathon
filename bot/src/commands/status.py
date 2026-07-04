"""!status — whole-office summary from live data."""
from .. import backend_client, formatting


async def handle() -> str:
    snapshot = await backend_client.get_snapshot()
    facts = formatting.plain_status(snapshot)
    return await formatting.humanize(facts)
