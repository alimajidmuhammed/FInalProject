"""
Modal Confirm - Integrated confirmation overlay.
Designed for the new Integrated Overlay system.
"""
import customtkinter as ctk
from typing import Callable, Optional
from gui.theme import COLORS, FONTS, RADIUS, SPACING

class ModalConfirm(ctk.CTkFrame):
    """Integrated Modal for confirmations."""
    
    def __init__(
        self,
        parent,
        title: str = "Are you sure?",
        message: str = "",
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        confirm_color: Optional[str] = None,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ):
        super().__init__(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['2xl'],
            border_width=2,
            border_color=COLORS['border'],
            width=600,
            height=400
        )
        self.pack_propagate(False)
        
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        
        self._setup_ui(title, message, confirm_text, cancel_text, confirm_color or COLORS['accent'])
        
    def _setup_ui(self, title: str, message: str, confirm_text: str, cancel_text: str, confirm_color: str):
        """Setup the modal UI."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icon
        ctk.CTkLabel(container, text="⚠️", font=("Segoe UI", 60)).pack(pady=(0, SPACING['md']))
        
        # Title
        ctk.CTkLabel(
            container,
            text=title,
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack()
        
        # Message
        ctk.CTkLabel(
            container,
            text=message,
            font=FONTS['body'],
            text_color=COLORS['text_secondary'],
            justify="center",
            wraplength=500
        ).pack(pady=SPACING['xl'])
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack()
        
        ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            font=FONTS['button'],
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_hover'],
            width=180,
            height=55,
            corner_radius=RADIUS['lg'],
            command=self._handle_cancel
        ).pack(side="left", padx=SPACING['md'])
        
        ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            font=FONTS['button'],
            fg_color=confirm_color,
            width=180,
            height=55,
            corner_radius=RADIUS['lg'],
            command=self._handle_confirm
        ).pack(side="right", padx=SPACING['md'])
        
    def _handle_confirm(self):
        # Hide overlay FIRST, then call callback so chained overlays work
        self.master.master.hide_overlay()
        if self.on_confirm: self.on_confirm()
        
    def _handle_cancel(self):
        self.master.master.hide_overlay()
        if self.on_cancel: self.on_cancel()
