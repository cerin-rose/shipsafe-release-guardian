#!/usr/bin/env python3
"""ShipSafe: multi-stack release readiness scanner. Writes FINAL_REPORT.md.
Usage:
  python scripts/shipsafe.py                  # default: spring (pom.xml)
  python scripts/shipsafe.py --stack react    # React (package.json)
"""
import re, subprocess, pathlib, datetime, sys, argparse

ROOT = pathlib.Path(__file__).parent.parent

# ── Stack manifests ────────────────────────────────────────────────────────────
STACKS = {
    "spring": {
        "src":          ROOT / "src",
        "manifest":     ROOT / "src/pom.xml",
        "config":       ROOT / "src/src/main/resources/application.properties",
        "diff_glob":    "*.java",
        "diff_cwd":     ROOT / "src",
        # check overrides
        "dep_cve":      r"log4j-core|log4j(?!-over)|fastjson|jackson-databind.*2\.[01]\.",
        "dep_security": r"spring-boot-starter-security",
        "dep_db_mig":   r"flyway|liquibase",
        "dep_phantom":  r"spring-boot-starter-\w+-test|spring-boot-starter-webmvc\b",
        "api_break":    r'^[+-]\s*@(Get|Post|Put|Delete|Patch|Request)Mapping',
        "vault_config": r"vault\.id|VAULT_ID",
        "actuator":     r"management\.endpoints\.web\.exposure\.include\s*=\s*\*",
        "tls":          r"server\.ssl\.",
        "secret":       r'(?i)(password|api[_-]?key|token|secret)\s*=\s*\S{4,}(?!\$\{)',
    },
    "react": {
        "src":          ROOT / "frontend",
        "manifest":     ROOT / "frontend/package.json",
        "config":       ROOT / "frontend/.env",
        "diff_glob":    "*.{js,ts,jsx,tsx}",
        "diff_cwd":     ROOT / "frontend",
        # check overrides
        "dep_cve":      r'"(lodash)":\s*"[34]\.|"(axios)":\s*"0\.[0-9]\.',
        "dep_security": r'"(helmet|express-rate-limit|csurf)"',
        "dep_db_mig":   r'"(knex|sequelize|typeorm|prisma)"',
        "dep_phantom":  None,   # no equivalent for React
        "api_break":    r'^[+-]\s*(export\s+)?(async\s+)?function\s+\w+(Route|Handler|Controller)',
        "vault_config": r"VAULT_ID|REACT_APP_VAULT",
        "actuator":     None,   # not applicable
        "tls":          r"HTTPS=true|ssl",
        "secret":       r'(?i)(password|api[_-]?key|token|secret)\s*=\s*["\'][A-Za-z0-9]',
    },
}

parser = argparse.ArgumentParser()
parser.add_argument("--stack", choices=STACKS.keys(), default="spring")
args, _ = parser.parse_known_args()
S = STACKS[args.stack]

# ── Helpers ────────────────────────────────────────────────────────────────────
def read(p):
    try: return pathlib.Path(p).read_text(errors="ignore")
    except FileNotFoundError: return ""

def grep_first(pattern, path):
    if not pattern: return None
    for i, ln in enumerate(read(path).splitlines(), 1):
        if re.search(pattern, ln):
            return i, ln.strip()
    return None

def git_diff():
    try: return subprocess.check_output(
        ["git","diff","main...HEAD","--", S["diff_glob"]],
        cwd=S["diff_cwd"], stderr=subprocess.DEVNULL, text=True)
    except Exception: return ""

CHECKS = []

def chk(id_, domain, sev, title, path, pattern, ok_if_absent=False, fail_msg="", pass_msg=""):
    hit = grep_first(pattern, path)
    if pattern is None:   # check not applicable for this stack
        CHECKS.append((id_, domain, "INFO", f"{title} [N/A for {args.stack}]",
                        f"Not applicable for {args.stack} stack", str(path), True)); return
    passed = (hit is None) if ok_if_absent else (hit is not None)
    fl = f"{path}:{hit[0]}" if hit else str(path)
    CHECKS.append((id_, domain, sev, title,
                   (fail_msg if (hit if ok_if_absent else not hit) else pass_msg), fl, passed))

# ── Checks ─────────────────────────────────────────────────────────────────────
diff = git_diff()
has_break = bool(re.search(S["api_break"], diff, re.M)) if S["api_break"] else False
CHECKS.append(("C01","API","HIGH","Breaking API change in diff",
    "Route/mapping change detected in diff" if has_break else "No breaking route changes",
    f"{S['diff_cwd']} (git diff)", not has_break))

chk("C02","Dependency","CRITICAL","Manifest known-CVE artifact",
    S["manifest"], S["dep_cve"], ok_if_absent=True,
    fail_msg="Potentially vulnerable dependency detected", pass_msg="No known-CVE coords found")

chk("C03","Dependency","HIGH","requirements.txt / lockfile CVE",
    ROOT/"requirements.txt", r"pandas[=<>!]*[01]\.|numpy[=<>!]*1\.[01]\.",
    ok_if_absent=True,
    fail_msg="Stale/vulnerable package detected", pass_msg="No stale packages found")

chk("C04","Config","CRITICAL","VAULT_ID missing from config",
    S["config"], S["vault_config"],
    fail_msg=f"VAULT_ID not bound in {S['config'].name}",
    pass_msg="VAULT_ID binding present")

