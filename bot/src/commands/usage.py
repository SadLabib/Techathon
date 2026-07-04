"""!usage — total power now + estimated kWh today, from live data."""
from .. import backend_client, formatting


async def handle() -> str:
    totals = await backend_client.get_usage()
    facts = formatting.plain_usage(totals)
    return await formatting.humanize(facts)
