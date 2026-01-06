"""
History View - Ticket management and history.
Shows all tickets with filtering and management options.
"""
from typing import Optional, List
import customtkinter as ctk

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from gui.components.ticket_card import TicketCard
from gui.components.admin_dialog import require_admin_pin
from database.db_manager import db
from database.models import Ticket, TicketStatus
from services.audit_service import audit_service


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
        # Confirm dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Cancellation")
        dialog.geometry("400x200")
        dialog.configure(fg_color=COLORS['bg_secondary'])
        dialog.transient(self)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 200) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Wait for window to be visible before grabbing
        dialog.wait_visibility()
        dialog.grab_set()
        
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        ctk.CTkLabel(
            content,
            text="Cancel Ticket?",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack(pady=SPACING['sm'])
        
        ctk.CTkLabel(
            content,
            text=f"Are you sure you want to cancel ticket {ticket.ticket_number}?",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(pady=SPACING['md'])
        
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=SPACING['md'])
        
        def confirm():
            db.cancel_ticket(ticket.id)
            dialog.destroy()
            self._load_tickets()
        
        ctk.CTkButton(
            btn_frame,
            text="Keep Ticket",
            font=FONTS['button'],
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            border_width=1,
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            height=40,
            command=dialog.destroy
        ).pack(side="left", expand=True, padx=SPACING['xs'])
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel Ticket",
            font=FONTS['button'],
            fg_color=COLORS['error'],
            hover_color="#cc4242",
            height=40,
            command=confirm
        ).pack(side="right", expand=True, padx=SPACING['xs'])
    
    def _show_ticket_detail(self, ticket: Ticket):
        """Show ticket detail popup."""
        passenger = db.get_passenger_by_id(ticket.passenger_id)
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Ticket {ticket.ticket_number}")
        dialog.geometry("700x600")
        dialog.configure(fg_color=COLORS['bg_secondary'])
        dialog.transient(self)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 700) // 2
        y = (dialog.winfo_screenheight() - 600) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Wait for window to be visible before grabbing
        dialog.wait_visibility()
        dialog.grab_set()
        
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['lg'])
        
        # Header
        ctk.CTkLabel(
            content,
            text=ticket.ticket_number,
            font=FONTS['heading'],
            text_color=COLORS['accent']
        ).pack(anchor="w")
        
        # Status
        status_color = {
            TicketStatus.BOOKED: COLORS['warning'],
            TicketStatus.CHECKED_IN: COLORS['success'],
            TicketStatus.CANCELLED: COLORS['error']
        }.get(ticket.status, COLORS['text_muted'])
        
        ctk.CTkLabel(
            content,
            text=f"● {ticket.status.value.upper().replace('_', ' ')}",
            font=FONTS['body'],
            text_color=status_color
        ).pack(anchor="w", pady=(SPACING['xs'], SPACING['lg']))
        
        # Route
        route_frame = ctk.CTkFrame(content, fg_color=COLORS['bg_card'], corner_radius=RADIUS['lg'])
        route_frame.pack(fill="x", pady=SPACING['md'])
        
        route_content = ctk.CTkFrame(route_frame, fg_color="transparent")
        route_content.pack(padx=SPACING['lg'], pady=SPACING['md'])
        
        ctk.CTkLabel(
            route_content,
            text=f"{ticket.source_airport}  →  {ticket.destination_airport}",
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS['text_primary']
        ).pack()
        
        if ticket.source_airport_name:
            ctk.CTkLabel(
                route_content,
                text=f"{ticket.source_airport_name} to {ticket.destination_airport_name}",
                font=FONTS['body_small'],
                text_color=COLORS['text_secondary']
            ).pack()
        
        # Details grid
        details_frame = ctk.CTkFrame(content, fg_color="transparent")
        details_frame.pack(fill="x", pady=SPACING['lg'])
        
        details = [
            ("Passenger", passenger.full_name if passenger else "Unknown"),
            ("Passport", passenger.passport_number if passenger else "N/A"),
            ("Date", str(ticket.flight_date)),
            ("Time", ticket.flight_time.strftime("%H:%M") if ticket.flight_time else "TBD"),
            ("Seat", ticket.seat_number or "Not assigned"),
            ("Gate", ticket.gate or "Not assigned"),
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            
            frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            frame.grid(row=row, column=col, sticky="w", padx=SPACING['md'], pady=SPACING['xs'])
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=FONTS['caption'],
                text_color=COLORS['text_muted']
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                frame,
                text=value,
                font=FONTS['body'],
                text_color=COLORS['text_primary']
            ).pack(anchor="w")
        
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Action buttons frame
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(SPACING['lg'], 0))
        
        # Reset Check-In button (only for checked-in tickets)
        if ticket.status == TicketStatus.CHECKED_IN:
            def do_reset():
                db.reset_ticket_checkin(ticket.id)
                audit_service.log_reset(ticket.ticket_number)
                dialog.destroy()
                self._load_tickets()
            
            def reset_checkin():
                # Require admin PIN
                require_admin_pin(
                    dialog,
                    on_success=do_reset,
                    title="Admin PIN Required"
                )
            
            ctk.CTkButton(
                btn_frame,
                text="🔄 Reset Check-In",
                font=FONTS['button'],
                fg_color=COLORS['warning'],
                hover_color="#cc8800",
                text_color=COLORS['bg_primary'],
                height=45,
                command=reset_checkin
            ).pack(side="left", expand=True, fill="x", padx=(0, SPACING['sm']))
        
        # Delete Passenger button (admin protected)
        def do_delete():
            if passenger:
                db.delete_passenger(passenger.id)
                audit_service.log_delete(passenger.full_name, passenger.passport_number)
                dialog.destroy()
                self._load_tickets()
        
        def delete_passenger():
            # Show confirmation dialog first
            confirm_dialog = ctk.CTkToplevel(dialog)
            confirm_dialog.title("Confirm Delete")
            confirm_dialog.geometry("450x220")
            confirm_dialog.configure(fg_color=COLORS['bg_secondary'])
            confirm_dialog.transient(dialog)
            
            # Center the dialog
            confirm_dialog.update_idletasks()
            x = (confirm_dialog.winfo_screenwidth() - 450) // 2
            y = (confirm_dialog.winfo_screenheight() - 220) // 2
            confirm_dialog.geometry(f"+{x}+{y}")
            
            confirm_dialog.wait_visibility()
            confirm_dialog.grab_set()
            
            confirm_content = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
            confirm_content.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
            
            ctk.CTkLabel(
                confirm_content,
                text="⚠️ Delete Passenger?",
                font=FONTS['subheading'],
                text_color=COLORS['error']
            ).pack(pady=SPACING['sm'])
            
            passenger_info = f"{passenger.full_name}\n({passenger.passport_number})" if passenger else "Unknown"
            ctk.CTkLabel(
                confirm_content,
                text=f"This will permanently delete:\n{passenger_info}\n\nAll tickets for this passenger will also be deleted.",
                font=FONTS['body'],
                text_color=COLORS['text_secondary'],
                justify="center"
            ).pack(pady=SPACING['md'])
            
            confirm_btn_frame = ctk.CTkFrame(confirm_content, fg_color="transparent")
            confirm_btn_frame.pack(fill="x", pady=SPACING['md'])
            
            def on_confirm():
                confirm_dialog.destroy()
                # Now require admin PIN
                require_admin_pin(
                    dialog,
                    on_success=do_delete,
                    title="Admin PIN Required"
                )
            
            ctk.CTkButton(
                confirm_btn_frame,
                text="Cancel",
                font=FONTS['button'],
                fg_color="transparent",
                hover_color=COLORS['bg_hover'],
                border_width=1,
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
                height=40,
                command=confirm_dialog.destroy
            ).pack(side="left", expand=True, padx=SPACING['xs'])
            
            ctk.CTkButton(
                confirm_btn_frame,
                text="Delete Permanently",
                font=FONTS['button'],
                fg_color=COLORS['error'],
                hover_color="#cc4242",
                height=40,
                command=on_confirm
            ).pack(side="right", expand=True, padx=SPACING['xs'])
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete Passenger",
            font=FONTS['button'],
            fg_color=COLORS['error'],
            hover_color="#cc4242",
            height=45,
            command=delete_passenger
        ).pack(side="left", expand=True, fill="x", padx=(0, SPACING['sm']))
        
        # Close button
        ctk.CTkButton(
            btn_frame,
            text="Close",
            font=FONTS['button'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            height=45,
            command=dialog.destroy
        ).pack(side="right", expand=True, fill="x")
    
    def on_show(self):
        """Called when view is shown."""
        self._load_tickets()
    
    def on_hide(self):
        """Called when view is hidden."""
        pass
