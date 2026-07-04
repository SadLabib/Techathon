# Hardware / Electrical Schematic

Deliverable #2 (15%). A **concept simulation** in [Wokwi](https://wokwi.com) or
[Tinkercad](https://www.tinkercad.com) — no real hardware. Wire **one
representative room** (2 fans + 3 lights), not all 15 devices; the design just
has to make physical sense.

**▶ Live Wokwi simulation:** <https://wokwi.com/projects/468643690609206273>
Open it in a browser — no setup needed. Toggle the switches to flip each
fan/light and turn the potentiometer to change the simulated current reading.

## What's in this folder

- `diagram.json` — the Wokwi circuit (ESP32 + LEDs + switches + potentiometer),
  matching `pin-mapping.md`
- `pin-mapping.md` — the ESP32 pin table, connection list, and electrical
  reasoning
- `src/sketch.ino` — the firmware that reads device state + current draw
- `platformio.ini` / `wokwi.toml` — build config so the circuit can be
  simulated straight from VS Code (see below)

## Run the simulation in VS Code

1. Install two VS Code extensions: **Wokwi Simulator**
   (`Wokwi.wokwi-vscode`) and **PlatformIO IDE** (`platformio.platformio-ide`).
2. Activate the free Wokwi license once: Command Palette →
   `Wokwi: Request a New License`, follow the browser prompt, then
   `Wokwi: Enter a License Key` and paste it back in VS Code.
3. Open this folder (`docs/circuit/`) in VS Code — PlatformIO needs
   `platformio.ini` at the workspace root, so open `docs/circuit` itself, not
   the whole repo.
4. Build the firmware: click the PlatformIO checkmark in the status bar (or
   run `pio run` in a terminal here). This compiles `src/sketch.ino` to
   `.pio/build/esp32dev/firmware.bin`, which `wokwi.toml` points at.
5. Start the simulation: Command Palette → `Wokwi: Start Simulator` (or the
   play icon that appears once `wokwi.toml` is detected).
6. Interact: toggle the slide switches to flip each fan/light input, turn the
   potentiometer to change the simulated current reading, and watch the
   Serial Monitor (auto-opens) print the room status once per second, exactly
   as `src/sketch.ino` implements it.

Rebuild (step 4) after any firmware edit, then restart the simulator to pick
up the new `.bin`.

## Concept

An **ESP32** reads the ON/OFF state of each device via a GPIO input, and senses
current draw on one channel with a current sensor (ACS712 / INA219) to justify
the wattage numbers used by the backend. The devices themselves are represented
by switches/relays driving LED (light) and DC-motor (fan) loads.
