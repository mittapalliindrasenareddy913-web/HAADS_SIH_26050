"""
HAADS SIH 26050 - Main Application Orchestrator
Entry point for Streamlit web server. Initializes camera, YOLO26n Edge AI, tracker,
environmental simulator, compensation engine, performance engine, health monitor,
and Wokwi hardware interface abstraction.
"""

import sys
import os
import streamlit as st

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from camera import CameraManager
from detector import YOLO26nDetector
from tracker import PersistentTracker
from environment import EnvironmentSimulator
from compensation import EnvironmentalCompensationEngine
from performance import PerformanceEngine
from health_monitor import HealthMonitor
from hardware_interface import HardwareInterface
from data_manager import SystemDataManager
from dashboard import render_dashboard


@st.cache_resource
def load_ai_and_camera():
    """Caches heavy resources (Webcam and YOLO26n Edge AI engine)."""
    camera_mgr = CameraManager(camera_index=config.DEFAULT_CAMERA_INDEX)
    camera_mgr.start()

    detector = YOLO26nDetector(
        model_name="yolo26n",
        custom_weights_path=config.CUSTOM_DRONE_MODEL_PATH,
        conf_threshold=config.CONFIDENCE_THRESHOLD
    )

    tracker = PersistentTracker(
        max_distance=100,
        max_lost=10,
        frame_width=config.FRAME_WIDTH,
        frame_height=config.FRAME_HEIGHT
    )

    return camera_mgr, detector, tracker


def main():
    camera_mgr, detector, tracker = load_ai_and_camera()

    # Session State management for dynamic simulation engines
    if "env_sim" not in st.session_state:
        st.session_state["env_sim"] = EnvironmentSimulator()
    if "comp_engine" not in st.session_state:
        st.session_state["comp_engine"] = EnvironmentalCompensationEngine()
    if "perf_engine" not in st.session_state:
        st.session_state["perf_engine"] = PerformanceEngine()
    if "health_mon" not in st.session_state:
        st.session_state["health_mon"] = HealthMonitor()
    if "hw_interface" not in st.session_state:
        st.session_state["hw_interface"] = HardwareInterface(mode="WOKWI")
    if "data_mgr" not in st.session_state:
        st.session_state["data_mgr"] = SystemDataManager()

    render_dashboard(
        camera_mgr,
        detector,
        tracker,
        st.session_state["env_sim"],
        st.session_state["comp_engine"],
        st.session_state["perf_engine"],
        st.session_state["health_mon"],
        st.session_state["hw_interface"],
        st.session_state["data_mgr"]
    )


if __name__ == "__main__":
    main()
