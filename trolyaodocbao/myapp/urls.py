from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('start_listening/', views.start_listening, name='start_listening'),
    path('process_input/', views.process_input, name='process_input'),
]