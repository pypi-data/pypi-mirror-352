"""
Screen Object Detector Library

A Python library for real-time object detection on screen using YOLO models.
Automatically saves detection results to JSON files.
"""

from .screen_detector import ScreenDetector
from .json_handler import JSONHandler

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Real-time object detection on screen with JSON output"

__all__ = [
    "ScreenDetector",
    "JSONHandler",
]