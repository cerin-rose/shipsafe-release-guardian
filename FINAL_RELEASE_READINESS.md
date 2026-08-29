# 🛡️ Release Readiness Report — ShipSafe Release Guardian

## Problem

Before every release, Release Managers and senior developers spend **4–6 hours manually verifying release readiness**.

They typically have to:

- Read 30+ commits using `git diff main...release`
- Audit 50+ dependencies in `pom.xml` for vulnerabilities
- Cross-check `application.properties` and `deploy.yaml`
- Verify required environment variables such as `VAULT_ID`
- Maintain Excel-based release checklists
- Rely on tribal knowledge from senior team members

This manual process is slow, inconsistent, and difficult to audit. A single missed issue can cause breaking API changes reaching production, vulnerable dependencies, missing IBM Cloud environment variables, deployment failures, production crashes, emergency rollbacks, and failed IBM Cloud deployment governance checks.

Currently, approximately **30% of releases require a hotfix**, and there is no reliable auditable proof showing that release-readiness checks were completed.

This report was generated automatically by **ShipSafe** — a one-command release-readiness guardian built using IBM Bob 2.0 — targeting Release Managers, SREs, Tech Leads, and Senior Developers managing microservices on IBM Cloud Code Engine and Red Hat OpenShift.

---

**Generated:** 2025-08-19 *(Deployment re-check: 2025-08-19 · Final re-check: 2025-08-19)*
**Project:** `org.springframework.samples:spring-petclinic:4.0.0-SNAPSHOT`  
**Branch:** `main`  
**Audited Artifacts:**
- `src/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java`
- `src/src/main/resources/application.properties`
- `src/pom.xml`

---

## ✅ Go / No-Go Decision Table

| Domain | Status | Blocking Issues |
|--------|--------|-----------------|
| **Secrets & Credentials** | 🟢 **GO** | ✅ `@Value("${vault.id}")` binding in place; `vault.id=${VAULT_ID}` in `application.properties` — no plaintext credential |
| **Dependency Health** | 🔴 **NO-GO** | 8 phantom Maven artifacts will cause build failure; javax→jakarta namespace mismatch |
| **Deployment Configuration** | 🔴 **NO-GO** | Actuator wildcard exposure; no TLS; no Spring Security |
| **Behavioral / API Changes** | 🟡 **WARN** | `lastName.strip()` changes search query behavior (commit `bb37aad`) |
| **Overall Release Decision** | 🔴 **NO-GO** | 2 domains still blocking — do not ship |

---

## Finding Summary

