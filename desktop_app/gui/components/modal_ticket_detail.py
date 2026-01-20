"""
Modal Ticket Detail - Integrated ticket information overlay.
Designed for the new Integrated Overlay system.
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict
from gui.theme import COLORS, FONTS, RADIUS, SPACING
from database.models import Ticket, TicketStatus

class ModalTicketDetail(ctk.CTkFrame):
    """Integrated Modal for displaying ticket details."""
    
    def __init__(
        self,
        parent,
        ticket: Ticket,
        passenger_name: str,
        passenger_passport: str,
        on_reset: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_print: Optional[Callable] = None,
        on_close: Optional[Callable] = None
    ):
        super().__init__(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['2xl'],
            border_width=2,
            border_color=COLORS['border'],
            width=900,
            height=850
        )
        self.pack_propagate(False)
        
        self.ticket = ticket
        self.on_reset = on_reset
        self.on_delete = on_delete
        self.on_print = on_print
        self.on_close = on_close
        
        self._setup_ui(passenger_name, passenger_passport)
        
    def _setup_ui(self, passenger_name: str, passenger_passport: str):
        """Setup the modal UI."""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Close button
        ctk.CTkButton(
            self,
            text="✕",
            width=50,
            height=50,
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_muted'],
            font=("Segoe UI", 24),
            command=self._handle_close
        ).place(relx=0.97, rely=0.03, anchor="ne")
        
        # Content
        ctk.CTkLabel(container, text="🎫 Ticket Details", font=FONTS['heading_large'], text_color=COLORS['text_primary']).pack(pady=(0, SPACING['sm']))
        ctk.CTkLabel(container, text=self.ticket.ticket_number, font=FONTS['subheading'], text_color=COLORS['accent']).pack()
        
        # Status
        status_color = {
            TicketStatus.BOOKED: COLORS['warning'],
            TicketStatus.CHECKED_IN: COLORS['success'],
            TicketStatus.CANCELLED: COLORS['error']
        }.get(self.ticket.status, COLORS['text_muted'])
        
        ctk.CTkLabel(container, text=f"● {self.ticket.status.value.upper().replace('_', ' ')}", font=FONTS['body'], text_color=status_color).pack(pady=(SPACING['xs'], SPACING['xl']))
        
        # Route
        route_frame = ctk.CTkFrame(container, fg_color=COLORS['bg_card'], corner_radius=RADIUS['xl'], border_width=1, border_color=COLORS['border'])
        route_frame.pack(fill="x", pady=SPACING['md'], padx=SPACING['xl'])
        
        route_content = ctk.CTkFrame(route_frame, fg_color="transparent")
        route_content.pack(padx=SPACING['3xl'], pady=SPACING['xl'])
        
        ctk.CTkLabel(route_content, text=f"{self.ticket.source_airport}  ➔  {self.ticket.destination_airport}", font=("Segoe UI", 48, "bold"), text_color=COLORS['text_primary']).pack()
        
        if self.ticket.source_airport_name:
            ctk.CTkLabel(route_content, text=f"{self.ticket.source_airport_name} to {self.ticket.destination_airport_name}", font=FONTS['body_large'], text_color=COLORS['text_secondary']).pack(pady=SPACING['sm'])
            
        # Details grid
        details_frame = ctk.CTkFrame(container, fg_color="transparent")
        details_frame.pack(fill="x", pady=SPACING['xl'])
        
        details = [
            ("Passenger", passenger_name),
            ("Passport", passenger_passport),
            ("Date", str(self.ticket.flight_date)),
            ("Time", self.ticket.flight_time.strftime("%H:%M") if self.ticket.flight_time else "TBD"),
            ("Seat", self.ticket.seat_number or "Not assigned"),
            ("Gate", self.ticket.gate or "Not assigned"),
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            frame.grid(row=row, column=col, sticky="w", padx=SPACING['xl'], pady=SPACING['sm'])
            
            ctk.CTkLabel(frame, text=label, font=FONTS['caption'], text_color=COLORS['text_muted']).pack(anchor="w")
            ctk.CTkLabel(frame, text=value, font=FONTS['body_large'], text_color=COLORS['text_primary']).pack(anchor="w")
        
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Actions
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(SPACING['xl'], 0))
        
        if self.ticket.status == TicketStatus.CHECKED_IN:
            ctk.CTkButton(btn_frame, text="🔄 Reset Status", font=FONTS['button'], fg_color=COLORS['warning'], hover_color="#cc8800", text_color=COLORS['bg_primary'], height=55, width=200, corner_radius=RADIUS['lg'], command=self.on_reset).pack(side="left", padx=SPACING['sm'])
            
        ctk.CTkButton(btn_frame, text="🖨️ Print Ticket", font=FONTS['button'], fg_color=COLORS['accent'], height=55, width=200, corner_radius=RADIUS['lg'], command=self.on_print).pack(side="left", padx=SPACING['sm'])
        
        ctk.CTkButton(btn_frame, text="🗑️ Delete Records", font=FONTS['button'], fg_color=COLORS['error'], height=55, width=200, corner_radius=RADIUS['lg'], command=self.on_delete).pack(side="right", padx=SPACING['sm'])

    def _handle_close(self):
        if self.on_close: self.on_close()
