"""
HAADS SIH 26050 - Subsystem Health & Threshold Alert Monitor
Monitors critical system modules, calculates health score,
and emits real-time alerts based on actual hardware state and environmental thresholds.
"""

import time


class HealthMonitor:
    def __init__(self):
        self.subsystems = {
            "camera": "ONLINE",
            "ai_detector": "ACTIVE",
            "tracking": "ACTIVE",
            "environment": "ACTIVE",
            "mpu6050": "NOT CONNECTED",
            "bme280": "NOT CONNECTED",
            "compensation": "ACTIVE",
            "servos": "NOT CONNECTED",
            "communication": "NOT CONNECTED"
        }
        self.alerts = []

    def update_health(self, camera_status, detector_status, tracking_count,
                      env_state, hw_state, perf_state):
        """
        Updates subsystem statuses and evaluates rule-based alerts.
        Hardware subsystem statuses strictly reflect real heartbeat/connection state.
        """
        self.alerts = []

        # 1. Camera Subsystem Status
        cam_str = str(camera_status).upper()
        if "ERROR" in cam_str:
            self.subsystems["camera"] = "ERROR"
            self.alerts.append({
                "level": "WARNING",
                "code": "CAMERA_UNAVAILABLE",
                "message": "Laptop webcam feed unavailable. Running software fallback."
            })
        else:
            self.subsystems["camera"] = "ONLINE"

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

        # 4. Hardware & Communication Status (Strictly derived from real Wokwi heartbeat!)
        is_wokwi_online = hw_state.get("is_connected", False)

        if is_wokwi_online:
            self.subsystems["communication"] = "CONNECTED"
            self.subsystems["mpu6050"] = "ONLINE"
            self.subsystems["bme280"] = "ONLINE"
            self.subsystems["servos"] = "ONLINE"
        else:
            self.subsystems["communication"] = "NOT CONNECTED"
            self.subsystems["mpu6050"] = "NOT CONNECTED"
            self.subsystems["bme280"] = "NOT CONNECTED"
            self.subsystems["servos"] = "NOT CONNECTED"
            self.alerts.append({
                "level": "INFO",
                "code": "WOKWI_OFFLINE",
                "message": "Wokwi simulation is not running or no telemetry heartbeat has been received. Software simulation fallback is active."
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

        if wind >= 25.0 and wind < 40.0:
            self.alerts.append({
                "level": "WARNING",
                "code": "HIGH_WIND",
                "message": f"High wind shear detected ({wind:.1f} km/h). Adaptive stabilization gain boosted."
            })
        elif wind >= 40.0:
            self.alerts.append({
                "level": "WARNING",
                "code": "EXTREME_WIND",
                "message": f"Extreme wind force detected ({wind:.1f} km/h). Aerodynamic drag compensation active."
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

        if not self.alerts:
            self.alerts.append({
                "level": "INFO",
                "code": "SYSTEM_NORMAL",
                "message": "All environmental parameters and operational subsystems operating normally."
            })

        # 6. Overall Health Score Calculation (0-100)
        health_points = 100
        if self.subsystems["camera"] == "ERROR":
            health_points -= 15
        if self.subsystems["ai_detector"] == "ERROR":
            health_points -= 30
        if not is_wokwi_online:
            health_points -= 10  # Minor reduction for running software simulation fallback

        overall_health = max(0, health_points)

        return {
            "overall_health_pct": overall_health,
            "subsystems": self.subsystems,
            "alerts": self.alerts,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
