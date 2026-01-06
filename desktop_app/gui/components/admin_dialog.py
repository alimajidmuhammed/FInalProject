"""
Admin Dialog - PIN verification for admin functions.
"""
import customtkinter as ctk
from typing import Callable, Optional

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from config import ADMIN_PIN


class AdminPinDialog(ctk.CTkToplevel):
    """Dialog for admin PIN verification - Fullscreen modal."""
    
    def __init__(
        self,
        parent,
        title: str = "Admin Verification",
        message: str = "Enter admin PIN to continue:",
        on_success: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ):
        super().__init__(parent)
        
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.entered_pin = ""
        
        # Window setup - Make it larger and more visible
        self.title(title)
        self.configure(fg_color=COLORS['bg_primary'])
        self.transient(parent)
        self.resizable(True, True)
        
        # Make dialog larger - 600x500
        self.geometry("600x500")
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 600) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"+{x}+{y}")
        
        self._setup_ui(message)
        
        # Wait for window visibility before grab
        self.wait_visibility()
        self.grab_set()
        self.focus_force()
    
    def _setup_ui(self, message: str):
        """Setup the dialog UI."""
        # Main container for centering
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="🔐 Admin Verification",
            font=FONTS['heading'],
            text_color=COLORS['accent']
        ).pack(pady=(0, SPACING['md']))
        
        # Message
        ctk.CTkLabel(
            main_frame,
            text=message,
            font=FONTS['body_large'],
            text_color=COLORS['text_secondary']
        ).pack(pady=SPACING['md'])
        
        # PIN display - Show empty circles initially
        self.pin_display = ctk.CTkLabel(
            main_frame,
            text="○  ○  ○  ○",
            font=('Segoe UI', 48, 'bold'),
            text_color=COLORS['text_muted']
        )
        self.pin_display.pack(pady=SPACING['lg'])
        
        # Error label
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=FONTS['body'],
            text_color=COLORS['error']
        )
        self.error_label.pack(pady=SPACING['sm'])
        
        # Keypad container
        keypad_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        keypad_frame.pack(pady=SPACING['lg'])
        
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['C', '0', 'OK']
        ]
        
        for row in buttons:
            row_frame = ctk.CTkFrame(keypad_frame, fg_color="transparent")
            row_frame.pack(pady=4)
            
            for digit in row:
                if digit == 'C':
                    btn = ctk.CTkButton(
                        row_frame,
                        text="Clear",
                        width=100,
                        height=60,
                        font=FONTS['button'],
                        fg_color=COLORS['error'],
                        hover_color='#cc4242',
                        command=self._clear_pin
                    )
                elif digit == 'OK':
                    btn = ctk.CTkButton(
                        row_frame,
                        text="OK",
                        width=100,
                        height=60,
                        font=FONTS['button'],
                        fg_color=COLORS['success'],
                        hover_color='#00aa44',
                        command=self._verify_pin
                    )
                else:
                    btn = ctk.CTkButton(
                        row_frame,
                        text=digit,
                        width=100,
                        height=60,
                        font=('Segoe UI', 24, 'bold'),
                        fg_color=COLORS['bg_card'],
                        hover_color=COLORS['bg_hover'],
                        text_color=COLORS['text_primary'],
                        command=lambda d=digit: self._add_digit(d)
                    )
                btn.pack(side="left", padx=4)
        
        # Cancel button
        ctk.CTkButton(
            main_frame,
            text="Cancel",
            font=FONTS['body_large'],
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_secondary'],
            height=40,
            width=200,
            command=self._cancel
        ).pack(pady=SPACING['lg'])
        
        # Bind keyboard
        self.bind('<Key>', self._on_key)
        self.bind('<Return>', lambda e: self._verify_pin())
        self.bind('<Escape>', lambda e: self._cancel())
    
    def _add_digit(self, digit: str):
        """Add a digit to the PIN."""
        if len(self.entered_pin) < 4:
            self.entered_pin += digit
            self._update_display()
            self.error_label.configure(text="")
    
    def _clear_pin(self):
        """Clear the entered PIN."""
        self.entered_pin = ""
        self._update_display()
        self.error_label.configure(text="")
    
    def _update_display(self):
        """Update the PIN display."""
        filled = len(self.entered_pin)
        # Use filled circle for entered, empty for remaining
        display = "●  " * filled + "○  " * (4 - filled)
        color = COLORS['accent'] if filled > 0 else COLORS['text_muted']
        self.pin_display.configure(text=display.strip(), text_color=color)
    
    def _verify_pin(self):
        """Verify the entered PIN."""
        if self.entered_pin == ADMIN_PIN:
            self.destroy()
            if self.on_success:
                self.on_success()
        else:
            self.error_label.configure(text="Incorrect PIN - Try again")
            self.entered_pin = ""
            self._update_display()
    
    def _cancel(self):
        """Cancel the dialog."""
        self.destroy()
        if self.on_cancel:
            self.on_cancel()
    
    def _on_key(self, event):
        """Handle keyboard input."""
        if event.char.isdigit():
            self._add_digit(event.char)
        elif event.keysym == 'BackSpace':
            if self.entered_pin:
                self.entered_pin = self.entered_pin[:-1]
                self._update_display()


def require_admin_pin(parent, on_success: Callable, title: str = "Admin Required"):
    """
    Show admin PIN dialog and call on_success if PIN is correct.
    
    Usage:
        require_admin_pin(self, lambda: self.do_admin_action())
    """
    AdminPinDialog(
        parent,
        title=title,
        on_success=on_success
    )
