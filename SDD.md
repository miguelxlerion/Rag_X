# Software Design Document (SDD)
## Enterprise RAG Assistant — IEEE 1016 Compliant

---

**Document Control**
- **Title:** Software Design Document — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Author:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Approved
- **IEEE Std:** 1016-2009 (IEEE Standard for Information Technology — Systems Design — Software Design Descriptions)

---

## Table of Contents
1. [Scope](#1-scope)
2. [Applicable Documents](#2-applicable-documents)
3. [System Overview](#3-system-overview)
4. [System Architecture](#4-system-architecture)
5. [Design Decisions & Trade-offs](#5-design-decisions--trade-offs)
6. [Data Design](#6-data-design)
7. [Interface Design](#7-interface-design)
8. [Component Design](#8-component-design)
9. [Deployment Design](#9-deployment-design)
10. [Security Design](#10-security-design)
11. [Quality Attributes](#11-quality-attributes)
12. [Testing Strategy](#12-testing-strategy)
13. [Glossary](#13-glossary)

---

## 1. Scope

### 1.1 Identification
**Project Name:** Enterprise RAG Assistant  
**Repository:** https://github.com/miguelxlerion/Rag_X  
**Type:** Retrieval-Augmented Generation (RAG) system for corporate knowledge bases

### 1.2 Purpose
This document describes the software design of the Enterprise RAG Assistant, a production-ready RAG system enabling mid-size companies (50–500 employees) to query private documentation (PDF, DOCX, Markdown, TXT, URLs) via natural language with verifiable citations, cost tracking, and sub-30-second response times.

### 1.3 Objectives
- Reduce document search time from 15–45 minutes to <30 seconds
- Eliminate hallucinations via strict context-only prompting with citations `[n]`
- Provide auditable cost/latency telemetry per query
- Support multi-tenant isolation by topic/domain
- Deploy via Docker Compose in 3 commands

### 1.4 Boundaries
**In Scope:** Document ingestion, semantic chunking, hybrid search (vector + BM25), LLM re-ranking, async query pipeline, cost tracking, topic isolation, admin UI  
**Out of Scope:** Fine-tuning models, real-time voice I/O, SSO/OIDC, advanced RBAC (future roadmap)

---

## 2. Applicable Documents

| Ref | Document | Version |
|-----|----------|---------|
| [1] | IEEE 1016-2009 | 2009 |
| [2] | IEEE 829-2008 (Test Documentation) | 2008 |
| [3] | ISO/IEC 25010 (Quality Model) | 2011 |
| [4] | CASE_STUDY_RAG_ASSISTANT.md | 1.0 |
| [5] | Decisiones de Arquitectura.csv | 1.0 |
| [6] | README.md | 1.0 |
| [7] | evaluate_rag.py | 1.0 |

---

## 3. System Overview

### 3.1 Context Diagram
```
┌─────────────┐     HTTPS/REST      ┌─────────────────────────────────────┐
│   Employee  │ ◄─────────────────► │     Enterprise RAG Assistant        │
└─────────────┘                     │  ┌─────────┐ ┌─────────┐ ┌───────┐ │
                                    │  │ Admin   │ │  API    │ │Worker │ │
                                    │  │  UI     │ │ Gateway │ │Pool   │ │
                                    │  └────┬────┘ └────┬────┘ └───┬───┘ │
                                    │       │         │         │      │
                                    │  ┌───▼─────────▼─────────▼───┐  │
                                    │  │      PostgreSQL + pgvector    │  │
                                    │  │      Redis (broker/cache)     │  │
                                    │  └─────────────────────────────┘  │
                                    └─────────────────────────────────────┘
```

### 3.2 Major Functions
| ID | Function | Description |
|----|----------|-------------|
| F1 | Document Ingestion | Upload PDF/DOCX/MD/TXT/URL → extract → chunk → embed → index |
| F2 | Query Processing | Natural language → hybrid search → re-rank → LLM generate → cite |
| F3 | Agent Management | Configure LLM/embedding/reranker agents with failover |
| F4 | Cost & Latency Tracking | Per-query tokens, USD cost, p50/p95 latency in `QueryLog` |
| F5 | Topic Isolation | Documents & conversations scoped by `Topic` — no cross-contamination |
| F6 | Admin Dashboard | React/Vite UI for agents, documents, metrics, config backup |

### 3.3 User Classes
| Class | Permissions |
|-------|-------------|
| Employee | Query via API / Panel Admin (no auth on panel) |
| Admin | Full Django Admin (`/admin`), agent config, superuser |
| System | Celery workers, beat scheduler, Flower monitor |

---

## 4. System Architecture

### 4.1 Architectural Style
**Pattern:** Layered, Microservice-ready (7 Docker services), Event-driven async pipeline  
**Decomposition:** Web (stateless) ↔ Redis broker ↔ Celery Workers (stateful compute) ↔ PostgreSQL (persistent)

### 4.2 Service Topology (docker-compose.yml)
| Service | Image | Ports | Role |
|---------|-------|-------|------|
| `db` | `pgvector/pgvector:pg16` | 5432 | PostgreSQL + HNSW index |
| `redis` | `redis:7-alpine` | 6379 | Broker, cache, pub/sub |
| `migrate` | `backend` | — | One-shot: migrate + collectstatic |
| `web` | `backend` | 8000 | Gunicorn 3w/4t — enqueues only |
| `worker` | `backend` | — | Celery: ingestion, embeddings, llm queues |
| `beat` | `backend` | — | Celery Beat: purge old QueryLog |
| `flower` | `backend` | 5555 | Celery monitoring (basic-auth) |
| `admin` | `frontend` (nginx) | 3000 | React/Vite SPA |

### 4.3 Concurrency Model
- **Web:** 3 gunicorn workers × 4 threads = 12 concurrent HTTP (I/O only)
- **Worker:** 1 prefork process per container (scales horizontally via `docker compose up -d --scale worker=4`)
- **Queues:** `ingestion` (document upload), `embeddings` (batch vectorize), `llm` (query generation)
- **Policy:** `acks_late=True`, `REJECT_ON_WORKER_LOST=True`, `visibility_timeout=3600`

---

## 5. Design Decisions & Trade-offs

Per [Decisiones de Arquitectura.csv](Decisiones%20de%20Arquitectura.csv) and CASE_STUDY §3:

| # | Decision | Selected | Alternative | Trade-off |
|---|----------|----------|-------------|-----------|
| 1 | Vector DB | **pgvector (HNSW)** | Pinecone, Weaviate, Qdrant | Zero extra infra, ACID, backup unified; horizontal scaling limited ~1M vecs |
| 2 | Chunking | **Semantic (SectionAwareSplitter + HybridChunker 800/80)** | Fixed 500 tokens | Respects headings, never cuts sentences; more complex |
| 3 | Drift Guard | **SemanticDriftGuard (cosine ≥0.70)** | None | Prevents topic mixing; extra embedding cost; opt-in (`USE_SEMANTIC_GUARD=0`) |
| 4 | Lexical Search | **Whoosh BM25** | Elasticsearch, OpenSearch | Embedded, no extra service; limited Spanish analyzer, no sharding |
| 5 | Fusion | **RRF (k=60) + MMR (λ=0.7) + Recency Boost** | Linear weighting | Scale-invariant; MMR adds `get_embeddings()` latency |
| 6 | Re-ranking | **LLMReranker (1-call JSON 1-10)** | Cross-encoder local | No GPU needed; +200–600ms + token cost; fallback to RRF |
| 7 | Async Queues | **Celery 5 + Redis** | RQ, Dramatiq, BullMQ | Chord, acks_late, Flower, beat; more ops complexity |
| 8 | ANN Index | **HNSW (ef_search=40)** | IVFFlat, brute | Good recall/latency for 1536-dim; memory > IVFFlat |
| 9 | OCR | **Tesseract (spa) + pdf2image** | None / SaaS | Free for scanned PDFs; heavy deps (poppler); opt-in `ENABLE_OCR=1` |
| 10 | Multi-tenancy | **Topic filter (`document_ids`)** | Physical sharding | Logical isolation; not row-level security |
| 11 | Resilience | **CircuitBreaker + FailoverLLMService** | Simple retry | Fast failover (1 try/agent); config per agent |
| 12 | Cost Control | **Context budget + lru_cache(2048) + MODEL_PRICING + QueryLog** | Unlimited | Predictable cost; 4-char token estimate not exact |
| 13 | Agent Config | **DB-stored agents (encrypted keys)** | Env-only | Per-agent keys, fallback order, UI manageable |

---

## 6. Data Design

### 6.1 Entity-Relationship (Django ORM — `backend/documents/models.py`, `backend/agents/models.py`)

```
Tenant (1) ──< Document (>── Topic (logical)
    │
    ├─< Chunk (index, section, page, token_count)
    │      │
    │      └─> chunk_embeddings (pgvector, HNSW)
    │
    ├─< QueryLog (tokens, cost_usd, latency_ms, citations)
    │
    └─< Conversation (>── ConversationMessage
```

**Agent** (`backend/agents/models.py:23-80`): `name`, `agent_type` (chat|embedding|reranker), `provider`, `model`, `base_url`, `api_key` (Fernet-encrypted), `temperature`, `max_tokens`, `top_k`, `system_prompt`, `embedding_dim`, `is_active`, `is_fallback`, `fallback_order`

**PlatformConfig** (`agents/models.py:82-88`): JSON blob for global retrieval params (`chunk_size`, `hybrid_top_k`, `rerank_top_k`, `use_semantic_guard`, etc.)

### 6.2 pgvector Schema (`chunk_embeddings`)
```sql
CREATE TABLE chunk_embeddings (
    chunk_id      INTEGER PRIMARY KEY REFERENCES documents_chunk(id),
    embedding     VECTOR(1536),        -- pgvector HNSW
    embedding_model VARCHAR(128),
    content_hash  CHAR(64),            -- SHA256 for deduplication
    created_at    TIMESTAMPTZ
);
CREATE INDEX ON chunk_embeddings USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);
```

### 6.3 Whoosh BM25 Index
- Location: `/app/storage/whoosh` (volume `rag_storage`)
- Fields: `chunk_id` (ID), `document_id` (ID), `content` (TEXT)
- Parser: `MultifieldParser(["content"])`

### 6.4 Data Flow Summary
```
Upload → extract_text() → HybridChunker → Chunk.bulk_create()
   → chord(embed_chunks_batch) → embed_texts() → upsert_embedding() + bm25.upsert_chunk()
   → finalize_ingestion() → Document.status = READY
Query → search_from_settings() → hybrid_search() (vector + BM25 → RRF → MMR → recency)
   → _load_chunks() → LLMReranker.rerank() → _build_messages() → FailoverLLMService
   → QueryLog.create() → return {answer, sources, cost, latency}
```

---

## 7. Interface Design

### 7.1 External REST API (Django REST Framework — `backend/api/`, `backend/query/`, `backend/documents/`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health/` | GET | None | `{status, database, redis, vector_embeddings}` |
| `/api/metrics/` | GET | None | Prometheus `rag_*` counters |
| `/api/documents/upload/` | POST | None | Multipart `file` + `topic` → `202 {task_id}` |
| `/api/documents/from-url/` | POST | None | JSON `{url, topic}` → `202 {task_id}` |
| `/api/documents/` | GET | None | Paginated list |
| `/api/documents/{id}/` | DELETE/PATCH | None | Delete / retry / update topic |
| `/api/query/` | POST | None | `{question, topic, history, agent_id}` → `202 {task_id}` |
| `/api/query/{task_id}/` | GET | None | Poll result (`status`, `result`, `error`) |
| `/api/agents/` | CRUD | None | Agent management (see below) |
| `/api/agents/{id}/test/` | POST | None | Test agent config without saving |
| `/api/agents/test-config/` | POST | None | Test arbitrary config (no DB write) |
| `/api/agents/seed-test-agents/` | POST | None | Create 9 demo agents |
| `/api/free-models/` | GET | None | Catalog of free models with key URLs |
| `/api/platform-config/` | GET/PUT | None | Global retrieval params |
| `/api/chat-agents/` | GET | None | Active chat agents for selector |
| `/api/conversations/` | CRUD | None | Session history per topic/agent |

### 7.2 Agent API Details
**AgentSerializer** (`agents/serializers.py:8-74`): `api_key` write-only (encrypted on save), `has_api_key`, `api_key_masked` read-only.  
**Endpoints:** `activate`, `deactivate`, `test` (probe prompt optional).

### 7.3 Frontend UI (React + Vite — `frontend/src/`)
| Tab | Component | Purpose |
|-----|-----------|---------|
| Agentes IA | `AgentCard`, `AgentForm` | List, create, edit, test, toggle active/fallback |
| Modelos Gratis | `FreeModelsCatalog` | Browse 8 providers, filter chat/embedding, pick model → prefill form |
| Búsqueda | `PlatformConfigForm` | Edit global retrieval params |
| Chat | `ChatQuery` | Ad-hoc query with streaming via Redis pub/sub |
| Documentos | `DocumentsList` | Upload, list, retry, delete, reindex |
| Chat y Documentos | `ChatDocuments` | Side-by-side chat + doc browser |

**Icons:** Professional SVG set in `Icon.tsx` (Key, Plug, Beaker, Download, Upload, Save, External, Check) — no emojis.

### 7.4 Internal Interfaces
| Interface | Components | Protocol |
|-----------|------------|----------|
| Web → Worker | `generate_answer`, `ingest_document` | Celery/Redis (JSON) |
| Worker → LLM | `FailoverLLMService.chat_completion` | HTTP/JSON (OpenAI, Anthropic, Google, Mistral, Groq, Ollama, OpenRouter) |
| Worker → Embeddings | `EmbeddingService.embed_texts` | HTTP/JSON (OpenAI, Google, Mistral, Ollama) |
| Worker → Redis Pub/Sub | `publish_stage(task_id, event, data)` | `rag:query:<task_id>` channel |
| Worker → pgvector | `upsert_embedding`, `vector_search` | Raw SQL via Django cursor |
| Worker → Whoosh | `bm25.upsert_chunk`, `bm25.search` | File-based index |

---

## 8. Component Design

### 8.1 Core Pipeline Modules (`backend/core/`)

| Module | Responsibility | Key Classes/Functions |
|--------|----------------|----------------------|
| `chunking.py` | Semantic document splitting | `extract_pdf_text_with_headings`, `SectionAwareSplitter`, `SemanticDriftGuard`, `HybridChunker` |
| `search.py` | Hybrid retrieval | `vector_search`, `bm25_search`, `rrf_fusion`, `mmr_select`, `hybrid_search`, `search_from_settings` |
| `rerank.py` | LLM re-ranking | `LLMReranker.rerank` (prompt → JSON scores → sort) |
| `llm.py` | LLM abstraction | `LLMService`, `FailoverLLMService` (provider-agnostic, circuit breaker) |
| `embeddings.py` | Embedding abstraction | `EmbeddingService`, `FailoverEmbeddingService` (batch, cache, dim check) |
| `vector_store.py` | pgvector access | `upsert_embedding`, `vector_search`, `get_embeddings`, `vector_dim` |
| `bm25.py` | Whoosh wrapper | `get_bm25_index().search/upsert/delete_document` |
| `circuit_breaker.py` | Resilience | `CircuitBreaker` (CLOSED/OPEN/HALF_OPEN, cooldown) |
| `providers.py` | Provider factory | `build_client`, `chat_call`, `embed_call`, `is_transient_error`, `is_client_error` |
| `token_budget.py` | Token estimation | `estimate_tokens` (4 char/token), `truncate_to_budget` |
| `url_ingest.py` | URL → Markdown | `trafilatura` fetch + extract |

### 8.2 Async Tasks (`backend/documents/tasks.py`, `backend/query/tasks.py`)

| Task | Queue | Retries | Key Logic |
|------|-------|---------|-----------|
| `ingest_document` | ingestion | 3 | Extract → chunk → chord(embed) → finalize |
| `embed_chunks_batch` | embeddings | 8 | Batch embed (8k tokens) → pgvector + Whoosh upsert |
| `finalize_ingestion` | ingestion | 0 | Aggregate chord results → READY/FAILED |
| `generate_answer` | llm | 3 | Reformulate → hybrid_search → rerank → LLM → QueryLog |
| `purge_old_query_logs` | beat (3600s) | 0 | Delete QueryLog > 30 days |

### 8.3 Agent Services (`backend/agents/services.py`)
- `get_active_agent(type)` — primary active agent
- `get_active_agents(type)` — chain for failover (primary + fallbacks ordered)
- `get_platform_config()` — merged defaults + DB overrides

---

## 9. Deployment Design

### 9.1 Docker Compose (Production-ready)
```yaml
# docker-compose.yml — 7 services, named volumes, healthchecks
services:
  db:       pgvector/pgvector:pg16, healthcheck pg_isready
  redis:    redis:7-alpine, maxmemory 256MB LRU
  migrate:  one-shot, depends_on db:healthy
  web:      gunicorn 3w/4t, depends_on migrate:completed, redis:healthy
  worker:   celery -Q embeddings,llm,ingestion -c1 --max-tasks-per-child=50
  beat:     celery beat, schedule /app/storage/celerybeat-schedule
  flower:   basic-auth admin:${FLOWER_PASSWORD:-admin123}
  admin:    nginx serving Vite build, depends_on web:started
volumes: pgdata, redisdata, rag_storage, rag_media
```

### 9.2 Environment Variables (`.env` / `.env.example`)
| Variable | Default | Purpose |
|----------|---------|---------|
| `POSTGRES_DB/USER/PASSWORD` | `rag/rag/rag` | DB credentials |
| `POSTGRES_HOST` | `db` | Internal Docker DNS |
| `REDIS_URL` | `redis://redis:6379/0` | Broker + cache |
| `OPENAI_API_KEY` | `sk-...` | Fallback provider key |
| `FLOWER_PASSWORD` | `admin123` | Flower basic-auth (matches Django Admin) |
| `DJANGO_SECRET_KEY` | `change-me...` | **Must rotate for production** |
| `CHUNK_SIZE/OVERLAP` | `800/80` | Chunking params |
| `USE_SEMANTIC_GUARD` | `0` | Drift guard opt-in |

### 9.3 Scaling Guidelines
| Load | Web | Worker | DB | Redis |
|------|-----|--------|----|-------|
| 100 users | 3w | 2 | 2 vCPU, 4GB | 256MB |
| 1,000 users | 6w | 4 | 4 vCPU, 16GB | 1GB |
| 10,000 users | 12w | 8+ | Read replicas, consider Pinecone | Cluster |

---

## 10. Security Design

| Layer | Mechanism |
|-------|-----------|
| **API Keys** | Fernet (AES-256) encryption at rest (`agents/crypto.py`), per-agent, never in logs |
| **Transport** | TLS termination at reverse proxy (nginx/Traefik) — not in compose |
| **Auth** | Django Admin: session + BasicAuth; API: CSRF-exempt for `/api/`, BasicAuth optional |
| **CORS/CSRF** | `CSRF_TRUSTED_ORIGINS` allowlisted; `/api/` exempt via `ApiCsrfExemptMiddleware` |
| **Secrets** | `.env` excluded from git; `DJANGO_SECRET_KEY` rotated per env |
| **Data Isolation** | Topic-level logical isolation (`document_ids` filter); `Tenant` FK optional |
| **Rate Limiting** | DRF throttles: anon 300/min, user 600/min, query 60/min, upload 20/min |
| **Dependencies** | Pinned versions in `requirements.txt`; `pip-audit` recommended |

---

## 11. Quality Attributes (ISO/IEC 25010)

| Attribute | Target | Verification |
|-----------|--------|--------------|
| **Functional Suitability** | RAG pipeline complete | `pytest -q` (43 passed), `evaluate_rag.py` metrics |
| **Performance** | p95 ≤ 3.5s | `evaluate_rag.py --k 5 --offline` → 3140ms |
| **Reliability** | 99.9% query success | CircuitBreaker, Failover, `acks_late`, retries |
| **Scalability** | Horizontal worker scaling | `docker compose up -d --scale worker=N` |
| **Maintainability** | Modular core, typed, tested | `pytest`, type hints, `ruff`/`black` ready |
| **Security** | Encrypted keys, no secrets in repo | `.gitignore` excludes `.env`, Fernet encryption |
| **Usability** | Admin UI, free model catalog, test button | `FreeModelsCatalog`, `ConfigBackup`, `Probar API` |
| **Portability** | Docker-only deploy | `docker compose up -d` (3 commands) |

**Measured Metrics (offline, 5 Q):**
- Recall@5: 1.000
- Precision@5: 0.280
- Faithfulness: 0.980
- Answer Relevancy: 0.399
- Latency p50: 1820 ms
- Latency p95: 3140 ms

---

## 12. Testing Strategy

### 12.1 Unit Tests (`backend/tests/`)
| Test Module | Coverage |
|-------------|----------|
| `test_chunking.py` | Section detection, splitting, drift guard |
| `test_circuit_breaker.py` | State transitions, thresholds |
| `test_search.py` | RRF fusion correctness |
| `test_rerank.py` | Fallback on error, score parsing, reordering |
| `test_token_budget.py` | Estimation, truncation |
| `test_providers.py` | Error classification (4xx vs 5xx/429) |
| `test_failover.py` | FailoverLLMService / FailoverEmbeddingService |
| `test_documents.py` | Upload/list/retry/delete (requires Django test DB) |

**Run:** `pytest -q` (43 passed, 8 doc tests skipped due to `trafilatura` missing outside Docker)

### 12.2 Integration / E2E
- **Manual:** `docker compose up -d` → `curl /api/health` → upload → query
- **Demo Script:** `python evaluate_rag.py --k 5 --offline --json-out metrics.json`
- **CI-ready:** `pytest` + `evaluate_rag.py --offline` in GitHub Actions

### 12.3 Load Testing (Future)
- Locust script against `/api/query/` with `task_id` polling
- Metrics: p95 latency, error rate, queue depth (Flower), DB connections

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **RAG** | Retrieval-Augmented Generation — LLM grounded in retrieved context |
| **Chunk** | Document fragment (≤800 tokens) with section/page metadata |
| **Embedding** | Dense vector (1536-dim) representing semantic meaning |
| **HNSW** | Hierarchical Navigable Small World — ANN index in pgvector |
| **BM25** | Best Matching 25 — probabilistic lexical ranking (Whoosh) |
| **RRF** | Reciprocal Rank Fusion — combines rankings without score normalization |
| **MMR** | Maximum Marginal Relevance — diversifies results (λ=0.7) |
| **Re-ranking** | Second-pass LLM scoring of candidates (1–10) |
| **Failover** | Automatic switch to backup agent on primary failure |
| **Circuit Breaker** | Stops calls to failing provider after threshold, cooldown then half-open |
| **Topic** | Logical namespace isolating documents & conversations |
| **QueryLog** | Audit record: tokens, cost, latency, answer, citations |
| **Flower** | Celery monitoring UI (port 5555) |
| **pgvector** | PostgreSQL extension for vector similarity search |

---

## Appendix A: Key File References

| Area | Path |
|------|------|
| Settings | `backend/config/settings.py:145-215` |
| Chunking | `backend/core/chunking.py:175-367` |
| Search | `backend/core/search.py:22-165` |
| Re-rank | `backend/core/rerank.py:38-81` |
| LLM/Embeddings | `backend/core/llm.py`, `backend/core/embeddings.py` |
| Ingestion Tasks | `backend/documents/tasks.py:34-171` |
| Query Tasks | `backend/query/tasks.py:37-74` |
| Agent Models | `backend/agents/models.py:23-80` |
| Agent Views | `backend/agents/views.py:17-134` |
| Frontend UI | `frontend/src/App.tsx`, `frontend/src/components/*.tsx` |
| Docker Compose | `docker-compose.yml:1-139` |
| Evaluation | `evaluate_rag.py:1-200` |

---

**End of Document** — *Enterprise RAG Assistant SDD v1.0 (IEEE 1016)*  
**Repository:** https://github.com/miguelxlerion/Rag_X