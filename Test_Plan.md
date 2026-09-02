# Test Plan
## Enterprise RAG Assistant
### IEEE 829-2008 Compliant

---

**Document Control**
- **Title:** Test Plan — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Author:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Baseline
- **IEEE Std:** 829-2008 (IEEE Standard for Software Test Documentation)

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Test Items](#2-test-items)
3. [Features to be Tested](#3-features-to-be-tested)
4. [Features Not to be Tested](#4-features-not-to-be-tested)
5. [Test Approach](#5-test-approach)
6. [Test Deliverables](#6-test-deliverables)
7. [Test Environment](#7-test-environment)
8. [Test Schedule](#8-test-schedule)
8. [Test Organization](#9-test-organization)
10. [Risks & Contingencies](#10-risks--contingencies)
11. [Approval](#11-approval)
12. [Appendices](#12-appendices)

---

## 1. Introduction

### 1.1 Purpose
This Test Plan defines the strategy, scope, resources, schedule, and deliverables for testing the Enterprise RAG Assistant. It covers unit, integration, system, performance, security, and acceptance testing.

### 1.2 Scope
**In Scope:** All functional requirements (FR-ING, FR-QRY, FR-AGT, FR-TOP, FR-TEL, FR-UI), non-functional requirements (performance, reliability, security, maintainability), and deployment validation.
**Out of Scope:** Model fine-tuning accuracy, third-party LLM provider internals, hardware failure testing, regulatory compliance certification.

### 1.3 Standards & References
- IEEE 829-2008 (Test Documentation)
- IEEE 829-2008 Annex A (Test Case Specification Template)
- ISO/IEC 25010 (Quality Model)
- SRS.md (Requirements), SDD.md (Design), QA_Plan.md

---

## 2. Test Items

| Test Item | Version | Description | Source |
|-----------|---------|-------------|--------|
| **Backend API** | v1.0.0 | Django 5 + DRF REST endpoints | `backend/` |
| **Core Pipeline** | v1.0.0 | Chunking, Search, Rerank, LLM, Embeddings | `backend/core/` |
| **Async Tasks** | v1.0.0 | Celery tasks (ingest, embed, query) | `backend/*/tasks.py` |
| **Agent Management** | v1.0.0 | CRUD, activation, failover, test | `backend/agents/` |
| **Frontend Dashboard** | v1.0.0 | React/Vite SPA (nginx) | `frontend/` |
| **Infrastructure** | v1.0.0 | Docker Compose, nginx, volumes | `docker-compose.yml` |
| **Evaluation Harness** | v1.0.0 | `evaluate_rag.py` | Root |
| **Documentation** | v1.0.0 | SDD, SRS, PMP, QA, Test Plan, Ops Manual, Maintenance, RTM | Root |

---

## 2. Test Items (continued)

### 2.1 Software Configuration
| Component | Version |
|-----------|---------|
| Python | 3.12 |
| Django | 5.2 |
| Celery | 5.6 |
| PostgreSQL | 16 + pgvector |
| Redis | 7.4 |
| React | 18.3 |
| Vite | 5.4 |
| Nginx | 1.27 |
| Docker | 24.0 |

---

## 3. Features to be Tested

### 3.1 Functional Test Coverage (per SRS)
| Feature Area | Requirements | Test Types |
|--------------|--------------|------------|
| **Document Ingestion (FR-ING)** | FR-ING-01..10 | Unit, Integration, E2E |
| **Query Processing (FR-QRY)** | FR-QRY-01..09 | Unit, Integration, Performance |
| **Agent Management (FR-AGT)** | FR-AGT-01..05 | Unit, Integration |
| **Topic Isolation (FR-TOP)** | FR-TOP-01..03 | Integration, Security |
| **Cost Telemetry (FR-TEL)** | FR-TEL-01..04 | Unit, Integration, Evaluation |
| **Admin Dashboard (FR-UI)** | FR-UI-01..06 | UI, Integration, Usability |

### 3.2 Non-Functional Test Coverage
| Quality Attribute | Requirements | Test Types |
|-------------------|--------------|------------|
| **Performance** | p95 ≤ 3.5s, Recall@5 ≥ 0.95 | Load, Stress, Evaluation Harness |
| **Reliability** | 99.9% success, graceful degradation | Chaos, Failover, Recovery |
| **Security** | Key encryption, rate limiting, TLS | Penetration, Static Analysis, Config Audit |
| **Maintainability** | Test coverage, modularity | Static Analysis, Code Review |
| **Portability** | Docker deploy, 3 commands | Install Test |

---

## 4. Features Not to be Tested

| Feature | Reason |
|---------|--------|
| **LLM Provider Internals** | Black-box; tested via contract |
| **PostgreSQL/pgvector Internals** | Mature OSS; tested via contract |
| **Redis Internals** | Mature OSS; tested via contract |
| **Docker Engine** | Platform dependency |
| **Hardware Failure** | Infrastructure responsibility |
| **Regulatory Compliance** | Out of scope for demo |
| **Mobile/Responsive UI** | Desktop-first admin panel |
| **Multi-language** | Spanish-only MVP |

---

## 5. Test Approach

### 5.1 Test Levels
| Level | Scope | Technique | Tools |
|-------|-------|-----------|-------|
| **Unit** | Individual modules (core, agents, tasks) | White-box, pytest | pytest, pytest-mock |
| **Integration** | Component interactions (API → Celery → DB) | Gray-box, pytest-django | pytest-django, testcontainers |
| **System** | Full pipeline (ingest → query → answer) | Black-box, E2E | curl, pytest, evaluate_rag.py |
| **Performance** | Latency, throughput, scalability | Load, Stress | evaluate_rag.py, Locust (planned) |
| **Security** | Auth, encryption, rate limiting, deps | SAST, DAST, Config Audit | pip-audit, Dependabot, manual |
| **Usability** | Admin UI, free model catalog | Heuristic, Exploratory | Manual |
| **Acceptance** | Requirements satisfaction | E2E, Demo | Manual, Demo script |

### 5.2 Test Design Techniques
| Technique | Applied To |
|-----------|------------|
| **Equivalence Partitioning** | API input validation, chunk sizes |
| **Boundary Value Analysis** | Chunk size/overlap, token limits, top_k |
| **State Transition** | Document status (PENDING→READY), Agent activation |
| **Error Guessing** | Missing API keys, malformed JSON, network failures |
| **Decision Table** | Agent type × Provider × Fallback combinations |
| **Exploratory** | Admin UI, Free Models Catalog |

### 5.3 Test Data Strategy
| Data Type | Source | Management |
|-----------|--------|------------|
| **Unit Test Fixtures** | Hardcoded in tests | In-repo (`backend/tests/`) |
| **Integration Test DB** | SQLite `:memory:` | Auto-created per test run |
| **E2E Test Documents** | `docs/manual-operaciones.md` | Versioned in repo |
| **Evaluation Dataset** | `data/eval_questions.json` | Versioned in repo (5 Q/A) |
| **Production-like Data** | Manual upload during demo | Ephemeral |

---

## 5. Test Approach (continued)

### 5.4 Pass/Fail Criteria
| Test Level | Pass Criteria |
|------------|---------------|
| **Unit** | 100% tests pass, 0 failures, coverage ≥ 80% |
| **Integration** | 100% tests pass, no flaky tests |
| **System (E2E)** | Upload → Query → Answer with citations; cost/latency logged |
| **Performance** | p95 ≤ 3.5s, Recall@5 ≥ 0.95, Faithfulness ≥ 0.95 |
| **Security** | 0 critical vulns, 0 keys in logs, rate limiting works |
| **Security (Config)** | `.env` not in git, TLS at proxy, keys encrypted |
| **Acceptance** | All FRs demonstrable in demo |

---

## 6. Test Deliverables

| Deliverable | Format | Timing |
|-------------|--------|--------|
| **Test Plan** | This document (Test_Plan.md) | Baseline |
| **Test Cases** | `backend/tests/*.py` | Continuous |
| **Test Scripts** | `evaluate_rag.py`, `pytest` commands | Continuous |
| **Test Data** | `data/eval_questions.json` | Baseline |
| **Test Reports** | pytest output, evaluate_rag.py JSON/MD | Per run |
| **Defect Reports** | GitHub Issues | Continuous |
| **Test Summary Report** | Summary per release | Per release |
| **Test Logs** | CI logs, pytest output | Per run |

---

## 7. Test Environment

### 7.1 Hardware
| Environment | Spec |
|-------------|------|
| **Local Dev** | Windows 11, Docker Desktop, 16GB RAM |
| **CI** | GitHub Actions (ubuntu-latest, 2 vCPU, 7GB RAM) |
| **Production Demo** | Docker Compose on Linux, 2 vCPU, 4GB RAM |

### 7.2 Software
| Component | Version |
|-----------|---------|
| OS | Ubuntu 22.04+ / Windows 11 |
| Docker | 24.0+ |
| Docker Compose | v2.20+ |
| Python | 3.12 |
| PostgreSQL | 16 + pgvector |
| Redis | 7.4 |
| Nginx | 1.27 |

### 7.3 Test Data Setup
```bash
# Unit/Integration (auto)
pytest -q  # Uses SQLite :memory:

# E2E / Evaluation (requires running stack)
docker compose up -d
python evaluate_rag.py --k 5 --offline --json-out metrics.json
```

---

## 8. Test Schedule

### 8.1 Test Phases
| Phase | Activities | Duration | Start | End |
|-------|------------|----------|-------|-----|
| **Test Planning** | Write Test Plan, design cases | 1 day | M1 | M1 |
| **Unit Test Development** | Write pytest cases per module | 3 days | M2 | M5 |
| **Integration Test Dev** | API + Celery + DB tests | 2 days | M5 | M6 |
| **Test Execution (Dev)** | Continuous `pytest -q` | Ongoing | M2 | M12 |
| **Integration Test Execution** | API + pipeline tests | 1 day | M7 | M7 |
| **System/E2E Testing** | Full pipeline, evaluation harness | 1 day | M7 | M8 |
| **Performance Testing** | `evaluate_rag.py --offline` | 0.5 day | M8 | M8 |
| **Security Testing** | `pip-audit`, config audit | 0.5 day | M8 | M8 |
| **Acceptance Testing** | Demo rehearsal | 0.5 day | M12 | M13 |
| **Regression Testing** | Pre-release full suite | 0.5 day | M13 | M13 |

### 8.2 Milestones
| Milestone | Exit Criteria |
|-----------|---------------|
| **Test Ready** | All test cases written, env ready |
| **Integration Complete** | All integration tests pass |
| **System Tested** | E2E pass, evaluation metrics met |
| **Release Ready** | All tests pass, performance met, security clean |

---

## 9. Test Organization

### 9.1 Roles
| Role | Name | Responsibilities |
|------|------|------------------|
| **Test Manager / QA Lead** | Miguel Xlerion | Planning, metrics, reporting, defect management |
| **Test Engineer** | (Self) | Case design, execution, automation, reporting |
| **Developer** | (Self) | Unit tests, fix defects, code review |

### 9.2 Communication
- **Daily:** Test status in standup notes
- **Per Run:** pytest output, evaluation metrics
- **Per Release:** Test Summary Report
- **Defects:** GitHub Issues with `bug` label

---

## 10. Risks & Contingencies

| Risk | Probability | Impact | Contingency |
|------|-------------|--------|-------------|
| **LLM API unavailable** | Medium | High | Failover agents, offline eval mode |
| **Docker build fails** | Low | High | Cache layers, pinned base images |
| **Test flakiness** | Low | Medium | Retry logic, isolate flaky tests |
| **Performance regression** | Medium | High | Baseline comparison, revert |
| **Security vuln in dep** | Medium | High | `pip-audit`, Dependabot, pin versions |
| **Test data corruption** | Low | Medium | Fresh SQLite per test, versioned eval data |

---

## 11. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Test Manager / QA Lead** | Miguel Xlerion | ✅ | 2026-09-01 |
| **Project Manager** | Miguel Xlerion | ✅ | 2026-09-01 |

---

## 12. Appendices

### Appendix A: Test Case Index (backend/tests/)
| File | Tests | Coverage |
|------|-------|----------|
| `test_chunking.py` | 8 | SectionAwareSplitter, HybridChunker, headings |
| `test_circuit_breaker.py` | 5 | State transitions, thresholds |
| `test_search.py` | 5 | RRF fusion correctness |
| `test_rerank.py` | 4 | Fallback, JSON parsing, reordering |
| `test_token_budget.py` | 5 | Estimation, truncation |
| `test_providers.py` | 9 | Error classification (4xx vs 5xx) |
| `test_failover.py` | 5 | FailoverLLMService, FailoverEmbeddingService |
| `test_documents.py` | 8 | Upload, list, retry, delete (skipped w/o trafilatura) |
| **Total** | **43** | **Core pipeline + agents** |

### Appendix B: Evaluation Harness Test Cases
| Test | Input | Expected |
|------|-------|----------|
| `Recall@5` | 5 Q with relevant_chunk_ids | ≥ 0.95 |
| `Precision@5` | Same | Reported |
| `Faithfulness` | Answer + contexts | ≥ 0.95 |
| `Answer Relevancy` | Question + answer | Reported |
| `Latency p95` | 5 Q with latency_ms | ≤ 3.5s |

### Appendix C: Security Test Cases
| Test | Method | Pass Criteria |
|------|--------|---------------|
| **API Key Encryption** | Inspect DB `agents.api_key` | Fernet ciphertext, not plaintext |
| **Rate Limiting** | Exceed 60 req/min to `/api/query/` | 429 response |
| **TLS at Proxy** | `curl -v https://...` | Valid cert, HSTS |
| **No Keys in Logs** | `docker compose logs` | No `sk-` or `api_key` patterns |
| **Dependabot Alerts** | GitHub Security tab | 0 critical/unpatched |

### Appendix D: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-01 | Miguel Xlerion | Baseline |

---
*End of Test Plan v1.0 (IEEE 829)*