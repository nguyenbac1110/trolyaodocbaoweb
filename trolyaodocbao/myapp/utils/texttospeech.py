from gtts import gTTS
import os
import playsound

class TextToSpeech:
    def __init__(self):
        self.language = 'vi'
        
    def speak(self, text):
        try:
            print("Bot:", text)
            chunks = [text[i:i+100] for i in range(0, len(text), 100)]
            
            for i, chunk in enumerate(chunks):
                filename = f"temp_audio_{i}.mp3"
                tts = gTTS(text=chunk, lang=self.language)
                tts.save(filename)
                playsound.playsound(filename)
                os.remove(filename)
        except Exception as e:
            print(f"Lỗi chuyển đổi text to speech: {str(e)}")