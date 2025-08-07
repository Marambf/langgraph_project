from langdetect import detect
from deep_translator import GoogleTranslator

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "en"

def translate_to_english(text: str) -> str:
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

def translate_from_english(text: str, target_lang: str) -> str:
    try:
        if target_lang == "en":
            return text
        return GoogleTranslator(source='en', target=target_lang).translate(text)
    except:
        return text
