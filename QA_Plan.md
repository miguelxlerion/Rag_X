# Quality Assurance Plan (QAP)
## Enterprise RAG Assistant
### IEEE 730-2014 Compliant

---

**Document Control**
- **Title:** Quality Assurance Plan — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Author:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Baseline
- **IEEE Std:** 730-2014 (IEEE Standard for Software Quality Assurance Plans)

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Quality Objectives](#2-quality-objectives)
3. [QA Organization](#3-qa-organization)
4. [Quality Standards & Metrics](#4-quality-standards--metrics)
5. [QA Activities](#5-qa-activities)
6. [Reviews & Audits](#6-reviews--audits)
7. [Defect Management](#7-defect-management)
8. [Tools & Environment](#8-tools--environment)
9. [Training & Competence](#9-training--competence)
10. [Appendices](#9-appendices)

---

## 1. Introduction

### 1.1 Purpose
This Quality Assurance Plan defines the processes, standards, metrics, and activities to ensure the Enterprise RAG Assistant meets its quality requirements throughout the software lifecycle.

### 1.2 Scope
Applies to all project deliverables: source code, infrastructure, documentation, test artifacts, and deployment packages.

### 1.3 Standards & References
- IEEE 730-2014 (Software Quality Assurance Plans)
- ISO/IEC 25010 (Systems and Software Quality Requirements and Evaluation — SQuaRE)
- IEEE 829 (Test Documentation), IEEE 830 (SRS), IEEE 1016 (SDD)
- ISO/IEC 25010 Quality Model
- SRS.md, SDD.md, PMP.md, Test_Plan.md

---

## 2. Quality Objectives

### 2.1 Product Quality Goals (ISO 25010)
| Quality Characteristic | Sub-characteristic | Target | Measurement |
|------------------------|-------------------|--------|-------------|
| **Functional Suitability** | Functional Completeness | 100% FRs implemented | SRS traceability |
| | Functional Correctness | 0 critical defects | Test pass rate |
| | Functional Appropriateness | Recall@5 ≥ 0.95 | `evaluate_rag.py` |
| **Performance Efficiency** | Time Behavior | p95 ≤ 3.5s | `evaluate_rag.py --offline` |
| | Resource Utilization | < 80% CPU, < 4GB RAM | Docker stats |
| | Capacity | 100 concurrent queries | Load test |
| **Reliability** | Maturity | 99.9% query success | `QueryLog` monitoring |
| | Availability | 99.5% uptime | Flower / health endpoint |
| | Fault Tolerance | Graceful degradation | CircuitBreaker, Failover |
| **Security** | Confidentiality | 0 key leaks | Fernet encryption, no keys in logs |
| | Integrity | 0 data corruption | pgvector ACID, Redis AOF |
| | Authenticity | Basic auth on Flower/Admin | Credential validation |
| **Maintainability** | Modularity | 12 core modules | Architecture review |
| | Testability | 43 unit tests passing | `pytest -q` |
| | Analyzability | Type hints, docs | Code review |
| **Portability** | Installability | `docker compose up -d` | 3 commands |
| | Adaptability | Multi-provider abstraction | Provider factory |

### 2.2 Process Quality Goals
| Goal | Target |
|------|--------|
| Requirements Volatility | < 5% change post-baseline |
| Defect Escape Rate | 0 to production |
| Test Coverage | ≥ 80% unit |
| Review Coverage | 100% PRs reviewed (self) |
| Documentation Currency | 100% docs match code |

---

## 3. QA Organization

### 3.1 Roles & Responsibilities
| Role | QA Responsibilities |
|------|---------------------|
| **QA Lead (PM)** | QA planning, metrics, reviews, audits, defect management |
| **Developer** | Unit tests, code reviews, static analysis, CI |
| **DevOps** | Infrastructure testing, deployment validation, monitoring |

### 3.2 Independence
Single-developer project — QA performed by same person with role separation:
- **Development Mode:** Write code + tests
- **QA Mode:** Run tests, review code, run evaluation harness, security scan
- **Release Mode:** Full regression, deployment verification

---

## 4. Quality Standards & Metrics

### 4.1 Quality Standards
| Standard | Application |
|----------|-------------|
| ISO/IEC 25010 | Product quality model |
| IEEE 829 | Test documentation |
| IEEE 830 | SRS |
| IEEE 1016 | SDD |
| IEEE 1058 | PMP |
| IEEE 730 | This QAP |
| PEP 8 / Black / Ruff | Python style |
| ESLint / Prettier | JS/TS style (if applicable) |
| Conventional Commits | Git history |

### 4.2 Quality Metrics Dashboard
| Metric | Target | Current | Frequency |
|--------|--------|---------|-----------|
| **Unit Test Pass Rate** | 100% | 43/43 | Per commit |
| **Code Coverage** | ≥ 80% | TBD | Per PR |
| **Critical Defects** | 0 | 0 | Per release |
| **Performance (p95)** | ≤ 3.5s | 3.14s | Per release |
| **Recall@5** | ≥ 0.95 | 1.000 | Per release |
| **Security Vulns (Critical)** | 0 | 0 | Monthly |
| **Documentation Currency** | 100% | 100% | Per release |
| **Technical Debt** | < 30 min | TBD | Monthly |

---

## 5. QA Activities

### 5.1 Development Phase
| Activity | Description | Trigger | Owner |
|----------|-------------|---------|-------|
| **Static Analysis** | `ruff check`, `black --check`, `mypy` (optional) | Pre-commit / CI | Dev |
| **Unit Testing** | `pytest -q` (43 tests) | Pre-commit / CI | Dev |
| **Code Review** | Self-review checklist (logic, tests, docs, security) | Per PR | Dev |
| **Type Checking** | Type hints on all public APIs | Per PR | Dev |
| **Security Scan** | `pip-audit`, `safety check` | Weekly / CI | DevOps |

### 5.2 Integration Phase
| Activity | Description | Trigger | Owner |
|----------|-------------|---------|-------|
| **Build Verification** | `docker compose build` success | CI | DevOps |
| **Container Health** | All 7 services `healthy` | Post-deploy | DevOps |
| **API Smoke Tests** | `curl /api/health`, `/api/metrics` | Post-deploy | Dev |
| **E2E Query Test** | Upload doc → query → verify citation | Per release | Dev |
| **Evaluation Harness** | `python evaluate_rag.py --offline` | Per release | QA |

### 5.3 Release Phase
| Activity | Description | Criteria |
|----------|-------------|----------|
| **Full Regression** | `pytest -q` + `evaluate_rag.py --offline` | 100% pass |
| **Performance Baseline** | `evaluate_rag.py --k 5 --offline` | p95 ≤ 3.5s |
| **Security Scan** | `pip-audit`, Dependabot clean | 0 critical |
| **Documentation Review** | All SDLC docs match code | 100% match |
| **Rollback Test** | Simulate rollback to previous tag | < 5 min |

### 5.4 Operational Phase
| Activity | Frequency | Owner |
|----------|-----------|-------|
| **Health Monitoring** | Continuous (Flower, `/api/health`) | DevOps |
| **Performance Monitoring** | Daily (p50/p95 from `QueryLog`) | DevOps |
| **Cost Monitoring** | Daily (cost per query) | Dev |
| **Security Scan** | Monthly (`pip-audit`, Dependabot) | DevOps |
| **Backup Verification** | Quarterly (restore test) | DevOps |
| **Dependency Update** | Monthly (minor), Quarterly (major) | Dev |

---

## 6. Reviews & Audits

### 6.1 Review Types
| Review Type | Frequency | Participants | Artifacts |
|-------------|-----------|--------------|-----------|
| **Code Review** | Per PR | Self | Diff, tests, docs |
| **Architecture Review** | Milestone gates (M2, M7) | PM | SDD, diagrams |
| **Requirements Review** | SRS baseline | PM | SRS.md, RTM |
| **Design Review** | SDD baseline | PM | SDD.md |
| **Test Plan Review** | Test Plan baseline | PM | Test_Plan.md |
| **Security Audit** | Monthly | DevOps | `pip-audit`, Dependabot |
| **Documentation Audit** | Per release | PM | All SDLC docs |

### 6.2 Audit Schedule
| Audit | Frequency | Scope |
|-------|-----------|-------|
| **Functional Configuration Audit** | Per release | FR implementation, tests |
| **Physical Configuration Audit** | Per release | Deployed artifacts match baseline |
| **Security Audit** | Monthly | Dependencies, secrets, TLS |
| **Process Audit** | Quarterly | CM, QA, CM processes |

---

## 7. Defect Management

### 7.1 Defect Lifecycle
```
New → Triage → Assigned → In Progress → Fixed → Verified → Closed
    ↑                                                    │
    └──────────────── Rejected / Deferred ─────────────┘
```

### 7.2 Severity Classification
| Severity | Definition | Response Time |
|----------|------------|---------------|
| **Critical** | System down, data loss, security breach | < 4 hours |
| **High** | Major feature broken, performance regression | < 24 hours |
| **Medium** | Minor feature broken, UI issue | < 72 hours |
| **Low** | Cosmetic, documentation typo | Next release |

### 7.3 Defect Tracking
- **Tool:** GitHub Issues
- **Labels:** `bug`, `severity:critical/high/medium/low`, `component:backend/frontend/infra/docs`
- **Fields:** Title, Description, Steps to Reproduce, Expected vs Actual, Severity, Component, Assignee, Status

### 7.4 Defect Metrics
| Metric | Target |
|--------|--------|
| **Defect Density** | < 0.5/KLOC |
| **Defect Escape Rate** | 0 to production |
| **Mean Time to Fix (Critical)** | < 4 hours |
| **Defect Reopen Rate** | < 5% |

---

## 8. Tools & Environment

### 8.1 QA Toolchain
| Tool | Purpose | Version |
|------|---------|---------|
| **pytest** | Unit/integration testing | 9.0+ |
| **pytest-cov** | Coverage | 4.1+ |
| **ruff** | Linting | 0.5+ |
| **black** | Formatting | 24.0+ |
| **pip-audit** | Security scanning | 2.7+ |
| **Dependabot** | Dependency alerts | GitHub |
| **Docker** | Container testing | 24.0+ |
| **Locust** | Load testing (planned) | 2.20+ |

### 8.2 Test Environments
| Environment | Purpose | Access |
|-------------|---------|--------|
| **Local Dev** | Developer machine | Docker Desktop |
| **CI Pipeline** | GitHub Actions | Automated |
| **Staging** | Pre-production (optional) | Docker Compose |
| **Production** | Live demo | Docker Compose |

---

## 9. Training & Competence

### 9.1 Required Competencies
| Role | Required Skills |
|------|-----------------|
| **Developer** | Python 3.12, Django 5, DRF, Celery, PostgreSQL, Redis, Docker, TypeScript, React, Testing |
| **DevOps** | Docker, Docker Compose, nginx, PostgreSQL, Redis, Monitoring |
| **QA** | pytest, Test Design, Security Testing, Performance Testing |

### 9.2 Training Plan
| Topic | Method | Frequency |
|-------|--------|-----------|
| New Dependencies | Read docs, spike | As needed |
| Security Best Practices | OWASP, `pip-audit` | Monthly |
| Performance Tuning | Profiling, load testing | Quarterly |
| New LLM Providers | Provider docs, spike | As needed |

---

## 10. Appendices

### Appendix A: QA Checklist (Per Release)
- [ ] All unit tests pass (`pytest -q`)
- [ ] Coverage ≥ 80% (`pytest --cov`)
- [ ] No critical vulnerabilities (`pip-audit`)
- [ ] `evaluate_rag.py --k 5 --offline` meets targets
- [ ] `docker compose build` succeeds
- [ ] All 7 services healthy
- [ ] API smoke tests pass
- [ ] E2E query test passes
- [ ] Documentation matches code
- [ ] Rollback tested
- [ ] CHANGELOG updated
- [ ] Tag created

### Appendix B: Code Review Checklist
- [ ] Logic correct and handles edge cases
- [ ] Tests added/updated for new code
- [ ] Type hints on public APIs
- [ ] Docstrings updated
- [ ] No hardcoded secrets
- [ ] Error handling + logging
- [ ] Performance considered (no N+1, caching)
- [ ] Security: input validation, auth checks
- [ ] Documentation updated (SRS, SDD, README if needed)

### Appendix C: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-01 | Miguel Xlerion | Baseline |

---
*End of QA Plan v1.0 (IEEE 730)*