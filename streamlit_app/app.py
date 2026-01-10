import streamlit as st
import os

# ------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------
st.set_page_config(
    page_title="Job Scraper Dashboard",
    layout="centered"
)

st.title("Job Scraper Dashboard")

st.markdown(
    "Download the latest consolidated job listings collected from multiple sources."
)

# ------------------------------------------------------
# Path Configuration
# ------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

COMBINED_FILE = "Combined.xlsx"
COMBINED_PATH = os.path.join(OUTPUT_DIR, COMBINED_FILE)

# ------------------------------------------------------
# Download Section
# ------------------------------------------------------
st.markdown("### Available Download")

if os.path.exists(COMBINED_PATH):
    with open(COMBINED_PATH, "rb") as file:
        st.download_button(
            label="Download Combined Jobs (ESTM, Developmentaid & C40)",
            data=file,
            file_name=COMBINED_FILE,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("Job data is not available at the moment. Please try again later.")
