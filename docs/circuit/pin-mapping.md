# ESP32 Pin Mapping — One Representative Room

Room modelled: **Work Room 1** (2 fans + 3 lights = 5 devices). The same pattern
repeats per room in a real build.

## Design intent

- Each device's ON/OFF state is read by the ESP32 on a **digital input** pin.
- One shared **current sensor** (ACS712) on the room's live line gives a real
  current reading, which validates the per-device wattages the backend assumes
  (fan ≈ 60 W, light ≈ 15 W).
- Loads are represented in simulation by LEDs (lights) and a small DC motor
  (fan) switched via transistors/relays.

## Pin mapping table

| ESP32 Pin | Direction | Connected to | Purpose |
|---|---|---|---|
| GPIO 32 | Digital input | Fan 1 state line | Read Fan 1 ON/OFF |
| GPIO 33 | Digital input | Fan 2 state line | Read Fan 2 ON/OFF |
| GPIO 25 | Digital input | Light 1 state line | Read Light 1 ON/OFF |
| GPIO 26 | Digital input | Light 2 state line | Read Light 2 ON/OFF |
| GPIO 27 | Digital input | Light 3 state line | Read Light 3 ON/OFF |
| GPIO 34 | Analog input (ADC1) | ACS712 OUT | Sense room current draw |
| 3V3 | Power | Sensor VCC, pull-down network | Logic + sensor supply |
| GND | Ground | Common ground rail | Shared reference |

> Notes: GPIO 34 is **input-only** and on ADC1 — safe to use for analog reads
> while Wi‑Fi is active (ADC2 conflicts with Wi‑Fi on the ESP32). GPIO 32/33/25/
> 26/27 are general-purpose digital pins with no boot-strapping caveats.

## Connection list

- **State-sense inputs (×5):** each device's switched line → a voltage divider
  (e.g. 10 kΩ / 10 kΩ) → ESP32 GPIO, so the pin sees a safe 0/3.3 V logic level.
  Add a **10 kΩ pull-down** on each input so a floating line reads a clean OFF.
- **Current sensor:** ACS712 in series with the room's live conductor;
  `OUT → GPIO 34`, `VCC → 3V3`, `GND → GND`.
- **Loads (simulation):** LEDs (with 220 Ω resistors) for lights; a DC motor via
  a transistor/relay for each fan. Each load shares the **common ground**.
- **Common ground:** the ESP32, sensor, and all load-return lines tie to one GND
  rail — without a shared ground the digital reads are meaningless.

## Electrical reasoning

- **Inputs vs outputs:** the microcontroller only *observes* here, so every
  device line is an **input**. Sensing (not switching) matches the brief.
- **Voltage safety:** ESP32 GPIO is 3.3 V tolerant; the divider + pull-down keep
  every input inside 0–3.3 V and define a deterministic OFF state.
- **Why one current sensor:** total room current is enough to cross-check the
  modelled wattage; per-device sensing would need 5 sensors and adds no value to
  a concept demo.
- **Debouncing:** mechanical switches bounce — debounce in firmware (e.g. read
  twice ~20 ms apart) rather than adding hardware.

## Firmware sketch (pseudocode, for the write-up)

```
setup():
  for pin in [32, 33, 25, 26, 27]: pinMode(pin, INPUT_PULLDOWN)
  # GPIO 34 is analog input, no pinMode needed

loop():
  states = { device: digitalRead(pin) for each device }
  current_A = read_acs712(GPIO34)
  publish(states, current_A)   # e.g. over Wi-Fi to the backend
  delay(1000)
```
