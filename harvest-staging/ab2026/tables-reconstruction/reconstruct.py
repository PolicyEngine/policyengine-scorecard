"""Rebuild in memory the two HM Treasury workbooks' staged cells from the
4f424b9 claims file (cell coordinates are in each row's locator), plus the
section-heading fills (B5, B27, B43, B58, B82; review A T-4) and Table 6.2's
total row (E14:J14; review A T-2). The primaries themselves are not fetched."""
import gzip, json, re, sys, importlib, io, hashlib
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import column_index_from_string as ci

SRC = sys.argv[1]  # 4f424b9 claims file
rows = [json.loads(l) for l in gzip.open(SRC, "rt")]

def cell(r):
    m = re.search(r"\(cell ([A-Z]+)(\d+)\)", r["publication"]["locator"])
    return ci(m.group(1)), int(m.group(2))

def build():
    wb = Workbook(); ws1 = wb.active; ws1.title = "Table 6.1"; ws2 = wb.create_sheet("Table 6.2")
    wb4 = Workbook(); ws4 = wb4.active; ws4.title = "Rounded Table 6.4"
    yrs = ["2026-27", "2027-28", "2028-29", "2029-30", "2030-31", "2031-32"]
    for i, y in enumerate(yrs):
        ws1.cell(4, ci("F") + i, y); ws2.cell(4, ci("E") + i, y); ws4.cell(3, ci("I") + i, y)
    prev = None
    sections = {5, 27, 43, 58, 82}
    for r in rows:
        c = r["conditions"]; col, rr = cell(r)
        t = c["table"]
        ws = {"6.1": ws1, "6.2": ws2, "6.4": ws4}[t]
        ws.cell(rr, col, int(r["value_raw"]) if re.fullmatch(r"-?\d+", r["value_raw"]) else float(r["value_raw"]))
        if t == "6.1" and c["row_type"] == "measure":
            ws.cell(rr, 2, int(c["table_line"])); ws.cell(rr, 3, r["reform_hint"])
            ws.cell(rr, 4, c.get("fiscal_head")); ws.cell(rr, 5, c["head"])
            if c["heading"] != prev:
                parts = c["heading"].split(" > ")
                for k, p in enumerate(parts):
                    hr = rr - len(parts) + k
                    ws.cell(hr, 2, p)
                    if hr in sections:
                        ws.cell(hr, 2).fill = PatternFill(fill_type="solid", fgColor="FFFFCCCC")
                prev = c["heading"]
        elif t == "6.1":
            ws.cell(rr, 3, r["reform_hint"])
        elif t == "6.2":
            ws.cell(rr, 2, int(c["table_line"])); ws.cell(rr, 3, r["reform_hint"]); ws.cell(rr, 4, c.get("fiscal_head"))
        else:
            ws.cell(rr, 6, int(c["table_line"])); ws.cell(rr, 7, r["reform_hint"]); ws.cell(rr, 8, c["head"])
            ws.cell(rr - 1, 6).value or None
    # Table 6.4 group headings: the row above each group's first line
    seen = set()
    for r in rows:
        c = r["conditions"]
        if c["table"] == "6.4" and c["announced_at"] not in seen:
            seen.add(c["announced_at"]); _, rr = cell(r); ws4.cell(rr - 1, 6, c["announced_at"])
    # Table 6.2 total (review A T-2: cells E14:J14)
    ws2.cell(14, 3, "Total cash impacts of financial transactions")
    for i, v in enumerate([-230, -1160, -2290, -2795, -3675, -3850]):
        ws2.cell(14, ci("E") + i, v)
    return wb, wb4

def stage(mod, out):
    wb, wb4 = build()
    S = importlib.import_module(mod)
    if hasattr(S, "stage_all"):
        staged = S.stage_all(wb, wb4)
    else:
        staged = []
        S.stage_t61(wb, staged); S.stage_t62(wb, staged); S.stage_t64(wb4, staged)
    p = __import__("pathlib").Path(out); S.write_gz(staged, p)
    print(out, len(staged), hashlib.sha256(p.read_bytes()).hexdigest())

if __name__ == "__main__":
    stage(sys.argv[2], sys.argv[3])
