# HAADS — AI Models & Weights Guide

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Primary AI Model Specification

- **Model Engine**: YOLO26n Edge AI Object Detector (`yolo26n.pt`)
- **Inference Latency**: ~25-30 ms on standard x86 CPU / Edge devices.
- **Input Resolution**: $640 \times 480$ RGB optical video feed.
- **Confidence Threshold**: $0.35$ (35%) default detection cutoff.
- **IoU NMS Threshold**: $0.45$ (45%) non-maximum suppression overlap.

---

## 2. Directory Placement & Auto-Search Resolution

The system detector (`app/detector.py`) automatically searches for weight files in the following priority order:

1. `models/custom_drone_yolo26n.pt` (Custom fine-tuned drone weights)
2. `models/yolo26n.pt`
3. `yolo26n.pt` (Project root directory)
4. `app/yolo26n.pt`

If local weights are missing, Ultralytics auto-downloads standard pre-trained YOLO model weights.

---

## 3. Fine-Tuning Roadmap (Phase 2)

Future model fine-tuning will utilize specialized drone target datasets:
- **Dataset**: Custom annotated anti-drone dataset (UAVs, Quadcopters, Fixed-wing micro drones).
- **Target Platform**: Export to ONNX (`yolo26n.onnx`) and Hailo-8 HEF binary (`yolo26n.hef`) for 60+ FPS edge execution.
