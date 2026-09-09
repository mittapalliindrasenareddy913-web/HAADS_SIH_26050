# HAADS — High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mittapalliindrasenareddy913-web-haads-sih-26050-app-jzmx3g.streamlit.app/)
[![SIH PS 26050](https://img.shields.io/badge/SIH%20Problem%20Statement-26050-orange.svg)](https://www.sih.gov.in/)
[![Team DEVOPS](https://img.shields.io/badge/Team-DEVOPS-blue.svg)](#team--project-identity)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![YOLO26n Edge AI](https://img.shields.io/badge/AI%20Engine-YOLO26n%20Edge-purple.svg)](models/)

---

## 🎯 Executive Summary & Problem Statement

**HAADS** is an edge-native anti-drone detection, precision tracking, and high-altitude atmospheric compensation system developed for **Smart India Hackathon (SIH) Problem Statement 26050** by **Team DEVOPS**.

Deploying electro-optical anti-drone platforms in high-altitude terrain (3,000 m – 6,000 m above sea level) presents severe environmental challenges: sub-zero temperatures, low barometric pressure, cross-wind shear, and structural vibration. HAADS addresses these challenges through a closed-loop feedback system combining **YOLO26n-based edge object detection and target tracking** (with drone-specific fine-tuning planned for the next development phase), persistent centroid trajectory tracking, dynamic atmospheric physics compensation, and real-time Wokwi ESP32 hardware telemetry.

> [!IMPORTANT]
> **SAFETY & NON-DESTRUCTIVE SCOPE STATEMENT**:  
> HAADS is designed strictly for **object detection, identification, spatial tracking, atmospheric compensation, virtual pan/tilt pointing, and subsystem health matrix monitoring**. This repository contains **NO RF jamming, NO signal disruption, NO physical neutralization, and NO weapon control**.

---

## 🟢 CURRENT ACADEMIC PROTOTYPE vs 🟡 PROPOSED FUTURE HARDWARE

To maintain complete technical integrity and credibility during evaluation, system capabilities are explicitly categorized:

### 🟢 CURRENT ACADEMIC PROTOTYPE (Implemented & Operational):
- **User Interface**: Streamlit interactive engineering dashboard UI.
- **Vision AI**: YOLO26n-based edge object detection and target tracking, with drone-specific fine-tuning planned for the next development phase. Includes screen-proxy target interpretation layer for phone targets.
- **Optical Ingestion**: Local USB webcam and native HTML5 browser camera stream ingestion.
- **Target Tracking**: Persistent centroid matching and IoU bounding box trajectory tracking with persistent Track IDs.
- **Environmental Compensation**: Mathematical physics simulation engine evaluating air density ($\rho$), aerodynamic drag force ($F_d$), thermal stiffness ($K_{temp}$), and pan/tilt servo pointing offsets under high-altitude stress.
- **Hardware Simulation**: Wokwi ESP32 virtual hardware simulation suite with MQTT telemetry transport and automatic software simulation fallback.

### 🟡 PROPOSED FUTURE HARDWARE (Engineering Roadmap):
- **Dedicated Edge AI Compute**: Raspberry Pi CM5 (Compute Module 5) with 13 TOPS Hailo-8 M.2 Neural Accelerator.
- **Real-Time Controller**: STM32H7 dual-core ARM Cortex-M7/M4 microcontroller running deterministic RTOS control loops.
- **Physical Sensing**: Dual industrial BME280 barometric sensors and heated military-grade IMU (ICM-42688).
- **Physical Actuation**: Heavy-duty brushless optical encoder pan/tilt gimbal platform.
- **Environmental Testing**: High-altitude thermal-vacuum chamber validation and field test deployments.

---

## 🌐 Live Prototype & Simulation Links

- **Live Streamlit Web Application**: [HAADS Streamlit Cloud Deployment](https://mittapalliindrasenareddy913-web-haads-sih-26050-app-jzmx3g.streamlit.app/)
- **Wokwi Hardware Simulation Suite**: See [wokwi/README.md](wokwi/README.md) for ESP32 hardware simulation instructions.

---

## 🏗️ System Architecture & Dataflow

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

## 📂 Repository Structure

```
HAADS-SIH-26050/
├── app.py                          # Root Streamlit entry point launcher shim
├── README.md                       # Main GitHub project documentation
├── LICENSE                         # MIT License
├── requirements.txt                # Production dependencies
├── .gitignore                      # Python & model gitignore configuration
├── test_pipeline.py                # 13-stage end-to-end integration test runner
├── yolo26n.pt                      # YOLO26n Edge AI model weights
│
├── app/                            # Modularized Application Core
│   ├── app.py                      # Application main orchestrator
│   ├── config.py                   # System configuration & thresholds
│   ├── camera.py                   # Camera manager & stream ingestion
│   ├── cv2_wrapper.py              # Headless OpenCV patch layer
│   ├── detector.py                 # YOLO26n Edge AI detector & proxy classifier
│   ├── tracker.py                  # Persistent target tracker (centroid / IoU)
│   ├── environment.py              # Environmental simulation engine
│   ├── compensation.py             # Physics compensation & stabilization engine
│   ├── performance.py              # Deterministic performance evaluator
│   ├── health_monitor.py           # Subsystem health matrix monitor
│   ├── hardware_interface.py       # Wokwi ESP32 MQTT hardware interface
│   ├── data_manager.py             # System telemetry JSON manager
│   ├── snapshot_manager.py         # Detection snapshot manager & gallery
│   ├── dashboard.py                # Streamlit engineering dashboard UI
│   └── camera_component/           # HTML5 browser webcam component
│
├── docs/                           # Comprehensive System Documentation
│   ├── system-architecture.md      # Dataflow & pipeline breakdown
│   ├── working-principle.md        # Mission execution & state machine workflow
│   ├── environmental-compensation.md # Atmospheric physics & compensation formulas
│   ├── hardware-architecture.md    # Host computer & micro-controller specs
│   ├── prototype-roadmap.md        # Multi-phase development roadmap
│   ├── testing-validation.md       # Integration test documentation & results
│   └── limitations.md              # Scope boundaries & future enhancements
│
├── hardware/                       # Hardware Engineering Documentation
│   ├── BOM.md                      # Detailed Bill of Materials (Simulation vs Proposed)
│   ├── wiring.md                   # ESP32 pinout & sensor wiring specifications
│   └── future-hardware.md          # Proposed physical RPi CM5 + Hailo-8 hardware
│
├── models/                         # AI Models Directory
│   └── README.md                   # Weights guide & fine-tuning documentation
│
├── wokwi/                          # Wokwi Hardware Simulation Suite
│   ├── diagram.json                # ESP32 + MPU6050 + BME280 wiring diagram
│   ├── wokwi.ino                   # ESP32 C++ firmware source
│   ├── libraries.txt               # Wokwi Arduino library dependencies
│   └── README.md                   # Wokwi setup guide
│
├── results/                        # Prototype evaluation results & demo logs
│   └── demo-results.md             # Evaluation logs & prototype verification
│
└── presentation/                   # Official SIH Presentation
    └── DEVOPS_SIH_26050_Presentation.pdf # SIH presentation slide deck
```

---

## ⚡ Quickstart Guide

### 1. Clone & Setup Environment
```bash
git clone https://github.com/mittapalliindrasenareddy913-web/HAADS_SIH_26050.git
cd HAADS_SIH_26050
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Streamlit Application
```bash
streamlit run app.py
```
*Navigates automatically to `http://localhost:8501` in your browser.*

### 3. Run Automated Integration Test Suite
```bash
python test_pipeline.py
```

---

## 📊 Prototype Performance Evaluation

Simulation-based performance evaluation generated by the HAADS performance engine.

| Evaluation Metric | Uncompensated System | HAADS Compensated System | Simulated Improvement |
| :--- | :---: | :---: | :---: |
| **Tracking Accuracy** | 68.2% | 85.6% | **+17.4%** |
| **Gimbal Stabilization Rate** | 32.8% | 78.2% | **+45.4%** |
| **Overall Performance Score** | 50.4% | 81.9% | **+31.6% Boost** |

> [!NOTE]
> **Note**: These values represent simulation-based prototype evaluation generated by the performance engine and are not physical field-test measurements.

---

## 👥 Team & Project Identity

- **Team Name**: DEVOPS
- **Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)
- **SIH Problem Statement ID**: 26050
- **Repository Name**: HAADS-SIH-26050
- **Presentation Deck**: Located in `presentation/DEVOPS_SIH_26050_Presentation.pdf`

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — free for educational, academic, and research applications.
