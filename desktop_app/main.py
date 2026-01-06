#!/usr/bin/env python3
"""
Flight Kiosk System - Main Entry Point

A self-service flight ticketing and check-in kiosk with:
- Flight booking with airport search
- Face capture during booking
- Face recognition check-in
- Boarding pass generation with voice announcements
- Ticket history management
- ESP32 integration for gate control

Run with: python main.py
"""
import sys
import warnings
from pathlib import Path

# Suppress deprecation warnings from third-party packages
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import init_directories
from gui.app import create_app


def main():
    """Main entry point."""
    print("=" * 50)
    print("  ✈ Flight Kiosk System")
    print("  Self-Service Terminal v1.0.0")
    print("=" * 50)
    
    # Initialize directories
    print("\n[*] Initializing directories...")
    init_directories()
    
    # Check dependencies
    print("[*] Checking dependencies...")
    check_dependencies()
    
    # Create and run app
    print("[*] Starting application...")
    print("-" * 50)
    
    app = create_app()
    app.mainloop()


def check_dependencies():
    """Check if required dependencies are available."""
    missing = []
    
    try:
        import customtkinter
        print("  ✓ CustomTkinter")
    except ImportError:
        missing.append("customtkinter")
        print("  ✗ CustomTkinter")
    
    try:
        import cv2
        print("  ✓ OpenCV")
    except ImportError:
        missing.append("opencv-python")
        print("  ✗ OpenCV")
    
    try:
        import mediapipe
        print("  ✓ MediaPipe")
    except ImportError:
        print("  ⚠ MediaPipe (optional - will use OpenCV fallback)")
    
    try:
        import face_recognition
        print("  ✓ face_recognition")
    except ImportError:
        print("  ⚠ face_recognition (face recognition will not work)")
    
    try:
        import edge_tts
        print("  ✓ edge-tts")
    except ImportError:
        print("  ⚠ edge-tts (voice announcements will not work)")
    
    try:
        import reportlab
        print("  ✓ ReportLab")
    except ImportError:
        print("  ⚠ ReportLab (boarding pass PDF will not work)")
    
    try:
        from tkcalendar import DateEntry
        print("  ✓ tkcalendar")
    except ImportError:
        missing.append("tkcalendar")
        print("  ✗ tkcalendar")
    
    try:
        import rapidfuzz
        print("  ✓ rapidfuzz")
    except ImportError:
        missing.append("rapidfuzz")
        print("  ✗ rapidfuzz")
    
    try:
        import paho.mqtt.client
        print("  ✓ paho-mqtt")
    except ImportError:
        print("  ⚠ paho-mqtt (MQTT ESP32 control will not work)")
    
    try:
        import serial
        print("  ✓ pyserial")
    except ImportError:
        print("  ⚠ pyserial (Serial ESP32 control will not work)")
    
    if missing:
        print(f"\n[!] Missing required dependencies: {', '.join(missing)}")
        print("    Install with: pip install " + " ".join(missing))
        sys.exit(1)
    
    print()


if __name__ == "__main__":
    main()
