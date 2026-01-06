"""
Theme configuration for the Flight Kiosk GUI.
Supports both dark and light themes with cyan accents.
"""

# Current theme mode
_current_mode = "dark"

# Dark theme colors
DARK_COLORS = {
    # Backgrounds
    'bg_primary': '#0a0e17',      # Deep navy black
    'bg_secondary': '#141b2d',    # Dark blue-gray
    'bg_card': '#1e2738',         # Card background
    'bg_input': '#252d3d',        # Input field background
    'bg_hover': '#2a3548',        # Hover state
    
    # Accents
    'accent': '#00d4ff',          # Bright cyan
    'accent_hover': '#00a8cc',    # Darker cyan
    'accent_light': '#33ddff',    # Lighter cyan
    
    # Status colors
    'success': '#00e676',         # Green
    'warning': '#ffc107',         # Amber
    'error': '#ff5252',           # Red
    'info': '#2196f3',            # Blue
    
    # Text
    'text_primary': '#ffffff',    # White
    'text_secondary': '#8892a0',  # Gray
    'text_muted': '#5a6270',      # Darker gray
    
    # Borders
    'border': '#2a3548',          # Border color
    'border_light': '#3d4a5c',    # Lighter border
}

# Light theme colors
LIGHT_COLORS = {
    # Backgrounds
    'bg_primary': '#f5f7fa',      # Light gray
    'bg_secondary': '#ffffff',    # White
    'bg_card': '#ffffff',         # Card background
    'bg_input': '#e8ecf1',        # Input field background
    'bg_hover': '#e1e5eb',        # Hover state
    
    # Accents
    'accent': '#0099cc',          # Darker cyan for contrast
    'accent_hover': '#007aa3',    # Even darker cyan
    'accent_light': '#33b5e5',    # Lighter cyan
    
    # Status colors
    'success': '#00a854',         # Darker green for contrast
    'warning': '#d48806',         # Darker amber
    'error': '#cf1322',           # Darker red
    'info': '#1890ff',            # Blue
    
    # Text
    'text_primary': '#1a1a2e',    # Dark navy
    'text_secondary': '#5c6370',  # Gray
    'text_muted': '#8c939d',      # Lighter gray
    
    # Borders
    'border': '#d9dde3',          # Light border
    'border_light': '#e8ecf1',    # Even lighter border
}

# Active colors (defaults to dark)
COLORS = DARK_COLORS.copy()

# Font configuration
FONTS = {
    'heading_large': ('Segoe UI', 32, 'bold'),
    'heading': ('Segoe UI', 24, 'bold'),
    'subheading': ('Segoe UI', 18, 'bold'),
    'body_large': ('Segoe UI', 16),
    'body': ('Segoe UI', 14),
    'body_small': ('Segoe UI', 12),
    'caption': ('Segoe UI', 10),
    'button': ('Segoe UI', 14, 'bold'),
    'code': ('Consolas', 12),
}

# Spacing
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
    'xxl': 48,
}

# Border radius
RADIUS = {
    'sm': 4,
    'md': 8,
    'lg': 12,
    'xl': 16,
    'full': 9999,
}

# Shadows (for potential future use)
SHADOWS = {
    'sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
    'md': '0 4px 6px rgba(0, 0, 0, 0.4)',
    'lg': '0 10px 15px rgba(0, 0, 0, 0.5)',
}


def get_theme_mode() -> str:
    """Get the current theme mode."""
    return _current_mode


def set_theme_mode(mode: str):
    """Set the theme mode and update COLORS."""
    global _current_mode, COLORS
    
    if mode not in ("dark", "light"):
        mode = "dark"
    
    _current_mode = mode
    
    if mode == "dark":
        COLORS.clear()
        COLORS.update(DARK_COLORS)
    else:
        COLORS.clear()
        COLORS.update(LIGHT_COLORS)


def toggle_theme() -> str:
    """Toggle between dark and light theme. Returns new mode."""
    new_mode = "light" if _current_mode == "dark" else "dark"
    set_theme_mode(new_mode)
    return new_mode


def apply_theme(ctk):
    """Apply custom theme to CustomTkinter."""
    ctk.set_appearance_mode(_current_mode)
    ctk.set_default_color_theme("blue")
