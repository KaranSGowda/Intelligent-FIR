from flask import session

try:
    from googletrans import Translator
    _translator = Translator()
except ImportError:
    _translator = None

def translate_text(text, dest_lang=None):
    if not _translator or not text:
        return text
    # Use session language if not provided
    if not dest_lang:
        dest_lang = session.get('lang', 'en')
    # googletrans expects 'en', 'hi', 'ta', 'kn', etc.
    dest = dest_lang.split('-')[0]
    try:
        result = _translator.translate(text, dest=dest)
        return result.text
    except Exception:
        return text