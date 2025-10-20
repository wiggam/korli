"""
Language validation service for the application.
Provides validation for supported languages across chat and lesson features.
"""

from typing import List, Dict, Optional

# Language map with OpenAI-compatible codes and simple A1/A2-friendly greetings
LANGUAGE_MAP = {
    "Afrikaans": {
        "code": "af-ZA",
        "greeting": "Hallo! Hoe gaan dit?",
        "topic": "Waaroor wil jy vandag gesels?",
    },
    "Arabic": {
        "code": "ar-XA",
        "greeting": "مرحباً! كيف حالك؟",
        "topic": "عن ماذا ترغب في التحدث اليوم؟",
    },
    "Bulgarian": {
        "code": "bg-BG",
        "greeting": "Здравей! Как си?",
        "topic": "За какво искаш да говорим днес?",
    },
    "Catalan": {
        "code": "ca-ES",
        "greeting": "Hola! Com estàs?",
        "topic": "De què t’agradaria parlar avui?",
    },
    "Chinese": {
        "code": "cmn-CN",
        "greeting": "你好！你好吗？",
        "topic": "你今天想聊什么？",
    },
    "Croatian": {
        "code": "hr-HR",
        "greeting": "Bok! Kako si?",
        "topic": "O čemu želiš razgovarati danas?",
    },
    "Czech": {
        "code": "cs-CZ",
        "greeting": "Ahoj! Jak se máš?",
        "topic": "O čem bys chtěl dnes mluvit?",
    },
    "Danish": {
        "code": "da-DK",
        "greeting": "Hej! Hvordan har du det?",
        "topic": "Hvad vil du gerne tale om i dag?",
    },
    "Dutch": {
        "code": "nl-NL",
        "greeting": "Hallo! Hoe gaat het?",
        "topic": "Waar wil je het vandaag over hebben?",
    },
    "English": {
        "code": "en-US",
        "greeting": "Hello! How are you?",
        "topic": "What would you like to talk about today?",
    },
    "Filipino": {
        "code": "fil-PH",
        "greeting": "Kumusta! Kamusta ka?",
        "topic": "Anong gusto mong pag-usapan ngayon?",
    },
    "Finnish": {
        "code": "fi-FI",
        "greeting": "Hei! Mitä kuuluu?",
        "topic": "Mistä haluaisit puhua tänään?",
    },
    "French": {
        "code": "fr-FR",
        "greeting": "Salut ! Comment ça va ?",
        "topic": "De quoi aimerais-tu parler aujourd’hui ?",
    },
    "German": {
        "code": "de-DE",
        "greeting": "Hallo! Wie geht’s?",
        "topic": "Worüber möchtest du heute sprechen?",
    },
    "Greek": {
        "code": "el-GR",
        "greeting": "Γεια σου! Τι κάνεις;",
        "topic": "Για τι θα ήθελες να μιλήσουμε σήμερα;",
    },
    "Hebrew": {
        "code": "he-IL",
        "greeting": "שלום! מה שלומך?",
        "topic": "על מה תרצה לדבר היום?",
    },
    "Hindi": {
        "code": "hi-IN",
        "greeting": "नमस्ते! आप कैसे हैं?",
        "topic": "आज आप किस बारे में बात करना चाहेंगे?",
    },
    "Hungarian": {
        "code": "hu-HU",
        "greeting": "Szia! Hogy vagy?",
        "topic": "Miről szeretnél ma beszélni?",
    },
    "Indonesian": {
        "code": "id-ID",
        "greeting": "Halo! Apa kabar?",
        "topic": "Tentang apa kamu ingin berbicara hari ini?",
    },
    "Italian": {
        "code": "it-IT",
        "greeting": "Ciao! Come stai?",
        "topic": "Di cosa ti piacerebbe parlare oggi?",
    },
    "Japanese": {
        "code": "ja-JP",
        "greeting": "こんにちは！お元気ですか？",
        "topic": "今日は何について話したいですか？",
    },
    "Korean": {
        "code": "ko-KR",
        "greeting": "안녕하세요! 잘 지내요?",
        "topic": "오늘은 어떤 이야기를 하고 싶어요?",
    },
    "Malay": {
        "code": "ms-MY",
        "greeting": "Hai! Apa khabar?",
        "topic": "Apa yang ingin anda bincangkan hari ini?",
    },
    "Norwegian": {
        "code": "nb-NO",
        "greeting": "Hei! Hvordan har du det?",
        "topic": "Hva vil du snakke om i dag?",
    },
    "Polish": {
        "code": "pl-PL",
        "greeting": "Cześć! Jak się masz?",
        "topic": "O czym chciałbyś dziś porozmawiać?",
    },
    "Portuguese (Portugal)": {
        "code": "pt-PT",
        "greeting": "Olá! Como estás?",
        "topic": "Sobre o que gostarias de falar hoje?",
    },
    "Portuguese (Brazil)": {
        "code": "pt-BR",
        "greeting": "Oi! Tudo bem?",
        "topic": "Sobre o que você gostaria de conversar hoje?",
    },
    "Romanian": {
        "code": "ro-RO",
        "greeting": "Bună! Ce mai faci?",
        "topic": "Despre ce ai vrea să vorbim astăzi?",
    },
    "Russian": {
        "code": "ru-RU",
        "greeting": "Привет! Как дела?",
        "topic": "О чём ты хотел бы поговорить сегодня?",
    },
    "Slovak": {
        "code": "sk-SK",
        "greeting": "Ahoj! Ako sa máš?",
        "topic": "O čom by si chcel dnes hovoriť?",
    },
    "Spanish (Spain)": {
        "code": "es-ES",
        "greeting": "¡Hola! ¿Cómo estás?",
        "topic": "¿De qué te gustaría hablar hoy?",
    },
    "Spanish (Mexico)": {
        "code": "es-MX",
        "greeting": "¡Hola! ¿Cómo estás?",
        "topic": "¿De qué te gustaría hablar hoy?",
    },
    "Swedish": {
        "code": "sv-SE",
        "greeting": "Hej! Hur mår du?",
        "topic": "Vad vill du prata om idag?",
    },
    "Thai": {
        "code": "th-TH",
        "greeting": "สวัสดี! สบายดีไหม?",
        "topic": "วันนี้คุณอยากคุยเรื่องอะไร?",
    },
    "Turkish": {
        "code": "tr-TR",
        "greeting": "Merhaba! Nasılsın?",
        "topic": "Bugün ne hakkında konuşmak istersin?",
    },
    "Ukrainian": {
        "code": "uk-UA",
        "greeting": "Привіт! Як справи?",
        "topic": "Про що ти хотів би сьогодні поговорити?",
    },
    "Vietnamese": {
        "code": "vi-VN",
        "greeting": "Xin chào! Bạn khỏe không?",
        "topic": "Hôm nay bạn muốn nói về điều gì?",
    },
}


