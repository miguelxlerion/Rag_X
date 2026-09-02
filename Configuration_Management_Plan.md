# Configuration Management Plan (CMP)
## Enterprise RAG Assistant
### IEEE 828-2012 / ISO 10007 Compliant

---

**Document Control**
- **Title:** Configuration Management Plan — Enterprise RAG Assistant
- **Version:** 1.0
- **Date:** 2026-09-01
- **Author:** Miguel Xlerion
- **Classification:** Portfolio / Internal Demo
- **Status:** Baseline

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [CM Organization](#2-cm-organization)
3. [Configuration Identification](#3-configuration-identification)
4. [Change Control](#4-change-control)
5. [Configuration Status Accounting](#5-configuration-status-accounting)
6. [Configuration Audits](#6-configuration-audits)
7. [Release Management](#7-release-management)
8. [Tools & Infrastructure](#8-tools--infrastructure)
9. [Appendices](#9-appendices)

---

## 1. Introduction

### 1.1 Purpose
This plan defines the configuration management (CM) policies, procedures, and tools for the Enterprise RAG Assistant project. It ensures integrity, traceability, and control of all configuration items throughout the project lifecycle.

### 1.2 Scope
Applies to all configuration items (CIs): source code, infrastructure-as-code, configuration files, documentation, test data, container images, and deployment scripts.

### 1.3 Standards & References
- IEEE 828-2012 (Configuration Management)
- ISO 10007 (Quality Management — Configuration Management)
- PMP.md §8, SDD.md §9

---

## 2. CM Organization

### 2.1 Roles & Responsibilities
| Role | Responsibility |
|------|----------------|
| **Configuration Manager (PM)** | CM policy, baseline approval, audit authorization |
| **Developer** | CI creation, branching, merging, tagging |
| **DevOps** | Container image versioning, infrastructure CI versioning |
| **Release Manager (PM)** | Release packaging, deployment, rollback |

### 2.2 CM Repository
- **Primary:** GitHub (`https://github.com/miguelxlerion/Rag_X`)
- **Branching Model:** Trunk-based (`master` protected, short-lived feature branches)
- **Access Control:** Single contributor (PM) — direct push to `master` with CI checks

---

## 3. Configuration Identification

### 3.1 Configuration Item (CI) Types
| CI Type | Examples | Identifier Format |
|---------|----------|-------------------|
| **Source Code** | `backend/`, `frontend/src/`, `scripts/` | Git path + commit SHA |
| **Infrastructure-as-Code** | `docker-compose.yml`, `Dockerfile*`, `nginx.conf`, `.github/workflows/` | Git path + commit SHA |
| **Configuration Templates** | `.env.example`, `backend/config/settings.py` | Git path + commit SHA |
| **Documentation** | `*.md`, `docs/` | Git path + commit SHA |
| **Test Data** | `data/eval_questions.json` | Git path + commit SHA |
| **Container Images** | `rag-empresarial-web`, `rag-empresarial-admin`, etc. | `registry/image:tag` (semver) |
| **Runtime Config** | `.env` (local only), `docker-compose.override.yml` | Not versioned (secrets) |

### 3.2 CI Attributes
Each CI tracks:
- **Unique ID:** Git path + commit SHA (code) / Image digest (containers)
- **Version:** Git commit SHA / Semantic version tag
- **Status:** Draft → Reviewed → Baseline → Released → Archived
- **Owner:** PM/Dev
- **Dependencies:** List of related CIs

### 3.3 Baselines
| Baseline | CIs Included | Trigger | Approval |
|----------|--------------|---------|----------|
| **Architecture Baseline** | `docker-compose.yml`, `backend/config/settings.py`, core models (`documents/models.py`, `agents/models.py`), `SDD.md` | M2 (Architecture complete) | PM |
| **Functional Baseline** | All source code, tests passing, `SRS.md` | M7 (All FRs implemented) | PM |
| **Documentation Baseline** | All SDLC docs (`SRS.md`, `SDD.md`, `PMP.md`, `Risk_Management_Plan.md`, `QA_Plan.md`, `Test_Plan.md`, `Deployment_Operations_Manual.md`, `Maintenance_Plan.md`, `RTM.md`) | M12 (SDLC suite complete) | PM |
| **Release Baseline** | Tagged release (`v1.0.0`), all baselines, `CHANGELOG.md` | M13 (Demo ready) | PM |

### 3.4 CI Naming Conventions
| CI Type | Convention |
|---------|------------|
| **Git Commits** | `type(scope): subject` (Conventional Commits) |
| **Git Tags** | `vMAJOR.MINOR.PATCH` (Semantic Versioning) |
| **Container Images** | `rag-empresarial-{service}:v{MAJOR}.{MINOR}.{PATCH}` |
| **Branches** | `feat/{id}-{short-desc}`, `fix/{id}-{short-desc}`, `hotfix/{id}` |

---

## 4. Change Control

### 4.1 Change Request (CR) Process
```
CR Submission → Triage → Impact Analysis → Decision (Approve/Reject/Defer) → Implementation → Verification → Closure
```

### 4.2 Change Categories
| Category | Description | Approval | Timeline |
|----------|-------------|----------|----------|
| **Emergency Fix** | Production bug, security vuln | PM (immediate) | < 4 hours |
| **Bug Fix** | Non-critical defect | PM | Next sprint |
| **Enhancement** | New feature, improvement | PM + Impact Analysis | Next release |
| **Breaking Change** | API/schema change | PM + Architecture Review | Major release |
| **Documentation** | Docs only | PM | Immediate |

### 4.3 Change Control Board (CCB)
- **Composition:** PM (single authority for portfolio project)
- **Authority:** Approve/Reject/Defer CRs
- **Meeting:** Ad-hoc for emergency; weekly for planned changes

### 4.4 Emergency Change Procedure
1. Create `hotfix/{id}` branch from `master`
2. Implement fix + test
2. Push → CI passes → Merge to `master`
3. Tag patch release (`vX.Y.Z+1`)
4. Deploy to staging → production
4. Document in `CHANGELOG.md`

---

## 5. Configuration Status Accounting

### 5.1 Status Tracking
| CI | Current Version | Status | Baseline | Last Changed |
|----|-----------------|--------|----------|--------------|
| Source Code | `v1.0.0` | Released | Functional | 2026-09-01 |
| Docker Compose | `v1.0.0` | Released | Architecture | 2026-09-01 |
| Documentation | `v1.0.0` | Released | Documentation | 2026-09-01 |
| Container Images | `v1.0.0` | Released | Release | 2026-09-01 |
| Test Suite | `v1.0.0` | Released | Functional | 2026-09-01 |

### 5.2 Reporting
- **Daily:** Git commit log, CI status
- **Per Release:** Baseline comparison report (what changed since last baseline)
- **Audit:** Full CI inventory with versions, status, owners

---

## 6. Configuration Audits

### 6.1 Functional Configuration Audit (FCA)
- **When:** Per release baseline (M7, M13)
- **Scope:** Verify all FRs implemented, tests pass, documentation matches code
- **Method:** `pytest -q`, `evaluate_rag.py`, manual E2E, doc review

### 6.2 Physical Configuration Audit (PCA)
- **When:** Release baseline (M13)
- **Scope:** Verify deployed artifacts match baseline (container images, configs, docs)
- **Method:** `docker image inspect`, `git diff` vs tag, deployed version check

### 6.3 Audit Schedule
| Audit Type | Frequency | Trigger |
|------------|-----------|---------|
| FCA | Per release | M7, M13 |
| PCA | Per release | M13 |
| Spot Check | Monthly | Random CI verification |

---

## 7. Release Management

### 7.1 Release Types
| Type | Version Bump | Criteria |
|------|--------------|----------|
| **Major** | `MAJOR.0.0` | Breaking API changes, schema changes |
| **Minor** | `0.MINOR.0` | New features, backward compatible |
| **Patch** | `0.0.PATCH` | Bug fixes, security patches |

### 7.2 Release Process
1. **Prepare:** Update `CHANGELOG.md`, bump version in `pyproject.toml`/`package.json`
2. **Tag:** `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Build:** `docker compose build` → multi-arch images
4. **Push:** `docker push` to registry (GHCR/Docker Hub)
5. **Deploy:** `docker compose pull && docker compose up -d`
5. **Verify:** Health checks, smoke tests, `evaluate_rag.py`
6. **Announce:** GitHub Release notes, update README badges

### 7.3 Rollback Procedure
1. `git checkout vX.Y.Z-1`
2. `docker compose pull`
3. `docker compose up -d`
4. Verify health
5. Document in `CHANGELOG.md`

---

## 8. Tools & Infrastructure

### 8.1 CM Tools
| Tool | Purpose | Version |
|------|---------|---------|
| **Git** | Source control | 2.40+ |
| **GitHub** | Remote repo, Issues, Actions | SaaS |
| **Docker** | Containerization | 24.0+ |
| **Docker Compose** | Orchestration | v2.20+ |
| **Docker Hub / GHCR** | Image registry | SaaS |
| **GitHub Actions** | CI/CD | SaaS |

### 8.2 Repository Structure
```
Rag_X/
├── .github/workflows/       # CI/CD pipelines
├── backend/                 # Django source
│   ├── config/             # Settings, URLs
│   ├── core/               # RAG pipeline modules
│   ├── documents/          # Document app
│   ├── query/              # Query app
│   ├── agents/             # Agent management
│   └── tests/              # Unit tests
├── frontend/               # React/Vite source
│   ├── src/
│   └── nginx.conf
├── docs/                   # Additional docs
├── data/                   # Test data
├── scripts/                # Utility scripts
├── docker-compose.yml      # Orchestration
├── Dockerfile*             # Container definitions
├── nginx.conf              # Frontend proxy
├── requirements.txt        # Python deps
├── package.json            # Node deps
├── SDD.md                  # IEEE 1016
├── SRS.md                  # IEEE 830
├── PMP.md                  # IEEE 1058
├── Risk_Management_Plan.md
├── QA_Plan.md              # IEEE 730
├── Test_Plan.md            # IEEE 829
├── Deployment_Operations_Manual.md
├── Maintenance_Plan.md
├── RTM.md                  # Traceability
├── CASE_STUDY_RAG_ASSISTANT.md
├── Decisiones de Arquitectura.csv
├── evaluate_rag.py
├── README.md
├── .env.example
└── .gitignore
```

---

## 9. Appendices

### Appendix A: CI Register Template
| CI ID | Name | Type | Version | Status | Baseline | Owner | Dependencies |
|-------|------|------|---------|--------|----------|-------|--------------|
| CI-001 | `backend/core/chunking.py` | Source | `v1.0.0` | Released | Functional | Dev | `token_budget.py`, `langchain` |
| CI-002 | `docker-compose.yml` | IaC | `v1.0.0` | Released | Architecture | DevOps | `Dockerfile*`, `.env.example` |

### Appendix B: Change Request Template
| Field | Description |
|-------|-------------|
| CR ID | Auto-generated |
| Title | Brief description |
| Type | Emergency / Bug / Enhancement / Breaking / Doc |
| Description | Detailed change description |
| Rationale | Why needed |
| Impact Analysis | Affected CIs, tests, docs, performance, security |
| Risk | Low/Medium/High |
| Implementation Plan | Steps, rollback plan |
| Testing | Test cases to run |
| Approval | PM signature/date |
| Implementation Date | Target date |
| Verification | Test results |
| Closure Date | Actual closure |

### Appendix C: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-01 | Miguel Xlerion | Baseline |

---
*End of Configuration Management Plan v1.0 (IEEE 828 / ISO 10007)*