#!/usr/bin/env python3
"""Read FINAL_REPORT.md and write ShipSafe_Tasks.xlsx with one row per check."""
import re, pathlib
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

ROOT   = pathlib.Path(__file__).parent.parent
REPORT = ROOT / "FINAL_REPORT.md"
OUT    = ROOT / "ShipSafe_Tasks.xlsx"

SEVERITY_FILL = {
    "CRITICAL": "FFCCCC", "HIGH": "FFE0CC", "MEDIUM": "FFFACC", "LOW": "E8F4E8",
}
STATUS_ICON = {"✅": "PASS", "🔴": "FAIL", "🟠": "FAIL", "🟡": "WARN"}

FIX_HINTS = {
    "C06": "Set management.endpoints.web.exposure.include=health in application.properties",
    "C07": "Add server.ssl.* properties and configure a keystore for HTTPS",
    "C08": "Add spring-boot-starter-security to pom.xml and create a SecurityFilterChain bean",
    "C09": "Add flyway-core or liquibase-core to pom.xml for managed schema migrations",
    "C14": "Add CUDA_VISIBLE_DEVICES env var to pipeline.yaml GPU job definition",
    "C15": "Replace spring-boot-starter-webmvc with spring-boot-starter-web in pom.xml",
}

def parse_table(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r"\|\s*(C\d+)\s*\|\s*(\w+)\s*\|\s*\w+\s*\|\s*(.+?)\s*\|\s*`(.+?)`\s*\|\s*(\S+)\s*\|", line)
        if not m: continue
        tid, sev, bug, file_line, icon = m.groups()
        fp = file_line.split(":")[0].strip()
        ln = file_line.split(":")[1].strip() if ":" in file_line else ""
        status = STATUS_ICON.get(icon, "PASS")
        fix = FIX_HINTS.get(tid, "No action required — check passed") if status != "PASS" else "No action required — check passed"
        rows.append((tid, fp, ln, bug.strip(), sev, fix, status))
    return rows

text = REPORT.read_text()
rows = parse_table(text)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "ShipSafe Tasks"

headers = ["Task ID", "File", "Line", "Bug", "Severity", "Fix Suggestion", "Status"]
ws.column_dimensions["A"].width = 9
ws.column_dimensions["B"].width = 52
ws.column_dimensions["C"].width = 6
ws.column_dimensions["D"].width = 44
ws.column_dimensions["E"].width = 11
ws.column_dimensions["F"].width = 62
ws.column_dimensions["G"].width = 9

ws.append(headers)
for cell in ws[1]:
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F4E79")
    cell.alignment = Alignment(horizontal="center", wrap_text=True)

for tid, fp, ln, bug, sev, fix, status in rows:
    ws.append([tid, fp, ln, bug, sev, fix, "Pending" if status != "PASS" else "OK"])
    row = ws.max_row
    fill = PatternFill("solid", fgColor=SEVERITY_FILL.get(sev, "FFFFFF"))
    for col in range(1, 8):
        ws.cell(row, col).fill = fill
        ws.cell(row, col).alignment = Alignment(wrap_text=True, vertical="top")

wb.save(OUT)
print(f"Written {len(rows)} tasks → {OUT.name}")
