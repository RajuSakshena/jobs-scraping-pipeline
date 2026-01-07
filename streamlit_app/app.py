import streamlit as st
import os

st.title("Job Scraper Dashboard")

files = {
    "Oracle Jobs": "../output/oracle_india_jobs.xlsx",
    "C40 Jobs": "../output/c40_jobs.xlsx",
}

for name, path in files.items():
    if os.path.exists(path):
        with open(path, "rb") as f:
            st.download_button(
                label=f"Download {name}",
                data=f,
                file_name=os.path.basename(path)
            )
    else:
        st.warning(f"{name} file not found")
