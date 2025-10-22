"""
Language validation service for the application.
Provides validation for supported languages across chat and lesson features.
"""

from typing import List, Dict, Optional

# Language map with ISO 639-1 codes for OpenAI Whisper STT and simple A1/A2-friendly greetings
LANGUAGE_MAP = {
    "Afrikaans": {
        "code": "af",
        "greeting": "Hallo! Hoe gaan dit?",
        "topic": "Waaroor wil jy vandag gesels?",
    },
    "Arabic": {
        "code": "ar",
        "greeting": "مرحباً! كيف حالك؟",
        "topic": "عن ماذا ترغب في التحدث اليوم؟",
    },
    "Bulgarian": {
        "code": "bg",
        "greeting": "Здравей! Как си?",
        "topic": "За какво искаш да говорим днес?",
    },
    "Catalan": {
        "code": "ca",
        "greeting": "Hola! Com estàs?",
        "topic": "De què t'agradaria parlar avui?",
    },
    "Chinese": {
        "code": "zh",
        "greeting": "你好！你好吗？",
        "topic": "你今天想聊什么？",
    },
    "Croatian": {
        "code": "hr",
        "greeting": "Bok! Kako si?",
        "topic": "O čemu želiš razgovarati danas?",
    },
    "Czech": {
        "code": "cs",
        "greeting": "Ahoj! Jak se máš?",
        "topic": "O čem bys chtěl dnes mluvit?",
    },
    "Danish": {
        "code": "da",
        "greeting": "Hej! Hvordan har du det?",
        "topic": "Hvad vil du gerne tale om i dag?",
    },
    "Dutch": {
        "code": "nl",
        "greeting": "Hallo! Hoe gaat het?",
        "topic": "Waar wil je het vandaag over hebben?",
    },
    "English": {
        "code": "en",
        "greeting": "Hello! How are you?",
        "topic": "What would you like to talk about today?",
    },
    "Filipino": {
        "code": "tl",  # Filipino uses Tagalog code
        "greeting": "Kumusta! Kamusta ka?",
        "topic": "Anong gusto mong pag-usapan ngayon?",
    },
    "Finnish": {
        "code": "fi",
        "greeting": "Hei! Mitä kuuluu?",
        "topic": "Mistä haluaisit puhua tänään?",
    },
    "French": {
        "code": "fr",
        "greeting": "Salut ! Comment ça va ?",
        "topic": "De quoi aimerais-tu parler aujourd'hui ?",
    },
    "German": {
        "code": "de",
        "greeting": "Hallo! Wie geht's?",
        "topic": "Worüber möchtest du heute sprechen?",
    },
    "Greek": {
        "code": "el",
        "greeting": "Γεια σου! Τι κάνεις;",
        "topic": "Για τι θα ήθελες να μιλήσουμε σήμερα;",
    },
    "Hebrew": {
        "code": "he",
        "greeting": "שלום! מה שלומך?",
        "topic": "על מה תרצה לדבר היום?",
    },
    "Hindi": {
        "code": "hi",
        "greeting": "नमस्ते! आप कैसे हैं?",
        "topic": "आज आप किस बारे में बात करना चाहेंगे?",
    },
    "Hungarian": {
        "code": "hu",
        "greeting": "Szia! Hogy vagy?",
        "topic": "Miről szeretnél ma beszélni?",
    },
    "Indonesian": {
        "code": "id",
        "greeting": "Halo! Apa kabar?",
        "topic": "Tentang apa kamu ingin berbicara hari ini?",
    },
    "Italian": {
        "code": "it",
        "greeting": "Ciao! Come stai?",
        "topic": "Di cosa ti piacerebbe parlare oggi?",
    },
    "Japanese": {
        "code": "ja",
        "greeting": "こんにちは！お元気ですか？",
        "topic": "今日は何について話したいですか？",
    },
    "Korean": {
        "code": "ko",
        "greeting": "안녕하세요! 잘 지내요?",
        "topic": "오늘은 어떤 이야기를 하고 싶어요?",
    },
    "Malay": {
        "code": "ms",
        "greeting": "Hai! Apa khabar?",
        "topic": "Apa yang ingin anda bincangkan hari ini?",
    },
    "Norwegian": {
        "code": "no",
        "greeting": "Hei! Hvordan har du det?",
        "topic": "Hva vil du snakke om i dag?",
    },
    "Polish": {
        "code": "pl",
        "greeting": "Cześć! Jak się masz?",
        "topic": "O czym chciałbyś dziś porozmawiać?",
    },
    "Portuguese (Portugal)": {
        "code": "pt",
        "greeting": "Olá! Como estás?",
        "topic": "Sobre o que gostarias de falar hoje?",
    },
    "Portuguese (Brazil)": {
        "code": "pt",
        "greeting": "Oi! Tudo bem?",
        "topic": "Sobre o que você gostaria de conversar hoje?",
    },
    "Romanian": {
        "code": "ro",
        "greeting": "Bună! Ce mai faci?",
        "topic": "Despre ce ai vrea să vorbim astăzi?",
    },
    "Russian": {
        "code": "ru",
        "greeting": "Привет! Как дела?",
        "topic": "О чём ты хотел бы поговорить сегодня?",
    },
    "Slovak": {
        "code": "sk",
        "greeting": "Ahoj! Ako sa máš?",
        "topic": "O čom by si chcel dnes hovoriť?",
    },
    "Spanish (Spain)": {
        "code": "es",
        "greeting": "¡Hola! ¿Cómo estás?",
        "topic": "¿De qué te gustaría hablar hoy?",
    },
    "Spanish (Mexico)": {
        "code": "es",
        "greeting": "¡Hola! ¿Cómo estás?",
        "topic": "¿De qué te gustaría hablar hoy?",
    },
    "Swedish": {
        "code": "sv",
        "greeting": "Hej! Hur mår du?",
        "topic": "Vad vill du prata om idag?",
    },
    "Thai": {
        "code": "th",
        "greeting": "สวัสดี! สบายดีไหม?",
        "topic": "วันนี้คุณอยากคุยเรื่องอะไร?",
    },
    "Turkish": {
        "code": "tr",
        "greeting": "Merhaba! Nasılsın?",
        "topic": "Bugün ne hakkında konuşmak istersin?",
    },
    "Ukrainian": {
        "code": "uk",
        "greeting": "Привіт! Як справи?",
        "topic": "Про що ти хотів би сьогодні поговорити?",
    },
    "Vietnamese": {
        "code": "vi",
        "greeting": "Xin chào! Bạn khỏe không?",
        "topic": "Hôm nay bạn muốn nói về điều gì?",
    },
    "Armenian": {
        "code": "hy",
        "greeting": "Բարև! Ինչպե՞ս ես:",
        "topic": "Որի մասին կցանկանայիր խոսել այսօր:",
    },
    "Azerbaijani": {
        "code": "az",
        "greeting": "Salam! Necəsən?",
        "topic": "Bu gün nə haqqında danışmaq istərdiniz?",
    },
    "Belarusian": {
        "code": "be",
        "greeting": "Прывітанне! Як справы?",
        "topic": "Пра што ты хацеў бы пагаварыць сёння?",
    },
    "Bosnian": {
        "code": "bs",
        "greeting": "Zdravo! Kako si?",
        "topic": "O čemu želiš razgovarati danas?",
    },
    "Estonian": {
        "code": "et",
        "greeting": "Tere! Kuidas läheb?",
        "topic": "Millest sa tahaksid täna rääkida?",
    },
    "Galician": {
        "code": "gl",
        "greeting": "Ola! Como estás?",
        "topic": "De que che gustaría falar hoxe?",
    },
    "Icelandic": {
        "code": "is",
        "greeting": "Halló! Hvernig hefurðu það?",
        "topic": "Um hvað viltu tala í dag?",
    },
    "Kannada": {
        "code": "kn",
        "greeting": "ನಮಸ್ಕಾರ! ನೀವು ಹೇಗಿದ್ದೀರಿ?",
        "topic": "ಇಂದು ನೀವು ಯಾವ ವಿಷಯದ ಬಗ್ಗೆ ಮಾತನಾಡಲು ಬಯಸುತ್ತೀರಿ?",
    },
    "Kazakh": {
        "code": "kk",
        "greeting": "Сәлем! Қалың қалай?",
        "topic": "Бүгін не туралы сөйлескіңіз келеді?",
    },
    "Latvian": {
        "code": "lv",
        "greeting": "Sveiki! Kā iet?",
        "topic": "Par ko tu vēlētos runāt šodien?",
    },
    "Lithuanian": {
        "code": "lt",
        "greeting": "Labas! Kaip sekasi?",
        "topic": "Apie ką norėtum šiandien pakalbėti?",
    },
    "Macedonian": {
        "code": "mk",
        "greeting": "Здраво! Како си?",
        "topic": "За што сакаш да зборуваме денес?",
    },
    "Marathi": {
        "code": "mr",
        "greeting": "नमस्कार! तू कसा आहेस?",
        "topic": "आज तुम्हाला कशाबद्दल बोलायचे आहे?",
    },
    "Maori": {
        "code": "mi",
        "greeting": "Kia ora! Kei te pēhea koe?",
        "topic": "He aha tāu e hiahia ana ki te kōrero i tēnei rā?",
    },
    "Nepali": {
        "code": "ne",
        "greeting": "नमस्ते! तपाईं कस्तो हुनुहुन्छ?",
        "topic": "आज तपाईं के बारेमा कुरा गर्न चाहनुहुन्छ?",
    },
    "Persian": {
        "code": "fa",
        "greeting": "سلام! حال شما چطور است؟",
        "topic": "امروز می‌خواهید در مورد چه چیزی صحبت کنید؟",
    },
    "Serbian": {
        "code": "sr",
        "greeting": "Здраво! Како си?",
        "topic": "О чему желиш да причамо данас?",
    },
    "Slovenian": {
        "code": "sl",
        "greeting": "Živjo! Kako si?",
        "topic": "O čem bi rad govoril danes?",
    },
    "Swahili": {
        "code": "sw",
        "greeting": "Habari! Habari gani?",
        "topic": "Ungependa kuzungumza kuhusu nini leo?",
    },
    "Tagalog": {
        "code": "tl",
        "greeting": "Kumusta! Kumusta ka?",
        "topic": "Anong gusto mong pag-usapan ngayon?",
    },
    "Tamil": {
        "code": "ta",
        "greeting": "வணக்கம்! எப்படி இருக்கிறீர்கள்?",
        "topic": "இன்று நீங்கள் எதைப் பற்றி பேச விரும்புகிறீர்கள்?",
    },
    "Urdu": {
        "code": "ur",
        "greeting": "السلام علیکم! آپ کیسے ہیں؟",
        "topic": "آج آپ کس بارے میں بات کرنا چاہیں گے؟",
    },
    "Welsh": {
        "code": "cy",
        "greeting": "Helo! Sut wyt ti?",
        "topic": "Am beth hoffet ti siarad heddiw?",
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
