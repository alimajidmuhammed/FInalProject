"""
Dashboard View - Analytics and statistics for the Flight Kiosk.
Shows booking stats, check-in rates, and recent activity.
"""
from datetime import datetime, timedelta
from typing import Dict, List
import customtkinter as ctk

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from database.db_manager import db
from database.models import TicketStatus
from services.audit_service import audit_service


class DashboardView(ctk.CTkFrame):
    """
    Analytics dashboard showing kiosk statistics.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS['bg_primary'], **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dashboard interface."""
        # Main scroll container
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['lg'])
        
        # Header
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING['lg']))
        
        ctk.CTkLabel(
            header,
            text="📊 Dashboard",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Refresh button
        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            font=FONTS['body'],
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_primary'],
            height=35,
            width=100,
            command=self._refresh_stats
        ).pack(side="right")
        
        # Stats cards row
        self.stats_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.stats_row.pack(fill="x", pady=SPACING['md'])
        
        # Create stat cards
        self.stat_cards = {}
        stats = [
            ("total", "📋 Total Tickets", COLORS['accent']),
            ("booked", "🎫 Booked", COLORS['warning']),
            ("checked", "✅ Checked In", COLORS['success']),
            ("cancelled", "❌ Cancelled", COLORS['error']),
        ]
        
        for key, title, color in stats:
            card = self._create_stat_card(self.stats_row, title, "0", color)
            card.pack(side="left", fill="x", expand=True, padx=SPACING['xs'])
            self.stat_cards[key] = card
        
        # Today's activity section
        activity_header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        activity_header.pack(fill="x", pady=(SPACING['xl'], SPACING['md']))
        
        ctk.CTkLabel(
            activity_header,
            text="Today's Activity",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Today's date
        ctk.CTkLabel(
            activity_header,
            text=datetime.now().strftime("%B %d, %Y"),
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(side="right")
        
        # Today's stats row
        self.today_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.today_row.pack(fill="x", pady=SPACING['md'])
        
        self.today_cards = {}
        today_stats = [
            ("bookings", "🎫 Bookings", COLORS['accent']),
            ("checkins", "🛂 Check-Ins", COLORS['success']),
            ("cancellations", "❌ Cancellations", COLORS['error']),
            ("resets", "🔄 Resets", COLORS['warning']),
        ]
        
        for key, title, color in today_stats:
            card = self._create_stat_card(self.today_row, title, "0", color)
            card.pack(side="left", fill="x", expand=True, padx=SPACING['xs'])
            self.today_cards[key] = card
        
        # Quick stats
        quick_frame = ctk.CTkFrame(
            self.scroll,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['lg']
        )
        quick_frame.pack(fill="x", pady=SPACING['lg'])
        
        quick_content = ctk.CTkFrame(quick_frame, fg_color="transparent")
        quick_content.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])
        
        ctk.CTkLabel(
            quick_content,
            text="📈 Quick Stats",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        self.quick_stats_frame = ctk.CTkFrame(quick_content, fg_color="transparent")
        self.quick_stats_frame.pack(fill="x", pady=SPACING['md'])
        
        # Recent activity section
        recent_header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        recent_header.pack(fill="x", pady=(SPACING['lg'], SPACING['md']))
        
        ctk.CTkLabel(
            recent_header,
            text="📝 Recent Activity",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        self.recent_frame = ctk.CTkFrame(
            self.scroll,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['lg']
        )
        self.recent_frame.pack(fill="x")
    
    def _create_stat_card(self, parent, title: str, value: str, color: str):
        """Create a statistics card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['lg']
        )
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])
        
        # Value
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=FONTS['heading_large'],
            text_color=color
        )
        value_label.pack()
        
        # Title
        ctk.CTkLabel(
            content,
            text=title,
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Store reference to value label for updates
        card.value_label = value_label
        
        return card
    
    def _refresh_stats(self):
        """Refresh all statistics."""
        # Get all tickets
        tickets = db.get_all_tickets()
        
        # Overall stats
        total = len(tickets)
        booked = sum(1 for t in tickets if t.status == TicketStatus.BOOKED)
        checked = sum(1 for t in tickets if t.status == TicketStatus.CHECKED_IN)
        cancelled = sum(1 for t in tickets if t.status == TicketStatus.CANCELLED)
        
        self.stat_cards['total'].value_label.configure(text=str(total))
        self.stat_cards['booked'].value_label.configure(text=str(booked))
        self.stat_cards['checked'].value_label.configure(text=str(checked))
        self.stat_cards['cancelled'].value_label.configure(text=str(cancelled))
        
        # Today's stats from audit log
        today_stats = audit_service.get_today_stats()
        
        self.today_cards['bookings'].value_label.configure(text=str(today_stats.get('bookings', 0)))
        self.today_cards['checkins'].value_label.configure(text=str(today_stats.get('checkins', 0)))
        self.today_cards['cancellations'].value_label.configure(text=str(today_stats.get('cancellations', 0)))
        self.today_cards['resets'].value_label.configure(text=str(today_stats.get('resets', 0)))
        
        # Quick stats
        self._update_quick_stats(tickets)
        
        # Recent activity
        self._update_recent_activity()
    
    def _update_quick_stats(self, tickets):
        """Update quick statistics."""
        # Clear existing
        for widget in self.quick_stats_frame.winfo_children():
            widget.destroy()
        
        # Calculate metrics
        total = len(tickets)
        checked = sum(1 for t in tickets if t.status == TicketStatus.CHECKED_IN)
        check_rate = (checked / total * 100) if total > 0 else 0
        
        # Get most popular routes
        routes = {}
        for t in tickets:
            route = f"{t.source_airport} → {t.destination_airport}"
            routes[route] = routes.get(route, 0) + 1
        
        top_route = max(routes.items(), key=lambda x: x[1])[0] if routes else "N/A"
        
        # Display stats
        quick_stats = [
            ("Check-in Rate", f"{check_rate:.1f}%"),
            ("Most Popular Route", top_route),
            ("Total Passengers", str(len(db.get_all_passengers()))),
        ]
        
        for label, value in quick_stats:
            stat_frame = ctk.CTkFrame(self.quick_stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                stat_frame,
                text=label,
                font=FONTS['caption'],
                text_color=COLORS['text_muted']
            ).pack()
            
            ctk.CTkLabel(
                stat_frame,
                text=value,
                font=FONTS['body_large'],
                text_color=COLORS['text_primary']
            ).pack()
    
    def _update_recent_activity(self):
        """Update recent activity log."""
        # Clear existing
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
        
        content = ctk.CTkFrame(self.recent_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['md'])
        
        # Get recent logs
        logs = audit_service.get_recent_logs(10)
        
        if not logs:
            ctk.CTkLabel(
                content,
                text="No recent activity",
                font=FONTS['body'],
                text_color=COLORS['text_muted']
            ).pack(pady=SPACING['lg'])
            return
        
        # Show logs in reverse (newest first)
        for log in reversed(logs):
            log = log.strip()
            if not log:
                continue
            
            log_frame = ctk.CTkFrame(content, fg_color="transparent")
            log_frame.pack(fill="x", pady=SPACING['xs'])
            
            # Parse log entry
            parts = log.split(" | ")
            if len(parts) >= 2:
                timestamp = parts[0]
                action = parts[1] if len(parts) > 1 else ""
                details = parts[2] if len(parts) > 2 else ""
                
                # Timestamp
                ctk.CTkLabel(
                    log_frame,
                    text=timestamp,
                    font=FONTS['caption'],
                    text_color=COLORS['text_muted'],
                    width=150
                ).pack(side="left")
                
                # Action
                action_color = COLORS['text_primary']
                if 'SUCCESS' in action or 'BOOKING' in action:
                    action_color = COLORS['success']
                elif 'FAILED' in action or 'CANCEL' in action:
                    action_color = COLORS['error']
                elif 'RESET' in action:
                    action_color = COLORS['warning']
                
                ctk.CTkLabel(
                    log_frame,
                    text=action.strip(),
                    font=FONTS['body_small'],
                    text_color=action_color,
                    width=120
                ).pack(side="left")
                
                # Details
                ctk.CTkLabel(
                    log_frame,
                    text=details.strip()[:50],
                    font=FONTS['body_small'],
                    text_color=COLORS['text_secondary']
                ).pack(side="left", padx=SPACING['sm'])
    
    def on_show(self):
        """Called when view is shown."""
        self._refresh_stats()
    
    def on_hide(self):
        """Called when view is hidden."""
        pass
