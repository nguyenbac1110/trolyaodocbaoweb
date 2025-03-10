import speech_recognition as sr

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def convert_speech_to_text(self):
        with sr.Microphone() as source:
            print("Đang lắng nghe...")
            audio = self.recognizer.listen(source)
            
            try:
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                print("Bạn đã nói: " + text)
                return text
            except sr.UnknownValueError:
                print("Không thể nhận dạng giọng nói")
                return None
            except sr.RequestError as e:
                print("Lỗi kết nối; {0}".format(e))
                return None 