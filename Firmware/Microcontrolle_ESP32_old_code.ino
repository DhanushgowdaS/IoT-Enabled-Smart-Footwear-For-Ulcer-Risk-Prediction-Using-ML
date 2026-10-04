#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:8000/log";

int sampleCount = 0;
float sumFSR1 = 0, sumFSR2 = 0, sumFSR3 = 0, sumFSR4 = 0, sumTemp1 = 0;
unsigned long startTime = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("
WiFi Connected");
  startTime = millis();
}

void loop() {
  sumFSR1 += analogRead(34);
  sumFSR2 += analogRead(36);
  sumFSR3 += analogRead(32);
  sumFSR4 += analogRead(33);
  sumTemp1 += 29.25;
  sampleCount++;

  if (millis() - startTime >= 10000) {
    sendData(
      sumFSR1 / sampleCount,
      sumFSR2 / sampleCount,
      sumFSR3 / sampleCount,
      sumFSR4 / sampleCount,
      sumTemp1 / sampleCount
    );

    sumFSR1 = sumFSR2 = sumFSR3 = sumFSR4 = sumTemp1 = 0;
    sampleCount = 0;
    startTime = millis();
  }

  delay(100);
}

void sendData(float f1, float f2, float f3, float f4, float t1) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["fsr1"] = f1;
  doc["fsr2"] = f2;
  doc["fsr3"] = f3;
  doc["fsr4"] = f4;
  doc["temp1"] = t1;

  String json;
  serializeJson(doc, json);

  int code = http.POST(json);
  Serial.print("HTTP: ");
  Serial.println(code);
  if (code > 0) Serial.println(http.getString());

  http.end();
}
