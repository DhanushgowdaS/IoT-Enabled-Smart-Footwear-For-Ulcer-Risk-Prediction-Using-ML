#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:8000/log";

#define FSR1_PIN 34
#define FSR2_PIN 36
#define FSR3_PIN 32
#define FSR4_PIN 33
#define ONE_WIRE_BUS 4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensors(&oneWire);

unsigned long startTime = 0;
int sampleCount = 0;
float sumFSR1 = 0, sumFSR2 = 0, sumFSR3 = 0, sumFSR4 = 0, sumTemp = 0;

void setup() {
  Serial.begin(115200);
  tempSensors.begin();
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected");
  startTime = millis();
}

void loop() {
  sumFSR1 += analogRead(FSR1_PIN);
  sumFSR2 += analogRead(FSR2_PIN);
  sumFSR3 += analogRead(FSR3_PIN);
  sumFSR4 += analogRead(FSR4_PIN);

  tempSensors.requestTemperatures();
  float temperature = tempSensors.getTempCByIndex(0);

  if (temperature != DEVICE_DISCONNECTED_C) {
    sumTemp += temperature;
    sampleCount++;
  }

  if (millis() - startTime >= 10000 && sampleCount > 0) {
    sendData(
      sumFSR1 / sampleCount,
      sumFSR2 / sampleCount,
      sumFSR3 / sampleCount,
      sumFSR4 / sampleCount,
      sumTemp / sampleCount
    );

    sumFSR1 = sumFSR2 = sumFSR3 = sumFSR4 = sumTemp = 0;
    sampleCount = 0;
    startTime = millis();
  }

  delay(100);
}

void sendData(float f1, float f2, float f3, float f4, float temp) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> doc;
  doc["scenario"] = "Walking";
  doc["fsr1"] = f1;
  doc["fsr2"] = f2;
  doc["fsr3"] = f3;
  doc["fsr4"] = f4;
  doc["temp1"] = temp;

  String body;
  serializeJson(doc, body);
  int code = http.POST(body);

  Serial.print("HTTP: ");
  Serial.println(code);
  if (code > 0) Serial.println(http.getString());

  http.end();
}
