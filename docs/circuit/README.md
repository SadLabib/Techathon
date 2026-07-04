# Hardware / Electrical Schematic

Deliverable #2 (15%). A **concept simulation** in [Wokwi](https://wokwi.com) or
[Tinkercad](https://www.tinkercad.com) — no real hardware. Wire **one
representative room** (2 fans + 3 lights), not all 15 devices; the design just
has to make physical sense.

## What to put in this folder

- `wokwi-schematic.png` — screenshot of the working simulation
- `pin-mapping.md` — the ESP32 pin table, connection list, and electrical
  reasoning ([already drafted here](./pin-mapping.md))

Build the schematic yourself from `pin-mapping.md` (we intentionally don't
export a Wokwi project file — the mapping is the design).

## Concept

An **ESP32** reads the ON/OFF state of each device via a GPIO input, and senses
current draw on one channel with a current sensor (ACS712 / INA219) to justify
the wattage numbers used by the backend. The devices themselves are represented
by switches/relays driving LED (light) and DC-motor (fan) loads.
