"""
HAADS SIH 26050 - Streamlit Engineering Dashboard Module
Renders the 11-section engineering dashboard for High Altitude Anti-Drone System prototype.
SIH Problem Statement 26050 Alignment: High Altitude Performance Optimization and Robust Design.
"""

import streamlit as st
import cv2
import json
import time
import os
import math
import numpy as np

import config
from environment import EnvironmentSimulator
from compensation import EnvironmentalCompensationEngine
from performance import PerformanceEngine
from health_monitor import HealthMonitor
from hardware_interface import HardwareInterface
from data_manager import SystemDataManager


def create_synthetic_drone_frame(target_x, target_y):
    """Generates a synthetic high-contrast quadcopter drone target frame."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Background grid
    for y in range(0, 480, 40):
        cv2.line(frame, (0, y), (640, y), (25, 30, 35), 1)
    for x in range(0, 640, 40):
        cv2.line(frame, (x, 0), (x, 480), (25, 30, 35), 1)

    tx, ty = int(target_x), int(target_y)
    # Draw Quadcopter Drone Target
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

    # ----------------------------------------------------
    # SIDEBAR: CONTROLS & ENVIRONMENT PRESETS
    # ----------------------------------------------------
    st.sidebar.header("🕹️ System Controls")
    
    # Environment Scenario Presets
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
    st.sidebar.subheader("Refresh & Test Helpers")
    auto_refresh = st.sidebar.checkbox("🔄 Enable Auto Live Refresh Loop (1s)", value=False)
    
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

    # Read current Wokwi state (driven strictly by heartbeat)
    hw_state = hw_interface.get_state()

    # ----------------------------------------------------
    # INPUT SELECTION & FRAME PREPARATION
    # ----------------------------------------------------
    target_mode = st.radio(
        "Select Target Input Source:",
        ["Synthetic Drone Target", "Scan Target with Camera", "Upload Image"],
        index=0,
        horizontal=True
    )

    frame = None
    cam_source = "SYNTHETIC TARGET"
    cam_status_str = "STANDBY"

    if target_mode == "Synthetic Drone Target":
        st.markdown("<span class='sim-badge'>DEFAULT DEMONSTRATION MODE — SYNTHETIC TARGET</span>", unsafe_allow_html=True)
        c_sim1, c_sim2 = st.columns(2)
        with c_sim1:
            sim_target_x = st.slider("Simulated Target X Position", 50, 590, 420, key="sim_tx")
        with c_sim2:
            sim_target_y = st.slider("Simulated Target Y Position", 50, 430, 180, key="sim_ty")
        
        frame = create_synthetic_drone_frame(sim_target_x, sim_target_y)
        cam_source = "SYNTHETIC TARGET"
        cam_status_str = "SYNTHETIC DRONE TARGET — SIMULATION ONLY"

    elif target_mode == "Scan Target with Camera":
        st.markdown("<span class='real-badge'>CAMERA SCAN WORKFLOW</span>", unsafe_allow_html=True)
        st.caption("Initial State: SYSTEM READY — No target scanned yet. Click 'Scan Target Frame' to capture and process.")
        
        cam_img_buffer = st.camera_input("📷 Click to Scan Target Frame", key="camera_scan_input")
        if cam_img_buffer is not None:
            bytes_data = cam_img_buffer.getvalue()
            file_bytes = np.frombuffer(bytes_data, np.uint8)
            decoded_frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if decoded_frame is not None:
                frame = cv2.resize(decoded_frame, (640, 480))
                cam_source = "BROWSER CAMERA"
                cam_status_str = "ONLINE (CAMERA FRAME PROCESSED)"
        else:
            # When camera option chosen but frame not captured yet: show clear standby message
            st.info("SYSTEM READY — Click 'Take Photo' above to capture a frame for YOLO26n detection.")
            frame = create_synthetic_drone_frame(320, 240)
            cam_source = "CAMERA STANDBY"
            cam_status_str = "SYSTEM READY — AWAITING CAPTURE"

    elif target_mode == "Upload Image":
        st.markdown("<span class='real-badge'>IMAGE FILE ANALYSIS</span>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Drone or Target Image File", type=["jpg", "jpeg", "png"], key="img_uploader")
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            file_bytes = np.frombuffer(bytes_data, np.uint8)
            decoded_frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if decoded_frame is not None:
                frame = cv2.resize(decoded_frame, (640, 480))
                cam_source = "UPLOADED IMAGE"
                cam_status_str = "ONLINE (IMAGE PROCESSED)"
        else:
            frame = create_synthetic_drone_frame(320, 240)
            cam_source = "UPLOAD STANDBY"
            cam_status_str = "AWAITING FILE UPLOAD"

    if frame is None:
        frame = create_synthetic_drone_frame(420, 180)

    # ----------------------------------------------------
    # SYSTEM PIPELINE EXECUTION
    # ----------------------------------------------------
    # 1. Edge AI detection
    raw_detections = detector.detect(frame) if detector.model_loaded else []

    # If synthetic target mode is active and YOLO returned no detections, synthesize target entry
    if len(raw_detections) == 0 and "SYNTHETIC" in cam_source:
        raw_detections = [{
            "bbox": [sim_target_x - 30, sim_target_y - 20, sim_target_x + 30, sim_target_y + 20],
            "center": (float(sim_target_x), float(sim_target_y)),
            "width": 60.0,
            "height": 40.0,
            "confidence": 0.94,
            "class_id": 0,
            "class_name": "micro_drone"
        }]

    # 2. Object tracking
    active_tracks = tracker.update(raw_detections)
    primary_target = tracker.get_primary_target()

    if primary_target:
        target_x = primary_target.target_x
        target_y = primary_target.target_y
        error_x = primary_target.error_x
        error_y = primary_target.error_y
        track_id = primary_target.track_id
        confidence = primary_target.confidence
        target_cls = primary_target.class_name
        bbox = primary_target.bbox
    else:
        target_x, target_y = 320.0, 240.0
        error_x, error_y = 0.0, 0.0
        track_id = None
        confidence = 0.0
        target_cls = "N/A"
        bbox = []

    # 3. Environmental state & compensation calculations
    env_state = env_sim.get_state()
    comp_state = comp_engine.calculate_compensation(env_state, error_x, error_y)

    # 4. Pointing calculation
    base_pan, base_tilt = 90, 90
    pan_calc = base_pan + comp_state["metrics"]["pan_correction_deg"]
    tilt_calc = base_tilt + comp_state["metrics"]["tilt_correction_deg"]

    hw_state = hw_interface.send_pan_tilt(pan_calc, tilt_calc)

    # 5. Performance evaluation
    target_error_dist = math.hypot(error_x, error_y)
    perf_results = perf_engine.evaluate_performance(env_state, comp_state, target_error_dist)

    # 6. Health & Alerts
    health_results = health_mon.update_health(
        cam_status_str, detector.model_loaded, len(active_tracks),
        env_state, hw_state, perf_results
    )

    # 7. Update system_data.json
    full_state_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "camera": {"status": cam_status_str, "fps": round(camera_mgr.fps, 1), "source": cam_source},
        "detection": {
            "model_name": detector.model_name,
            "object_count": len(raw_detections),
            "target_class": target_cls,
            "confidence": confidence,
            "bbox": bbox,
            "track_id": track_id
        },
        "tracking": {
            "target_x": target_x, "target_y": target_y,
            "error_x": error_x, "error_y": error_y,
            "trajectory": primary_target.trajectory if primary_target else []
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
        st.metric("Detection Status", "ACTIVE" if len(raw_detections) > 0 else "READY")
    with ov4:
        st.metric("Tracking Status", f"Track ID-{track_id}" if track_id else "SEARCHING")
    with ov5:
        st.metric("Overall Performance", f"{perf_results['compensated']['overall']}%", delta=f"+{perf_results['overall_improvement_pct']}% Comp")

    st.markdown("---")

    # ----------------------------------------------------
    # 2. TARGET DETECTION & IDENTIFICATION
    # ----------------------------------------------------
    st.subheader("2. Target Detection & Identification")
    col_det1, col_det2 = st.columns([6, 4])

    with col_det1:
        annotated_frame = frame.copy()
        cv2.line(annotated_frame, (320, 220), (320, 260), (0, 255, 0), 1)
        cv2.line(annotated_frame, (300, 240), (340, 240), (0, 255, 0), 1)
        cv2.putText(annotated_frame, "CENTER (320,240)", (325, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        for track in active_tracks:
            bx1, by1, bx2, by2 = [int(v) for v in track.bbox]
            cv2.rectangle(annotated_frame, (bx1, by1), (bx2, by2), (255, 105, 180), 2)
            label_text = f"ID-{track.track_id} {track.class_name} ({track.confidence:.2f})"
            cv2.putText(annotated_frame, label_text, (bx1, max(15, by1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 105, 180), 2)
            if len(track.trajectory) > 1:
                pts = np.array(track.trajectory, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [pts], isClosed=False, color=(0, 255, 255), thickness=2)
            cv2.line(annotated_frame, (320, 240), (int(track.target_x), int(track.target_y)), (0, 165, 255), 2)

        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        st.image(rgb_frame, channels="RGB", use_container_width=True)

    with col_det2:
        st.markdown("#### Detection Result Summary")
        st.write(f"• **Model**: `{detector.model_name}`")
        st.write(f"• **Input Source**: `{cam_source}`")
        st.write(f"• **Detected Class**: **`{target_cls}`**")
        st.write(f"• **Confidence Score**: **`{confidence * 100:.1f}%`**")
        st.write(f"• **Track Object ID**: **`{track_id if track_id else 'N/A'}`**")
        st.write(f"• **Inference Latency**: `{detector.last_inference_time_ms:.1f} ms`")
        if "SYNTHETIC" in cam_source:
            st.caption("ℹ️ *Mode: SYNTHETIC TARGET — SIMULATION ONLY*")
        else:
            st.caption("ℹ️ *Model outputs actual detected COCO object class.*")

    st.markdown("---")

    # ----------------------------------------------------
    # 3. TARGET TRACKING & PRECISION POINTING
    # ----------------------------------------------------
    st.subheader("3. Target Tracking & Precision Pointing")
    tp1, tp2, tp3 = st.columns(3)
    with tp1:
        st.metric("Target Center X / Y", f"({target_x:.1f}, {target_y:.1f})")
        st.metric("Tracking Error Distance", f"{target_error_dist:.1f} px")
    with tp2:
        st.metric("Pointing Error X", f"{error_x:+.1f} px")
        st.metric("Pointing Error Y", f"{error_y:+.1f} px")
    with tp3:
        actuator_label = "WOKWI PAN/TILT SERVO" if hw_state.get("is_connected", False) else "Virtual / Simulated Pan-Tilt"
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
    
    is_wokwi_online = hw_state.get("is_connected", False)
    state_name = hw_state.get("state", "WOKWI_OFFLINE")

    if is_wokwi_online:
        st.markdown("<span class='real-badge'>WOKWI HARDWARE LINK: ONLINE</span>", unsafe_allow_html=True)
        st.success(f"PYTHON HARDWARE LINK: CONNECTED | ACTIVE CONTROL MODE: LIVE WOKWI (MQTT)")
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
        st.write(f"• Communication: **{'CONNECTED (MQTT)' if is_wokwi_online else 'NOT CONNECTED'}**")

    st.markdown("---")

    # ----------------------------------------------------
    # 9. SUBSYSTEM HEALTH
    # ----------------------------------------------------
    st.subheader("9. Subsystem Health Matrix")
    health_cols = st.columns(3)

    subs = list(health_results["subsystems"].items())
    for idx, (sub, stat) in enumerate(subs):
        with health_cols[idx % 3]:
            icon = "✅" if stat in ["ONLINE", "ACTIVE", "CONNECTED"] else "❌"
            st.write(f"{icon} **{sub.upper()}**: `{stat}`")

    st.markdown("---")

    # ----------------------------------------------------
    # 10. SYSTEM ALERTS
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

    # Auto rerun handling if enabled
    if auto_refresh:
        time.sleep(1.0)
        if hasattr(st, 'rerun'):
            st.rerun()
        elif hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
