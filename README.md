# Flight Kiosk System

A Python-based self-service kiosk for flight booking, face recognition check-in, and boarding pass generation with ESP32 integration.

## Features

- **Flight Booking**: Search and book flights with airport fuzzy search
- **Face Capture**: Auto-capture passenger face during booking
- **Check-In**: Face recognition based self check-in
- **Boarding Pass**: PDF generation with voice announcements
- **History**: View and manage all tickets
- **ESP32 Integration**: Gate control via MQTT or Serial

## Requirements

- Python 3.10+
- Webcam for face capture
- (Optional) ESP32-S3 for gate control

## Quick Start

```bash
# Navigate to the app directory
cd desktop_app

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Project Structure

```
FinalProject/
├── desktop_app/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Dependencies
│   ├── gui/                  # GUI components
│   │   ├── app.py           # Main window
│   │   ├── booking_view.py  # Booking interface
│   │   ├── checkin_view.py  # Check-in interface
│   │   ├── history_view.py  # Ticket management
│   │   └── components/      # Reusable widgets
│   ├── services/            # Business logic
│   │   ├── face_service.py  # Face detection/recognition
│   │   ├── voice_service.py # TTS announcements
│   │   ├── esp_service.py   # ESP32 communication
│   │   └── ...
│   └── database/            # SQLite database
└── esp32/
    └── gate_controller/     # ESP32 firmware
```

## ESP32 Setup

1. Flash `esp32/gate_controller/gate_controller.ino` to your ESP32-S3
2. Update WiFi credentials in the firmware
3. Connect servo, LEDs, and buzzer as per pin definitions
4. The kiosk will auto-detect the ESP32 on check-in

## License

MIT License
