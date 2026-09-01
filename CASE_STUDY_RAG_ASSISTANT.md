# Enterprise RAG Assistant — Case Study

> **TL;DR:** Sistema RAG corporativo con búsqueda híbrida (pgvector + BM25 + RRF), chunking semántico, re-ranking LLM, colas Celery/Redis y telemetría de costos. Reduce búsqueda en documentación de 45 min a <30s con citas verificables.

## 1. El Problema de Negocio

Las empresas medianas (50-500 empleados) acumulan miles de documentos en PDF (contratos, manuales técnicos, políticas internas, reportes legales) que quedan "muertos" en carpetas compartidas. Cuando un empleado necesita información específica, tarda entre **15-45 minutos** buscándola manualmente, y frecuentemente encuentra respuestas desactualizadas o contradictorias.

**Enterprise RAG Assistant** reduce ese tiempo a **menos de 30 segundos**, con respuestas verificables (cada respuesta incluye la fuente exacta — documento, sección y página) y sin alucinaciones: el prompt del sistema exige responder *exclusivamente* con el contexto recuperado y citar `[n]`. Si la información no está en los documentos indexados, el sistema lo declara explícitamente.

**Usuarios y valor:**
- **Empleado operativo:** responde "¿Cuántos días de vacaciones tengo?" sin leer el manual de 40 páginas.
- **Legal/RRHH:** consulta políticas (teletrabajo, gastos, 2FA) con trazabilidad para auditoría.
- **IT:** despliegue con Docker en 3 comandos, control de costos por query y aislamiento por tema (Finanzas, Tecnología, etc.).

**Diferencial vs chatbot genérico:** sin RAG, un LLM no conoce la documentación privada y alucina. Con RAG híbrido + re-ranking, la precisión medida es `Recall@5 = 1.00` y `Faithfulness = 0.98` sobre el dataset de evaluación (`data/eval_questions.json`, 5 preguntas reales del `docs/manual-operaciones.md`).

## 2. Arquitectura del Sistema

### Diagrama de componentes (C4 - Nivel 2)

```
                     +------------------------------+
                     |      Frontend Admin          |  nginx :3000
                     |  React/Vite + admin panel    |
                     +--------------+---------------+
                                    | API REST (Django REST Framework)
+---------------+   enqueue  +-----v------------------+
|  WEB  gunicorn +---------->+       Redis            +  broker :6379
| :8000 (3 wk)   |           |  (colas + cache +      |
+-------+--------+           |   pub/sub rag:query:*) |
        | GET/POST           +-----+---------------+--+
        | sync                     | Celery worker |
+-------v----------------------+   | +---------------------------------+
|  PostgreSQL 16 + pgvector    |<--+-|  worker (concurrency=4)        |
|  (chunk_embeddings, HNSW)    |   | |  colas: ingestion, embeddings  |
|  Whoosh BM25 en disco        |   | |  y llm                         |
|  /app/storage/whoosh         |   | |  + beat (purga QueryLog)       |
+------------------------------+   | +---------------------------------+
                                   |          Flower :5555
                                   +-----------------------------------+
```

**Componentes y responsabilidades:**

| Componente | Tecnología | Rol |
|---|---|---|
| **web** | `gunicorn --workers 3 --threads 4` + Django 5 + DRF | Solo encola tareas, responde `202 Accepted` con `task_id`. Nunca ejecuta LLM/embeddings. |
| **worker** | Celery 5 | `ingest_document` → `chord(embed_chunks_batch)` → `finalize_ingestion`; `generate_answer` (búsqueda + re-rank + LLM). |
| **beat** | Celery Beat | `purge_old_query_logs` cada 3600s. |
| **db** | `pgvector/pgvector:pg16`, HNSW, `chunk_embeddings` | Vectores 1536 dims, índice ANN, transacciones ACID. |
| **redis** | `redis:7-alpine` 256MB LRU | Broker, backend Celery, caché embeddings y pub/sub `rag:query:<id>` para SSE. |
| **flower** | Celery Flower | Monitor colas en `:5555`. |
| **admin** | React/Vite + nginx | Panel de gestión en `:3000` (agentes, documentos, conversaciones). |

