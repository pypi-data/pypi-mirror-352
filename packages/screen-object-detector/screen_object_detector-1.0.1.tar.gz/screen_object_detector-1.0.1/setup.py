from setuptools import setup, find_packages

setup(
    name="screen-object-detector",
    version="1.0.1",
    author="Jester",
    author_email="thettboy11@gmail.com",
    description="Real-time object detection on screen using YOLO models",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "ultralytics>=8.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.21.0",
        "mss>=6.1.0",
        "pillow>=9.0.0",
    ],
    entry_points={
        'console_scripts': [
            'screen-detector=screen_object_detector.cli:main',
        ],
    },
)