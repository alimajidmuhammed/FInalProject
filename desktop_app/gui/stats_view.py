"""
Statistics Dashboard View for Flight Kiosk System.
Displays charts and metrics for admin users.
"""
import customtkinter as ctk
from typing import Optional, Callable
import logging

from gui.theme import COLORS, FONTS, SPACING, RADIUS
from services.stats_service import stats_service
from services.i18n_service import i18n, t

logger = logging.getLogger(__name__)


class StatsView(ctk.CTkFrame):
    """Statistics dashboard with charts and metrics."""
    
    def __init__(self, parent, show_overlay_callback: Optional[Callable] = None):
        """Initialize stats view."""
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        
        self.show_overlay = show_overlay_callback
        self._setup_ui()
        
        # Listen for language changes
        i18n.add_listener(self._on_language_change)
    
    def _setup_ui(self):
        """Setup the UI layout."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self._create_header()
        
        # Main content
        self._create_content()
    
    def _create_header(self):
        """Create the header section."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=SPACING['xl'], pady=SPACING['lg'])
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=t('stats.title'),
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 " + t('app.retry'),
            font=FONTS['body'],
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_primary'],
            corner_radius=RADIUS['md'],
            width=120,
            command=self.refresh_stats
        )
        refresh_btn.grid(row=0, column=1, padx=SPACING['sm'])
        
        # Export button
        export_btn = ctk.CTkButton(
            header_frame,
            text="📊 " + t('stats.exportReport'),
            font=FONTS['body'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            text_color=COLORS['bg_primary'],
            corner_radius=RADIUS['md'],
            width=150,
            command=self._export_report
        )
        export_btn.grid(row=0, column=2)
    
    def _create_content(self):
        """Create the main content area."""
        # Scrollable container
        self.content_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.content_scroll.grid(row=1, column=0, sticky="nsew", padx=SPACING['lg'], pady=SPACING['sm'])
        self.content_scroll.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stats cards row
        self._create_stats_cards()
        
        # Charts row
        self._create_charts_section()
        
        # Popular routes and system health
        self._create_details_section()
    
    def _create_stats_cards(self):
        """Create the statistics card widgets."""
        stats = stats_service.get_today_stats()
        
        cards_data = [
            {
                'title': t('stats.totalBookings'),
                'value': str(stats.get('bookings', 0)),
                'icon': '📦',
                'color': COLORS['accent']
            },
            {
                'title': t('stats.totalCheckIns'),
                'value': str(stats.get('checkins', 0)),
                'icon': '✅',
                'color': COLORS['success']
            },
            {
                'title': t('stats.totalCancellations'),
                'value': str(stats.get('cancellations', 0)),
                'icon': '❌',
                'color': COLORS['error']
            },
            {
                'title': 'Resets',
                'value': str(stats.get('resets', 0)),
                'icon': '🔄',
                'color': COLORS['warning']
            }
        ]
        
        self.stat_cards = []
        for i, card_data in enumerate(cards_data):
            card = self._create_stat_card(
                self.content_scroll,
                card_data['title'],
                card_data['value'],
                card_data['icon'],
                card_data['color']
            )
            card.grid(row=0, column=i, padx=SPACING['sm'], pady=SPACING['md'], sticky="nsew")
            self.stat_cards.append(card)
    
    def _create_stat_card(
        self,
        parent,
        title: str,
        value: str,
        icon: str,
        accent_color: str
    ) -> ctk.CTkFrame:
        """Create a single stat card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['lg'],
            border_width=1,
            border_color=COLORS['border']
        )
        card.grid_columnconfigure(0, weight=1)
        
        # Icon and value row
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['sm']))
        
        icon_label = ctk.CTkLabel(
            top_frame,
            text=icon,
            font=('Segoe UI', 32)
        )
        icon_label.pack(side="left")
        
        value_label = ctk.CTkLabel(
            top_frame,
            text=value,
            font=('Segoe UI Display', 36, 'bold'),
            text_color=accent_color
        )
        value_label.pack(side="right")
        
        # Store reference for updates
        card.value_label = value_label
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        title_label.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Store reference
        card.title_label = title_label
        
        return card
    
    def _create_charts_section(self):
        """Create the charts section."""
        # Period selector frame
        period_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        period_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=SPACING['lg'])
        
        self.period_label = ctk.CTkLabel(
            period_frame,
            text="📈 Period Statistics",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        )
        self.period_label.pack(side="left")
        
        # Period buttons
        periods = [
            ('today', t('stats.today')),
            ('week', t('stats.thisWeek')),
            ('month', t('stats.thisMonth')),
            ('all', t('stats.allTime'))
        ]
        
        self.period_buttons = {}
        for period_key, period_text in reversed(periods):
            btn = ctk.CTkButton(
                period_frame,
                text=period_text,
                font=FONTS['body_small'],
                fg_color=COLORS['bg_card'] if period_key != 'today' else COLORS['accent'],
                hover_color=COLORS['accent_hover'],
                text_color=COLORS['text_primary'] if period_key != 'today' else COLORS['bg_primary'],
                corner_radius=RADIUS['sm'],
                width=100,
                height=32,
                command=lambda p=period_key: self._select_period(p)
            )
            btn.pack(side="right", padx=SPACING['xs'])
            self.period_buttons[period_key] = btn
        
        self.selected_period = 'today'
        
        # Stats table
        self._create_stats_table()
    
    def _create_stats_table(self):
        """Create a stats comparison table."""
        self.table_frame = ctk.CTkFrame(
            self.content_scroll,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['lg'],
            border_width=1,
            border_color=COLORS['border']
        )
        self.table_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=SPACING['sm'])
        self.table_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Get all stats
        today_stats = stats_service.get_today_stats()
        week_stats = stats_service.get_week_stats()
        month_stats = stats_service.get_month_stats()
        all_stats = stats_service.get_all_time_stats()
        
        # Header row
        headers = ['Metric', t('stats.today'), t('stats.thisWeek'), t('stats.thisMonth'), t('stats.allTime')]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=FONTS['body'] if i == 0 else FONTS['body_small'],
                text_color=COLORS['text_secondary'] if i > 0 else COLORS['text_primary']
            )
            label.grid(row=0, column=i, padx=SPACING['md'], pady=SPACING['md'], sticky="w" if i == 0 else "")
        
        # Data rows
        metrics = [
            ('Bookings', 'bookings', COLORS['accent']),
            ('Check-Ins', 'checkins', COLORS['success']),
            ('Cancellations', 'cancellations', COLORS['error']),
            ('Resets', 'resets', COLORS['warning']),
        ]
        
        for row_idx, (metric_name, metric_key, color) in enumerate(metrics, start=1):
            # Metric name
            name_label = ctk.CTkLabel(
                self.table_frame,
                text=f"  {metric_name}",
                font=FONTS['body'],
                text_color=color
            )
            name_label.grid(row=row_idx, column=0, padx=SPACING['md'], pady=SPACING['sm'], sticky="w")
            
            # Values
            values = [
                today_stats.get(metric_key, 0),
                week_stats.get(metric_key, 0),
                month_stats.get(metric_key, 0),
                all_stats.get(metric_key, 0)
            ]
            
            for col_idx, value in enumerate(values, start=1):
                value_label = ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    font=FONTS['body'],
                    text_color=COLORS['text_primary']
                )
                value_label.grid(row=row_idx, column=col_idx, padx=SPACING['md'], pady=SPACING['sm'])
    
    def _create_details_section(self):
        """Create the details section with routes and system info."""
        # Popular routes
        routes_frame = ctk.CTkFrame(
            self.content_scroll,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['lg'],
            border_width=1,
            border_color=COLORS['border']
        )
        routes_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=SPACING['xs'], pady=SPACING['lg'])
        
        routes_title = ctk.CTkLabel(
            routes_frame,
            text=f"🛫 {t('stats.popularRoutes')}",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        )
        routes_title.pack(anchor="w", padx=SPACING['lg'], pady=SPACING['md'])
        
        popular_routes = stats_service.get_popular_routes(5)
        if popular_routes:
            for route, count in popular_routes:
                route_row = ctk.CTkFrame(routes_frame, fg_color="transparent")
                route_row.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
                
                route_label = ctk.CTkLabel(
                    route_row,
                    text=route,
                    font=FONTS['body'],
                    text_color=COLORS['text_primary']
                )
                route_label.pack(side="left")
                
                count_label = ctk.CTkLabel(
                    route_row,
                    text=str(count),
                    font=FONTS['body'],
                    text_color=COLORS['accent']
                )
                count_label.pack(side="right")
        else:
            no_data = ctk.CTkLabel(
                routes_frame,
                text="No route data available",
                font=FONTS['body'],
                text_color=COLORS['text_secondary']
            )
            no_data.pack(padx=SPACING['lg'], pady=SPACING['md'])
        
        # Add bottom padding
        ctk.CTkFrame(routes_frame, fg_color="transparent", height=SPACING['md']).pack()
        
        # System health
        health_frame = ctk.CTkFrame(
            self.content_scroll,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['lg'],
            border_width=1,
            border_color=COLORS['border']
        )
        health_frame.grid(row=3, column=2, columnspan=2, sticky="nsew", padx=SPACING['xs'], pady=SPACING['lg'])
        
        health_title = ctk.CTkLabel(
            health_frame,
            text=f"💚 {t('stats.systemHealth')}",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        )
        health_title.pack(anchor="w", padx=SPACING['lg'], pady=SPACING['md'])
        
        # ESP32 status
        from services.esp_service import esp_service
        esp_connected = esp_service.is_connected()
        
        esp_row = ctk.CTkFrame(health_frame, fg_color="transparent")
        esp_row.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
        
        esp_label = ctk.CTkLabel(
            esp_row,
            text=t('stats.espStatus'),
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        esp_label.pack(side="left")
        
        esp_status = ctk.CTkLabel(
            esp_row,
            text=f"{'🟢 ' + t('stats.connected') if esp_connected else '🔴 ' + t('stats.disconnected')}",
            font=FONTS['body'],
            text_color=COLORS['success'] if esp_connected else COLORS['error']
        )
        esp_status.pack(side="right")
        
        # Database info
        try:
            from database.db_manager import db
            ticket_count = len(db.get_all_tickets())
            passenger_count = len(db.get_all_passengers())
        except Exception:
            ticket_count = passenger_count = 0
        
        db_row = ctk.CTkFrame(health_frame, fg_color="transparent")
        db_row.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
        
        db_label = ctk.CTkLabel(
            db_row,
            text="Database Records",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        db_label.pack(side="left")
        
        db_status = ctk.CTkLabel(
            db_row,
            text=f"{ticket_count} tickets, {passenger_count} passengers",
            font=FONTS['body'],
            text_color=COLORS['accent']
        )
        db_status.pack(side="right")
        
        # Log stats
        from services.logger_service import logger_service
        log_stats = logger_service.get_log_stats()
        
        log_row = ctk.CTkFrame(health_frame, fg_color="transparent")
        log_row.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
        
        log_label = ctk.CTkLabel(
            log_row,
            text="Log Files",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        log_label.pack(side="left")
        
        log_status = ctk.CTkLabel(
            log_row,
            text=f"{log_stats.get('total_files', 0)} files ({log_stats.get('total_size_mb', 0)} MB)",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        log_status.pack(side="right")
        
        # Add bottom padding
        ctk.CTkFrame(health_frame, fg_color="transparent", height=SPACING['md']).pack()
    
    def _select_period(self, period: str):
        """Handle period selection."""
        self.selected_period = period
        
        # Update button colors
        for key, btn in self.period_buttons.items():
            if key == period:
                btn.configure(
                    fg_color=COLORS['accent'],
                    text_color=COLORS['bg_primary']
                )
            else:
                btn.configure(
                    fg_color=COLORS['bg_card'],
                    text_color=COLORS['text_primary']
                )
        
        # Get stats for selected period
        if period == 'today':
            stats = stats_service.get_today_stats()
        elif period == 'week':
            stats = stats_service.get_week_stats()
        elif period == 'month':
            stats = stats_service.get_month_stats()
        else:
            stats = stats_service.get_all_time_stats()
        
        # Update cards
        card_keys = ['bookings', 'checkins', 'cancellations', 'resets']
        for i, key in enumerate(card_keys):
            if i < len(self.stat_cards):
                self.stat_cards[i].value_label.configure(text=str(stats.get(key, 0)))
    
    def refresh_stats(self):
        """Refresh all statistics."""
        self._select_period(self.selected_period)
        
        # Rebuild the table
        self.table_frame.destroy()
        self._create_stats_table()
        
        logger.info("Statistics refreshed")
    
    def _export_report(self):
        """Export statistics report."""
        report_path = stats_service.export_report('csv')
        
        if report_path:
            logger.info(f"Report exported to {report_path}")
            # Could show a success message here
        else:
            logger.error("Failed to export report")
    
    def _on_language_change(self, lang_code: str):
        """Handle language change."""
        self.title_label.configure(text=t('stats.title'))
        # Could refresh more labels here
    
    def destroy(self):
        """Cleanup when destroyed."""
        i18n.remove_listener(self._on_language_change)
        super().destroy()
