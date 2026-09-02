# Software Requirements Specification (SRS)
## Enterprise RAG Assistant
### IEEE 830-1998 Compliant

---

**Document Control**
- **Title:** Software Requirements Specification — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Author:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Baseline
- **IEEE Std:** 830-1998 (IEEE Recommended Practice for Software Requirements Specifications)

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Specific Requirements](#3-specific-requirements)
4. [Interface Requirements](#4-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Verification & Validation](#6-verification--validation)
7. [Appendices](#7-appendices)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements for the **Enterprise RAG Assistant**, a production-ready Retrieval-Augmented Generation system that enables mid-size organizations (50–500 employees) to query private corporate documentation via natural language with verifiable citations, cost tracking, and sub-30-second response times.

### 1.2 Scope
**Product Name:** Enterprise RAG Assistant  
**Repository:** https://github.com/miguelxlerion/Rag_X  
**Boundaries:** Document ingestion (PDF, DOCX, MD, TXT, URL), semantic chunking, hybrid search (vector + BM25), LLM re-ranking, async query pipeline, topic isolation, admin dashboard, cost/latency telemetry.  
**Out of Scope:** Model fine-tuning, voice I/O, SSO/OIDC, advanced RBAC, multi-language UI (Spanish-only MVP).

### 1.3 Definitions, Acronyms, Abbreviations
| Term | Definition |
|------|------------|
| **RAG** | Retrieval-Augmented Generation |
| **LLM** | Large Language Model |
| **Chunk** | Document fragment ≤800 tokens with section/page metadata |
| **Embedding** | Dense vector (1536-dim) representing semantic meaning |
| **HNSW** | Hierarchical Navigable Small World — ANN index in pgvector |
| **BM25** | Best Matching 25 — lexical ranking (Whoosh) |
| **RRF** | Reciprocal Rank Fusion — ranking fusion without score normalization |
| **MMR** | Maximum Marginal Relevance — result diversification |
| **QueryLog** | Audit record: tokens, cost, latency, answer, citations |
| **Topic** | Logical namespace isolating documents & conversations |

### 1.4 References
- IEEE 830-1998, IEEE 1016-2009 (SDD), IEEE 829-2008 (Test Plan), ISO/IEC 25010
- SDD.md (Software Design Document), evaluate_rag.py, CASE_STUDY_RAG_ASSISTANT.md

---

## 2. Overall Description

### 2.1 Product Perspective
**Standalone Dockerized System** — 7 services orchestrated via Docker Compose:
- No external SaaS dependencies (pgvector, Whoosh, Redis, PostgreSQL self-hosted)
- Optional external LLM providers (OpenAI, Anthropic, Google, Mistral, Groq, Ollama, OpenRouter)
- Integrates with existing corporate infrastructure via REST API

### 2.2 User Classes and Characteristics
| Class | Description | Technical Level |
|-------|-------------|-----------------|
| **Employee** | End-user querying documentation | Low (natural language) |
| **Knowledge Manager** | Uploads documents, manages topics | Medium |
| **System Admin** | Configures agents, monitors health | High (Django Admin, Flower) |
| **DevOps** | Deploys, scales, maintains infra | High |

### 2.3 Operating Environment
- **Deployment:** Docker Compose (Linux containers)
- **Host OS:** Linux (Docker Desktop / Server)
- **Dependencies:** PostgreSQL 16 + pgvector, Redis 7, Python 3.12
- **External APIs:** Optional LLM providers (HTTPS/JSON)

### 2.4 Design and Implementation Constraints
- **Container-only deployment** — no bare-metal install
- **Python 3.12+, Django 5, DRF** — pinned in `requirements.txt`
- **No GPUs required** — LLM inference via external APIs
- **Spanish language only** (prompts, UI, tokenization)
- **Offline evaluation mode** — `evaluate_rag.py --offline`

### 2.5 Assumptions and Dependencies
| Assumption | Impact if False |
|------------|-----------------|
| Docker Engine available | Cannot deploy |
| At least one LLM provider API key | Queries fail (demo agents need keys) |
| PostgreSQL pgvector extension | Vector search unavailable |
| Redis 7+ for broker/cache | Async pipeline broken |

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 Document Ingestion (FR-ING)
| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-ING-01 | System shall accept PDF, DOCX, Markdown, TXT file uploads via multipart POST | Must | SDD §8.1, SDD §8.2 |
| FR-ING-02 | System shall ingest documents from public URLs (HTML → Markdown via trafilatura) | Must | SDD §8.1 |
| FR-ING-03 | System shall extract text preserving headings (PDF: font size ≥1.15×median; DOCX: Heading* styles; MD: `#` syntax) | Must | SDD §8.1 `chunking.py:85-141` |
| FR-ING-04 | System shall chunk semantically: SectionAwareSplitter → sentences → RecursiveCharacterTextSplitter fallback | Must | SDD §8.1 `chunking.py:175-367` |
| FR-ING-05 | System shall never split a sentence when a separator exists | Must | SDD §8.1 |
| FR-ING-06 | System shall optionally apply SemanticDriftGuard (cosine ≥0.70) to prevent topic mixing | Should | SDD §8.1 `chunking.py:274-313` |
| FR-ING-07 | System shall process ingestion asynchronously via Celery chord (extract → chunk → parallel embed batches → finalize) | Must | SDD §8.2 `tasks.py:34-171` |
| FR-ING-08 | System shall deduplicate chunks by content_hash (SHA256) and cache embeddings (lru_cache 2048) | Must | SDD §8.1 `embeddings.py:100-105` |
| FR-ING-09 | System shall support OCR for scanned PDFs (Tesseract spa, opt-in `ENABLE_OCR=1`) | Could | SDD §8.1 `chunking.py:109-119` |
| FR-ING-10 | System shall report ingestion status (PENDING → PROCESSING → CHUNKED → EMBEDDED → READY/FAILED) | Must | SDD §8.2 |

#### 3.1.2 Query Processing (FR-QRY)
| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-QRY-01 | System shall accept natural language questions via POST `/api/query/` with optional `topic`, `history`, `agent_id` | Must | SDD §7.1 |
| FR-QRY-02 | System shall respond `202 Accepted` with `task_id` immediately (web never blocks) | Must | SDD §4.2 |
| FR-QRY-03 | System shall reformulate question using conversation history (LLM, temp=0.0) | Must | SDD §8.1 `query/service.py:49-74` |
| FR-QRY-04 | System shall perform hybrid search: vector (pgvector HNSW) + lexical (Whoosh BM25) → RRF (k=60) → MMR (λ=0.7) → recency boost | Must | SDD §8.1 `search.py:22-165` |
| FR-QRY-05 | System shall re-rank top candidates via LLMReranker (1-call JSON 1–10 scores, fallback to RRF) | Must | SDD §8.1 `rerank.py:38-81` |
| FR-QRY-06 | System shall generate answer with strict Spanish system prompt: cite sources `[n]`, no hallucination | Must | SDD §8.1 `query/service.py:26-32` |
| FR-QRY-07 | System shall truncate context to `MAX_CONTEXT_TOKENS` (default 32000) iteratively | Must | SDD §8.1 `query/service.py:259-283` |
| FR-QRY-08 | System shall stream progress via Redis pub/sub (`rag:query:<task_id>`) for SSE | Should | SDD §7.4 |
| FR-QRY-09 | System shall return answer with citations `[n]`, sources (doc, section, page), tokens, cost USD, latency ms, model | Must | SDD §7.1 |

#### 3.1.3 Agent Management (FR-AGT)
| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-AGT-01 | System shall support three agent types: chat (LLM), embedding, reranker | Must | SDD §6.1 |
| FR-AGT-02 | System shall support providers: OpenAI, Anthropic, Google, Mistral, Groq, Ollama, OpenRouter, Custom | Must | SDD §6.1 `providers.py` |
| FR-AGT-03 | System shall store API keys encrypted (Fernet/AES-256) per agent | Must | SDD §10 |
| FR-AGT-04 | System shall support failover chain: primary (is_active) + fallbacks (is_fallback ordered by fallback_order) | Must | SDD §8.3 `services.py:29-42` |
| FR-AGT-04 | System shall test agent config without persisting (`POST /api/agents/test-config/`) | Must | SDD §7.1 |
| FR-AGT-05 | System shall seed 9 demo agents (Google, Groq, Mistral, OpenRouter, Ollama for chat/embedding/reranker) | Must | SDD §8.3 `seed_test_agents.py` |

#### 3.1.4 Topic Isolation (FR-TOP)
| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-TOP-01 | System shall isolate documents by `Topic` (logical namespace) | Must | SDD §6.1 |
| FR-TOP-02 | System shall filter hybrid search by `document_ids` derived from topic | Must | SDD §8.1 `search.py:116-145` |
| FR-TOP-03 | System shall scope conversations to topic (no cross-topic history) | Must | SDD §6.1 |

#### 3.1.5 Cost & Telemetry (FR-TEL)
| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-TEL-01 | System shall log per-query: prompt/completion tokens, total cost USD, latency ms, model used | Must | SDD §6.1 `QueryLog` |
| FR-TEL-02 | System shall estimate cost via `MODEL_PRICING_USD_PER_1M` (configurable) | Must | SDD §8.1 `llm.py:79-82` |
| FR-TEL-03 | System shall expose Prometheus metrics at `/api/metrics/` (`rag_*` counters) | Should | SDD §7.1 |
| FR-TEL-04 | System shall provide offline evaluation harness (`evaluate_rag.py`) with Recall@K, Precision@K, Faithfulness, Relevancy, p95 | Should | SDD §12 |

#### 3.1.6 Admin Dashboard (FR-UI)
| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-UI-01 | System shall provide React/Vite SPA at `:3000` (nginx) | Must | SDD §7.3 |
| FR-UI-02 | Dashboard shall manage agents (CRUD, activate/deactivate, fallback, test) | Must | SDD §7.3 `AgentCard`, `AgentForm` |
| FR-UI-03 | Dashboard shall browse free model catalog with key URLs (8 providers) | Should | SDD §7.3 `FreeModelsCatalog` |
| FR-UI-04 | Dashboard shall configure global retrieval params (chunk_size, top_k, MMR, etc.) | Should | SDD §7.3 `PlatformConfigForm` |
| FR-UI-05 | Dashboard shall upload documents, list, retry, delete, reindex | Must | SDD §7.3 `DocumentsList` |
| FR-UI-06 | Dashboard shall export/import configuration JSON (keys excluded) + localStorage backup | Should | SDD §7.3 `ConfigBackup` |

---

## 4. Interface Requirements

### 4.1 User Interfaces
| Interface | Technology | Description |
|-----------|------------|-------------|
| **Admin Dashboard** | React 18 + Vite + nginx | SPA at `:3000`, tabs: Agents, Free Models, Search, Chat, Documents |
| **Django Admin** | Django Admin | `:8000/admin` — superuser management, DB inspection |
| **Flower** | Celery Flower | `:5555` — worker/task monitoring (basic-auth) |

### 4.2 Software Interfaces (API)
| Interface | Protocol | Format | Endpoints |
|-----------|----------|--------|-----------|
| **REST API** | HTTPS/REST | JSON | 15+ endpoints (see SDD §7.1) |
| **Celery Tasks** | Redis/JSON | JSON | `generate_answer`, `ingest_document`, `embed_chunks_batch` |
| **LLM Providers** | HTTPS/REST | JSON | OpenAI, Anthropic, Google, Mistral, Groq, Ollama, OpenRouter |
| **Pub/Sub** | Redis | JSON | `rag:query:<task_id>` channel |

### 4.3 Hardware Interfaces
- **Network:** HTTP/HTTPS (port 8000, 3000, 5555), PostgreSQL (5432), Redis (6379)
- **Storage:** Docker volumes `pgdata`, `redisdata`, `rag_storage`, `rag_media`

---

## 5. Non-Functional Requirements

### 5.1 Performance (ISO 25010: Time Behavior)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Query latency p50 | ≤ 2.0s | `evaluate_rag.py --offline` |
| Query latency p95 | ≤ 3.5s | `evaluate_rag.py --offline` |
| Ingestion throughput | ≥ 50 pages/min | Manual test |
| Concurrent queries | ≥ 12 (3w × 4t) | Load test |
| Worker horizontal scaling | Linear | `docker compose up --scale worker=N` |

**Measured (offline, 5 Q):** p50=1820ms, p95=3140ms, Recall@5=1.000, Faithfulness=0.980

### 5.2 Reliability (ISO 25010: Availability, Fault Tolerance)
| Requirement | Target | Mechanism |
|-------------|--------|-----------|
| Query success rate | ≥ 99.9% | CircuitBreaker, Failover, retries |
| Worker crash recovery | Auto | `acks_late`, `REJECT_ON_WORKER_LOST` |
| Provider failure | Transparent failover | `FailoverLLMService` (1 try/agent) |
| Data durability | PostgreSQL ACID | pgvector + pgdata volume |

### 5.3 Scalability (ISO 25010: Capacity)
| Dimension | Target | Approach |
|-----------|--------|----------|
| Workers | Horizontal | `--scale worker=N` |
| Vector DB | ~1M vectors | pgvector HNSW; migrate to Pinecone if >1M |
| Documents | Unlimited | Chunk deduplication, pgvector |
| Topics | Unlimited | Logical isolation |

### 5.4 Security (ISO 25010: Confidentiality, Integrity)
| Requirement | Implementation |
|-------------|----------------|
| API Key encryption | Fernet (AES-256) at rest (`agents/crypto.py`) |
| Transport security | TLS at reverse proxy (nginx/Traefik) |
| Rate limiting | DRF throttles: anon 300/min, user 600/min, query 60/min, upload 20/min |
| Secrets management | `.env` excluded from git; `DJANGO_SECRET_KEY` rotated per env |
| Data isolation | Topic-level logical isolation (`document_ids` filter) |

### 5.5 Maintainability (ISO 25010: Modularity, Testability)
| Attribute | Target |
|-----------|--------|
| Test coverage | 43 unit tests passing (`pytest -q`) |
| Modularity | 12 core modules, 5 async tasks, typed |
| Linting | `ruff`/`black` ready |
| Documentation | SDD, SRS, Test Plan, Deployment Manual |

### 5.6 Usability
| Requirement | Implementation |
|-------------|----------------|
| Free model catalog | 8 providers with key URLs, filter chat/embedding |
| Test before save | `Probar API` button in agent form |
| Config backup | Export/import JSON + localStorage |
| Icons | Professional SVG set (no emojis) |

---

## 6. Verification & Validation

| Requirement | Verification Method | Acceptance Criteria |
|-------------|---------------------|---------------------|
| FR-ING-01..10 | Unit + Integration test | `pytest backend/tests/test_documents.py` |
| FR-QRY-01..09 | Unit + E2E test | `pytest backend/tests/test_*.py` + manual curl |
| FR-AGT-01..05 | Unit test | `pytest backend/tests/test_failover.py test_providers.py` |
| FR-TOP-01..03 | Integration test | Upload to topic A, query topic B → no results |
| FR-TEL-01..04 | Evaluation harness | `python evaluate_rag.py --k 5 --offline` |
| NFR Performance | Evaluation harness | p95 ≤ 3.5s, Recall@5 ≥ 0.95 |
| NFR Reliability | Chaos test (kill worker) | Query completes via failover |

---

## 7. Appendices

### Appendix A: Requirements Traceability Matrix (RTM)
| Req ID | SDD Section | Test Case | Status |
|--------|-------------|-----------|--------|
| FR-ING-01 | SDD §8.1 | `test_documents.py::test_upload_accepts` | Pass |
| FR-ING-03 | SDD §8.1 | `test_chunking.py::test_section_aware_splitter` | Pass |
| FR-ING-07 | SDD §8.2 | `test_documents.py::test_upload_retry` | Pass |
| FR-QRY-04 | SDD §8.1 | `test_search.py::test_rrf_*` | Pass |
| FR-QRY-05 | SDD §8.1 | `test_rerank.py::test_rerank_*` | Pass |
| FR-AGT-04 | SDD §8.3 | `test_failover.py::test_failover_llm` | Pass |
| FR-TOP-01 | SDD §6.1 | Manual: topic isolation | Verified |
| FR-TEL-04 | SDD §12 | `evaluate_rag.py --offline` | Pass |

### Appendix B: Glossary
See SDD §13.

### Appendix C: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-01 | Miguel Xlerion | Baseline |

---
*End of SRS v1.0 (IEEE 830)*