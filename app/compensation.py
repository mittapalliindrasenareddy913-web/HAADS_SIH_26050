"""
HAADS SIH 26050 - Environmental Compensation Module
Calculates physical disturbance estimates and adaptive stabilization gain
for virtual pan/tilt pointing under severe high-altitude environmental stress.
All formulas are deterministic and labeled as PROTOTYPE SIMULATION MODEL.
"""

import math
import numpy as np


class EnvironmentalCompensationEngine:
    def __init__(self):
        # Toggles for individual compensation features
        self.enable_temp_comp = True
        self.enable_wind_comp = True
        self.enable_pressure_comp = True
        self.enable_vibration_comp = True

    def calculate_compensation(self, env_state, error_x=0.0, error_y=0.0):
        """
        Calculates environmental disturbance estimates and compensated pointing offsets.
        Inputs:
            env_state: dict from EnvironmentSimulator.get_state()
            error_x, error_y: raw tracking error pixels from frame center
        Returns:
            Structured compensation results dict
        """
        temp = env_state.get("temperature", 20.0)
        press = env_state.get("pressure", 950.0)
        wind = env_state.get("wind_speed", 5.0)
        vib = env_state.get("vibration", "LOW")
        rho = env_state.get("air_density_kg_m3", 1.15)

        # ----------------------------------------------------
        # 1. TEMPERATURE EFFECT & STIFFNESS COMPENSATION
        # Sub-zero temperatures increase cable stiffness and lubricant viscosity.
        # ----------------------------------------------------
        if temp < 0:
            temp_stiffness = 1.0 + (abs(temp) / 30.0) * 0.75  # Up to +75% torque load at -30°C
            temp_sensor_drift = (abs(temp) / 30.0) * 2.5     # Estimated sensor bias in °/s
        else:
            temp_stiffness = 1.0
            temp_sensor_drift = 0.0

        temp_gain_comp = temp_stiffness if self.enable_temp_comp else 1.0

        # ----------------------------------------------------
        # 2. WIND EFFECT & AERODYNAMIC DISTURBANCE COMPENSATION
        # Wind velocity creates aerodynamic force on sensor platform: F_drag ~ 0.5 * rho * v^2
        # ----------------------------------------------------
        wind_v_ms = wind / 3.6  # Convert km/h to m/s
        aerodynamic_drag_force = 0.5 * rho * (wind_v_ms ** 2) * 0.05  # N (simulated surface area 0.05 m²)
        wind_gain_boost = 1.0 + (wind / 60.0) * 0.90 if self.enable_wind_comp else 1.0
        
        # Pointing wind deflection estimate (pixels offset)
        wind_deflection_x = (wind / 60.0) * 15.0  # max 15 pixels drag shift

        # ----------------------------------------------------
        # 3. VIBRATION EFFECT & DAMPENING
        # Structural vibration introduces high-frequency mechanical jitter.
        # ----------------------------------------------------
        vib_mult_map = {"LOW": 1.0, "MEDIUM": 1.35, "HIGH": 1.80}
        vib_mult = vib_mult_map.get(vib, 1.0)
        vib_filter_gain = (1.0 / vib_mult) if self.enable_vibration_comp else 1.0

        # ----------------------------------------------------
        # 4. PRESSURE EFFECT & AIR DENSITY DAMPING
        # Lower air pressure at high altitude reduces aerodynamic damping of mechanical oscillation.
        # ----------------------------------------------------
        standard_press = 1013.25
        press_ratio = press / standard_press
        press_damping_factor = press_ratio if self.enable_pressure_comp else 1.0

        # ----------------------------------------------------
        # 5. COMBINED ADAPTIVE STABILIZATION GAIN
        # ----------------------------------------------------
        base_gain = 0.15
        adaptive_gain = base_gain * temp_gain_comp * wind_gain_boost * vib_filter_gain

        # Pointing Corrections (pixels to servo angle conversion)
        # Apply wind deflection compensation if wind comp is enabled
        effective_error_x = error_x + (wind_deflection_x if self.enable_wind_comp else 0.0)
        effective_error_y = error_y

        pan_correction = effective_error_x * adaptive_gain
        tilt_correction = effective_error_y * adaptive_gain

        # Estimated Motor Load % (0% to 100%)
        estimated_motor_load = min(100.0, 20.0 + (temp_stiffness - 1.0) * 40.0 + (wind / 60.0) * 45.0)

        return {
            "model_type": "PROTOTYPE SIMULATION MODEL",
            "toggles": {
                "temperature": self.enable_temp_comp,
                "wind": self.enable_wind_comp,
                "pressure": self.enable_pressure_comp,
                "vibration": self.enable_vibration_comp
            },
            "metrics": {
                "temp_stiffness_factor": round(temp_stiffness, 3),
                "sensor_drift_deg_s": round(temp_sensor_drift, 2),
                "aerodynamic_drag_n": round(aerodynamic_drag_force, 4),
                "wind_deflection_px": round(wind_deflection_x, 1),
                "vibration_multiplier": round(vib_mult, 2),
                "pressure_damping_ratio": round(press_damping_factor, 3),
                "adaptive_stabilization_gain": round(adaptive_gain, 4),
                "estimated_motor_load_pct": round(estimated_motor_load, 1),
                "pan_correction_deg": round(pan_correction, 2),
                "tilt_correction_deg": round(tilt_correction, 2)
            }
        }
