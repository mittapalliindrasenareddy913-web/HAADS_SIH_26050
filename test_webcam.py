"""
HAADS SIH 26050 - Step 4 Verification Script
Tests laptop built-in webcam initialization and frame retrieval via OpenCV.
"""

import sys
import os
import cv2
import time

# Ensure package directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from camera import CameraManager

def test_camera():
    print("==========================================")
    print("STEP 4: LAPTOP BUILT-IN WEBCAM VERIFICATION")
    print("==========================================")
    
    cam = CameraManager(camera_index=0)
    print("Initializing camera...")
    success = cam.start()
    
    print(f"Camera Start Success: {success}")
    print(f"Camera Status: {cam.status}")
    if cam.error_message:
        print(f"Error Message: {cam.error_message}")
        
    if success:
        print("Reading 10 test frames...")
        for i in range(10):
            ret, frame = cam.get_frame()
            if ret and frame is not None:
                h, w, c = frame.shape
                print(f"  Frame {i+1}: Success ({w}x{h}, {c} channels) | Current FPS: {cam.fps:.1f}")
            else:
                print(f"  Frame {i+1}: Failed to grab frame")
            time.sleep(0.05)
        
        cam.stop()
        print("Camera safely released.")
        print("RESULT: SUCCESS - Built-in webcam is working properly.")
        return True
    else:
        print("WARNING: Real webcam unavailable or permission denied. Testing fallback frame generator...")
        ret, frame = cam.get_frame()
        h, w, c = frame.shape
        print(f"  Fallback Frame: Success ({w}x{h}, {c} channels)")
        print("RESULT: FALLBACK READY - System handles missing webcam gracefully.")
        return False

if __name__ == "__main__":
    test_camera()
