# Project Management Plan (PMP)
## Enterprise RAG Assistant
### IEEE 1058-1998 Compliant

---

**Document Control**
- **Title:** Project Management Plan — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Project Manager:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Baseline
- **IEEE Std:** 1058-1998 (IEEE Standard for Software Project Management Plans)

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Project Organization](#2-project-organization)
3. [Project Schedule](#3-project-schedule)
4. [Resource Allocation](#4-resource-allocation)
5. [Budget Estimate](#5-budget-estimate)
6. [Risk Management](#6-risk-management)
7. [Quality Management](#7-quality-management)
8. [Configuration Management](#8-configuration-management)
8. [Communication Plan](#9-communication-plan)
10. [Procurement & External Dependencies](#10-procurement--external-dependencies)
11. [Monitoring & Control](#11-monitoring--control)
12. [Appendices](#12-appendices)

---

## 1. Project Overview

### 1.1 Project Identification
- **Project Name:** Enterprise RAG Assistant
- **Project Code:** ERA-2026-001
- **Repository:** https://github.com/miguelxlerion/Rag_X
- **Start Date:** 2026-08-15
- **Baseline Date:** 2026-09-01
- **Target Completion:** 2026-09-15 (portfolio delivery)

### 1.2 Objectives & Success Criteria
| Objective | Success Metric | Target |
|-----------|----------------|--------|
| Functional RAG pipeline | End-to-end query with citations | 100% FRs implemented |
| Demo-ready deployment | `docker compose up -d` in <5 min | 3 commands |
| Performance | p95 latency | ≤ 3.5s |
| Quality | Recall@5 | ≥ 0.95 |
| Maintainability | Test coverage | 43 unit tests passing |

### 1.3 Scope Summary
**In Scope:** Document ingestion, semantic chunking, hybrid search, LLM re-ranking, async pipeline, topic isolation, admin UI, cost telemetry, evaluation harness, SDLC documentation suite.  
**Out of Scope:** Model fine-tuning, voice I/O, SSO, advanced RBAC, multi-language, mobile app.

---

## 2. Project Organization

### 2.1 Roles & Responsibilities
| Role | Name | Responsibilities |
|------|------|------------------|
| **Project Manager / Lead Developer** | Miguel Xlerion | Architecture, core development, DevOps, documentation, deployment |
| **QA Engineer** | (Self) | Test planning, execution, automation, metrics |
| **DevOps Engineer** | (Self) | Docker, CI/CD, monitoring, scaling |
| **Technical Writer** | (Self) | SRS, SDD, SRS, Test Plan, user docs, SDLC suite |

### 2.2 Organizational Structure
```
Project Manager (Miguel Xlerion)
    │
    ├─ Development (Backend: Django/DRF/Celery, Frontend: React/Vite)
    ├─ QA / Testing (pytest, evaluate_rag.py, manual E2E)
    ├─ DevOps / Infra (Docker Compose, Dockerfile, nginx, volumes)
    ├─ Documentation (SDD, SRS, PMP, Risk, QA, Test Plan, Ops Manual)
    └─ Deployment / Release (GitHub, Docker Hub, README)
```

### 2.3 Stakeholders
| Stakeholder | Interest | Communication |
|-------------|----------|---------------|
| Portfolio Reviewers | Code quality, architecture, documentation | GitHub repo, README, SDLC docs |
| Technical Interviewers | Live demo, architecture discussion | Running demo, CASE_STUDY |
| Future Employers | Production readiness | SDD, SRS, Test Plan, Ops Manual |

---

## 3. Project Schedule

### 3.1 Milestones
| Milestone | Target Date | Status |
|-----------|-------------|--------|
| M1: Project Initiation & Repo Setup | 2026-08-15 | ✅ Done |
| M2: Core Architecture (Django, Celery, pgvector, Redis) | 2026-08-20 | ✅ Done |
| M3: Document Ingestion Pipeline (extract, chunk, embed) | 2026-08-25 | ✅ Done |
| M4: Hybrid Search + RRF + MMR | 2026-08-28 | ✅ Done |
| M5: LLM Re-ranking + Failover | 2026-08-30 | ✅ Done |
| M5: Admin Dashboard (React/Vite) | 2026-09-01 | ✅ Done |
| M6: Free Models Catalog + Test Config | 2026-09-01 | ✅ Done |
| M7: Evaluation Harness + Metrics | 2026-09-01 | ✅ Done |
| M8: SDD (IEEE 1016) | 2026-09-01 | ✅ Done |
| M9: SRS (IEEE 830) | 2026-09-01 | ✅ Done |
| M10: PMP (IEEE 1058) | 2026-09-01 | ✅ Done |
| M11: Risk, QA, Test Plan, Ops Manual | 2026-09-02 | 🔄 In Progress |
| M12: SDLC Suite Complete + GitHub Push | 2026-09-02 | 🔄 In Progress |
| M13: Portfolio Demo Ready | 2026-09-03 | ⏳ Pending |

### 3.2 Work Breakdown Structure (WBS)
| WBS ID | Work Package | Duration | Dependencies |
|--------|--------------|----------|--------------|
| 1.1 | Repository & Docker Setup | 1 day | — |
| 1.2 | Core Models & Migrations | 1 day | 1.1 |
| 1.3 | Ingestion Pipeline (extract, chunk, embed) | 3 days | 1.2 |
| 1.4 | Hybrid Search (pgvector + Whoosh + RRF + MMR) | 2 days | 1.2 |
| 1.5 | LLM Integration + Failover + Circuit Breaker | 2 days | 1.2 |
| 1.6 | Query Pipeline (reformulate → search → rerank → generate) | 2 days | 1.3, 1.4, 1.5 |
| 1.7 | Topic Isolation + Cost Telemetry | 1 day | 1.3, 1.6 |
| 1.7 | Admin Dashboard (React/Vite) | 3 days | 1.2 |
| 1.8 | Free Models Catalog + Test Config | 1 day | 1.7 |
| 1.9 | Evaluation Harness | 1 day | 1.6 |
| 1.10 | SDD (IEEE 1016) | 1 day | 1.1-1.9 |
| 1.11 | SRS (IEEE 830) | 1 day | 1.10 |
| 1.12 | PMP (IEEE 1058) | 1 day | 1.10 |
| 1.13 | Risk Management Plan | 0.5 day | 1.10 |
| 1.14 | QA Plan (IEEE 730) | 0.5 day | 1.10 |
| 1.15 | Test Plan (IEEE 829) | 0.5 day | 1.10 |
| 1.16 | Configuration Management Plan | 0.5 day | 1.10 |
| 1.17 | Deployment & Ops Manual | 0.5 day | 1.10 |
| 1.18 | Maintenance Plan | 0.5 day | 1.10 |
| 1.19 | RTM (Traceability) | 0.5 day | All above |
| 1.20 | Final Review + GitHub Push | 0.5 day | 1.11-1.19 |

**Total Estimated Effort:** ~22 person-days (single developer)

---

## 4. Resource Allocation

### 4.1 Human Resources
| Resource | Role | Allocation |
|----------|------|------------|
| Miguel Xlerion | PM, Dev, QA, DevOps, Docs | 100% (single contributor) |

### 4.2 Technical Resources
| Resource | Specification | Purpose |
|----------|---------------|---------|
| **Development Machine** | Windows 11 + Docker Desktop | Local dev |
| **GitHub** | Private/Public repo | Source control, CI/CD |
| **Docker Hub** | Base images | `pgvector/pgvector:pg16`, `python:3.12-slim`, `node:22-alpine`, `nginx:1.27-alpine`, `redis:7-alpine` |
| **LLM Providers** | API keys | OpenAI, Anthropic, Google, Mistral, Groq, Ollama, OpenRouter |
| **Monitoring** | Flower, Prometheus | Observability |

### 4.3 Software Licenses
| Component | License |
|-----------|---------|
| Django, DRF, Celery, pgvector, Whoosh, Redis, React, Vite, nginx | BSD / MIT / Apache 2.0 (permissive) |
| Project code | MIT (portfolio) |

---

## 5. Budget Estimate

### 5.1 Development Cost (Internal)
| Category | Effort (days) | Rate (€/day) | Cost (€) |
|----------|---------------|--------------|----------|
| Development | 14 | Internal | — |
| Testing & QA | 3 | Internal | — |
| Documentation (SDLC suite) | 4 | Internal | — |
| DevOps / Deployment | 1 | Internal | — |
| **Total** | **22** | | **Internal effort only** |

### 5.2 Operational Cost (Monthly — Demo Scale)
| Resource | Specification | Monthly Cost (€) |
|----------|---------------|------------------|
| **VPS / Cloud** | 2 vCPU, 4GB RAM, 50GB SSD | ~20-40 |
| **LLM API (demo)** | ~500 queries/mo @ avg $0.002 | ~1-5 |
| **Domain + TLS** | Let's Encrypt / Cloudflare | 0 |
| **Total** | | **~21-45 €/mo** |

### 5.3 Production Scale Projection (from SDD §9.3)
| Users | Monthly Infra | LLM API | Total |
|-------|---------------|---------|-------|
| 100 | €20-40 | €30 | €50-70 |
| 1,000 | €80-150 | €300 | €380-450 |
| 10,000 | €400-800 | €3,000 | €3,400-3,800 |

---

## 6. Risk Management

### 6.1 Risk Register
| Risk ID | Description | Probability | Impact | Score | Mitigation Strategy | Owner |
|---------|-------------|-------------|--------|-------|---------------------|-------|
| R1 | LLM provider API changes / deprecation | Medium | High | 15 | Multi-provider abstraction (`providers.py`), Failover chain, version pinning | Dev |
| R2 | pgvector HNSW performance degrades >1M vectors | Low | High | 10 | Monitor `vector_embeddings` count; migration plan to Pinecone/Qdrant | DevOps |
| R3 | Docker Desktop license / compatibility issues | Low | Medium | 6 | Test on Linux server; provide Linux deploy instructions | DevOps |
| R4 | LLM provider rate limits / quota exhaustion | Medium | Medium | 12 | CircuitBreaker, exponential backoff, multiple providers, usage monitoring | Dev |
| R5 | Data loss (DB corruption, volume loss) | Low | Critical | 15 | Daily pg_dump to S3/NFS; Redis AOF + RDB; test restore quarterly | DevOps |
| R6 | Security vulnerability in dependencies | Medium | High | 15 | `pip-audit` monthly; `dependabot` alerts; pinned versions in requirements.txt | Dev |
| R7 | Single point of failure (single developer) | High | High | 20 | Comprehensive documentation (SDLC suite), automated tests, runbooks | PM |
| R8 | Scope creep (adding features beyond MVP) | Medium | Medium | 12 | Strict scope baseline; change control via GitHub Issues | PM |
| R9 | LLM cost overrun (unmonitored usage) | Medium | Medium | 12 | Per-query cost logging, `MODEL_PRICING` config, budget alerts | Dev |
| R10 | Knowledge loss (no documentation) | Low | High | 10 | **This SDLC suite** (SDD, SRS, PMP, Ops Manual, Test Plan) | PM |

### 6.2 Risk Monitoring
- **Frequency:** Weekly review during active development; monthly post-launch
- **Escalation:** Risks with score ≥15 → immediate mitigation action
- **Tracking:** GitHub Issues labeled `risk` with labels `probability:X`, `impact:Y`

---

## 7. Quality Management

### 7.1 Quality Standards
| Standard | Application |
|----------|-------------|
| ISO/IEC 25010 | Quality model (performance, reliability, security, maintainability) |
| IEEE 829 | Test Plan & Test Cases |
| IEEE 830 | SRS |
| IEEE 1016 | SDD |
| IEEE 1058 | This PMP |
| IEEE 730 | QA Plan |
| IEEE 1061 | Quality Metrics |

### 7.2 Quality Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| **Code Coverage** | ≥ 80% (unit) | `pytest --cov` |
| **Defect Density** | < 0.5/KLOC | GitHub Issues / KLOC |
| **Test Pass Rate** | 100% (unit) | `pytest -q` |
| **Performance** | p95 ≤ 3.5s | `evaluate_rag.py` |
| **Security** | 0 critical vulns | `pip-audit`, `dependabot` |

### 7.3 Reviews & Audits
| Review | Frequency | Participants |
|--------|-----------|--------------|
| Code Review | Per PR (self-review) | PM/Dev |
| Architecture Review | Milestone gates | PM |
| Security Audit | Monthly | Dev |
| Documentation Review | Per deliverable | PM |

---

## 8. Configuration Management

### 8.1 Version Control
- **Tool:** Git (GitHub)
- **Branching Strategy:** Trunk-based (`master` only, feature branches short-lived)
- **Commit Convention:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **Tagging:** Semantic versioning (`v1.0.0`, `v1.1.0`)

### 8.2 Baselines
| Baseline | Artifacts | Trigger |
|----------|-----------|---------|
| **Architecture Baseline** | SDD, docker-compose.yml, core models | M2 |
| **Functional Baseline** | All FRs implemented, tests passing | M7 |
| **Documentation Baseline** | SDLC suite complete | M12 |
| **Release Baseline** | Tagged release, demo ready | M13 |

### 8.3 Change Control
| Change Type | Process |
|-------------|---------|
| **Bug Fix** | Branch → PR → Tests → Merge → Tag patch |
| **Feature** | Issue → Branch → PR → Review → Tests → Merge → Tag minor |
| **Breaking Change** | Issue → Design doc → PR → Review → Tests → Tag major |
| **Emergency Hotfix** | Hotfix branch → Tests → Direct merge → Tag patch |

### 8.4 Configuration Items (CI)
| CI | Repository Path | Versioning |
|----|-----------------|------------|
| Source Code | `backend/`, `frontend/`, `scripts/` | Git |
| Infrastructure | `docker-compose.yml`, `Dockerfile*`, `nginx.conf` | Git |
| Configuration | `.env.example`, `.env` (local only), `settings.py` | Git (template) |
| Documentation | `*.md`, `docs/` | Git |
| Test Data | `data/eval_questions.json` | Git |
| Container Images | Docker Hub / GHCR | Semantic tags |

---

## 9. Communication Plan

| Meeting / Artifact | Frequency | Audience | Channel |
|--------------------|-----------|----------|---------|
| **Daily Standup** | Daily (dev days) | PM/Dev | Local notes |
| **Milestone Review** | Per milestone | PM | GitHub Milestone |
| **Code Commit** | Continuous | GitHub | GitHub notifications |
| **Issue Triage** | Weekly | PM | GitHub Issues |
| **Security Alert** | Immediate | PM | Dependabot / email |
| **Documentation Update** | Per doc | PM | Git commit |

---

## 10. Procurement & External Dependencies

### 10.1 External Services
| Dependency | Provider | Contract Type | Fallback |
|------------|----------|---------------|----------|
| **OpenAI API** | OpenAI | Pay-per-use | Anthropic, Groq, OpenRouter |
| **Anthropic API** | Anthropic | Pay-per-use | OpenAI, Groq |
| **Google Gemini API** | Google | Free tier / Pay-per-use | OpenAI, Mistral |
| **Mistral API** | Mistral | Pay-per-use | OpenRouter, Groq |
| **Groq API** | Groq | Free tier | OpenRouter, Ollama |
| **Ollama** | Local | Self-hosted | — |
| **OpenRouter** | OpenRouter | Free tier / Pay-per-use | Direct providers |
| **Docker Hub** | Docker Inc. | Free tier | GHCR, self-hosted registry |

### 10.2 Open Source Components (requirements.txt)
All permissive licenses (BSD, MIT, Apache 2.0). No copyleft dependencies.

---

## 11. Monitoring & Control

### 11.1 KPIs
| KPI | Target | Source |
|-----|--------|--------|
| **Velocity** | ~5 story points/day | GitHub Projects |
| **Defect Escape Rate** | 0 to production | GitHub Issues |
| **Build Success Rate** | 100% | Docker build logs |
| **Test Pass Rate** | 100% | `pytest -q` |
| **Documentation Completeness** | 100% SDLC docs | Checklist |

### 11.2 Reporting
| Report | Frequency | Format |
|--------|-----------|--------|
| **Burndown** | Daily (dev) | GitHub Milestone |
| **Risk Status** | Weekly | GitHub Issues `risk` |
| **Quality Dashboard** | Per release | `pytest --cov`, `evaluate_rag.py` |
| **Cost Report** | Monthly | `QueryLog` aggregation |

### 11.3 Corrective Actions
| Trigger | Action |
|---------|--------|
| Test failure | Block merge, fix before merge |
| Performance regression | Revert, investigate, optimize |
| Security vuln | Immediate patch, deploy |
| Cost overrun | Alert, switch to cheaper provider |

---

## 12. Appendices

### Appendix A: Glossary
See SDD §13.

### Appendix B: References
- SDD.md (IEEE 1016)
- SRS.md (IEEE 830)
- Risk_Management_Plan.md
- QA_Plan.md
- Test_Plan.md
- Deployment_Operations_Manual.md
- Maintenance_Plan.md
- RTM.md

### Appendix C: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-01 | Miguel Xlerion | Baseline |

---
*End of PMP v1.0 (IEEE 1058)*