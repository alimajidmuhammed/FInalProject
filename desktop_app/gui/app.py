"""
Main Application Window - Flight Kiosk System.
Modern dark-themed interface with sidebar navigation.
Features: Theme toggle, session timeout, keyboard shortcuts.
"""
import customtkinter as ctk

from gui.theme import COLORS, FONTS, RADIUS, SPACING, apply_theme, toggle_theme, get_theme_mode, set_theme_mode
from gui.booking_view import BookingView
from gui.checkin_view import CheckInView
from gui.history_view import HistoryView
from gui.dashboard_view import DashboardView
from config import SESSION_TIMEOUT_SECONDS
from services.audit_service import audit_service


class App(ctk.CTk):
    """
    Main application window with sidebar navigation.
    """
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("✈ Flight Kiosk System")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Apply theme
        apply_theme(ctk)
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Current view tracking
        self.current_view = None
        self.views = {}
        
        # Session timeout tracking
        self._last_activity = 0
        self._timeout_warning_shown = False
        self._timeout_job = None
        
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        self._start_activity_tracking()
        self._show_view("booking")
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_secondary'],
            corner_radius=0,
            width=250
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Sidebar content
        self._setup_sidebar()
        
        # Main content area
        self.content = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )
        self.content.pack(side="right", fill="both", expand=True)
        
        # Initialize views
        self.views["booking"] = BookingView(self.content, on_booking_complete=self._on_booking_complete)
        self.views["checkin"] = CheckInView(self.content)
        self.views["history"] = HistoryView(self.content)
        self.views["dashboard"] = DashboardView(self.content)
    
    def _setup_sidebar(self):
        """Setup the sidebar navigation."""
        # Logo/Header area
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xl'])
        
        # App title
        ctk.CTkLabel(
            logo_frame,
            text="✈",
            font=("Segoe UI", 48),
            text_color=COLORS['accent']
        ).pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="Flight Kiosk",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        ).pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="Self-Service Terminal",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Divider
        ctk.CTkFrame(
            self.sidebar,
            fg_color=COLORS['border'],
            height=1
        ).pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=SPACING['md'])
        
        self.nav_buttons = {}
        
        nav_items = [
            ("booking", "🎫", "Book Flight", "F1"),
            ("checkin", "🛂", "Check-In", "F2"),
            ("history", "📋", "History", "F3"),
            ("dashboard", "📊", "Dashboard", "F4"),
        ]
        
        for key, icon, title, shortcut in nav_items:
            btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=SPACING['xs'])
            
            btn = ctk.CTkButton(
                btn_frame,
                text=f"{icon}  {title}",
                font=FONTS['button'],
                fg_color="transparent",
                hover_color=COLORS['bg_hover'],
                text_color=COLORS['text_primary'],
                anchor="w",
                height=50,
                corner_radius=RADIUS['md'],
                command=lambda k=key: self._show_view(k)
            )
            btn.pack(fill="x")
            
            # Shortcut label
            ctk.CTkLabel(
                btn_frame,
                text=shortcut,
                font=FONTS['caption'],
                text_color=COLORS['text_muted']
            ).place(relx=0.9, rely=0.5, anchor="center")
            
            self.nav_buttons[key] = btn
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=SPACING['lg'], pady=SPACING['lg'])
        
        # ESP Status
        self.esp_status_frame = ctk.CTkFrame(
            bottom_frame,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['md']
        )
        self.esp_status_frame.pack(fill="x", pady=SPACING['sm'])
        
        status_content = ctk.CTkFrame(self.esp_status_frame, fg_color="transparent")
        status_content.pack(padx=SPACING['md'], pady=SPACING['sm'])
        
        ctk.CTkLabel(
            status_content,
            text="ESP32 Status",
            font=FONTS['caption'],
            text_color=COLORS['text_muted']
        ).pack(anchor="w")
        
        self.esp_status_label = ctk.CTkLabel(
            status_content,
            text="● Not Connected",
            font=FONTS['body_small'],
            text_color=COLORS['error']
        )
        self.esp_status_label.pack(anchor="w")
        
        # Version
        ctk.CTkLabel(
            bottom_frame,
            text="v1.0.0 | Esc = Home",
            font=FONTS['caption'],
            text_color=COLORS['text_muted']
        ).pack(pady=SPACING['sm'])
    
    def _setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts."""
        self.bind('<Escape>', lambda e: self._show_view("booking"))
        self.bind('<F1>', lambda e: self._show_view("booking"))
        self.bind('<F2>', lambda e: self._show_view("checkin"))
        self.bind('<F3>', lambda e: self._show_view("history"))
        self.bind('<F4>', lambda e: self._show_view("dashboard"))
    
    def _start_activity_tracking(self):
        """Start tracking user activity for session timeout."""
        import time
        self._last_activity = time.time()
        
        # Bind activity events
        self.bind('<Motion>', self._on_activity)
        self.bind('<Button>', self._on_activity)
        self.bind('<Key>', self._on_activity)
        
        # Start timeout check
        self._check_timeout()
    
    def _on_activity(self, event=None):
        """Reset activity timer on user interaction."""
        import time
        self._last_activity = time.time()
        self._timeout_warning_shown = False
    
    def _check_timeout(self):
        """Check for session timeout."""
        import time
        
        idle_time = time.time() - self._last_activity
        
        # Warning at 30 seconds before timeout
        if idle_time >= SESSION_TIMEOUT_SECONDS - 30 and not self._timeout_warning_shown:
            self._timeout_warning_shown = True
            self._show_timeout_warning()
        
        # Timeout reached
        if idle_time >= SESSION_TIMEOUT_SECONDS:
            self._on_session_timeout()
        
        # Schedule next check
        self._timeout_job = self.after(5000, self._check_timeout)
    
    def _show_timeout_warning(self):
        """Show a warning that session will timeout soon."""
        # Could show a popup or notification
        pass
    
    def _on_session_timeout(self):
        """Handle session timeout."""
        import time
        self._last_activity = time.time()
        
        # Log the timeout
        audit_service.log_session_timeout()
        
        # Reset to home view
        if self.current_view != "booking":
            self._show_view("booking")
    
    def _toggle_theme(self):
        """Toggle between dark and light theme."""
        new_mode = toggle_theme()
        
        # Update icon
        if new_mode == "light":
            self.theme_icon.configure(text="☀️")
        else:
            self.theme_icon.configure(text="🌙")
        
        # Apply theme to CTk - CTk handles most color changes automatically
        ctk.set_appearance_mode(new_mode)
    
    def _refresh_colors(self):
        """Refresh all UI colors after theme change."""
        # CTk handles most theming automatically when using set_appearance_mode
        # Only need to update custom-colored elements
        pass
    
    def _show_view(self, view_key: str):
        """Switch to the specified view."""
        # Reset activity timer
        self._on_activity()
        
        # Hide current view
        if self.current_view:
            current = self.views.get(self.current_view)
            if current:
                current.pack_forget()
                if hasattr(current, 'on_hide'):
                    current.on_hide()
        
        # Update nav button styles
        for key, btn in self.nav_buttons.items():
            if key == view_key:
                btn.configure(fg_color=COLORS['accent'])
            else:
                btn.configure(fg_color="transparent")
        
        # Show new view
        view = self.views.get(view_key)
        if view:
            view.pack(fill="both", expand=True)
            if hasattr(view, 'on_show'):
                view.on_show()
        
        self.current_view = view_key
    
    def _on_booking_complete(self, ticket):
        """Handle booking completion."""
        # Could auto-switch to check-in or show notification
        pass
    
    def update_esp_status(self, connected: bool, message: str = ""):
        """Update ESP32 connection status display."""
        if connected:
            self.esp_status_label.configure(
                text=f"● Connected {message}",
                text_color=COLORS['success']
            )
        else:
            self.esp_status_label.configure(
                text="● Not Connected",
                text_color=COLORS['error']
            )
    
    def on_closing(self):
        """Handle window close."""
        # Cancel timeout job
        if self._timeout_job:
            self.after_cancel(self._timeout_job)
        
        # Stop camera and other services
        for view in self.views.values():
            if hasattr(view, 'on_hide'):
                view.on_hide()
        
        self.destroy()


def create_app() -> App:
    """Create and return the application instance."""
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    return app
