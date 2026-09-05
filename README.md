# High Altitude Performance Optimization and Robust Design of Anti-Drone System

**Smart India Hackathon (SIH) Problem Statement ID:** 26050  
**Project Category:** Academic Engineering Prototype  
**Primary Model:** YOLO26n Edge AI  

---

> [!IMPORTANT]
> **SAFETY & SCOPE BOUNDARY**:
> This prototype is designed strictly for **object detection, identification, tracking, high-altitude environmental simulation, environmental compensation, performance estimation, virtual pan/tilt pointing, system health monitoring, and threshold alerts**.  
> **DO NOT IMPLEMENT / NON-DESTRUCTIVE SCOPE**: This system contains NO RF jamming, NO signal disruption, NO physical neutralization, and NO weapon control.

> [!NOTE]
> **ZERO PHYSICAL ELECTRONICS REQUIRED**:
> The prototype uses your **laptop built-in webcam** for real-world computer vision input. All electronic hardware (ESP32, IMU, sensors, potentiometers, servos) is simulated using **Wokwi virtual electronics** with an automatic **Software Simulation Fallback**.

---

## 1. System Architecture (Sir's Block Diagram)

The overall system architecture follows four major functional blocks:

```
[ LAPTOP — REAL INPUT ]
   Laptop Built-in Webcam (OpenCV)
            │
            ▼
[ PROCESSING & CONTROL — LAPTOP ]
   YOLO26n Edge AI Object Detection
            │
            ▼
   Persistent Object Tracker (Track ID, Bounding Box X,Y,W,H, Trajectory, Error X,Y)
            │
            ▼
[ ENVIRONMENTAL SIMULATION ]
   High-Altitude Environmental Simulation (Temp, Pressure, Wind, Vibration)
            │
            ▼
   Environmental Compensation Engine (Stiffness, Drag Force, Adaptive Stabilization Gain)
            │
            ▼
   Deterministic Performance & Subsystem Health Engine
            │
            ▼
   Virtual Pan/Tilt Pointing Servo Angle Calculation
            │
            ▼
   system_data.json (Central Structured State Exchange Format)
            │
            ▼
   Streamlit Engineering Dashboard
            │
            ▼
[ HARDWARE SIMULATION — WOKWI ]
   ESP32 DevKit V1 ── MPU6050 (IMU)
                    ├── BME280 (Press/Temp)
                    ├── 4 Potentiometers (Temp, Press, Wind, Vib)
                    └── Pan/Tilt Servos (GPIO 26 / 27)
```

---

## 2. REAL vs. SIMULATED Distinction

To ensure presentation honesty during competition judging, data sources are explicitly segregated:

### 🟢 REAL:
- Laptop hardware
- Laptop built-in webcam feed
- OpenCV video frame ingestion
- YOLO26n Edge AI inference engine
- Persistent object tracking & center coordinate calculations
- Python backend processing
- Streamlit interactive UI dashboard

### 🟡 SIMULATED:
- High-altitude environment (Sub-zero temperature, low air pressure, high wind shear, structural vibration)
- ESP32 DevKit V1 micro-controller
- MPU6050 6-DOF IMU sensor
- BME280 barometric pressure & temperature sensor
- 4 Virtual potentiometers (Environmental input knobs)
- Virtual Pan/Tilt servo actuators
- Mechanical stiffness, cable drag, aerodynamic disturbance, sensor drift, and performance estimates

---

## 3. Project Structure

```
HAADS_SIH_26050/
├── app.py                   # Main entry point (Streamlit launcher)
├── config.py                # System parameters, model paths, scenario thresholds
├── camera.py                # OpenCV webcam manager with error & permission handling
├── detector.py              # YOLO26n Edge AI detection engine
├── tracker.py               # Target trajectory & persistent ID tracker
├── environment.py           # High-altitude environmental simulation model
├── compensation.py          # Environmental compensation & disturbance estimators
├── performance.py           # Deterministic performance estimation engine (No random numbers)
├── health_monitor.py        # Subsystem health metrics & alert generator
├── hardware_interface.py    # Abstraction for Wokwi ESP32 / Software fallback
├── data_manager.py          # Atomic JSON state writer/reader (system_data.json)
├── dashboard.py             # Streamlit engineering dashboard UI
├── system_data.json         # Real-time state exchange document
├── test_webcam.py           # Webcam verification test
├── test_pipeline.py         # Full integration test suite
├── requirements.txt         # Dependencies
├── README.md                # Documentation
└── wokwi/
    ├── diagram.json         # Wokwi circuit diagram specification
    ├── wokwi.ino            # ESP32 C++ Arduino sketch
    └── README.md            # Wokwi simulation guide
```