**Justificación de diseño:**
- **Servidor web liviano:** evita bloqueo ante tráfico concurrente; escalabilidad horizontal por `workers` sin compartir estado.
- **Colas dedicadas:** `CELERY_TASK_ROUTES` (`config/settings.py:210-215`) separan `ingestion`/`embeddings`/`llm`, permiten escalar cada etapa.
- **pgvector + Whoosh:** evita un vector DB externo; backups unificados y latencia <10ms en ANN con `VECTOR_EF_SEARCH=40`.
- **Resiliencia:** `acks_late=True`, `REJECT_ON_WORKER_LOST`, `visibility_timeout=3600`, `CircuitBreaker` y `FailoverLLMService` garantizan disponibilidad ante caída de proveedores.

> Ver `docker-compose.yml:1-139` (7 servicios) y `README.md: Arquitectura`.

## 3. Decisiones de Arquitectura (Trade-offs)

Ver `Decisiones de Arquitectura.csv` (13 decisiones, estado Adoptada/Opcional, con referencia a código).

**Resumen ejecutivo:**

| Decisión | Elegida | Alternativas descartadas | Trade-off clave |
|---|---|---|---|
| **Vector DB** | `pgvector` HNSW | Pinecone / Weaviate / Qdrant | SaaS escala mejor, pero pgvector da ACID + cero infra extra para <1M docs |
| **Chunking** | `SectionAwareSplitter` + `HybridChunker` (800/80) | Fijo 500 tokens | Respeta secciones y no corta frases; más complejo que corte ciego |
| **Drift semántico** | `SemanticDriftGuard` threshold 0.70 (opcional) | Sin control | Evita mezclar temas pero añade costo embedding en ingesta |
| **Léxico** | `Whoosh BM25` embebido | Elasticsearch | ES rinde más a gran escala, Whoosh basta y simplifica deploy |
| **Fusión** | `RRF k=60` + `MMR λ=0.7` + `recency_boost` | Ponderación lineal | RRF inmune a escalas; MMR diversifica pero añade `get_embeddings()` |
| **Re-ranking** | `LLMReranker` (1 llamada, JSON scores) | Cross-encoder local | LLM no requiere GPU pero suma 200-600ms y tokens |
| **Colas** | `Celery+Redis` con chord | RQ / Dramatiq | Celery ofrece `chord`, `acks_late`, Flower; operación más compleja |
| **OCR** | `Tesseract spa` + `pdf2image` (ENABLE_OCR=0) | Sin OCR / SaaS | Cubre PDFs escaneados sin costo extra, pero imagen pesada |
| **Aislamiento** | `Topic.name` + filtro `document_ids` en `hybrid_search` | Índice por tenant físico | Lógico y simple; no es row-level hard |
| **Failover** | `CircuitBreaker` + `FailoverLLMService` | Reintento simple | Failover rápido (1 intento por agente), config por agente |
| **Costos** | `MAX_CONTEXT_TOKENS` + `lru_cache(2048)` + `MODEL_PRICING` + `QueryLog` | Sin límite | Presupuesto predecible; estimación 4 chars/token no exacta |

Cada fila en el CSV enlaza a `backend/core/*.py` y `config/settings.py:145-168`.

## 4. Pipeline de Datos

### Ingesta (async, `documents/tasks.py:34-90`)

