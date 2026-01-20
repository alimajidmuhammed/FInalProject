"""
Enhanced Logger Service for Flight Kiosk System.
Provides centralized logging with rotation and color output.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Add color to levelname
        record.levelname = f"{color}{record.levelname:8}{reset}"
        return super().format(record)


class LoggerService:
    """Centralized logging service with file rotation."""
    
    def __init__(self):
        """Initialize the logger service."""
        self.log_dir = Path(__file__).parent.parent.parent / 'data' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self._loggers = {}
        self._root_configured = False
        
        # Configure root logger
        self._configure_root_logger()
    
    def _configure_root_logger(self):
        """Configure the root logger with handlers."""
        if self._root_configured:
            return
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = ColorFormatter(
            '%(asctime)s │ %(levelname)s │ %(name)-20s │ %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = self.log_dir / 'kiosk.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
        
        # Error-only file handler
        error_file = self.log_dir / 'errors.log'
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        root_logger.addHandler(error_handler)
        
        self._root_configured = True
        logging.info("Logger service initialized")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a named logger."""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def get_recent_logs(
        self,
        count: int = 100,
        level: Optional[str] = None,
        search: Optional[str] = None
    ) -> list:
        """
        Get recent log entries.
        
        Args:
            count: Maximum number of entries to return
            level: Filter by log level (DEBUG, INFO, WARNING, ERROR)
            search: Search string to filter entries
            
        Returns:
            List of log entry dicts
        """
        log_file = self.log_dir / 'kiosk.log'
        entries = []
        
        if not log_file.exists():
            return entries
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Process lines in reverse (newest first)
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Parse log entry
                try:
                    parts = line.split(' | ', 3)
                    if len(parts) >= 4:
                        entry = {
                            'timestamp': parts[0],
                            'level': parts[1].strip(),
                            'module': parts[2].strip(),
                            'message': parts[3]
                        }
                        
                        # Apply filters
                        if level and entry['level'] != level:
                            continue
                        if search and search.lower() not in line.lower():
                            continue
                        
                        entries.append(entry)
                        
                        if len(entries) >= count:
                            break
                except Exception:
                    continue
                    
        except Exception as e:
            logging.error(f"Failed to read logs: {e}")
        
        return entries
    
    def get_error_logs(self, count: int = 50) -> list:
        """Get recent error logs."""
        return self.get_recent_logs(count=count, level='ERROR')
    
    def clear_old_logs(self, days: int = 30) -> int:
        """
        Clear log files older than specified days.
        
        Returns:
            Number of files deleted
        """
        import os
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        
        try:
            for log_file in self.log_dir.glob('*.log.*'):
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                if mtime < cutoff:
                    log_file.unlink()
                    deleted += 1
                    logging.info(f"Deleted old log file: {log_file.name}")
        except Exception as e:
            logging.error(f"Failed to clear old logs: {e}")
        
        return deleted
    
    def get_log_stats(self) -> dict:
        """Get statistics about log files."""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'error_count': 0,
            'warning_count': 0
        }
        
        try:
            for log_file in self.log_dir.glob('*.log*'):
                stats['total_files'] += 1
                stats['total_size_mb'] += log_file.stat().st_size / (1024 * 1024)
            
            # Count errors and warnings in main log
            main_log = self.log_dir / 'kiosk.log'
            if main_log.exists():
                with open(main_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '| ERROR' in line:
                            stats['error_count'] += 1
                        elif '| WARNING' in line:
                            stats['warning_count'] += 1
        except Exception as e:
            logging.error(f"Failed to get log stats: {e}")
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats


# Global logger service instance
logger_service = LoggerService()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger."""
    return logger_service.get_logger(name)
