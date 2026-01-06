"""
Boarding Pass Service - Generates printable boarding passes as PDFs.
Uses ReportLab for professional PDF generation.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional
import io

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm, inch
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

from config import BOARDING_PASSES_DIR, ASSETS_DIR, init_directories


class BoardingPassService:
    """Generates professional boarding pass PDFs."""
    
    # Colors
    PRIMARY_COLOR = HexColor('#0a0e17')
    ACCENT_COLOR = HexColor('#00d4ff')
    SECONDARY_COLOR = HexColor('#141b2d')
    TEXT_COLOR = black
    LIGHT_TEXT = HexColor('#666666')
    
    def __init__(self):
        """Initialize boarding pass service."""
        init_directories()
    
    def generate(
        self,
        ticket_number: str,
        passenger_name: str,
        source_airport: str,
        source_city: str,
        destination_airport: str,
        destination_city: str,
        flight_date: str,
        flight_time: str,
        seat: str,
        gate: str,
        passport_number: str = ""
    ) -> Optional[Path]:
        """
        Generate a boarding pass PDF.
        Returns path to generated PDF or None on failure.
        """
        if not REPORTLAB_AVAILABLE:
            print("Warning: ReportLab not available")
            return None
        
        # Create output filename
        filename = f"boarding_pass_{ticket_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = BOARDING_PASSES_DIR / filename
        
        # Create PDF
        try:
            self._create_boarding_pass(
                str(output_path),
                ticket_number=ticket_number,
                passenger_name=passenger_name,
                source_airport=source_airport,
                source_city=source_city,
                destination_airport=destination_airport,
                destination_city=destination_city,
                flight_date=flight_date,
                flight_time=flight_time,
                seat=seat,
                gate=gate,
                passport_number=passport_number
            )
            return output_path
        except Exception as e:
            print(f"Error generating boarding pass: {e}")
            return None
    
    def _create_boarding_pass(
        self,
        output_path: str,
        **kwargs
    ):
        """Create the actual boarding pass PDF."""
        # Use a custom page size for boarding pass (landscape, smaller)
        page_width = 250 * mm
        page_height = 100 * mm
        
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
        
        # Background
        c.setFillColor(white)
        c.rect(0, 0, page_width, page_height, fill=True)
        
        # Header bar
        c.setFillColor(self.PRIMARY_COLOR)
        c.rect(0, page_height - 25*mm, page_width, 25*mm, fill=True)
        
        # Header text
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(10*mm, page_height - 15*mm, "✈ BOARDING PASS")
        
        c.setFont("Helvetica", 10)
        c.drawRightString(page_width - 10*mm, page_height - 12*mm, f"#{kwargs['ticket_number']}")
        c.drawRightString(page_width - 10*mm, page_height - 18*mm, kwargs['flight_date'])
        
        # Main content area
        content_y = page_height - 35*mm
        
        # Passenger Name
        c.setFillColor(self.LIGHT_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(10*mm, content_y, "PASSENGER NAME")
        
        c.setFillColor(self.TEXT_COLOR)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(10*mm, content_y - 6*mm, kwargs['passenger_name'].upper())
        
        # Flight Route Section
        route_y = content_y - 20*mm
        
        # From
        c.setFillColor(self.LIGHT_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(10*mm, route_y, "FROM")
        
        c.setFillColor(self.TEXT_COLOR)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(10*mm, route_y - 8*mm, kwargs['source_airport'])
        
        c.setFont("Helvetica", 9)
        c.drawString(10*mm, route_y - 15*mm, kwargs['source_city'])
        
        # Arrow
        c.setFillColor(self.ACCENT_COLOR)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(55*mm, route_y - 8*mm, "→")
        
        # To
        c.setFillColor(self.LIGHT_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(70*mm, route_y, "TO")
        
        c.setFillColor(self.TEXT_COLOR)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(70*mm, route_y - 8*mm, kwargs['destination_airport'])
        
        c.setFont("Helvetica", 9)
        c.drawString(70*mm, route_y - 15*mm, kwargs['destination_city'])
        
        # Divider line
        c.setStrokeColor(HexColor('#e0e0e0'))
        c.setLineWidth(0.5)
        c.line(130*mm, page_height - 30*mm, 130*mm, 10*mm)
        
        # Right side - Seat, Gate, Time
        right_x = 145*mm
        
        # Gate
        c.setFillColor(self.LIGHT_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(right_x, content_y, "GATE")
        
        c.setFillColor(self.PRIMARY_COLOR)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(right_x, content_y - 8*mm, kwargs['gate'])
        
        # Seat
        c.setFillColor(self.LIGHT_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(right_x + 40*mm, content_y, "SEAT")
        
        c.setFillColor(self.ACCENT_COLOR)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(right_x + 40*mm, content_y - 8*mm, kwargs['seat'])
        
        # Boarding Time
        c.setFillColor(self.LIGHT_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(right_x, route_y, "BOARDING TIME")
        
        c.setFillColor(self.TEXT_COLOR)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(right_x, route_y - 8*mm, kwargs['flight_time'])
        
        # Footer
        footer_y = 8*mm
        c.setFillColor(self.LIGHT_TEXT)
        c.setFont("Helvetica", 7)
        c.drawString(10*mm, footer_y, "Please arrive at the gate 30 minutes before departure")
        c.drawRightString(page_width - 10*mm, footer_y, "Thank you for flying with us!")
        
        # QR Code
        qr_x = page_width - 35*mm
        qr_y = route_y - 25*mm
        qr_size = 25*mm
        
        if QRCODE_AVAILABLE:
            # Generate QR code with ticket info
            qr_data = f"TICKET:{kwargs['ticket_number']}|PAX:{kwargs['passenger_name']}|{kwargs['source_airport']}-{kwargs['destination_airport']}|DATE:{kwargs['flight_date']}|SEAT:{kwargs['seat']}|GATE:{kwargs['gate']}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=1,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes for ReportLab
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Draw QR code on PDF
            qr_image = ImageReader(img_buffer)
            c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
        else:
            # Fallback placeholder if qrcode not available
            c.setStrokeColor(self.LIGHT_TEXT)
            c.setLineWidth(1)
            c.rect(qr_x, qr_y, qr_size, qr_size)
            c.setFillColor(self.LIGHT_TEXT)
            c.setFont("Helvetica", 6)
            c.drawCentredString(qr_x + 12.5*mm, qr_y + 10*mm, "SCAN HERE")
        
        c.save()
    
    def open_pdf(self, pdf_path: Path):
        """Open PDF in default viewer."""
        import subprocess
        import platform
        
        system = platform.system()
        try:
            if system == 'Linux':
                subprocess.Popen(['xdg-open', str(pdf_path)])
            elif system == 'Darwin':
                subprocess.Popen(['open', str(pdf_path)])
            elif system == 'Windows':
                subprocess.Popen(['start', '', str(pdf_path)], shell=True)
        except Exception as e:
            print(f"Could not open PDF: {e}")
    
    def print_pdf(self, pdf_path: Path):
        """Print PDF (Linux with lpr command)."""
        import subprocess
        try:
            subprocess.run(['lpr', str(pdf_path)], check=True)
            return True
        except Exception as e:
            print(f"Could not print PDF: {e}")
            return False


# Global boarding pass service instance
boarding_pass_service = BoardingPassService()
