"""
HAADS SIH 26050 - Hardware Interface Abstraction Module
Provides dual-mode interface: WOKWI hardware simulation or SOFTWARE SIMULATION.
Enforces presentation honesty: explicitly reports link status when offline.
"""

import time
import requests
import numpy as np


class HardwareInterface:
    def __init__(self, mode="SOFTWARE_SIMULATION", wokwi_url="http://localhost:8180"):
        self.mode = mode  # "WOKWI" or "SOFTWARE_SIMULATION"
        self.wokwi_url = wokwi_url
        self.connection_status = "PYTHON HARDWARE LINK: NOT CONNECTED"
        self.wokwi_simulation_status = "WOKWI SIMULATION: RUNNING SEPARATELY"
        self.active_control_mode = "ACTIVE CONTROL MODE: SOFTWARE SIMULATION"
        self.is_connected = False
        
        # Virtual Servo Actuator States
        self.pan_angle = 90
        self.tilt_angle = 90

        # Sensor Cache
        self.last_imu = {"accel_x": 0.01, "accel_y": 0.02, "accel_z": 9.81,
                         "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0}
        self.last_potentiometers = {"temperature": 20.0, "pressure": 950.0,
                                    "wind": 5.0, "vibration": "LOW"}

        # Attempt initial link check
        self.check_wokwi_connection()

    def check_wokwi_connection(self):
        """
        Attempts to establish contact with local Wokwi simulation server/bridge.
        Updates connection_status transparently.
        """
        if self.mode == "WOKWI":
            try:
                response = requests.get(f"{self.wokwi_url}/status", timeout=0.5)
                if response.status_code == 200:
                    self.is_connected = True
                    self.connection_status = "PYTHON HARDWARE LINK: CONNECTED"
                    self.active_control_mode = "ACTIVE CONTROL MODE: LIVE WOKWI"
                    return True
                else:
                    self.is_connected = False
                    self.connection_status = "PYTHON HARDWARE LINK: NOT CONNECTED"
                    self.active_control_mode = "ACTIVE CONTROL MODE: SOFTWARE SIMULATION"
            except Exception:
                self.is_connected = False
                self.connection_status = "PYTHON HARDWARE LINK: NOT CONNECTED"
                self.active_control_mode = "ACTIVE CONTROL MODE: SOFTWARE SIMULATION"
        else:
            self.is_connected = False
            self.connection_status = "PYTHON HARDWARE LINK: NOT CONNECTED"
            self.active_control_mode = "ACTIVE CONTROL MODE: SOFTWARE SIMULATION"

        return False

    def read_sensors(self):
        """
        Reads sensors from Wokwi if connected, otherwise returns deterministic software simulation fallback.
        """
        if self.is_connected:
            try:
                resp = requests.get(f"{self.wokwi_url}/sensors", timeout=0.5)
                if resp.status_code == 200:
                    data = resp.json()
                    self.last_imu = data.get("imu", self.last_imu)
                    self.last_potentiometers = data.get("potentiometers", self.last_potentiometers)
                    return self.last_imu, self.last_potentiometers
            except Exception:
                self.check_wokwi_connection()

        # Software Simulation Fallback
        return self.last_imu, self.last_potentiometers

    def send_pan_tilt(self, target_pan, target_tilt):
        """
        Sends target pan/tilt servo angles (clamped between 0° and 180°).
        """
        self.pan_angle = int(np.clip(target_pan, 0, 180))
        self.tilt_angle = int(np.clip(target_tilt, 0, 180))

        if self.is_connected:
            try:
                requests.post(f"{self.wokwi_url}/servo",
                              json={"pan": self.pan_angle, "tilt": self.tilt_angle},
                              timeout=0.3)
            except Exception:
                self.check_wokwi_connection()

        return {
            "pan_angle": self.pan_angle,
            "tilt_angle": self.tilt_angle,
            "connection_status": self.connection_status,
            "wokwi_simulation_status": self.wokwi_simulation_status,
            "active_control_mode": self.active_control_mode,
            "source": "WOKWI" if self.is_connected else "SOFTWARE_SIMULATION"
        }
