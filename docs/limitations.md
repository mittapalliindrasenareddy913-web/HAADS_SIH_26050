# HAADS — Prototype Limitations & Scope Boundaries

**Project Name**: HAADS (High-Altitude Ruggedized Anti-Drone Detection & Precision Tracking System)  
**SIH Problem Statement ID**: 26050  
**Team Name**: DEVOPS  

---

## 1. Scope Transparency Statement

To ensure clear academic and technical integrity, the capabilities of the current HAADS implementation are explicitly categorized into **Current Prototype Scope** versus **Future Hardware Scope**.

---

## 2. Current Prototype Scope & Technical Limitations

1. **YOLO26n Base Weights**: Current prototype utilizes standard YOLO26n pre-trained weights for real-time edge performance on CPU/laptop architectures. Fine-tuning on specialized drone-only datasets is planned for Phase 2.
2. **Camera Sensor Input**: Operational performance depends on the optical quality, field of view, and resolution of the attached webcam or browser stream.
3. **Hardware Simulation**: Servo actuation and sensor telemetry (BME280 / MPU6050) are simulated via the Wokwi ESP32 MQTT simulation suite (`wokwi/`).

---

## 3. Mitigation & Future Enhancements

- **Model Optimization**: TensorRT and ONNX runtime export for low-latency inference on AI accelerators.
- **Physical Gimbal Integration**: Direct PWM and CAN-bus control for heavy pan/tilt optics.
- **Thermal Optics Integration**: Dual IR/optical fusion sensor head to defeat camouflage and low-light environments.
