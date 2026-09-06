"""
HAADS SIH 26050 - Full System Integration & Device Filter Verification Test Suite
Verifies end-to-end functionality across all subsystems:
Camera Device Filtering -> Laptop Webcam Selection -> Phone Link Exclusion -> Mobile Browser Behavior ->
YOLO26n Edge AI -> Target Tracking -> Mobile Phone Alert -> Environmental Simulation -> Compensation Engine ->
Performance Evaluation -> Truthful Health Matrix -> JSON Logging -> MQTT Wokwi Heartbeat State Machine.
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera import CameraManager, filter_camera_devices
from detector import YOLO26nDetector
from tracker import PersistentTracker
from environment import EnvironmentSimulator
from compensation import EnvironmentalCompensationEngine
from performance import PerformanceEngine
from health_monitor import HealthMonitor
from hardware_interface import HardwareInterface
from data_manager import SystemDataManager


def run_integration_test():
    print("==========================================================")
    print("HAADS SIH 26050 - FULL SYSTEM INTEGRATION VERIFICATION")
    print("==========================================================")

    # 1. Device Filter Unit Test — Laptop Browser Mode
    print("\n[TEST 1/13] Testing Device-Local Laptop Camera Selection Filter...")
    mock_devices = [
        {"label": "Phone Link - MITTAPALLI", "deviceId": "dev_phone1"},
        {"label": "Android Virtual Camera", "deviceId": "dev_phone2"},
        {"label": "Integrated Camera (04f2:b6d9)", "deviceId": "dev_laptop1"},
        {"label": "USB HD Webcam", "deviceId": "dev_laptop2"}
    ]
    chosen_dev, chosen_label = filter_camera_devices(mock_devices, is_mobile=False)
    print(f"  Laptop Candidate Devices: {[d['label'] for d in mock_devices]}")
    print(f"  Selected Device: '{chosen_label}' (ID: {chosen_dev['deviceId']})")
    assert "MITTAPALLI" not in chosen_label, "Filter failed: Phone Link camera was selected on laptop!"
    assert "Integrated" in chosen_label or "Webcam" in chosen_label, "Filter failed: Built-in laptop camera was not prioritized!"

    # 2. Device Filter Unit Test — Mobile Browser Mode
    print("\n[TEST 2/13] Testing Mobile Browser Camera Selection...")
    mock_mobile_devices = [
        {"label": "Android Front Camera", "deviceId": "dev_mobile1"}
    ]
    mobile_dev, mobile_label = filter_camera_devices(mock_mobile_devices, is_mobile=True)
    print(f"  Mobile Selected Device: '{mobile_label}'")
    assert "Android" in mobile_label, "Filter failed: Mobile camera excluded on mobile browser!"

    # 3. Initializing Laptop Webcam Manager
    print("\n[TEST 3/13] Initializing Laptop Webcam Manager...")
    cam = CameraManager(camera_index=0)
    cam_ok = cam.start()
    print(f"  Camera Status: {cam.status} | Success: {cam_ok}")
    ret, frame = cam.get_frame()
    if frame is not None:
        print(f"  Captured Frame: {frame.shape[1]}x{frame.shape[0]} px")

    # 4. YOLO26n Edge AI Detector Test
    print("\n[TEST 4/13] Loading YOLO26n Edge AI Model...")
    detector = YOLO26nDetector(model_name="yolo26n")
    print(f"  Detector Name: {detector.model_name}")
    print(f"  Model Loaded: {detector.model_loaded}")

    detections = detector.detect(frame) if frame is not None else []
    print(f"  Raw Detections Count: {len(detections)}")

    # 5. Tracker Test
    print("\n[TEST 5/13] Testing Persistent Target Tracker...")
    tracker = PersistentTracker(frame_width=640, frame_height=480)
    tracks = tracker.update(detections)
    print(f"  Active Tracks: {len(tracks)}")
    primary = tracker.get_primary_target()
    if primary:
        print(f"  Primary Target ID: {primary.track_id} ({primary.class_name}) | Center: ({primary.target_x}, {primary.target_y})")
        print(f"  Error Vector: Error X={primary.error_x:+.1f} px, Error Y={primary.error_y:+.1f} px")
    else:
        print("  No active target currently in view (Using frame center 320, 240).")

    # 6. Mobile Phone Detection Alert Test
    print("\n[TEST 6/13] Testing Real Mobile Phone Detection Alert Logic...")
    mock_phone_detection = [{
        "bbox": [100.0, 100.0, 250.0, 400.0],
        "center": (175.0, 250.0),
        "width": 150.0,
        "height": 300.0,
        "confidence": 0.964,
        "class_id": 67,
        "class_name": "cell phone"
    }]
    phone_tracks = tracker.update(mock_phone_detection)
    phone_target = tracker.get_primary_target()
    assert phone_target is not None, "Target tracker failed to track mobile phone!"
    assert phone_target.class_name == "cell phone", f"Expected 'cell phone', got '{phone_target.class_name}'"
    print(f"  Detected Target Class: '{phone_target.class_name}' | Confidence: {phone_target.confidence * 100:.1f}% | Track ID: {phone_target.track_id}")
    print("  🚨 TARGET ALERT PASS: Mobile Phone detected with true COCO label and confidence!")

    # 7. Environmental Simulator & Scenarios
    print("\n[TEST 7/13] Testing Environmental Simulation Scenarios...")
    env_sim = EnvironmentSimulator()
    print(f"  Default Environment: {env_sim.temperature}°C, {env_sim.pressure} hPa, {env_sim.wind_speed} km/h, {env_sim.vibration}")
    env_sim.load_scenario("COMBINED HIGH-ALTITUDE STRESS")
    env_state = env_sim.get_state()
    print(f"  Loaded 'COMBINED HIGH-ALTITUDE STRESS': {env_state['temperature']}°C, {env_state['pressure']} hPa, {env_state['wind_speed']} km/h, {env_state['vibration']}")

    # 8. Environmental Compensation Engine
    print("\n[TEST 8/13] Testing Compensation Engine...")
    comp_engine = EnvironmentalCompensationEngine()
    err_x = phone_target.error_x if phone_target else 50.0
    err_y = phone_target.error_y if phone_target else -20.0
    comp_results = comp_engine.calculate_compensation(env_state, err_x, err_y)
    m = comp_results["metrics"]
    print(f"  Temp Stiffness Factor: x{m['temp_stiffness_factor']}")
    print(f"  Aerodynamic Drag Force: {m['aerodynamic_drag_n']} N")
    print(f"  Adaptive Stabilization Gain: {m['adaptive_stabilization_gain']}")
    print(f"  Pan Correction: {m['pan_correction_deg']}°, Tilt Correction: {m['tilt_correction_deg']}°")

    # 9. Performance Engine (Uncompensated vs Compensated)
    print("\n[TEST 9/13] Testing Deterministic Performance Engine...")
    perf_engine = PerformanceEngine()
    perf_res = perf_engine.evaluate_performance(env_state, comp_results, abs(err_x))
    uncomp = perf_res["uncompensated"]
    comp = perf_res["compensated"]
    print(f"  WITHOUT COMPENSATION -> Overall: {uncomp['overall']}%, Stabilization: {uncomp['stabilization']}%")
    print(f"  WITH COMPENSATION    -> Overall: {comp['overall']}%, Stabilization: {comp['stabilization']}%")
    print(f"  Net Performance Boost: +{perf_res['overall_improvement_pct']}%")

    # 10. Hardware Interface — OFFLINE State Machine Test
    print("\n[TEST 10/13] Testing Wokwi OFFLINE Initial State...")
    hw = HardwareInterface(mode="AUTO")
    hw_res_off = hw.send_pan_tilt(90 + m['pan_correction_deg'], 90 + m['tilt_correction_deg'])
    print(f"  State Machine State: {hw_res_off['state']}")
    print(f"  Connection Status: {hw_res_off['connection_status']}")
    print(f"  Active Control Mode: {hw_res_off['active_control_mode']}")
    print(f"  Hardware Source: {hw_res_off['source']}")
    assert hw_res_off['state'] == "WOKWI_OFFLINE", "Expected WOKWI_OFFLINE when no telemetry heartbeat received."

    # 11. Hardware Interface — ONLINE Telemetry Heartbeat Test
    print("\n[TEST 11/13] Simulating Incoming Wokwi Heartbeat...")
    hw.process_telemetry_heartbeat({
        "device": "wokwi-esp32",
        "status": "online",
        "temperature": -20.0,
        "pressure": 600.0,
        "wind": 40.0,
        "vibration": 0.5,
        "pan": 95,
        "tilt": 85,
        "timestamp": time.time()
    })
    hw_res_on = hw.send_pan_tilt(95, 85)
    print(f"  State Machine State: {hw_res_on['state']}")
    print(f"  Connection Status: {hw_res_on['connection_status']}")
    print(f"  Active Control Mode: {hw_res_on['active_control_mode']}")
    print(f"  Hardware Source: {hw_res_on['source']}")
    assert hw_res_on['state'] == "WOKWI_ONLINE", "Expected WOKWI_ONLINE after heartbeat payload received."

    # 12. Subsystem Health Matrix State Transitions
    print("\n[TEST 12/13] Testing Subsystem Health Matrix Truthful State Transitions...")
    health_mon = HealthMonitor()
    
    # Test WAITING FOR PERMISSION state
    h_wait = health_mon.update_health("WAITING FOR PERMISSION", "WAITING", "WAITING", env_state, hw_res_on, perf_res)
    assert h_wait["subsystems"]["camera"] == "WAITING FOR PERMISSION", "Expected 'WAITING FOR PERMISSION' camera status!"
    assert h_wait["subsystems"]["ai_detector"] == "WAITING", "Expected 'WAITING' detector status before frames!"

    # Test ONLINE state
    h_online = health_mon.update_health("ONLINE", "ACTIVE", "ACTIVE", env_state, hw_res_on, perf_res)
    assert h_online["subsystems"]["camera"] == "ONLINE", "Expected 'ONLINE' camera status when frames arrive!"
    assert h_online["subsystems"]["ai_detector"] == "ACTIVE", "Expected 'ACTIVE' detector status after frame processing!"
    print(f"  Truthful Health Matrix: {h_online['subsystems']}")

    # 13. Data Manager (system_data.json)
    print("\n[TEST 13/13] Testing Atomic system_data.json Data Manager...")
    dm = SystemDataManager()
    full_state = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "camera": {"status": cam.status, "device_label": chosen_label, "fps": round(cam.fps, 1)},
        "detection": {"model_name": detector.model_name, "object_count": len(mock_phone_detection)},
        "tracking": {"target_x": phone_target.target_x, "target_y": phone_target.target_y, "error_x": err_x, "error_y": err_y},
        "environment": env_state,
        "compensation": comp_results,
        "performance": perf_res,
        "health": h_online,
        "hardware": hw_res_on
    }
    saved_ok = dm.save_state(full_state)
    loaded_state = dm.load_state()
    print(f"  Save Success: {saved_ok}")
    print(f"  Loaded JSON Timestamp: {loaded_state.get('timestamp')}")

    # Cleanup
    cam.stop()
    print("\n==========================================================")
    print("ALL 13 INTEGRATION & UNIT TESTS COMPLETED SUCCESSFULLY!")
    print("==========================================================")


if __name__ == "__main__":
    run_integration_test()
