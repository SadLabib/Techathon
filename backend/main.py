"""FastAPI backend: REST + WebSocket over one shared Store.

Run:  uvicorn main:app --reload --port 8000
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.state import Store

# The one and only source of truth. The Discord bot can import this same object.
store = Store()


class ConnectionManager:
    """Tracks connected dashboards and pushes snapshots to all of them."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


async def simulator_loop():
    """Tick the store forever and broadcast every new snapshot."""
    while True:
        store.tick()
        await manager.broadcast({"type": "snapshot", "data": store.snapshot()})
        await asyncio.sleep(config.TICK_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulator_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Office Energy Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------- REST API
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/devices")
def get_devices():
    """Full live snapshot: devices, totals, alerts, times."""
    return store.snapshot()


@app.get("/api/rooms/{room_id}")
def get_room(room_id: str):
    if room_id not in config.ROOMS:
        raise HTTPException(status_code=404, detail="Unknown room")
    return store.room_snapshot(room_id)


@app.get("/api/usage")
def get_usage():
    return store.snapshot()["totals"]


@app.get("/api/alerts")
def get_alerts():
    return {"alerts": store.snapshot()["alerts"]}


# ------------------------------------------------------------------ WebSocket
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    # Send one snapshot immediately so the UI paints without waiting a tick.
    await ws.send_json({"type": "snapshot", "data": store.snapshot()})
    try:
        while True:
            # We don't need client messages; this just keeps the socket open.
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)
