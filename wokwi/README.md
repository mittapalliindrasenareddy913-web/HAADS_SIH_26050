# HAADS — Wokwi ESP32 Hardware Simulation Suite

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Overview

The `wokwi/` directory contains the complete Wokwi ESP32 hardware simulation suite for real-time testing of sensors, actuators, and MQTT telemetry communication with the Streamlit edge dashboard.

---

## 2. File Inventory

- `diagram.json`: Complete Wokwi graphical wiring diagram (ESP32 DevKit V1 + MPU6050 + BME280 + 4 Potentiometers + 2 Servos + Buzzer).
- `wokwi.ino`: Arduino C++ firmware for ESP32 with MQTT telemetry publishing and PWM servo driving.
- `libraries.txt`: Required Wokwi Arduino libraries (`Adafruit BME280`, `Adafruit MPU6050`, `ESP32Servo`, `PubSubClient`, `ArduinoJson`).

---

## 3. How to Run Wokwi Simulation

1. Open [Wokwi.com](https://wokwi.com/) in your web browser.
2. Create a new **ESP32** project.
3. Replace the code in `sketch.ino` with the contents of `wokwi/wokwi.ino`.
4. Replace `diagram.json` with `wokwi/diagram.json`.
5. Add the libraries from `wokwi/libraries.txt` in the Library Manager tab.
6. Click **Start Simulation** (Play button).
7. The ESP32 connects to Wi-Fi (`Wokwi-GUEST`) and publishes MQTT sensor telemetry to topic `haads/sih26050/telemetry` on public broker `test.mosquitto.org:1883`.
8. The Streamlit dashboard (`app/app.py`) automatically detects incoming heartbeats and transitions hardware link status to `WOKWI_ONLINE`.

---

## 4. Hardware Pinout Reference

See [hardware/wiring.md](../hardware/wiring.md) for full GPIO pinout details.
