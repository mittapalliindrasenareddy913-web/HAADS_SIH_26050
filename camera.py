"""
HAADS SIH 26050 - Camera Module
Handles real laptop built-in webcam capture via OpenCV.
Provides robust permission, unavailable, and safe release handling.
"""

import cv2
import time
import numpy as np


PHONE_KEYWORDS = ["phone link", "mittapalli", "android", "iphone", "mobile", "phone", "remote camera", "continuity", "virtual"]
LAPTOP_KEYWORDS = ["integrated", "built-in", "hd webcam", "hd camera", "laptop", "webcam", "internal"]

def filter_camera_devices(device_list, is_mobile=False):
    """
    Filters camera devices list.
    - If is_mobile is True: returns default mobile camera without excluding mobile keywords.
    - If is_mobile is False (laptop/desktop): excludes remote/phone link cameras and prioritizes built-in laptop webcams.
    """
    if not device_list:
        return None, "No Video Input Devices Available"

    if is_mobile:
        first = device_list[0]
        label = first.get("label", "Mobile Camera") if isinstance(first, dict) else str(first)
        return first, label

    # Laptop / Desktop Browser: Exclude phone link & remote cameras
    candidates = []
    for dev in device_list:
        lbl = (dev.get("label", "") if isinstance(dev, dict) else str(dev)).lower()
        if not any(kw in lbl for kw in PHONE_KEYWORDS):
            candidates.append(dev)

    valid_list = candidates if candidates else device_list

    # Prefer built-in laptop camera keywords
    for dev in valid_list:
        lbl = (dev.get("label", "") if isinstance(dev, dict) else str(dev)).lower()
        if any(kw in lbl for kw in LAPTOP_KEYWORDS):
            selected_lbl = dev.get("label", "Integrated Laptop Camera") if isinstance(dev, dict) else str(dev)
            return dev, selected_lbl

    fallback = valid_list[0]
    fallback_lbl = fallback.get("label", "Laptop Webcam") if isinstance(fallback, dict) else str(fallback)
    return fallback, fallback_lbl


class CameraManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.status = "DISCONNECTED"
        self.error_message = ""
        self.fps = 0.0
        self._prev_frame_time = 0

    def start(self):
        """Attempts to open the laptop built-in webcam."""
        try:
            # Try DirectShow backend first on Windows for faster initialization
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                # Fallback to default backend
                self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                # Try index 1 if index 0 failed
                self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(1)

            if self.cap is not None and self.cap.isOpened():
                # Verify frame reading works
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.status = "ONLINE"
                    self.error_message = ""
                    return True
                else:
                    self.status = "ERROR"
                    self.error_message = "Camera opened but failed to read frames (Permission / Busy)."
                    self.cap.release()
                    self.cap = None
                    return False
            else:
                self.status = "ERROR"
                self.error_message = "Webcam not detected or permission denied."
                return False

        except Exception as e:
            self.status = "ERROR"
            self.error_message = f"Camera initialization error: {str(e)}"
            if self.cap:
                self.cap.release()
                self.cap = None
            return False

    def get_frame(self):
        """
        Reads a frame from the webcam.
        Returns: (success: bool, frame: np.ndarray or None)
        """
        if self.cap is None or not self.cap.isOpened():
            return False, self.get_fallback_frame("Webcam Unavailable")

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.status = "ERROR"
            self.error_message = "Frame capture interrupted."
            return False, self.get_fallback_frame("Frame Grab Failed")

        # Update FPS
        curr_time = time.time()
        if self._prev_frame_time > 0:
            dt = curr_time - self._prev_frame_time
            if dt > 0:
                self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt) if self.fps > 0 else (1.0 / dt)
        self._prev_frame_time = curr_time
        
        self.status = "ONLINE"
        return True, frame

    def get_fallback_frame(self, text="SIMULATED WEBCAM FEED"):
        """Generates a placeholder frame when real camera is unavailable."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw background grid pattern
        for y in range(0, 480, 40):
            cv2.line(frame, (0, y), (640, y), (30, 30, 30), 1)
        for x in range(0, 640, 40):
            cv2.line(frame, (x, 0), (x, 480), (30, 30, 30), 1)

        cv2.putText(frame, "REAL WEBCAM FEED: UNAVAILABLE", (120, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, text, (180, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        return frame

    def stop(self):
        """Safely releases camera resource."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.status = "STOPPED"
