"""
QR Code Service for Flight Kiosk System.
Handles QR code generation for tickets and scanning for check-in.
"""
import json
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    logger.warning("qrcode library not installed. QR generation will be disabled.")

try:
    import cv2
    from pyzbar import pyzbar
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False
    logger.warning("pyzbar library not installed. QR scanning will be disabled.")


class QRService:
    """Service for generating and scanning QR codes."""
    
    def __init__(self):
        """Initialize QR service."""
        self.qr_dir = Path(__file__).parent.parent.parent / 'data' / 'qr_codes'
        self.qr_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_ticket_qr(
        self,
        ticket_number: str,
        passenger_name: str,
        route: str,
        flight_date: str,
        save_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Generate a QR code for a ticket.
        
        Args:
            ticket_number: The ticket number
            passenger_name: Full passenger name
            route: Route string (e.g., "JFK → LHR")
            flight_date: Flight date string
            save_path: Optional path to save the QR image
            
        Returns:
            Path to saved QR image, or None on failure
        """
        if not HAS_QRCODE:
            logger.error("qrcode library not available")
            return None
        
        try:
            # Create QR data payload
            qr_data = {
                'type': 'flight_ticket',
                'ticket': ticket_number,
                'passenger': passenger_name,
                'route': route,
                'date': flight_date,
                'version': '1.0'
            }
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            # Create image with custom colors
            img = qr.make_image(fill_color='#0a0e17', back_color='white')
            
            # Determine save path
            if save_path is None:
                save_path = self.qr_dir / f'qr_{ticket_number}.png'
            
            # Save image
            img.save(str(save_path))
            logger.info(f"Generated QR code for ticket {ticket_number}")
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return None
    
    def decode_qr_from_image(self, image) -> Optional[Dict]:
        """
        Decode QR code from an image (numpy array).
        
        Args:
            image: OpenCV image (numpy array)
            
        Returns:
            Decoded ticket data dict, or None if not found/invalid
        """
        if not HAS_PYZBAR:
            logger.error("pyzbar library not available")
            return None
        
        try:
            # Convert to grayscale for better detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Decode QR codes
            decoded_objects = pyzbar.decode(gray)
            
            for obj in decoded_objects:
                if obj.type == 'QRCODE':
                    try:
                        data = json.loads(obj.data.decode('utf-8'))
                        if data.get('type') == 'flight_ticket':
                            logger.info(f"Decoded QR: ticket {data.get('ticket')}")
                            return data
                    except json.JSONDecodeError:
                        # Not a valid JSON QR code
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to decode QR: {e}")
            return None
    
    def get_qr_bounds(self, image) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the bounding box of a QR code in an image.
        
        Args:
            image: OpenCV image (numpy array)
            
        Returns:
            Tuple of (x, y, width, height) or None if no QR found
        """
        if not HAS_PYZBAR:
            return None
        
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            decoded_objects = pyzbar.decode(gray)
            
            for obj in decoded_objects:
                if obj.type == 'QRCODE':
                    rect = obj.rect
                    return (rect.left, rect.top, rect.width, rect.height)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get QR bounds: {e}")
            return None
    
    def is_available(self) -> Dict[str, bool]:
        """Check which QR features are available."""
        return {
            'generation': HAS_QRCODE,
            'scanning': HAS_PYZBAR
        }


# Global QR service instance
qr_service = QRService()
