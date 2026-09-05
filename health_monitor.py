"""
HAADS SIH 26050 - Subsystem Health & Threshold Alert Monitor
Monitors 9 critical system modules, calculates deterministic health score,
and emits real-time rule-based alerts based on physical environmental thresholds.
"""

import time


class HealthMonitor:
    def __init__(self):
        self.subsystems = {
            "camera": "ONLINE",
            "ai_detector": "ACTIVE",
            "tracking": "ACTIVE",
            "environment": "ACTIVE",
            "mpu6050": "ONLINE",
            "bme280": "ONLINE",
            "compensation": "ACTIVE",
            "servos": "ONLINE",
            "communication": "CONNECTED"
        }
        self.alerts = []

    def update_health(self, camera_status, detector_status, tracking_count,
                      env_state, hw_state, perf_state):
        """
        Updates subsystem statuses and evaluates rule-based alerts.
        """
        self.alerts = []

        # 1. Camera Status
        cam_str = str(camera_status).upper()
        if "ONLINE" in cam_str or "ACTIVE" in cam_str or "BROWSER" in cam_str or "UPLOAD" in cam_str or "STANDBY" in cam_str or "SIMULATED" in cam_str:
            self.subsystems["camera"] = "ONLINE"
        else:
            self.subsystems["camera"] = "ERROR"
            self.alerts.append({
                "level": "WARNING",
                "code": "CAMERA_UNAVAILABLE",
                "message": "Laptop webcam feed unavailable. Running software fallback."
            })

        # 2. AI Detector Status
        self.subsystems["ai_detector"] = "ACTIVE" if detector_status else "ERROR"
        if self.subsystems["ai_detector"] == "ERROR":
            self.alerts.append({
                "level": "ERROR",
                "code": "AI_MODEL_ERROR",
                "message": "YOLO26n Edge AI detector engine initialization error."
            })

        # 3. Tracking Status
        if tracking_count > 0:
            self.subsystems["tracking"] = "ACTIVE"
        else:
            self.subsystems["tracking"] = "SEARCHING"

        # 4. Hardware & Communication Status
        hw_source = hw_state.get("source", "SOFTWARE_SIMULATION")
        hw_conn = hw_state.get("connection_status", "")

        if hw_source == "WOKWI" or "CONNECTED" in hw_conn:
            self.subsystems["communication"] = "CONNECTED"
            self.subsystems["mpu6050"] = "ONLINE"
            self.subsystems["bme280"] = "ONLINE"
            self.subsystems["servos"] = "ONLINE"
        else:
            self.subsystems["communication"] = "NOT CONNECTED"
            self.subsystems["mpu6050"] = "SOFTWARE_SIMULATION"
            self.subsystems["bme280"] = "SOFTWARE_SIMULATION"
            self.subsystems["servos"] = "SOFTWARE_SIMULATION"
            self.alerts.append({
                "level": "INFO",
                "code": "WOKWI_OFFLINE",
                "message": "Wokwi serial/HTTP link NOT CONNECTED. Active mode: SOFTWARE SIMULATION FALLBACK."
            })

        # 5. Environmental Threshold Alerts
        temp = env_state.get("temperature", 20.0)
        wind = env_state.get("wind_speed", 5.0)
        vib = env_state.get("vibration", "LOW")

        if temp <= -15.0:
            self.alerts.append({
                "level": "WARNING",
                "code": "EXTREME_COLD",
                "message": f"Sub-zero extreme cold ({temp:.1f}°C). Mechanical stiffness compensation active."
            })

        if wind >= 35.0:
            self.alerts.append({
                "level": "WARNING",
                "code": "HIGH_WIND_SHEAR",
                "message": f"High wind shear detected ({wind:.1f} km/h). Adaptive stabilization gain boosted."
            })

        if temp <= -15.0 and wind >= 35.0:
            self.alerts.append({
                "level": "CRITICAL",
                "code": "EXTREME_COMBINED_HAZARD",
                "message": "Critical severe high-altitude hazard! Extreme cold combined with high wind shear."
            })

        if vib == "HIGH":
            self.alerts.append({
                "level": "WARNING",
                "code": "HIGH_VIBRATION",
                "message": "High structural vibration detected. High-frequency filtering active."
            })

        # 6. Overall Health Score Calculation (0-100)
        health_points = 100
        if self.subsystems["camera"] == "ERROR":
            health_points -= 20
        if self.subsystems["ai_detector"] == "ERROR":
            health_points -= 30
        if perf_state.get("compensated", {}).get("overall", 100) < 60:
            health_points -= 15
            self.alerts.append({
                "level": "WARNING",
                "code": "PERFORMANCE_DEGRADED",
                "message": "Overall system performance estimated below 60% due to severe environmental stress."
            })

        overall_health = max(0, health_points)

        return {
            "overall_health_pct": overall_health,
            "subsystems": self.subsystems,
            "alerts": self.alerts,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
