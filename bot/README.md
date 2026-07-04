# Discord Bot

Deliverable #5 (10%). A Discord bot that answers questions about the office by
reading the **same backend** as the dashboard, with friendly, LLM-humanized
replies.

> Commands and the alert watcher are implemented; running it just needs deps
> installed and a Discord token + (optional) Anthropic key in `.env`. See
> [`../docs/PLAN.md`](../docs/PLAN.md) §7.5.

## Module layout (separation of concerns)

| File | Concern |
|---|---|
| `src/config.py` | Env/config (bot token, backend URL, LLM key, alert channel) |
| `src/backend_client.py` | Async HTTP calls to the backend API (the shared truth) |
| `src/formatting.py` | Turn a snapshot into plain text + optional LLM humanization |
| `src/commands/status.py` | `!status` — whole-office summary |
| `src/commands/room.py` | `!room <name>` — one room |
| `src/commands/usage.py` | `!usage` — total power + estimated kWh today |
| `src/alert_watcher.py` | Poll `/api/alerts`, proactively post new ones (bonus) |
| `src/main.py` | discord.py client that wires commands + watcher together |

The command modules are plain async functions returning strings — they don't
import discord, so they can be unit-tested against the backend without a Discord
connection.

## Commands

| Command | Does |
|---|---|
| `!status` | "Drawing Room: 1 fan ON, 2 lights ON. Work Room 1: all off…" |
| `!room <name>` | Status of one room (`drawing`, `work1`, `work2`) |
| `!usage` | "Total power right now: 740W. Today's estimated usage: 4.2 kWh." |

Answers come from live simulated data — never hardcoded. Numbers are computed in
code and only *phrased* by the LLM, so the bot can never contradict the
dashboard.

## Setup (once implemented)

```bash
cd bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # fill in DISCORD_TOKEN, ANTHROPIC_API_KEY, etc.
python -m src.main
```
