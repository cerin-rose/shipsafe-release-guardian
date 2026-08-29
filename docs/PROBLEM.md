# ShipSafe: IBM Cloud Release Readiness Guardian

## Problem

Before every release, Release Managers and senior developers spend **4–6 hours manually verifying release readiness**.

They typically have to:

- Read 30+ commits using `git diff main...release`
- Audit 50+ dependencies in `pom.xml` for vulnerabilities
- Cross-check `application.properties` and `deploy.yaml`
- Verify required environment variables such as `VAULT_ID`
- Maintain Excel-based release checklists
- Rely on tribal knowledge from senior team members

This manual process is slow, inconsistent, and difficult to audit.

A single missed issue can cause:

- Breaking API changes reaching production
- Vulnerable dependencies such as `log4j 2.14.0`
- Missing IBM Cloud environment variables
- Deployment failures
- Production crashes
- Emergency rollbacks at 2 AM
- Failed IBM Cloud deployment governance checks

Currently, approximately **30% of releases require a hotfix**, and there is no reliable auditable proof showing that release-readiness checks were completed.

### Target Users

ShipSafe is designed for:

- Release Managers
- Site Reliability Engineers (SREs)
- Tech Leads
- Senior Developers

Especially teams managing **5–20 microservices** deployed on:

- IBM Cloud Code Engine
- Red Hat OpenShift
- Other IBM Cloud environments

---

## Solution: ShipSafe

**ShipSafe** is a one-command release-readiness guardian built using **IBM Bob 2.0**.

A developer or Release Manager runs:

```text
Agent: Prepare IBM Cloud Release Readiness for v2.4