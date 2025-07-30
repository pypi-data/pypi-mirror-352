import cv2
import numpy as np
import mss
import time
from ultralytics import YOLO
from .json_handler import JSONHandler
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, Callable


class ScreenDetector:
    """
    Real-time object detection on screen using YOLO models.

    Automatically saves detection results to JSON files and provides
    various detection modes and callback functionality.
    """

    def __init__(self, model_path: str, target_class_id: int = 0,
                 json_file: str = "screen_detections.json",
                 confidence_threshold: float = 0.5,
                 clean_output: bool = False,
                 monitor_index: int = 1):
        """
        Initialize screen detector.

        Args:
            model_path (str): Path to YOLO model file (.pt)
            target_class_id (int): Class ID to detect (default: 0)
            json_file (str): JSON file path for saving results
            confidence_threshold (float): Detection confidence threshold (0.0-1.0)
            clean_output (bool): Whether to use clean output mode
            monitor_index (int): Monitor index to capture (1 = primary monitor)
        """
        if not clean_output:
            print(f"Loading YOLO model: {model_path}")

        self.model = YOLO(model_path)
        self.target_class_id = target_class_id
        self.confidence_threshold = confidence_threshold
        self.json_handler = JSONHandler(json_file)
        self.running = False
        self.clean_output = clean_output
        self.last_click_status = None
        self.detection_callback = None

        # Initialize screen capture
        with mss.mss() as sct:
            self.monitor = sct.monitors[monitor_index]

        if not clean_output:
            print(f"Model loaded successfully")
            print(f"Screen resolution: {self.monitor['width']}x{self.monitor['height']}")
            print(f"Target class ID: {target_class_id}")
            print(f"Confidence threshold: {confidence_threshold}")

            if hasattr(self.model, 'names'):
                print(f"Available classes: {self.model.names}")

    def capture_screen(self) -> np.ndarray:
        """
        Capture current screen.

        Returns:
            np.ndarray: Screen capture as BGR image
        """
        with mss.mss() as sct:
            screenshot = sct.grab(self.monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            return frame

    def detect_object(self, frame: np.ndarray) -> Tuple[Optional[int], Optional[int], bool, float]:
        """
        Detect target object in frame.

        Args:
            frame (np.ndarray): Input image frame

        Returns:
            tuple: (x, y, detected, confidence) - coordinates, detection status, and confidence
        """
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)

        best_detection = None
        highest_confidence = 0

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])

                    if class_id == self.target_class_id:
                        if confidence > highest_confidence:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            center_x = int((x1 + x2) / 2)
                            center_y = int((y1 + y2) / 2)
                            best_detection = (center_x, center_y, True, confidence)
                            highest_confidence = confidence

        if best_detection:
            return best_detection
        else:
            return None, None, False, 0.0

    def single_detection(self) -> Tuple[Optional[int], Optional[int], bool, float]:
        """
        Perform single detection and save to JSON.

        Returns:
            tuple: (x, y, detected, confidence)
        """
        frame = self.capture_screen()
        x, y, click, confidence = self.detect_object(frame)
        self.json_handler.save_detection(x, y, click, self.monitor, confidence)

        if not self.clean_output:
            if click:
                print(f"Object FOUND at ({x}, {y}) - confidence: {confidence:.3f}")
            else:
                print(f"Object NOT FOUND")

        # Call callback if set
        if self.detection_callback:
            self.detection_callback(x, y, click, confidence)

        return x, y, click, confidence

    def start_continuous_detection(self, update_interval: float = 0.5,
                                   duration: Optional[int] = None,
                                   callback: Optional[Callable] = None):
        """
        Start continuous detection loop.

        Args:
            update_interval (float): Time between detections in seconds
            duration (int, optional): Total runtime in seconds (None = infinite)
            callback (callable, optional): Function to call on each detection
        """
        self.running = True
        self.detection_callback = callback
        start_time = time.time()

        if not self.clean_output:
            print(f"Starting continuous detection (confidence: {self.confidence_threshold})")
            if duration:
                print(f"Runtime: {duration} seconds")
            else:
                print("Runtime: infinite (press Ctrl+C to stop)")

        while self.running:
            try:
                frame = self.capture_screen()
                x, y, click, confidence = self.detect_object(frame)
                self.json_handler.save_detection(x, y, click, self.monitor, confidence)

                timestamp = datetime.now().strftime("%H:%M:%S")

                # Output handling
                if self.clean_output:
                    if self.last_click_status != click:
                        if click:
                            print(f"[{timestamp}] FOUND: ({x}, {y}) conf:{confidence:.3f}")
                        else:
                            print(f"[{timestamp}] LOST")
                        self.last_click_status = click
                else:
                    if click:
                        print(f"[{timestamp}] Object found: ({x}, {y}) - confidence: {confidence:.3f}")
                    else:
                        print(f"[{timestamp}] Object not found")

                # Call callback if set
                if self.detection_callback:
                    self.detection_callback(x, y, click, confidence)

                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    print(f"\nRuntime {duration} seconds completed. Stopping...")
                    break

                time.sleep(update_interval)

            except Exception as e:
                print(f"Detection error: {e}")
                time.sleep(1)

    def set_confidence_threshold(self, new_threshold: float):
        """
        Update confidence threshold.

        Args:
            new_threshold (float): New threshold value (0.0-1.0)
        """
        if 0.0 <= new_threshold <= 1.0:
            old_threshold = self.confidence_threshold
            self.confidence_threshold = new_threshold
            if not self.clean_output:
                print(f"Confidence threshold: {old_threshold} → {new_threshold}")
        else:
            raise ValueError(f"Invalid confidence threshold: {new_threshold} (must be 0.0-1.0)")

    def set_detection_callback(self, callback: Callable[[Optional[int], Optional[int], bool, float], None]):
        """
        Set callback function for detection events.

        Args:
            callback (callable): Function that receives (x, y, detected, confidence)
        """
        self.detection_callback = callback

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            dict: Model information including classes and settings
        """
        return {
            "classes": self.model.names if hasattr(self.model, 'names') else "Unknown",
            "target_class_id": self.target_class_id,
            "confidence_threshold": self.confidence_threshold,
            "screen_resolution": f"{self.monitor['width']}x{self.monitor['height']}"
        }

    def get_current_detection(self) -> Optional[Dict[str, Any]]:
        """
        Get current detection data from JSON.

        Returns:
            dict or None: Current detection data
        """
        return self.json_handler.load_detection()

    def get_detection_history(self) -> list:
        """
        Get detection history.

        Returns:
            list: List of detection records
        """
        return self.json_handler.get_detection_history()

    def print_status(self):
        """Print current detection status."""
        self.json_handler.print_current_status()

    def stop_detection(self):
        """Stop continuous detection."""
        self.running = False
        if not self.clean_output:
            print("Detection stopped")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_detection()