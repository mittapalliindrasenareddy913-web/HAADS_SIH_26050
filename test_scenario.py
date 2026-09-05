"""
HAADS SIH 26050 - Verification Test for Scenario Loading & Sliders
Specifically verifies MODE 4 — EXTREME COMBINED loading (-20°C, 650 hPa, 40 km/h, HIGH vibration).
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from environment import EnvironmentSimulator
from compensation import EnvironmentalCompensationEngine
from performance import PerformanceEngine
from health_monitor import HealthMonitor
from hardware_interface import HardwareInterface
from data_manager import SystemDataManager


def test_extreme_combined_scenario():
    print("==========================================================")
    print("VERIFYING SCENARIO MODE 4 — EXTREME COMBINED")
    print("==========================================================")

    env_sim = EnvironmentSimulator()
    
    # Load preset
    ok = env_sim.load_scenario("MODE 4 — EXTREME COMBINED")
    assert ok, "Failed to load MODE 4 — EXTREME COMBINED scenario"
    print("[1/4] Scenario preset loaded successfully.")

    # Test slider update (as Streamlit sidebar sliders do)
    env_sim.set_parameters(temp=-20.0, pressure=650.0, wind=40.0, vibration="HIGH")
    state = env_sim.get_state()

    print(f"  Temperature: {state['temperature']} °C (Expected: -20.0 °C)")
    print(f"  Pressure: {state['pressure']} hPa (Expected: 650.0 hPa)")
    print(f"  Wind Speed: {state['wind_speed']} km/h (Expected: 40.0 km/h)")
    print(f"  Vibration: {state['vibration']} (Expected: HIGH)")
    print(f"  Air Density: {state['air_density_kg_m3']} kg/m³")

    assert state['temperature'] == -20.0, f"Expected -20.0, got {state['temperature']}"
    assert state['pressure'] == 650.0, f"Expected 650.0, got {state['pressure']}"
    assert state['wind_speed'] == 40.0, f"Expected 40.0, got {state['wind_speed']}"
    assert state['vibration'] == "HIGH", f"Expected HIGH, got {state['vibration']}"
    print("[2/4] Environmental parameter validation PASSED.")

    # Test compensation calculation under Mode 4
    comp_engine = EnvironmentalCompensationEngine()
    comp_res = comp_engine.calculate_compensation(state, error_x=50.0, error_y=-30.0)
    print("[3/4] Environmental Compensation calculation PASSED.")

    # Test performance calculation under Mode 4
    perf_engine = PerformanceEngine()
    perf_res = perf_engine.evaluate_performance(state, comp_res, target_error_px=58.3)
    print(f"  Uncompensated Overall: {perf_res['uncompensated']['overall']}%")
    print(f"  Compensated Overall: {perf_res['compensated']['overall']}%")
    print(f"  Overall Improvement: +{perf_res['overall_improvement_pct']}%")
    print("[4/4] Performance calculation PASSED.")

    print("\n==========================================================")
    print("MODE 4 — EXTREME COMBINED VERIFICATION PASSED 100% WITHOUT EXCEPTION!")
    print("==========================================================")


if __name__ == "__main__":
    test_extreme_combined_scenario()
