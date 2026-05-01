#define ENABLE_USER_AUTH
#define ENABLE_DATABASE

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <FirebaseClient.h>
#include "secrets.h"

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

// Sensor data structure
struct SensorData {
  uint32_t timestamp;
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
    Serial.println("WiFi failed (will retry in loop).");
  }
}

void calibrateBaseline() {
  Serial.println("Calibrating baseline... KEEP PUMP OFF FOR 3 SECONDS");
  delay(3000);

  uint32_t b1 = 0, b2 = 0;
  for (int i = 0; i < 250; i++) {
    b1 += analogRead(P1_PIN);
    b2 += analogRead(P2_PIN);
    delay(5);  // Longer wait between samples
  }

  baseP1 = (b1 / 250.0f / 4095.0f) * 3.3f;
  baseP2 = (b2 / 250.0f / 4095.0f) * 3.3f;

  Serial.print("Baseline P1="); Serial.print(baseP1, 4);
  Serial.print(" V, P2=");      Serial.print(baseP2, 4);
  Serial.println(" V");
}

void setup() {
  Serial.begin(115200);

  pinMode(F1_PIN, INPUT_PULLUP);
  pinMode(F2_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(F1_PIN), count1, RISING);
  attachInterrupt(digitalPinToInterrupt(F2_PIN), count2, RISING);

  analogReadResolution(12);

  connectWiFi();

  ssl_client.setInsecure();
  ssl_client.setConnectionTimeout(1000);
  ssl_client.setHandshakeTimeout(5);

  initializeApp(aClient, app, getAuth(user_auth), processData, "authTask");
  app.getApp<RealtimeDatabase>(Database);
  Database.url(DATABASE_URL);

  calibrateBaseline();

  Serial.println("✓ Ready! CSV order for ML:");
  Serial.println("timestamp,P1_SPU,F1_Lmin,F2_Lmin,P2_SPU,Label");
}

void loop() {
  app.loop();

  // Manual label from serial: send '1' for leak, '0' for normal
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '1') {
      currentLabel = 1;
      Serial.println("[LABEL] Changed to: LEAK (1)");
    }
    if (c == '0') {
      currentLabel = 0;
      Serial.println("[LABEL] Changed to: NORMAL (0)");
    }
  }

  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  uint32_t now = millis();
  if (now - prevMs < INTERVAL_MS) return;
  prevMs = now;

  // Snapshot pulse counts atomically
  noInterrupts();
  uint32_t p1Count = pulse1;
  uint32_t p2Count = pulse2;
  pulse1 = 0;
  pulse2 = 0;
  interrupts();

  // Flow (L/min)
  float f1 = p1Count / FLOW_CAL;
  float f2 = p2Count / FLOW_CAL;

  // Pressure oversampling (30x)
  uint32_t p1raw = 0, p2raw = 0;
  for (int i = 0; i < 250; i++) {
    p1raw += analogRead(P1_PIN);
    p2raw += analogRead(P2_PIN);
  }
  float v1 = (p1raw / 250.0f / 4095.0f) * 3.3f;
  float v2 = (p2raw / 250.0f / 4095.0f) * 3.3f;

  float p1_spu = (v1 - baseP1) * SPU_GAIN;
  float p2_spu = (v2 - baseP2) * SPU_GAIN;
  
  // Allow negative values - they show real pressure drift!
  // (Removed clamping to 0)

  // Local CSV print in exact ML order
  uint32_t tSec = now / 1000;
  Serial.print(tSec);         Serial.print(",");
  Serial.print(p1_spu, 3);    Serial.print(",");
  Serial.print(f1, 3);        Serial.print(",");
  Serial.print(f2, 3);        Serial.print(",");
  Serial.print(p2_spu, 3);    Serial.print(",");
  Serial.println(currentLabel);

  // Store data for Firebase write
  pendingData.timestamp = tSec;
  pendingData.p1_spu = p1_spu;
  pendingData.f1 = f1;
  pendingData.f2 = f2;
  pendingData.p2_spu = p2_spu;
  pendingData.label = currentLabel;
  hasPendingData = true;

  // ========== ATTEMPT FIREBASE WRITE ==========
  if (now - lastWriteTime >= WRITE_INTERVAL_MS && hasPendingData) {
      String path = String("/sensor_readings/") + String((int)pendingData.timestamp);

      // Write all fields
      Database.set<int>(aClient, (path + "/timestamp").c_str(), (int)pendingData.timestamp, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/p1_spu").c_str(), pendingData.p1_spu, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/f1_lmin").c_str(), pendingData.f1, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/f2_lmin").c_str(), pendingData.f2, nullptr, "writeTask");
      Database.set<float>(aClient, (path + "/p2_spu").c_str(), pendingData.p2_spu, nullptr, "writeTask");
      Database.set<int>(aClient, (path + "/label").c_str(), pendingData.label, nullptr, "writeTask");

      writeInProgress = true;
      lastWriteTime = now;
      Serial.print("✅ Data sent. Timestamp: ");
      Serial.println((int)pendingData.timestamp);
      
      hasPendingData = false;
  }
}

void processData(AsyncResult &aResult) {
  if (!aResult.isResult()) return;

  if (String(aResult.uid().c_str()) != "writeTask" && String(aResult.uid().c_str()) != "authTask") {
    return;
  }

  if (aResult.isError()) {
    Serial.print("❌ Error [");
    Serial.print(aResult.uid().c_str());
    Serial.print("]: ");
    Serial.println(aResult.error().message().c_str());
  } else {
    if (String(aResult.uid().c_str()) == "writeTask") {
      writeInProgress = false;
    }
  }
}
