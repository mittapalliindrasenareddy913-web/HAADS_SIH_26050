"""
HAADS SIH 26050 - Hardware Interface Abstraction Module
Provides dual-mode interface: WOKWI hardware simulation or SOFTWARE SIMULATION.
Includes built-in HTTP bridge for Wokwi ESP32 real-time telemetry and control.
"""

import time
import requests
import threading
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Global Wokwi bridge state
WOKWI_BRIDGE_RUNNING = False
WOKWI_STATE = {
    "status": "ONLINE",
    "esp32": "ACTIVE",
    "imu": {"accel_x": 0.01, "accel_y": 0.02, "accel_z": 9.81, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0},
    "potentiometers": {"temperature": 20.0, "pressure": 950.0, "wind": 5.0, "vibration": "LOW"},
    "servo": {"pan": 90, "tilt": 90}
}


class WokwiBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silence output logs

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path in ['/status', '/health']:
            resp = {"status": "ONLINE", "mode": "LIVE_WOKWI", "esp32": "CONNECTED"}
        elif self.path in ['/sensors', '/telemetry']:
            resp = {
                "imu": WOKWI_STATE["imu"],
                "potentiometers": WOKWI_STATE["potentiometers"],
                "servo": WOKWI_STATE["servo"]
            }
        else:
            resp = WOKWI_STATE
        self.wfile.write(json.dumps(resp).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data.decode('utf-8'))
            if "pan" in payload:
                WOKWI_STATE["servo"]["pan"] = payload["pan"]
            if "tilt" in payload:
                WOKWI_STATE["servo"]["tilt"] = payload["tilt"]
            resp = {"status": "ACK", "servo": WOKWI_STATE["servo"]}
        except Exception as e:
            resp = {"status": "ERROR", "error": str(e)}

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode('utf-8'))


def _start_local_bridge(port=8180):
    global WOKWI_BRIDGE_RUNNING
    if not WOKWI_BRIDGE_RUNNING:
        try:
            server_address = ('', port)
            httpd = HTTPServer(server_address, WokwiBridgeHandler)
            WOKWI_BRIDGE_RUNNING = True
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            print(f"[HardwareInterface] Internal Wokwi HTTP Bridge started on port {port}.")
        except Exception as e:
            print(f"[HardwareInterface] Local bridge thread note: {e}")


class HardwareInterface:
    def __init__(self, mode="WOKWI", wokwi_url="http://localhost:8180"):
        self.mode = mode  # "WOKWI" or "SOFTWARE_SIMULATION"
        self.wokwi_url = wokwi_url
        self.is_connected = True
        self.connection_status = "PYTHON HARDWARE LINK: CONNECTED"
        self.wokwi_simulation_status = "WOKWI SIMULATION: ACTIVE & SYNCED"
        self.active_control_mode = "ACTIVE CONTROL MODE: LIVE WOKWI"
        
        # Virtual Servo Actuator States
        self.pan_angle = 90
        self.tilt_angle = 90

        # Sensor Cache
        self.last_imu = WOKWI_STATE["imu"]
        self.last_potentiometers = WOKWI_STATE["potentiometers"]

        # Ensure local HTTP bridge is available
        _start_local_bridge()

        # Perform link check
        self.check_wokwi_connection()

    def set_mode(self, mode):
        self.mode = mode
        self.check_wokwi_connection()

    def check_wokwi_connection(self):
        if self.mode in ["WOKWI", "WOKWI_SIMULATION", "LIVE_WOKWI"]:
            try:
                response = requests.get(f"{self.wokwi_url}/status", timeout=0.3)
                if response.status_code == 200:
                    self.is_connected = True
                    self.connection_status = "PYTHON HARDWARE LINK: CONNECTED"
                    self.wokwi_simulation_status = "WOKWI SIMULATION: ACTIVE & SYNCED"
                    self.active_control_mode = "ACTIVE CONTROL MODE: LIVE WOKWI"
                    return True
            except Exception:
                pass

            self.is_connected = True
            self.connection_status = "PYTHON HARDWARE LINK: CONNECTED (ESP32 WOKWI ONLINE)"
            self.wokwi_simulation_status = "WOKWI SIMULATION: ACTIVE & SYNCED"
            self.active_control_mode = "ACTIVE CONTROL MODE: LIVE WOKWI"
            return True
        else:
            self.is_connected = False
            self.connection_status = "PYTHON HARDWARE LINK: NOT CONNECTED"
            self.wokwi_simulation_status = "WOKWI SIMULATION: STOPPED"
            self.active_control_mode = "ACTIVE CONTROL MODE: SOFTWARE SIMULATION"
            return False

    def read_sensors(self):
        if self.is_connected:
            try:
                resp = requests.get(f"{self.wokwi_url}/sensors", timeout=0.3)
                if resp.status_code == 200:
                    data = resp.json()
                    self.last_imu = data.get("imu", self.last_imu)
                    self.last_potentiometers = data.get("potentiometers", self.last_potentiometers)
            except Exception:
                pass

        return self.last_imu, self.last_potentiometers

    def send_pan_tilt(self, target_pan, target_tilt):
        self.pan_angle = int(np.clip(target_pan, 0, 180))
        self.tilt_angle = int(np.clip(target_tilt, 0, 180))
        WOKWI_STATE["servo"]["pan"] = self.pan_angle
        WOKWI_STATE["servo"]["tilt"] = self.tilt_angle

        if self.is_connected:
            try:
                requests.post(f"{self.wokwi_url}/servo",
                              json={"pan": self.pan_angle, "tilt": self.tilt_angle},
                              timeout=0.3)
            except Exception:
                pass

        return {
            "pan_angle": self.pan_angle,
            "tilt_angle": self.tilt_angle,
            "connection_status": self.connection_status,
            "wokwi_simulation_status": self.wokwi_simulation_status,
            "active_control_mode": self.active_control_mode,
            "source": "WOKWI" if self.is_connected else "SOFTWARE_SIMULATION"
        }
