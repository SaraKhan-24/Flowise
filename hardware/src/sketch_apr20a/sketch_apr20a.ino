#define ENABLE_USER_AUTH
#define ENABLE_DATABASE

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <FirebaseClient.h>
#include "secrets.h"
#include "time.h"

// --- NTP CONFIGURATION ---
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 18000; // Pakistan is GMT+5 (5 * 3600)
const int   daylightOffset_sec = 0; // No DST in Pakistan

// ---------------- SENSORS ----------------
const int F1_PIN = 18;
const int F2_PIN = 19;
const int P1_PIN = 34;
const int P2_PIN = 35;

const uint32_t INTERVAL_MS = 1000;
const float FLOW_CAL = 7.5;
const float SPU_GAIN = 370.0;

// ---------------- STATE ----------------
volatile uint32_t pulse1 = 0, pulse2 = 0;
float baseP1 = 0.0, baseP2 = 0.0;
int currentLabel = 0;
uint32_t prevMs = 0;

// Write flow control
uint32_t lastWriteTime = 0;
const uint32_t WRITE_INTERVAL_MS = 2000;
bool writeInProgress = false;

const char* DEVICE_ID = "esp32_node_01";

// Updated for Formatted Time
struct SensorData {
  String timestamp; // Changed to String
  float p1_spu;
  float f1;
  float f2;
  float p2_spu;
  int label;
};

SensorData pendingData;
bool hasPendingData = false;

// ---------------- FIREBASE OBJECTS ----------------
void processData(AsyncResult &aResult);

UserAuth user_auth(Web_API_KEY, USER_EMAIL, USER_PASS);
FirebaseApp app;
WiFiClientSecure ssl_client;
using AsyncClient = AsyncClientClass;
AsyncClient aClient(ssl_client);
RealtimeDatabase Database;

// ---------------- ISR ----------------
void IRAM_ATTR count1() { pulse1++; }
void IRAM_ATTR count2() { pulse2++; }

// ---------------- HELPERS ----------------
void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting WiFi");
  uint8_t attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    Serial.print(".");
    delay(250);
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi OK. IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi failed.");
  }
}

void calibrateBaseline() {
  Serial.println("Calibrating baseline... KEEP PUMP OFF");
  delay(3000);

  uint32_t b1 = 0, b2 = 0;
  for (int i = 0; i < 250; i++) {
    b1 += analogRead(P1_PIN);
    b2 += analogRead(P2_PIN);
    delay(5);
  }

  baseP1 = (b1 / 250.0f / 4095.0f) * 3.3f;
  baseP2 = (b2 / 250.0f / 4095.0f) * 3.3f;
}

void setup() {
  Serial.begin(115200);

  pinMode(F1_PIN, INPUT_PULLUP);
  pinMode(F2_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(F1_PIN), count1, RISING);
  attachInterrupt(digitalPinToInterrupt(F2_PIN), count2, RISING);

  analogReadResolution(12);
  connectWiFi();

  // Initialize and Wait for NTP Sync
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.print("Waiting for NTP time sync");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\n✅ Time Synced!");

  ssl_client.setInsecure();
  ssl_client.setConnectionTimeout(1000);
  ssl_client.setHandshakeTimeout(5);

  initializeApp(aClient, app, getAuth(user_auth), processData, "authTask");
  app.getApp<RealtimeDatabase>(Database);
  Database.url(DATABASE_URL);

  calibrateBaseline();
}

void loop() {
  app.loop();

  if (Serial.available()) {
    char c = Serial.read();
    if (c == '1') currentLabel = 1;
    if (c == '0') currentLabel = 0;
  }

  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  uint32_t now = millis();
  if (now - prevMs < INTERVAL_MS) return;
  prevMs = now;

  noInterrupts();
  uint32_t p1Count = pulse1; uint32_t p2Count = pulse2;
  pulse1 = 0; pulse2 = 0;
  interrupts();

  float f1 = p1Count / FLOW_CAL;
  float f2 = p2Count / FLOW_CAL;

  uint32_t p1raw = 0, p2raw = 0;
  for (int i = 0; i < 250; i++) {
    p1raw += analogRead(P1_PIN);
    p2raw += analogRead(P2_PIN);
  }
  float v1 = (p1raw / 250.0f / 4095.0f) * 3.3f;
  float v2 = (p2raw / 250.0f / 4095.0f) * 3.3f;
  float p1_spu = (v1 - baseP1) * SPU_GAIN;
  float p2_spu = (v2 - baseP2) * SPU_GAIN;

  // --- NEW FORMATTING LOGIC ---
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Time Error");
    return;
  }
    // Create the human-readable version for the data value
  char buf[25];
  strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &timeinfo);
  String formattedTime = String(buf);

  // Create a sanitized version for the Firebase PATH (Key)
  // Example: "2026-05-04_22-57-07"
  char pathBuf[25];
  strftime(pathBuf, sizeof(pathBuf), "%Y-%m-%d_%H-%M-%S", &timeinfo);
  String safePath = String(pathBuf);

  // Serial Print
  Serial.print(formattedTime); Serial.print(",");
  Serial.print(p1_spu, 3);    Serial.print(",");
  Serial.print(f1, 3);        Serial.print(",");
  Serial.print(f2, 3);        Serial.print(",");
  Serial.print(p2_spu, 3);    Serial.print(",");
  Serial.println(currentLabel);

  pendingData = {formattedTime, p1_spu, f1, f2, p2_spu, currentLabel};
  hasPendingData = true;

  // --- UPDATED FIREBASE WRITE ---
  if (now - lastWriteTime >= WRITE_INTERVAL_MS && hasPendingData) {
      String path = String("/sensor_readings/") + safePath;

      Database.set<String>(aClient, (path + "/timestamp").c_str(), formattedTime, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/p1_spu").c_str(), pendingData.p1_spu, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/f1_lmin").c_str(), pendingData.f1, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/f2_lmin").c_str(), pendingData.f2, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/p2_spu").c_str(), pendingData.p2_spu, nullptr, "writeTask");
      Database.set<int>(aClient, (path + "/label").c_str(), pendingData.label, nullptr, "writeTask");

      lastWriteTime = now;
      hasPendingData = false;
  }
}

void processData(AsyncResult &aResult) {
  if (!aResult.isResult()) return;
  if (aResult.isError()) {
    Serial.print("❌ Error: ");
    Serial.println(aResult.error().message().c_str());
  }
}