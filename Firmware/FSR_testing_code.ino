const int FSR1 = 34;
const int FSR2 = 36;
const int FSR3 = 32;
const int FSR4 = 33;

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.print("FSR1: ");
  Serial.print(analogRead(FSR1));
  Serial.print(" | FSR2: ");
  Serial.print(analogRead(FSR2));
  Serial.print(" | FSR3: ");
  Serial.print(analogRead(FSR3));
  Serial.print(" | FSR4: ");
  Serial.println(analogRead(FSR4));
  delay(500);
}
