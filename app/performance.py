"""
HAADS SIH 26050 - Deterministic Performance Estimation Engine
Calculates Detection, Tracking, Stabilization, and Overall Performance metrics (0-100%).
Provides side-by-side WITHOUT COMPENSATION vs WITH COMPENSATION evaluation.
Uses strictly deterministic formulas with zero random numbers.
Explicitly labeled as SIMULATED PERFORMANCE ESTIMATE.
"""

import math
import numpy as np


class PerformanceEngine:
    def __init__(self):
        self.label = "SIMULATED PERFORMANCE ESTIMATE"

    def evaluate_performance(self, env_state, comp_state, target_error_px=0.0):
        """
        Evaluates system performance under given environmental & compensation conditions.
        Returns:
            dict containing:
                - 'uncompensated': {detection, tracking, stabilization, overall}
                - 'compensated': {detection, tracking, stabilization, overall}
                - 'improvement_delta': float
        """
        temp = env_state.get("temperature", 20.0)
        press = env_state.get("pressure", 950.0)
        wind = env_state.get("wind_speed", 5.0)
        vib = env_state.get("vibration", "LOW")

        vib_degrade_map = {"LOW": 0.0, "MEDIUM": 8.0, "HIGH": 22.0}
        vib_penalty = vib_degrade_map.get(vib, 0.0)

        # Environmental Degradation Factors (0 to 100 scale)
        temp_penalty = max(0.0, (20.0 - temp) * 0.6)        # Cold penalty (up to 30% at -30°C)
        wind_penalty = (wind / 60.0) * 35.0                 # Wind penalty (up to 35% at 60 km/h)
        press_penalty = max(0.0, (950.0 - press) / 450.0) * 15.0  # Pressure penalty (up to 15% at 500 hPa)
        error_penalty = min(25.0, (target_error_px / 320.0) * 35.0)  # Off-center error penalty

        # ============================================================
        # 1. UNCOMPENSATED SYSTEM PERFORMANCE (Raw Environmental Degradation)
        # ============================================================
        uncomp_det = max(30.0, 98.0 - (temp_penalty * 0.3 + press_penalty * 0.4 + vib_penalty * 0.5))
        uncomp_trk = max(25.0, 95.0 - (wind_penalty * 0.7 + vib_penalty * 0.6 + error_penalty * 0.8))
        uncomp_stb = max(20.0, 95.0 - (temp_penalty * 0.8 + wind_penalty * 0.9 + vib_penalty * 1.0))

        uncomp_overall = (0.25 * uncomp_det) + (0.35 * uncomp_trk) + (0.40 * uncomp_stb)

        # ============================================================
        # 2. COMPENSATED SYSTEM PERFORMANCE (With Environmental Algorithms Active)
        # ============================================================
        toggles = comp_state.get("toggles", {})
        temp_active = toggles.get("temperature", True)
        wind_active = toggles.get("wind", True)
        press_active = toggles.get("pressure", True)
        vib_active = toggles.get("vibration", True)

        # Effective penalties after active compensation
        eff_temp_pen = temp_penalty * (0.25 if temp_active else 1.0)
        eff_wind_pen = wind_penalty * (0.30 if wind_active else 1.0)
        eff_press_pen = press_penalty * (0.40 if press_active else 1.0)
        eff_vib_pen = vib_penalty * (0.35 if vib_active else 1.0)
        eff_err_pen = error_penalty * 0.5  # Closed-loop tracking error reduction

        comp_det = max(40.0, 98.0 - (eff_temp_pen * 0.3 + eff_press_pen * 0.4 + eff_vib_pen * 0.5))
        comp_trk = max(35.0, 96.0 - (eff_wind_pen * 0.7 + eff_vib_pen * 0.6 + eff_err_pen * 0.8))
        comp_stb = max(30.0, 97.0 - (eff_temp_pen * 0.8 + eff_wind_pen * 0.9 + eff_vib_pen * 1.0))

        comp_overall = (0.25 * comp_det) + (0.35 * comp_trk) + (0.40 * comp_stb)

        return {
            "label": self.label,
            "uncompensated": {
                "detection": round(uncomp_det, 1),
                "tracking": round(uncomp_trk, 1),
                "stabilization": round(uncomp_stb, 1),
                "overall": round(uncomp_overall, 1)
            },
            "compensated": {
                "detection": round(comp_det, 1),
                "tracking": round(comp_trk, 1),
                "stabilization": round(comp_stb, 1),
                "overall": round(comp_overall, 1)
            },
            "overall_improvement_pct": round(comp_overall - uncomp_overall, 1)
        }
