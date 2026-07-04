// Work Room 1 — state-sensing demo (2 fans + 3 lights + 1 current sensor)
// ESP32 only OBSERVES: every device line is an INPUT.
#define FAN1_PIN    32
#define FAN2_PIN    33
#define LIGHT1_PIN  25
#define LIGHT2_PIN  26
#define LIGHT3_PIN  27
#define CURRENT_PIN 34   // input-only, ADC1 — safe with Wi-Fi

void setup() {
  Serial.begin(115200);
  // INPUT_PULLDOWN: reads a clean OFF when the switch does not drive the pin.
  pinMode(FAN1_PIN,   INPUT_PULLDOWN);
  pinMode(FAN2_PIN,   INPUT_PULLDOWN);
  pinMode(LIGHT1_PIN, INPUT_PULLDOWN);
  pinMode(LIGHT2_PIN, INPUT_PULLDOWN);
  pinMode(LIGHT3_PIN, INPUT_PULLDOWN);
  // GPIO34 is analog input — no pinMode needed.
}

void loop() {
  Serial.println("=== Work Room 1 Status ===");
  Serial.printf("Fan 1:   %s\n", digitalRead(FAN1_PIN)   ? "ON" : "OFF");
  Serial.printf("Fan 2:   %s\n", digitalRead(FAN2_PIN)   ? "ON" : "OFF");
  Serial.printf("Light 1: %s\n", digitalRead(LIGHT1_PIN) ? "ON" : "OFF");
  Serial.printf("Light 2: %s\n", digitalRead(LIGHT2_PIN) ? "ON" : "OFF");
  Serial.printf("Light 3: %s\n", digitalRead(LIGHT3_PIN) ? "ON" : "OFF");

  int raw = analogRead(CURRENT_PIN);        // 0..4095
  float current = (raw / 4095.0) * 30.0;    // ACS712-30A range
  Serial.printf("Current: %.2f A\n", current);
  Serial.println("--------------------------\n");

  delay(1000);
}
