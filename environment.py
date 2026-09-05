"""
HAADS SIH 26050 - Environmental Simulation Module
Simulates high-altitude environmental parameters (Temperature, Pressure, Wind Speed, Vibration).
Provides deterministic physical property estimations (Air density, aerodynamic drag boost).
Explicitly labeled as SIMULATED ENVIRONMENT.
"""

import sys
import os
import math
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config


def _clamp(val, min_val, max_val):
    """Robust clamp helper function."""
    try:
        return float(np.clip(val, min_val, max_val))
    except Exception:
        return float(max(min_val, min(max_val, val)))


class EnvironmentSimulator:
    def __init__(self):
        self.temperature = config.TEMP_DEFAULT_C       # °C
        self.pressure = config.PRESSURE_DEFAULT_HPA   # hPa
        self.wind_speed = config.WIND_DEFAULT_KMH     # km/h
        self.vibration = config.VIBRATION_DEFAULT       # LOW, MEDIUM, HIGH
        self.source = "SOFTWARE_SIMULATION"              # SOFTWARE_SIMULATION or WOKWI_POTENTIOMETER
        self.active_scenario = "MODE 1 — NORMAL"

    def set_parameters(self, temp=None, pressure=None, wind=None, vibration=None, source=None):
        """Sets environmental simulation parameters with validation bounds."""
        if temp is not None:
            self.temperature = _clamp(temp, config.TEMP_MIN_C, config.TEMP_MAX_C)
        if pressure is not None:
            self.pressure = _clamp(pressure, config.PRESSURE_MIN_HPA, config.PRESSURE_MAX_HPA)
        if wind is not None:
            self.wind_speed = _clamp(wind, config.WIND_MIN_KMH, config.WIND_MAX_KMH)
        if vibration is not None and vibration in config.VIBRATION_LEVELS:
            self.vibration = vibration
        if source is not None:
            self.source = source

    def load_scenario(self, scenario_name):
        """Loads a predefined high-altitude scenario preset."""
        if scenario_name in config.SCENARIOS:
            preset = config.SCENARIOS[scenario_name]
            self.temperature = preset["temperature"]
            self.pressure = preset["pressure"]
            self.wind_speed = preset["wind_speed"]
            self.vibration = preset["vibration"]
            self.active_scenario = scenario_name
            return True
        return False

    def get_air_density(self):
        """
        Calculates estimated air density (rho) in kg/m³ using ideal gas equation:
        rho = (P * 100) / (R_specific * T_kelvin)
        P in Pa (hPa * 100), R_specific = 287.058 J/(kg·K), T in Kelvin (°C + 273.15)
        """
        t_kelvin = self.temperature + 273.15
        p_pa = self.pressure * 100.0
        rho = p_pa / (287.058 * t_kelvin)
        return round(rho, 4)

    def get_state(self):
        """Returns structured dictionary of simulated environmental state."""
        return {
            "temperature": round(self.temperature, 1),
            "pressure": round(self.pressure, 1),
            "wind_speed": round(self.wind_speed, 1),
            "vibration": self.vibration,
            "air_density_kg_m3": self.get_air_density(),
            "source": self.source,
            "active_scenario": self.active_scenario,
            "label": "SIMULATED ENVIRONMENT"
        }
