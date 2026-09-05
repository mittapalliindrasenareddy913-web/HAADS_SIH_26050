# Wokwi Hardware Simulation Setup & Fix Guide (HAADS SIH 26050)

This directory contains the virtual electronics simulation files for the **High Altitude Performance Optimization and Robust Design of Anti-Drone System**.

---

## 🛠️ Resolving "ESP32Servo.h: No such file or directory" in Wokwi

Wokwi requires external Arduino libraries to be registered in `libraries.txt` or via the **Library Manager** tab.

### Method 1: Create `libraries.txt` in Wokwi (Recommended)
In the Wokwi editor:
1. Click the **+ New File** button (top left of the code panel).
2. Name the file: `libraries.txt`
3. Copy and paste the following 4 lines:
```text
ESP32Servo
Adafruit MPU6050
Adafruit Unified Sensor
Adafruit BME280 Library
```

### Method 2: Use Wokwi Library Manager Tab
1. Click the **Library Manager** tab (`+` icon next to files in Wokwi).
2. Search and click **Add** for:
   - `ESP32Servo`
   - `Adafruit MPU6050`
   - `Adafruit Unified Sensor`
   - `Adafruit BME280 Library`

---

## 📐 Circuit Schematic (`diagram.json`)

Component list & GPIO pins:
- **ESP32 DevKit V1**
- **MPU6050 IMU**: I2C (SDA -> GPIO 21, SCL -> GPIO 22)
- **BME280 Sensor**: I2C (SDA -> GPIO 21, SCL -> GPIO 22)
- **Temperature Potentiometer**: Analog -> GPIO 34
- **Pressure Potentiometer**: Analog -> GPIO 35
- **Wind Speed Potentiometer**: Analog -> GPIO 32
- **Vibration Potentiometer**: Analog -> GPIO 33
- **Pan Servo**: PWM -> GPIO 26
- **Tilt Servo**: PWM -> GPIO 27

---

## 🖥️ Expected Serial Telemetry Output

When the Wokwi simulation starts, the Serial Monitor (115200 baud) will display:

```text
==============================================
HAADS WOKWI HARDWARE SIMULATION
==============================================
[ESP32] MPU6050 initialized successfully.
[ESP32] BME280 initialized successfully.
[ESP32] Pan Servo attached to GPIO 26.
[ESP32] Tilt Servo attached to GPIO 27.

HAADS WOKWI HARDWARE SIMULATION TELEMETRY
Temperature: 20.0 C
Pressure: 950.0 hPa
Wind: 5.0 km/h
Vibration: LOW
IMU (MPU6050): OK [Ax:0.01, Ay:0.02, Az:9.81]
BME280: OK
Pan Servo Angle: 90 deg
Tilt Servo Angle: 90 deg
```
