"""
Modal Selector - Integrated selection overlay for airports and other options.
Designed to run within the App's overlay system.
"""
import customtkinter as ctk
from typing import List, Callable, Optional
from gui.theme import COLORS, FONTS, RADIUS, SPACING

class ModalSelector(ctk.CTkFrame):
    """
    An integrated, touch-friendly selection component.
    """
    
    def __init__(
        self,
        parent,
        items: List[str],
        title: str = "Select Option",
        current_value: Optional[str] = None,
        on_select: Optional[Callable[[str], None]] = None,
        on_close: Optional[Callable[[], None]] = None
    ):
        # We take up 90% of the screen width and height for a premium overlay look
        super().__init__(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['2xl'],
            border_width=2,
            border_color=COLORS['border'],
            width=1000,
            height=800
        )
        self.pack_propagate(False)
        
        self.items = items
        self.current_value = current_value
        self.on_select = on_select
        self.on_close = on_close
        
        self._setup_ui(title)
        
    def _setup_ui(self, title: str):
        """Setup the integrated UI."""
        # Top bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=80)
        top_bar.pack(fill="x", padx=SPACING['xl'], pady=SPACING['lg'])
        
        ctk.CTkLabel(
            top_bar,
            text=title,
            font=FONTS['heading'],
            text_color=COLORS['accent']
        ).pack(side="left")
        
        ctk.CTkButton(
            top_bar,
            text="✕",
            font=FONTS['heading'],
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            width=50,
            text_color=COLORS['text_muted'],
            command=self._handle_close
        ).pack(side="right")
        
        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        
        search_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_input'], corner_radius=RADIUS['full'], height=60)
        search_frame.pack(fill="x", padx=SPACING['xxl'], pady=(0, SPACING['xl']))
        search_frame.pack_propagate(False)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Type to search destination...",
            font=FONTS['body_large'],
            fg_color="transparent",
            border_width=0,
            placeholder_text_color=COLORS['text_muted']
        )
        self.search_entry.pack(fill="both", expand=True, padx=SPACING['xl'])
        self.search_entry.focus_set()
        
        # Grid area
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll.pack(fill="both", expand=True, padx=SPACING['xl'], pady=(0, SPACING['xl']))
        
        self._render_items(self.items)
        
    def _render_items(self, items: List[str]):
        """Render the list of items (limited to 50 for performance)."""
        for widget in self.scroll.winfo_children():
            widget.destroy()
        
        # Limit to 50 items for fast rendering
        display_items = items[:50]
        
        for item in display_items:
            is_selected = item == self.current_value
            
            bg_color = COLORS['accent'] if is_selected else COLORS['bg_card']
            text_color = COLORS['bg_primary'] if is_selected else COLORS['text_primary']
            hover_color = COLORS['accent_hover'] if is_selected else COLORS['bg_hover']
            
            btn = ctk.CTkButton(
                self.scroll,
                text=item,
                font=FONTS['body_large'] if not is_selected else ("Segoe UI", 20, "bold"),
                fg_color=bg_color,
                hover_color=hover_color,
                text_color=text_color,
                height=60,
                corner_radius=RADIUS['md'],
                anchor="w",
                command=lambda val=item: self._on_item_click(val)
            )
            btn.pack(fill="x", pady=2, padx=SPACING['xs'])
        
        # Show count if limited
        if len(items) > 50:
            ctk.CTkLabel(
                self.scroll,
                text=f"+ {len(items) - 50} more... (type to filter)",
                font=FONTS['caption'],
                text_color=COLORS['text_muted']
            ).pack(pady=SPACING['sm'])

    def _on_search(self, *args):
        # Debounce search with 100ms delay
        if hasattr(self, '_search_job'):
            self.after_cancel(self._search_job)
        self._search_job = self.after(100, self._do_search)
    
    def _do_search(self):
        query = self.search_var.get().lower()
        filtered = [i for i in self.items if query in i.lower()]
        self._render_items(filtered)
        
    def _on_item_click(self, value: str):
        if self.on_select:
            self.on_select(value)
        self._handle_close()
        
    def _handle_close(self):
        if self.on_close:
            self.on_close()
