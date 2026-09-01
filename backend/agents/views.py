from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.embeddings import EmbeddingService
from core.llm import LLMService
from core.providers import EMBEDDING_PROVIDERS, KEYLESS_PROVIDERS, is_client_error
from django.conf import settings

from .models import Agent, AgentType
from .serializers import AgentSerializer, PlatformConfigSerializer
from .services import PLATFORM_DEFAULTS, get_platform_config, save_platform_config


class AgentViewSet(ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete", "put"]

    @action(detail=False, methods=["get"])
    def active(self, request):
        agents = Agent.objects.filter(is_active=True)
        return Response(AgentSerializer(agents, many=True).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        agent = self.get_object()
        Agent.objects.filter(agent_type=agent.agent_type, is_active=True).exclude(pk=agent.pk).update(is_active=False)
        agent.is_active = True
        agent.save(update_fields=["is_active", "updated_at"])
        return Response(AgentSerializer(agent).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        agent = self.get_object()
        agent.is_active = False
        agent.save(update_fields=["is_active", "updated_at"])
        return Response(AgentSerializer(agent).data)

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        agent = self.get_object()
        probe = (request.data.get("probe") or "").strip() or "Prueba de conexión del agente."
        if agent.agent_type in (AgentType.CHAT, AgentType.EMBEDDING):
            if agent.agent_type == AgentType.EMBEDDING and agent.provider not in EMBEDDING_PROVIDERS:
                return Response(
                    {
                        "ok": False,
                        "error": f"El proveedor «{agent.provider}» no ofrece embeddings. "
                        "Usa OpenAI, Google, Mistral u Ollama para el agente de embeddings.",
                    }
                )
            api_key = agent.api_key_plain
            needs_key = agent.provider not in KEYLESS_PROVIDERS
            if needs_key and not api_key:
                return Response(
                    {
                        "ok": False,
                        "error": "Este agente no tiene su propia API key. "
                        "Cada agente usa una clave exclusiva: configúrala en el campo «API Key».",
                    }
                )
        try:
            if agent.agent_type == AgentType.CHAT:
                llm = LLMService(
                    provider=agent.provider,
                    api_key=api_key,
                    base_url=agent.base_url,
                    use_breaker=False,
                )
                response = llm.chat_completion(
                    messages=[
                        {"role": "system", "content": "Eres un agente de prueba. Responde en una frase."},
                        {"role": "user", "content": probe},
                    ],
                    model=agent.model,
                    temperature=agent.temperature,
                    max_tokens=128,
                    retries=1,
                )
                return Response(
                    {"ok": True, "response": response["content"], "tokens": response["completion_tokens"]}
                )
            if agent.agent_type == AgentType.EMBEDDING:
                service = EmbeddingService(
                    model=agent.model,
                    batch_size=1,
                    provider=agent.provider,
                    api_key=api_key,
                    base_url=agent.base_url,
                    use_breaker=False,
                )
                vectors = service.embed_texts([probe], retries=1)
                return Response({"ok": True, "dim": len(vectors[0]), "sample": vectors[0][:3]})
            return Response(
                {"ok": True, "response": "Agente de re-ranking verificado (requiere pipeline para medir)."}
            )
        except Exception as exc:
            response_status = status.HTTP_200_OK if is_client_error(exc) else status.HTTP_502_BAD_GATEWAY
            return Response({"ok": False, "error": str(exc)[:500]}, status=response_status)


class TestConfigView(APIView):
    """Probar una configuración sin guardarla: útil para el botón 'Probar API' del formulario."""

    def post(self, request):
        provider = (request.data.get("provider") or "openai").strip()
        model = (request.data.get("model") or "").strip()
        api_key = (request.data.get("api_key") or "").strip()
        base_url = (request.data.get("base_url") or "").strip()
        agent_type = (request.data.get("agent_type") or "chat").strip()
        temperature = request.data.get("temperature", 0.2)
        max_tokens = request.data.get("max_tokens", 128)
        embedding_dim = request.data.get("embedding_dim", 1536)
        probe = (request.data.get("probe") or "").strip() or "Prueba de conexión del agente."

        if not model:
            return Response({"ok": False, "error": "Indica un modelo (ej. gpt-4o-mini, gemini-2.0-flash, llama-3.3-70b-versatile)."}, status=status.HTTP_400_BAD_REQUEST)
        if agent_type == "embedding" and provider not in EMBEDDING_PROVIDERS:
            return Response(
                {"ok": False, "error": f"El proveedor «{provider}» no ofrece embeddings. Usa OpenAI, Google, Mistral u Ollama."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if provider not in KEYLESS_PROVIDERS and not api_key:
            return Response(
                {"ok": False, "error": f"Falta API key para {provider}. Obtén una en el catálogo de modelos gratuitos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if agent_type == AgentType.CHAT or agent_type == "chat":
                llm = LLMService(provider=provider, api_key=api_key, base_url=base_url, use_breaker=False)
                response = llm.chat_completion(
                    messages=[
                        {"role": "system", "content": "Eres un agente de prueba. Responde en una frase."},
                        {"role": "user", "content": probe},
                    ],
                    model=model,
                    temperature=float(temperature) if temperature is not None else 0.2,
                    max_tokens=int(max_tokens) if max_tokens else 128,
                    retries=1,
                )
                return Response({"ok": True, "response": response["content"], "tokens": response["completion_tokens"], "model": model, "provider": provider})
            if agent_type == AgentType.EMBEDDING or agent_type == "embedding":
                service = EmbeddingService(
                    model=model,
                    batch_size=1,
                    provider=provider,
                    api_key=api_key,
                    base_url=base_url,
                    use_breaker=False,
                    embedding_dim=int(embedding_dim) if embedding_dim else None,
                )
                vectors = service.embed_texts([probe], retries=1)
                return Response({"ok": True, "dim": len(vectors[0]), "sample": vectors[0][:3], "model": model, "provider": provider})
            return Response({"ok": True, "response": "Agente de re-ranking verificado (requiere pipeline para medir).", "model": model})
        except Exception as exc:
            response_status = status.HTTP_200_OK if is_client_error(exc) else status.HTTP_502_BAD_GATEWAY
            return Response({"ok": False, "error": str(exc)[:600]}, status=response_status)


FREE_MODELS_CATALOG = [
    {
        "provider": "google",
        "label": "Google Gemini",
        "key_url": "https://aistudio.google.com/app/apikey",
        "docs_url": "https://ai.google.dev/gemini-api/docs",
        "free_note": "Free tier generoso — 15 RPM / 1M tokens día",
        "models": [
            {"name": "gemini-2.0-flash", "type": "chat", "free": True, "desc": "Recomendado RAG — rápido y barato, 1M contexto"},
            {"name": "gemini-2.0-flash-lite", "type": "chat", "free": True, "desc": "Más barato, ideal re-ranking"},
            {"name": "gemini-1.5-flash", "type": "chat", "free": True, "desc": "Estable, free tier alto"},
            {"name": "gemini-2.5-flash", "type": "chat", "free": True, "desc": "Nuevo, mejor razonamiento"},
            {"name": "text-embedding-004", "type": "embedding", "free": True, "desc": "Embeddings 768 dims, gratis"},
            {"name": "gemini-embedding-001", "type": "embedding", "free": True, "desc": "Nuevo embeddings Gemini"},
        ],
    },
    {
        "provider": "groq",
        "label": "Groq",
        "key_url": "https://console.groq.com/keys",
        "docs_url": "https://console.groq.com/docs/quickstart",
        "free_note": "Free tier sin tarjeta — 14k tokens/min",
        "models": [
            {"name": "llama-3.3-70b-versatile", "type": "chat", "free": True, "desc": "Mejor calidad Groq, recomendado"},
            {"name": "llama-3.1-8b-instant", "type": "chat", "free": True, "desc": "Ultra-rápido, ideal tests"},
            {"name": "gemma2-9b-it", "type": "chat", "free": True, "desc": "Google Gemma, bueno ES"},
            {"name": "mixtral-8x7b-32768", "type": "chat", "free": True, "desc": "Mixtral, ventana 32k"},
        ],
    },
    {
        "provider": "mistral",
        "label": "Mistral AI",
        "key_url": "https://console.mistral.ai/api-keys",
        "docs_url": "https://docs.mistral.ai/",
        "free_note": "Free trial $5 + tier gratuito limitado",
        "models": [
            {"name": "mistral-small-latest", "type": "chat", "free": True, "desc": "Rápido y barato, recomendado free"},
            {"name": "mistral-large-latest", "type": "chat", "free": False, "desc": "Pago, mejor calidad"},
            {"name": "mistral-embed", "type": "embedding", "free": True, "desc": "Embeddings Mistral 1024 dims"},
        ],
    },
    {
        "provider": "openrouter",
        "label": "OpenRouter",
        "key_url": "https://openrouter.ai/keys",
        "docs_url": "https://openrouter.ai/models?filter=free",
        "free_note": "Modelos :free sin tarjeta — pool de gratuitos",
        "models": [
            {"name": "meta-llama/llama-3.3-70b-instruct:free", "type": "chat", "free": True, "desc": "Llama 3.3 70B gratis"},
            {"name": "google/gemini-2.0-flash-exp:free", "type": "chat", "free": True, "desc": "Gemini 2.0 exp gratis"},
            {"name": "qwen/qwen-2.5-72b-instruct:free", "type": "chat", "free": True, "desc": "Qwen 72B gratis"},
            {"name": "mistralai/mistral-7b-instruct:free", "type": "chat", "free": True, "desc": "Mistral 7B gratis"},
        ],
    },
    {
        "provider": "openai",
        "label": "OpenAI",
        "key_url": "https://platform.openai.com/api-keys",
        "docs_url": "https://platform.openai.com/docs/models",
        "free_note": "Requiere $5 mínimo — no es gratis puro, pero gpt-4o-mini muy barato",
        "models": [
            {"name": "gpt-4o-mini", "type": "chat", "free": False, "desc": "$0.15/1M — recomendado producción"},
            {"name": "gpt-4o", "type": "chat", "free": False, "desc": "$2.50/1M — alta calidad"},
            {"name": "text-embedding-3-small", "type": "embedding", "free": False, "desc": "$0.02/1M — barato"},
        ],
    },
    {
        "provider": "anthropic",
        "label": "Anthropic Claude",
        "key_url": "https://console.anthropic.com/settings/keys",
        "docs_url": "https://docs.anthropic.com/",
        "free_note": "$5 crédito inicial — luego pago",
        "models": [
            {"name": "claude-3-5-haiku-20241022", "type": "chat", "free": False, "desc": "Rápido y barato Anthropic"},
            {"name": "claude-3-7-sonnet-20250219", "type": "chat", "free": False, "desc": "Mejor calidad, más caro"},
        ],
    },
    {
        "provider": "ollama",
        "label": "Ollama (local)",
        "key_url": "https://ollama.com/download",
        "docs_url": "https://ollama.com/library",
        "free_note": "100% gratis y privado — corre en tu máquina",
        "models": [
            {"name": "llama3.2", "type": "chat", "free": True, "desc": "Local, 3B — rápido"},
            {"name": "qwen2.5", "type": "chat", "free": True, "desc": "Local, bueno ES"},
            {"name": "nomic-embed-text", "type": "embedding", "free": True, "desc": "Embeddings local 768 dims"},
            {"name": "mxbai-embed-large", "type": "embedding", "free": True, "desc": "Embeddings local 1024 dims"},
        ],
    },
    {
        "provider": "huggingface",
        "label": "Hugging Face (gratis)",
        "key_url": "https://huggingface.co/settings/tokens",
        "docs_url": "https://huggingface.co/docs/inference-providers/index",
        "free_note": "Inference API gratis con rate limit",
        "models": [
            {"name": "meta-llama/Llama-3.1-8B-Instruct", "type": "chat", "free": True, "desc": "Via HF Inference, gratis"},
            {"name": "sentence-transformers/all-MiniLM-L6-v2", "type": "embedding", "free": True, "desc": "Embeddings HF gratis"},
        ],
    },
]


class SeedTestAgentsView(APIView):
    def post(self, request):
        from django.core.management import call_command
        from io import StringIO
        buf = StringIO()
        try:
            call_command("seed_test_agents", stdout=buf)
            return Response({"ok": True, "output": buf.getvalue()})
        except Exception as exc:
            return Response({"ok": False, "error": str(exc)[:500]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FreeModelsView(APIView):
    def get(self, request):
        return Response(FREE_MODELS_CATALOG)


class PlatformConfigView(APIView):
    def get(self, request):
        return Response(get_platform_config())

    def put(self, request):
        serializer = PlatformConfigSerializer(data={"data": request.data or {}})
        serializer.is_valid(raise_exception=True)
        config = save_platform_config(serializer.validated_data["data"])
        return Response(config)


class ChatAgentsView(APIView):
    """Lista de agentes de chat activos disponibles para el selector del frontend."""

    def get(self, request):
        from .models import AgentType
        agents = Agent.objects.filter(agent_type=AgentType.CHAT, is_active=True).order_by("name")
        return Response(
            [
                {
                    "id": a.id,
                    "name": a.name,
                    "provider": a.provider,
                    "model": a.model,
                    "description": a.description,
                }
                for a in agents
            ]
        )
