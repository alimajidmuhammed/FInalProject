"""
Print Service for Flight Kiosk System.
Handles printing to thermal printers and standard printers.
"""
import logging
import subprocess
import platform
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class PrinterType(Enum):
    """Types of supported printers."""
    STANDARD = "standard"
    THERMAL = "thermal"
    ESCPOS = "escpos"


class PrintService:
    """Service for printing boarding passes and receipts."""
    
    def __init__(self):
        """Initialize print service."""
        self._available_printers: List[str] = []
        self._default_printer: Optional[str] = None
        self._refresh_printers()
    
    def _refresh_printers(self):
        """Refresh list of available printers."""
        system = platform.system()
        
        try:
            if system == 'Linux':
                result = subprocess.run(
                    ['lpstat', '-p'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if 'printer' in line.lower():
                            parts = line.split()
                            if len(parts) >= 2:
                                self._available_printers.append(parts[1])
                
                # Get default printer
                result = subprocess.run(
                    ['lpstat', '-d'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and 'destination' in result.stdout:
                    parts = result.stdout.split(':')
                    if len(parts) >= 2:
                        self._default_printer = parts[1].strip()
                        
            elif system == 'Windows':
                # Use wmic on Windows
                result = subprocess.run(
                    ['wmic', 'printer', 'get', 'name'],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines()[1:]:
                        printer_name = line.strip()
                        if printer_name:
                            self._available_printers.append(printer_name)
                            
        except Exception as e:
            logger.error(f"Failed to enumerate printers: {e}")
    
    def get_available_printers(self) -> List[str]:
        """Get list of available printer names."""
        return self._available_printers.copy()
    
    def get_default_printer(self) -> Optional[str]:
        """Get the default printer name."""
        return self._default_printer
    
    def print_pdf(
        self,
        pdf_path: Path,
        printer_name: Optional[str] = None,
        copies: int = 1
    ) -> bool:
        """
        Print a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            printer_name: Printer name (or None for default)
            copies: Number of copies
            
        Returns:
            True if print job was submitted successfully
        """
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return False
        
        system = platform.system()
        
        try:
            if system == 'Linux':
                cmd = ['lpr']
                if printer_name:
                    cmd.extend(['-P', printer_name])
                cmd.extend(['-#', str(copies)])
                cmd.append(str(pdf_path))
                
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    logger.info(f"Print job submitted: {pdf_path.name}")
                    return True
                else:
                    logger.error(f"Print failed: {result.stderr.decode()}")
                    return False
                    
            elif system == 'Windows':
                # Use default Windows print command
                import os
                os.startfile(str(pdf_path), 'print')
                logger.info(f"Print dialog opened: {pdf_path.name}")
                return True
                
            elif system == 'Darwin':  # macOS
                cmd = ['lpr']
                if printer_name:
                    cmd.extend(['-P', printer_name])
                cmd.append(str(pdf_path))
                
                result = subprocess.run(cmd, capture_output=True)
                return result.returncode == 0
                
        except Exception as e:
            logger.error(f"Print error: {e}")
            return False
        
        return False
    
    def print_text(
        self,
        text: str,
        printer_name: Optional[str] = None
    ) -> bool:
        """
        Print plain text (useful for thermal printers).
        
        Args:
            text: Text to print
            printer_name: Printer name (or None for default)
            
        Returns:
            True if successful
        """
        system = platform.system()
        
        try:
            if system == 'Linux':
                cmd = ['lpr']
                if printer_name:
                    cmd.extend(['-P', printer_name])
                
                result = subprocess.run(
                    cmd,
                    input=text.encode(),
                    capture_output=True
                )
                return result.returncode == 0
                
        except Exception as e:
            logger.error(f"Text print error: {e}")
            return False
        
        return False
    
    def format_boarding_pass_text(
        self,
        ticket_number: str,
        passenger_name: str,
        source: str,
        destination: str,
        date: str,
        time: str,
        seat: str,
        gate: str
    ) -> str:
        """
        Format boarding pass for thermal printer.
        
        Returns:
            Formatted text string
        """
        width = 42  # Standard thermal printer width
        separator = "=" * width
        dash = "-" * width
        
        lines = [
            separator,
            "        ✈ BOARDING PASS".center(width),
            separator,
            "",
            f"PASSENGER: {passenger_name.upper()}",
            f"TICKET:    {ticket_number}",
            "",
            dash,
            f"FROM: {source}".ljust(20) + f"TO: {destination}".rjust(width - 20),
            dash,
            "",
            f"DATE: {date}".ljust(22) + f"TIME: {time}".rjust(width - 22),
            "",
            f"GATE: {gate}".ljust(22) + f"SEAT: {seat}".rjust(width - 22),
            "",
            separator,
            "Arrive 30 min before boarding".center(width),
            "Thank you for flying with us!".center(width),
            separator,
            "",
            ""
        ]
        
        return "\n".join(lines)
    
    def print_boarding_pass(
        self,
        ticket_number: str,
        passenger_name: str,
        source: str,
        destination: str,
        date: str,
        time: str,
        seat: str,
        gate: str,
        printer_name: Optional[str] = None
    ) -> bool:
        """
        Print a boarding pass as text to a thermal printer.
        
        Returns:
            True if successful
        """
        text = self.format_boarding_pass_text(
            ticket_number, passenger_name,
            source, destination,
            date, time, seat, gate
        )
        return self.print_text(text, printer_name)
    
    def is_available(self) -> bool:
        """Check if printing is available."""
        return len(self._available_printers) > 0
    
    def get_status(self) -> Dict:
        """Get printer status information."""
        return {
            'available': self.is_available(),
            'printers': self._available_printers,
            'default': self._default_printer,
            'platform': platform.system()
        }


# Global print service instance
print_service = PrintService()
