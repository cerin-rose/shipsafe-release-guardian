#!/usr/bin/env python3
"""Live deployment check: actuator health + VAULT_ID env. Writes live_status.json."""
import json, os, urllib.request, urllib.error, datetime

HEALTH_URL = "http://localhost:8080/actuator/health"
OUT = "live_status.json"

result = {
    "generated": datetime.datetime.now().isoformat(timespec="seconds"),
    "health": {"reachable": False, "status_code": None, "body": None},
    "vault_id": {"set": False, "source": None},
    "overall": "NO-GO",
}

# ── 1. Actuator health check ──────────────────────────────────────────────────
try:
    with urllib.request.urlopen(HEALTH_URL, timeout=5) as resp:
        result["health"]["status_code"] = resp.status
        result["health"]["reachable"] = True
        result["health"]["body"] = json.loads(resp.read())
except urllib.error.HTTPError as e:
    result["health"]["status_code"] = e.code
    result["health"]["reachable"] = True          # server replied, just non-2xx
    try: result["health"]["body"] = json.loads(e.read())
    except Exception: pass
except (urllib.error.URLError, OSError):
    result["health"]["status_code"] = 503
    result["health"]["body"] = "offline"          # server unreachable — graceful

# ── 2. VAULT_ID env check ─────────────────────────────────────────────────────
vault = os.environ.get("VAULT_ID")
if vault:
    result["vault_id"] = {"set": True, "source": "environment"}
else:
    result["vault_id"] = {"set": False, "source": None}

# ── 3. Overall verdict ────────────────────────────────────────────────────────
health_ok = result["health"]["status_code"] == 200
vault_ok  = result["vault_id"]["set"]
result["overall"] = "GO" if (health_ok and vault_ok) else "NO-GO"

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)

print(f"{result['overall']} | health={result['health']['status_code']} | VAULT_ID={'set' if vault_ok else 'missing'} → {OUT}")
