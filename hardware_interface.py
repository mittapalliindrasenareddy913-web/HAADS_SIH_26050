"""
HAADS SIH 26050 - Hardware Interface Abstraction Module
Provides MQTT-based telemetry link with Wokwi ESP32 Hardware Simulation,
plus HTTP test endpoint fallback. Implements genuine 5-second heartbeat state machine:
WOKWI_OFFLINE, WOKWI_CONNECTING, WOKWI_ONLINE.
"""

import time
import json
import threading
import requests
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False


WOKWI_ONLINE_TIMEOUT = 5.0  # seconds


class HardwareInterface:
    def __init__(self, mode="AUTO", mqtt_broker="broker.hivemq.com", mqtt_port=1883):
        self.mode = mode
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic_telemetry = "isr/sih/26050/telemetry"
        self.mqtt_topic_servo = "isr/sih/26050/servo"

        self.last_heartbeat_time = 0.0
        self.mqtt_connected = False
        self.mqtt_client = None

        # Virtual/Real Actuator & Sensor Telemetry Cache
        self.pan_angle = 90
        self.tilt_angle = 90
        self.last_telemetry = {
            "device": "wokwi-esp32",
            "temperature": 20.0,
            "pressure": 950.0,
            "wind": 5.0,
            "vibration": 0.1,
            "pan": 90,
            "tilt": 90,
            "timestamp": 0
        }

        # Initialize MQTT Listener Non-blocking Thread
        if MQTT_AVAILABLE:
            self._start_mqtt_client()

        # Initialize Local HTTP Test Endpoint
        self._start_local_http_test_bridge()

    def _start_mqtt_client(self):
        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                self.mqtt_connected = True
                client.subscribe(self.mqtt_topic_telemetry)
                print(f"[HardwareInterface] Connected to MQTT broker '{self.mqtt_broker}'. Subscribed to '{self.mqtt_topic_telemetry}'.")
            else:
                self.mqtt_connected = False

        def on_message(client, userdata, msg):
            try:
                payload_str = msg.payload.decode("utf-8")
                data = json.loads(payload_str)
                self.process_telemetry_heartbeat(data)
            except Exception as e:
                pass

        def mqtt_start():
            try:
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2 if hasattr(mqtt, "CallbackAPIVersion") else None, client_id=f"HAADS-Python-{int(time.time())}")
                client.on_connect = on_connect
                client.on_message = on_message
                self.mqtt_client = client
                client.connect_async(self.mqtt_broker, self.mqtt_port, keepalive=30)
                client.loop_start()
            except Exception as e:
                print(f"[HardwareInterface] MQTT init note: {e}")

        t = threading.Thread(target=mqtt_start, daemon=True)
        t.start()

    def _start_local_http_test_bridge(self, port=8180):
        hw_self = self
        class TestBridgeHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                state = hw_self.get_state()
                self.wfile.write(json.dumps(state).encode('utf-8'))

            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                    hw_self.process_telemetry_heartbeat(data)
                    resp = {"status": "ACK", "heartbeat": "UPDATED"}
                except Exception as e:
                    resp = {"status": "ERROR", "error": str(e)}

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))

        def run_server():
            try:
                server_address = ('', port)
                httpd = HTTPServer(server_address, TestBridgeHandler)
                httpd.serve_forever()
            except Exception:
                pass

        t = threading.Thread(target=run_server, daemon=True)
        t.start()

    def process_telemetry_heartbeat(self, data):
        """Processes incoming telemetry heartbeat payload (from MQTT or HTTP test endpoint)."""
        self.last_heartbeat_time = time.time()
        if isinstance(data, dict):
            self.last_telemetry.update(data)
            if "pan" in data:
                self.pan_angle = int(data["pan"])
            if "tilt" in data:
                self.tilt_angle = int(data["tilt"])

    def get_connection_state(self):
        """
        Determines current state machine state:
        - WOKWI_ONLINE: Heartbeat received within last 5 seconds.
        - WOKWI_CONNECTING: Heartbeat received within 5-8 seconds.
        - WOKWI_OFFLINE: No heartbeat for >5 seconds (or never received).
        """
        if self.last_heartbeat_time <= 0:
            return "WOKWI_OFFLINE"
        
        elapsed = time.time() - self.last_heartbeat_time
        if elapsed <= WOKWI_ONLINE_TIMEOUT:
            return "WOKWI_ONLINE"
        elif elapsed <= WOKWI_ONLINE_TIMEOUT + 3.0:
            return "WOKWI_CONNECTING"
        else:
            return "WOKWI_OFFLINE"

    def get_state(self):
        state_str = self.get_connection_state()
        is_online = (state_str == "WOKWI_ONLINE")

        if is_online:
            connection_status = "WOKWI HARDWARE LINK: ONLINE"
            python_link_status = "PYTHON HARDWARE LINK: CONNECTED"
            active_control_mode = "ACTIVE CONTROL MODE: LIVE WOKWI"
            source = "WOKWI"
        elif state_str == "WOKWI_CONNECTING":
            connection_status = "WOKWI HARDWARE LINK: CONNECTING..."
            python_link_status = "PYTHON HARDWARE LINK: CONNECTING..."
            active_control_mode = "SOFTWARE SIMULATION FALLBACK"
            source = "SOFTWARE_SIMULATION"
        else:
            connection_status = "WOKWI HARDWARE LINK: OFFLINE"
            python_link_status = "PYTHON HARDWARE LINK: NOT CONNECTED"
            active_control_mode = "SOFTWARE SIMULATION FALLBACK"
            source = "SOFTWARE_SIMULATION"

        return {
            "state": state_str,
            "is_connected": is_online,
            "connection_status": connection_status,
            "python_link_status": python_link_status,
            "active_control_mode": active_control_mode,
            "source": source,
            "last_heartbeat_age_sec": round(time.time() - self.last_heartbeat_time, 1) if self.last_heartbeat_time > 0 else None,
            "pan_angle": self.pan_angle,
            "tilt_angle": self.tilt_angle,
            "telemetry": self.last_telemetry
        }

    def read_sensors(self):
        state_info = self.get_state()
        if state_info["is_connected"]:
            vib_val = float(self.last_telemetry.get("vibration", 0.1))
            vib_str = "HIGH" if vib_val > 0.6 else ("MEDIUM" if vib_val > 0.3 else "LOW")
            pots = {
                "temperature": float(self.last_telemetry.get("temperature", 20.0)),
                "pressure": float(self.last_telemetry.get("pressure", 950.0)),
                "wind": float(self.last_telemetry.get("wind", 5.0)),
                "vibration": vib_str
            }
            imu = {"accel_x": 0.01, "accel_y": 0.02, "accel_z": 9.81, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0}
            return imu, pots
        else:
            return {"accel_x": 0.01, "accel_y": 0.02, "accel_z": 9.81, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0}, \
                   {"temperature": 20.0, "pressure": 950.0, "wind": 5.0, "vibration": "LOW"}

    def send_pan_tilt(self, target_pan, target_tilt):
        self.pan_angle = int(np.clip(target_pan, 0, 180))
        self.tilt_angle = int(np.clip(target_tilt, 0, 180))

        if self.mqtt_client and self.mqtt_connected:
            try:
                cmd = f"SERVO:{self.pan_angle},{self.tilt_angle}"
                self.mqtt_client.publish(self.mqtt_topic_servo, cmd)
            except Exception:
                pass

        state_info = self.get_state()
        state_info["pan_angle"] = self.pan_angle
        state_info["tilt_angle"] = self.tilt_angle
        return state_info
