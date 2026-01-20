import sys
import time
from pathlib import Path

# Add desktop_app to path
sys.path.insert(0, str(Path(__file__).parent / "desktop_app"))

from services.esp_service import esp_service

def test_esp_connection():
    print("[*] Starting ESP32 Hardware Verification...")
    
    # 1. Attempt Auto-Connect
    print("  [+] Attempting to auto-connect...")
    connected = esp_service.auto_connect()
    
    if not connected:
        print("  [✗] Connection Failed!")
        print("      Check if /dev/ttyUSB0 belongs to your user (try: sudo chmod 666 /dev/ttyUSB0)")
        return
    
    print(f"  [✓] Connected via: {esp_service.connection_type}")
    
    # 2. Test Commands
    try:
        print("  [+] Sending GREEN LED command (Check your ESP)...")
        esp_service.led_success()
        time.sleep(2)
        
        print("  [+] Sending BUZZER SUCCESS command...")
        esp_service.buzzer_success()
        time.sleep(1)
        
        print("  [+] Sending LED OFF command...")
        esp_service.led_off()
        
        print("\n[✓] VERIFICATION COMPLETE: Communication is working.")
        print("    You should have seen the LED turn Green and heard the buzzer.")
        
    except Exception as e:
        print(f"  [✗] Error during test: {e}")
    finally:
        esp_service.disconnect()

if __name__ == "__main__":
    test_esp_connection()
