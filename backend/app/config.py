"""Central configuration. Change these to reshape the office or the simulation."""
import os

# --- Office layout ---------------------------------------------------------
ROOMS = ["drawing", "work1", "work2"]
ROOM_NAMES = {
    "drawing": "Drawing Room",
    "work1": "Work Room 1",
    "work2": "Work Room 2",
}

# Device count is config-driven. Default = 2 fans + 3 lights per room = 15 total
# (the math-consistent reading of the spec). Bump these to change the count.
FANS_PER_ROOM = int(os.getenv("FANS_PER_ROOM", "2"))
LIGHTS_PER_ROOM = int(os.getenv("LIGHTS_PER_ROOM", "3"))

# Realistic wattage when a device is ON (0 when off).
RATINGS = {"fan": 60, "light": 15}

# --- Simulation clock ------------------------------------------------------
# The simulator runs on a real timer (TICK_SECONDS) but advances a fake
# "office clock" faster than real time, so a full day passes in a couple of
# minutes for the demo (and after-hours alerts can fire on camera).
TICK_SECONDS = float(os.getenv("TICK_SECONDS", "2.0"))
SIM_MINUTES_PER_TICK = int(os.getenv("SIM_MINUTES_PER_TICK", "20"))
SIM_START_HOUR = int(os.getenv("SIM_START_HOUR", "8"))

# --- Alert rules -----------------------------------------------------------
OFFICE_START_HOUR = 9   # 9 AM
OFFICE_END_HOUR = 17    # 5 PM
CONTINUOUS_ON_ALERT_MINUTES = 120  # a room fully ON longer than this -> alert
