import streamlit as st
import os

st.set_page_config(page_title="Job Scraper Dashboard", layout="centered")
st.title("Job Scraper Dashboard")

# Output folder (same level as app.py)
base_path = os.path.join("output")

# Files to show
files = {
    "Oracle Jobs": "oracle_india_jobs.xlsx",
    "C40 Jobs": "c40_jobs.xlsx",
    "Combined Jobs": "combined_jobs.xlsx",
}

for name, filename in files.items():
    file_path = os.path.join(base_path, filename)
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Download {name}",
                data=f,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning(f"{name} file not found in {file_path}")