# Maintenance Plan
## Enterprise RAG Assistant
### IEEE 1219 / ISO/IEC 14764 / ITIL Compliant

---

**Document Control**
- **Title:** Maintenance Plan — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Author:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Baseline

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Maintenance Organization](#2-maintenance-organization)
3. [Maintenance Categories](#3-maintenance-categories)
4. [Maintenance Schedule](#4-maintenance-schedule)
5. [Procedures by Category](#5-procedures-by-category)
6. [Change Management Integration](#6-change-management-integration)
7. [Tools & Automation](#7-tools--automation)
8. [Metrics & Reporting](#8-metrics--reporting)
9. [Training & Knowledge Transfer](#9-training--knowledge-transfer)
10. [Appendices](#10-appendices)

---

## 1. Introduction

### 1.1 Purpose
This Maintenance Plan defines the processes, schedules, and procedures for maintaining the Enterprise RAG Assistant in operational condition throughout its lifecycle. It covers corrective, adaptive, perfective, and preventive maintenance.

### 1.2 Scope
Applies to all system components: backend (Django/Celery), frontend (React/Vite), infrastructure (Docker Compose, PostgreSQL, Redis), documentation, and dependencies.

### 1.3 Standards & References
- IEEE 1219 (Software Maintenance)
- ISO/IEC 14764 (Software Engineering — Maintenance)
- ITIL v4 (Service Operation, Continual Improvement)
- Deployment_Operations_Manual.md, PMP.md, Risk_Management_Plan.md

### 1.4 Maintenance Objectives
| Objective | Target |
|-----------|--------|
| **Availability** | 99.5% uptime (excluding planned maintenance) |
| **MTTR (Critical)** | < 4 hours |
| **MTTR (Standard)** | < 24 hours |
| **Security Patch Latency** | < 72 hours (critical), 30 days (moderate) |
| **Dependency Freshness** | ≤ 30 days behind latest minor/patch |
| **Technical Debt** | ≤ 30 minutes estimated effort |

---

## 2. Maintenance Organization

### 2.1 Roles & Responsibilities
| Role | Responsibilities |
|------|------------------|
| **Maintenance Lead (PM)** | Planning, prioritization, approval, stakeholder communication |
| **Developer** | Code changes, testing, deployment, documentation updates |
| **DevOps** | Infrastructure maintenance, monitoring, backup/restore, security |
| **QA** | Regression testing, performance validation, release verification |

### 2.2 Escalation Path
```
Developer → Maintenance Lead (PM) → Stakeholders
     │
     └─ Security Incident → Immediate PM notification → Stakeholders
```

---

## 3. Maintenance Categories

Per ISO/IEC 14764:

| Category | Definition | Examples |
|----------|------------|----------|
| **Corrective** | Fix defects after delivery | Bug fixes, crash recovery, data corruption repair |
| **Adaptive** | Modify for environment changes | OS upgrades, Docker version, LLM API changes, Python version |
| **Perfective** | Improve performance/maintainability | Query optimization, UI improvements, refactoring, new features |
| **Preventive** | Prevent future problems | Dependency updates, security patches, capacity planning, doc updates |

### 3.1 Category Distribution (Target)
| Category | % Effort | Frequency |
|----------|----------|-----------|
| Corrective | 20% | As needed |
| Adaptive | 20% | Monthly / per environment change |
| Perfective | 40% | Sprint-based |
| Preventive | 20% | Weekly / Monthly |

---

## 4. Maintenance Schedule

### 4.1 Recurring Activities

| Activity | Frequency | Owner | Artifact |
|----------|-----------|-------|----------|
| **Security Scan** | Weekly | DevOps | `pip-audit` report |
| **Dependabot Review** | Weekly | Dev | GitHub Dependabot alerts |
| **Dependency Update (patch)** | Monthly | Dev | PR with `requirements.txt` / `package.json` |
| **Dependency Update (minor)** | Quarterly | Dev | PR + full regression |
| **OS/Base Image Update** | Quarterly | DevOps | Dockerfile base image bump |
| **Log Rotation Check** | Monthly | DevOps | `docker system df`, log size |
| **Disk Space Review** | Monthly | DevOps | `df -h`, `docker system df` |
| **Backup Restore Test** | Quarterly | DevOps | Restore report |
| **Performance Baseline** | Per release | QA | `evaluate_rag.py` metrics |
| **Cost Analysis** | Monthly | Dev | `QueryLog` aggregation |
| **Documentation Review** | Per release | PM | All SDLC docs |
| **Capacity Planning** | Quarterly | DevOps | Metrics trends |
| **SSL Cert Renewal** | Auto (90 days) | DevOps | Certbot / Let's Encrypt |

### 4.2 Maintenance Windows
| Window | Schedule | Duration | Activities |
|--------|----------|----------|------------|
| **Daily** | 02:00-04:00 UTC | 30 min | pg_dump, log rotation, security scan |
| **Weekly** | Sunday 03:00 UTC | 1 hour | Dependabot review, dependency patches |
| **Monthly** | 1st Sunday 04:00 UTC | 2 hours | Minor dependency updates, log cleanup, disk check |
| **Quarterly** | 1st of Jan/Apr/Jul/Oct 05:00 UTC | 4 hours | Minor upgrades, restore test, capacity review, SSL renew |

### 4.3 Unplanned Maintenance
| Trigger | Response | Communication |
|---------|----------|---------------|
| **Critical Bug** | Immediate hotfix branch → deploy | Stakeholders notified |
| **Security Incident** | Immediate isolation + patch | Stakeholders + legal (if PII) |
| **Performance Degradation** | Rollback / scale / optimize | PM notified |
| **Security Vulnerability (CVSS ≥ 7)** | Patch within 72h | PM → Stakeholders |

---

## 5. Procedures by Category

### 5.1 Corrective Maintenance

#### 5.1.1 Bug Fix Process
```
1. Defect reported → GitHub Issue (label: bug, severity)
2. Triage → Assign severity, component, owner
3. Reproduce → Write failing test
4. Fix → Code change + test passes
5. Review → Self-review checklist (Appendix B, QA_Plan.md)
6. Deploy → Hotfix branch → CI → merge → tag patch
7. Verify → Smoke test + evaluation harness
8. Close → GitHub Issue closed, CHANGELOG updated
```

#### 5.1.2 Common Corrective Actions
| Defect Type | Typical Fix |
|-------------|-------------|
| **Query "degraded"** | Check LLM provider status, circuit breaker, API key validity |
| **Document stuck PROCESSING** | Restart worker, check Celery logs, retry task |
| **Vector dim mismatch** | Reindex (Admin UI) or revert embedding model |
| **Rate limit (429)** | Backoff + failover, add provider keys |
| **Worker OOM** | Reduce concurrency, increase RAM, chunk size tuning |

### 5.2 Adaptive Maintenance

#### 5.2.1 Environment Changes
| Change | Procedure |
|--------|-----------|
| **Docker/Compose version** | Update `Dockerfile*` base images, test build, deploy |
| **Python version** | Update `Dockerfile` `FROM python:X.Y`, test full suite |
| **PostgreSQL major version** | `pg_dump` → new container → `pg_restore` → test |
| **Redis version** | Update image tag, verify AOF/RDB compatibility |
| **LLM Provider API change** | Update `providers.py` mappings, add model to catalog, test |

#### 5.2.2 LLM Provider API Changes
1. Monitor provider changelogs (GitHub Issues labeled `provider`)
2. Update `backend/core/providers.py`: `PROVIDER_LABELS`, `OPENAI_COMPATIBLE_BASE_URLS`, `ENV_KEY_BY_PROVIDER`
3. Update `frontend/src/types.ts`: `MODELS_BY_PROVIDER`, `PROVIDER_KEY_URL`, `PROVIDER_DOCS_URL`
4. Test via Admin UI → **Modelos Gratis** → **Usar este modelo** → **Probar API**
5. Rebuild frontend: `cd frontend && npm run build`
5. `docker compose build admin && docker compose up -d admin`

### 5.3 Perfective Maintenance

#### 5.3.1 Performance Optimization
| Area | Typical Actions |
|------|-----------------|
| **Query Latency** | Tune `HYBRID_TOP_K`, `RERANK_TOP_K`, `VECTOR_EF_SEARCH`, `MMR_LAMBDA` |
| **Ingestion Speed** | Increase `EMBED_BATCH_SIZE`, `worker` concurrency, `CHUNK_SIZE` |
| **Memory Usage** | Reduce `CHUNK_SIZE`, `MAX_CONTEXT_TOKENS`, worker concurrency |
| **DB Performance** | `ANALYZE`, `VACUUM`, pgvector index tuning (`m`, `ef_construction`) |

#### 5.3.2 Code Quality / Refactoring
- **Technical Debt:** Track in GitHub Issues labeled `tech-debt`
- **Refactoring:** Small, incremental PRs with tests
- **Code Style:** `ruff check --fix`, `black --check` in CI
- **Type Hints:** Add to all new public APIs

#### 5.3.3 Feature Enhancements (Roadmap)
| Priority | Enhancement | Effort |
|----------|-------------|--------|
| High | Cross-encoder re-ranking (local) | 2 days |
| High | RBAC per Tenant | 2 days |
| High | Streaming SSE responses | 2 days |
| Medium | OpenTelemetry tracing | 2 days |
| Medium | Prometheus alerts + Grafana dashboards | 2 days |
| Low | Mobile-responsive Admin UI | 3 days |

### 5.4 Preventive Maintenance

#### 5.4.1 Dependency Management
```bash
# Weekly (automated via Dependabot + manual review)
pip-audit
# Review Dependabot PRs → merge patch/minor → test → deploy

# Quarterly (manual)
# 1. Update base images in Dockerfile* (python, node, nginx, redis, postgres)
# 2. Update minor versions in requirements.txt / package.json
# 3. Full regression test (pytest + evaluate_rag.py)
# 4. Deploy to staging → smoke test → production
```

#### 5.4.2 Security Hardening
| Action | Frequency |
|--------|-----------|
| `pip-audit` / `safety check` | Weekly (CI) |
| Dependabot alert review | Weekly |
| TLS cert renewal check | Monthly (auto) |
| API key rotation | Per provider (90 days typical) |
| `DJANGO_SECRET_KEY` rotation | 90 days |
| `FLOWER_PASSWORD` rotation | 90 days |
| Rate limit tuning | Quarterly |

#### 5.4.3 Capacity Management
| Metric | Threshold | Action |
|--------|-----------|--------|
| **Disk > 80%** | `df -h` | Prune logs, `docker system prune`, expand disk |
| **Redis > 80% maxmemory** | `redis-cli info memory` | Increase `maxmemory`, LRU eviction |
| **DB connections > 80%** | `pg_stat_activity` | Increase `max_connections`, tune pool |
| **Query p95 > 5s** | `QueryLog` aggregation | Scale workers, tune params, add provider |
| **LLM cost > budget** | Daily `QueryLog` sum | Alert, switch to cheaper provider |

---

## 6. Change Management Integration

### 6.1 Maintenance Change Types
| Type | Process | Approval |
|------|---------|----------|
| **Emergency Fix** | Hotfix branch → CI → deploy | PM (immediate) |
| **Scheduled Maintenance** | Feature branch → PR → CI → merge → tag | PM |
| **Dependency Update** | Dependabot PR / manual PR → CI → merge | PM |
| **Infrastructure Change** | IaC change → test in staging → deploy | PM + DevOps |

### 6.2 Emergency Maintenance Bypass
For critical production issues:
1. Create `hotfix/{issue-id}` from `master`
2. Implement minimal fix + test
3. `git push` → CI passes → merge to `master`
4. `docker compose build && docker compose up -d`
5. Verify health + smoke test
6. Document in `CHANGELOG.md` and GitHub Issue

### 6.3 Post-Maintenance Verification
| Check | Tool |
|-------|------|
| Health endpoint | `curl /api/health/` |
| Query smoke test | `curl POST /api/query/` |
| Evaluation metrics | `python evaluate_rag.py --k 5 --offline` |
| Worker status | Flower UI |
| Logs clean | `docker compose logs --tail=50` |

---

## 7. Tools & Automation

### 7.1 Automation Scripts
| Script | Purpose | Schedule |
|--------|---------|----------|
| `backup_rag.sh` | pg_dump → S3 | Daily 02:00 UTC (cron) |
| `log_cleanup.sh` | `docker system prune`, log truncate | Weekly (cron) |
| `security_scan.sh` | `pip-audit`, `safety` | Weekly (GitHub Actions) |
| `dependency_check.sh` | Dependabot PR creation | Weekly (GitHub) |
| `health_check.sh` | `/api/health/` + alerting | Every 5 min (cron/systemd) |

### 7.2 CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/ci.yml (recommended)
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: docker compose build
      - name: Unit Tests
        run: docker compose run --rm web pytest -q
      - name: Security Scan
        run: pip-audit
      - name: Evaluate (optional)
        run: python evaluate_rag.py --k 5 --offline --json-out metrics.json
```

### 7.3 Monitoring Automation
| Tool | Purpose |
|------|---------|
| **Flower** | Celery worker/task monitoring |
| **Prometheus + Grafana** | Metrics dashboards (planned) |
| **cron + health_check.sh** | Uptime monitoring |
| **logrotate / Docker json-file** | Log management |

---

## 8. Metrics & Reporting

### 8.1 Maintenance KPIs
| KPI | Target | Source |
|-----|--------|--------|
| **MTTR (Critical)** | < 4 hours | GitHub Issue timestamps |
| **MTTR (Standard)** | < 24 hours | GitHub Issue timestamps |
| **Deployment Frequency** | Weekly | Git tags |
| **Change Failure Rate** | < 5% | Failed deployments / total |
| **Mean Time Between Failures** | > 30 days | Incident log |
| **Security Patch Latency** | < 72h (critical) | Dependabot / pip-audit |
| **Technical Debt Ratio** | < 5% | SonarQube (if added) / manual |

### 8.2 Reporting Cadence
| Report | Frequency | Audience | Format |
|--------|-----------|----------|--------|
| **Weekly Status** | Weekly | PM | GitHub Milestone / Local |
| **Monthly Maintenance Report** | Monthly | Stakeholders | Markdown (GitHub) |
| **Quarterly Review** | Quarterly | Stakeholders | Presentation / Markdown |
| **Incident Postmortem** | Per incident | PM + Stakeholders | Markdown (GitHub Wiki) |

---

## 9. Training & Knowledge Transfer

### 9.1 Documentation as Knowledge Base
| Document | Purpose |
|----------|---------|
| **SDD.md** | Architecture, design decisions, component details |
| **SRS.md** | Requirements traceability |
| **Deployment_Operations_Manual.md** | Deploy, operate, troubleshoot |
| **Maintenance_Plan.md** | This document |
| **Runbooks** (Ops Manual §11) | Step-by-step procedures |
| **Code Comments + Type Hints** | Inline knowledge |
| **GitHub Wiki** (optional) | Incident postmortems, decisions |

### 9.2 Knowledge Transfer Checklist (for handoff)
- [ ] Walkthrough: Architecture (SDD §4), Data Flow (Ops Manual §2.3)
- [ ] Hands-on: Deploy locally (`docker compose up -d`)
- [ ] Demo: End-to-end query, Admin UI, Flower
- [ ] Runbooks: Deploy, Scale, Rotate Secrets, DR (Ops Manual §11)
- [ ] Access: GitHub, Docker Hub, Cloud provider, Monitoring
- [ ] Contacts: LLM provider support, hosting support
- [ ] Incident history: GitHub Issues `postmortem` label

---

## 10. Appendices

### Appendix A: Maintenance Checklist Templates

#### Daily
- [ ] Health check: `curl /api/health/`
- [ ] Log review: `docker compose logs --since=24h | grep -i error`
- [ ] Backup verification: pg_dump exists in S3

#### Weekly
- [ ] Dependabot PRs reviewed/merged
- [ ] `pip-audit` clean
- [ ] Disk space > 20% free
- [ ] Redis memory < 80%
- [ ] Flower: all workers online, queue depth normal

#### Monthly
- [ ] Dependency updates (patch) applied
- [ ] Log rotation verified
- [ ] Disk usage trend reviewed
- [ ] Cost report generated
- [ ] Documentation currency check

#### Quarterly
- [ ] Base image updates
- [ ] Minor dependency updates
- [ ] Full regression test
- [ ] Backup restore test
- [ ] Capacity planning review
- [ ] SSL cert validity
- [ ] Runbook review/update

### Appendix B: Version Compatibility Matrix
| Component | Current | Supported Range | Next Review |
|-----------|---------|-----------------|-------------|
| Python | 3.12 | 3.11 - 3.13 | 2026-12 |
| Django | 5.2 | 5.0 - 5.2 | 2026-12 |
| Celery | 5.6 | 5.4 - 5.6 | 2026-12 |
| PostgreSQL | 16 | 15 - 16 | 2027-01 |
| Redis | 7.4 | 7.2 - 7.4 | 2027-01 |
| React | 18.3 | 18.x | 2027-01 |
| Vite | 5.4 | 5.x | 2027-01 |
| Nginx | 1.27 | 1.25+ | 2027-01 |

### Appendix C: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-01 | Miguel Xlerion | Baseline |

---
*End of Maintenance Plan v1.0 (IEEE 1219 / ISO 14764)*