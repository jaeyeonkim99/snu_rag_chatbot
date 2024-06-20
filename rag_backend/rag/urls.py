from django.urls import path

from . import views

urlpatterns = [
    path("", views.rag_chat, name="rag_chat"),
]
