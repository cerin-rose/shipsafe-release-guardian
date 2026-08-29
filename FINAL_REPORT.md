# ShipSafe Release Readiness Report
**Generated:** 2026-08-29 | **Stack:** `spring`  
**Overall:** 🔴 NO-GO — see findings below

---
## Go / No-Go Table
| ID | Severity | Domain | Check | File:Line | Status |
|----|----------|--------|-------|-----------|--------|
| C01 | HIGH | API | Breaking API change in diff | `src (git diff)` | ✅ |
| C02 | CRITICAL | Dependency | Manifest known-CVE artifact | `src/pom.xml` | ✅ |
| C03 | HIGH | Dependency | requirements.txt / lockfile CVE | `requirements.txt` | ✅ |
| C04 | CRITICAL | Config | VAULT_ID missing from config | `src/src/main/resources/application.properties:30` | ✅ |
| C05 | CRITICAL | Security | Hardcoded secret in config | `src/src/main/resources/application.properties` | ✅ |
| C06 | HIGH | Config | Actuator / debug endpoint wildcard exposed | `src/src/main/resources/application.properties:21` | 🟠 |
| C07 | HIGH | Security | No TLS/HTTPS configured | `src/src/main/resources/application.properties` | 🟠 |
| C08 | HIGH | Security | No security middleware/dependency | `src/pom.xml` | 🟠 |
| C09 | MEDIUM | Database | No DB migration tool | `src/pom.xml` | 🟡 |
| C10 | MEDIUM | Container | Dockerfile exposes privileged port (<1024) | `src/Dockerfile` | ✅ |
| C11 | HIGH | Pipeline | Hardcoded S3 bucket in pipeline.yaml | `pipeline.yaml` | ✅ |
| C12 | MEDIUM | Notebook | Notebook contains api_key literal | `notebook.ipynb` | ✅ |
| C13 | LOW | Notebook | Notebook hardcoded local CSV path | `notebook.ipynb` | ✅ |
| C14 | LOW | Pipeline | GPU env var (CUDA_VISIBLE_DEVICES) missing | `pipeline.yaml` | 🟡 |
| C16 | CRITICAL | Deploy | VAULT_ID missing from deploy/codeengine.yaml | `deploy/codeengine.yaml` | 🔴 |
| C15 | CRITICAL | Dependency | Phantom / invalid dependencies in manifest | `src/pom.xml:64` | 🔴 |

---

## Finding Details
### C06 — Actuator / debug endpoint wildcard exposed
**Severity:** HIGH | **File:Line:** `src/src/main/resources/application.properties:21`  
All endpoints exposed via wildcard

### C07 — No TLS/HTTPS configured
**Severity:** HIGH | **File:Line:** `src/src/main/resources/application.properties`  
No TLS config found in application.properties

### C08 — No security middleware/dependency
**Severity:** HIGH | **File:Line:** `src/pom.xml`  
Security library missing from pom.xml

### C09 — No DB migration tool
**Severity:** MEDIUM | **File:Line:** `src/pom.xml`  
No DB migration library detected

### C14 — GPU env var (CUDA_VISIBLE_DEVICES) missing
**Severity:** LOW | **File:Line:** `pipeline.yaml`  
CUDA_VISIBLE_DEVICES not set

### C16 — VAULT_ID missing from deploy/codeengine.yaml
**Severity:** CRITICAL | **File:Line:** `deploy/codeengine.yaml`  
VAULT_ID not declared in codeengine.yaml env block

### C15 — Phantom / invalid dependencies in manifest
**Severity:** CRITICAL | **File:Line:** `src/pom.xml:64`  
Phantom artifact: <artifactId>spring-boot-starter-webmvc</artifactId>

