# HAADS — Bill of Materials (BOM)

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Classification Overview

Components are categorized into:
- **`[SIMULATION]`**: Wokwi virtual hardware suite components.
- **`[CURRENT PROTOTYPE]`**: Workstation & Edge AI software prototype elements.
- **`[PROPOSED PHYSICAL HARDWARE]`**: Production-grade hardware roadmap elements.

---

## 2. Detailed Bill of Materials

| Component Name | Model / Specification | Function / Role | Status Category | Qty | Approx Cost (INR) |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Edge Microcontroller** | ESP32 DevKit V1 | Real-time sensor reading & MQTT broker transport | `[SIMULATION / PROTOTYPE]` | 1 | ₹450 |
| **Environmental Sensor** | BME280 (I2C 0x76) | Barometric pressure & temperature measurement | `[SIMULATION]` | 1 | ₹350 |
| **Motion Inertial Unit** | MPU6050 6-DOF IMU (I2C 0x68) | Angular rate & vibration accelerometer sensing | `[SIMULATION]` | 1 | ₹250 |
| **Pan / Tilt Servo Motors** | SG90 / MG996R Servos | Optical tracking gimbal elevation & azimuth sweep | `[SIMULATION]` | 2 | ₹600 |
| **Alarm Buzzer** | 5V Active Buzzer | Target acquisition audio alert | `[SIMULATION]` | 1 | ₹40 |
| **Environment Potentiometers**| 10k Linear Potentiometers | Manual altitude parameter simulation controls | `[SIMULATION]` | 4 | ₹80 |
| **Host Workstation** | x86_64 Laptop / Desktop PC | Streamlit dashboard UI & PyTorch YOLO26n Edge AI | `[CURRENT PROTOTYPE]` | 1 | Existing |
| **Optical Ingestion Camera** | 1080p USB Optical Webcam | High-resolution visual target detection | `[CURRENT PROTOTYPE]` | 1 | ₹1,500 |
| **Raspberry Pi CM5 Compute Module**| RPi CM5 8GB RAM + 32GB eMMC | Dedicated high-altitude Edge AI compute module | `[PROPOSED]` | 1 | ₹7,500 |
| **AI Accelerator Module** | Hailo-8 M.2 AI Module (13 TOPS)| Low-latency YOLO26n neural acceleration | `[PROPOSED]` | 1 | ₹12,000 |
| **Real-Time MCU** | STM32H743 Dual-Core ARM | High-precision CAN-bus gimbal motor controller | `[PROPOSED]` | 1 | ₹1,800 |
| **Heated Military IMU** | ICM-42688-P (Heated Enclosure) | Sub-zero vibration-resistant attitude reference | `[PROPOSED]` | 1 | ₹4,500 |
| **Heavy Pan/Tilt Gimbal** | Brushless Optical Encoder Gimbal | High-altitude wind-resistant optical tracking platform | `[PROPOSED]` | 1 | ₹18,000 |
| **IP67 Sealed Housing** | Anodized Aluminum Enclosure | Environmental protection with internal thermal heater | `[PROPOSED]` | 1 | ₹8,500 |

---

## 3. Financial Summary

- **Current Prototype & Wokwi Simulation Cost**: ~₹3,270 (Excluding host computer)
- **Proposed Industrial Production Unit Cost**: ~₹53,800 per unit