class LanguageValidator:
    """Service class for language validation and management."""
    
    @staticmethod
    def get_supported_languages() -> List[str]:
        return list(LANGUAGE_MAP.keys())
    
    @staticmethod
    def is_language_supported(language: str) -> bool:
        return language in LANGUAGE_MAP
    
    @staticmethod
    def validate_language(language: str) -> str:
        if not language:
            raise ValueError("Language cannot be empty")
        if not LanguageValidator.is_language_supported(language):
            supported = ", ".join(LanguageValidator.get_supported_languages())
            raise ValueError(f"Language '{language}' is not supported. Supported: {supported}")
        return language
    
    @staticmethod
    def get_language_code(language: str) -> Optional[str]:
        validated = LanguageValidator.validate_language(language)
        return LANGUAGE_MAP.get(validated, {}).get("code")

    @staticmethod
    def get_language_greeting(language: str) -> Optional[str]:
        validated = LanguageValidator.validate_language(language)
        return LANGUAGE_MAP.get(validated, {}).get("greeting")

    @staticmethod
    def get_language_topic(language: str) -> Optional[str]:
        validated = LanguageValidator.validate_language(language)
        return LANGUAGE_MAP.get(validated, {}).get("topic")


# Convenience functions
def validate_language(language: str) -> str:
    return LanguageValidator.validate_language(language)

def is_language_supported(language: str) -> bool:
    return LanguageValidator.is_language_supported(language)

def get_supported_languages() -> List[str]:
    return LanguageValidator.get_supported_languages()

def get_language_greeting(language: str) -> Optional[str]:
    return LanguageValidator.get_language_greeting(language)

def get_language_topic(language: str) -> Optional[str]:
    return LanguageValidator.get_language_topic(language)