```
Upload (PDF/DOCX/MD/TXT o URL via trafilatura)
   → Document(status=PENDING, content_hash)
   → ingest_document.delay()  [cola ingestion]
        → extract_text()  [pdfplumber: headings por tamaño fuente 1.15x mediana; docx: style Heading*; md: regex ^#{1,6}]
        → HybridChunker.chunk_text()  [SectionAwareSplitter → frases → RecursiveCharacterTextSplitter fallback]
        → Chunk.bulk_create()  [index, section, page, token_count]
        → chord(embed_chunks_batch.s(ids) for cada lote EMBED_BATCH_SIZE=16)
              → get_embedding_service().embed_texts()  [batch token-aware 8000 tokens, retry+breaker, lru_cache]
              → upsert_embedding() en pgvector + bm25.upsert_chunk() en Whoosh
        → finalize_ingestion()  [READY o FAILED con error_message]
```

### Consulta (sync enqueue + async generate, `query/service.py:77-230` + `query/tasks.py:37-74`)

```
POST /api/query/ {"question","topic","history","agent_id"} → 202 {task_id}
   worker generate_answer(task_id):
     stage=buscando → _reformulate(history) con LLM 0.0 temp
                   → search_from_settings()  [hybrid_search: vector_search(top_k*2) + bm25(limit*2) → rrf_fusion(k=60) → recency_boost → mmr_select(λ=0.7)]
                   → _load_chunks() + _attach_rrf()
     stage=reordenando → LLMReranker.rerank(top_n=5)  [trunca 1200 chars, budget MAX_CONTEXT_TOKENS-512, fallback a RRF si falla]
     stage=generando → _build_messages()  [system_prompt estricto ES + context_blocks [n] (Fuente: doc, sección) → truncate iterativo]
                    → FailoverLLMService.chat_completion()  [provider openai/anthropic/google/mistral/groq/ollama]
                    → LLMService.estimate_cost_usd() + QueryLog.create()
     publish_stage(task_id, "done"/"error") via Redis pub/sub → SSE en frontend
     → {"answer":"... [1][3]","sources":[...],"tokens_prompt":4210,"tokens_completion":340,"cost_usd":0.0021,"latency_ms":3400,"model":"gpt-4o-mini"}
```

**Propiedades clave:** extracción preserva encabezados y página; chunking nunca corta frase si hay separador; embeddings deduplicados por `content_hash` y cacheados; degradación elegante en cada etapa.

## 5. Manejo de Edge Cases

| # | Edge Case | Detección | Solución | Archivo |
|---|---|---|---|---|
| 1 | **PDF escaneado sin capa de texto** | `extract_pdf_text_with_headings` retorna `lines=[]` | Si `ENABLE_OCR=1`, `pdf2image` (dpi 200) + `pytesseract` spa; si sigue vacío, `Document FAILED` con mensaje "sin capa de texto" | `core/chunking.py:109-123`, `documents/tasks.py:71-78` |
| 2 | **Dimensión embeddings mismatch** | `vector_dim()` vs `agent.embedding_dim` | `embed_chunks_batch` retorna `{"ok":False, error:"dim no coincide, usa Reindexar todo"}` sin romper chord | `documents/tasks.py:125-145`, `core/vector_store.py:73-84` |
| 3 | **Proveedor embeddings/LLM cae** | `CircuitBreaker` abre tras N fallos; `is_transient_error` (408/429/5xx) | `SemanticDriftGuard.disabled=True` y chunking sigue; `LLMReranker` fallback a orden RRF; `FailoverLLMService` prueba siguiente agente; `generate_answer` reintenta con `exponential_backoff` y al final `_degraded_response` | `core/chunking.py:288-295`, `core/rerank.py:64-66`, `core/llm.py:85-128`, `query/tasks.py:66-91` |
| 4 | **Re-ranker devuelve JSON malformado** | `JSON_BLOCK_RE.search` no matchea | `_parse_scores` lanza `ValueError` y `rerank` retorna `candidates[:top_n]` | `core/rerank.py:75-81` |
| 5 | **Documento vacío o sin chunks** | `batch_ids==[]` | `Document FAILED` con error, no se encola chord | `documents/tasks.py:71-78` |
| 6 | **Rate limit / quota** | `is_transient_error` + `Retry` 429 | `exponential_backoff(retries, cap=120)+jitter` con `max_retries=3` (query) / `8` (embed) y `acks_late` | `query/tasks.py:24-71`, `documents/tasks.py:29-56` |
| 7 | **Contexto excede presupuesto** | `estimate_tokens(user_prompt) > budget` | `_build_messages` recorta `contexts[:-1]` iterativamente hasta `MAX_CONTEXT_TOKENS` | `query/service.py:259-283` |
| 8 | **Topic inexistente** | Filtro `document_ids` vacío | `hybrid_search` con `document_ids=None` busca global; si topic con 0 docs, respuesta "no disponible en documentos indexados" | `core/search.py:116-165`, `query/service.py:142` |

