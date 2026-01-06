"""
Audit Service - Logging for all kiosk actions.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import DATA_DIR


class AuditService:
    """Logs all significant actions for audit trail."""
    
    def __init__(self):
        """Initialize the audit logger."""
        self.log_file = DATA_DIR / "audit.log"
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup the audit logger."""
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)
            
            # Format: timestamp | action | details
            formatter = logging.Formatter(
                '%(asctime)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log(self, action: str, details: str = "", user: str = "system"):
        """Log an action."""
        message = f"{action.upper():15} | {user:15} | {details}"
        self.logger.info(message)
    
    def log_booking(self, ticket_number: str, passenger: str, route: str):
        """Log a new booking."""
        self.log(
            "BOOKING",
            f"Ticket: {ticket_number}, Passenger: {passenger}, Route: {route}",
            passenger
        )
    
    def log_checkin(self, ticket_number: str, passenger: str, success: bool):
        """Log a check-in attempt."""
        status = "SUCCESS" if success else "FAILED"
        self.log(
            f"CHECKIN_{status}",
            f"Ticket: {ticket_number}, Passenger: {passenger}",
            passenger
        )
    
    def log_reset(self, ticket_number: str, admin: str = "admin"):
        """Log a check-in reset."""
        self.log(
            "RESET_CHECKIN",
            f"Ticket: {ticket_number}",
            admin
        )
    
    def log_cancel(self, ticket_number: str, reason: str = "user_request"):
        """Log a ticket cancellation."""
        self.log(
            "CANCEL",
            f"Ticket: {ticket_number}, Reason: {reason}"
        )
    
    def log_print(self, ticket_number: str):
        """Log a boarding pass print."""
        self.log(
            "PRINT_PASS",
            f"Ticket: {ticket_number}"
        )
    
    def log_session_timeout(self):
        """Log a session timeout reset."""
        self.log(
            "SESSION_TIMEOUT",
            "Auto-reset to home due to inactivity"
        )
    
    def log_admin_access(self, action: str, success: bool):
        """Log an admin access attempt."""
        status = "GRANTED" if success else "DENIED"
        self.log(
            f"ADMIN_{status}",
            f"Action: {action}"
        )
    
    def log_delete(self, passenger_name: str, passport: str, admin: str = "admin"):
        """Log a passenger deletion."""
        self.log(
            "DELETE_PASSENGER",
            f"Passenger: {passenger_name}, Passport: {passport}",
            admin
        )
    
    def get_recent_logs(self, count: int = 50) -> list:
        """Get recent log entries."""
        if not self.log_file.exists():
            return []
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                return lines[-count:]
        except Exception:
            return []
    
    def get_today_stats(self) -> dict:
        """Get statistics for today."""
        today = datetime.now().strftime('%Y-%m-%d')
        stats = {
            'bookings': 0,
            'checkins': 0,
            'cancellations': 0,
            'resets': 0
        }
        
        if not self.log_file.exists():
            return stats
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if today in line:
                        if 'BOOKING' in line:
                            stats['bookings'] += 1
                        elif 'CHECKIN_SUCCESS' in line:
                            stats['checkins'] += 1
                        elif 'CANCEL' in line:
                            stats['cancellations'] += 1
                        elif 'RESET_CHECKIN' in line:
                            stats['resets'] += 1
        except Exception:
            pass
        
        return stats


# Global audit service instance
audit_service = AuditService()
