from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.speechtotext import SpeechToText
from .utils.texttospeech import TextToSpeech
from .actions.action import XuLyTinTuc
import json

def chat_view(request):
    return render(request, 'myapp/chat.html')

@csrf_exempt
def start_listening(request):
    stt = SpeechToText()
    text = stt.convert_speech_to_text()
    return JsonResponse({'text': text if text else ''})

@csrf_exempt
def process_input(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        xu_ly = XuLyTinTuc()
        
        # Process the input and get response
        # Add your logic here based on the input text
        
        tts = TextToSpeech()
        response = "Processed: " + text  # Replace with actual processing
        tts.speak(response)
        
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'})