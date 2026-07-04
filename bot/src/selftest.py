"""Exercise the command handlers against a running backend, no Discord needed.

Run:  python -m src.selftest    (backend must be up at BACKEND_URL)
"""
import asyncio

from . import config
from .commands import room, status, usage


async def main() -> None:
    print(f"Backend: {config.BACKEND_URL}")
    print(f"Gemini:  {'enabled' if config.GEMINI_API_KEY else 'disabled (plain text)'}\n")

    print("!status ->")
    print(" ", await status.handle(), "\n")

    for name in ("drawing", "work1", "work2"):
        print(f"!room {name} ->")
        print(" ", await room.handle(name), "\n")

    print("!usage ->")
    print(" ", await usage.handle())


if __name__ == "__main__":
    asyncio.run(main())
