"""
Airport Selector - Searchable dropdown for airport selection.
"""
from typing import Callable, Optional, Dict, List
import customtkinter as ctk

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from services.airport_service import airport_service


class AirportSelector(ctk.CTkFrame):
    """
    A searchable dropdown component for selecting airports.
    """
    
    def __init__(
        self,
        parent,
        label: str = "Airport",
        placeholder: str = "Search by city, country, or code...",
        on_select: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_select = on_select
        self.selected_airport: Optional[Dict] = None
        self.search_results: List[Dict] = []
        self.dropdown_visible = False
        
        self._setup_ui(label, placeholder)
    
    def _setup_ui(self, label: str, placeholder: str):
        """Setup the selector UI."""
        # Label
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        self.label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        # Container for entry and dropdown
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="x")
        
        # Search entry
        self.entry = ctk.CTkEntry(
            self.container,
            placeholder_text=placeholder,
            font=FONTS['body'],
            height=45,
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted']
        )
        self.entry.pack(fill="x")
        self.entry.bind("<KeyRelease>", self._on_search)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Dropdown frame (initially hidden)
        self.dropdown_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['md'],
            height=200
        )
        
        # Selected display (shown after selection)
        self.selected_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['md'],
            height=45
        )
        
        self.selected_label = ctk.CTkLabel(
            self.selected_frame,
            text="",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        self.selected_label.pack(side="left", padx=SPACING['md'], pady=SPACING['sm'])
        
        self.clear_btn = ctk.CTkButton(
            self.selected_frame,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_secondary'],
            font=FONTS['body'],
            command=self._clear_selection
        )
        self.clear_btn.pack(side="right", padx=SPACING['xs'])
    
    def _on_search(self, event=None):
        """Handle search input."""
        query = self.entry.get().strip()
        
        if len(query) < 2:
            self._hide_dropdown()
            return
        
        # Search airports
        self.search_results = airport_service.search(query, limit=8)
        
        if self.search_results:
            self._show_dropdown()
        else:
            self._hide_dropdown()
    
    def _show_dropdown(self):
        """Show the dropdown with search results."""
        # Clear existing items
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()
        
        # Add result items
        for airport in self.search_results:
            item = ctk.CTkButton(
                self.dropdown_frame,
                text=airport_service.format_airport_display(airport),
                font=FONTS['body_small'],
                fg_color="transparent",
                hover_color=COLORS['bg_hover'],
                text_color=COLORS['text_primary'],
                anchor="w",
                height=40,
                command=lambda a=airport: self._select_airport(a)
            )
            item.pack(fill="x", pady=1)
        
        # Show dropdown
        if not self.dropdown_visible:
            self.dropdown_frame.pack(fill="x", pady=(SPACING['xs'], 0))
            self.dropdown_visible = True
    
    def _hide_dropdown(self):
        """Hide the dropdown."""
        if self.dropdown_visible:
            self.dropdown_frame.pack_forget()
            self.dropdown_visible = False
    
    def _select_airport(self, airport: Dict):
        """Handle airport selection."""
        self.selected_airport = airport
        
        # Update display
        display_text = airport_service.format_airport_short(airport)
        self.selected_label.configure(text=display_text)
        
        # Show selected frame, hide entry
        self.entry.pack_forget()
        self._hide_dropdown()
        self.selected_frame.pack(fill="x")
        
        # Callback
        if self.on_select:
            self.on_select(airport)
    
    def _clear_selection(self):
        """Clear the current selection."""
        self.selected_airport = None
        
        # Hide selected frame, show entry
        self.selected_frame.pack_forget()
        self.entry.delete(0, "end")
        self.entry.pack(fill="x")
        
        # Callback with None
        if self.on_select:
            self.on_select(None)
    
    def _on_focus_in(self, event=None):
        """Handle focus in."""
        self.entry.configure(border_color=COLORS['accent'])
    
    def _on_focus_out(self, event=None):
        """Handle focus out."""
        self.entry.configure(border_color=COLORS['border'])
        # Delay hiding to allow click on dropdown items
        self.after(200, self._hide_dropdown)
    
    def get_selected(self) -> Optional[Dict]:
        """Get the selected airport."""
        return self.selected_airport
    
    def set_airport(self, airport: Dict):
        """Programmatically set the selected airport."""
        self._select_airport(airport)
    
    def reset(self):
        """Reset the selector to initial state."""
        self._clear_selection()
