"""
History View - Ticket management and history.
Shows all tickets with filtering and management options.
"""
from typing import Optional, List
import customtkinter as ctk

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from gui.components.ticket_card import TicketCard
from gui.components.admin_modal import AdminPinModal
from gui.components.modal_confirm import ModalConfirm
from gui.components.modal_ticket_detail import ModalTicketDetail
from database.db_manager import db
from database.models import Ticket, TicketStatus
from services.audit_service import audit_service
from services.boarding_pass_service import boarding_pass_service


class HistoryView(ctk.CTkFrame):
    """
    Ticket history and management view.
    Displays all tickets with filtering and action capabilities.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS['bg_primary'], **kwargs)
        
        self.tickets: List[Ticket] = []
        self.current_filter = "all"
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the history interface."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['xl'], pady=SPACING['lg'])
        
        ctk.CTkLabel(
            header,
            text="📋 Ticket History",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="View and manage all tickets",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(SPACING['xs'], 0))
        
        # Filter tabs
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=SPACING['xl'], pady=(0, SPACING['md']))
        
        self.filter_buttons = {}
        filters = [
            ("all", "All Tickets"),
            ("booked", "Booked"),
            ("checked_in", "Checked In"),
            ("cancelled", "Cancelled")
        ]
        
        for filter_key, label in filters:
            btn = ctk.CTkButton(
                filter_frame,
                text=label,
                font=FONTS['body'],
                fg_color=COLORS['accent'] if filter_key == "all" else "transparent",
                hover_color=COLORS['bg_hover'],
                text_color=COLORS['text_primary'],
                height=36,
                corner_radius=RADIUS['md'],
                command=lambda k=filter_key: self._set_filter(k)
            )
            btn.pack(side="left", padx=(0, SPACING['sm']))
            self.filter_buttons[filter_key] = btn
        
        # Stats bar
        stats_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['lg'],
            height=60
        )
        stats_frame.pack(fill="x", padx=SPACING['xl'], pady=(0, SPACING['lg']))
        stats_frame.pack_propagate(False)
        
        stats_content = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_content.pack(fill="both", expand=True, padx=SPACING['lg'])
        
        self.stats_labels = {}
        stats = [
            ("total", "Total", COLORS['text_primary']),
            ("booked", "Booked", COLORS['warning']),
            ("checked", "Checked In", COLORS['success']),
            ("cancelled", "Cancelled", COLORS['error'])
        ]
        
        for key, label, color in stats:
            stat_item = ctk.CTkFrame(stats_content, fg_color="transparent")
            stat_item.pack(side="left", expand=True, fill="both")
            
            value_label = ctk.CTkLabel(
                stat_item,
                text="0",
                font=FONTS['heading'],
                text_color=color
            )
            value_label.pack(side="top", pady=(SPACING['sm'], 0))
            
            ctk.CTkLabel(
                stat_item,
                text=label,
                font=FONTS['caption'],
                text_color=COLORS['text_muted']
            ).pack(side="top")
            
            self.stats_labels[key] = value_label
        
        # Tickets list
        self.tickets_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.tickets_scroll.pack(fill="both", expand=True, padx=SPACING['xl'], pady=(0, SPACING['lg']))
        
        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.tickets_scroll,
            text="No tickets found",
            font=FONTS['body_large'],
            text_color=COLORS['text_muted']
        )
    
    def _set_filter(self, filter_key: str):
        """Set the current filter."""
        self.current_filter = filter_key
        
        # Update button styles
        for key, btn in self.filter_buttons.items():
            if key == filter_key:
                btn.configure(fg_color=COLORS['accent'])
            else:
                btn.configure(fg_color="transparent")
        
        self._refresh_tickets()
    
    def _load_tickets(self):
        """Load tickets from database."""
        self.tickets = db.get_all_tickets()
        self._update_stats()
        self._refresh_tickets()
    
    def _update_stats(self):
        """Update statistics display."""
        total = len(self.tickets)
        booked = sum(1 for t in self.tickets if t.status == TicketStatus.BOOKED)
        checked = sum(1 for t in self.tickets if t.status == TicketStatus.CHECKED_IN)
        cancelled = sum(1 for t in self.tickets if t.status == TicketStatus.CANCELLED)
        
        self.stats_labels['total'].configure(text=str(total))
        self.stats_labels['booked'].configure(text=str(booked))
        self.stats_labels['checked'].configure(text=str(checked))
        self.stats_labels['cancelled'].configure(text=str(cancelled))
    
    def _refresh_tickets(self):
        """Refresh the tickets display."""
        # Clear existing
        for widget in self.tickets_scroll.winfo_children():
            widget.destroy()
        
        # Filter tickets
        filtered = self._filter_tickets()
        
        if not filtered:
            self.empty_label = ctk.CTkLabel(
                self.tickets_scroll,
                text="No tickets found",
                font=FONTS['body_large'],
                text_color=COLORS['text_muted']
            )
            self.empty_label.pack(pady=SPACING['xxl'])
            return
        
        # Display tickets
        for ticket in filtered:
            passenger = db.get_passenger_by_id(ticket.passenger_id)
            passenger_name = passenger.full_name if passenger else "Unknown"
            
            card = TicketCard(
                self.tickets_scroll,
                ticket=ticket,
                passenger_name=passenger_name,
                on_click=self._on_ticket_click,
                on_cancel=self._on_cancel_ticket,
                show_actions=True
            )
            card.pack(fill="x", pady=(0, SPACING['md']))
    
    def _filter_tickets(self) -> List[Ticket]:
        """Filter tickets based on current filter."""
        if self.current_filter == "all":
            return self.tickets
        elif self.current_filter == "booked":
            return [t for t in self.tickets if t.status == TicketStatus.BOOKED]
        elif self.current_filter == "checked_in":
            return [t for t in self.tickets if t.status == TicketStatus.CHECKED_IN]
        elif self.current_filter == "cancelled":
            return [t for t in self.tickets if t.status == TicketStatus.CANCELLED]
        return self.tickets
    
    def _on_ticket_click(self, ticket: Ticket):
        """Handle ticket click - show details."""
        self._show_ticket_detail(ticket)
    
    def _on_cancel_ticket(self, ticket: Ticket):
        """Handle ticket cancellation."""
        app = self.master.master # HistoryView -> content -> App
        
        def do_confirm():
            db.cancel_ticket(ticket.id)
            self._load_tickets()
        
        app.show_overlay(
            ModalConfirm,
            title="Cancel Ticket?",
            message=f"Are you sure you want to cancel ticket {ticket.ticket_number}?\nThis action cannot be undone.",
            confirm_text="Cancel Ticket",
            cancel_text="Keep Ticket",
            confirm_color=COLORS['error'],
            on_confirm=do_confirm
        )

    def _show_ticket_detail(self, ticket: Ticket):
        """Show ticket detail popup in integrated overlay."""
        passenger = db.get_passenger_by_id(ticket.passenger_id)
        app = self.master.master
        
        def do_reset():
            def confirmed():
                db.reset_ticket_checkin(ticket.id)
                audit_service.log_reset(ticket.ticket_number)
                app.hide_overlay()
                self._load_tickets()
            
            app.show_overlay(AdminPinModal, on_success=confirmed, on_cancel=lambda: self._show_ticket_detail(ticket))

        def confirm_delete():
            def do_delete():
                if passenger:
                    db.delete_passenger(passenger.id)
                    audit_service.log_delete(passenger.full_name, passenger.passport_number)
                    app.hide_overlay()
                    self._load_tickets()
            
            app.show_overlay(
                ModalConfirm,
                title="Delete Data?",
                message=f"This will permanently delete all records for:\n{passenger.full_name if passenger else 'User'}",
                confirm_text="Delete Permanently",
                confirm_color=COLORS['error'],
                on_confirm=lambda: app.show_overlay(AdminPinModal, on_success=do_delete, on_cancel=lambda: self._show_ticket_detail(ticket))
            )

        def print_ticket():
            if passenger:
                ticket_path = boarding_pass_service.generate(
                    ticket_number=ticket.ticket_number,
                    passenger_name=passenger.full_name,
                    source_airport=ticket.source_airport,
                    source_city=ticket.source_airport_name or ticket.source_airport,
                    destination_airport=ticket.destination_airport,
                    destination_city=ticket.destination_airport_name or ticket.destination_airport,
                    flight_date=str(ticket.flight_date),
                    flight_time=ticket.flight_time.strftime("%H:%M") if ticket.flight_time else "TBD",
                    seat=ticket.seat_number or "TBD",
                    gate=ticket.gate or "TBD",
                    passport_number=passenger.passport_number
                )
                
                if ticket_path:
                    from services.sound_service import sound_service
                    sound_service.play_success()
                    # Optionally open the PDF
                    from pathlib import Path
                    boarding_pass_service.open_pdf(Path(ticket_path))
                
                app.hide_overlay()

        app.show_overlay(
            ModalTicketDetail,
            ticket=ticket,
            passenger_name=passenger.full_name if passenger else "Unknown",
            passenger_passport=passenger.passport_number if passenger else "N/A",
            on_reset=do_reset,
            on_delete=confirm_delete,
            on_print=print_ticket,
            on_close=app.hide_overlay
        )
    
    def on_show(self):
        """Called when view is shown."""
        self._load_tickets()
    
    def on_hide(self):
        """Called when view is hidden."""
        pass
