from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('process_input/', views.process_input, name='process_input'),
]