# How IBM Bob Was Used - Solo Project

**Team:** Solo (1 person)  
**Coins:** 40 total, 9.96 used, 39 left

Used **IBM Bob 2.0** as the core development assistant.

## 1. Agent Mode

Used one main command:

`Agent: Build Release Guardian per docs/PROBLEM.md. Spawn 3 internal subagents in parallel...`

Bob planned the work using a **Todo List (2/2)** and executed the tasks.

## 2. Parallel Tasks + Subagents

Bob spawned **3 internal subagents in parallel**:

- **Risk Analyzer (39s)**
  - Analyzed `git diff`
  - Flagged `VAULT_ID`
  - Location: `OwnerController.java:50`

- **Dependency Guard (31s)**
  - Audited `@src/pom.xml`
  - Flagged phantom dependency at line `64`

- **Deployment Validator (38s)**
  - Checked:
    `@src/src/main/resources/application.properties:21`
  - Validated actuator `*` configuration

All three tasks ran **in parallel, not sequentially**.

## 3. Document Understanding

Bob read and analyzed project files using context mentions:

- `@src/pom.xml`
- `@src/src/main/resources/application.properties`
- `@src/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java:50`
- `@docs/PROBLEM.md`
- `@deploy/codeengine.yaml`

## 4. Auto-Approve + Context Mentions

Used:

- `@` context mentions
- Auto-approve
- Automated validation through `scripts/shipsafe.py`
- Approximately 80 lines of validation logic
- `--stack react` support
- 16 release-safety checks

## 5. Bob-Built Code

Through Agent Mode, Bob created or completed:

- `scripts/shipsafe.py`
- `live_check.py`
- `notify.py`
- `excel_tasks.py`
- `dashboard/app.py`
- `deploy/codeengine.yaml`
- `.github/workflows/shipsafe.yaml`

## Optional watsonx Integration

Designed for future enterprise integration with:

- IBM Granite
- watsonx Orchestrate
- Slack notifications
- `.env`-based configuration

The integration is designed and ready for enterprise extension.

## Evidence

- `bob_sessions/00_account.png` — Bob account / 40 coins
- `bob_sessions/01_tasks.png` — 3 parallel subagents
- `bob_sessions/02_dashboard.png` — Live ShipSafe dashboard