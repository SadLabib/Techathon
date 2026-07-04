# Architecture

One backend is the **single source of truth** for device state. A simulator
mutates it; the web dashboard and the Discord bot both read from it, so the two
interfaces can never disagree.

```
                        ┌──────────────────────────────────────────────┐
                        │                BACKEND (one process)          │
                        │                                               │
  ┌──────────────┐ tick │   ┌───────────────┐      ┌────────────────┐   │
  │  Simulator   ├──────┼──▶│  State Store  │─────▶│  Alert Engine  │   │
  │ flips devices│ ~2s  │   │ (source of    │      │ office-hours + │   │
  │ sets power   │      │   │  truth)       │      │ 2h-on rules    │   │
  └──────────────┘      │   └───────┬───────┘      └───────┬────────┘   │
                        │           ▼                      ▼            │
                        │   ┌──────────────────────────────────────┐   │
                        │   │  REST API          WebSocket (/ws)    │   │
                        │   │  /api/devices      emit "snapshot"    │   │
                        │   │  /api/rooms/:id    on every tick      │   │
                        │   │  /api/usage /api/alerts               │   │
                        │   └───────┬───────────────────┬───────────┘   │
                        └───────────┼───────────────────┼───────────────┘
                        REST (init) │                   │ live push / poll
                        + WS (live) ▼                   ▼
                        ┌────────────────────┐   ┌────────────────────┐
                        │   WEB DASHBOARD     │   │    DISCORD BOT      │
                        │  React + Vite       │   │  discord.py         │
                        │  device panel       │   │  !status / !room    │
                        │  power meter        │   │  !usage             │
                        │  alerts panel       │   │  LLM-humanized      │
                        └─────────┬──────────┘   └─────────┬──────────┘
                                  ▼                        ▼
                              Boss (browser)          Boss (Discord)
```

## Data flow (one device change → both surfaces)

1. A simulator tick flips a device (e.g. `work2-fan-1` → ON), stamps
   `lastChanged`, and recomputes `powerW`.
2. It writes into the **State Store** — the only mutable state in the system.
3. The **Alert Engine** re-evaluates its rules against the new snapshot.
4. The backend **broadcasts** the new snapshot over WebSocket → every dashboard
   updates instantly, no refresh.
5. When the boss runs `!status` in Discord, the bot reads the **same** API and
   gets the identical snapshot.

## Repository layout

| Folder | Concern |
|---|---|
| `backend/` | FastAPI app — state store, simulator, alert engine, REST + WebSocket |
| `frontend/` | React dashboard — live UI over WebSocket |
| `bot/` | Discord bot — reads the backend API, LLM-humanized replies |
| `docs/` | Diagrams, circuit schematic, architecture, plan, problem statement |
| `scripts/` | Dev helpers (run everything at once) |

> The rendered system diagram (not Mermaid) lives in `docs/diagrams/`, and the
> hardware schematic + pin mapping in `docs/circuit/`.
