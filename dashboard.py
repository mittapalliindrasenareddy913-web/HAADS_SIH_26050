"""
HAADS SIH 26050 - Streamlit Engineering Dashboard Module
Renders the 11-section engineering dashboard for High Altitude Anti-Drone System prototype.
SIH Problem Statement 26050 Alignment: High Altitude Performance Optimization and Robust Design.
Includes Native HTML5 device-local webcam component, YOLO26n Edge AI detection, mobile phone alerts, and Wokwi MQTT telemetry.
"""

import streamlit as st
import streamlit.components.v1 as components
import cv2
import json
import time
import os
import math
import base64
import numpy as np

import config
from environment import EnvironmentSimulator
from compensation import EnvironmentalCompensationEngine
from performance import PerformanceEngine
from health_monitor import HealthMonitor
from hardware_interface import HardwareInterface
from data_manager import SystemDataManager
from detector import YOLO26nDetector
from tracker import PersistentTracker
from camera import filter_camera_devices, PHONE_KEYWORDS, LAPTOP_KEYWORDS

COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_component")
device_camera_component = components.declare_component("device_camera", path=COMPONENT_DIR)


def create_synthetic_drone_frame(target_x, target_y):
    """Generates a synthetic high-contrast quadcopter drone target frame."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    for y in range(0, 480, 40):
        cv2.line(frame, (0, y), (640, y), (25, 30, 35), 1)
    for x in range(0, 640, 40):
        cv2.line(frame, (x, 0), (x, 480), (25, 30, 35), 1)

    tx, ty = int(target_x), int(target_y)
    cv2.circle(frame, (tx, ty), 12, (0, 200, 255), -1)
    cv2.line(frame, (tx - 35, ty - 25), (tx + 35, ty + 25), (180, 180, 180), 3)
    cv2.line(frame, (tx - 35, ty + 25), (tx + 35, ty - 25), (180, 180, 180), 3)
    for rx, ry in [(tx - 35, ty - 25), (tx + 35, ty - 25), (tx - 35, ty + 25), (tx + 35, ty + 25)]:
        cv2.circle(frame, (rx, ry), 15, (0, 255, 255), 2)
        cv2.circle(frame, (rx, ry), 4, (0, 255, 255), -1)

    cv2.putText(frame, "SYNTHETIC TARGET -- SIMULATION ONLY", (tx - 110, max(20, ty - 35)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
    return frame


def render_dashboard(camera_mgr, detector, tracker, env_sim, comp_engine, perf_engine, health_mon, hw_interface, data_mgr):
    st.set_page_config(
        page_title="HAADS - High Altitude Edge AI System",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for dark engineering styling
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .stMetric { background-color: #1e222d; padding: 12px; border-radius: 8px; border: 1px solid #2d313e; }
        .real-badge { background-color: #0e6251; color: #a3e4d7; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
        .sim-badge { background-color: #7d6608; color: #f9e79f; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
        .offline-badge { background-color: #641e16; color: #fadbd8; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
        .waiting-badge { background-color: #7d6608; color: #f9e79f; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
        .alert-box { padding: 10px; border-radius: 6px; margin-bottom: 8px; }
        .alert-WARNING { background-color: #78281f; color: #fadbd8; border-left: 5px solid #e74c3c; }
        .alert-CRITICAL { background-color: #641e16; color: #f5b7b1; border-left: 5px solid #922b21; font-weight: bold; }
        .alert-INFO { background-color: #1b4f72; color: #d4efdf; border-left: 5px solid #3498db; }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🎯 HIGH ALTITUDE EDGE AI SYSTEM")
    st.caption("High Altitude Performance Optimization and Robust Design of Anti-Drone System | SIH Problem Statement 26050")
    st.info("💡 **Objective**: Environmental compensation and robust precision tracking for reliable high-altitude operation.")
    st.markdown("---")

    # Read current Wokwi state (strictly driven by real MQTT heartbeat)
    hw_state = hw_interface.get_state()
    is_wokwi_online = hw_state.get("is_connected", False)

    # ----------------------------------------------------
    # SIDEBAR: CONTROLS & ENVIRONMENT PRESETS
    # ----------------------------------------------------
    st.sidebar.header("🕹️ System Controls")
    
    st.sidebar.subheader("High-Altitude Scenarios")
    selected_scenario = st.sidebar.selectbox(
        "Select Environmental Preset:",
        list(config.SCENARIOS.keys())
    )

    if st.sidebar.button("Apply Preset Scenario"):
        env_sim.load_scenario(selected_scenario)
        st.sidebar.success(f"Loaded {selected_scenario}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Manual Environmental Sliders")

    temp_val = st.sidebar.slider("Temperature (°C)", config.TEMP_MIN_C, config.TEMP_MAX_C, float(env_sim.temperature), step=1.0)
    press_val = st.sidebar.slider("Barometric Pressure (hPa)", config.PRESSURE_MIN_HPA, config.PRESSURE_MAX_HPA, float(env_sim.pressure), step=10.0)
    wind_val = st.sidebar.slider("Wind Speed (km/h)", config.WIND_MIN_KMH, config.WIND_MAX_KMH, float(env_sim.wind_speed), step=1.0)
    vib_val = st.sidebar.selectbox("Structural Vibration Level", config.VIBRATION_LEVELS, index=config.VIBRATION_LEVELS.index(env_sim.vibration))

    env_sim.set_parameters(temp=temp_val, pressure=press_val, wind=wind_val, vibration=vib_val)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Compensation Engine Toggles")
    comp_engine.enable_temp_comp = st.sidebar.checkbox("Enable Temperature Compensation", value=comp_engine.enable_temp_comp)
    comp_engine.enable_wind_comp = st.sidebar.checkbox("Enable Wind Compensation", value=comp_engine.enable_wind_comp)
    comp_engine.enable_pressure_comp = st.sidebar.checkbox("Enable Pressure Compensation", value=comp_engine.enable_pressure_comp)
    comp_engine.enable_vibration_comp = st.sidebar.checkbox("Enable Vibration Compensation", value=comp_engine.enable_vibration_comp)

    st.sidebar.markdown("---")
    st.sidebar.caption("🧪 **Wokwi Test Telemetry Helper**")
    if st.sidebar.button("Simulate Wokwi Heartbeat Signal"):
        hw_interface.process_telemetry_heartbeat({
            "device": "wokwi-esp32",
            "status": "online",
            "temperature": float(env_sim.temperature),
            "pressure": float(env_sim.pressure),
            "wind": float(env_sim.wind_speed),
            "vibration": 0.2,
            "pan": 95,
            "tilt": 85,
            "timestamp": time.time()
        })
        st.sidebar.success("Sent simulated MQTT Heartbeat to Python!")

    # ----------------------------------------------------
    # TARGET INPUT SELECTION
    # ----------------------------------------------------
    target_mode = st.radio(
        "Select Target Input Source:",
        ["Start Live Camera", "Synthetic Drone Target (Simulation Only)"],
        index=0,
        horizontal=True
    )

    demo_proxy_mode = st.checkbox("📱 Enable Demo Proxy Target Mode (Use Cell Phone / Object as Drone-Proxy Test)", value=True)

    # Initialize Real System Pipeline State Variables
    camera_state = "INITIALIZING"
    camera_device_label = "LOCAL DEVICE CAMERA"
    yolo_state = "WAITING"
    tracking_state = "WAITING"
    target_cls = "NO TARGET DETECTED"
    confidence = None
    track_id = None
    bbox = []
    target_x, target_y = 320.0, 240.0
    error_x, error_y = 0.0, 0.0
    latency_ms = 0.0
    cam_source = "LIVE LAPTOP CAMERA"
    cell_phone_detected = False
    cell_phone_conf = None
    cell_phone_tid = None
    frame_count = 0
    fps = 0.0
    frame_width = 0
    frame_height = 0
    track_state = "live"
    last_callback_error = "None"

    # ----------------------------------------------------
    # 2. TARGET DETECTION & IDENTIFICATION
    # ----------------------------------------------------
    st.subheader("2. Target Detection & Identification")
    col_det1, col_det2 = st.columns([6, 4])

    if target_mode == "Start Live Camera":
        cam_source = "LIVE LOCAL CAMERA"
        
        with col_det1:
            st.markdown("#### 📷 LOCAL DEVICE CAMERA FEED")
            camera_data = device_camera_component(key="device_local_cam")

        if isinstance(camera_data, dict):
            camera_status = camera_data.get("status", "INITIALIZING")
            camera_device_label = camera_data.get("device_label", "LOCAL DEVICE CAMERA")
            frame_width = camera_data.get("width", 640)
            frame_height = camera_data.get("height", 480)
            frame_count = camera_data.get("frame_count", 0)
            track_state = camera_data.get("track_state", "live")
            raw_frame_b64 = camera_data.get("frame", None)
            cam_err = camera_data.get("error", None)

            if cam_err:
                last_callback_error = str(cam_err)

            if camera_status == "ONLINE" and raw_frame_b64:
                camera_state = "ONLINE"

                if isinstance(raw_frame_b64, str) and "," in raw_frame_b64:
                    try:
                        header, b64_data = raw_frame_b64.split(",", 1)
                        img_bytes = base64.b64decode(b64_data)
                        np_arr = np.frombuffer(img_bytes, np.uint8)
                        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                        if img is not None:
                            # 1. Run YOLO inference on real camera frame
                            t0 = time.time()
                            if detector and detector.model_loaded:
                                yolo_state = "ACTIVE"
                                raw_detections = detector.detect(img)
                                latency_ms = (time.time() - t0) * 1000.0
                            else:
                                yolo_state = "ERROR" if detector else "WAITING"
                                raw_detections = []

                            # 2. Update persistent tracker with real detections
                            if len(raw_detections) == 0:
                                tracking_state = "WAITING"
                                target_cls = "NO TARGET DETECTED"
                                confidence = None
                                track_id = None
                                bbox = []
                                target_x, target_y = 320.0, 240.0
                                error_x, error_y = 0.0, 0.0
                            else:
                                active_tracks = tracker.update(raw_detections)
                                primary_target = tracker.get_primary_target()

                                if primary_target:
                                    tracking_state = "ACTIVE"
                                    target_x = float(primary_target.target_x)
                                    target_y = float(primary_target.target_y)
                                    error_x = float(primary_target.error_x)
                                    error_y = float(primary_target.error_y)
                                    track_id = primary_target.track_id
                                    confidence = float(primary_target.confidence)
                                    target_cls = primary_target.class_name
                                    bbox = primary_target.bbox
                                else:
                                    tracking_state = "ACQUIRING"
                                    first_det = raw_detections[0]
                                    target_cls = first_det["class_name"]
                                    confidence = float(first_det["confidence"])
                                    bbox = first_det["bbox"]
                                    target_x, target_y = float(first_det["center"][0]), float(first_det["center"][1])
                                    error_x = target_x - 320.0
                                    error_y = target_y - 240.0
                                    track_id = None

                                # Check if cell phone is detected
                                for det in raw_detections:
                                    cname = det["class_name"].lower()
                                    if cname in ["cell phone", "mobile phone", "phone"]:
                                        cell_phone_detected = True
                                        cell_phone_conf = float(det["confidence"])
                                        cell_phone_tid = track_id if track_id else 1
                                        break
                    except Exception as e:
                        last_callback_error = f"{type(e).__name__}: {str(e)}"
            elif "PERMISSION" in str(camera_status):
                camera_state = "CAMERA PERMISSION DENIED"
            elif "NOT SUPPORTED" in str(camera_status):
                camera_state = "CAMERA API NOT SUPPORTED"
            elif "NO LOCAL" in str(camera_status) or "NO DEVICE" in str(camera_status):
                camera_state = "NO LOCAL CAMERA FOUND"
            else:
                camera_state = str(camera_status)
        else:
            camera_state = "INITIALIZING (AWAITING WEBCAM FRAMES)"

    else:
        # Synthetic Target Mode (Explicit Simulation Fallback)
        cam_source = "SYNTHETIC TARGET"
        st.markdown("<span class='sim-badge'>SYNTHETIC DRONE TARGET — SIMULATION ONLY</span>", unsafe_allow_html=True)
        c_sim1, c_sim2 = st.columns(2)
        with c_sim1:
            sim_target_x = st.slider("Simulated Target X Position", 50, 590, 420, key="sim_tx")
        with c_sim2:
            sim_target_y = st.slider("Simulated Target Y Position", 50, 430, 180, key="sim_ty")
        
        synth_frame = create_synthetic_drone_frame(sim_target_x, sim_target_y)
        rgb_synth = cv2.cvtColor(synth_frame, cv2.COLOR_BGR2RGB)
        
        with col_det1:
            st.image(rgb_synth, channels="RGB", use_container_width=True)

        camera_state = "ONLINE (SIMULATED)"
        camera_device_label = "SYNTHETIC TARGET GENERATOR"
        yolo_state = "ACTIVE"
        tracking_state = "ACTIVE"
        target_cls = "SYNTHETIC DRONE TARGET"
        confidence = 0.94
        track_id = 1
        target_x, target_y = float(sim_target_x), float(sim_target_y)
        error_x = target_x - 320.0
        error_y = target_y - 240.0
        latency_ms = 12.5

    with col_det2:
        st.markdown("#### Detection Result Summary")
        st.write(f"• **Model**: `{detector.model_name}`")
        st.write(f"• **Input Source**: `{cam_source}`")
        
        # Real Camera Status Badge
        if camera_state == "ONLINE":
            st.markdown("• **Camera Status**: <span class='real-badge'>🟢 ONLINE (LOCAL DEVICE CAMERA)</span>", unsafe_allow_html=True)
        elif camera_state in ["INITIALIZING", "CONNECTING", "WAITING"]:
            st.markdown("• **Camera Status**: <span class='waiting-badge'>🟡 INITIALIZING (AWAITING WEBCAM FRAMES)</span>", unsafe_allow_html=True)
        elif "WAITING FOR PERMISSION" in camera_state:
            st.markdown("• **Camera Status**: <span class='waiting-badge'>🟡 WAITING FOR PERMISSION</span>", unsafe_allow_html=True)
        elif "PERMISSION" in camera_state:
            st.markdown("• **Camera Status**: <span class='offline-badge'>⛔ PERMISSION DENIED</span>", unsafe_allow_html=True)
        elif "DEVICE" in camera_state or "NO LOCAL" in camera_state:
            st.markdown("• **Camera Status**: <span class='offline-badge'>❌ NO DEVICE DETECTED</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"• **Camera Status**: <span class='offline-badge'>🔴 {camera_state}</span>", unsafe_allow_html=True)

        # Real YOLO Detection Values (No hardcoded values!)
        st.write(f"• **Detected Object**: **`{target_cls}`**")
        st.write(f"• **Confidence Score**: **`{f'{confidence * 100:.1f}%' if confidence is not None else '—'}`**")
        st.write(f"• **Track Object ID**: **`{track_id if track_id is not None else '—'}`**")
        st.write(f"• **Inference Latency**: `{f'{latency_ms:.1f} ms' if latency_ms > 0 else '—'}`")
        
        st.write("")

        # ----------------------------------------------------
        # 🚨 REAL-TIME MOBILE PHONE DETECTION ALERT
        # ----------------------------------------------------
        is_phone_target = (cell_phone_detected or "cell phone" in target_cls.lower() or "phone" in target_cls.lower())
        
        if is_phone_target and target_mode == "Start Live Camera":
            display_conf_str = f"{cell_phone_conf * 100:.1f}%" if cell_phone_conf else (f"{confidence * 100:.1f}%" if confidence else "N/A")
            display_tid_str = str(cell_phone_tid if cell_phone_tid else (track_id if track_id else 1))

            st.markdown(f"""
                <div style="background-color: #78281f; padding: 14px; border-radius: 8px; border-left: 6px solid #e74c3c; margin-bottom: 12px;">
                    <h3 style="color: #fadbd8; margin: 0; font-size: 1.2em;">🚨 TARGET ALERT</h3>
                    <hr style="border: 0.5px solid #e74c3c; margin: 6px 0;">
                    <p style="color: #ffffff; font-weight: bold; margin: 2px 0;">Mobile Phone Detected</p>
                    <p style="color: #fadbd8; margin: 2px 0;">• Object: <b>CELL PHONE</b></p>
                    <p style="color: #fadbd8; margin: 2px 0;">• Confidence: <b>{display_conf_str}</b></p>
                    <p style="color: #fadbd8; margin: 2px 0;">• Track ID: <b>{display_tid_str}</b></p>
                    <p style="color: #fadbd8; margin: 2px 0;">• Source: <b>LIVE LOCAL CAMERA</b></p>
                </div>
            """, unsafe_allow_html=True)

        if demo_proxy_mode and is_phone_target and target_mode == "Start Live Camera":
            st.markdown("""
                <div style="background-color: #1b4f72; padding: 12px; border-radius: 6px; border-left: 4px solid #3498db; margin-bottom: 12px;">
                    <p style="color: #d4efdf; font-weight: bold; margin: 0;">📱 Mobile Phone → Drone Image Proxy Demonstration</p>
                    <p style="color: #ffffff; margin: 3px 0;">• Physical Object: <b>CELL PHONE</b></p>
                    <p style="color: #ffffff; margin: 2px 0;">• Displayed Target: <b>DRONE IMAGE</b></p>
                    <p style="color: #ffffff; margin: 2px 0;">• Target Role: <b>DRONE-PROXY TEST OBJECT</b></p>
                    <p style="color: #ffffff; margin: 2px 0;">• Status: <b>SIMULATION / DEMONSTRATION ONLY</b></p>
                </div>
            """, unsafe_allow_html=True)

    # 🔍 EXPANDABLE CAMERA DIAGNOSTICS
    with st.expander("🔍 Camera / Browser Component Diagnostics & Status Debugger", expanded=False):
        c_diag1, c_diag2 = st.columns(2)
        with c_diag1:
            st.write(f"• **Camera API**: `HTML5 navigator.mediaDevices.getUserMedia`")
            st.write(f"• **Active Camera Device**: `{camera_device_label}`")
            st.write(f"• **Camera Status**: `{camera_state}`")
            st.write(f"• **Total Frames Received**: `{frame_count}`")
            st.write(f"• **Frame Resolution**: `{f'{frame_width}x{frame_height} px' if frame_width > 0 else 'N/A'}`")
            st.write(f"• **Track State**: `{track_state}`")
            st.write(f"• **Last Component Error**: `{last_callback_error}`")
        with c_diag2:
            st.write(f"• **YOLO26n Engine State**: `{yolo_state}`")
            st.write(f"• **Last Object Detected**: `{target_cls}`")
            st.write(f"• **Last Confidence Score**: `{f'{confidence * 100:.1f}%' if confidence is not None else '—'}`")
            st.write(f"• **Tracking Status**: `{tracking_state}`")
            st.write(f"• **Track Object ID**: `{track_id if track_id is not None else '—'}`")
            st.write(f"• **Inference Latency**: `{f'{latency_ms:.1f} ms' if latency_ms > 0 else '—'}`")

    st.markdown("---")

    # ----------------------------------------------------
    # SYSTEM PIPELINE COMPUTATION
    # ----------------------------------------------------
    # Environmental state & compensation calculations
    env_state = env_sim.get_state()
    comp_state = comp_engine.calculate_compensation(env_state, error_x, error_y)

    # Pointing calculation
    base_pan, base_tilt = 90, 90
    pan_calc = base_pan + comp_state["metrics"]["pan_correction_deg"]
    tilt_calc = base_tilt + comp_state["metrics"]["tilt_correction_deg"]

    hw_state = hw_interface.send_pan_tilt(pan_calc, tilt_calc)

    # Performance evaluation
    target_error_dist = math.hypot(error_x, error_y)
    perf_results = perf_engine.evaluate_performance(env_state, comp_state, target_error_dist)

    # Health & Alerts Evaluation (Derived strictly from real state!)
    health_results = health_mon.update_health(
        camera_state, yolo_state, tracking_state,
        env_state, hw_state, perf_results
    )

    # Save state to system_data.json
    full_state_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "camera": {"status": camera_state, "device_label": camera_device_label, "fps": round(fps, 1), "source": cam_source, "frames_received": frame_count},
        "detection": {
            "model_name": detector.model_name,
            "target_class": target_cls,
            "confidence": confidence,
            "bbox": bbox,
            "track_id": track_id
        },
        "tracking": {
            "target_x": target_x, "target_y": target_y,
            "error_x": error_x, "error_y": error_y
        },
        "environment": env_state,
        "compensation": comp_state,
        "performance": perf_results,
        "health": health_results,
        "hardware": hw_state
    }
    data_mgr.save_state(full_state_data)

    # ----------------------------------------------------
    # 1. SYSTEM OVERVIEW
    # ----------------------------------------------------
    st.subheader("1. System Overview")
    ov1, ov2, ov3, ov4, ov5 = st.columns(5)
    with ov1:
        st.metric("System Mode", "PROTOTYPE", help="Academic Engineering Prototype (Non-destructive)")
    with ov2:
        st.metric("System Health", f"{health_results['overall_health_pct']}%")
    with ov3:
        st.metric("Detection Status", "ACTIVE" if (target_cls != "NO TARGET DETECTED") else "NO TARGET")
    with ov4:
        st.metric("Tracking Status", f"Track ID-{track_id}" if track_id is not None else "NO ACTIVE TARGET")
    with ov5:
        st.metric("Overall Performance", f"{perf_results['compensated']['overall']}%", delta=f"+{perf_results['overall_improvement_pct']}% Comp")

    st.markdown("---")

    # ----------------------------------------------------
    # 3. TARGET TRACKING & PRECISION POINTING
    # ----------------------------------------------------
    st.subheader("3. Target Tracking & Precision Pointing")
    tp1, tp2, tp3 = st.columns(3)
    with tp1:
        st.metric("Target Center X / Y", f"({target_x:.1f}, {target_y:.1f})" if target_cls != "NO TARGET DETECTED" else "N/A")
        st.metric("Tracking Error Distance", f"{target_error_dist:.1f} px" if target_cls != "NO TARGET DETECTED" else "0.0 px")
    with tp2:
        st.metric("Pointing Error X", f"{error_x:+.1f} px" if target_cls != "NO TARGET DETECTED" else "0.0 px")
        st.metric("Pointing Error Y", f"{error_y:+.1f} px" if target_cls != "NO TARGET DETECTED" else "0.0 px")
    with tp3:
        actuator_label = "WOKWI PAN/TILT SERVO" if is_wokwi_online else "Virtual / Simulated Pan-Tilt"
        st.metric("Pan Servo Angle", f"{hw_state['pan_angle']}°", help=actuator_label)
        st.metric("Tilt Servo Angle", f"{hw_state['tilt_angle']}°", help=actuator_label)

    st.caption(f"Actuator Mode: **{actuator_label}** | Adaptive Stabilization Gain: **{comp_state['metrics']['adaptive_stabilization_gain']}**")

    st.markdown("---")

    # ----------------------------------------------------
    # 4. HIGH-ALTITUDE ENVIRONMENT
    # ----------------------------------------------------
    st.subheader("4. High-Altitude Environment")
    st.markdown("<span class='sim-badge'>PROTOTYPE SIMULATION MODEL</span>", unsafe_allow_html=True)
    st.write("")
    st.info(f"Active Scenario: **{env_state['active_scenario']}** — *{config.SCENARIOS.get(env_state['active_scenario'], {}).get('description', '')}*")

    e1, e2, e3, e4, e5 = st.columns(5)
    with e1:
        st.metric("Temperature", f"{env_state['temperature']} °C")
    with e2:
        st.metric("Barometric Pressure", f"{env_state['pressure']} hPa")
    with e3:
        st.metric("Wind Speed", f"{env_state['wind_speed']} km/h")
    with e4:
        st.metric("Vibration Level", f"{env_state['vibration']}")
    with e5:
        st.metric("Air Density", f"{env_state['air_density_kg_m3']} kg/m³")

    st.markdown("---")

    # ----------------------------------------------------
    # 5. ENVIRONMENTAL IMPACT ANALYSIS
    # ----------------------------------------------------
    st.subheader("5. Environmental Impact Analysis")
    st.caption("Causal Chain: Environmental Condition → Impact Estimation → Compensation Requirement")

    m = comp_state["metrics"]
    ia1, ia2, ia3, ia4 = st.columns(4)
    with ia1:
        st.markdown("**1. Cold & Cable Rigidity**")
        st.write(f"• Temp Stiffness Factor: **x{m['temp_stiffness_factor']}**")
        st.write(f"• Est. Sensor Drift: **{m['sensor_drift_deg_s']} °/s**")
    with ia2:
        st.markdown("**2. Wind & Drag Force**")
        st.write(f"• Aerodynamic Drag: **{m['aerodynamic_drag_n']} N**")
        st.write(f"• Wind Deflection Shift: **{m['wind_deflection_px']} px**")
    with ia3:
        st.markdown("**3. Air Pressure & Derating**")
        st.write(f"• Air Density Derating: **{(1.225 - env_state['air_density_kg_m3'])/1.225*100:.1f}%**")
        st.write(f"• Motor Load Impact: **{m['estimated_motor_load_pct']}%**")
    with ia4:
        st.markdown("**4. Thermal & Structural Stress**")
        st.write(f"• Thermal Cycling Factor: **{abs(20.0 - env_state['temperature'])/50.0:.2f}**")
        st.write(f"• Vibration Filtering: **{env_state['vibration']}**")

    st.markdown("---")

    # ----------------------------------------------------
    # 6. ENVIRONMENTAL COMPENSATION
    # ----------------------------------------------------
    st.subheader("6. Environmental Compensation")
    st.markdown("```ENVIRONMENTAL DISTURBANCE ➔ IMPACT ESTIMATION ➔ COMPENSATION ➔ CORRECTED SYSTEM RESPONSE```")
    st.write("")

    comp1, comp2, comp3 = st.columns(3)
    with comp1:
        st.markdown("##### Cable Stiffness Compensation")
        st.write(f"• Status: **{'ACTIVE' if comp_engine.enable_temp_comp else 'DISABLED'}**")
        st.write(f"• Pan Correction Delta: **{m['pan_correction_deg']:+.2f}°**")
    with comp2:
        st.markdown("##### Wind Disturbance Stabilization")
        st.write(f"• Status: **{'ACTIVE' if comp_engine.enable_wind_comp else 'DISABLED'}**")
        st.write(f"• Tilt Correction Delta: **{m['tilt_correction_deg']:+.2f}°**")
    with comp3:
        st.markdown("##### Adaptive Gain & Motor Load")
        st.write(f"• Status: **{'ACTIVE' if comp_engine.enable_vibration_comp else 'DISABLED'}**")
        st.write(f"• Adaptive Stabilization Gain: **{m['adaptive_stabilization_gain']}**")
        st.write(f"• Estimated Servo Torque Load: **{m['estimated_motor_load_pct']}%**")

    st.markdown("---")

    # ----------------------------------------------------
    # 7. PERFORMANCE ASSESSMENT
    # ----------------------------------------------------
    st.subheader("7. Performance Assessment")
    st.caption("Demonstrates the effectiveness of high-altitude environmental compensation algorithms. *Model-based estimate.*")

    uncomp = perf_results["uncompensated"]
    comp = perf_results["compensated"]

    comp_col1, comp_col2, comp_col3 = st.columns(3)

    with comp_col1:
        st.markdown("### ❌ WITHOUT COMPENSATION")
        st.progress(int(uncomp["overall"]) / 100.0)
        st.write(f"• Overall Performance: **{uncomp['overall']}%**")
        st.write(f"• Stabilization Performance: **{uncomp['stabilization']}%**")
        st.write(f"• Tracking Performance: **{uncomp['tracking']}%**")

    with comp_col2:
        st.markdown("### ✅ WITH COMPENSATION")
        st.progress(int(comp["overall"]) / 100.0)
        st.write(f"• Overall Performance: **{comp['overall']}%**")
        st.write(f"• Stabilization Performance: **{comp['stabilization']}%**")
        st.write(f"• Tracking Performance: **{comp['tracking']}%**")

    with comp_col3:
        st.markdown("### 📈 COMPENSATION GAIN")
        st.metric("Overall Performance Boost", f"+{perf_results['overall_improvement_pct']}%")
        st.metric("Stabilization Gain Delta", f"+{round(comp['stabilization'] - uncomp['stabilization'], 1)}%")

    st.markdown("---")

    # ----------------------------------------------------
    # 8. HARDWARE SIMULATION — WOKWI
    # ----------------------------------------------------
    st.subheader("8. Hardware Simulation — Wokwi")

    if is_wokwi_online:
        st.markdown("<span class='real-badge'>WOKWI HARDWARE LINK: ONLINE</span>", unsafe_allow_html=True)
        st.success("PYTHON HARDWARE LINK: CONNECTED | ACTIVE CONTROL MODE: LIVE WOKWI")
        st.caption(f"MQTT Topic: `isr/sih/26050/telemetry` | Last Heartbeat Age: {hw_state.get('last_heartbeat_age_sec', 0)}s ago")
    else:
        st.markdown("<span class='offline-badge'>WOKWI HARDWARE LINK: OFFLINE</span>", unsafe_allow_html=True)
        st.warning("PYTHON HARDWARE LINK: NOT CONNECTED | ACTIVE CONTROL MODE: SOFTWARE SIMULATION FALLBACK")
        st.caption("Wokwi simulation is not running or no telemetry heartbeat has been received within 5 seconds.")

    h_col1, h_col2 = st.columns(2)
    with h_col1:
        st.write(f"• ESP32 DevKit V1: **{'ONLINE' if is_wokwi_online else 'NOT CONNECTED'}**")
        st.write(f"• MPU6050 IMU: **{'ONLINE' if is_wokwi_online else 'NOT CONNECTED'}**")
        st.write(f"• BME280 Sensor: **{'ONLINE' if is_wokwi_online else 'NOT CONNECTED'}**")
    with h_col2:
        st.write(f"• Pan/Tilt Servos: **{'ONLINE' if is_wokwi_online else 'NOT CONNECTED'}**")
        st.write(f"• Potentiometers: **{'ONLINE' if is_wokwi_online else 'NOT CONNECTED'}**")
        st.write(f"• Communication: **{'CONNECTED' if is_wokwi_online else 'NOT CONNECTED'}**")

    # Expandable MQTT Diagnostics Debugger
    with st.expander("🔍 MQTT Diagnostics & Telemetry Debugger", expanded=False):
        st.write(f"• **MQTT Broker**: `broker.hivemq.com:1883`")
        st.write(f"• **Telemetry Topic**: `isr/sih/26050/telemetry`")
        st.write(f"• **MQTT Connection Status**: `{hw_state.get('mqtt_connection_status', 'DISCONNECTED')}`")
        if hw_state.get('mqtt_connection_error'):
            st.error(f"MQTT Error: {hw_state.get('mqtt_connection_error')}")
        st.write(f"• **Heartbeat State Machine**: `{hw_state.get('state', 'WOKWI_OFFLINE')}`")
        st.write(f"• **Total Telemetry Messages Received**: `{hw_state.get('mqtt_message_count', 0)}`")
        st.write(f"• **Last Heartbeat Age**: `{hw_state.get('last_heartbeat_age_sec')} seconds`")
        st.markdown("**Last Telemetry Payload Received:**")
        st.json(hw_state.get('mqtt_last_payload') if hw_state.get('mqtt_last_payload') else {"status": "No payload received yet"})

    st.markdown("---")

    # ----------------------------------------------------
    # 9. SUBSYSTEM HEALTH MATRIX
    # ----------------------------------------------------
    st.subheader("9. Subsystem Health Matrix")
    health_cols = st.columns(3)

    subs = list(health_results["subsystems"].items())
    for idx, (sub, stat) in enumerate(subs):
        with health_cols[idx % 3]:
            icon = "✅" if stat in ["ONLINE", "ACTIVE", "CONNECTED"] else ("🟡" if stat in ["WAITING", "WAITING FOR PERMISSION", "INITIALIZING", "ACQUIRING", "READY"] else "❌")
            st.write(f"{icon} **{sub.upper()}**: `{stat}`")

    st.markdown("---")

    # ----------------------------------------------------
    # 10. SYSTEM ALERTS FEED
    # ----------------------------------------------------
    st.subheader("10. System Alerts Feed")
    if health_results["alerts"]:
        for alt in health_results["alerts"]:
            lvl = alt["level"]
            st.markdown(f"<div class='alert-box alert-{lvl}'><b>[{lvl}] {alt['code']}</b><br>{alt['message']}</div>", unsafe_allow_html=True)
    else:
        st.success("All environmental parameters and operational subsystems operating normally.")

    st.markdown("---")

    # ----------------------------------------------------
    # 11. SIH SOLUTION SUMMARY
    # ----------------------------------------------------
    st.subheader("11. SIH Solution Summary — How This Prototype Addresses SIH 26050")
    
    st.markdown("""
