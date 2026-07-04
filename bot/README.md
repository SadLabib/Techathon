# Discord Bot

Deliverable #5 (10%). A Discord bot that answers questions about the office by
reading the **same backend** as the dashboard, with friendly, LLM-humanized
replies (Google **Gemini** free tier).

> Fully implemented. To run it you need deps installed, a **Discord bot token**,
> and optionally a **Gemini API key** (without one, replies are plain but still
> correct). See [`../docs/PLAN.md`](../docs/PLAN.md) §7.5.

## Module layout (separation of concerns)

| File | Concern |
|---|---|
| `src/config.py` | Env/config (bot token, backend URL, Gemini key, alert channel) |
| `src/backend_client.py` | Async HTTP calls to the backend API (the shared truth) |
| `src/formatting.py` | Snapshot → plain text + optional Gemini humanization |
| `src/commands/status.py` | `!status` — whole-office summary |
| `src/commands/room.py` | `!room <name>` — one room |
| `src/commands/usage.py` | `!usage` — total power + estimated kWh today |
| `src/alert_watcher.py` | Poll `/api/alerts`, proactively post new ones (bonus) |
| `src/main.py` | discord.py client that wires commands + watcher together |

The command modules are plain async functions returning strings — they don't
import discord, so they can be tested against the backend without Discord.

## Commands

| Command | Does |
|---|---|
| `!status` | "Drawing Room: 1 fan ON, 2 lights ON. Work Room 1: all off…" |
| `!room <name>` | Status of one room (`drawing`, `work1`, `work2`) |
| `!usage` | "Total power right now: 740W. Today's estimated usage: 4.2 kWh." |

Answers come from live simulated data — never hardcoded. Numbers are computed in
code and only *phrased* by Gemini, so the bot can never contradict the dashboard.

## Setup

Make sure the **backend is running first** (`../backend`).

```bash
cd bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then fill it in (see below)
python -m src.main
```

### `.env` values

| Var | Required? | Where to get it |
|---|---|---|
| `DISCORD_TOKEN` | Yes | Discord Developer Portal → your app → Bot → Reset Token |
| `BACKEND_URL` | Yes | Your backend URL, e.g. `http://localhost:8000` |
| `GEMINI_API_KEY` | Optional | <https://aistudio.google.com/apikey> (free) |
| `GEMINI_MODEL` | Optional | Defaults to `gemini-2.0-flash` |
| `ALERT_CHANNEL_ID` | Optional | Right-click a channel → Copy Channel ID (for proactive alerts) |

## Getting the bot into Discord (step by step)

1. Go to <https://discord.com/developers/applications> → **New Application**.
2. Open **Bot** (left menu) → **Reset Token** → copy it into `DISCORD_TOKEN`.
3. On the same Bot page, enable **Privileged Gateway Intents → Message Content
   Intent** (required to read `!` commands).
4. Open **OAuth2 → URL Generator**: tick scope **bot**, then bot permissions
   **Send Messages** + **Read Message History**. Copy the generated URL.
5. Paste that URL in a browser, pick your server, and **Authorize** — the bot
   joins your server.
6. Run `python -m src.main`. When the console prints `Logged in as ...`, type
   `!status` in any channel the bot can see.

To get `ALERT_CHANNEL_ID`: Discord → User Settings → Advanced → enable
**Developer Mode**, then right-click the channel → **Copy Channel ID**.

## Testing without Discord

You can exercise the whole data path (backend → formatting) without a Discord
connection:

```bash
python -m src.selftest        # prints what !status / !room / !usage would reply
```