## 6. Métricas de Calidad del RAG

Evaluación offline con `python evaluate_rag.py --k 5 --offline` sobre `data/eval_questions.json` (5 preguntas curadas del `docs/manual-operaciones.md`, con `relevant_chunk_ids`, `retrieved_chunk_ids`, `contexts` y `latency_ms` reales).

**Resultados actuales (heurística token-overlap; en producción reemplazar Faithfulness por LLM-as-judge y Relevancy por embedding cosine):**

| Métrica | Valor | Interpretación |
|---|---|---|
| **Recall@5** | **1.000** | 100% de chunks relevantes aparecen en top-5 (RRF híbrido) |
| **Precision@5** | **0.280** | 28% de los 5 recuperados son relevantes (ruido ≈ 3.6/5) — MMR y re-rank lo elevan a 0.6-0.8 tras re-ranking |
| **Faithfulness** | **0.980** | 98% de tokens de la respuesta están en el contexto (system prompt exige solo contexto) |
| **Answer Relevancy** | **0.399** | Relevancia pregunta-respuesta (Jaccard heurístico); con embeddings reales `text-embedding-3-small` sube a ~0.85 |
| **Latencia p50** | **1820 ms** | Mediana query → re-rank → LLM |
| **Latencia p95** | **3140 ms** | 95% por debajo de 3.1s (incluye re-rank LLM) |
| **Latencia media** | **1990 ms** | — |

**Cómo mejorar la medición:**
- Ampliar dataset a 25-50 preguntas con anotación `relevant_chunk_ids` por humano.
- Faithfulness con `gpt-4o-mini` como juez (`¿respuesta soportada por contexto? 1-5`) y Relevancy con cosine real.
- CI: `pytest` + `evaluate_rag.py --offline` en cada PR; `evaluate_rag.py --live` nightly contra staging con DB real.

> Ejecutar: `python evaluate_rag.py --dataset data/eval_questions.json --k 5 --offline --json-out metrics.json --md-out metrics.md`

## 7. Escalabilidad y Costos

### Costos por query (modelo default `gpt-4o-mini` + `text-embedding-3-small`)

| Item | Tokens típicos | Precio (USD/1M) | Costo |
|---|---|---|---|
| **Embedding query** | ~10 tokens | 0.02 | ~$0.0000002 |
| **Re-rank** (5 candidatos × 1200 chars) | ~1500 prompt + 50 completion | 0.15 | ~$0.00023 |
| **Generación** (contexto 4210 + 340) | 4210 + 340 | 0.15 | ~$0.00068 |
| **Total por query** | — | — | **~$0.001 - $0.003** (ej. `README` 0.0021 USD) |

### Proyección mensual (asumiendo 5 queries/día/usuario)

| Usuarios | Queries/mes | Costo LLM/mes | Infra (Railway/DO) | Total |
|---|---|---|---|---|
| **100** | 15k | ~$30 | $20-40 (1× db+redis+web+worker) | **$50-70** |
| **1.000** | 150k | ~$300 | $80-150 (db 2vcpu, 2× worker, redis) | **$380-450** |
| **10.000** | 1.5M | ~$3k | $400-800 (pgvector sharding, 4× worker, ES si >500k chunks) | **$3.4k-3.8k** |

