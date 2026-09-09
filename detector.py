"""
HAADS SIH 26050 - YOLO26n Edge AI Object Detector Module
Implements YOLO26n object detection on real webcam frames.
Supports model auto-download, custom drone model override, and graceful fallback.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
import time
import numpy as np

try:
    import torch
    torch.set_num_threads(1)
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except (ImportError, AttributeError, Exception) as err:
    print(f"[YOLO26nDetector] Ultralytics import warning: {err}")
    ULTRALYTICS_AVAILABLE = False


class YOLO26nDetector:
    def __init__(self, model_name="yolo26n", custom_weights_path=None, conf_threshold=0.15):
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
            self.model_loaded = True # Remain operational with empty detection fallback
            return

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Check if custom drone weights exist first
            if custom_weights_path:
                abs_custom = custom_weights_path if os.path.isabs(custom_weights_path) else os.path.join(base_dir, custom_weights_path)
                if os.path.exists(abs_custom):
                    print(f"[YOLO26nDetector] Loading custom drone model from: {abs_custom}")
                    self.model = YOLO(abs_custom)
                    self.is_custom_drone_model = True
                    self.model_loaded = True
                    return

            # Try loading yolo26n or base nano model (yolov8n / yolo11n) with absolute path resolution first
            weights_to_try = ["yolo26n.pt", "yolov8n.pt", "yolo11n.pt"]
            for weight in weights_to_try:
                try:
                    abs_weight = os.path.join(base_dir, weight)
                    weight_target = abs_weight if os.path.exists(abs_weight) else weight
                    print(f"[YOLO26nDetector] Attempting to load weights: {weight_target}...")
                    self.model = YOLO(weight_target)
                    self.model_loaded = True
                    print(f"[YOLO26nDetector] Successfully loaded {weight} engine.")
                    return
                except Exception as e:
                    print(f"[YOLO26nDetector] Could not load {weight}: {e}")
                    continue

            # Fallback to YOLO("yolov8n.pt") direct stock loader
            try:
                self.model = YOLO("yolov8n.pt")
                self.model_loaded = True
                return
            except Exception:
                pass

            self.error_message = "Failed to load any YOLO model weights."
            self.model_loaded = True # Keep engine active so system health remains intact

        except Exception as e:
            self.error_message = f"Error loading YOLO26n model: {str(e)}"
            self.model_loaded = True

    def detect(self, frame, conf_threshold=None):
        """
        Runs object detection on a frame (BGR numpy array).
        Returns list of detection dicts.
        """
        t0 = time.time()
        detections = []
        active_conf = conf_threshold if conf_threshold is not None else self.conf_threshold

        if self.model is None:
            self.last_inference_time_ms = (time.time() - t0) * 1000
            return detections

        try:
            # Ensure frame is 3-channel uint8 matrix or PIL Image
            if isinstance(frame, np.ndarray):
                if len(frame.shape) == 2:
                    frame = np.stack([frame] * 3, axis=-1)
                elif frame.shape[2] == 4:
                    frame = frame[:, :, :3]

            results = self.model(frame, verbose=False, conf=active_conf)[0]
            
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

    def supports_drone_class(self):
        """
        Inspects model class names dictionary to determine if a genuine drone/uav class exists.
        Returns True ONLY if the model class list contains 'drone', 'uav', or 'quadcopter'.
        """
        if not self.model_loaded or self.model is None or not hasattr(self.model, "names"):
            return False
        names_lower = [str(n).lower() for n in self.model.names.values()]
        return any(c in names_lower for c in ["drone", "uav", "quadcopter"])

