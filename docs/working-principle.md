# HAADS — Working Principle & Mission Execution Workflow

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Operating Principle Overview

HAADS operates on a high-speed closed-loop feedback pipeline:
1. **Visual Sensing**: Ingests high-framerate optical feeds from USB webcams or HTML5 browser streams.
2. **Edge AI Inference**: Detects target objects in under 30 ms using YOLO26n Edge AI.
3. **Persistent Tracking**: Associates spatial bounding boxes across sequential frames using centroid distance and IoU metrics.
4. **Environmental Sensing & Physics Modeling**: Evaluates real-time ambient atmospheric pressure, temperature, wind shear, and mechanical vibration.
5. **Dynamic Compensation Calculation**: Computes mechanical drag torque and pointing correction factors.
6. **Actuation & Telemetry Control**: Transmits pan/tilt control signals to physical or simulated servo gimbals.

---

## 2. Step-by-Step Execution Pipeline

```
  [ Webcam / Browser Frame ]
              │
              ▼
    [ YOLO26n Edge AI ] ──────> Target Bounding Boxes + Confidence %
              │
              ▼
   [ Persistent Tracker ] ────> Track ID + Centroid Coordinates (X, Y)
              │
              ▼
 [ Environmental Sensors ] ───> Temp, Pressure, Wind Speed, Vibration
              │
              ▼
 [ Compensation Engine ] ────> Pan Offset (Δθ_pan), Tilt Offset (Δθ_tilt)
              │
              ▼
 [ Gimbal Actuation Servo ] ──> Corrected Pointing Vector (θ_pan, θ_tilt)
```

---

## 3. Mission States & Transition Logic

| Mission State | Description | Trigger Condition |
| :--- | :--- | :--- |
| **SEARCH & SCAN** | Pan/tilt gimbal sweeps target area while AI detector scans frames. | No active target detected (`Active Tracks = 0`). |
| **TARGET ACQUIRED** | Bounding box locked, persistent Track ID assigned, alert emitted. | Bounding box detected with confidence $\ge 35\%$. |
| **PRECISION TRACKING** | Closed-loop tracking active; environmental compensation adjustments applied continuously. | Target locked for $\ge 3$ consecutive frames. |
| **SIGNAL LOSS FALLBACK** | Position prediction vector holds last known trajectory for 10 frames. | Temporary target occlusion or frame drop. |
