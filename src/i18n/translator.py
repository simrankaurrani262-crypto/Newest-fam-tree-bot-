"""
Internationalization Translator
"""
from typing import Dict, Optional
import json
from pathlib import Path

from src.config.settings import settings


class Translator:
    """Translation manager"""
    
    def __init__(self):
        self.translations: Dict[str, Dict] = {}
        self.default_lang = settings.DEFAULT_LANGUAGE
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files"""
        locales_dir = Path(__file__).parent / "locales"
        
        for lang in settings.SUPPORTED_LANGUAGES:
            file_path = locales_dir / lang / "messages.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
    
    def translate(
        self,
        key: str,
        lang: str = None,
        **kwargs
    ) -> str:
        """
        Translate a key to the specified language
        
        Args:
            key: Translation key (dot notation)
            lang: Target language code
            **kwargs: Format arguments
        
        Returns:
            Translated string
        """
        lang = lang or self.default_lang
        
        # Get translation
        translation = self.translations.get(lang, {})
        
        # Navigate nested keys
        keys = key.split('.')
        for k in keys:
            translation = translation.get(k, key)
            if not isinstance(translation, dict):
                break
        
        # Format if string
        if isinstance(translation, str):
            return translation.format(**kwargs)
        
        # Fallback to key if translation not found
        return key
    
    def get(self, key: str, lang: str = None) -> str:
        """Alias for translate"""
        return self.translate(key, lang)


# Global translator instance
translator = Translator()


def get_translator() -> Translator:
    """Get translator instance"""
    return translator
