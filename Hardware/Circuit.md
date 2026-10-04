# Circuit Reference

## ESP32 Connections

| ESP32 GPIO | Connection |
|---|---|
| GPIO34 | FSR1 |
| GPIO35 | FSR2 |
| GPIO32 | FSR3 |
| GPIO33 | FSR4 |
| GPIO4 | DS18B20 DATA |

Each FSR uses a 10 kΩ resistor in its voltage-divider circuit.

The DS18B20 DATA line uses a 4.7 kΩ pull-up resistor to the sensor supply.
