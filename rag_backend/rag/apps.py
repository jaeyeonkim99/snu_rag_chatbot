from django.apps import AppConfig

from .rag_search import Ragsearch


class RagConfig(AppConfig):
    name = "rag"

    def ready(self):
        from django.conf import settings

        settings.RAG_SEARCH_INSTANCE = Ragsearch()
