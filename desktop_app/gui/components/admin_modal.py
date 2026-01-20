"""
Admin Dialog - Integrated PIN verification for admin functions.
Designed for the new Integrated Overlay system.
"""
import customtkinter as ctk
from typing import Callable, Optional
from gui.theme import COLORS, FONTS, RADIUS, SPACING
from config import ADMIN_PIN

class AdminPinModal(ctk.CTkFrame):
    """Integrated Modal for admin PIN verification."""
    
    def __init__(
        self,
        parent,
        title: str = "Admin Verification",
        message: str = "Enter admin PIN to continue:",
        on_success: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ):
        super().__init__(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['2xl'],
            border_width=2,
            border_color=COLORS['border'],
            width=600,
            height=700
        )
        self.pack_propagate(False)
        
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.entered_pin = ""
        
        self._setup_ui(message)
        
    def _setup_ui(self, message: str):
        """Setup the modal UI."""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Close button
        ctk.CTkButton(
            self,
            text="✕",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_muted'],
            font=("Segoe UI", 20),
            command=self._cancel
        ).place(relx=0.95, rely=0.05, anchor="ne")
        
        # Icon
        ctk.CTkLabel(container, text="🔐", font=("Segoe UI", 80)).pack(pady=(0, SPACING['lg']))
        
        # Title
        ctk.CTkLabel(
            container,
            text="Admin Verification",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        ).pack()
        
        # Message
        ctk.CTkLabel(
            container,
            text=message,
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(pady=SPACING['lg'])
        
        # PIN display
        self.pin_display = ctk.CTkLabel(
            container,
            text="○  ○  ○  ○",
            font=('Segoe UI', 64, 'bold'),
            text_color=COLORS['text_muted']
        )
        self.pin_display.pack(pady=SPACING['xl'])
        
        # Keypad
        keypad_frame = ctk.CTkFrame(container, fg_color="transparent")
        keypad_frame.pack()
        
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['C', '0', 'OK']
        ]
        
        for row in buttons:
            row_frame = ctk.CTkFrame(keypad_frame, fg_color="transparent")
            row_frame.pack(pady=SPACING['sm'])
            for digit in row:
                if digit == 'C':
                    btn_color = COLORS['bg_card']; text_color = COLORS['error']; cmd = self._clear_pin; text = "Clear"
                elif digit == 'OK':
                    btn_color = COLORS['accent']; text_color = COLORS['bg_primary']; cmd = self._verify_pin; text = "OK"
                else:
                    btn_color = COLORS['bg_input']; text_color = COLORS['text_primary']; cmd = lambda d=digit: self._add_digit(d); text = digit
                
                ctk.CTkButton(
                    row_frame,
                    text=text,
                    width=100,
                    height=70,
                    font=FONTS['button'] if not text.isdigit() else ('Segoe UI', 28, 'bold'),
                    fg_color=btn_color,
                    hover_color=COLORS['bg_hover'] if text.isdigit() else None,
                    text_color=text_color,
                    corner_radius=RADIUS['lg'],
                    command=cmd
                ).pack(side="left", padx=SPACING['sm'])
        
        # Error label
        self.error_label = ctk.CTkLabel(container, text="", font=FONTS['body_small'], text_color=COLORS['error'])
        self.error_label.pack(pady=SPACING['md'])
        
    def _add_digit(self, digit: str):
        if len(self.entered_pin) < 4:
            self.entered_pin += digit
            self._update_display()
            self.error_label.configure(text="")
            if len(self.entered_pin) == 4:
                self.after(300, self._verify_pin)
    
    def _clear_pin(self):
        self.entered_pin = ""
        self._update_display()
        self.error_label.configure(text="")
    
    def _update_display(self):
        filled = len(self.entered_pin)
        display = "●  " * filled + "○  " * (4 - filled)
        color = COLORS['accent'] if filled > 0 else COLORS['text_muted']
        self.pin_display.configure(text=display.strip(), text_color=color)
    
    def _verify_pin(self):
        if not self.entered_pin: return
        if self.entered_pin == ADMIN_PIN:
            if self.on_success: self.on_success()
            self.master.master.hide_overlay() # AdminPinModal -> overlay_container -> App
        else:
            self.error_label.configure(text="Incorrect PIN")
            self.entered_pin = ""
            self._update_display()
    
    def _cancel(self):
        if self.on_cancel: self.on_cancel()
        self.master.master.hide_overlay()
