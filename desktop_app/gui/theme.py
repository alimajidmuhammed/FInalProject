"""
Theme configuration for the Flight Kiosk GUI.
Supports both dark and light themes with cyan accents.
"""

# Current theme mode
_current_mode = "dark"

# Dark theme colors
DARK_COLORS = {
    # Backgrounds
    'bg_primary': '#05070a',      # even deeper navy black
    'bg_secondary': '#0d1117',    # modern dark gray
    'bg_card': '#161b22',         # card background
    'bg_input': '#1c2128',        # slightly darker input
    'bg_hover': '#30363d',        # hover state
    
    # Accents
    'accent': '#00f2ff',          # Neon cyan
    'accent_hover': '#00cce6',    # Darker cyan
    'accent_light': '#80fbff',    # Lighter cyan
    
    # Status colors
    'success': '#00ff88',         # Neon green
    'warning': '#ffcc00',         # Bright amber
    'error': '#ff3366',           # Vivid red-pink
    'info': '#0077ff',            # Electric blue
    
    # Text
    'text_primary': '#f0f6fc',    # Off-white
    'text_secondary': '#8b949e',  # Gray
    'text_muted': '#484f58',      # Darker gray
    
    # Borders
    'border': '#444c56',          # Lighter border for visibility
    'border_light': '#57606a',    # Lighter border
}

# Light theme colors
LIGHT_COLORS = {
    # Backgrounds
    'bg_primary': '#f6f8fa',      # Light gray
    'bg_secondary': '#ffffff',    # White
    'bg_card': '#ffffff',         # Card background
    'bg_input': '#f3f4f6',        # Input field background
    'bg_hover': '#ebedef',        # Hover state
    
    # Accents
    'accent': '#0969da',          # Professional blue
    'accent_hover': '#0550ae',    # Darker blue
    'accent_light': '#54aeff',    # Lighter blue
    
    # Status colors
    'success': '#1a7f37',         # Darker green
    'warning': '#9a6700',         # Darker amber
    'error': '#cf222e',           # Darker red
    'info': '#0969da',            # Blue
    
    # Text
    'text_primary': '#1f2328',    # Deep gray
    'text_secondary': '#656d76',  # Gray
    'text_muted': '#8c959f',      # Lighter gray
    
    # Borders
    'border': '#d0d7de',          # Light border
    'border_light': '#d8dee4',    # Even lighter border
}

# Active colors (defaults to dark)
COLORS = DARK_COLORS.copy()

# Font configuration
FONTS = {
    'heading_large': ('Segoe UI Display', 40, 'bold'),
    'heading': ('Segoe UI Display', 28, 'bold'),
    'subheading': ('Segoe UI', 20, 'bold'),
    'body_large': ('Segoe UI', 18),
    'body': ('Segoe UI', 15),
    'body_small': ('Segoe UI', 13),
    'caption': ('Segoe UI', 11),
    'button': ('Segoe UI', 15, 'bold'),
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
    '3xl': 64,
}

# Border radius
RADIUS = {
    'sm': 8,
    'md': 12,
    'lg': 20,
    'xl': 28,
    '2xl': 40,
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
