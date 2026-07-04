"""The single source of truth: the in-memory store + the device simulator.

Both the web dashboard (via WebSocket/REST) and the Discord bot read from one
`Store` instance, so the two interfaces can never disagree.
"""
import random
import uuid
from datetime import datetime, timezone

from . import config


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SimClock:
    """A fake wall clock that ticks faster than real time for the demo."""

    def __init__(self, start_hour: int):
        self.minutes = start_hour * 60

    def advance(self, delta: int) -> bool:
        """Advance the clock; return True if it rolled past midnight."""
        prev = self.minutes
        self.minutes = (self.minutes + delta) % (24 * 60)
        return self.minutes < prev

    @property
    def hour(self) -> int:
        return self.minutes // 60

    @property
    def label(self) -> str:
        return f"{self.minutes // 60:02d}:{self.minutes % 60:02d}"


def build_devices() -> list[dict]:
    """Create every device as a plain dict. 'status' is the whole state."""
    devices: list[dict] = []
    for room in config.ROOMS:
        for i in range(1, config.FANS_PER_ROOM + 1):
            devices.append(_make_device(room, "fan", i))
        for i in range(1, config.LIGHTS_PER_ROOM + 1):
            devices.append(_make_device(room, "light", i))
    return devices


def _make_device(room: str, dtype: str, index: int) -> dict:
    label = f"{'Fan' if dtype == 'fan' else 'Light'} {index}"
    return {
        "id": f"{room}-{dtype}-{index}",
        "label": label,
        "type": dtype,
        "room": room,
        "status": "off",
        "powerW": 0,
        "lastChanged": now_iso(),
    }


class Store:
    def __init__(self):
        random.seed(42)  # reproducible demos
        self.devices = build_devices()
        self.clock = SimClock(config.SIM_START_HOUR)
        self.alerts: list[dict] = []          # newest first
        self.energy_kwh = 0.0                  # accumulates over the sim-day
        self._active_alert_keys: set[str] = set()
        self._room_all_on_since: dict[str, int | None] = {r: None for r in config.ROOMS}
        self._seed_initial()

    def _seed_initial(self):
        """Start the day with the work rooms already busy."""
        for d in self.devices:
            if d["room"] != "drawing":
                self._set(d, True)

    def _set(self, device: dict, on: bool):
        new_status = "on" if on else "off"
        if device["status"] != new_status:
            device["status"] = new_status
            device["powerW"] = config.RATINGS[device["type"]] if on else 0
            device["lastChanged"] = now_iso()

    # ------------------------------------------------------------------ tick
    def tick(self):
        """One simulation step: advance clock, flip devices, score alerts."""
        rolled = self.clock.advance(config.SIM_MINUTES_PER_TICK)
        if rolled:                       # new day -> reset daily counters
            self.energy_kwh = 0.0
            self._active_alert_keys.clear()
        self._simulate_devices()
        self._accumulate_energy()
        self._evaluate_alerts()

    def _simulate_devices(self):
        """Bias behaviour by time of day so the data looks believable."""
        hour = self.clock.hour
        office = config.OFFICE_START_HOUR <= hour < config.OFFICE_END_HOUR
        for d in self.devices:
            if office:
                on_bias = 0.9 if d["room"] != "drawing" else 0.4
            else:
                on_bias = 0.1  # a few "forgotten" devices linger -> alerts
            if random.random() < 0.25:  # this device reconsiders its state
                self._set(d, random.random() < on_bias)

    def _accumulate_energy(self):
        total_w = sum(d["powerW"] for d in self.devices)
        sim_hours = config.SIM_MINUTES_PER_TICK / 60.0
        self.energy_kwh += (total_w * sim_hours) / 1000.0

    # ---------------------------------------------------------------- alerts
    def _add_alert(self, key: str, severity: str, message: str, room: str | None = None):
        if key in self._active_alert_keys:
            return
        self._active_alert_keys.add(key)
        self.alerts.insert(0, {
            "id": str(uuid.uuid4()),
            "severity": severity,
            "message": message,
            "room": room,
            "createdAt": now_iso(),
            "simTime": self.clock.label,
        })
        self.alerts = self.alerts[:50]

    def _evaluate_alerts(self):
        hour = self.clock.hour
        office = config.OFFICE_START_HOUR <= hour < config.OFFICE_END_HOUR
        for room in config.ROOMS:
            room_devices = [d for d in self.devices if d["room"] == room]
            on_devices = [d for d in room_devices if d["status"] == "on"]
            all_on = len(on_devices) == len(room_devices)

            # Rule: every device in a room ON continuously for > 2 hours.
            if all_on:
                if self._room_all_on_since[room] is None:
                    self._room_all_on_since[room] = self.clock.minutes
                else:
                    duration = self.clock.minutes - self._room_all_on_since[room]
                    if duration < 0:
                        duration += 24 * 60
                    if duration >= config.CONTINUOUS_ON_ALERT_MINUTES:
                        self._add_alert(
                            f"2h:{room}", "warning",
                            f"{config.ROOM_NAMES[room]} has had all devices ON "
                            f"for over 2 hours straight.",
                            room,
                        )
            else:
                self._room_all_on_since[room] = None

            # Rule: devices left on after office hours (9 AM - 5 PM).
            if not office and on_devices:
                fans = sum(1 for d in on_devices if d["type"] == "fan")
                lights = sum(1 for d in on_devices if d["type"] == "light")
                self._add_alert(
                    f"afterhours:{room}", "warning",
                    f"{config.ROOM_NAMES[room]} still has {fans} fan(s) and "
                    f"{lights} light(s) ON at {self.clock.label}. "
                    f"Did someone forget to leave?",
                    room,
                )

    # ------------------------------------------------------------- snapshots
    def snapshot(self) -> dict:
        per_room = {r: 0 for r in config.ROOMS}
        total = 0
        for d in self.devices:
            per_room[d["room"]] += d["powerW"]
            total += d["powerW"]
        return {
            "devices": self.devices,
            "totals": {
                "totalPowerW": total,
                "perRoomW": per_room,
                "estimatedKWhToday": round(self.energy_kwh, 2),
            },
            "alerts": self.alerts,
            "serverTime": now_iso(),
            "simTime": self.clock.label,
        }

    def room_snapshot(self, room: str) -> dict:
        room_devices = [d for d in self.devices if d["room"] == room]
        return {
            "room": room,
            "roomName": config.ROOM_NAMES[room],
            "devices": room_devices,
            "powerW": sum(d["powerW"] for d in room_devices),
            "simTime": self.clock.label,
        }
