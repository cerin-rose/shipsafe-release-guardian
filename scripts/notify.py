#!/usr/bin/env python3
"""Notify GO/NO-GO via Telegram → Slack → console. Reads FINAL_REPORT.md + live_status.json."""
import json, os, pathlib, re, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).parent.parent

def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

def build_message():
    overall = "UNKNOWN"
    live = {}
    report_path = ROOT / "FINAL_REPORT.md"
    live_path   = ROOT / "live_status.json"
    if report_path.exists():
        m = re.search(r"\*\*Overall:\*\*\s*(.+)", report_path.read_text())
        if m: overall = m.group(1).strip()
    if live_path.exists():
        live = json.loads(live_path.read_text())
    health  = live.get("health", {}).get("status_code", "N/A")
    vault   = "set" if live.get("vault_id", {}).get("set") else "missing"
    verdict = live.get("overall", overall)
    return (f"ShipSafe Release Guardian\n"
            f"Static scan: {overall}\n"
            f"Live check:  {verdict} | health={health} | VAULT_ID={vault}")

def post(url, payload, headers):
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    urllib.request.urlopen(req, timeout=10)

def notify(msg):
    load_env()
    bot  = os.environ.get("TELEGRAM_BOT")
    chat = os.environ.get("TELEGRAM_CHAT")
    if bot and chat:
        post(f"https://api.telegram.org/bot{bot}/sendMessage", {"chat_id": chat, "text": msg}, {})
        print("Sent via Telegram"); return
    webhook = os.environ.get("SLACK_WEBHOOK")
    if webhook:
        post(webhook, {"text": msg}, {})
        print("Sent via Slack"); return
    print("=== Console fallback ===\n" + msg)

if __name__ == "__main__":
    notify(build_message())
