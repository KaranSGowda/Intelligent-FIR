from flask import session
import asyncio

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
        # For googletrans 3.x, we need to handle async calls
        async def translate_async():
            return await _translator.translate(text, dest=dest)
        
        # Run the async function
        result = asyncio.run(translate_async())
        return result.text if hasattr(result, 'text') else str(result)
    except Exception as e:
        # Return original text if translation fails
        return text