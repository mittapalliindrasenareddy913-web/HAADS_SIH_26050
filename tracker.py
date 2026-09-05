"""
HAADS SIH 26050 - Object Tracker Module
Provides persistent object tracking, trajectory history logging, velocity calculation,
and pointing error computation relative to frame center (320, 240).
"""

import math
import numpy as np


class TrackedObject:
    def __init__(self, track_id, detection, max_history=30):
        self.track_id = track_id
        self.class_name = detection["class_name"]
        self.class_id = detection["class_id"]
        self.confidence = detection["confidence"]
        self.bbox = detection["bbox"]
        self.target_x = detection["center"][0]
        self.target_y = detection["center"][1]
        self.width = detection["width"]
        self.height = detection["height"]
        
        self.trajectory = [(self.target_x, self.target_y)]
        self.max_history = max_history
        self.velocity = (0.0, 0.0)
        self.age = 1
        self.lost_count = 0

        self.error_x = 0.0
        self.error_y = 0.0

    def update(self, detection, frame_center_x=320, frame_center_y=240):
        new_x, new_y = detection["center"]
        dt_x = new_x - self.target_x
        dt_y = new_y - self.target_y
        
        # Exponential smoothing for velocity estimate
        self.velocity = (0.7 * self.velocity[0] + 0.3 * dt_x,
                         0.7 * self.velocity[1] + 0.3 * dt_y)

        self.target_x = new_x
        self.target_y = new_y
        self.bbox = detection["bbox"]
        self.width = detection["width"]
        self.height = detection["height"]
        self.confidence = detection["confidence"]
        
        # Append trajectory
        self.trajectory.append((self.target_x, self.target_y))
        if len(self.trajectory) > self.max_history:
            self.trajectory.pop(0)

        # Pointing Error calculation
        self.error_x = self.target_x - frame_center_x
        self.error_y = self.target_y - frame_center_y

        self.age += 1
        self.lost_count = 0

    def mark_lost(self):
        self.lost_count += 1


class PersistentTracker:
    def __init__(self, max_distance=100, max_lost=10, frame_width=640, frame_height=480):
        self.next_track_id = 1
        self.tracks = {}  # track_id -> TrackedObject
        self.max_distance = max_distance
        self.max_lost = max_lost
        self.frame_center_x = frame_width // 2
        self.frame_center_y = frame_height // 2
        self.primary_target_id = None

    def update(self, detections):
        """
        Updates object tracks with new detections using Euclidean distance matching.
        Returns active tracked objects list.
        """
        unmatched_detections = list(range(len(detections)))
        matched_track_ids = []

        # Distance matching for existing tracks
        for track_id, track in list(self.tracks.items()):
            best_dist = float("inf")
            best_det_idx = -1

            for idx in unmatched_detections:
                det_center = detections[idx]["center"]
                dist = math.hypot(det_center[0] - track.target_x, det_center[1] - track.target_y)
                if dist < best_dist and dist < self.max_distance:
                    best_dist = dist
                    best_det_idx = idx

            if best_det_idx != -1:
                det = detections[best_det_idx]
                track.update(det, self.frame_center_x, self.frame_center_y)
                matched_track_ids.append(track_id)
                unmatched_detections.remove(best_det_idx)
            else:
                track.mark_lost()

        # Remove dead tracks
        dead_ids = [tid for tid, t in self.tracks.items() if t.lost_count > self.max_lost]
        for tid in dead_ids:
            del self.tracks[tid]

        # Create new tracks for unmatched detections
        for idx in unmatched_detections:
            det = detections[idx]
            new_track = TrackedObject(self.next_track_id, det)
            new_track.update(det, self.frame_center_x, self.frame_center_y)
            self.tracks[self.next_track_id] = new_track
            self.next_track_id += 1

        # Select primary target (e.g. highest confidence or active track closest to center)
        self._select_primary_target()

        return list(self.tracks.values())

    def _select_primary_target(self):
        if not self.tracks:
            self.primary_target_id = None
            return

        # Select target with minimum distance to center or highest confidence
        best_tid = None
        min_err = float("inf")

        for tid, track in self.tracks.items():
            if track.lost_count == 0:
                err_dist = math.hypot(track.error_x, track.error_y)
                if err_dist < min_err:
                    min_err = err_dist
                    best_tid = tid

        self.primary_target_id = best_tid

    def get_primary_target(self):
        if self.primary_target_id in self.tracks:
            return self.tracks[self.primary_target_id]
        return None
