"""
Theme configuration for the Flight Kiosk GUI.
Supports dark, light, and high contrast themes with accessibility features.
"""

# Current theme mode
_current_mode = "dark"
_accessibility_mode = False
_large_text = False

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

# High contrast theme for accessibility
HIGH_CONTRAST_COLORS = {
    # Backgrounds
    'bg_primary': '#000000',      # Pure black
    'bg_secondary': '#000000',    # Pure black
    'bg_card': '#1a1a1a',         # Very dark gray
    'bg_input': '#1a1a1a',        # Very dark gray
    'bg_hover': '#333333',        # Dark gray
    
    # Accents - bright and saturated
    'accent': '#00ffff',          # Bright cyan
    'accent_hover': '#00cccc',    # Slightly darker cyan
    'accent_light': '#66ffff',    # Light cyan
    
    # Status colors - maximum contrast
    'success': '#00ff00',         # Bright green
    'warning': '#ffff00',         # Bright yellow
    'error': '#ff0000',           # Bright red
    'info': '#00aaff',            # Bright blue
    
    # Text - maximum contrast
    'text_primary': '#ffffff',    # Pure white
    'text_secondary': '#ffffff',  # Pure white (higher contrast)
    'text_muted': '#cccccc',      # Light gray
    
    # Borders - high visibility
    'border': '#ffffff',          # White borders
    'border_light': '#cccccc',    # Light gray borders
}

# Active colors (defaults to dark)
COLORS = DARK_COLORS.copy()

# Standard font configuration
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

# Large font configuration for accessibility
LARGE_FONTS = {
    'heading_large': ('Segoe UI Display', 52, 'bold'),
    'heading': ('Segoe UI Display', 36, 'bold'),
    'subheading': ('Segoe UI', 26, 'bold'),
    'body_large': ('Segoe UI', 24),
    'body': ('Segoe UI', 20),
    'body_small': ('Segoe UI', 18),
    'caption': ('Segoe UI', 16),
    'button': ('Segoe UI', 20, 'bold'),
    'code': ('Consolas', 16),
}

# Store reference to current fonts
_current_fonts = FONTS

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

# Large spacing for accessibility
LARGE_SPACING = {
    'xs': 8,
    'sm': 12,
    'md': 24,
    'lg': 32,
    'xl': 48,
    'xxl': 64,
    '3xl': 80,
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
    
    if mode not in ("dark", "light", "high_contrast"):
        mode = "dark"
    
    _current_mode = mode
    
    if mode == "dark":
        COLORS.clear()
        COLORS.update(DARK_COLORS)
    elif mode == "light":
        COLORS.clear()
        COLORS.update(LIGHT_COLORS)
    elif mode == "high_contrast":
        COLORS.clear()
        COLORS.update(HIGH_CONTRAST_COLORS)


def toggle_theme() -> str:
    """Toggle between dark and light theme. Returns new mode."""
    new_mode = "light" if _current_mode == "dark" else "dark"
    set_theme_mode(new_mode)
    return new_mode


def apply_theme(ctk):
    """Apply custom theme to CustomTkinter."""
    ctk.set_appearance_mode(_current_mode if _current_mode != "high_contrast" else "dark")
    ctk.set_default_color_theme("blue")


def is_accessibility_mode() -> bool:
    """Check if accessibility mode is enabled."""
    return _accessibility_mode


def set_accessibility_mode(enabled: bool):
    """Enable or disable accessibility mode."""
    global _accessibility_mode, COLORS
    _accessibility_mode = enabled
    
    if enabled:
        set_theme_mode("high_contrast")
    else:
        set_theme_mode("dark")


def is_large_text() -> bool:
    """Check if large text mode is enabled."""
    return _large_text


def set_large_text(enabled: bool):
    """Enable or disable large text mode."""
    global _large_text, FONTS, _current_fonts
    _large_text = enabled
    
    if enabled:
        _current_fonts = LARGE_FONTS
        FONTS.clear()
        FONTS.update(LARGE_FONTS)
    else:
        _current_fonts = FONTS
        # Restore default fonts
        FONTS.clear()
        FONTS.update({
            'heading_large': ('Segoe UI Display', 40, 'bold'),
            'heading': ('Segoe UI Display', 28, 'bold'),
            'subheading': ('Segoe UI', 20, 'bold'),
            'body_large': ('Segoe UI', 18),
            'body': ('Segoe UI', 15),
            'body_small': ('Segoe UI', 13),
            'caption': ('Segoe UI', 11),
            'button': ('Segoe UI', 15, 'bold'),
            'code': ('Consolas', 12),
        })


def get_current_fonts() -> dict:
    """Get the current font configuration."""
    return _current_fonts.copy()


def get_touch_target_size() -> int:
    """Get minimum touch target size for accessibility (48px recommended)."""
    return 56 if _accessibility_mode else 44
