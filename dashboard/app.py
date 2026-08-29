#!/usr/bin/env python3
"""ShipSafe dashboard — Flask app serving GO/NO-GO, 15-check table, history."""
import json, re, pathlib
from flask import Flask, render_template, jsonify
import openpyxl

ROOT   = pathlib.Path(__file__).parent.parent
app    = Flask(__name__, template_folder=".")

def read(p):
    try: return pathlib.Path(p).read_text(errors="ignore")
    except FileNotFoundError: return ""

def report_data():
    text    = read(ROOT / "FINAL_REPORT.md")
    overall = "UNKNOWN"
    m = re.search(r"\*\*Overall:\*\*\s*(.+)", text)
    if m: overall = m.group(1).strip()
    rows = []
    ICON = {"✅": "PASS", "🔴": "FAIL", "🟠": "FAIL", "🟡": "WARN"}
    for line in text.splitlines():
        hit = re.match(r"\|\s*(C\d+)\s*\|\s*(\w+)\s*\|\s*\w+\s*\|\s*(.+?)\s*\|\s*`(.+?)`\s*\|\s*(\S+)\s*\|", line)
        if hit:
            tid, sev, bug, fl, icon = hit.groups()
            rows.append({"id": tid, "severity": sev, "bug": bug.strip(),
                         "file_line": fl, "status": ICON.get(icon, "PASS")})
    return overall, rows

def live_data():
    try: return json.loads(read(ROOT / "live_status.json"))
    except Exception: return {}

def xlsx_history():
    path = ROOT / "ShipSafe_Tasks.xlsx"
    if not path.exists(): return []
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = [{"id": r[0], "file": r[1], "line": r[2], "bug": r[3],
             "severity": r[4], "fix": r[5], "status": r[6]}
            for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
    wb.close(); return rows

@app.route("/")
def index():
    overall, checks = report_data()
    live  = live_data()
    tasks = xlsx_history()
    return render_template("index.html", overall=overall, checks=checks,
                           live=live, tasks=tasks)

@app.route("/api/status")
def api_status():
    overall, checks = report_data()
    live = live_data()
    return jsonify({"overall": overall, "live": live,
                    "pass": sum(1 for c in checks if c["status"]=="PASS"),
                    "fail": sum(1 for c in checks if c["status"]!="PASS")})

if __name__ == "__main__":
    app.run(debug=False, port=5001)
