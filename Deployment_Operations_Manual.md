# Deployment & Operations Manual
## Enterprise RAG Assistant
### ITIL / ISO 20000 / DevOps Compliant

---

**Document Control**
- **Title:** Deployment & Operations Manual — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Author:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Baseline

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Prerequisites](#3-prerequisites)
4. [Installation & Deployment](#4-installation--deployment)
5. [Configuration](#5-configuration)
6. [Service Management](#6-service-management)
7. [Monitoring & Observability](#7-monitoring--observability)
8. [Backup & Disaster Recovery](#8-backup--disaster-recovery)
9. [Security Operations](#9-security-operations)
10. [Troubleshooting](#10-troubleshooting)
11. [Runbooks](#11-runbooks)
12. [Appendices](#12-appendices)

---

## 1. Introduction

### 1.1 Purpose
This manual provides comprehensive procedures for deploying, operating, monitoring, and maintaining the Enterprise RAG Assistant in production.

### 1.2 Scope
Covers: initial deployment, configuration, day-to-day operations, monitoring, backup/recovery, security, and troubleshooting for the 7-service Docker Compose stack.

### 1.3 Audience
- DevOps Engineers
- System Administrators
- Developers (for local deployment)
- Support Engineers

### 1.4 References
- SDD.md §4, §9
- SRS.md §4, §5
- PMP.md §9, §10
- docker-compose.yml, Dockerfile*, nginx.conf

---

## 2. System Architecture Overview

### 2.1 Service Topology (7 Services)
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

### 2.2 Service Details
| Service | Container | Port | Healthcheck | Depends On |
|---------|-----------|------|-------------|------------|
| **db** | `pgvector/pgvector:pg16` | 5432 | `pg_isready` | — |
| **redis** | `redis:7-alpine` | 6379 | `redis-cli ping` | — |
| **migrate** | `backend` | — | Exit 0 | db:healthy |
| **web** | `backend` | 8000 | HTTP `/api/health` | migrate, redis |
| **worker** | `backend` | — | Celery inspect | migrate, redis |
| **beat** | `backend` | — | Celery inspect | redis |
| **flower** | `backend` | 5555 | HTTP `/` | redis |
| **admin** | `frontend` (nginx) | 3000 | HTTP `/` | web |

### 2.3 Data Flows
1. **Ingestion:** Upload → `web` → Redis queue `ingestion` → `worker` → extract/chunk → Redis queue `embeddings` (chord) → `worker` → pgvector + Whoosh → `finalize_ingestion`
2. **Query:** `POST /api/query/` → `web` → Redis queue `llm` → `worker` → reformulate → hybrid search → rerank → LLM → `QueryLog` → Redis pub/sub `rag:query:<task_id>` → SSE to frontend

---

## 3. Prerequisites

### 3.1 System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 vCPU | 4 vCPU |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 20 GB | 50 GB SSD |
| **OS** | Linux (Ubuntu 22.04+) / Windows 11 + Docker Desktop | Linux |
| **Docker** | 24.0+ | 24.0+ |
| **Docker Compose** | v2.20+ | v2.20+ |

### 3.2 External Dependencies
| Dependency | Purpose | Required |
|------------|---------|----------|
| **LLM Provider API Key** | At least one (OpenAI, Anthropic, Google, Mistral, Groq, OpenRouter, Ollama) | Yes (for queries) |
| **Domain + TLS** | Production HTTPS | Recommended |
| **S3/NFS for Backups** | pg_dump storage | Production only |

---

## 4. Installation & Deployment

### 4.1 Quick Start (Development / Demo)
```bash
# 1. Clone repository
git clone https://github.com/miguelxlerion/Rag_X.git
cd Rag_X

# 2. Configure environment
cp .env.example .env
# Edit .env: add at least one LLM API key (e.g., OPENAI_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY)

# 3. Build and start
docker compose build
docker compose up -d

# 4. Wait for migration (check logs)
docker compose logs -f migrate
# Should see: "Applying documents.0006_topic... OK" then "156 static files copied"

# 5. Create admin user (optional, for Django Admin)
docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
U = get_user_model()
U.objects.filter(username='admin').exists() or U.objects.create_superuser('admin','admin@demo.local','admin123')
print('admin / admin123 ready')
"

# 6. Verify
curl http://localhost:8000/api/health/
# {"status":"ok","database":"ok","redis":"ok","vector_embeddings":0}

# 7. Access UIs
open http://localhost:3000    # Panel Admin
open http://localhost:8000    # API root
open http://localhost:5555    # Flower (admin / admin123)
open http://localhost:8000/admin  # Django Admin (admin / admin123)
```

### 4.2 Production Deployment Checklist
- [ ] **Server:** 2+ vCPU, 8GB RAM, 50GB SSD, Ubuntu 22.04+
- [ ] **Docker:** Installed, user in `docker` group
- [ ] **Domain:** A record → server IP
- [ ] **TLS:** Reverse proxy (nginx/Traefik) with Let's Encrypt cert
- [ ] **Firewall:** Only 80/443 (proxy), 5555 (Flower, restrict IP), 22 (SSH)
- [ ] **Environment:** `.env` with production secrets (rotate `DJANGO_SECRET_KEY`)
- [ ] **LLM Keys:** At least one provider key in `.env` or via Admin UI
- [ ] **Backups:** S3/NFS mount for pg_dump
- [ ] **Monitoring:** Prometheus/Grafana or Flower + logs
- [ ] **Log Rotation:** Configured (Docker json-file driver max-size)

### 4.3 Deployment Commands
```bash
# Initial deploy
git clone https://github.com/miguelxlerion/Rag_X.git
cd Rag_X
cp .env.example .env
# Edit .env with production values
docker compose build
docker compose up -d

# Update / Redeploy
git pull
docker compose build
docker compose up -d --remove-orphans

# Scale workers
docker compose up -d --scale worker=4

# View logs
docker compose logs -f web
docker compose logs -f worker
docker compose logs -f flower
```

---

## 5. Configuration

### 5.1 Environment Variables (`.env`)
| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | `change-me...` | **Must rotate for production** |
| `DJANGO_DEBUG` | `1` | Set `0` in production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Set to your domain(s) |
| `POSTGRES_DB/USER/PASSWORD` | `rag/rag/rag` | DB credentials |
| `POSTGRES_HOST` | `db` | Internal Docker DNS |
| `REDIS_URL` | `redis://redis:6379/0` | Broker + cache |
| `OPENAI_API_KEY` | `sk-...` | Fallback LLM key |
| `ANTHROPIC_API_KEY` | | Anthropic key |
| `GOOGLE_API_KEY` | | Google Gemini key |
| `MISTRAL_API_KEY` | | Mistral key |
| `GROQ_API_KEY` | | Groq key |
| `OPENROUTER_API_KEY` | | OpenRouter key |
| `FLOWER_PASSWORD` | `admin123` | Flower basic-auth (matches Django Admin) |
| `CHUNK_SIZE` | `800` | Token chunk size |
| `CHUNK_OVERLAP` | `80` | Token overlap |
| `HYBRID_TOP_K` | `20` | Vector+BM25 candidates |
| `RERANK_TOP_K` | `5` | Post-rerank contexts |
| `MAX_CONTEXT_TOKENS` | `32000` | LLM context budget |
| `USE_SEMANTIC_GUARD` | `0` | Drift guard (costly) |
| `ENABLE_OCR` | `0` | Tesseract for scanned PDFs |

### 5.2 Agent Configuration (via Admin UI)
1. Open `http://localhost:3000` → **Agentes IA**
2. Click **+ Nuevo agente** or use **✨ Crear agentes prueba**
3. Configure per agent:
   - **Nombre, Tipo** (chat/embedding/reranker)
   - **Proveedor** (OpenAI, Google, Groq, Mistral, Ollama, OpenRouter, Custom)
   - **Modelo** (select from catalog or type custom)
   - **API Key** (per-agent, encrypted) — click **🔌 Probar API** before saving
   - **Parámetros:** temperature, max_tokens, top_k, system_prompt (chat), embedding_dim (embedding)
   - **Failover:** `is_fallback`, `fallback_order`
4. Activate one chat + one embedding agent minimum

### 5.3 Free Models (No Credit Card)
| Provider | Models | Key URL |
|----------|--------|---------|
| **Google** | `gemini-2.0-flash`, `text-embedding-004` | https://aistudio.google.com/app/apikey |
| **Groq** | `llama-3.3-70b-versatile`, `gemma2-9b-it` | https://console.groq.com/keys |
| **Mistral** | `mistral-small-latest`, `mistral-embed` | https://console.mistral.ai/api-keys |
| **OpenRouter** | `meta-llama/llama-3.3-70b-instruct:free`, `google/gemini-2.0-flash-exp:free` | https://openrouter.ai/keys |
| **Ollama** | `llama3.2`, `nomic-embed-text` (local) | https://ollama.com/download |

---

## 6. Service Management

### 6.1 Service Control
```bash
# Status
docker compose ps

# Logs (follow)
docker compose logs -f web
docker compose logs -f worker
docker compose logs -f flower

# Restart single service
docker compose restart web
docker compose restart worker

# Stop all
docker compose down

# Stop + remove volumes (DATA LOSS!)
docker compose down -v

# Rebuild single service
docker compose build web
docker compose up -d web
```

### 6.2 Celery Worker Management
```bash
# Inspect workers
docker compose exec worker celery -A config inspect active
docker compose exec worker celery -A config inspect registered

# Queue lengths
docker compose exec worker celery -A config inspect active_queues

# Purge queue (careful!)
docker compose exec worker celery -A config purge

# Flower UI: http://localhost:5555 (admin / admin123)
```

### 6.3 Database Management
```bash
# Django shell
docker compose exec web python manage.py shell

# Run migrations manually
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static
docker compose exec web python manage.py collectstatic --noinput

# Database backup (pg_dump)
docker compose exec db pg_dump -U rag rag > backup_$(date +%F).sql

# Restore
docker compose exec -T db psql -U rag rag < backup_2026-09-01.sql
```

---

## 7. Monitoring & Observability

### 7.1 Health Endpoints
| Endpoint | Purpose | Expected |
|----------|---------|----------|
| `GET /api/health/` | Overall health | `{"status":"ok","database":"ok","redis":"ok","vector_embeddings":N}` |
| `GET /api/metrics/` | Prometheus metrics | `rag_*` counters |
| `GET /api/health/` (Flower) | Flower UI | HTML page |
| `GET /` (Admin) | Admin UI | HTML page |

### 7.2 Key Metrics to Monitor
| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| **API Health** | `/api/health/` | `status != "ok"` |
| **Query Latency p95** | `QueryLog.latency_ms` (p95) | > 5s |
| **Query Success Rate** | `QueryLog` count vs errors | < 99% |
| **Worker Queue Depth** | Flower / `celery inspect` | > 100 pending |
| **DB Connections** | `pg_stat_activity` | > 80% of max |
| **Redis Memory** | `redis-cli info memory` | > 80% maxmemory |
| **Disk Usage** | `df -h` | > 80% |
| **LLM Cost/Day** | `QueryLog.total_cost_usd` sum | > Budget |

### 7.3 Logging
```bash
# Application logs (stdout)
docker compose logs -f web
docker compose logs -f worker

# Celery Flower UI
open http://localhost:5555  # admin / admin123

# Django logs (in web container)
docker compose exec web tail -f /var/log/django.log  # if configured
```

### 7.4 Prometheus Metrics (via `/api/metrics/`)
```
rag_documents_total
rag_documents_status{status="ready"}
rag_chunks_total
rag_embeddings_total
rag_queries_total
rag_query_latency_seconds_bucket
rag_query_cost_usd_total
rag_worker_queue_length
```

---

## 8. Backup & Disaster Recovery

### 8.1 Backup Strategy
| Asset | Method | Frequency | Retention | Location |
|-------|--------|-----------|-----------|----------|
| **PostgreSQL** | `pg_dump` (custom format) | Daily 02:00 UTC | 30 days | S3 / NFS |
| **Redis** | RDB + AOF (auto) | Continuous | 7 days | Volume `redisdata` |
| **Docker Volumes** | `docker volume backup` | Weekly | 4 weeks | S3 / NFS |
| **Configuration** | `.env`, `docker-compose.yml` | On change | Infinite | Git (secrets excluded) |

### 8.2 Backup Script (Cron)
```bash
#!/bin/bash
# /usr/local/bin/backup_rag.sh
set -euo pipefail

DATE=$(date +%F_%H-%M)
DB_DUMP="/backups/rag_db_${DATE}.dump"
pg_dump -h db -U rag -Fc rag > "${DB_DUMP}"
gzip "${DB_DUMP}"

# Upload to S3 (requires awscli configured)
aws s3 cp "${DB_DUMP}.gz" s3://my-bucket/rag-backups/

# Retention
find /backups -name "rag_db_*.dump.gz" -mtime +30 -delete
```

### 8.3 Restore Procedures
#### 8.3.1 Full Restore (RTO: 2h, RPO: 24h)
```bash
# 1. Stop services
docker compose down

# 2. Restore DB
docker compose up -d db
docker compose exec -T db pg_restore -U rag -d rag /backup/rag_db_latest.dump

# 3. Restore volumes (if needed)
docker volume create rag_media
docker volume create rag_storage
# Restore from volume backups

# 4. Start all
docker compose up -d

# 5. Verify
curl http://localhost:8000/api/health/
```

#### 8.3.2 Point-in-Time Recovery
```bash
# Use pg_dump with --create --clean for full schema+data
# Or use WAL archiving for true PITR (not configured by default)
```

### 8.4 Recovery Time Objectives
| Scenario | RTO | RPO |
|----------|-----|-----|
| **Full System Restore** | 2 hours | 24 hours |
| **DB Only Restore** | 30 minutes | 24 hours |
| **Single Table Restore** | 15 minutes | 24 hours |
| **Worker Failure** | Auto (Celery retries) | 0 |
| **Web Failure** | Auto (Docker restart) | 0 |

---

## 9. Security Operations

### 9.1 Credential Management
| Credential | Storage | Rotation |
|------------|---------|----------|
| **Django SECRET_KEY** | `.env` (env var) | Every 90 days |
| **LLM API Keys** | Per-agent (Fernet encrypted in DB) | Per provider policy |
| **DB Password** | `.env` | Every 90 days |
| **Flower Password** | `.env` (`FLOWER_PASSWORD`) | Every 90 days |
| **TLS Certs** | Reverse proxy (Let's Encrypt) | Auto (90 days) |

### 9.2 Security Checklist (Monthly)
- [ ] `pip-audit` — no critical vulnerabilities
- [ ] Dependabot — all alerts resolved
- [ ] `grep -r "sk-\|api_key" docker compose logs` — no keys leaked
- [ ] TLS cert valid + HSTS enabled
- [ ] Rate limiting effective (test 429)
- [ ] API keys rotated per provider schedule
- [ ] Backup restore tested (quarterly)

### 9.3 Incident Response
| Severity | Response | Escalation |
|----------|----------|------------|
| **Critical** (data breach, downtime) | Immediate isolation, forensic snapshot, notify | PM → Stakeholders |
| **High** (data loss, auth bypass) | Isolate, patch, redeploy | PM |
| **Medium** (performance, minor bug) | Patch in next sprint | PM |
| **Low** (cosmetic, doc) | Next release | — |

---

## 10. Troubleshooting

### 10.1 Common Issues

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| **`/api/health/` → `vector_embeddings: 0`** | No documents ingested | Upload docs via Admin UI |
| **Query returns "degraded"** | LLM provider down | Check Flower → worker logs; verify API keys |
| **Worker stuck / queue growing** | LLM timeout / rate limit | Check Flower → worker logs; increase `LLM_TIMEOUT` |
| **`401` on Flower** | Wrong password | Use `admin` / `admin123` (or `FLOWER_PASSWORD`) |
| **`401` on Django Admin** | Wrong credentials | Use `admin` / `admin123` |
| **`500` on `/api/query/`** | LLM error / circuit open | Check worker logs; check circuit breaker state |
| **Document stuck `PROCESSING`** | Celery worker down | `docker compose restart worker` |
| **`vector_embeddings` dim mismatch** | Changed embedding model | Run **Reindexar todo** in Admin UI or change dim back |
| **Out of memory (OOM)** | Large docs / many workers | Reduce `worker` concurrency, increase RAM |
| **Disk full** | Logs / volumes / backups | `docker system prune -f`, rotate logs |

### 10.2 Diagnostic Commands
```bash
# Full stack status
docker compose ps

# Service logs (last 100 lines)
docker compose logs --tail=100 web
docker compose logs --tail=100 worker

# Celery worker status
docker compose exec worker celery -A config inspect active
docker compose exec worker celery -A config inspect stats

# Database connectivity
docker compose exec web python -c "import psycopg2; print(psycopg2.connect('postgresql://rag:rag@db:5432/rag').close())"

# Redis connectivity
docker compose exec redis redis-cli ping

# Disk space
df -h
docker system df

# Network connectivity (from web container)
docker compose exec web curl -s http://db:5432  # should fail (TCP)
docker compose exec web curl -s http://redis:6379  # should fail (TCP)
```

### 10.3 Log Analysis
```bash
# Search for errors
docker compose logs web 2>&1 | grep -i error
docker compose logs worker 2>&1 | grep -i error

# Search for specific query
docker compose logs worker 2>&1 | grep "task_id"

# Circuit breaker state
docker compose logs worker 2>&1 | grep -i "circuit\|breaker"

# Rate limit hits
docker compose logs web 2>&1 | grep "429"
```

---

## 11. Runbooks

### 11.1 RB-001: Deploy New Version
**Trigger:** New release tag pushed
**Steps:**
1. `git pull && git checkout vX.Y.Z`
2. `docker compose build`
3. `docker compose up -d --remove-orphans`
4. `curl http://localhost:8000/api/health/`
5. `python evaluate_rag.py --k 5 --offline`
6. Verify Admin UI loads
7. Tag release: `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`

### 11.2 RB-002: Scale Workers
**Trigger:** High queue depth, latency spike
**Steps:**
1. `docker compose up -d --scale worker=4` (or desired count)
2. Verify in Flower: `http://localhost:5555` → Workers
3. Monitor latency: `curl /api/metrics/`

### 11.3 RB-003: Rotate Secrets
**Trigger:** 90-day rotation / security incident
**Steps:**
1. Generate new `DJANGO_SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
2. Update `.env` with new key
3. `docker compose restart web worker beat flower`
4. Rotate LLM API keys in Admin UI (per agent → edit → new key → **Probar API** → save)
5. Update `.env` fallback keys (`OPENAI_API_KEY`, etc.)
6. `docker compose restart web worker`
6. Verify queries work

### 11.4 RB-004: Full Disaster Recovery
**Trigger:** Data center loss, catastrophic failure
**Steps:**
1. Provision new server (meet prerequisites §3.1)
2. `git clone https://github.com/miguelxlerion/Rag_X.git`
3. `cp .env.example .env` → populate with restored secrets
3. `docker compose build`
4. `docker compose up -d db redis`
5. Restore DB from latest `pg_dump` (see §8.3.1)
6. `docker compose up -d`
7. Verify health, run evaluation harness

### 11.5 RB-005: Add LLM Provider
**Trigger:** New provider needed
**Steps:**
1. Add provider to `backend/core/providers.py` (`PROVIDER_LABELS`, `OPENAI_COMPATIBLE_BASE_URLS`, `ENV_KEY_BY_PROVIDER`)
2. Add to `CHAT_PROVIDERS` / `EMBEDDING_PROVIDERS` sets
3. Add models to `frontend/src/types.ts` (`MODELS_BY_PROVIDER`, `PROVIDER_KEY_URL`, `PROVIDER_DOCS_URL`)
3. Add to `FreeModelsCatalog` if free tier exists
4. Rebuild frontend: `cd frontend && npm run build`
4. `docker compose build admin && docker compose up -d admin`
5. Test via Admin UI → **Modelos Gratis** → **Usar este modelo**

---

## 12. Appendices

### Appendix A: Service Ports Reference
| Service | Internal Port | External Port | Protocol |
|---------|---------------|---------------|----------|
| PostgreSQL | 5432 | — (internal) | TCP |
| Redis | 6379 | — (internal) | TCP |
| Web (API) | 8000 | 8000 | HTTP |
| Admin (nginx) | 80 | 3000 | HTTP |
| Flower | 5555 | 5555 | HTTP |

### Appendix B: Volume Mapping
| Volume | Mount Path | Purpose |
|--------|------------|---------|
| `pgdata` | `/var/lib/postgresql/data` | PostgreSQL data |
| `redisdata` | `/data` | Redis persistence |
| `rag_storage` | `/app/storage` | Whoosh index, Celery beat schedule |
| `rag_media` | `/app/media` | Uploaded documents |

### Appendix C: Key File Locations (in containers)
| File | Container | Path |
|------|-----------|------|
| `.env` | web, worker, beat, flower | `/app/.env` |
| `settings.py` | web, worker, beat, flower | `/app/backend/config/settings.py` |
| Whoosh index | web, worker | `/app/storage/whoosh/` |
| Celery beat schedule | beat | `/app/storage/celerybeat-schedule` |
| Uploaded files | web, worker | `/app/media/ingest/` |
| Static files | web, admin | `/app/staticfiles/`, `/usr/share/nginx/html/` |

### Appendix D: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-01 | Miguel Xlerion | Baseline |

---
*End of Deployment & Operations Manual v1.0*