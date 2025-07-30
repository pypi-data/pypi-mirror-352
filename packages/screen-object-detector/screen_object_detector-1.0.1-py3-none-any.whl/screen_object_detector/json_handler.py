import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List


class JSONHandler:
    """
    Handles JSON file operations for screen detection results.

    Automatically creates JSON files and manages detection data storage.
    """

    def __init__(self, json_file: str = "screen_detections.json"):
        """
        Initialize JSON handler.

        Args:
            json_file (str): Path to JSON file for storing detection results
        """
        self.json_file = json_file
        self._ensure_json_file_exists()

    def _ensure_json_file_exists(self):
        """Create JSON file with initial data if it doesn't exist."""
        json_dir = os.path.dirname(self.json_file) if os.path.dirname(self.json_file) else '.'
        os.makedirs(json_dir, exist_ok=True)

        if not os.path.exists(self.json_file):
            initial_data = {
                "timestamp": datetime.now().isoformat(),
                "x": None,
                "y": None,
                "click": False,
                "confidence": None,
                "screen_resolution": None
            }

            try:
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
                print(f"Created JSON file: {self.json_file}")
            except Exception as e:
                print(f"Error creating JSON file: {e}")

    def save_detection(self, x: Optional[int], y: Optional[int], click: bool,
                       monitor_info: Dict[str, Any], confidence: Optional[float] = None):
        """
        Save detection results to JSON file.

        Args:
            x (int, optional): X coordinate of detected object
            y (int, optional): Y coordinate of detected object
            click (bool): Whether object was detected
            monitor_info (dict): Screen resolution and monitor information
            confidence (float, optional): Detection confidence score
        """
        detection_data = {
            "timestamp": datetime.now().isoformat(),
            "x": x,
            "y": y,
            "click": click,
            "confidence": confidence,
            "screen_resolution": f"{monitor_info.get('width', 0)}x{monitor_info.get('height', 0)}"
        }

        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(detection_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving JSON: {e}")

    def load_detection(self) -> Optional[Dict[str, Any]]:
        """
        Load current detection data from JSON file.

        Returns:
            dict or None: Detection data or None if file doesn't exist/error
        """
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None

    def get_detection_history(self, history_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Append current detection to history file and return history.

        Args:
            history_file (str, optional): Path to history file

        Returns:
            list: List of detection records (max 100 latest)
        """
        if history_file is None:
            base_name = self.json_file.replace('.json', '')
            history_file = f"{base_name}_history.json"

        current_data = self.load_detection()
        if current_data is None:
            return []

        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []

        history.append(current_data)

        # Keep only last 100 records
        if len(history) > 100:
            history = history[-100:]

        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

        return history

    def print_current_status(self):
        """Print current detection status to console."""
        data = self.load_detection()
        if data:
            print(f"\nCurrent detection status:")
            print(f"   Time: {data['timestamp']}")
            print(f"   Coordinates: {data.get('x', 'None')}, {data.get('y', 'None')}")
            print(f"   Object detected: {data['click']}")
            if 'confidence' in data and data['confidence'] is not None:
                print(f"   Confidence: {data['confidence']:.3f}")
            if 'screen_resolution' in data:
                print(f"   Resolution: {data['screen_resolution']}")
            print()
        else:
            print("No detection data found\n")

    def clear_detection_data(self):
        """Reset JSON file to initial state."""
        self._ensure_json_file_exists()