/*
=========================================================
Smart Footwear for Ulcer Risk Prediction
ESP32 Sensor Firmware
=========================================================

Reads:
- 4 × FSR pressure sensors
- 1 × DS18B20 temperature sensor

Every 5 seconds, the sensor values are averaged and sent
to the FastAPI backend over HTTPS.

Backend:
https://iot-enabled-smart-footwear-for-ulcer.onrender.com/log

Serial Monitor:
115200 baud
=========================================================
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ==========================
// WiFi Configuration
// ==========================
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ==========================
// Render FastAPI Endpoint
// ==========================
const char* serverUrl =
  "https://iot-enabled-smart-footwear-for-ulcer.onrender.com/log";

// ==========================
// Pin Configuration
// ==========================
#define FSR1_PIN 34
#define FSR2_PIN 35
#define FSR3_PIN 32
#define FSR4_PIN 33
#define ONE_WIRE_BUS 4

// ==========================
// Temperature Sensor
// ==========================
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensors(&oneWire);

// ==========================
// Sampling Variables
// ==========================
unsigned long startTime = 0;

int sensorSampleCount = 0;
int tempSampleCount = 0;

float sumFSR1 = 0;
float sumFSR2 = 0;
float sumFSR3 = 0;
float sumFSR4 = 0;
float sumTemp = 0;

// ==========================
// Setup
// ==========================
void setup() {

  Serial.begin(115200);

  tempSensors.begin();

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  unsigned long wifiStart = millis();

  while (WiFi.status() != WL_CONNECTED &&
         millis() - wifiStart < 30000) {

    delay(500);
    Serial.print(".");
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {

    Serial.println("WiFi Connected");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

  } else {

    Serial.println("WiFi connection timeout");
  }

  startTime = millis();
}

// ==========================
// Main Loop
// ==========================
void loop() {

  // Reconnect WiFi if disconnected
  if (WiFi.status() != WL_CONNECTED) {

    Serial.println("WiFi disconnected. Reconnecting...");
    WiFi.reconnect();

    delay(1000);
    return;
  }

  // ==========================
  // Read FSR Sensors
  // ==========================
  sumFSR1 += analogRead(FSR1_PIN);
  sumFSR2 += analogRead(FSR2_PIN);
  sumFSR3 += analogRead(FSR3_PIN);
  sumFSR4 += analogRead(FSR4_PIN);

  sensorSampleCount++;

  // ==========================
  // Read DS18B20
  // ==========================
  tempSensors.requestTemperatures();

  float temperature = tempSensors.getTempCByIndex(0);

  if (temperature != DEVICE_DISCONNECTED_C) {

    sumTemp += temperature;
    tempSampleCount++;

  } else {

    Serial.println("Temperature sensor disconnected");
  }

  // ==========================
  // Send Every 5 Seconds
  // ==========================
  if (millis() - startTime >= 5000 &&
      sensorSampleCount > 0 &&
      tempSampleCount > 0) {

    float avgFSR1 = sumFSR1 / sensorSampleCount;
    float avgFSR2 = sumFSR2 / sensorSampleCount;
    float avgFSR3 = sumFSR3 / sensorSampleCount;
    float avgFSR4 = sumFSR4 / sensorSampleCount;
    float avgTemp = sumTemp / tempSampleCount;

    Serial.println();
    Serial.println("==============================");
    Serial.println("Sending Sensor Data");
    Serial.println("==============================");

    Serial.printf("FSR1 : %.2f\n", avgFSR1);
    Serial.printf("FSR2 : %.2f\n", avgFSR2);
    Serial.printf("FSR3 : %.2f\n", avgFSR3);
    Serial.printf("FSR4 : %.2f\n", avgFSR4);
    Serial.printf("TEMP : %.2f C\n", avgTemp);

    sendData(
      avgFSR1,
      avgFSR2,
      avgFSR3,
      avgFSR4,
      avgTemp
    );

    // Reset accumulators
    sumFSR1 = 0;
    sumFSR2 = 0;
    sumFSR3 = 0;
    sumFSR4 = 0;
    sumTemp = 0;

    sensorSampleCount = 0;
    tempSampleCount = 0;

    startTime = millis();
  }

  delay(100);
}

// ==========================
// Send Data to Render
// ==========================
void sendData(
  float f1,
  float f2,
  float f3,
  float f4,
  float temp
) {

  if (WiFi.status() != WL_CONNECTED) {

    Serial.println("WiFi disconnected. Data not sent");
    return;
  }

  WiFiClientSecure client;

  // Render uses HTTPS.
  // setInsecure() skips certificate verification.
  client.setInsecure();

  HTTPClient http;

  http.setTimeout(30000);

  if (!http.begin(client, serverUrl)) {

    Serial.println("HTTP connection setup failed");
    return;
  }

  http.addHeader("Content-Type", "application/json");

  // ==========================
  // Create JSON
  // ==========================
  StaticJsonDocument<256> doc;

  doc["scenario"] = "Walking";
  doc["fsr1"] = f1;
  doc["fsr2"] = f2;
  doc["fsr3"] = f3;
  doc["fsr4"] = f4;
  doc["temp1"] = temp;

  String jsonData;
  serializeJson(doc, jsonData);

  Serial.println();
  Serial.println("JSON Sent:");
  Serial.println(jsonData);

  // ==========================
  // HTTP POST
  // ==========================
  int httpResponseCode = http.POST(jsonData);

  Serial.print("HTTP Response Code: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) {

    String response = http.getString();

    Serial.println("Server Response:");
    Serial.println(response);

  } else {

    Serial.print("POST Failed: ");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();
}
