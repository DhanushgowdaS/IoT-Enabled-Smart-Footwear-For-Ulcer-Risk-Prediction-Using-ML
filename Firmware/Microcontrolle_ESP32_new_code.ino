/*
=========================================================
Smart Footwear for Ulcer Risk Prediction
ESP32 Sensor Firmware
=========================================================

Reads:
- 4 × FSR pressure sensors
- 1 × DS18B20 temperature sensor

Every 10 seconds, exactly 10 complete one-second sensor samples
are averaged and sent to the FastAPI backend over HTTPS.

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

const int SAMPLES_PER_WINDOW = 10;
const unsigned long SAMPLE_INTERVAL_MS = 1000;
const int MAX_POST_ATTEMPTS = 5;
const unsigned long HTTP_TIMEOUT_MS = 15000;
const unsigned long RETRY_DELAY_MS = 3000;

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensors(&oneWire);

unsigned long lastSampleTime = 0;

int sampleCount = 0;

float sumFSR1 = 0;
float sumFSR2 = 0;
float sumFSR3 = 0;
float sumFSR4 = 0;
float sumTemp = 0;

void resetWindow() {
  sampleCount = 0;
  sumFSR1 = 0;
  sumFSR2 = 0;
  sumFSR3 = 0;
  sumFSR4 = 0;
  sumTemp = 0;
}

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

  resetWindow();
  lastSampleTime = millis() - SAMPLE_INTERVAL_MS;

  Serial.println();
  Serial.println("Starting 10-second sensor window...");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    WiFi.reconnect();
    delay(1000);
    return;
  }

  if (millis() - lastSampleTime < SAMPLE_INTERVAL_MS) {
    delay(20);
    return;
  }

  lastSampleTime = millis();

  tempSensors.requestTemperatures();

  float temperature =
    tempSensors.getTempCByIndex(0);

  if (temperature == DEVICE_DISCONNECTED_C) {
    Serial.println(
      "Temperature sensor disconnected - sample discarded"
    );
    return;
  }

  float fsr1 = analogRead(FSR1_PIN);
  float fsr2 = analogRead(FSR2_PIN);
  float fsr3 = analogRead(FSR3_PIN);
  float fsr4 = analogRead(FSR4_PIN);

  sumFSR1 += fsr1;
  sumFSR2 += fsr2;
  sumFSR3 += fsr3;
  sumFSR4 += fsr4;
  sumTemp += temperature;

  sampleCount++;

  Serial.printf(
    "Sample %d/%d collected | FSR1: %.0f | FSR2: %.0f | FSR3: %.0f | FSR4: %.0f | TEMP: %.2f C\n",
    sampleCount,
    SAMPLES_PER_WINDOW,
    fsr1,
    fsr2,
    fsr3,
    fsr4,
    temperature
  );

  if (sampleCount < SAMPLES_PER_WINDOW) {
    return;
  }

  float avgFSR1 =
    sumFSR1 / SAMPLES_PER_WINDOW;

  float avgFSR2 =
    sumFSR2 / SAMPLES_PER_WINDOW;

  float avgFSR3 =
    sumFSR3 / SAMPLES_PER_WINDOW;

  float avgFSR4 =
    sumFSR4 / SAMPLES_PER_WINDOW;

  float avgTemp =
    sumTemp / SAMPLES_PER_WINDOW;

  Serial.println();
  Serial.println("==============================");
  Serial.println("10 samples collected");
  Serial.println("Sending 10-second averaged data");
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

  resetWindow();

  lastSampleTime = millis();

  Serial.println();
  Serial.println("Starting next 10-second sensor window...");
  Serial.println();
}

void sendData(
  float f1,
  float f2,
  float f3,
  float f4,
  float temp
) {
  for (
    int attempt = 1;
    attempt <= MAX_POST_ATTEMPTS;
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

        if (attempt < MAX_POST_ATTEMPTS) {
          delay(RETRY_DELAY_MS);
          continue;
        }

        return;
      }
    }

    WiFiClientSecure client;
    client.setInsecure();

    HTTPClient http;
    http.setTimeout(HTTP_TIMEOUT_MS);

    if (!http.begin(client, serverUrl)) {
      Serial.print(
        "HTTP connection setup failed - Attempt "
      );
      Serial.print(attempt);
      Serial.print("/");
      Serial.println(MAX_POST_ATTEMPTS);

      if (attempt < MAX_POST_ATTEMPTS) {
        delay(RETRY_DELAY_MS);
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
    Serial.print("JSON Sent (Attempt ");
    Serial.print(attempt);
    Serial.print("/");
    Serial.print(MAX_POST_ATTEMPTS);
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

      if (
        httpResponseCode >= 200 &&
        httpResponseCode < 300
      ) {
        Serial.println("Data sent successfully.");
        return;
      }

      Serial.println(
        "Server returned a non-success response."
      );

    } else {
      Serial.print("POST Failed: ");
      Serial.println(
        http.errorToString(httpResponseCode)
      );
    }

    http.end();

    if (attempt < MAX_POST_ATTEMPTS) {
      Serial.println(
        "Retrying in 3 seconds..."
      );
      delay(RETRY_DELAY_MS);
    }
  }

  Serial.println(
    "All POST attempts failed"
  );
}
