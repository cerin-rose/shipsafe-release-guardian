# ShipSafe: IBM Cloud Release Readiness Guardian

**Solo Student Project | Beginner PHP → Java | Binghamton University**

> **One command turns hours of manual release checking into an automated GO / NO-GO release review.**

```bash
python3 scripts/shipsafe.py
```

ShipSafe uses **IBM Bob 2.0** and three specialized release-readiness agents to inspect code changes, dependencies, configuration, and deployment risks before software reaches production.

---

## Why I Built ShipSafe

When I started working in a real development team, I noticed how much responsibility sits with Tech Leads and Release Managers.

Multiple developers finish features at different times. Pull requests need review. Branches need merging. Dependencies change. Configuration changes. And eventually, someone has to answer:

> **Is this release actually safe to ship?**

A tiny issue can create a much bigger production problem:

* One missing environment variable
* One vulnerable dependency
* One deleted API
* One deployment configuration mismatch

ShipSafe was built to catch those small mistakes **before production does**.

---

# Problem

Before a release, Release Managers and senior developers may spend **4–6 hours manually checking**:

* `git diff`
* Java source changes
* `pom.xml`
* dependency vulnerabilities
* `application.properties`
* environment variables such as `VAULT_ID`
* deployment configuration
* release checklists

A single missed issue can result in:

```text
Small configuration mistake
        ↓
Deployment failure
        ↓
Production incident
        ↓
Rollback
        ↓
Emergency hotfix
```

For example, application code may expect:

```java
System.getenv("VAULT_ID")
```

while the deployment configuration never provides `VAULT_ID`.

The code may look fine locally, but the deployed application can fail.

Traditional release checks are often:

* Manual
* Sequential
* Difficult to audit
* Dependent on senior-team knowledge
* Easy to miss under time pressure

---

# Solution

**ShipSafe** is an AI-powered release-readiness guardian built with **IBM Bob 2.0**.

The developer runs:

```bash
python3 scripts/shipsafe.py
```

ShipSafe analyzes the application across multiple release-risk areas and generates a clear:

# GO / NO-GO

decision.

---

# Three Parallel Release Agents

ShipSafe separates release analysis into three specialized areas.

## Risk Analyzer

Checks:

```text
git diff
Java source
API changes
breaking changes
```

Example risks:

* Deleted API endpoints
* Unexpected code removals
* Breaking contracts
* High-risk source changes

---

## Dependency Guard

Checks:

```text
pom.xml
package dependencies
known vulnerability patterns
major dependency changes
```

Example risks:

* Vulnerable dependencies
* Phantom starters
* Dependency compatibility problems
* Security-sensitive version changes

---

## Deployment Validator

Checks whether the deployment environment matches what the application expects.

It compares:

```text
Application code
application.properties
deploy/codeengine.yaml
environment variables
```

Example:

```text
Code expects VAULT_ID
        +
Deployment does not provide VAULT_ID
        ↓
BLOCKER
```

During the Bob workflow, the three checks ran in parallel at approximately:

| Agent                | Time |
| -------------------- | ---: |
| Dependency Guard     |  31s |
| Deployment Validator |  38s |
| Risk Analyzer        |  39s |

The parallel design reduces waiting time and keeps each agent focused on one type of release risk.

See:

```text
docs/ARCHITECTURE.md
```

for the architecture decision.

---

# 16 Release Readiness Checks

ShipSafe currently evaluates checks including:

1. Breaking API changes
2. Maven dependency / CVE risk
3. Missing `VAULT_ID`
4. Hardcoded secrets
5. Exposed actuator endpoints
6. Missing TLS configuration
7. Missing security configuration
8. Database migration risks
9. Dockerfile validation
10. `s3.bucket` configuration
11. Notebook API keys
12. Hardcoded CSV paths
13. GPU configuration
14. Phantom Maven starters
15. Application environment mapping
16. `deploy/codeengine.yaml` secret / `VAULT_ID` validation

Each check contributes to the final release decision.

---

# Outputs

Running ShipSafe produces multiple release artifacts.

## 1. FINAL_REPORT.md

```text
FINAL_REPORT.md
```

Contains:

* 16 release checks
* PASS / FAIL status
* GO / NO-GO recommendation
* Release findings
* Fix guidance

---

## 2. ShipSafe_Tasks.xlsx

```text
ShipSafe_Tasks.xlsx
```

Contains:

* 16 release tasks
* Current status
* Pending / OK state
* Fix suggestions
* Audit-friendly task history

---

## 3. Dashboard

Run:

```bash
python3 dashboard/app.py
```

Then open:

```text
http://127.0.0.1:5001
```

The dashboard shows:

* Release readiness checks
* Current status
* Live application health
* Task history
* Findings

---

## 4. Live Check

Run:

```bash
python3 scripts/live_check.py
```

ShipSafe creates:

```text
live_status.json
```

Example:

```text
503 — application offline
```

This allows release readiness to include the application's live health state.

---

## 5. Notifications

ShipSafe also includes:

```text
notify.py
```

for extending release findings to notification systems such as:

* Slack
* Telegram

---

# Usage

## Clone the Project

```bash
git clone https://github.com/cerin-rose/shipsafe-release-guardian.git
cd shipsafe-release-guardian
```

## Run ShipSafe for Spring / Java

```bash
python3 scripts/shipsafe.py
```

## Run ShipSafe for React

