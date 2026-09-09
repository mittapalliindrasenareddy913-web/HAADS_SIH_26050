# HAADS — System Architecture & Pipeline Specification

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Executive Summary

HAADS is an edge-native anti-drone detection, tracking, and atmospheric compensation system built to operate under severe high-altitude environmental stress (sub-zero temperatures, low atmospheric pressure, high wind shear, and structural vibration). 

The software architecture decouples sensor ingestion, Edge AI detection, target tracking, environmental simulation/compensation, health monitoring, and hardware telemetry into distinct, modular subsystems.

---

## 2. High-Level Dataflow Architecture

```
  +-------------------------------------------------------------------------+
  |                              INPUT STREAM                               |
  |  Local USB Webcam / HTML5 Browser Ingestion / Camera Component          |
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |                          CV2 WRAPPER / INGESTION                        |
  |  Headless OpenCV compatibility layer & NumPy frame normalization (640x480) |
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |                      YOLO26n EDGE AI DETECTOR                           |
  |  Single-pass detection, screen-proxy interpretation layer for phone targets|
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |                       PERSISTENT TARGET TRACKER                         |
  |  Centroid & IoU trajectory tracking, unique Track ID assignment, smoothing |
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |                   ENVIRONMENTAL COMPENSATION ENGINE                     |
  |  Atmospheric density calculation, drag torque compensation, gimbal offsets|
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +------------------------------------+------------------------------------+
  |              HARDWARE TELEMETRY / WOKWI MQTT LINK                       |
  |  ESP32 telemetry ingestion, BME280/MPU6050 feedback, Servo PWM output  |
  +------------------------------------+------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |                        ENGINEERING DASHBOARD                            |
  |  Streamlit UI, real-time overlays, health matrix, performance analytics |
  +-------------------------------------------------------------------------+
```

---

## 3. Subsystem Breakdown

### 3.1 Frame Ingestion (`app/camera.py`, `app/camera_component/`)
- Supports local OpenCV webcam capturing (`cv2.VideoCapture`).
- Provides fallback to native HTML5 Browser Camera component (`app/camera_component/index.html`) using Base64 JPEG decoding via WebSockets/Streamlit callbacks.
- Computes real-time execution FPS.

### 3.2 Detection Engine (`app/detector.py`)
- Executes **YOLO26n Edge AI** object detection model (`yolo26n.pt`).
- Includes screen-proxy target detection layer: accurately identifies physical mobile phone devices showing drone/person media while preserving target classifications.
- Provides fallback empty detection matrix if PyTorch/Ultralytics is unavailable.

### 3.3 Target Tracking (`app/tracker.py`)
- Tracks target centroids and bounding boxes across frames using Euclidean distance matching and IoU overlap.
- Assigns persistent `Track ID` values, maintaining stability across temporary frame drops.
- Maintains spatial velocity vectors (`vx`, `vy`) to predict future target positions.

### 3.4 Environmental Compensation Engine (`app/compensation.py`)
- Ingests ambient atmospheric temperature ($T$), barometric pressure ($P$), wind velocity ($v_w$), and vibration magnitude ($a_{vib}$).
- Calculates air density:
  $$\rho = \frac{P \times 100}{R_d \times (T + 273.15)}$$
- Computes dynamic drag force and thermal cable stiffness factors to generate pan/tilt servo offset angles ($\Delta \theta_{pan}, \Delta \theta_{tilt}$).

### 3.5 Hardware Interface & Telemetry (`app/hardware_interface.py`)
- Interfaces with real-time hardware over MQTT broker (`test.mosquitto.org:1883`).
- Ingests BME280 ($T, P$) and MPU6050 ($\text{gyro}_x, \text{gyro}_y, \text{gyro}_z$) sensor telemetry.
- Transmits computed servo commands ($\theta_{pan}, \theta_{tilt}$) to physical or Wokwi-simulated pan/tilt servos.
- Implements state-machine fallback (`WOKWI_ONLINE` $\leftrightarrow$ `WOKWI_OFFLINE` / `SOFTWARE_SIMULATION`).

### 3.6 Health Monitoring Matrix (`app/health_monitor.py`)
- Tracks operational state for 9 critical system elements: `camera`, `ai_detector`, `tracking`, `environment`, `mpu6050`, `bme280`, `compensation`, `servos`, and `communication`.
- Emits real-time diagnostic health matrix for engineering dashboard.
