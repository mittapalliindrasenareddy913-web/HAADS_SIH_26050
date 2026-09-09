# HAADS — Hardware Architecture Specification

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Architecture Classification

The HAADS hardware model clearly delineates between the **Current Academic Prototype & Simulation Environment** and the **Proposed Future Physical Hardware Architecture**.

---

## 2. Current Prototype Hardware Configuration (Implemented)

```
  +-------------------------------------------------------------------------+
  |                          HOST EDGE COMPUTER                             |
  |  Intel / AMD x86_64 Laptop running Windows/Linux                       |
  |  - Streamlit UI Dashboard                                               |
  |  - PyTorch / YOLO26n Edge AI Engine                                     |
  |  - Compensation & Performance Engines                                   |
  +------------------------------------+------------------------------------+
                                       | MQTT Telemetry (Broker: test.mosquitto.org)
                                       v
  +-------------------------------------------------------------------------+
  |                     WOKWI ESP32 HARDWARE SIMULATOR                      |
  |  ESP32 DevKit V1 Microcontroller                                        |
  |  - MPU6050 6-DOF IMU (I2C 0x68)                                         |
  |  - BME280 Environmental Sensor (I2C 0x76)                               |
  |  - Potentiometer Environmental Controls                                 |
  |  - Pan / Tilt Servo Actuators (GPIO 26 / 27)                             |
  +-------------------------------------------------------------------------+
```

---

## 3. Proposed Future Physical Hardware Architecture (Roadmap)

```
  +-------------------------------------------------------------------------+
  |                     PRIMARY EDGE AI COMPUTER                            |
  |  Raspberry Pi CM5 (Compute Module 5) + 13 TOPS Hailo-8 AI Accelerator   |
  |  - 4K Optical Camera Input via MIPI-CSI                                |
  |  - Real-time YOLO26n Inference at >60 FPS                              |
  +------------------------------------+------------------------------------+
                                       | High-Speed SPI / CAN Bus Interface
                                       v
  +-------------------------------------------------------------------------+
  |                     REAL-TIME MOTOR CONTROLLER                          |
  |  STM32H743 Dual-Core ARM Cortex-M7/M4 Microcontroller                   |
  |  - Ruggedized Optical Encoder Pan/Tilt Gimbal Motors                   |
  |  - Dual Industrial BME280 Barometric Sensors                             |
  |  - Heated Military IMU (ICM-42688) with Active Vibration Dampeners     |
  +-------------------------------------------------------------------------+
```
