"""
HAADS SIH 26050 - Camera Module
Clean lightweight state container for browser-local device camera stream.
Decoupled from server hardware locks to prevent browser NotReadableError.
"""

import time
import numpy as np
import cv2


class CameraManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.status = "ONLINE"
        self.error_message = ""
        self.fps = 0.0
        self._prev_frame_time = 0
        self.last_frame = None

    def start(self):
        """Initializes CameraManager state as ready for browser local stream."""
        self.status = "ONLINE"
        self.error_message = ""
        return True

    def update_browser_frame(self, frame):
        """Updates CameraManager with a decoded frame matrix received from browser."""
        self.last_frame = frame
        self.status = "ONLINE"
        self.error_message = ""
        curr_time = time.time()
        if self._prev_frame_time > 0:
            dt = curr_time - self._prev_frame_time
            if dt > 0:
                self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt) if self.fps > 0 else (1.0 / dt)
        self._prev_frame_time = curr_time

    def get_frame(self):
        """Returns the latest frame matrix or clean placeholder."""
        if self.last_frame is not None:
            return True, self.last_frame
        return True, self.get_fallback_frame("Awaiting Local Camera Feed")

    def get_fallback_frame(self, text="SIMULATED WEBCAM FEED"):
        """Generates placeholder frame matrix when real camera feed is initializing."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        for y in range(0, 480, 40):
            cv2.line(frame, (0, y), (640, y), (30, 30, 30), 1)
        for x in range(0, 640, 40):
            cv2.line(frame, (x, 0), (x, 480), (30, 30, 30), 1)

        cv2.putText(frame, "LOCAL CAMERA FEED: INITIALIZING", (110, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
        cv2.putText(frame, text, (180, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        return frame

    def stop(self):
        """Safely stops CameraManager."""
        self.status = "STOPPED"
        self.last_frame = None
