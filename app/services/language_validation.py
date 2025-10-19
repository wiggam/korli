"""
Language validation service for the application.
Provides validation for supported languages across chat and lesson features.
"""

from typing import List, Dict, Optional
from enum import Enum

# Language map with OpenAI-compatible codes (removed male/female voice codes)
LANGUAGE_MAP = {
    "Afrikaans": { "code": "af-ZA" },
    "Arabic": { "code": "ar-XA" },
    "Bulgarian": { "code": "bg-BG" },
    "Catalan": { "code": "ca-ES" },
    "Chinese": { "code": "cmn-CN" },
    "Croatian": { "code": "hr-HR" },
    "Czech": { "code": "cs-CZ" },
    "Danish": { "code": "da-DK" },
    "Dutch": { "code": "nl-NL" },
    "English": { "code": "en-US" },
    "Filipino": { "code": "fil-PH" },
    "Finnish": { "code": "fi-FI" },
    "French": { "code": "fr-FR" },
    "German": { "code": "de-DE" },
    "Greek": { "code": "el-GR" },
    "Hebrew": { "code": "he-IL" },
    "Hindi": { "code": "hi-IN" },
    "Hungarian": { "code": "hu-HU" },
    "Indonesian": { "code": "id-ID" },
    "Italian": { "code": "it-IT" },
    "Japanese": { "code": "ja-JP" },
    "Korean": { "code": "ko-KR" },
    "Malay": { "code": "ms-MY" },
    "Norwegian": { "code": "nb-NO" },
    "Polish": { "code": "pl-PL" },
    "Portuguese (Portugal)": { "code": "pt-PT" },
    "Portuguese (Brazil)": { "code": "pt-BR" },
    "Romanian": { "code": "ro-RO" },
    "Russian": { "code": "ru-RU" },
    "Slovak": { "code": "sk-SK" },
    "Spanish (Spain)": { "code": "es-ES" },
    "Spanish (Mexico)": { "code": "es-MX" },
    "Swedish": { "code": "sv-SE" },
    "Thai": { "code": "th-TH" },
    "Turkish": { "code": "tr-TR" },
    "Ukrainian": { "code": "uk-UA" },
    "Vietnamese": { "code": "vi-VN" },
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
        
        Args:
            language: The language name to validate (must match exactly)
            
        Returns:
            The same language name if valid
            
        Raises:
            ValueError: If language is not supported
        """
        if not language:
            raise ValueError("Language cannot be empty")
        
        # Simple lookup - no normalization needed for dropdown selections
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
