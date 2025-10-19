"""
Language validation service for the application.
Provides validation for supported languages across chat and lesson features.
"""

from typing import List, Dict, Optional

# Language map with OpenAI-compatible codes (removed male/female voice codes)
LANGUAGE_MAP = {
    "Afrikaans": {"code": "af-ZA", "greeting": "Hallo! Hoe gaan dit?"},
    "Arabic": {"code": "ar-XA", "greeting": "مرحباً! كيف حالك؟"},
    "Bulgarian": {"code": "bg-BG", "greeting": "Здравей! Как си?"},
    "Catalan": {"code": "ca-ES", "greeting": "Hola! Com estàs?"},
    "Chinese": {"code": "cmn-CN", "greeting": "你好！你好吗？"},
    "Croatian": {"code": "hr-HR", "greeting": "Bok! Kako si?"},
    "Czech": {"code": "cs-CZ", "greeting": "Ahoj! Jak se máš?"},
    "Danish": {"code": "da-DK", "greeting": "Hej! Hvordan har du det?"},
    "Dutch": {"code": "nl-NL", "greeting": "Hallo! Hoe gaat het?"},
    "English": {"code": "en-US", "greeting": "Hello! How are you?"},
    "Filipino": {"code": "fil-PH", "greeting": "Kumusta! Kamusta ka?"},
    "Finnish": {"code": "fi-FI", "greeting": "Hei! Mitä kuuluu?"},
    "French": {"code": "fr-FR", "greeting": "Salut ! Comment ça va ?"},
    "German": {"code": "de-DE", "greeting": "Hallo! Wie geht’s?"},
    "Greek": {"code": "el-GR", "greeting": "Γεια σου! Τι κάνεις;"},
    "Hebrew": {"code": "he-IL", "greeting": "שלום! מה שלומך?"},
    "Hindi": {"code": "hi-IN", "greeting": "नमस्ते! आप कैसे हैं?"},
    "Hungarian": {"code": "hu-HU", "greeting": "Szia! Hogy vagy?"},
    "Indonesian": {"code": "id-ID", "greeting": "Halo! Apa kabar?"},
    "Italian": {"code": "it-IT", "greeting": "Ciao! Come stai?"},
    "Japanese": {"code": "ja-JP", "greeting": "こんにちは！お元気ですか？"},
    "Korean": {"code": "ko-KR", "greeting": "안녕하세요! 잘 지내요?"},
    "Malay": {"code": "ms-MY", "greeting": "Hai! Apa khabar?"},
    "Norwegian": {"code": "nb-NO", "greeting": "Hei! Hvordan har du det?"},
    "Polish": {"code": "pl-PL", "greeting": "Cześć! Jak się masz?"},
    "Portuguese (Portugal)": {"code": "pt-PT", "greeting": "Olá! Como estás?"},
    "Portuguese (Brazil)": {"code": "pt-BR", "greeting": "Oi! Tudo bem?"},
    "Romanian": {"code": "ro-RO", "greeting": "Bună! Ce mai faci?"},
    "Russian": {"code": "ru-RU", "greeting": "Привет! Как дела?"},
    "Slovak": {"code": "sk-SK", "greeting": "Ahoj! Ako sa máš?"},
    "Spanish (Spain)": {"code": "es-ES", "greeting": "¡Hola! ¿Cómo estás?"},
    "Spanish (Mexico)": {"code": "es-MX", "greeting": "¡Hola! ¿Cómo estás?"},
    "Swedish": {"code": "sv-SE", "greeting": "Hej! Hur mår du?"},
    "Thai": {"code": "th-TH", "greeting": "สวัสดี! สบายดีไหม?"},
    "Turkish": {"code": "tr-TR", "greeting": "Merhaba! Nasılsın?"},
    "Ukrainian": {"code": "uk-UA", "greeting": "Привіт! Як справи?"},
    "Vietnamese": {"code": "vi-VN", "greeting": "Xin chào! Bạn khỏe không?"},
}


class LanguageValidator:
    """Service class for language validation and management."""
    
    @staticmethod
    def get_supported_languages() -> List[str]:
        """Get list of all supported language names."""
        return list(LANGUAGE_MAP.keys())
    
    @staticmethod
    def is_language_supported(language: str) -> bool:
        """Check if a language is supported."""
        return language in LANGUAGE_MAP
    
    @staticmethod
    def validate_language(language: str) -> str:
        """
        Validate a language name against supported languages.
        Returns the same language name if valid, otherwise raises ValueError.
        """
        if not language:
            raise ValueError("Language cannot be empty")
        
        if not LanguageValidator.is_language_supported(language):
            supported_languages = LanguageValidator.get_supported_languages()
            raise ValueError(
                f"Language '{language}' is not supported. "
                f"Supported languages: {', '.join(supported_languages)}"
            )
        
        return language
    
    @staticmethod
    def get_language_code(language: str) -> Optional[str]:
        """Get the OpenAI language code for a given language name."""
        validated_language = LanguageValidator.validate_language(language)
        return LANGUAGE_MAP.get(validated_language, {}).get("code")

    @staticmethod
    def get_language_greeting(language: str) -> Optional[str]:
        """Get the default greeting in the given language."""
        validated_language = LanguageValidator.validate_language(language)
        return LANGUAGE_MAP.get(validated_language, {}).get("greeting")


# Convenience functions for easy importing
def validate_language(language: str) -> str:
    """Convenience function for language validation."""
    return LanguageValidator.validate_language(language)

def is_language_supported(language: str) -> bool:
    """Convenience function to check if language is supported."""
    return LanguageValidator.is_language_supported(language)

def get_supported_languages() -> List[str]:
    """Convenience function to get all supported languages."""
    return LanguageValidator.get_supported_languages()

def get_language_greeting(language: str) -> Optional[str]:
    """Convenience function to get the default greeting in a given language."""
    return LanguageValidator.get_language_greeting(language)
