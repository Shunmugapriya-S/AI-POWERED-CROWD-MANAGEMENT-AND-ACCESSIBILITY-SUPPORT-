import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
import os

class LiveCrowdDetector:
    def __init__(self):
        """Initialize live crowd detector with YOLO"""
        self.model = None
        self.latest_count = 0
        self.latest_frame = None
        self.is_running = False
        self.cap = None
        self.crowd_level = "Unknown"
        self.fb_manager = None
        self.bus_id = "TN-01-AN-1234" # Default Bus ID
        self.status_msg = "Idle"
        self.count_buffer = []  # For smoothing count
        self.buffer_size = 5    # Reduced for faster response
        
    def set_firebase_manager(self, manager, bus_id=None):
        """Set firebase manager for real-time updates"""
        self.fb_manager = manager
        if bus_id:
            self.bus_id = bus_id
        
    def load_model(self):
        """Load YOLO model only once"""
        if self.model is not None:
            return True
        try:
            self.status_msg = "Loading YOLO model..."
            self.model = YOLO('yolov8n.pt')
            self.status_msg = "Model loaded. Warming up..."
            # Warm up the model
            self.model(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)
            self.status_msg = "Ready"
            return True
        except Exception as e:
            self.status_msg = f"Error: {e}"
            print(f"Error loading model: {e}")
            return False
    
    def start_detection(self, camera_index=0):
        """Start live detection in background thread"""
        if self.is_running:
            return
        
        # Pre-load model before starting thread to avoid race conditions
        if not self.load_model():
            print("Failed to load model")
            return

        self.is_running = True
        thread = threading.Thread(target=self._detection_loop, args=(camera_index,))
        thread.daemon = True
        thread.start()
    
    def _detection_loop(self, camera_index):
        """Main detection loop running in background"""
        self.status_msg = "Opening camera..."
        if os.name == 'nt':
            # On Windows, CAP_DSHOW is much faster to open
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened() and os.name == 'nt':
            # Fallback if DSHOW fails
            self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            self.status_msg = "Error: Camera not found or busy"
            print("Error: Cannot open camera")
            self.is_running = False
            return
        
        self.status_msg = "Camera connected"
        
        # Set lower resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Model is already loaded in start_detection
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            # Run YOLO detection for better accuracy
            # High recall settings: 0.35 confidence and 0.5 IOU to catch people in crowded buses
            # 480 size provides better detail than 320 for person detection
            results = self.model(frame, conf=0.35, iou=0.5, verbose=False, classes=[0], imgsz=480)
            
            count = 0
            annotated_frame = frame.copy()
            
            # Process results efficiently
            if len(results) > 0:
                result = results[0]
                boxes = result.boxes
                for box in boxes:
                    count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    
                    # Visible boxes and labels
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"Person {confidence:.2f}"
                    cv2.putText(annotated_frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Smooth the count using a moving average/median to prevent jumps
            self.count_buffer.append(count)
            if len(self.count_buffer) > self.buffer_size:
                self.count_buffer.pop(0)
            
            # Use median to ignore outliers
            if len(self.count_buffer) > 0:
                smoothed_count = int(np.median(self.count_buffer))
            else:
                smoothed_count = count
                
            self.latest_count = smoothed_count
            
            # Update crowd level using smoothed count
            if self.latest_count <= 4:
                self.crowd_level = "Low"
                color = (0, 255, 0)
            elif self.latest_count <= 7:
                self.crowd_level = "Medium"
                color = (0, 165, 255)
            else:
                self.crowd_level = "High"
                color = (0, 0, 255)
            
            # Add visible overlay
            cv2.putText(annotated_frame, f'People: {self.latest_count} ({self.crowd_level})', (10, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3) # Larger and thicker for visibility
            
            # Store latest frame
            self.latest_frame = annotated_frame
            
            # Update Firebase if manager attached
            if self.fb_manager:
                self.fb_manager.update_crowd_status(self.bus_id, self.latest_count, self.crowd_level)
            
            # Minimal sleep for better FPS
            time.sleep(0.001)
        
        if self.cap:
            self.cap.release()
    
    def stop_detection(self):
        """Stop detection"""
        self.is_running = False
        time.sleep(0.1) # Give thread time to finish
        if self.cap:
            self.cap.release()
            self.cap = None
        self.latest_frame = None
        self.status_msg = "Stopped"
    
    def get_latest_frame(self):
        """Get the latest annotated frame"""
        return self.latest_frame
    
    def get_crowd_data(self):
        """Get current crowd data"""
        return {
            'count': self.latest_count,
            'level': self.crowd_level
        }
