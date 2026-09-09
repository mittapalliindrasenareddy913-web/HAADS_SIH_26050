"""
HAADS SIH 26050 - Main Application Launcher
Root entry point for Streamlit web server (compatible with Streamlit Cloud auto-deployment).
Initializes module path environment and delegates execution to app/app.py.
"""

import os
import sys

# Prevent OpenBLAS / PyTorch / OpenCV thread allocation errors
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Ensure app directory and project root are in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(PROJECT_ROOT, "app")

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(1, PROJECT_ROOT)

import runpy

TARGET_SCRIPT = os.path.join(APP_DIR, "app.py")

if __name__ == "__main__":
    runpy.run_path(TARGET_SCRIPT, run_name="__main__")

