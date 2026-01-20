"""
Flight Ticketing Kiosk System - Configuration
Version 2.0 with multi-language and enhanced features
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Database
DATABASE_PATH = DATA_DIR / "tickets.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Face data storage
FACES_DIR = DATA_DIR / "faces"
BOARDING_PASSES_DIR = DATA_DIR / "boarding_passes"

# QR Code storage
QR_CODES_DIR = DATA_DIR / "qr_codes"

# Logs directory
LOGS_DIR = DATA_DIR / "logs"
REPORTS_DIR = DATA_DIR / "reports"

# Encryption key file
ENCRYPTION_KEY_FILE = DATA_DIR / ".encryption_key"

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Face recognition settings
FACE_MATCH_THRESHOLD = 0.45  # Lower = stricter (0.45 = 55% minimum confidence)
FACE_STABILITY_FRAMES = 30  # Frames to wait before auto-capture

# QR Code settings
QR_CHECK_IN_ENABLED = True
QR_BOX_SIZE = 10
QR_BORDER = 4

# ESP32 settings
MQTT_BROKER = "localhost"  # Change to your MQTT broker IP
MQTT_PORT = 1883
MQTT_TOPIC_GATE = "kiosk/gate"
MQTT_TOPIC_STATUS = "kiosk/status"

SERIAL_PORT = "/dev/ttyUSB0"  # Change based on your system
SERIAL_BAUD = 9600

# Voice settings
VOICE_NAME = "en-US-AriaNeural"  # Microsoft Edge TTS female voice
VOICE_RATE = "+0%"

# Session settings
SESSION_TIMEOUT_SECONDS = 120  # 2 minutes of inactivity before auto-reset

# Admin settings
ADMIN_PIN = "1234"  # PIN for admin functions like reset check-in

# Security settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
RATE_LIMIT_WINDOW_SECONDS = 60
MAX_FACE_ATTEMPTS_PER_MINUTE = 10

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_RETENTION_DAYS = 30
LOG_MAX_SIZE_MB = 5
LOG_BACKUP_COUNT = 5

# Localization settings
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "ar", "ku"]
LOCALES_DIR = BASE_DIR / "locales"

# Accessibility settings
ACCESSIBILITY_MODE = False
HIGH_CONTRAST = False
LARGE_TEXT = False
VOICE_GUIDANCE = True

# Sound settings
SOUNDS_DIR = ASSETS_DIR / "sounds"
SOUND_ENABLED = True

# UI Theme colors (Modern Dark Airline Theme)
THEME = {
    "bg_primary": "#0a0e17",      # Deep navy black
    "bg_secondary": "#141b2d",    # Dark blue-gray
    "bg_card": "#1e2738",         # Card background
    "accent": "#00d4ff",          # Bright cyan
    "accent_hover": "#00a8cc",    # Darker cyan
    "success": "#00e676",         # Green
    "warning": "#ffc107",         # Amber
    "error": "#ff5252",           # Red
    "text_primary": "#ffffff",    # White
    "text_secondary": "#8892a0",  # Gray
    "border": "#2a3548",          # Border color
}

# Ensure directories exist
def init_directories():
    """Create required directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    BOARDING_PASSES_DIR.mkdir(parents=True, exist_ok=True)
    QR_CODES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    LOCALES_DIR.mkdir(parents=True, exist_ok=True)
