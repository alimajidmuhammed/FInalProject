/*
  Flight Kiosk Gate Controller - ESP32-S3 Firmware
  
  Controls:
  - Servo motor for gate opening
  - Green LED (success indicator)
  - Red LED (error indicator)
  - Buzzer for audio feedback
  
  Communication:
  - WiFi with MQTT for wireless control
  - USB Serial as fallback
  
  Commands:
  - OPEN_GATE: Opens the gate for 3 seconds
  - CLOSE_GATE: Forces gate closed
  - LED_GREEN: Turn on green LED
  - LED_RED: Turn on red LED
  - LED_OFF: Turn off all LEDs
  - BUZZER_SUCCESS: Play success tone
  - BUZZER_ERROR: Play error tone
  - STATUS: Report current status
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>

// ==================== Configuration ====================

// WiFi credentials - UPDATE THESE
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT broker - UPDATE THIS
const char* MQTT_BROKER = "192.168.1.100";  // Your MQTT broker IP
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "flight_kiosk_gate";
const char* MQTT_TOPIC_GATE = "kiosk/gate";
const char* MQTT_TOPIC_STATUS = "kiosk/status";

// Pin definitions - Adjust for your wiring
#define SERVO_PIN       4
#define LED_GREEN_PIN   5
#define LED_RED_PIN     6
#define BUZZER_PIN      7

// Servo positions
#define GATE_CLOSED     0
#define GATE_OPEN       90

// Gate open duration (ms)
#define GATE_OPEN_TIME  3000

// ==================== Global Objects ====================

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
Servo gateServo;

bool gateIsOpen = false;
unsigned long gateOpenTime = 0;

// ==================== Setup ====================

void setup() {
  Serial.begin(9600);
  Serial.println("\n=== Flight Kiosk Gate Controller ===");
  
  // Initialize pins
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize servo
  gateServo.attach(SERVO_PIN);
  gateServo.write(GATE_CLOSED);
  
  // Initial state - all off
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Connect WiFi
  setupWiFi();
  
  // Setup MQTT
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  
  Serial.println("Setup complete. Waiting for commands...");
  Serial.println("Commands: OPEN_GATE, LED_GREEN, LED_RED, LED_OFF, BUZZER_SUCCESS, BUZZER_ERROR, STATUS");
}

void setupWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed. Using Serial only.");
  }
}

void reconnectMQTT() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  if (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT...");
    
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println("connected!");
      mqttClient.subscribe(MQTT_TOPIC_GATE);
      
      // Publish online status
      mqttClient.publish(MQTT_TOPIC_STATUS, "{\"status\":\"online\"}");
    } else {
      Serial.print("failed, rc=");
      Serial.println(mqttClient.state());
    }
  }
}

// ==================== MQTT Callback ====================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Parse JSON payload
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.c_str());
    return;
  }
  
  const char* command = doc["command"];
  if (command) {
    processCommand(String(command));
  }
}

// ==================== Command Processing ====================

void processCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  
  Serial.print("Command: ");
  Serial.println(cmd);
  
  if (cmd == "OPEN_GATE") {
    openGate();
  }
  else if (cmd == "CLOSE_GATE") {
    closeGate();
  }
  else if (cmd == "LED_GREEN") {
    ledGreen();
  }
  else if (cmd == "LED_RED") {
    ledRed();
  }
  else if (cmd == "LED_OFF") {
    ledOff();
  }
  else if (cmd == "BUZZER_SUCCESS") {
    buzzerSuccess();
  }
  else if (cmd == "BUZZER_ERROR") {
    buzzerError();
  }
  else if (cmd == "STATUS") {
    reportStatus();
  }
  else {
    Serial.println("Unknown command: " + cmd);
  }
}

// ==================== Gate Control ====================

void openGate() {
  Serial.println("Opening gate...");
  gateServo.write(GATE_OPEN);
  gateIsOpen = true;
  gateOpenTime = millis();
  
  // Publish status
  publishStatus("gate_opened");
}

void closeGate() {
  Serial.println("Closing gate...");
  gateServo.write(GATE_CLOSED);
  gateIsOpen = false;
  
  // Publish status
  publishStatus("gate_closed");
}

// ==================== LED Control ====================

void ledGreen() {
  digitalWrite(LED_GREEN_PIN, HIGH);
  digitalWrite(LED_RED_PIN, LOW);
  Serial.println("LED: Green ON");
}

void ledRed() {
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_RED_PIN, HIGH);
  Serial.println("LED: Red ON");
}

void ledOff() {
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);
  Serial.println("LED: All OFF");
}

// ==================== Buzzer Control ====================

void buzzerSuccess() {
  // Play success melody
  Serial.println("Buzzer: Success tone");
  
  tone(BUZZER_PIN, 523, 100);  // C5
  delay(120);
  tone(BUZZER_PIN, 659, 100);  // E5
  delay(120);
  tone(BUZZER_PIN, 784, 150);  // G5
  delay(170);
  noTone(BUZZER_PIN);
}

void buzzerError() {
  // Play error sound
  Serial.println("Buzzer: Error tone");
  
  tone(BUZZER_PIN, 200, 200);
  delay(250);
  tone(BUZZER_PIN, 200, 200);
  delay(250);
  noTone(BUZZER_PIN);
}

// ==================== Status Reporting ====================

void reportStatus() {
  StaticJsonDocument<128> doc;
  doc["gate"] = gateIsOpen ? "open" : "closed";
  doc["wifi"] = WiFi.status() == WL_CONNECTED ? "connected" : "disconnected";
  doc["mqtt"] = mqttClient.connected() ? "connected" : "disconnected";
  
  char buffer[128];
  serializeJson(doc, buffer);
  
  Serial.println(buffer);
  
  if (mqttClient.connected()) {
    mqttClient.publish(MQTT_TOPIC_STATUS, buffer);
  }
}

void publishStatus(const char* status) {
  if (mqttClient.connected()) {
    StaticJsonDocument<64> doc;
    doc["status"] = status;
    
    char buffer[64];
    serializeJson(doc, buffer);
    mqttClient.publish(MQTT_TOPIC_STATUS, buffer);
  }
}

// ==================== Main Loop ====================

void loop() {
  // Handle MQTT
  if (WiFi.status() == WL_CONNECTED) {
    if (!mqttClient.connected()) {
      reconnectMQTT();
    }
    mqttClient.loop();
  }
  
  // Handle Serial commands
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    processCommand(cmd);
  }
  
  // Auto-close gate after timeout
  if (gateIsOpen && (millis() - gateOpenTime > GATE_OPEN_TIME)) {
    closeGate();
    ledOff();
  }
  
  delay(10);
}
