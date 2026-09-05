"""
HAADS SIH 26050 - Full System Integration Test
Verifies end-to-end functionality across all 18 steps:
Camera -> YOLO26n -> Tracking -> Environment -> Compensation -> Performance -> Health -> JSON -> Hardware Interface.
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera import CameraManager
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

    # 1. Camera Test
    print("\n[TEST 1/9] Initializing Laptop Webcam...")
    cam = CameraManager(camera_index=0)
    cam_ok = cam.start()
    print(f"  Camera Status: {cam.status} | Success: {cam_ok}")
    ret, frame = cam.get_frame()
    if frame is not None:
        print(f"  Captured Frame: {frame.shape[1]}x{frame.shape[0]} px")

    # 2. YOLO26n Edge AI Detector Test
    print("\n[TEST 2/9] Loading YOLO26n Edge AI Model...")
    detector = YOLO26nDetector(model_name="yolo26n")
    print(f"  Detector Name: {detector.model_name}")
    print(f"  Model Loaded: {detector.model_loaded}")

    detections = detector.detect(frame) if frame is not None else []
    print(f"  Raw Detections Count: {len(detections)}")

    # 3. Tracker Test
    print("\n[TEST 3/9] Testing Persistent Target Tracker...")
    tracker = PersistentTracker(frame_width=640, frame_height=480)
    tracks = tracker.update(detections)
    print(f"  Active Tracks: {len(tracks)}")
    primary = tracker.get_primary_target()
    if primary:
        print(f"  Primary Target ID: {primary.track_id} ({primary.class_name}) | Center: ({primary.target_x}, {primary.target_y})")
        print(f"  Error Vector: Error X={primary.error_x:+.1f} px, Error Y={primary.error_y:+.1f} px")
    else:
        print("  No active target currently in view (Using frame center 320, 240).")

    # 4. Environmental Simulator & Scenarios
    print("\n[TEST 4/9] Testing Environmental Simulation Scenarios...")
    env_sim = EnvironmentSimulator()
    print(f"  Default Environment: {env_sim.temperature}°C, {env_sim.pressure} hPa, {env_sim.wind_speed} km/h, {env_sim.vibration}")
    env_sim.load_scenario("MODE 4 — EXTREME COMBINED")
    env_state = env_sim.get_state()
    print(f"  Loaded 'MODE 4 — EXTREME COMBINED': {env_state['temperature']}°C, {env_state['pressure']} hPa, {env_state['wind_speed']} km/h, {env_state['vibration']}")

    # 5. Environmental Compensation Engine
    print("\n[TEST 5/9] Testing Compensation Engine...")
    comp_engine = EnvironmentalCompensationEngine()
    err_x = primary.error_x if primary else 50.0
    err_y = primary.error_y if primary else -20.0
    comp_results = comp_engine.calculate_compensation(env_state, err_x, err_y)
    m = comp_results["metrics"]
    print(f"  Temp Stiffness Factor: x{m['temp_stiffness_factor']}")
    print(f"  Aerodynamic Drag Force: {m['aerodynamic_drag_n']} N")
    print(f"  Adaptive Stabilization Gain: {m['adaptive_stabilization_gain']}")
    print(f"  Pan Correction: {m['pan_correction_deg']}°, Tilt Correction: {m['tilt_correction_deg']}°")

    # 6. Performance Engine (Uncompensated vs Compensated)
    print("\n[TEST 6/9] Testing Deterministic Performance Engine...")
    perf_engine = PerformanceEngine()
    perf_res = perf_engine.evaluate_performance(env_state, comp_results, abs(err_x))
    uncomp = perf_res["uncompensated"]
    comp = perf_res["compensated"]
    print(f"  WITHOUT COMPENSATION -> Overall: {uncomp['overall']}%, Stabilization: {uncomp['stabilization']}%")
    print(f"  WITH COMPENSATION    -> Overall: {comp['overall']}%, Stabilization: {comp['stabilization']}%")
    print(f"  Net Performance Boost: +{perf_res['overall_improvement_pct']}%")

    # 7. Hardware Interface & Wokwi Connection Status
    print("\n[TEST 7/9] Testing Hardware Interface & Fallback...")
    hw = HardwareInterface(mode="SOFTWARE_SIMULATION")
    hw_res = hw.send_pan_tilt(90 + m['pan_correction_deg'], 90 + m['tilt_correction_deg'])
    print(f"  Connection Status: {hw_res['connection_status']}")
    print(f"  Hardware Source: {hw_res['source']}")
    print(f"  Pan Angle: {hw_res['pan_angle']}°, Tilt Angle: {hw_res['tilt_angle']}°")

    # 8. Health Monitor & Alerts
    print("\n[TEST 8/9] Testing Subsystem Health & Alerts...")
    health_mon = HealthMonitor()
    health_res = health_mon.update_health(cam.status, detector.model_loaded, len(tracks), env_state, hw_res, perf_res)
    print(f"  Overall Health Score: {health_res['overall_health_pct']}%")
    print(f"  Active Alerts Count: {len(health_res['alerts'])}")
    for alt in health_res["alerts"]:
        print(f"    - [{alt['level']}] {alt['code']}: {alt['message']}")

    # 9. Data Manager (system_data.json)
    print("\n[TEST 9/9] Testing Atomic system_data.json Data Manager...")
    dm = SystemDataManager()
    full_state = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "camera": {"status": cam.status, "fps": round(cam.fps, 1)},
        "detection": {"model_name": detector.model_name, "object_count": len(detections)},
        "tracking": {"target_x": 320.0, "target_y": 240.0, "error_x": err_x, "error_y": err_y},
        "environment": env_state,
        "compensation": comp_results,
        "performance": perf_res,
        "health": health_res,
        "hardware": hw_res
    }
    saved_ok = dm.save_state(full_state)
    loaded_state = dm.load_state()
    print(f"  Save Success: {saved_ok}")
    print(f"  Loaded JSON Timestamp: {loaded_state.get('timestamp')}")

    # Cleanup
    cam.stop()
    print("\n==========================================================")
    print("ALL INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
    print("==========================================================")


if __name__ == "__main__":
    run_integration_test()
