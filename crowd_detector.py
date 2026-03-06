# -*- coding: utf-8 -*-
# ============================================================
#   CROWD DETECTOR MODULE (YOLO-based)
#   Handles:
#     - Loading YOLOv8n model
#     - Background thread camera capture
#     - Person detection + crowd level classification
#     - Optional Firebase sync for live crowd data
# ============================================================

import os
import cv2
import time
import threading
import numpy as np
import streamlit as st
from ultralytics import YOLO

os.environ["TORCH_LOAD_WEIGHTS_ONLY"] = "0"


class LiveCrowdDetector:
    """Runs YOLO person detection in a background thread and exposes results."""

    def __init__(self):
        self.model = None
        self.is_running = False
        self.cap = None
        self.latest_frame = None
        self.latest_count = 0
        self.crowd_level = "Unknown"
        self.fb_manager = None
        self.bus_id = "TN-01-AN-1234"
        self.status_msg = "Idle"
        self.count_buffer = []
        self.buffer_size = 5     # Frames used for smoothing

    # ---- Setup ----

    def set_firebase_manager(self, manager, bus_id=None):
        """Attach a FirebaseManager for real-time crowd sync."""
        self.fb_manager = manager
        if bus_id:
            self.bus_id = bus_id

    def load_model(self):
        """Load YOLOv8n model (runs only once)."""
        if self.model is not None:
            return True
        try:
            self.status_msg = "Loading YOLO model..."
            self.model = YOLO('yolov8n.pt')
            self.status_msg = "Warming up model..."
            # Warm-up pass to speed up first inference
            self.model(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)
            self.status_msg = "Ready"
            print("[Detector] YOLO model loaded and warmed up.")
            return True
        except Exception as e:
            self.status_msg = f"Model Error: {e}"
            print(f"[Detector] Error loading model: {e}")
            return False

    # ---- Detection Control ----

    def start_detection(self, camera_index=0):
        """Start background detection thread."""
        if self.is_running:
            return
        if not self.load_model():
            print("[Detector] Cannot start — model not loaded.")
            return
        self.is_running = True
        thread = threading.Thread(
            target=self._detection_loop,
            args=(camera_index,),
            daemon=True
        )
        thread.start()
        print(f"[Detector] Detection thread started on camera {camera_index}.")

    def stop_detection(self):
        """Stop the background detection thread and release camera."""
        self.is_running = False
        time.sleep(0.15)  # Allow thread to exit cleanly
        if self.cap:
            self.cap.release()
            self.cap = None
        self.latest_frame = None
        self.status_msg = "Stopped"
        print("[Detector] Detection stopped.")

    # ---- Background Loop ----

    def _detection_loop(self, camera_index):
        """Internal loop: read frames, run YOLO, update results."""
        self.status_msg = "Opening camera..."

        # On Windows, DSHOW backend opens much faster
        if os.name == 'nt':
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(camera_index)

        # Fallback if DSHOW failed
        if not self.cap.isOpened() and os.name == 'nt':
            self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            self.status_msg = "❌ Camera not found or busy"
            self.is_running = False
            print("[Detector] Failed to open camera.")
            return

        # Set resolution for faster processing
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.status_msg = "Camera connected ✅"

        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            # Run detection — class 0 = person only
            results = self.model(
                frame,
                conf=0.35,
                iou=0.5,
                verbose=False,
                classes=[0],
                imgsz=480
            )

            raw_count = 0
            annotated = frame.copy()

            if results:
                for box in results[0].boxes:
                    raw_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        annotated, f"Person {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                    )

            # Smooth count using rolling median (reduces false spikes)
            self.count_buffer.append(raw_count)
            if len(self.count_buffer) > self.buffer_size:
                self.count_buffer.pop(0)
            self.latest_count = int(np.median(self.count_buffer)) if self.count_buffer else raw_count

            # Determine crowd level
            if self.latest_count <= 4:
                self.crowd_level = "Low"
                color = (0, 255, 0)
            elif self.latest_count <= 7:
                self.crowd_level = "Medium"
                color = (0, 165, 255)
            else:
                self.crowd_level = "High"
                color = (0, 0, 255)

            # Draw overlay text on frame
            cv2.putText(
                annotated,
                f'People: {self.latest_count} ({self.crowd_level})',
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3
            )

            self.latest_frame = annotated

            # Push to Firebase if connected
            if self.fb_manager:
                self.fb_manager.update_crowd_status(
                    self.bus_id, self.latest_count, self.crowd_level
                )

            time.sleep(0.001)  # Minimal sleep for max FPS

        # Cleanup on exit
        if self.cap:
            self.cap.release()

    # ---- Data Access ----

    def get_latest_frame(self):
        """Return the latest annotated frame (or None if not running)."""
        return self.latest_frame

    def get_crowd_data(self):
        """Return current crowd count and level."""
        return {
            'count': self.latest_count,
            'level': self.crowd_level
        }


# ---- Cached Singleton ----

@st.cache_resource
def get_live_detector():
    """Return a shared (cached) LiveCrowdDetector with model pre-loaded."""
    from firebase_manager import get_firebase_manager
    detector = LiveCrowdDetector()
    detector.load_model()
    fb = get_firebase_manager()
    if fb.initialized:
        detector.set_firebase_manager(fb)
    return detector
