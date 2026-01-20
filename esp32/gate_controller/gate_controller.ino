/*
  Flight Kiosk Gate Controller
  **ESP8266 / ESP32 Universal Version**

  Logic: ACTIVE LOW (Because your LED is ON when it should be OFF)
  - LOW  = LED ON
  - HIGH = LED OFF
*/

#include <Arduino.h>

// ==================== Configuration ====================
// ESP8266 Built-in LED is usually on GPIO 2
#define LED_PIN 2

// Gate simulation
bool gateIsOpen = false;
unsigned long gateOpenTime = 0;
const unsigned long GATE_DURATION = 3000;

void setup() {
  Serial.begin(9600);
  Serial.println("\n=== Flight Kiosk Gate Controller ===");

  pinMode(LED_PIN, OUTPUT);

  // STARTUP: Turn LED OFF
  // Since your board is Active Low, we must write HIGH to turn it OFF.
  digitalWrite(LED_PIN, HIGH);

  Serial.println("Ready. Commands: OPEN_GATE, LED_BLUE, LED_RED, LED_GREEN");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();
    if (cmd.length() > 0)
      processCommand(cmd);
  }

  if (gateIsOpen && (millis() - gateOpenTime > GATE_DURATION)) {
    closeGate();
  }
  delay(10);
}

void processCommand(String cmd) {
  Serial.print("CMD: ");
  Serial.println(cmd);

  if (cmd == "OPEN_GATE")
    openGate();
  else if (cmd == "CLOSE_GATE")
    closeGate();
  else if (cmd == "LED_BLUE")
    ledBlue();
  else if (cmd == "LED_RED")
    ledRed();
  else if (cmd == "LED_GREEN")
    ledGreen();
  else if (cmd == "LED_OFF")
    ledOff();
  else if (cmd == "STATUS")
    Serial.println("Status: Online");
}

void openGate() {
  Serial.println("Gate: OPENING (Simulated)");
  gateIsOpen = true;
  gateOpenTime = millis();
}

void closeGate() {
  Serial.println("Gate: CLOSING (Simulated)");
  gateIsOpen = false;
}

// ==================== LED LOGIC ====================
// REMEMBER: LOW = ON, HIGH = OFF for your board

void ledBlue() {
  // Scanning: Turn ON
  digitalWrite(LED_PIN, LOW); // LOW is ON
  Serial.println("LED: Blue (Scanning) ON");
}

void ledRed() {
  // Error: Fast Blinks
  Serial.println("LED: Red Sequence");
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PIN, LOW); // ON
    delay(100);
    digitalWrite(LED_PIN, HIGH); // OFF
    delay(100);
  }
}

void ledGreen() {
  // Success: Slow Blinks
  Serial.println("LED: Green Sequence");
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, LOW); // ON
    delay(500);
    digitalWrite(LED_PIN, HIGH); // OFF
    delay(200);
  }
}

void ledOff() {
  // Turn OFF
  digitalWrite(LED_PIN, HIGH); // HIGH is OFF
  Serial.println("LED: All OFF");
}
