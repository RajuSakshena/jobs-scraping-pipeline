import os
import traceback
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

from scrapers.oracle.oracle_jobs_scraper import scrape_jobs
from scrapers.c40.c40 import scrape_c40_jobs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
COMBINED_FILE = os.path.join(OUTPUT_DIR, "combined_jobs.xlsx")

FINAL_COLUMNS = [
    "Source",
    "Title",
    "Description",
    "Matched_Vertical",
    "Posting_Date",
    "Apply_Link"
]


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


def run_all_scrapers_and_combine():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    combined_rows = []

    # ================= ORACLE =================
    try:
        oracle_df = scrape_jobs()

        for _, row in oracle_df.iterrows():
            combined_rows.append({
                "Source": "Oracle Careers",
                "Title": row["Title"],
                "Description": None,
                "Matched_Vertical": None,
                "Posting_Date": row["Posting_Date"],
                "Apply_Link": f'=HYPERLINK("{row["Apply_Link"]}", "Apply")'
                if row["Apply_Link"] else ""
            })
    except Exception:
        print("❌ Oracle failed")
        traceback.print_exc()

    # ================= C40 =================
    try:
        c40_df = scrape_c40_jobs()

        for _, row in c40_df.iterrows():
            combined_rows.append({
                "Source": "C40",
                "Title": row["Title"],
                "Description": row["Description"],
                "Matched_Vertical": row["Matched_Vertical"],
                "Posting_Date": None,
                "Apply_Link": row["Apply_Link"]
            })
    except Exception:
        print("❌ C40 failed")
        traceback.print_exc()

    if not combined_rows:
        print("❌ No data collected")
        return

    combined_df = pd.DataFrame(combined_rows, columns=FINAL_COLUMNS)
    combined_df.to_excel(COMBINED_FILE, index=False, engine="openpyxl")

    format_excel(COMBINED_FILE)

    print(f"✅ Combined Excel created successfully: {COMBINED_FILE}")


if __name__ == "__main__":
    run_all_scrapers_and_combine()
