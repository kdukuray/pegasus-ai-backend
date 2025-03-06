from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_api, name="chat_api"),
    path("/thread/messages/<chat_thread_id>", views.get_chat_thread_messages, name="get_chat_thread_messages"),
    path("/threads", views.get_chat_threads, name="get_chat_threads"),
]