1. **Environmental Monitoring**: Measures/simulates temperature, pressure, wind speed, structural vibration, and air density.
2. **Environmental Compensation**: Dynamically adjusts stabilization gain, tracking offsets, and motor torque according to environmental disturbances.
3. **Temperature-Induced Cable Rigidity Compensation**: Models increased mechanical stiffness and its effect on precision pan/tilt pointing.
4. **Wind Disturbance Compensation**: Estimates aerodynamic drag and cross-wind deflection, applying real-time stabilization correction.
5. **Sensor Drift Correction**: Estimates and compensates IMU sensor thermal drift during extended high-altitude operation.
6. **Thermal Management Model**: Evaluates the effect of sub-zero extreme cold on subsystem performance.
7. **Adaptive Control**: Dynamically adjusts control parameters based on real-time environmental stress factors.
8. **Health Monitoring**: Continuously evaluates 9 subsystem modules and generates rule-based alerts.
9. **Predictive Performance Assessment**: Estimates expected detection, tracking, and overall system performance under representative high-altitude conditions.
10. **Hardware-in-the-Loop Simulation**: Integrates Wokwi ESP32, MPU6050, BME280, potentiometers, and pan/tilt servos via MQTT telemetry for prototype-level hardware simulation.
""")

    st.caption("🔒 *Note on Neutralization Scope: Authorized-response / operator-alert interface is outside the physical prototype scope.*")

    # ----------------------------------------------------
    # AUTOMATIC DASHBOARD RERUN LOOP (Every 2 seconds)
    # ----------------------------------------------------
    time.sleep(2.0)
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
