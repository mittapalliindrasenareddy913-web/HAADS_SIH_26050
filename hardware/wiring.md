# HAADS — ESP32 Sensor & Actuator Pinout Specification

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Pin Assignment Table

Matches Wokwi hardware simulation (`wokwi/diagram.json`):

| Device / Module | Pin Name | ESP32 Pin | Signal Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| **MPU6050 IMU** | VCC | `3V3` | Power | 3.3V Power Supply |
| **MPU6050 IMU** | GND | `GND` | Power | System Ground |
| **MPU6050 IMU** | SDA | `GPIO 21` | I2C Data | Shared I2C Data Bus (Address `0x68`) |
| **MPU6050 IMU** | SCL | `GPIO 22` | I2C Clock | Shared I2C Clock Bus |
| **BME280 Sensor** | VIN | `3V3` | Power | 3.3V Power Supply |
| **BME280 Sensor** | GND | `GND` | Power | System Ground |
| **BME280 Sensor** | SDA | `GPIO 21` | I2C Data | Shared I2C Data Bus (Address `0x76`) |
| **BME280 Sensor** | SCL | `GPIO 22` | I2C Clock | Shared I2C Clock Bus |
| **Temperature Pot**| SIG | `GPIO 34` | Analog (ADC1_CH6) | Temperature simulation (-30°C to +30°C) |
| **Pressure Pot** | SIG | `GPIO 35` | Analog (ADC1_CH7) | Pressure simulation (500 hPa to 1000 hPa) |
| **Wind Speed Pot** | SIG | `GPIO 32` | Analog (ADC1_CH4) | Wind shear simulation (0 to 60 km/h) |
| **Vibration Pot** | SIG | `GPIO 33` | Analog (ADC1_CH5) | Structural vibration simulation (LOW/MED/HIGH) |
| **Pan Servo** | SIG | `GPIO 26` | PWM (LEDC CH0) | Azimuth tracking actuation (0° to 180°) |
| **Tilt Servo** | SIG | `GPIO 27` | PWM (LEDC CH1) | Elevation tracking actuation (0° to 180°) |
| **Alarm Buzzer** | SIG | `GPIO 25` | Digital Out | Active target alert notification |

---

## 2. Bus Architecture

- **I2C Bus (GPIO 21 SDA / GPIO 22 SCL)**: Runs at 400 kHz Fast-Mode, servicing both MPU6050 and BME280 on independent slave addresses (`0x68` & `0x76`).
- **ADC Channels**: ADC1 is used exclusively to prevent conflicts with Wi-Fi/MQTT communications on ADC2.
