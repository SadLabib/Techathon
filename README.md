# Office Energy Monitor

Real-time monitoring of an office's lights and fans through a **web dashboard**
and a **Discord bot**, both reading from a **single FastAPI backend** that is
the one source of truth for device state.

See [`docs/PLAN.md`](./docs/PLAN.md) for the full build plan and
[`docs/architecture.md`](./docs/architecture.md) for the architecture.

```
[Simulator] -> [FastAPI Store] -> REST + WebSocket -> [ Dashboard ] & [ Bot ]
```

## Repository layout

| Folder | What's in it |
|---|---|
| `backend/` | FastAPI app — state store, simulator, alert engine, REST + WebSocket |
| `frontend/` | React + Vite + Tailwind dashboard (live over WebSocket) |
| `bot/` | Discord bot — reads the same backend API, LLM-humanized replies |
| `docs/` | Plan, architecture, system diagram, circuit schematic, problem statement |
| `scripts/` | Dev helpers (`dev.sh` runs backend + frontend together) |

## What's built so far

- **Backend** (`backend/`) — FastAPI + WebSocket. An in-memory `Store` holds all
  devices; a background simulator ticks every ~2s, flips devices realistically
  by time of day, accumulates energy, and raises alerts (after-hours + a room
  fully on > 2h). New snapshots are pushed to every connected dashboard.
- **Frontend** (`frontend/`) — React + Vite + Tailwind. Live device panel per
  room (fans spin, lights glow), live power meter with per-room breakdown, and
  a timestamped alerts panel. Updates over WebSocket with no page refresh and
  auto-reconnects.

## Prerequisites

- Python 3.10+
- Node.js 18+

## Run everything (one command)

```bash
./scripts/dev.sh
```

Starts the backend and frontend together (Ctrl-C stops both). Override ports
with `BACKEND_PORT` / `FRONTEND_PORT`. Prefer to run them separately? See below.

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Check it: <http://localhost:8000/api/devices> should return a live JSON snapshot.

## Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The connection dot turns green ("Live") once the
WebSocket is up. Open a second browser tab to see both update in lockstep.

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/devices` | Full snapshot: devices, totals, alerts, times |
| GET | `/api/rooms/{room_id}` | One room (`drawing`, `work1`, `work2`) |
| GET | `/api/usage` | Totals only (power + estimated kWh today) |
| GET | `/api/alerts` | Current alerts |
| WS  | `/ws` | Live snapshot stream (`{ "type": "snapshot", "data": {...} }`) |

## Configuration (backend env vars)

| Var | Default | Meaning |
|---|---|---|
| `FANS_PER_ROOM` | `2` | Fans per room |
| `LIGHTS_PER_ROOM` | `3` | Lights per room |
| `TICK_SECONDS` | `2.0` | Real seconds between simulation ticks |
| `SIM_MINUTES_PER_TICK` | `20` | How much the office clock advances per tick |
| `SIM_START_HOUR` | `8` | Office clock start hour |

> Device count is config-driven and defaults to **15** (2 fans + 3 lights × 3
> rooms), the math-consistent reading of the brief. Set `FANS_PER_ROOM` /
> `LIGHTS_PER_ROOM` to change it.

## Discord bot

The bot in `bot/` reads the same backend API and humanizes replies with an LLM.
See [`bot/README.md`](./bot/README.md) for setup and commands (`!status`,
`!room <name>`, `!usage`).
