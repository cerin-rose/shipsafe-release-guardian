#!/usr/bin/env python3
"""Notify GO/NO-GO via Telegram → Slack → console. Reads FINAL_REPORT.md + live_status.json."""
# For Top Leads merging to main: Set TELEGRAM_BOT or SLACK_WEBHOOK in .env to get GO/NO-GO in any channel (Telegram/Slack/Teams) before merging to main
import json, os, pathlib, re, urllib.request, urllib.error
from datetime import datetime

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
    generated = ""
    live = {}
    report_path = ROOT / "FINAL_REPORT.md"
    live_path   = ROOT / "live_status.json"

    checks_pass = checks_fail = checks_warn = 0
    ICON = {"✅": "PASS", "🔴": "FAIL", "🟠": "FAIL", "🟡": "WARN"}

    if report_path.exists():
        text = report_path.read_text()
        m = re.search(r"\*\*Overall:\*\*\s*(.+)", text)
        if m: overall = m.group(1).strip()
        g = re.search(r"\*\*Generated:\*\*\s*([\d\-T: ]+)", text)
        if g: generated = g.group(1).strip()
        for line in text.splitlines():
            hit = re.match(r"\|\s*C\d+\s*\|.+\|\s*(\S+)\s*\|", line)
            if hit:
                s = ICON.get(hit.group(1), "PASS")
                if s == "PASS":   checks_pass += 1
                elif s == "FAIL": checks_fail += 1
                else:             checks_warn += 1

    if live_path.exists():
        live = json.loads(live_path.read_text())

    health  = live.get("health", {}).get("status_code", "N/A")
    vault   = "set" if live.get("vault_id", {}).get("set") else "missing"
    verdict = live.get("overall", overall)
    total   = checks_pass + checks_fail + checks_warn
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    return (
        f"ShipSafe Release Guardian\n"
        f"Sent: {sent_at}\n"
        f"Report generated: {generated or 'unknown'}\n"
        f"\n"
        f"Static scan: {overall}\n"
        f"Live check:  {verdict} | health={health} | VAULT_ID={vault}\n"
        f"\n"
        f"Checks ({total}):  Pass={checks_pass}  Fail={checks_fail}  Warn={checks_warn}"
    )

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
