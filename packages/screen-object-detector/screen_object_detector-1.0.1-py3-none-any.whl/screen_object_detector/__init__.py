"""
Screen Object Detector Library

A Python library for real-time object detection on screen using YOLO models.
Automatically saves detection results to JSON files.
"""

from .screen_detector import ScreenDetector
from .json_handler import JSONHandler
from .cli import main as cli_main

__version__ = "1.0.1"
__author__ = "Jester"
__email__ = "thettboy11@gmail.com"
__description__ = "Real-time object detection on screen with JSON output"

__all__ = [
    "ScreenDetector",
    "JSONHandler",
    "cli_main",
]