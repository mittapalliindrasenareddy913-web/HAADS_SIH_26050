"""
HAADS SIH 26050 - Streamlit Engineering Dashboard Module
Renders the 10-section engineering dashboard for the High Altitude Anti-Drone System prototype.
Differentiates REAL vs SIMULATED data, presents UNCOMPENSATED vs COMPENSATED performance comparison,
and displays Wokwi connection status cleanly.
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
        .alert-box { padding: 10px; border-radius: 6px; margin-bottom: 8px; }
        .alert-WARNING { background-color: #78281f; color: #fadbd8; border-left: 5px solid #e74c3c; }
        .alert-CRITICAL { background-color: #641e16; color: #f5b7b1; border-left: 5px solid #922b21; font-weight: bold; }
        .alert-INFO { background-color: #1b4f72; color: #d4efdf; border-left: 5px solid #3498db; }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🎯 HIGH ALTITUDE EDGE AI SYSTEM")
    st.caption("High Altitude Performance Optimization and Robust Design of Anti-Drone System | SIH Problem Statement 26050")
    st.markdown("---")

    # ----------------------------------------------------
    # SIDEBAR: SCENARIOS & ENVIRONMENT CONTROLS
    # ----------------------------------------------------
    st.sidebar.header("🕹️ Environment Controls")
    st.sidebar.markdown("<span class='sim-badge'>SIMULATED ENVIRONMENT</span>", unsafe_allow_html=True)
    st.sidebar.write("")

    # Scenario Preset Selector
    selected_scenario = st.sidebar.selectbox(
        "Load Predefined Scenario Preset:",
        list(config.SCENARIOS.keys())
    )

    if st.sidebar.button("Apply Preset Scenario"):
        env_sim.load_scenario(selected_scenario)
        st.sidebar.success(f"Loaded {selected_scenario}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Manual High-Altitude Sliders")

    # Sliders for Environmental Simulation
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

    # ----------------------------------------------------
    # SYSTEM PIPELINE EXECUTION
    # ----------------------------------------------------
    # 1. Read real webcam frame
    cam_success, frame = camera_mgr.get_frame()

    # 2. Run YOLO26n Edge AI inference on frame
    raw_detections = detector.detect(frame) if (cam_success and frame is not None) else []

    # 3. Object tracking
    active_tracks = tracker.update(raw_detections)
    primary_target = tracker.get_primary_target()

    # Calculate target error
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

    # 4. Environmental state & compensation calculations
    env_state = env_sim.get_state()
    comp_state = comp_engine.calculate_compensation(env_state, error_x, error_y)

    # 5. Virtual Pan/Tilt Calculation
    base_pan, base_tilt = 90, 90
    pan_calc = base_pan + comp_state["metrics"]["pan_correction_deg"]
    tilt_calc = base_tilt + comp_state["metrics"]["tilt_correction_deg"]

    hw_state = hw_interface.send_pan_tilt(pan_calc, tilt_calc)

    # 6. Performance Evaluation
    target_error_dist = math.hypot(error_x, error_y)
    perf_results = perf_engine.evaluate_performance(env_state, comp_state, target_error_dist)

    # 7. Health & Alerts
    health_results = health_mon.update_health(
        camera_mgr.status, detector.model_loaded, len(active_tracks),
        env_state, hw_state, perf_results
    )

    # 8. Update system_data.json
    full_state_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "camera": {"status": camera_mgr.status, "fps": round(camera_mgr.fps, 1)},
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
    # DASHBOARD SECTION 1: SYSTEM OVERVIEW
    # ----------------------------------------------------
    st.subheader("1. System Overview")
    ov1, ov2, ov3, ov4, ov5 = st.columns(5)
    with ov1:
        st.metric("System Mode", "PROTOTYPE", help="Academic Engineering Prototype (Non-destructive)")
    with ov2:
        st.metric("System Health", f"{health_results['overall_health_pct']}%", delta=None)
    with ov3:
        st.metric("Webcam Status / FPS", f"{camera_mgr.status} ({camera_mgr.fps:.1f} FPS)", help="REAL Laptop Webcam")
    with ov4:
        st.metric("Objects Tracked", len(active_tracks), help="YOLO26n Detections")
    with ov5:
        st.metric("Overall Performance", f"{perf_results['compensated']['overall']}%", delta=f"+{perf_results['overall_improvement_pct']}% Comp")

    st.markdown("---")

    # ----------------------------------------------------
    # DASHBOARD SECTION 2 & 3: LIVE CAMERA & ENVIRONMENT
    # ----------------------------------------------------
    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.subheader("2. Real-Time Camera & YOLO26n Edge AI Tracking")
        st.markdown("<span class='real-badge'>REAL LAPTOP WEBCAM INPUT</span>", unsafe_allow_html=True)
        st.write("")

        # Draw bounding boxes and trajectory on frame
        annotated_frame = frame.copy() if (frame is not None) else camera_mgr.get_fallback_frame()

        # Draw crosshair frame center (320, 240)
        cv2.line(annotated_frame, (320, 220), (320, 260), (0, 255, 0), 1)
        cv2.line(annotated_frame, (300, 240), (340, 240), (0, 255, 0), 1)
        cv2.putText(annotated_frame, "CENTER", (325, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # Draw tracks
        for track in active_tracks:
            bx1, by1, bx2, by2 = [int(v) for v in track.bbox]
            # Bounding box
            cv2.rectangle(annotated_frame, (bx1, by1), (bx2, by2), (255, 105, 180), 2)
            # Label
            label_text = f"ID-{track.track_id} {track.class_name} ({track.confidence:.2f})"
            cv2.putText(annotated_frame, label_text, (bx1, max(15, by1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 105, 180), 2)

            # Trajectory path
            if len(track.trajectory) > 1:
                pts = np.array(track.trajectory, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [pts], isClosed=False, color=(0, 255, 255), thickness=2)

            # Error Line from Center
            cv2.line(annotated_frame, (320, 240), (int(track.target_x), int(track.target_y)), (0, 165, 255), 1)

        # Convert BGR to RGB for Streamlit display
        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        st.image(rgb_frame, channels="RGB", use_container_width=True)

        st.caption(f"Model: {detector.model_name} | Inference Time: {detector.last_inference_time_ms:.1f} ms")

    with col_right:
        st.subheader("3. Simulated Environment")
        st.markdown("<span class='sim-badge'>SIMULATED ENVIRONMENT</span>", unsafe_allow_html=True)
        st.write("")

        st.info(f"Active Scenario: **{env_state['active_scenario']}**")
        e1, e2 = st.columns(2)
        with e1:
            st.metric("Temperature", f"{env_state['temperature']} °C")
            st.metric("Barometric Pressure", f"{env_state['pressure']} hPa")
        with e2:
            st.metric("Wind Speed", f"{env_state['wind_speed']} km/h")
            st.metric("Structural Vibration", f"{env_state['vibration']}")

        st.metric("Calculated Air Density", f"{env_state['air_density_kg_m3']} kg/m³")

    st.markdown("---")

    # ----------------------------------------------------
    # DASHBOARD SECTION 4, 5, 6: COMPENSATION, POINTING & PERFORMANCE
    # ----------------------------------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("4. Environmental Compensation")
        st.markdown("<span class='sim-badge'>PROTOTYPE SIMULATION MODEL</span>", unsafe_allow_html=True)
        st.write("")
        m = comp_state["metrics"]
        st.write(f"• Temp Stiffness Factor: **x{m['temp_stiffness_factor']}**")
        st.write(f"• Est. Sensor Drift: **{m['sensor_drift_deg_s']} °/s**")
        st.write(f"• Aerodynamic Drag Force: **{m['aerodynamic_drag_n']} N**")
        st.write(f"• Wind Deflection Shift: **{m['wind_deflection_px']} px**")
        st.write(f"• Adaptive Stabilization Gain: **{m['adaptive_stabilization_gain']}**")
        st.write(f"• Estimated Motor Load: **{m['estimated_motor_load_pct']}%**")

    with c2:
        st.subheader("5. Tracking & Virtual Pointing")
        st.markdown("<span class='sim-badge'>VIRTUAL CAMERA POINTING</span>", unsafe_allow_html=True)
        st.write("")
        st.write(f"• Target Center: **X={target_x:.1f}, Y={target_y:.1f}**")
        st.write(f"• Pointing Error X: **{error_x:+.1f} px**")
        st.write(f"• Pointing Error Y: **{error_y:+.1f} px**")
        st.write(f"• Virtual Pan Servo Angle: **{hw_state['pan_angle']}°** (GPIO 26)")
        st.write(f"• Virtual Tilt Servo Angle: **{hw_state['tilt_angle']}°** (GPIO 27)")

    with c3:
        st.subheader("6. Performance Estimate")
        st.markdown("<span class='sim-badge'>DETERMINISTIC MODEL</span>", unsafe_allow_html=True)
        st.write("")
        cp = perf_results["compensated"]
        st.write(f"• Detection Performance: **{cp['detection']}%**")
        st.write(f"• Tracking Performance: **{cp['tracking']}%**")
        st.write(f"• Stabilization Performance: **{cp['stabilization']}%**")
        st.write(f"• Overall Performance: **{cp['overall']}%**")

    st.markdown("---")

    # ----------------------------------------------------
    # DASHBOARD SECTION 7: BEFORE VS AFTER COMPENSATION
    # ----------------------------------------------------
    st.subheader("7. Performance Comparison — BEFORE vs AFTER Compensation")
    st.caption("Demonstrates the effectiveness of high-altitude environmental compensation algorithms under identical environmental conditions.")

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
    # DASHBOARD SECTION 8, 9, 10: HARDWARE, HEALTH & ALERTS
    # ----------------------------------------------------
    h1, h2, h3 = st.columns(3)

    with h1:
        st.subheader("8. Hardware Simulation (Wokwi)")
        st.info("WOKWI SIMULATION: RUNNING SEPARATELY")
        st.warning(hw_state.get("connection_status", "PYTHON HARDWARE LINK: NOT CONNECTED"))
        st.write(f"• **{hw_state.get('active_control_mode', 'ACTIVE CONTROL MODE: SOFTWARE SIMULATION')}**")
        st.write("• ESP32 DevKit V1: **ACTIVE (SIMULATED)**")
        st.write("• MPU6050 IMU: **SDA:21 / SCL:22**")
        st.write("• BME280 Sensor: **SDA:21 / SCL:22**")
        st.write("• 4 Potentiometers: **Temp(34), Press(35), Wind(32), Vib(33)**")
        st.write("• Pan/Tilt Servos: **GPIO 26 / GPIO 27**")

    with h2:
        st.subheader("9. Subsystem Health Matrix")
        for sub, stat in health_results["subsystems"].items():
            icon = "✅" if stat in ["ONLINE", "ACTIVE"] else ("⚠️" if stat == "SIMULATED" or stat == "SEARCHING" else "❌")
            st.write(f"{icon} **{sub.upper()}**: {stat}")

    with h3:
        st.subheader("10. System Alerts Feed")
        if health_results["alerts"]:
            for alt in health_results["alerts"]:
                lvl = alt["level"]
                st.markdown(f"<div class='alert-box alert-{lvl}'><b>[{lvl}] {alt['code']}</b><br>{alt['message']}</div>", unsafe_allow_html=True)
        else:
            st.success("All environmental parameters within normal bounds.")

    # Refresh button / Auto loop indicator
    time.sleep(0.05)
    st.experimental_rerun() if hasattr(st, 'experimental_rerun') else None
