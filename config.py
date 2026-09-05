"""
HAADS SIH 26050 - System Configuration
Central parameters for detection model, environmental thresholds, and simulation constants.
"""

import os

# Project Information
SIH_PROBLEM_ID = "26050"
PROJECT_TITLE = "High Altitude Performance Optimization and Robust Design of Anti-Drone System"
SYSTEM_MODE = "ACADEMIC_ENGINEERING_PROTOTYPE"

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
SYSTEM_DATA_FILE = os.path.join(BASE_DIR, "system_data.json")

# Model Configuration
# Primary Edge AI model requested: YOLO26n (with fallback/configurable model path)
PRIMARY_MODEL_NAME = "YOLO26n Edge AI — Object Detection & Tracking"
DEFAULT_YOLO_WEIGHTS = "yolo26n.pt"  # Will fallback to yolov8n.pt / yolo11n.pt if yolo26n.pt is unavailable
CUSTOM_DRONE_MODEL_PATH = os.path.join(MODELS_DIR, "custom_drone_yolo26n.pt")
CONFIDENCE_THRESHOLD = 0.35
IOU_THRESHOLD = 0.45

# Camera Settings
DEFAULT_CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_CENTER_X = FRAME_WIDTH // 2  # 320
FRAME_CENTER_Y = FRAME_HEIGHT // 2  # 240

# Environmental Ranges (High Altitude Simulation)
TEMP_MIN_C = -30.0
TEMP_MAX_C = 30.0
TEMP_DEFAULT_C = 20.0

PRESSURE_MIN_HPA = 500.0
PRESSURE_MAX_HPA = 1000.0
PRESSURE_DEFAULT_HPA = 950.0

WIND_MIN_KMH = 0.0
WIND_MAX_KMH = 60.0
WIND_DEFAULT_KMH = 5.0

VIBRATION_LEVELS = ["LOW", "MEDIUM", "HIGH"]
VIBRATION_DEFAULT = "LOW"

# Pan/Tilt Pointing Servo Limits
PAN_MIN_ANGLE = 0
PAN_MAX_ANGLE = 180
PAN_CENTER_ANGLE = 90

TILT_MIN_ANGLE = 0
TILT_MAX_ANGLE = 180
TILT_CENTER_ANGLE = 90

# Pointing Control Gain
BASE_KP_PAN = 0.15
BASE_KP_TILT = 0.15

# Preset Scenario Definitions
SCENARIOS = {
    "MODE 1 — NORMAL": {
        "temperature": 20.0,
        "pressure": 950.0,
        "wind_speed": 5.0,
        "vibration": "LOW",
        "description": "Standard ground / low altitude operating conditions."
    },
    "MODE 2 — EXTREME COLD": {
        "temperature": -20.0,
        "pressure": 700.0,
        "wind_speed": 10.0,
        "vibration": "MEDIUM",
        "description": "High-altitude sub-zero environment causing mechanical stiffness & sensor drift."
    },
    "MODE 3 — HIGH WIND": {
        "temperature": -5.0,
        "pressure": 750.0,
        "wind_speed": 40.0,
        "vibration": "MEDIUM",
        "description": "Strong cross-wind shear requiring active stabilization compensation."
    },
    "MODE 4 — EXTREME COMBINED": {
        "temperature": -20.0,
        "pressure": 650.0,
        "wind_speed": 40.0,
        "vibration": "HIGH",
        "description": "Severe high-altitude combination of sub-zero cold, low air pressure, heavy wind & structural vibration."
    }
}
