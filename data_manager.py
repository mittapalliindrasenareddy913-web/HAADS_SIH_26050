"""
HAADS SIH 26050 - Data Manager Module
Central structured state exchange manager.
Performs safe atomic JSON read and write operations on system_data.json.
"""

import os
import json
import time
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config


class SystemDataManager:
    def __init__(self, filepath=config.SYSTEM_DATA_FILE):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            default_data = self.get_default_state()
            self.save_state(default_data)

    def get_default_state(self):
        """Returns clean default state matching system_data.json specification."""
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "camera": {
                "status": "ONLINE",
                "fps": 0.0
            },
            "detection": {
                "model_name": "YOLO26n Edge AI — Object Detection & Tracking",
                "object_count": 0,
                "target_class": "N/A",
                "confidence": 0.0,
                "bbox": [],
                "track_id": None
            },
            "tracking": {
                "target_x": 320.0,
                "target_y": 240.0,
                "error_x": 0.0,
                "error_y": 0.0,
                "trajectory": []
            },
            "environment": {
                "temperature": 20.0,
                "pressure": 950.0,
                "wind_speed": 5.0,
                "vibration": "LOW",
                "humidity": 45.0,
                "source": "SOFTWARE_SIMULATION",
                "label": "SIMULATED ENVIRONMENT"
            },
            "imu": {
                "accel_x": 0.0,
                "accel_y": 0.0,
                "accel_z": 9.81,
                "gyro_x": 0.0,
                "gyro_y": 0.0,
                "gyro_z": 0.0
            },
            "compensation": {
                "temperature": True,
                "wind": True,
                "pressure": True,
                "vibration": True,
                "adaptive_gain": 0.15,
                "model_type": "PROTOTYPE SIMULATION MODEL"
            },
            "performance": {
                "uncompensated": {"detection": 98.0, "tracking": 95.0, "stabilization": 95.0, "overall": 95.7},
                "compensated": {"detection": 98.0, "tracking": 96.0, "stabilization": 97.0, "overall": 96.9},
                "improvement_pct": 1.2,
                "label": "SIMULATED PERFORMANCE ESTIMATE"
            },
            "health": {
                "camera": True,
                "ai": True,
                "tracking": True,
                "sensors": True,
                "pan_servo": True,
                "tilt_servo": True,
                "communication": False,
                "overall": 100
            },
            "hardware": {
                "source": "SOFTWARE_SIMULATION",
                "connection_status": "WOKWI CONNECTION: NOT CONNECTED",
                "pan_angle": 90,
                "tilt_angle": 90
            }
        }

    def save_state(self, state_dict):
        """Safely writes system state dictionary to system_data.json using atomic temp file replacement."""
        try:
            state_dict["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            temp_file = self.filepath + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, indent=2)
            os.replace(temp_file, self.filepath)
            return True
        except Exception as e:
            print(f"[SystemDataManager] JSON write error: {e}")
            return False

    def load_state(self):
        """Reads system state from system_data.json."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"[SystemDataManager] JSON read error: {e}, using default.")
            return self.get_default_state()
