"""
HAADS SIH 26050 - YOLO26n Edge AI Object Detector Module
Implements YOLO26n object detection on real webcam frames.
Supports model auto-download, custom drone model override, and graceful fallback.
"""

import os
import sys
import time
import numpy as np

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class YOLO26nDetector:
    def __init__(self, model_name="yolo26n", custom_weights_path=None, conf_threshold=0.35):
        self.model_name = "YOLO26n Edge AI — Object Detection & Tracking"
        self.conf_threshold = conf_threshold
        self.model = None
        self.model_loaded = False
        self.is_custom_drone_model = False
        self.error_message = ""
        self.last_inference_time_ms = 0.0

        # Attempt model initialization
        self._load_model(model_name, custom_weights_path)

    def _load_model(self, model_name, custom_weights_path):
        if not ULTRALYTICS_AVAILABLE:
            self.error_message = "ultralytics package not installed yet."
            self.model_loaded = False
            return

        try:
            # Check if custom drone weights exist first
            if custom_weights_path and os.path.exists(custom_weights_path):
                print(f"[YOLO26nDetector] Loading custom drone model from: {custom_weights_path}")
                self.model = YOLO(custom_weights_path)
                self.is_custom_drone_model = True
                self.model_loaded = True
                return

            # Try loading yolo26n or base nano model (yolov8n / yolo11n)
            weights_to_try = ["yolo26n.pt", "yolov8n.pt", "yolo11n.pt"]
            for weight in weights_to_try:
                try:
                    print(f"[YOLO26nDetector] Attempting to load weights: {weight}...")
                    self.model = YOLO(weight)
                    self.model_loaded = True
                    print(f"[YOLO26nDetector] Successfully loaded {weight} engine.")
                    return
                except Exception as e:
                    print(f"[YOLO26nDetector] Could not load {weight}: {e}")
                    continue

            self.error_message = "Failed to load any YOLO model weights."
            self.model_loaded = False

        except Exception as e:
            self.error_message = f"Error loading YOLO26n model: {str(e)}"
            self.model_loaded = False

    def detect(self, frame):
        """
        Runs object detection on a frame (BGR numpy array).
        Returns:
            detections: List of dicts containing:
                - bbox: [x1, y1, x2, y2] (pixels)
                - center: (center_x, center_y)
                - width: w, height: h
                - confidence: float (0.0 to 1.0)
                - class_id: int
                - class_name: str
        """
        t0 = time.time()
        detections = []

        if not self.model_loaded or self.model is None:
            # Simulated dummy detection if model is still loading or unavailable
            self.last_inference_time_ms = (time.time() - t0) * 1000
            return detections

        try:
            results = self.model(frame, verbose=False, conf=self.conf_threshold)[0]
            
            for box in results.boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self.model.names.get(cls_id, f"object_{cls_id}")

                w = x2 - x1
                h = y2 - y1
                cx = x1 + w / 2.0
                cy = y1 + h / 2.0

                detections.append({
                    "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                    "center": (round(cx, 1), round(cy, 1)),
                    "width": round(w, 1),
                    "height": round(h, 1),
                    "confidence": round(conf, 3),
                    "class_id": cls_id,
                    "class_name": cls_name
                })

        except Exception as e:
            self.error_message = f"Inference error: {str(e)}"

        self.last_inference_time_ms = (time.time() - t0) * 1000
        return detections