| ID | Severity | Domain | File:Line | Title |
|----|----------|--------|-----------|-------|
| [RG-001](#rg-001) | ~~🔴 CRITICAL~~ ✅ FIXED | Risk | `OwnerController.java:50` | ~~VAULT_ID leaked via `System.getenv()`~~ — `@Value` binding confirmed |
| [DV-001](#dv-001) | ~~🔴 CRITICAL~~ ✅ FIXED | Deployment | `OwnerController.java:50` | ~~VAULT_ID not bound via Spring~~ — `vault.id=${VAULT_ID}` in `application.properties` |
| [DG-001](#dg-001) | 🔴 CRITICAL | Dependency | `pom.xml:64` | Phantom artifact `spring-boot-starter-webmvc` |
| [DG-002](#dg-002) | 🔴 CRITICAL | Dependency | `pom.xml:123–170` | 8 phantom `-test` starters cause build failure |
| [DG-009](#dg-009) | 🔴 CRITICAL | Dependency | `pom.xml:68` | `javax.cache` namespace invalid in Spring Boot 4.1 |
| [DV-003](#dv-003) | 🟠 HIGH | Deployment | `application.properties:21` | Actuator wildcard exposure (`include=*`) |
| [DV-004](#dv-004) | 🟠 HIGH | Deployment | `application.properties:1–30` | No Spring Security — actuator endpoints unprotected |
| [DV-005](#dv-005) | 🟠 HIGH | Deployment | `application.properties:1–30` | No HTTPS/TLS configured |
| [DV-002](#dv-002) | 🟠 HIGH | Deployment | `OwnerController.java:50` | Vault field is dead code; credential leak risk |
| [RG-003](#rg-003) | 🟠 HIGH | Risk | `application.properties:21` | Actuator exposure amplifies RG-001 credential risk |
| [DG-010](#dg-010) | 🟠 HIGH | Dependency | `pom.xml:116` | `spring-boot-devtools` may leak into production JAR |
| [DG-011](#dg-011) | 🟡 MEDIUM | Dependency | `pom.xml:110` | Font Awesome 4.7.0 — severely outdated (2016) |
| [DG-012](#dg-012) | 🟡 MEDIUM | Dependency | `pom.xml:128` | Phantom `spring-boot-starter-restclient` artifact |
| [RG-002](#rg-002) | 🟡 MEDIUM | Risk | `OwnerController.java:103–105` | `lastName.strip()` changes query behavior |

---

## Detailed Findings

---

### Risk Analyzer

#### RG-001
**Severity:** 🔴 CRITICAL | **Category:** Secrets Management  
**File:Line:** `src/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java:50`

```java
private String vault = System.getenv("VAULT_ID");
```

**Status:** ✅ **FIXED** — Final re-check confirmed.

**Resolution:**
- [`OwnerController.java:50`](src/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java:50): `@Value("${vault.id}") private String vault;` — now uses Spring environment abstraction.
- [`application.properties:30`](src/src/main/resources/application.properties:30): `vault.id=${VAULT_ID}` — runtime env var injected via Spring placeholder; no plaintext value committed.
- `VAULT_ID=xxx` stub line removed from `application.properties`.

No further action required for this finding.

---

#### RG-002
**Severity:** 🟡 MEDIUM | **Category:** Behavioral Change  
**File:Line:** `src/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java:103–105`

```java
else {
    lastName = lastName.strip();
}
```

**Status:** Committed — introduced in commit `bb37aad` ("fix: normalize whitespace in owner search").

**Issues:**
- Search input to `findByLastNameStartingWith()` is now whitespace-trimmed.
- Inputs like `"  Smith"` previously searched the DB with leading spaces; now they resolve to `"Smith"`.
- Low functional risk (normalization is sensible) but constitutes a behavior change that should appear in release notes and be regression-tested.

**Remediation:**
- Add a regression test covering trimmed-input searches.
- Document in the release changelog.

---

#### RG-003
**Severity:** 🟠 HIGH | **Category:** Configuration Risk  
**File:Line:** `src/src/main/resources/application.properties:21`

**Issues:**
- Actuator wildcard exposure (`include=*`) combined with RG-001 means `/actuator/env` could expose the `VAULT_ID` value to any unauthenticated caller.
- See [DV-003](#dv-003) for full remediation.

---

### Dependency Guard

#### DG-001
**Severity:** 🔴 CRITICAL | **Category:** Phantom Artifact  
**File:Line:** `src/pom.xml:64`

```xml
<artifactId>spring-boot-starter-webmvc</artifactId>
```

**Issues:** The correct artifact is `spring-boot-starter-web`. `spring-boot-starter-webmvc` does not exist in Maven Central and will cause a build resolution failure.

**Remediation:** Change to `spring-boot-starter-web`.

---

#### DG-002
**Severity:** 🔴 CRITICAL | **Category:** Phantom Artifacts  
**File:Line:** `src/pom.xml:123, 128, 133, 138, 143, 148, 153, 168`

The following test-scoped dependencies do not exist as Spring Boot starter artifacts:

| Artifact | Line |
|----------|------|
| `spring-boot-starter-data-jpa-test` | 123 |
| `spring-boot-starter-restclient` | 128 |
| `spring-boot-starter-restclient-test` | 133 |
| `spring-boot-starter-thymeleaf-test` | 138 |
| `spring-boot-starter-validation-test` | 143 |
| `spring-boot-starter-webmvc-test` | 148 |
| `spring-boot-starter-actuator-test` | 153 |
| `spring-boot-starter-cache-test` | 168 |

**Issues:** Maven will fail to resolve all 8 artifacts, breaking the build entirely.

**Remediation:** Replace all with `spring-boot-starter-test` (single unified Spring Boot test starter) and add specific libraries (e.g., `org.testcontainers:*`) as needed.

---

#### DG-009
**Severity:** 🔴 CRITICAL | **Category:** Namespace Conflict  
**File:Line:** `src/pom.xml:68`

```xml
<groupId>javax.cache</groupId>
<artifactId>cache-api</artifactId>
```

**Issues:** Spring Boot 4.1.0 is based on Spring Framework 6.x and Jakarta EE 9+, which mandates the `jakarta.*` namespace. `javax.cache` is the legacy pre-Jakarta namespace and is incompatible at runtime.

**Remediation:** Replace with `jakarta.cache:jakarta.cache-api`.

---

#### DG-010
**Severity:** 🟠 HIGH | **Category:** Development Dependency  
**File:Line:** `src/pom.xml:116`

**Issues:** `spring-boot-devtools` is marked `optional=true` but can still be included in the classpath if the build configuration does not explicitly exclude it. Devtools disables caching, restarts the application on class changes, and exposes a remote debug port — all dangerous in production.

**Remediation:** Confirm `spring-boot-maven-plugin` excludes devtools, or remove the dependency if production builds do not need it.

---

#### DG-011
**Severity:** 🟡 MEDIUM | **Category:** Dependency Staleness  
**File:Line:** `src/pom.xml:110`

**Issues:** `org.webjars.npm:font-awesome:4.7.0` was released in 2016 and is no longer actively maintained. Icons are missing, and the package is not patched for supply-chain concerns.

**Remediation:** Upgrade to Font Awesome 6.x (current stable series).

---

#### DG-012
**Severity:** 🟡 MEDIUM | **Category:** Phantom Artifact  
**File:Line:** `src/pom.xml:128`

**Issues:** `spring-boot-starter-restclient` is not a valid Spring Boot starter. Spring Boot 3.2+ includes `RestClient` in `spring-boot-starter-web`; no separate starter exists.

**Remediation:** Remove and rely on `spring-boot-starter-test` + `spring-boot-starter-web`.

---

### Deployment Validator

#### DV-001
**Severity:** ~~🔴 CRITICAL~~ ✅ **FIXED** | **Category:** Environment Binding
**File:Line:** `src/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java:50`

**Final re-check (2025-08-19):** Both fixes confirmed in place.

| Check | File | Line | Result |
|-------|------|------|--------|
| `@Value("${vault.id}")` binding | `OwnerController.java` | 50 | ✅ Correct |
| `vault.id=${VAULT_ID}` placeholder | `application.properties` | 30 | ✅ Correct |
| `VAULT_ID=xxx` plaintext stub removed | `application.properties` | — | ✅ Removed |

No remaining action required.

---

#### DV-002
**Severity:** 🟠 HIGH | **Category:** Dead Code / Secret Leak  
**File:Line:** `src/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java:50`

**Issues:** The `vault` field is declared but never referenced in any method of `OwnerController`. It is pure dead code that nonetheless holds a credential in-memory and is accessible via reflection and heap dumps.

**Remediation:** Remove the field. If vault access is needed in the future, implement it with proper Spring injection and usage at the call site.

---

#### DV-003
**Severity:** 🟠 HIGH | **Category:** Operational Security  
**File:Line:** `src/src/main/resources/application.properties:21`

```properties
management.endpoints.web.exposure.include=*
```

**Issues:**
- Comment on line 20 explicitly states "Don't do this in production, only for development and testing" — yet this is the default `application.properties` shipped to all environments.
- Exposes `/actuator/env`, `/actuator/beans`, `/actuator/configprops`, `/actuator/heapdump`, `/actuator/threaddump`, and others — all unauthenticated.
- `/actuator/env` will expose the runtime value of `VAULT_ID` if it is set (amplifies RG-001).

**Remediation:**
```properties
# application.properties (default — all environments)
management.endpoints.web.exposure.include=health

# application-dev.properties (development only)
management.endpoints.web.exposure.include=*
```

---

#### DV-004
**Severity:** 🟠 HIGH | **Category:** Authentication  
**File:Line:** `src/src/main/resources/application.properties:1–30`

**Issues:** No Spring Security configuration is present in the codebase. Actuator endpoints and all application routes are unauthenticated.

**Remediation:** Add `spring-boot-starter-security` and a `SecurityFilterChain` bean that restricts actuator access to authenticated/authorized callers only.

---

#### DV-005
**Severity:** 🟠 HIGH | **Category:** Transport Security  
**File:Line:** `src/src/main/resources/application.properties:1–30`

**Issues:** No `server.ssl.*` properties are configured. The application listens on plain HTTP, transmitting credentials and session data in cleartext.

**Remediation:** Configure TLS via `server.ssl.key-store`, `server.ssl.key-store-password`, `server.ssl.key-store-type`, and redirect port 80 → 443.

---

## Prioritized Remediation Roadmap

| Priority | ID(s) | Action | Owner | Target |
|----------|-------|--------|-------|--------|
| **P0 — Immediate** | RG-001, DV-001, DV-002 | Revert uncommitted `vault` field from OwnerController.java | Dev | Before next commit |
| **P0 — Immediate** | DG-001, DG-002, DG-009, DG-012 | Fix phantom artifacts and `javax.cache` namespace in pom.xml | Dev | Before next build |
| **P1 — This Sprint** | DV-003, DV-004, RG-003 | Restrict actuator exposure; add Spring Security | Security | This sprint |
| **P1 — This Sprint** | DV-005 | Configure HTTPS/TLS in production profile | Ops | This sprint |
| **P2 — Next Sprint** | DG-010, DG-011 | Remove devtools risk; upgrade Font Awesome | Dev | Next sprint |
| **P3 — Release Notes** | RG-002 | Document `lastName.strip()` behavior change; add regression test | Dev/QA | Before release |

---

## Configuration Cross-Reference Matrix

| Item | `OwnerController.java` | `application.properties` | Status |
|------|----------------------|--------------------------|--------|
| `VAULT_ID` Spring binding | Line 50: `@Value("${vault.id}")` *(fixed)* | Line 30: `vault.id=${VAULT_ID}` *(fixed)* | ✅ Correct — runtime env var via Spring |
| `VAULT_ID` plaintext exposure | No raw `System.getenv()` | No `VAULT_ID=xxx` stub | ✅ Clean |
| Actuator exposure | N/A | Line 21: `include=*` | ❌ Wildcard — insecure |
| TLS / HTTPS | N/A | **Not configured** | ❌ Missing |
| Spring Security | **Not configured** | **Not configured** | ❌ Missing |
| `open-in-view` | N/A | Line 11: `false` | ✅ Correct |
| DB init scripts | N/A | Lines 3–4: parametrized | ✅ Acceptable |

---

*Report produced by ShipSafe Release Guardian — Risk Analyzer · Dependency Guard · Deployment Validator*
