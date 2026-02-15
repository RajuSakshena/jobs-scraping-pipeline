import os
import traceback
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

from scrapers.estm.estm import scrape_jobs as scrape_estm_jobs
from scrapers.c40.c40 import scrape_c40_jobs
from scrapers.developmentaid.developmentaid import scrape_jobs as scrape_developmentaid_jobs


# ======================================================
# PATH SETUP (Flask Safe Version)
# ======================================================

BASE_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
COMBINED_FILE = os.path.join(OUTPUT_DIR, "Combined.xlsx")


FINAL_COLUMNS = [
    "Source",
    "Title",
    "Description",
    "Matched_Vertical",
    "Deadline",          # ✅ Changed
    "Apply_Link"
]


# ======================================================
# EXCEL FORMAT FUNCTION
# ======================================================

def format_excel(path):
    try:
        wb = load_workbook(path)
        ws = wb.active

        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 55
        ws.column_dimensions["C"].width = 120
        ws.column_dimensions["D"].width = 35
        ws.column_dimensions["E"].width = 22   # Deadline column
        ws.column_dimensions["F"].width = 45

        for row in ws.iter_rows(min_row=2):
            ws.row_dimensions[row[0].row].height = 80
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

        wb.save(path)
        print("✅ Excel formatting applied")

    except Exception:
        print("❌ Excel formatting failed")
        traceback.print_exc()


# ======================================================
# MAIN RUNNER FUNCTION
# ======================================================

def run_all_scrapers_and_combine():
    try:
        print("🚀 Starting scraper process...")

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        combined_rows = []

        # ================= ESTM =================
        try:
            print("🔎 Running ESTM scraper...")
            estm_df = scrape_estm_jobs()

            if estm_df is not None and not estm_df.empty:
                for _, row in estm_df.iterrows():
                    link = row.get("Apply_Link", "")
                    combined_rows.append({
                        "Source": "ESTM",
                        "Title": row.get("Title"),
                        "Description": None,
                        "Matched_Vertical": None,
                        "Deadline": row.get("Deadline"),   # ✅ Changed
                        "Apply_Link": f'=HYPERLINK("{link}", "Apply")' if link else ""
                    })
                print(f"✅ ESTM rows added: {len(estm_df)}")
            else:
                print("⚠ ESTM returned no data")

        except Exception:
            print("❌ ESTM failed")
            traceback.print_exc()

        # ================= C40 =================
        try:
            print("🔎 Running C40 scraper...")
            c40_df = scrape_c40_jobs()

            if c40_df is not None and not c40_df.empty:
                for _, row in c40_df.iterrows():
                    combined_rows.append({
                        "Source": "C40",
                        "Title": row.get("Title"),
                        "Description": row.get("Description"),
                        "Matched_Vertical": row.get("Matched_Vertical"),
                        "Deadline": None,   # C40 does not provide
                        "Apply_Link": row.get("Apply_Link")
                    })
                print(f"✅ C40 rows added: {len(c40_df)}")
            else:
                print("⚠ C40 returned no data")

        except Exception:
            print("❌ C40 failed")
            traceback.print_exc()

        # ================= DevelopmentAid =================
        try:
            print("🔎 Running DevelopmentAid scraper...")
            da_df = scrape_developmentaid_jobs()

            if da_df is not None and not da_df.empty:
                for _, row in da_df.iterrows():
                    link = row.get("Apply_Link", "")
                    combined_rows.append({
                        "Source": "DevelopmentAid",
                        "Title": row.get("Title"),
                        "Description": row.get("Description"),
                        "Matched_Vertical": row.get("Category"),
                        "Deadline": None,   # Not available
                        "Apply_Link": f'=HYPERLINK("{link}", "Apply")' if link else ""
                    })
                print(f"✅ DevelopmentAid rows added: {len(da_df)}")
            else:
                print("⚠ DevelopmentAid returned no data")

        except Exception:
            print("❌ DevelopmentAid failed")
            traceback.print_exc()

        # ================= FINAL EXPORT =================
        if not combined_rows:
            print("❌ No data collected from any scraper")
            return None

        combined_df = pd.DataFrame(combined_rows, columns=FINAL_COLUMNS)

        combined_df.to_excel(COMBINED_FILE, index=False, engine="openpyxl")

        format_excel(COMBINED_FILE)

        print("📁 Output directory:", OUTPUT_DIR)
        print("📄 Combined file created at:", COMBINED_FILE)
        print("🎉 Scraping process completed successfully!")

        return COMBINED_FILE

    except Exception:
        print("🔥 Critical error in main runner")
        traceback.print_exc()
        return None


# ======================================================
# DIRECT RUN SUPPORT
# ======================================================

if __name__ == "__main__":
    run_all_scrapers_and_combine()