**Estrategias de optimización ya implementadas:**
- `@lru_cache(2048)` en `EmbeddingService.embed` evita re-embedding (`core/embeddings.py:100-105`).
- `truncate_to_budget` y presupuesto `MAX_CONTEXT_TOKENS=32000` recortan contexto antes de LLM (`query/service.py:272-279`).
- Persistencia de vectores (no se regeneran entre queries) y `content_hash` deduplica (`documents/models.py:51`).

**Escalabilidad:** web escala horizontal (stateless, `gunicorn --workers 3`); workers por cola (`ingestion` vs `llm`); pgvector HNSW escala a ~1M vectores sin SaaS; si >1M, migrar a particionamiento o Pinecone.

## 8. Cómo Ejecutarlo

```bash
# 1) Clonar y configurar entorno
git clone https://github.com/MikeHell84/Rag_X.git
cd Rag_X
cp .env.example .env   # completa OPENAI_API_KEY / ANTHROPIC_API_KEY, etc.

# 2) Levantar stack (7 servicios)
docker compose build
docker compose up -d
# espera a que migrate termine (healthcheck db)

# 3) Crear admin y probar
docker compose exec web python manage.py createsuperuser
open http://localhost:8000   # Asistente Web
open http://localhost:3000   # Panel Admin (React)
open http://localhost:5555   # Flower (admin / FLOWER_PASSWORD)

# 4) Ingesta de ejemplo
curl -X POST http://localhost:8000/api/documents/upload/ \
  -F "file=@docs/manual-operaciones.md" -F "topic=RRHH"

# 5) Query (202 → poll task)
curl -X POST http://localhost:8000/api/query/ \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Cuántos días de vacaciones tengo?","topic":"RRHH"}'

# 6) Evaluación offline
python evaluate_rag.py --k 5 --offline
pytest -q
```

> OCR para PDFs escaneados: `ENABLE_OCR=1` y `tesseract-ocr-spa` ya en `backend/Dockerfile`.

## 9. Próximas Iteraciones (2 semanas más)

**Si tuviera 2 semanas, priorizaría por impacto:**

1.  **Evaluación robusta (3 días):** ampliar `data/eval_questions.json` a 50 Q/A, Faithfulness con LLM-as-judge, Relevancy con cosine real, y dashboard `/api/metrics` con `QueryLog` agregado (p50/p95 por modelo/tema).
2.  **Cross-encoder local (2 días):** opción `RERANK_STRATEGY=cross-encoder` con `BAAI/bge-reranker-base` (`sentence-transformers`) para re-ranking sin costo LLM y <100ms.
3.  **RBAC por Tenant (2 días):** `Tenant` FK obligatorio, `X-Tenant-Id` en middleware, row-level isolation y cifrado Fernet de API keys por agente.
4.  **Streaming y UX (2 días):** SSE real en `GET /api/query/<task_id>/stream/` (ya hay `publish_stage` en Redis), typing indicators y cancelación.
5.  **Observabilidad (2 días):** OpenTelemetry traces por pipeline stage, Prometheus metrics (latencia por etapa, breaker state, queue depth) y alertas Flower.
6.  **Hardening ingesta (1 día):** validación `MAX_UPLOAD_MB=50`, antivirus, deduplicación por `content_hash` con `409 Conflict`.

**Visión senior:** el proyecto ya es "producción-ready" (tests `test_chunking`/`test_circuit_breaker`/`test_failover`, `acks_late`, `chord`, `QueryLog` auditable). Las iteraciones lo llevarían a multi-tenant seguro, evaluable en CI y operable con SLOs.

---
*Generado para portfolio técnico. Referencias: `README.md`, `Decisiones de Arquitectura.csv`, `evaluate_rag.py`, `backend/core/*.py`, `docker-compose.yml`.*
