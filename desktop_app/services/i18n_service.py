"""
Internationalization (i18n) Service for Flight Kiosk System.
Provides multi-language support with RTL/LTR handling.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import logging

logger = logging.getLogger(__name__)


class I18nService:
    """Internationalization service for managing translations."""
    
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'native': 'English', 'direction': 'ltr'},
        'ar': {'name': 'Arabic', 'native': 'العربية', 'direction': 'rtl'},
        'ku': {'name': 'Kurdish', 'native': 'کوردی', 'direction': 'rtl'},
    }
    
    def __init__(self):
        """Initialize the i18n service."""
        self.current_language = 'en'
        self.translations: Dict[str, Dict] = {}
        self._listeners: List[Callable] = []
        self._locales_dir = Path(__file__).parent.parent / 'locales'
        self._load_all_translations()
    
    def _load_all_translations(self):
        """Load all translation files."""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            self._load_translation(lang_code)
    
    def _load_translation(self, lang_code: str) -> bool:
        """Load a specific translation file."""
        file_path = self._locales_dir / f'{lang_code}.json'
        
        if not file_path.exists():
            logger.warning(f"Translation file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
            logger.info(f"Loaded translations for: {lang_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to load translations for {lang_code}: {e}")
            return False
    
    def set_language(self, lang_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            lang_code: Language code (en, ar, ku)
            
        Returns:
            True if language was set successfully
        """
        if lang_code not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language: {lang_code}")
            return False
        
        if lang_code not in self.translations:
            if not self._load_translation(lang_code):
                return False
        
        old_language = self.current_language
        self.current_language = lang_code
        
        # Notify listeners of language change
        if old_language != lang_code:
            self._notify_listeners()
        
        return True
    
    def get_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def get_direction(self) -> str:
        """Get the text direction for current language (ltr or rtl)."""
        return self.SUPPORTED_LANGUAGES.get(
            self.current_language, {}
        ).get('direction', 'ltr')
    
    def is_rtl(self) -> bool:
        """Check if current language is RTL."""
        return self.get_direction() == 'rtl'
    
    def get_language_info(self, lang_code: Optional[str] = None) -> Dict:
        """Get information about a language."""
        code = lang_code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(code, {})
    
    def get_available_languages(self) -> List[Dict]:
        """Get list of available languages with their info."""
        return [
            {'code': code, **info}
            for code, info in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current language.
        
        Args:
            key: Dot-notation key (e.g., 'nav.home', 'booking.title')
            **kwargs: Variables to interpolate (e.g., name='John')
            
        Returns:
            Translated string or the key if not found
        """
        # Get current language translations
        translations = self.translations.get(self.current_language, {})
        
        # Navigate the nested structure
        value = self._get_nested(translations, key)
        
        # Fallback to English if not found
        if value is None and self.current_language != 'en':
            english = self.translations.get('en', {})
            value = self._get_nested(english, key)
        
        # Return key if still not found
        if value is None:
            logger.debug(f"Translation not found: {key}")
            return key
        
        # Interpolate variables
        if kwargs:
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing interpolation variable for {key}: {e}")
        
        return value
    
    def _get_nested(self, data: Dict, key: str) -> Optional[str]:
        """Get a value from nested dict using dot notation."""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def add_listener(self, callback: Callable):
        """Add a listener for language changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Remove a language change listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self):
        """Notify all listeners of language change."""
        for callback in self._listeners:
            try:
                callback(self.current_language)
            except Exception as e:
                logger.error(f"Error in language change listener: {e}")


# Global i18n service instance
i18n = I18nService()


# Convenience function for translations
def t(key: str, **kwargs) -> str:
    """Shortcut for i18n.t()"""
    return i18n.t(key, **kwargs)
