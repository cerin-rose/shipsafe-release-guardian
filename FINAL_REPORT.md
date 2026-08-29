# ShipSafe Release Readiness Report
**Generated:** 2026-08-29 | **Stack:** `react`  
**Overall:** 🔴 NO-GO — see findings below

---
## Go / No-Go Table
| ID | Severity | Domain | Check | File:Line | Status |
|----|----------|--------|-------|-----------|--------|
| C01 | HIGH | API | Breaking API change in diff | `frontend (git diff)` | ✅ |
| C02 | CRITICAL | Dependency | Manifest known-CVE artifact | `frontend/package.json:1` | 🔴 |
| C03 | HIGH | Dependency | requirements.txt / lockfile CVE | `requirements.txt` | ✅ |
| C04 | CRITICAL | Config | VAULT_ID missing from config | `frontend/.env` | 🔴 |
| C05 | CRITICAL | Security | Hardcoded secret in config | `frontend/.env` | ✅ |
| C06 | INFO | Config | Actuator / debug endpoint wildcard exposed [N/A for react] | `frontend/.env` | ✅ |
| C07 | HIGH | Security | No TLS/HTTPS configured | `frontend/.env` | 🟠 |
| C08 | HIGH | Security | No security middleware/dependency | `frontend/package.json` | 🟠 |
| C09 | MEDIUM | Database | No DB migration tool | `frontend/package.json` | 🟡 |
| C10 | MEDIUM | Container | Dockerfile exposes privileged port (<1024) | `src/Dockerfile` | ✅ |
| C11 | HIGH | Pipeline | Hardcoded S3 bucket in pipeline.yaml | `pipeline.yaml` | ✅ |
| C12 | MEDIUM | Notebook | Notebook contains api_key literal | `notebook.ipynb` | ✅ |
| C13 | LOW | Notebook | Notebook hardcoded local CSV path | `notebook.ipynb` | ✅ |
| C14 | LOW | Pipeline | GPU env var (CUDA_VISIBLE_DEVICES) missing | `pipeline.yaml` | 🟡 |
| C16 | CRITICAL | Deploy | VAULT_ID missing from deploy/codeengine.yaml | `deploy/codeengine.yaml` | 🔴 |
| C15 | INFO | Dependency | Phantom / invalid dependencies in manifest | `frontend/package.json` | ✅ |

---

## Finding Details
### C02 — Manifest known-CVE artifact
**Severity:** CRITICAL | **File:Line:** `frontend/package.json:1`  
Potentially vulnerable dependency detected

### C04 — VAULT_ID missing from config
**Severity:** CRITICAL | **File:Line:** `frontend/.env`  
VAULT_ID not bound in .env

### C07 — No TLS/HTTPS configured
**Severity:** HIGH | **File:Line:** `frontend/.env`  
No TLS config found in .env

### C08 — No security middleware/dependency
**Severity:** HIGH | **File:Line:** `frontend/package.json`  
Security library missing from package.json

### C09 — No DB migration tool
**Severity:** MEDIUM | **File:Line:** `frontend/package.json`  
No DB migration library detected

### C14 — GPU env var (CUDA_VISIBLE_DEVICES) missing
**Severity:** LOW | **File:Line:** `pipeline.yaml`  
CUDA_VISIBLE_DEVICES not set

### C16 — VAULT_ID missing from deploy/codeengine.yaml
**Severity:** CRITICAL | **File:Line:** `deploy/codeengine.yaml`  
VAULT_ID not declared in codeengine.yaml env block

