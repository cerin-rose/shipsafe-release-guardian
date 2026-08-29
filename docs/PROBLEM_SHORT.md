# ShipSafe: IBM Cloud Release Readiness Guardian

## Problem

Release Managers and senior developers often spend **4–6 hours before every release** manually checking code changes, dependencies, environment variables, and deployment configuration.

For teams managing multiple microservices, one small miss can become a major production issue:

* A deleted API can break the frontend.
* A vulnerable dependency can create a security risk.
* A missing variable like `VAULT_ID` can cause deployment failure.
* Manual Excel checklists and tribal knowledge make the process inconsistent and hard to audit.

As a junior developer, I also noticed how much pressure this creates for Tech Leads who must review work from multiple developers and make sure everything still works together.

## Solution

**ShipSafe** is a one-command release-readiness guardian built with **IBM Bob 2.0**.

Run:

`Agent: Prepare IBM Cloud Release Readiness for v2.4`

Bob launches three parallel agents:

* **Risk Analyzer** — checks Git changes for breaking APIs and risky code changes.
* **Dependency Guard** — checks `pom.xml` and package changes for vulnerabilities and compatibility risks.
* **Deployment Validator** — compares what the code expects with `application.properties`, `codeengine.yaml`, and other deployment configuration.

ShipSafe combines the findings into one auditable report with:

* **GO / NO-GO**
* Blocking issues
* Recommended fixes
* Release notes
* SRE / Tech Lead review evidence

## Goal

Catch small release mistakes **before they become production incidents**.

**One command. Three agents. Safer releases.**