hit5 = grep_first(S["secret"], S["config"])
CHECKS.append(("C05","Security","CRITICAL","Hardcoded secret in config",
    "No hardcoded secrets detected" if hit5 is None else f"Possible hardcoded secret: {hit5[1]}",
    f"{S['config']}:{hit5[0]}" if hit5 else str(S["config"]), hit5 is None))

chk("C06","Config","HIGH","Actuator / debug endpoint wildcard exposed",
    S["config"], S["actuator"], ok_if_absent=True,
    fail_msg="All endpoints exposed via wildcard", pass_msg="Endpoint exposure is restricted")

chk("C07","Security","HIGH","No TLS/HTTPS configured",
    S["config"], S["tls"],
    fail_msg=f"No TLS config found in {S['config'].name}",
    pass_msg="TLS configuration present")

chk("C08","Security","HIGH","No security middleware/dependency",
    S["manifest"], S["dep_security"],
    fail_msg=f"Security library missing from {S['manifest'].name}",
    pass_msg="Security dependency present")

chk("C09","Database","MEDIUM","No DB migration tool",
    S["manifest"], S["dep_db_mig"],
    fail_msg="No DB migration library detected", pass_msg="DB migration tool present")

chk("C10","Container","MEDIUM","Dockerfile exposes privileged port (<1024)",
    ROOT/"src/Dockerfile", r"^EXPOSE\s+([1-9][0-9]{0,2})\b", ok_if_absent=True,
    fail_msg="EXPOSE uses port <1024", pass_msg="No privileged port or Dockerfile absent")

chk("C11","Pipeline","HIGH","Hardcoded S3 bucket in pipeline.yaml",
    ROOT/"pipeline.yaml", r'(?i)s3[_-]?bucket\s*[:=]\s*["\']?\w', ok_if_absent=True,
    fail_msg="S3 bucket hardcoded in pipeline.yaml", pass_msg="No hardcoded S3 bucket")

chk("C12","Notebook","MEDIUM","Notebook contains api_key literal",
    ROOT/"notebook.ipynb", r'api[_-]?key\s*=\s*["\'][A-Za-z0-9]', ok_if_absent=True,
    fail_msg="api_key literal in notebook", pass_msg="No api_key literal in notebook")

chk("C13","Notebook","LOW","Notebook hardcoded local CSV path",
    ROOT/"notebook.ipynb", r'["\'][A-Za-z]:[/\\]|["\']\/(?:home|Users|data)\/\S+\.csv',
    ok_if_absent=True,
    fail_msg="Hardcoded absolute CSV path in notebook", pass_msg="No hardcoded CSV path")

chk("C14","Pipeline","LOW","GPU env var (CUDA_VISIBLE_DEVICES) missing",
    ROOT/"pipeline.yaml", r"CUDA_VISIBLE_DEVICES",
    fail_msg="CUDA_VISIBLE_DEVICES not set", pass_msg="CUDA_VISIBLE_DEVICES configured")

chk("C16","Deploy","CRITICAL","VAULT_ID missing from deploy/codeengine.yaml",
    ROOT/"deploy/codeengine.yaml", r"name:\s*VAULT_ID",
    fail_msg="VAULT_ID not declared in codeengine.yaml env block",
    pass_msg="VAULT_ID present in codeengine.yaml")

hit15 = grep_first(S["dep_phantom"], S["manifest"]) if S["dep_phantom"] else None
CHECKS.append(("C15","Dependency","CRITICAL" if S["dep_phantom"] else "INFO",
    "Phantom / invalid dependencies in manifest",
    "No phantom deps detected" if hit15 is None else f"Phantom artifact: {hit15[1]}",
    f"{S['manifest']}:{hit15[0]}" if hit15 else str(S["manifest"]),
    hit15 is None))

# ── Write report ───────────────────────────────────────────────────────────────
go = all(c[6] for c in CHECKS)
lines = [f"# ShipSafe Release Readiness Report\n",
         f"**Generated:** {datetime.date.today()} | **Stack:** `{args.stack}`  \n",
         f"**Overall:** {'🟢 GO — all checks passed' if go else '🔴 NO-GO — see findings below'}\n\n---\n",
         "## Go / No-Go Table\n",
         "| ID | Severity | Domain | Check | File:Line | Status |\n",
         "|----|----------|--------|-------|-----------|--------|\n"]
for id_,dom,sev,title,detail,fl,ok in CHECKS:
    icon = "✅" if ok else ("🔴" if sev=="CRITICAL" else "🟠" if sev=="HIGH" else "🟡")
    short_fl = str(fl).replace(str(ROOT)+"/","")
    lines.append(f"| {id_} | {sev} | {dom} | {title} | `{short_fl}` | {icon} |\n")
lines += ["\n---\n\n## Finding Details\n"]
for id_,dom,sev,title,detail,fl,ok in CHECKS:
    if not ok:
        short_fl = str(fl).replace(str(ROOT)+"/","")
        lines.append(f"### {id_} — {title}\n**Severity:** {sev} | **File:Line:** `{short_fl}`  \n{detail}\n\n")
if go:
    lines.append("_All checks passed — no findings._\n")
(ROOT/"FINAL_REPORT.md").write_text("".join(lines))
print(f"[{args.stack}] {'GO' if go else 'NO-GO'} — report written to FINAL_REPORT.md")

import sys as _sys, runpy as _runpy
_sys.path.insert(0, str(pathlib.Path(__file__).parent))
_runpy.run_path(str(pathlib.Path(__file__).parent / "excel_tasks.py"))
from notify import notify, build_message
notify(build_message())
