# ShipSafe Architecture — Why 3 Parallel Subagents, Not 1

## Architecture Decision

ShipSafe uses **3 specialized subagents in parallel** instead of one generic agent:

* **Risk Analyzer**
* **Dependency Guard**
* **Deployment Validator**

Each agent focuses on one release-risk domain, while the main Bob agent acts as the orchestrator.

---

## Why Not One Agent?

### One Generic Agent — Sequential

A single agent would check each area one after another:

`Risk → Dependency → Deployment`

Approximate time:

* Risk: 40s
* Dependency: 30s
* Deployment: 30s

**Total: ~100 seconds**

This also mixes very different contexts such as:

* Git diffs
* Java source
* `pom.xml`
* deployment YAML
* environment variables

That can create unnecessary context noise.

---

### Three Parallel Subagents

ShipSafe runs all three checks at the same time:

* Risk Analyzer: **39s**
* Dependency Guard: **31s**
* Deployment Validator: **38s**

Total wall-clock time becomes approximately:

**39 seconds**

That is about **60% faster** than sequential execution.

Each agent also gets a cleaner, isolated responsibility:

```text
Risk Agent        → Code + Git Diff
Dependency Agent  → Libraries + CVEs
Deployment Agent  → Config + Environment
```

---

## Architecture

```text
Developer
   │
   │ Agent: Prepare Release v2.4
   ▼
Main Bob Agent / Orchestrator
   │
   ├── Risk Analyzer
   │     ├─ git diff main...release
   │     └─ @src/*.java
   │
   ├── Dependency Guard
   │     ├─ pom.xml
   │     ├─ requirements.txt
   │     └─ vulnerability checks
   │
   └── Deployment Validator
         ├─ application.properties
         ├─ deploy/codeengine.yaml
         └─ VAULT_ID / env validation
   │
   ▼
Merge Findings
   │
   ├── FINAL_REPORT.md
   ├── ShipSafe_Tasks.xlsx
   └── Dashboard
```

Optional reasoning and orchestration can be extended with:

* **watsonx.ai Granite**
* **watsonx Orchestrate**

---

## How It Scales

Each microservice can receive its own 3-agent release guardian.

Example:

```bash
python scripts/shipsafe.py --service payments
python scripts/shipsafe.py --service users
python scripts/shipsafe.py --service orders
```

Or through a GitHub Actions matrix:

```text
Service 1 → 3 agents
Service 2 → 3 agents
Service 3 → 3 agents
...
```

For 100 services, the architecture can distribute checks across available parallel workers instead of forcing one agent to inspect every service sequentially.

The key idea is:

> **More services do not require one increasingly overloaded release agent. Each service gets its own isolated release check.**

---

## Trade-Off

### Cost

Three subagents used approximately:

**9.96 Bob coins**

compared with roughly **3 coins** for a simpler single-agent run.

The additional cost provides:

* Faster release checks
* Cleaner agent context
* Specialized analysis
* Easier debugging
* Better scalability

For a release gate, the extra cost is justified by reduced waiting time and stronger validation.

### Complexity

Parallel execution requires orchestration.

ShipSafe keeps that complexity inside Bob's agent workflow, so the developer still interacts with the system using one command.

---

## Solo vs Team

### Solo Developer

```text
1 Developer
     ↓
3 Specialized AI Agents
```

A solo developer effectively gets three focused release reviewers working at once.

### Team of 5

```text
5 Services
   ↓
5 × 3 Specialized Agents
   ↓
15 Focused Release Checks
```

Each service can be evaluated independently without forcing every check through one shared context.

---

## Why This Architecture Fits ShipSafe

ShipSafe is not trying to build one AI that knows everything.

It is building a **small release team**.

One agent asks:

> What changed?

Another asks:

> Is anything unsafe?

Another asks:

> Will this actually deploy?

The orchestrator combines those answers into one decision:

# GO / NO-GO
