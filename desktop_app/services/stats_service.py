"""
Statistics Service for Flight Kiosk System.
Provides aggregated statistics and analytics.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


class StatsService:
    """Service for aggregating and providing statistics."""
    
    def __init__(self):
        """Initialize stats service."""
        self.log_file = Path(__file__).parent.parent.parent / 'data' / 'audit.log'
        self._cache: Dict = {}
        self._cache_time: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=5)
    
    def get_today_stats(self) -> Dict[str, int]:
        """Get statistics for today."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self._get_stats_for_date_range(today, today)
    
    def get_week_stats(self) -> Dict[str, int]:
        """Get statistics for this week."""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        return self._get_stats_for_date_range(
            week_start.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d')
        )
    
    def get_month_stats(self) -> Dict[str, int]:
        """Get statistics for this month."""
        today = datetime.now()
        month_start = today.replace(day=1)
        return self._get_stats_for_date_range(
            month_start.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d')
        )
    
    def get_all_time_stats(self) -> Dict[str, int]:
        """Get all-time statistics."""
        return self._get_stats_for_date_range('2020-01-01', '2099-12-31')
    
    def _get_stats_for_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, int]:
        """Get statistics for a date range."""
        stats = {
            'bookings': 0,
            'checkins': 0,
            'cancellations': 0,
            'resets': 0,
            'failed_checkins': 0
        }
        
        if not self.log_file.exists():
            return stats
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    # Check if line is within date range
                    if len(line) >= 10:
                        line_date = line[:10]
                        if start_date <= line_date <= end_date:
                            if 'BOOKING' in line and 'BOOKING_' not in line:
                                stats['bookings'] += 1
                            elif 'CHECKIN_SUCCESS' in line:
                                stats['checkins'] += 1
                            elif 'CHECKIN_FAILED' in line:
                                stats['failed_checkins'] += 1
                            elif 'CANCEL' in line:
                                stats['cancellations'] += 1
                            elif 'RESET_CHECKIN' in line:
                                stats['resets'] += 1
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
        
        return stats
    
    def get_hourly_distribution(self, days: int = 7) -> Dict[int, int]:
        """
        Get the distribution of activity by hour.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict mapping hour (0-23) to count
        """
        distribution = defaultdict(int)
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime('%Y-%m-%d')
        
        if not self.log_file.exists():
            return dict(distribution)
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if len(line) >= 19:
                        line_date = line[:10]
                        if line_date >= cutoff_str:
                            try:
                                hour = int(line[11:13])
                                if 'BOOKING' in line or 'CHECKIN_SUCCESS' in line:
                                    distribution[hour] += 1
                            except ValueError:
                                continue
        except Exception as e:
            logger.error(f"Failed to get hourly distribution: {e}")
        
        return dict(distribution)
    
    def get_popular_routes(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Get the most popular routes.
        
        Args:
            limit: Maximum number of routes to return
            
        Returns:
            List of (route, count) tuples
        """
        from database.db_manager import db
        
        routes = defaultdict(int)
        
        try:
            tickets = db.get_all_tickets()
            for ticket in tickets:
                route = f"{ticket.source_airport} → {ticket.destination_airport}"
                routes[route] += 1
        except Exception as e:
            logger.error(f"Failed to get popular routes: {e}")
        
        # Sort by count and return top N
        sorted_routes = sorted(routes.items(), key=lambda x: x[1], reverse=True)
        return sorted_routes[:limit]
    
    def get_daily_trend(self, days: int = 30) -> List[Dict]:
        """
        Get daily booking/checkin trends.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of dicts with date, bookings, checkins
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trend = []
        current = start_date
        
        while current <= end_date:
            date_str = current.strftime('%Y-%m-%d')
            stats = self._get_stats_for_date_range(date_str, date_str)
            trend.append({
                'date': date_str,
                'bookings': stats['bookings'],
                'checkins': stats['checkins'],
                'cancellations': stats['cancellations']
            })
            current += timedelta(days=1)
        
        return trend
    
    def get_summary(self) -> Dict:
        """Get a comprehensive summary of all statistics."""
        return {
            'today': self.get_today_stats(),
            'week': self.get_week_stats(),
            'month': self.get_month_stats(),
            'all_time': self.get_all_time_stats(),
            'hourly_distribution': self.get_hourly_distribution(),
            'popular_routes': self.get_popular_routes()
        }
    
    def export_report(self, format: str = 'csv') -> Optional[Path]:
        """
        Export statistics report.
        
        Args:
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file, or None on failure
        """
        import json as json_lib
        
        output_dir = Path(__file__).parent.parent.parent / 'data' / 'reports'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            summary = self.get_summary()
            
            if format == 'json':
                output_file = output_dir / f'stats_report_{timestamp}.json'
                with open(output_file, 'w') as f:
                    json_lib.dump(summary, f, indent=2)
            else:  # CSV
                output_file = output_dir / f'stats_report_{timestamp}.csv'
                with open(output_file, 'w') as f:
                    # Write header
                    f.write("Period,Bookings,Check-Ins,Cancellations,Resets,Failed Check-Ins\n")
                    
                    for period in ['today', 'week', 'month', 'all_time']:
                        stats = summary[period]
                        f.write(f"{period.title()},"
                               f"{stats['bookings']},"
                               f"{stats['checkins']},"
                               f"{stats['cancellations']},"
                               f"{stats['resets']},"
                               f"{stats['failed_checkins']}\n")
            
            logger.info(f"Exported stats report to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return None


# Global stats service instance
stats_service = StatsService()
