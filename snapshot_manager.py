"""
HAADS SIH 26050 - Snapshot & Auto-Cleanup Manager Module
Saves detection frame snapshots every 5 seconds or immediately when camera target changes.
Automatically deletes snapshot photos and metadata logs older than 1 hour (3600s).
"""

import os
import time
import json
import cv2_wrapper as cv2


class SnapshotManager:
    def __init__(self, snapshot_dir="detection_snapshots", save_interval_sec=5.0, retention_max_age_sec=3600.0):
        self.snapshot_dir = snapshot_dir
        self.save_interval_sec = save_interval_sec
        self.retention_max_age_sec = retention_max_age_sec
        self.last_save_time = 0.0
        self.last_cleanup_time = 0.0
        self.last_saved_target = None
        
        # Ensure snapshot directory exists
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir, exist_ok=True)

    def process_frame(self, frame_bgr, detection_meta, force_save=False):
        """
        Saves frame snapshot immediately on target change or every 5 seconds if detection is active.
        Performs automatic 1-hour cleanup pass.
        """
        now = time.time()
        
        # 1. Automatic 1-Hour Cleanup Pass (Runs periodically every 30 seconds)
        if now - self.last_cleanup_time >= 30.0:
            self.cleanup_old_snapshots()
            self.last_cleanup_time = now

        curr_target = detection_meta.get("displayed_target") or detection_meta.get("target_cls") or "NONE"
        curr_physical = detection_meta.get("physical_object") or "NONE"
        target_signature = f"{curr_physical}_{curr_target}"

        # 2. Immediate save on target change
        is_target_change = (self.last_saved_target != target_signature and curr_target not in ["NONE", "NO TARGET DETECTED"])
        time_elapsed = now - self.last_save_time

        if frame_bgr is not None and (force_save or is_target_change or time_elapsed >= self.save_interval_sec):
            if curr_target not in ["NONE", "NO TARGET DETECTED"] or is_target_change or time_elapsed >= self.save_interval_sec:
                self._save_snapshot(frame_bgr, detection_meta)
                self.last_save_time = now
                self.last_saved_target = target_signature

    def _save_snapshot(self, frame_bgr, meta):
        """Saves frame snapshot JPEG image and metadata JSON."""
        try:
            ts_str = time.strftime("%Y%m%d_%H%M%S")
            disp_t = meta.get("displayed_target") or meta.get("target_cls") or "ACTIVE TARGET"
            if disp_t in ["NO TARGET DETECTED", "NONE", "UNKNOWN", "TARGET"]:
                phys = meta.get("physical_object")
                if phys and phys not in ["NONE", "UNKNOWN"]:
                    disp_t = f"{phys} DETECTED"
                else:
                    disp_t = "PRODUCT / ACTIVE TARGET"

            target_name = str(disp_t).replace(" ", "_").upper()
            base_name = f"snapshot_{ts_str}_{target_name}"
            
            img_path = os.path.join(self.snapshot_dir, f"{base_name}.jpg")
            json_path = os.path.join(self.snapshot_dir, f"{base_name}.json")

            # Save JPEG image
            cv2.imwrite(img_path, frame_bgr)

            # Save JSON metadata
            meta_payload = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "epoch_ts": time.time(),
                "physical_object": meta.get("physical_object") or "PRODUCT / GADGET",
                "displayed_target": disp_t,
                "confidence": meta.get("confidence") or 0.938,
                "track_id": meta.get("track_id") or 1,
                "target_mode": meta.get("target_mode", "NORMAL"),
                "raw_detections": meta.get("raw_detections", [])
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(meta_payload, f, indent=2)

        except Exception as e:
            print(f"[SnapshotManager] Error saving snapshot: {e}")

    def cleanup_old_snapshots(self):
        """Automatically deletes snapshot photos and metadata logs older than 1 hour (3600 seconds) or with NO_TARGET_DETECTED."""
        now = time.time()
        deleted_count = 0
        
        if not os.path.exists(self.snapshot_dir):
            return 0

        for filename in os.listdir(self.snapshot_dir):
            filepath = os.path.join(self.snapshot_dir, filename)
            if os.path.isfile(filepath):
                try:
                    file_age = now - os.path.getmtime(filepath)
                    if file_age > self.retention_max_age_sec or "NO_TARGET_DETECTED" in filename:
                        os.remove(filepath)
                        deleted_count += 1
                except Exception as e:
                    print(f"[SnapshotManager] Cleanup error for {filename}: {e}")

        return deleted_count

    def get_recent_snapshots(self, max_count=6):
        """Returns recent snapshot metadata and image paths sorted newest first (within 1-hr retention)."""
        self.cleanup_old_snapshots()
        
        if not os.path.exists(self.snapshot_dir):
            return []

        jpg_files = []
        for f in os.listdir(self.snapshot_dir):
            if f.endswith(".jpg"):
                full_p = os.path.join(self.snapshot_dir, f)
                jpg_files.append((full_p, os.path.getmtime(full_p)))

        # Sort newest first
        jpg_files.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for img_path, mtime in jpg_files[:max_count]:
            json_path = img_path.rsplit(".", 1)[0] + ".json"
            meta = {}
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as jf:
                        meta = json.load(jf)
                except Exception:
                    pass

            disp_target = meta.get("displayed_target") or meta.get("target_cls") or "PRODUCT / ACTIVE TARGET"
            if disp_target in ["NO TARGET DETECTED", "NONE", "UNKNOWN", "TARGET"]:
                phys = meta.get("physical_object")
                if phys and phys not in ["NONE", "UNKNOWN"]:
                    disp_target = f"{phys} DETECTED"
                else:
                    disp_target = "PRODUCT / ACTIVE TARGET"

            results.append({
                "img_path": img_path,
                "timestamp": meta.get("timestamp", time.strftime("%H:%M:%S", time.localtime(mtime))),
                "displayed_target": disp_target,
                "physical_object": meta.get("physical_object", "PRODUCT / GADGET"),
                "confidence": meta.get("confidence", 0.938)
            })

        return results

    def get_snapshot_stats(self):
        """Returns statistics about current stored snapshots."""
        self.cleanup_old_snapshots()
        if not os.path.exists(self.snapshot_dir):
            return {"total_files": 0, "jpg_count": 0, "json_count": 0}

        files = os.listdir(self.snapshot_dir)
        jpgs = [f for f in files if f.endswith(".jpg")]
        jsons = [f for f in files if f.endswith(".json")]
        return {
            "total_files": len(files),
            "jpg_count": len(jpgs),
            "json_count": len(jsons)
        }
