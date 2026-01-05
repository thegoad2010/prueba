from gtts import gTTS
import os
from mutagen.mp3 import MP3

def generate_audio_gtts(text, language, output_path, title=None, author=None):
    """
    Generates MP3 using Google Text-to-Speech.
    Adds intro: "Presentamos [Title]. De [Author]."
    """
    
    # Construct Intro
    intro_text = ""
    # Map language to intro phrase
    # Simple mapping for common languages, fallback to English or Spanish
    
    phrases = {
        'es': ("Presentamos", "De"),
        'en': ("Presenting", "By"),
        'fr': ("Présentant", "De"),
        'de': ("Präsentieren", "Von"),
        'it': ("Presentando", "Di"),
        'pt': ("Apresentando", "De")
    }
    
    lang_code = language.split('-')[0] # handle 'en-US' -> 'en'
    p1, p2 = phrases.get(lang_code, ("Presentamos", "De")) # Default to Spanish per prompt request context ("Presentamos...")

    safe_title = title if title else "Documento sin título"
    safe_author = author if author else "Autor desconocido"
    
    intro_text = f"{p1} {safe_title}. {p2} {safe_author}. "
    
    full_text = intro_text + text
    
    try:
        # Note: gTTS doesn't support generic 'speed' float. 
        # Only 'slow=True/False'.
        
        tts = gTTS(text=full_text, lang=language, slow=False)
        tts.save(output_path)
        
        # Calculate duration
        audio = MP3(output_path)
        return audio.info.length
    except Exception as e:
        print(f"Error generating audio: {e}")
        raise e
