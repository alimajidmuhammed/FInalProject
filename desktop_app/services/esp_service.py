"""
ESP Service - Handles communication with ESP32 devices.
Supports MQTT (WiFi) and Serial (USB) connections.
"""
import json
import threading
import time
from typing import Optional, Callable
from enum import Enum

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

from config import (
    MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_GATE, MQTT_TOPIC_STATUS,
    SERIAL_PORT, SERIAL_BAUD
)


class ESPCommand(Enum):
    """Commands that can be sent to ESP32."""
    OPEN_GATE = "OPEN_GATE"
    CLOSE_GATE = "CLOSE_GATE"
    LED_GREEN = "LED_GREEN"
    LED_BLUE = "LED_BLUE"
    LED_RED = "LED_RED"
    LED_OFF = "LED_OFF"
    BUZZER_SUCCESS = "BUZZER_SUCCESS"
    BUZZER_ERROR = "BUZZER_ERROR"
    STATUS = "STATUS"


class ESPService:
    """Manages ESP32 communication via MQTT or Serial."""
    
    def __init__(self):
        """Initialize ESP service."""
        self.mqtt_client: Optional[mqtt.Client] = None
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self.connection_type: Optional[str] = None  # 'mqtt' or 'serial'
        self._status_callback: Optional[Callable] = None
        self._connection_callbacks: List[Callable] = []
        self._reconnect_thread: Optional[threading.Thread] = None
        self._should_reconnect = False

    def register_connection_callback(self, callback: Callable):
        """Register a callback for connection state changes (is_connected: bool)."""
        if callback not in self._connection_callbacks:
            self._connection_callbacks.append(callback)
            # Immediately notify with current state
            try:
                callback(self.is_connected)
            except Exception as e:
                print(f"Error in initial connection callback: {e}")

    def unregister_connection_callback(self, callback: Callable):
        """Unregister a connection callback."""
        if callback in self._connection_callbacks:
            self._connection_callbacks.remove(callback)

    def set_connection_callback(self, callback: Callable):
        """Legacy support for set_connection_callback."""
        self.register_connection_callback(callback)
    
    def _notify_connection_change(self, is_connected: bool):
        """Notify all listeners of connection change."""
        self.is_connected = is_connected
        for callback in self._connection_callbacks:
            try:
                callback(is_connected)
            except Exception as e:
                print(f"Error in connection callback: {e}")
    
    # ==================== MQTT Methods ====================
    
    def connect_mqtt(
        self, 
        broker: str = None, 
        port: int = None
    ) -> bool:
        """Connect to MQTT broker."""
        if not MQTT_AVAILABLE:
            print("Warning: paho-mqtt not available")
            return False
        
        broker = broker or MQTT_BROKER
        port = port or MQTT_PORT
        
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_message = self._on_mqtt_message
            
            self.mqtt_client.connect(broker, port, keepalive=60)
            self.mqtt_client.loop_start()
            
            # Wait briefly for connection
            time.sleep(1)
            
            if self.is_connected:
                self.connection_type = 'mqtt'
                return True
            return False
            
        except Exception as e:
            print(f"MQTT connection error: {e}")
            return False
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback when MQTT connects."""
        if rc == 0:
            self._notify_connection_change(True)
            # Subscribe to status topic
            client.subscribe(MQTT_TOPIC_STATUS)
            print("Connected to MQTT broker")
        else:
            print(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback when MQTT disconnects."""
        self._notify_connection_change(False)
        print("Disconnected from MQTT broker")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Callback when MQTT message received."""
        try:
            payload = msg.payload.decode('utf-8')
            if self._status_callback:
                self._status_callback(msg.topic, payload)
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def _send_mqtt(self, command: str, payload: dict = None) -> bool:
        """Send command via MQTT."""
        if not self.mqtt_client or not self.is_connected:
            return False
        
        try:
            message = {'command': command}
            if payload:
                message.update(payload)
            
            self.mqtt_client.publish(
                MQTT_TOPIC_GATE,
                json.dumps(message)
            )
            return True
        except Exception as e:
            print(f"MQTT send error: {e}")
            return False
    
    # ==================== Serial Methods ====================
    
    def connect_serial(self, port: str = None, baud: int = None) -> bool:
        """Connect via Serial (USB)."""
        if not SERIAL_AVAILABLE:
            print("Warning: pyserial not available")
            return False
        
        port = port or SERIAL_PORT
        baud = baud or SERIAL_BAUD
        
        try:
            self.serial_conn = serial.Serial(port, baud, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            self._notify_connection_change(True)
            self.connection_type = 'serial'
            print(f"Connected to serial port {port}")
            
            # Start reading thread
            self._start_serial_reader()
            
            return True
            
        except Exception as e:
            print(f"Serial connection error: {e}")
            return False
    
    def _start_serial_reader(self):
        """Start background thread to read serial data."""
        def reader():
            while self.serial_conn and self.serial_conn.is_open:
                try:
                    if self.serial_conn.in_waiting:
                        try:
                            line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                            if line and self._status_callback:
                                self._status_callback('serial', line)
                        except UnicodeDecodeError:
                            continue  # Ignore encoding errors
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Serial read fatal error: {e}")
                    self.disconnect()
                    break
        
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
    
    def _send_serial(self, command: str) -> bool:
        """Send command via Serial."""
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
        
        try:
            self.serial_conn.write(f"{command}\n".encode('utf-8'))
            return True
        except Exception as e:
            print(f"Serial send error: {e}")
            return False
    
    @staticmethod
    def list_serial_ports() -> list:
        """List available serial ports."""
        if not SERIAL_AVAILABLE:
            return []
        
        ports = serial.tools.list_ports.comports()
        return [(p.device, p.description) for p in ports]
    
    # ==================== Unified Interface ====================
    
    def send_command(self, command: ESPCommand, payload: dict = None) -> bool:
        """Send command to ESP32 using current connection method."""
        if not self.is_connected:
            print("ESP not connected")
            return False
        
        if self.connection_type == 'mqtt':
            return self._send_mqtt(command.value, payload)
        elif self.connection_type == 'serial':
            return self._send_serial(command.value)
        
        return False
    
    def open_gate(self) -> bool:
        """Open the gate."""
        return self.send_command(ESPCommand.OPEN_GATE)
    
    def led_success(self) -> bool:
        """Turn on green LED."""
        return self.send_command(ESPCommand.LED_GREEN)
    
    def led_error(self) -> bool:
        """Turn on red LED."""
        return self.send_command(ESPCommand.LED_RED)
    
    def led_scanning(self) -> bool:
        """Turn on blue LED (scanning)."""
        return self.send_command(ESPCommand.LED_BLUE)
    
    def led_off(self) -> bool:
        """Turn off LEDs."""
        return self.send_command(ESPCommand.LED_OFF)
    
    def buzzer_success(self) -> bool:
        """Play success buzzer."""
        return self.send_command(ESPCommand.BUZZER_SUCCESS)
    
    def buzzer_error(self) -> bool:
        """Play error buzzer."""
        return self.send_command(ESPCommand.BUZZER_ERROR)
    
    def on_checkin_success(self) -> bool:
        """Perform all success actions (LED + gate + buzzer)."""
        success = True
        success &= self.led_success()
        success &= self.buzzer_success()
        success &= self.open_gate()
        return success
    
    def on_checkin_failure(self) -> bool:
        """Perform all failure actions (red LED + error buzzer)."""
        success = True
        success &= self.led_error()
        success &= self.buzzer_error()
        return success
    
    def set_status_callback(self, callback: Callable):
        """Set callback for ESP status messages."""
        self._status_callback = callback
    
    def disconnect(self):
        """Disconnect from ESP32."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.mqtt_client = None
        
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None
        
        self.serial_conn = None
        
        self._notify_connection_change(False)
        self.connection_type = None
    
    def check_connection(self) -> bool:
        """Force a check of the current connection status."""
        was_connected = self.is_connected
        is_now_connected = False
        
        if self.connection_type == 'mqtt' and self.mqtt_client:
            is_now_connected = self.mqtt_client.is_connected()
        elif self.connection_type == 'serial' and self.serial_conn:
            is_now_connected = self.serial_conn.is_open
            
        if was_connected != is_now_connected:
            self._notify_connection_change(is_now_connected)
            if not is_now_connected:
                self.connection_type = None
                
        return is_now_connected

    def auto_connect(self) -> bool:
        """Attempt to auto-connect using best available method."""
        # Try MQTT first
        if MQTT_AVAILABLE and self.connect_mqtt():
            return True
        
        # Try Serial
        if SERIAL_AVAILABLE:
            ports = self.list_serial_ports()
            for port, desc in ports:
                if 'USB' in desc.upper() or 'ESP' in desc.upper():
                    if self.connect_serial(port):
                        return True
        
        print("No ESP32 connection available")
        return False


# Global ESP service instance
esp_service = ESPService()
