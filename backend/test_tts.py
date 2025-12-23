from gtts import gTTS
import io
import base64

try:
    print("Testing gTTS...")
    text = "Hola, esto es una prueba."
    lang = "es"
    
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    b64 = base64.b64encode(audio_fp.read()).decode('utf-8')
    print("Success! Base64 length:", len(b64))
except Exception as e:
    print(f"FAILED: {e}")
