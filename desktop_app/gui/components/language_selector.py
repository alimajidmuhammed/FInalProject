"""
Language Selector Component for Flight Kiosk System.
Dropdown for switching between languages.
"""
import customtkinter as ctk
from typing import Optional, Callable
import logging

from gui.theme import COLORS, FONTS, SPACING, RADIUS
from services.i18n_service import i18n, t

logger = logging.getLogger(__name__)


class LanguageSelector(ctk.CTkFrame):
    """Dropdown component for language selection."""
    
    def __init__(
        self,
        parent,
        on_change: Optional[Callable[[str], None]] = None,
        compact: bool = False
    ):
        """
        Initialize language selector.
        
        Args:
            parent: Parent widget
            on_change: Callback when language changes
            compact: If True, show only flag/icon
        """
        super().__init__(parent, fg_color="transparent")
        
        self.on_change = on_change
        self.compact = compact
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI."""
        languages = i18n.get_available_languages()
        
        # Get current language display
        current = i18n.get_language_info()
        current_text = self._get_display_text(current)
        
        # Create option menu
        values = [self._get_display_text(lang) for lang in languages]
        
        self.selector = ctk.CTkOptionMenu(
            self,
            values=values,
            command=self._on_select,
            font=FONTS['body_small'],
            fg_color=COLORS['bg_card'],
            button_color=COLORS['bg_secondary'],
            button_hover_color=COLORS['bg_hover'],
            dropdown_fg_color=COLORS['bg_card'],
            dropdown_hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_primary'],
            dropdown_text_color=COLORS['text_primary'],
            corner_radius=RADIUS['sm'],
            width=140 if not self.compact else 60,
            height=32
        )
        self.selector.set(current_text)
        self.selector.pack(fill="x")
    
    def _get_display_text(self, lang_info: dict) -> str:
        """Get display text for a language."""
        flag = self._get_flag(lang_info.get('code', 'en'))
        if self.compact:
            return flag
        return f"{flag} {lang_info.get('native', lang_info.get('name', 'Unknown'))}"
    
    def _get_flag(self, code: str) -> str:
        """Get flag emoji for language code."""
        flags = {
            'en': '🇬🇧',
            'ar': '🇸🇦',
            'ku': '🇮🇶'
        }
        return flags.get(code, '🌐')
    
    def _on_select(self, value: str):
        """Handle selection change."""
        # Find the language code from the display value
        for lang in i18n.get_available_languages():
            if self._get_display_text(lang) == value:
                code = lang['code']
                if i18n.set_language(code):
                    logger.info(f"Language changed to: {code}")
                    if self.on_change:
                        self.on_change(code)
                break
    
    def refresh(self):
        """Refresh the selector to show current language."""
        current = i18n.get_language_info()
        self.selector.set(self._get_display_text(current))


class LanguageModal(ctk.CTkFrame):
    """Full-screen language selection modal."""
    
    def __init__(self, parent, on_close: Optional[Callable] = None):
        """Initialize language modal."""
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        
        self.on_close = on_close
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=SPACING['xl'], pady=SPACING['xl'])
        
        title = ctk.CTkLabel(
            header,
            text="🌐 " + t('settings.language'),
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            header,
            text="Select your preferred language",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(pady=SPACING['sm'])
        
        # Language cards
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0)
        
        languages = i18n.get_available_languages()
        current = i18n.get_language()
        
        for i, lang in enumerate(languages):
            card = self._create_language_card(
                cards_frame,
                lang,
                is_selected=lang['code'] == current
            )
            card.grid(row=0, column=i, padx=SPACING['lg'], pady=SPACING['lg'])
    
    def _create_language_card(self, parent, lang: dict, is_selected: bool) -> ctk.CTkFrame:
        """Create a language selection card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['xl'],
            border_width=3 if is_selected else 1,
            border_color=COLORS['accent'] if is_selected else COLORS['border'],
            width=180,
            height=200
        )
        
        # Flag
        flag = self._get_flag(lang['code'])
        flag_label = ctk.CTkLabel(
            card,
            text=flag,
            font=('Segoe UI', 48)
        )
        flag_label.pack(pady=(SPACING['xl'], SPACING['md']))
        
        # Native name
        native_label = ctk.CTkLabel(
            card,
            text=lang['native'],
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        )
        native_label.pack()
        
        # English name
        name_label = ctk.CTkLabel(
            card,
            text=lang['name'],
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        name_label.pack(pady=SPACING['xs'])
        
        # Direction indicator
        direction = "← RTL" if lang['direction'] == 'rtl' else "LTR →"
        dir_label = ctk.CTkLabel(
            card,
            text=direction,
            font=FONTS['caption'],
            text_color=COLORS['text_muted']
        )
        dir_label.pack(pady=SPACING['sm'])
        
        # Make clickable
        for widget in [card, flag_label, native_label, name_label, dir_label]:
            widget.bind("<Button-1>", lambda e, c=lang['code']: self._select_language(c))
            widget.configure(cursor="hand2")
        
        return card
    
    def _get_flag(self, code: str) -> str:
        """Get flag emoji for language code."""
        flags = {
            'en': '🇬🇧',
            'ar': '🇸🇦',
            'ku': '🇮🇶'
        }
        return flags.get(code, '🌐')
    
    def _select_language(self, code: str):
        """Handle language selection."""
        if i18n.set_language(code):
            logger.info(f"Language changed to: {code}")
            if self.on_close:
                self.on_close()