```bash
python3 scripts/shipsafe.py --stack react
```

## Run Live Health Check

```bash
python3 scripts/live_check.py
```

## Start Dashboard

```bash
python3 dashboard/app.py
```

Open:

```text
http://127.0.0.1:5001
```

---

# Architecture

The automated workflow is designed as:

```text
Developer
    ↓
Push to release/*
    ↓
.github/workflows/shipsafe.yaml
    ↓
scripts/shipsafe.py
    ↓
16 Release Checks
    ↓
live_check.py
    ↓
notify.py
    ↓
┌──────────────────────┬──────────────────────┐
│                      │                      │
▼                      ▼                      ▼
FINAL_REPORT.md   ShipSafe_Tasks.xlsx      Dashboard
```

The Bob agent architecture adds three specialized parallel analysis areas:

```text
                  IBM Bob
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
      Risk       Dependency    Deployment
    Analyzer       Guard       Validator
        │            │            │
        └────────────┼────────────┘
                     ▼
                GO / NO-GO
```

See:

```text
docs/ARCHITECTURE.md
```

for why ShipSafe uses three parallel specialists instead of one generic sequential agent.

---

# Demo

The demo uses the public MIT-licensed:

```text
spring-petclinic
```

application with controlled synthetic release issues.

Current examples include:

### C04 — VAULT_ID

```text
application.properties:30
```

Status:

```text
PASS
```

after fixing the application configuration.

### C16 — Code Engine Deployment

```text
deploy/codeengine.yaml
```

Status:

```text
FAIL
```

because deployment configuration still requires attention.

This is intentional: ShipSafe reports the real current release state instead of forcing everything to appear green for the demo.

---

# Evidence It Worked

The first ShipSafe run produced:

```text
FINAL REPORT: NO-GO
```

with multiple release domains blocked.

After fixing the `VAULT_ID` configuration issue:

```text
Secrets & Credentials: GO
```

The relevant findings were marked fixed.

The overall release may still remain:

```text
NO-GO
```

because existing dependency or deployment technical debt remains.

That is expected behavior.

ShipSafe is designed to report an **honest production-readiness state**, not simply produce a successful demo result.

---

# Before vs ShipSafe

| Before                         | ShipSafe                            |
| ------------------------------ | ----------------------------------- |
| Hours of manual checks         | One command                         |
| Multiple people checking files | Automated release workflow          |
| Sequential investigation       | Parallel specialized analysis       |
| Excel-only checklist           | Markdown + Excel + Dashboard        |
| Tribal knowledge               | Repeatable checks                   |
| Easy to miss env variables     | Cross-file configuration validation |
| Difficult to audit             | Auditable release artifacts         |
| Problems found late            | Problems surfaced before deployment |

---

# Impact

ShipSafe aims to reduce:

* Release-review time
* Repeated Tech Lead review cycles
* Configuration mistakes
* Dependency risks
* Last-minute deployment failures
* Release anxiety
* Manual checklist work

For teams managing multiple services, the same workflow can be reused instead of rebuilding a release checklist for every service.

---

# IBM Bob 2.0 Usage

IBM Bob was used as the core development and orchestration environment.

ShipSafe demonstrates:

* **Agent Mode**
* **Parallel Subagents**
* **Document Understanding**
* **Repository Context Mentions**
* **Code Generation**
* **Release workflow orchestration**

Bob analyzed context including:

```text
@src/pom.xml
@application.properties
@OwnerController.java
@docs/PROBLEM.md
@deploy/codeengine.yaml
```

Bob was also used to help build:

```text
scripts/shipsafe.py
scripts/live_check.py
notify.py
excel_tasks.py
dashboard/app.py
deploy/codeengine.yaml
.github/workflows/shipsafe.yaml
```

Full details:

```text
docs/BOB_USAGE.md
```

---

# Data Sources

ShipSafe uses:

## Public Application

```text
spring-petclinic
```

* Public
* MIT licensed
* Real Spring Java application

## Synthetic Test Data

Controlled test cases include:

* Synthetic `VAULT_ID` issue
* Synthetic deployment configuration
* Synthetic vulnerable dependency examples
* Placeholder values only

The project contains:

* No personal information
* No client data
* No company-confidential data
* No real production secrets

Full details:

```text
docs/DATA_SOURCES.md
```

---

# Reusable Beyond PetClinic

ShipSafe was demonstrated using Spring PetClinic, but the release-checking pattern is reusable.

Current stack support includes:

```bash
python3 scripts/shipsafe.py
```

for the Java/Spring workflow and:

```bash
python3 scripts/shipsafe.py --stack react
```

for React-style projects.

The architecture can be extended to additional services by adapting the file paths and release checks.

---

# Future Integration

ShipSafe can grow into a fully automated release gate.

Possible integrations include:

* GitHub Actions
* Jenkins
* Jira
* Slack
* IBM Cloud Code Engine
* IBM Secrets Manager
* watsonx.ai Granite
* watsonx Orchestrate
* IBM Cloudant for release audit history

Future flow:

```text
Developer Push
      ↓
ShipSafe
      ↓
3 Parallel Release Checks
      ↓
GO / NO-GO
      ↓
Team Notification
      ↓
Human Approval
      ↓
IBM Cloud Deployment
```

---

# The Idea in One Line

> **ShipSafe catches the tiny release mistakes before they become big production problems.**

**One command. Three focused checks. One clear release decision.**