---

## 4. Key Engineering Modules

### YOLO26n Edge AI Detector (`detector.py`)
- Standard model: **YOLO26n Edge AI — Object Detection & Tracking**
- Support for future custom drone-trained YOLO26n models (`models/custom_drone_yolo26n.pt`) without code modification.
- Outputs bounding box `[X1, Y1, X2, Y2]`, class name, confidence, and center coordinates `(cx, cy)`.

### Object Tracker & Pointing Error (`tracker.py`)
- Maintains persistent `Track ID` across frames using Euclidean distance matching.
- Calculates pointing error vectors relative to frame center (320, 240):
  $$\text{error\_x} = \text{target\_x} - 320$$
  $$\text{error\_y} = \text{target\_y} - 240$$
- Logs trajectory history points for visual path rendering.

### Environmental Simulation Engine (`environment.py`)
- Simulates high-altitude operational parameters:
  - Temperature: **-30°C to +30°C**
  - Barometric Pressure: **500 hPa to 1000 hPa**
  - Wind Speed: **0 to 60 km/h**
  - Structural Vibration: **LOW / MEDIUM / HIGH**
- Calculates dynamic air density $\rho = \frac{P \times 100}{R \cdot T_{\text{Kelvin}}}$.

### Environmental Compensation (`compensation.py`)
- **Temperature Stiffness**: Models cable/lubricant stiffening at sub-zero temperatures ($T < 0^\circ\text{C}$).
- **Wind Drag Deflection**: Calculates aerodynamic drag force $F_{\text{drag}} = \frac{1}{2} \rho v^2 A$.
- **Adaptive Stabilization Gain**: Dynamically adjusts control gains to maintain pointing stability.
- **Formulas**: Strictly labeled as `PROTOTYPE SIMULATION MODEL`.

### Deterministic Performance Model (`performance.py`)
- Evaluates **WITHOUT COMPENSATION** vs **WITH COMPENSATION** side-by-side.
- Zero random numbers! All formulas respond deterministically to environmental changes.
- Clearly labeled as `SIMULATED PERFORMANCE ESTIMATE`.

### Subsystem Health & Alerts (`health_monitor.py`)
- Monitors 9 critical subsystems: Camera, AI, Tracking, Environment, MPU6050, BME280, Compensation, Servos, Communication.
- Triggers threshold alerts: `EXTREME_COLD`, `HIGH_WIND_SHEAR`, `EXTREME_COMBINED_HAZARD`, `HIGH_VIBRATION`, `WOKWI_OFFLINE`.

---

## 5. Predefined Scenario Modes

1. **MODE 1 — NORMAL**: $20^\circ\text{C}$, $950\text{ hPa}$, $5\text{ km/h}$, LOW vibration.
2. **MODE 2 — EXTREME COLD**: $-20^\circ\text{C}$, $700\text{ hPa}$, $10\text{ km/h}$, MEDIUM vibration.
3. **MODE 3 — HIGH WIND**: $-5^\circ\text{C}$, $750\text{ hPa}$, $40\text{ km/h}$, MEDIUM vibration.
4. **MODE 4 — EXTREME COMBINED**: $-20^\circ\text{C}$, $650\text{ hPa}$, $40\text{ km/h}$, HIGH vibration.

---

## 6. How to Run the Prototype

### Prerequisites
- Python 3.10+
- Laptop with built-in webcam

### Step 1: Install Dependencies
```bash
pip install -r HAADS_SIH_26050/requirements.txt
```

### Step 2: Run Full Integration Verification Test
```bash
python HAADS_SIH_26050/test_pipeline.py
```

### Step 3: Launch Streamlit Engineering Dashboard
```bash
streamlit run HAADS_SIH_26050/app.py
```

---

## 7. Wokwi Virtual Hardware Setup

1. Open [Wokwi.com](https://wokwi.com).
2. Create an **ESP32** project.
3. Copy `HAADS_SIH_26050/wokwi/diagram.json` into Wokwi `diagram.json`.
4. Copy `HAADS_SIH_26050/wokwi/wokwi.ino` into Wokwi `wokwi.ino`.
5. Click **Start Simulation**.

If Wokwi local bridge is not active:
The system automatically displays `WOKWI CONNECTION: NOT CONNECTED` and safely continues using `SOFTWARE SIMULATION FALLBACK`.
