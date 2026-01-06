"""
Ticket Card - Displays ticket information in a card format.
"""
from typing import Callable, Optional
import customtkinter as ctk

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from database.models import Ticket, TicketStatus


class TicketCard(ctk.CTkFrame):
    """
    A card component displaying ticket information.
    """
    
    STATUS_COLORS = {
        TicketStatus.BOOKED: COLORS['warning'],
        TicketStatus.CHECKED_IN: COLORS['success'],
        TicketStatus.CANCELLED: COLORS['error'],
    }
    
    def __init__(
        self,
        parent,
        ticket: Ticket,
        passenger_name: str = "",
        on_click: Optional[Callable] = None,
        on_checkin: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        show_actions: bool = True,
        **kwargs
    ):
        super().__init__(
            parent, 
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['lg'],
            **kwargs
        )
        
        self.ticket = ticket
        self.passenger_name = passenger_name
        self.on_click = on_click
        self.on_checkin = on_checkin
        self.on_cancel = on_cancel
        self.show_actions = show_actions
        
        self._setup_ui()
        
        # Make the whole card clickable (including all children)
        if on_click:
            self._bind_click_recursive(self, lambda e: on_click(ticket))
            self.configure(cursor="hand2")
    
    def _bind_click_recursive(self, widget, callback):
        """Recursively bind click event to widget and all its children."""
        widget.bind("<Button-1>", callback)
        try:
            widget.configure(cursor="hand2")
        except:
            pass  # Some widgets don't support cursor configuration
        
        # Bind to all children
        for child in widget.winfo_children():
            # Don't bind to buttons (they have their own actions)
            if not isinstance(child, ctk.CTkButton):
                self._bind_click_recursive(child, callback)
    
    def _setup_ui(self):
        """Setup the card UI."""
        # Main container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])
        
        # Header row (ticket number + status)
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING['sm']))
        
        # Ticket number
        ctk.CTkLabel(
            header,
            text=self.ticket.ticket_number,
            font=FONTS['subheading'],
            text_color=COLORS['accent']
        ).pack(side="left")
        
        # Status badge
        status_color = self.STATUS_COLORS.get(self.ticket.status, COLORS['text_muted'])
        status_text = self.ticket.status.value.upper().replace('_', ' ')
        
        ctk.CTkLabel(
            header,
            text=f"● {status_text}",
            font=FONTS['caption'],
            text_color=status_color
        ).pack(side="right")
        
        # Route row
        route_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        route_frame.pack(fill="x", pady=SPACING['sm'])
        
        # From
        from_frame = ctk.CTkFrame(route_frame, fg_color="transparent")
        from_frame.pack(side="left", expand=True, anchor="w")
        
        ctk.CTkLabel(
            from_frame,
            text="FROM",
            font=FONTS['caption'],
            text_color=COLORS['text_muted']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            from_frame,
            text=self.ticket.source_airport,
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        # Arrow
        ctk.CTkLabel(
            route_frame,
            text="→",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS['accent']
        ).pack(side="left", padx=SPACING['md'])
        
        # To
        to_frame = ctk.CTkFrame(route_frame, fg_color="transparent")
        to_frame.pack(side="left", expand=True, anchor="w")
        
        ctk.CTkLabel(
            to_frame,
            text="TO",
            font=FONTS['caption'],
            text_color=COLORS['text_muted']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            to_frame,
            text=self.ticket.destination_airport,
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        # Date and time row
        info_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        info_frame.pack(fill="x", pady=SPACING['sm'])
        
        # Date
        self._add_info_item(info_frame, "DATE", str(self.ticket.flight_date))
        
        # Time
        time_str = self.ticket.flight_time.strftime("%H:%M") if self.ticket.flight_time else "TBD"
        self._add_info_item(info_frame, "TIME", time_str)
        
        # Seat (if checked in)
        if self.ticket.seat_number:
            self._add_info_item(info_frame, "SEAT", self.ticket.seat_number, highlight=True)
        
        # Gate (if checked in)
        if self.ticket.gate:
            self._add_info_item(info_frame, "GATE", self.ticket.gate, highlight=True)
        
        # Passenger name
        if self.passenger_name:
            ctk.CTkLabel(
                self.content,
                text=f"Passenger: {self.passenger_name}",
                font=FONTS['body_small'],
                text_color=COLORS['text_secondary']
            ).pack(anchor="w", pady=(SPACING['sm'], 0))
        
        # Action buttons
        if self.show_actions and self.ticket.status == TicketStatus.BOOKED:
            actions = ctk.CTkFrame(self.content, fg_color="transparent")
            actions.pack(fill="x", pady=(SPACING['md'], 0))
            
            if self.on_cancel:
                ctk.CTkButton(
                    actions,
                    text="Cancel",
                    font=FONTS['body_small'],
                    fg_color="transparent",
                    hover_color=COLORS['bg_hover'],
                    border_width=1,
                    border_color=COLORS['error'],
                    text_color=COLORS['error'],
                    height=32,
                    command=lambda: self.on_cancel(self.ticket)
                ).pack(side="right", padx=SPACING['xs'])
    
    def _add_info_item(self, parent, label: str, value: str, highlight: bool = False):
        """Add an info item to the row."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=(0, SPACING['lg']))
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=FONTS['caption'],
            text_color=COLORS['text_muted']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            frame,
            text=value,
            font=FONTS['body'] if not highlight else FONTS['subheading'],
            text_color=COLORS['text_primary'] if not highlight else COLORS['accent']
        ).pack(anchor="w")
