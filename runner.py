import os
import traceback
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

from scrapers.estm.estm import scrape_jobs as scrape_estm_jobs
from scrapers.c40.c40 import scrape_c40_jobs
from scrapers.developmentaid.developmentaid import scrape_jobs as scrape_developmentaid_jobs

# ======================================================
# PATH SETUP
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
COMBINED_FILE = os.path.join(OUTPUT_DIR, "Combined.xlsx")

FINAL_COLUMNS = [
    "Source",
    "Title",
    "Description",
    "Matched_Vertical",
    "Posting_Date",
    "Apply_Link"
]

# ======================================================
# EXCEL FORMAT
# ======================================================
def format_excel(path):
    wb = load_workbook(path)
    ws = wb.active

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 55
    ws.column_dimensions["C"].width = 120
    ws.column_dimensions["D"].width = 35
    ws.column_dimensions["E"].width = 22
    ws.column_dimensions["F"].width = 45

    for row in ws.iter_rows(min_row=2):
        ws.row_dimensions[row[0].row].height = 80
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(path)

# ======================================================
# MAIN RUNNER
# ======================================================
def run_all_scrapers_and_combine():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    combined_rows = []

    # ================= ESTM =================
    try:
        estm_df = scrape_estm_jobs()

        for _, row in estm_df.iterrows():
            link = row.get("Apply_Link", "")
            combined_rows.append({
                "Source": "ESTM",
                "Title": row.get("Title"),
                "Description": None,
                "Matched_Vertical": None,
                "Posting_Date": row.get("Posting_Date"),
                "Apply_Link": f'=HYPERLINK("{link}", "Apply")' if link else ""
            })
    except Exception:
        print("❌ ESTM failed")
        traceback.print_exc()

    # ================= C40 =================
    try:
        c40_df = scrape_c40_jobs()

        for _, row in c40_df.iterrows():
            combined_rows.append({
                "Source": "C40",
                "Title": row.get("Title"),
                "Description": row.get("Description"),
                "Matched_Vertical": row.get("Matched_Vertical"),
                "Posting_Date": None,
                "Apply_Link": row.get("Apply_Link")
            })
    except Exception:
        print("❌ C40 failed")
        traceback.print_exc()

    # ================= DevelopmentAid =================
    try:
        da_df = scrape_developmentaid_jobs()

        for _, row in da_df.iterrows():
            link = row.get("Apply_Link", "")
            combined_rows.append({
                "Source": "DevelopmentAid",
                "Title": row.get("Title"),
                "Description": row.get("Description"),
                "Matched_Vertical": row.get("Category"),
                "Posting_Date": None,
                "Apply_Link": f'=HYPERLINK("{link}", "Apply")' if link else ""
            })
    except Exception:
        print("❌ DevelopmentAid failed")
        traceback.print_exc()

    # ================= FINAL EXPORT =================
    if not combined_rows:
        print("❌ No data collected from any scraper")
        return

    combined_df = pd.DataFrame(combined_rows, columns=FINAL_COLUMNS)
    combined_df.to_excel(COMBINED_FILE, index=False, engine="openpyxl")

    format_excel(COMBINED_FILE)

    print(f"✅ Combined Excel created successfully: {COMBINED_FILE}")

# ======================================================
# ENTRY POINT
# ======================================================
if __name__ == "__main__":
    run_all_scrapers_and_combine()
