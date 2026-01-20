"""
QR Code Service for Flight Kiosk System.
Handles QR code generation for tickets and scanning for check-in.
Uses OpenCV's built-in QR decoder with pyzbar as fallback.
"""
import json
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import cv2
    HAS_OPENCV = True
    # Check if OpenCV has QR detector
    try:
        _test_detector = cv2.QRCodeDetector()
        HAS_OPENCV_QR = True
    except Exception:
        HAS_OPENCV_QR = False
except ImportError:
    HAS_OPENCV = False
    HAS_OPENCV_QR = False

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    logger.warning("qrcode library not installed. QR generation will be disabled.")

try:
    from pyzbar import pyzbar
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False
    logger.info("pyzbar not available, using OpenCV QR detector")


class QRService:
    """Service for generating and scanning QR codes."""
    
    def __init__(self):
        """Initialize QR service."""
        self.qr_dir = Path(__file__).parent.parent.parent / 'data' / 'qr_codes'
        self.qr_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenCV QR detector
        if HAS_OPENCV_QR:
            self._qr_detector = cv2.QRCodeDetector()
        else:
            self._qr_detector = None
        
        # Log available methods
        if HAS_OPENCV_QR:
            logger.info("QR scanning: OpenCV QRCodeDetector available")
        elif HAS_PYZBAR:
            logger.info("QR scanning: pyzbar available")
        else:
            logger.warning("QR scanning: No scanner available!")
    
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
            # Create QR data payload - simplified for easier reading
            qr_data = {
                'type': 'flight_ticket',
                'ticket': ticket_number,
                'passenger': passenger_name,
                'route': route,
                'date': flight_date,
                'version': '1.0'
            }
            
            # Create QR code with high error correction
            qr = qrcode.QRCode(
                version=2,  # Slightly larger for better readability
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            # Create image with high contrast colors
            img = qr.make_image(fill_color='black', back_color='white')
            
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
        Uses OpenCV first, then falls back to pyzbar.
        
        Args:
            image: OpenCV image (numpy array)
            
        Returns:
            Decoded ticket data dict, or None if not found/invalid
        """
        # Try OpenCV QR detector first (no external dependencies)
        if HAS_OPENCV_QR and self._qr_detector is not None:
            result = self._decode_with_opencv(image)
            if result:
                return result
        
        # Fall back to pyzbar if available
        if HAS_PYZBAR:
            result = self._decode_with_pyzbar(image)
            if result:
                return result
        
        return None
    
    def _decode_with_opencv(self, image) -> Optional[Dict]:
        """Decode QR using OpenCV's built-in detector."""
        try:
            # Convert to grayscale for better detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Enhance contrast for better QR detection
            gray = cv2.equalizeHist(gray)
            
            # Detect and decode
            data, points, _ = self._qr_detector.detectAndDecode(gray)
            
            if data:
                try:
                    parsed = json.loads(data)
                    if parsed.get('type') == 'flight_ticket':
                        logger.info(f"OpenCV decoded QR: ticket {parsed.get('ticket')}")
                        return parsed
                except json.JSONDecodeError:
                    # Try parsing as simple ticket number
                    if data.startswith('TK-'):
                        return {'type': 'flight_ticket', 'ticket': data}
            
            return None
            
        except Exception as e:
            logger.debug(f"OpenCV QR decode error: {e}")
            return None
    
    def _decode_with_pyzbar(self, image) -> Optional[Dict]:
        """Decode QR using pyzbar library."""
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
                            logger.info(f"pyzbar decoded QR: ticket {data.get('ticket')}")
                            return data
                    except json.JSONDecodeError:
                        # Try parsing as simple ticket number
                        text = obj.data.decode('utf-8')
                        if text.startswith('TK-'):
                            return {'type': 'flight_ticket', 'ticket': text}
            
            return None
            
        except Exception as e:
            logger.debug(f"pyzbar QR decode error: {e}")
            return None
    
    def get_qr_bounds(self, image) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the bounding box of a QR code in an image.
        
        Args:
            image: OpenCV image (numpy array)
            
        Returns:
            Tuple of (x, y, width, height) or None if no QR found
        """
        if not HAS_OPENCV:
            return None
        
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Try OpenCV detector
            if HAS_OPENCV_QR and self._qr_detector is not None:
                _, points, _ = self._qr_detector.detectAndDecode(gray)
                if points is not None and len(points) > 0:
                    pts = points[0]
                    x = int(min(pts[:, 0]))
                    y = int(min(pts[:, 1]))
                    w = int(max(pts[:, 0]) - x)
                    h = int(max(pts[:, 1]) - y)
                    return (x, y, w, h)
            
            # Try pyzbar
            if HAS_PYZBAR:
                decoded_objects = pyzbar.decode(gray)
                for obj in decoded_objects:
                    if obj.type == 'QRCODE':
                        rect = obj.rect
                        return (rect.left, rect.top, rect.width, rect.height)
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to get QR bounds: {e}")
            return None
    
    def is_available(self) -> Dict[str, bool]:
        """Check which QR features are available."""
        return {
            'generation': HAS_QRCODE,
            'scanning': HAS_OPENCV_QR or HAS_PYZBAR,
            'opencv_scanner': HAS_OPENCV_QR,
            'pyzbar_scanner': HAS_PYZBAR
        }


# Global QR service instance
qr_service = QRService()
