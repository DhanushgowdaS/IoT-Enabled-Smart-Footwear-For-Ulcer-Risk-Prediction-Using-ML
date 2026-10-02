#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Preferences.h>

#define FSR1_PIN 34
#define FSR2_PIN 35
#define FSR3_PIN 32
#define FSR4_PIN 33
#define ONE_WIRE_BUS 4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
Preferences preferences;

const unsigned long SAMPLE_INTERVAL = 1000;

unsigned long lastSampleTime = 0;
unsigned long recordNo = 1;

String person = "Person1";
String scenario = "Standing";

float sumFSR1 = 0;
float sumFSR2 = 0;
float sumFSR3 = 0;
float sumFSR4 = 0;
float sumTemp = 0;
int sampleCount = 0;

void checkSerialCommands() {
  if (!Serial.available()) return;

  String command = Serial.readStringUntil('\n');
  command.trim();

  if (command.startsWith("PERSON=")) {
    person = command.substring(7);
    person.trim();
    Serial.print("# Person changed to: ");
    Serial.println(person);
  }
  else if (command.startsWith("SCENARIO=")) {
    scenario = command.substring(9);
    scenario.trim();
    Serial.print("# Scenario changed to: ");
    Serial.println(scenario);
  }
  else if (command == "RESETCOUNT") {
    recordNo = 1;
    preferences.putULong("recordNo", recordNo);
    Serial.println("# Record number reset to 1");
  }
  else if (command == "SHOW") {
    Serial.print("# Person: ");
    Serial.println(person);
    Serial.print("# Scenario: ");
    Serial.println(scenario);
    Serial.print("# Next Record: ");
    Serial.println(recordNo);
  }
}

void printHeader() {
  Serial.println("RecordNo,Type,Person,Scenario,FSR1,FSR2,FSR3,FSR4,Temperature");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(FSR1_PIN, INPUT);
  pinMode(FSR2_PIN, INPUT);
  pinMode(FSR3_PIN, INPUT);
  pinMode(FSR4_PIN, INPUT);

  sensors.begin();

  preferences.begin("dataLogger", false);
  recordNo = preferences.getULong("recordNo", 1);

  Serial.println();
  Serial.println("# SMART FOOTWEAR DATA LOGGER");
  Serial.println("# USB CSV DATA COLLECTION");
  Serial.println();

  Serial.print("# Starting Record No: ");
  Serial.println(recordNo);
  Serial.print("# Person: ");
  Serial.println(person);
  Serial.print("# Scenario: ");
  Serial.println(scenario);
  Serial.println();

  printHeader();
  lastSampleTime = millis();
}

void loop() {
  checkSerialCommands();

  unsigned long currentTime = millis();

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime += SAMPLE_INTERVAL;

    int fsr1 = analogRead(FSR1_PIN);
    int fsr2 = analogRead(FSR2_PIN);
    int fsr3 = analogRead(FSR3_PIN);
    int fsr4 = analogRead(FSR4_PIN);

    sensors.requestTemperatures();
    float temperature = sensors.getTempCByIndex(0);

    if (temperature == DEVICE_DISCONNECTED_C) {
      temperature = 0;
    }

    sumFSR1 += fsr1;
    sumFSR2 += fsr2;
    sumFSR3 += fsr3;
    sumFSR4 += fsr4;
    sumTemp += temperature;
    sampleCount++;

    Serial.print(recordNo);
    Serial.print(",RAW,");
    Serial.print(person);
    Serial.print(",");
    Serial.print(scenario);
    Serial.print(",");
    Serial.print(fsr1);
    Serial.print(",");
    Serial.print(fsr2);
    Serial.print(",");
    Serial.print(fsr3);
    Serial.print(",");
    Serial.print(fsr4);
    Serial.print(",");
    Serial.println(temperature, 2);

    recordNo++;

    if (sampleCount >= 10) {
      float avgFSR1 = sumFSR1 / 10.0;
      float avgFSR2 = sumFSR2 / 10.0;
      float avgFSR3 = sumFSR3 / 10.0;
      float avgFSR4 = sumFSR4 / 10.0;
      float avgTemp = sumTemp / 10.0;

      Serial.print(recordNo);
      Serial.print(",AVG10,");
      Serial.print(person);
      Serial.print(",");
      Serial.print(scenario);
      Serial.print(",");
      Serial.print(avgFSR1, 2);
      Serial.print(",");
      Serial.print(avgFSR2, 2);
      Serial.print(",");
      Serial.print(avgFSR3, 2);
      Serial.print(",");
      Serial.print(avgFSR4, 2);
      Serial.print(",");
      Serial.println(avgTemp, 2);

      recordNo++;
      preferences.putULong("recordNo", recordNo);

      sumFSR1 = 0;
      sumFSR2 = 0;
      sumFSR3 = 0;
      sumFSR4 = 0;
      sumTemp = 0;
      sampleCount = 0;
    }
  }
}
