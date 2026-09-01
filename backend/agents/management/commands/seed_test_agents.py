from django.core.management.base import BaseCommand

from agents.crypto import encrypt_secret
from agents.models import Agent


TEST_AGENTS = [
    {
        "name": "Gemini Flash (Gratis)",
        "agent_type": "chat",
        "provider": "google",
        "model": "gemini-2.0-flash",
        "description": "Gratis — 15 RPM via AI Studio. Recomendado RAG.",
        "temperature": 0.2,
        "max_tokens": 1024,
        "top_k": 5,
        "is_active": False,
        "is_fallback": False,
        "fallback_order": 0,
    },
    {
        "name": "Groq Llama 3.3 (Gratis)",
        "agent_type": "chat",
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "description": "Gratis — 14k tokens/min sin tarjeta. Muy rápido.",
        "temperature": 0.3,
        "max_tokens": 1024,
        "top_k": 5,
        "is_active": False,
        "is_fallback": True,
        "fallback_order": 1,
    },
    {
        "name": "Mistral Small (Gratis trial)",
        "agent_type": "chat",
        "provider": "mistral",
        "model": "mistral-small-latest",
        "description": "Gratis con trial $5 — bueno y barato.",
        "temperature": 0.2,
        "max_tokens": 1024,
        "top_k": 5,
        "is_active": False,
        "is_fallback": True,
        "fallback_order": 2,
    },
    {
        "name": "OpenRouter Llama (Gratis)",
        "agent_type": "chat",
        "provider": "openrouter",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "description": "Gratis via OpenRouter :free — sin tarjeta.",
        "temperature": 0.2,
        "max_tokens": 1024,
        "top_k": 5,
        "is_active": False,
        "is_fallback": True,
        "fallback_order": 3,
    },
    {
        "name": "Ollama Local (Gratis 100%)",
        "agent_type": "chat",
        "provider": "ollama",
        "model": "llama3.2",
        "base_url": "http://host.docker.internal:11434/v1",
        "description": "100% gratis local — sin API key. Requiere Ollama instalado.",
        "temperature": 0.2,
        "max_tokens": 1024,
        "top_k": 5,
        "is_active": False,
        "is_fallback": True,
        "fallback_order": 4,
    },
    {
        "name": "Embeddings Gemini (Gratis)",
        "agent_type": "embedding",
        "provider": "google",
        "model": "text-embedding-004",
        "description": "Embeddings gratis 768 dims via Google.",
        "embedding_dim": 768,
        "is_active": False,
        "is_fallback": False,
    },
    {
        "name": "Embeddings Mistral (Gratis trial)",
        "agent_type": "embedding",
        "provider": "mistral",
        "model": "mistral-embed",
        "description": "Embeddings Mistral 1024 dims.",
        "embedding_dim": 1024,
        "is_active": False,
        "is_fallback": True,
        "fallback_order": 1,
    },
    {
        "name": "Embeddings Local (Gratis)",
        "agent_type": "embedding",
        "provider": "ollama",
        "model": "nomic-embed-text",
        "base_url": "http://host.docker.internal:11434/v1",
        "description": "Local gratis — nomic-embed-text 768 dims.",
        "embedding_dim": 768,
        "is_active": False,
        "is_fallback": True,
        "fallback_order": 2,
    },
    {
        "name": "Re-ranker Default",
        "agent_type": "reranker",
        "provider": "google",
        "model": "gemini-2.0-flash-lite",
        "description": "Re-ranking barato con Gemini lite.",
        "top_k": 5,
        "is_active": False,
        "is_fallback": False,
    },
]


class Command(BaseCommand):
    help = "Crea agentes de prueba gratuitos (no sobrescribe existentes por nombre)."

    def add_arguments(self, parser):
        parser.add_argument("--force-active", action="store_true", help="Activa el primer chat y embedding")

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        for data in TEST_AGENTS:
            if Agent.objects.filter(name=data["name"]).exists():
                skipped += 1
                continue
            Agent.objects.create(**data)
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Creado: {data['name']} [{data['provider']}/{data['model']}]"))

        if options["force_active"]:
            # Activa el primer chat y embedding si ninguno está activo
            if not Agent.objects.filter(agent_type="chat", is_active=True).exists():
                first_chat = Agent.objects.filter(agent_type="chat").first()
                if first_chat:
                    first_chat.is_active = True
                    first_chat.save(update_fields=["is_active"])
                    self.stdout.write(self.style.WARNING(f"Activado: {first_chat.name}"))
            if not Agent.objects.filter(agent_type="embedding", is_active=True).exists():
                first_emb = Agent.objects.filter(agent_type="embedding").first()
                if first_emb:
                    first_emb.is_active = True
                    first_emb.save(update_fields=["is_active"])
                    self.stdout.write(self.style.WARNING(f"Activado: {first_emb.name}"))

        self.stdout.write(self.style.SUCCESS(f"Done — creados: {created}, ya existían: {skipped}"))
