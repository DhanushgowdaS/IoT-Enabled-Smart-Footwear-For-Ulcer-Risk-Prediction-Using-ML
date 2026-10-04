/*
=========================================================
Smart Footwear for Ulcer Risk Prediction
ESP32 Sensor Firmware
=========================================================

Reads:
- 4 × FSR pressure sensors
- 1 × DS18B20 temperature sensor

Every 10 seconds, exactly 10 one-second sensor samples are averaged and sent
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

const char* ssid = "Admin";
const char* password = "password";

const char* serverUrl =
  "https://iot-enabled-smart-footwear-for-ulcer.onrender.com/log";

#define FSR1_PIN 34
#define FSR2_PIN 35
#define FSR3_PIN 32
#define FSR4_PIN 33
#define ONE_WIRE_BUS 4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensors(&oneWire);

unsigned long startTime = 0;
unsigned long lastSampleTime = 0;

int sensorSampleCount = 0;
int tempSampleCount = 0;

float sumFSR1 = 0;
float sumFSR2 = 0;
float sumFSR3 = 0;
float sumFSR4 = 0;
float sumTemp = 0;

void setup() {

  Serial.begin(115200);

  tempSensors.begin();

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  unsigned long wifiStart = millis();

  while (
    WiFi.status() != WL_CONNECTED &&
    millis() - wifiStart < 30000
  ) {
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
  lastSampleTime = millis() - 1000;
}

void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    WiFi.reconnect();
    delay(1000);
    return;
  }

  if (millis() - lastSampleTime < 1000) {
    delay(20);
    return;
  }

  lastSampleTime = millis();

  sumFSR1 += analogRead(FSR1_PIN);
  sumFSR2 += analogRead(FSR2_PIN);
  sumFSR3 += analogRead(FSR3_PIN);
  sumFSR4 += analogRead(FSR4_PIN);

  sensorSampleCount++;

  tempSensors.requestTemperatures();

  float temperature =
    tempSensors.getTempCByIndex(0);

  if (temperature != DEVICE_DISCONNECTED_C) {
    sumTemp += temperature;
    tempSampleCount++;
  } else {
    Serial.println("Temperature sensor disconnected");
  }

  if (
    sensorSampleCount >= 10 &&
    tempSampleCount >= 10
  ) {

    float avgFSR1 =
      sumFSR1 / sensorSampleCount;

    float avgFSR2 =
      sumFSR2 / sensorSampleCount;

    float avgFSR3 =
      sumFSR3 / sensorSampleCount;

    float avgFSR4 =
      sumFSR4 / sensorSampleCount;

    float avgTemp =
      sumTemp / tempSampleCount;

    Serial.println();
    Serial.println("==============================");
    Serial.println("Sending Sensor Data");
    Serial.println("==============================");

    Serial.printf(
      "FSR1 : %.2f\n",
      avgFSR1
    );

    Serial.printf(
      "FSR2 : %.2f\n",
      avgFSR2
    );

    Serial.printf(
      "FSR3 : %.2f\n",
      avgFSR3
    );

    Serial.printf(
      "FSR4 : %.2f\n",
      avgFSR4
    );

    Serial.printf(
      "TEMP : %.2f C\n",
      avgTemp
    );

    sendData(
      avgFSR1,
      avgFSR2,
      avgFSR3,
      avgFSR4,
      avgTemp
    );

    sumFSR1 = 0;
    sumFSR2 = 0;
    sumFSR3 = 0;
    sumFSR4 = 0;
    sumTemp = 0;

    sensorSampleCount = 0;
    tempSampleCount = 0;

    startTime = millis();
    lastSampleTime = millis();
  }
}

void sendData(
  float f1,
  float f2,
  float f3,
  float f4,
  float temp
) {

  const int maxAttempts = 5;

  for (
    int attempt = 1;
    attempt <= maxAttempts;
    attempt++
  ) {

    if (WiFi.status() != WL_CONNECTED) {

      Serial.println(
        "WiFi disconnected. Reconnecting..."
      );

      WiFi.reconnect();

      unsigned long reconnectStart =
        millis();

      while (
        WiFi.status() != WL_CONNECTED &&
        millis() - reconnectStart < 10000
      ) {
        delay(250);
      }

      if (WiFi.status() != WL_CONNECTED) {

        Serial.println(
          "WiFi reconnection failed"
        );

        if (attempt < maxAttempts) {
          delay(3000);
          continue;
        }

        return;
      }
    }

    WiFiClientSecure client;
    client.setInsecure();

    HTTPClient http;
    http.setTimeout(8000);

    if (!http.begin(client, serverUrl)) {

      Serial.print(
        "HTTP connection setup failed - Attempt "
      );
      Serial.print(attempt);
      Serial.print("/");
      Serial.println(maxAttempts);

      if (attempt < maxAttempts) {
        delay(3000);
        continue;
      }

      return;
    }

    http.addHeader(
      "Content-Type",
      "application/json"
    );

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
    Serial.print(
      "JSON Sent (Attempt "
    );
    Serial.print(attempt);
    Serial.print("/");
    Serial.print(maxAttempts);
    Serial.println("):");
    Serial.println(jsonData);

    int httpResponseCode =
      http.POST(jsonData);

    Serial.print(
      "HTTP Response Code: "
    );
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {

      String response =
        http.getString();

      Serial.println("Server Response:");
      Serial.println(response);

      http.end();
      return;

    } else {

      Serial.print("POST Failed: ");
      Serial.println(
        http.errorToString(
          httpResponseCode
        )
      );
    }

    http.end();

    if (attempt < maxAttempts) {
      Serial.println(
        "Retrying in 3 seconds..."
      );
      delay(3000);
    }
  }

  Serial.println(
    "All POST attempts failed"
  );
}
