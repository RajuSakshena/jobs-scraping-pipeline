import streamlit as st
import os
import base64

# ------------------------------------------------------
# Base64 Image Encoder
# ------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_of_bin_file('TMI.png')

# ------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------
st.set_page_config(
    page_title="Job Scraper Dashboard",
    layout="wide"
)

# ------------------------------------------------------
# GLOBAL CSS (Including styles from scraper.html)
# ------------------------------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Force white background and remove dark styling */
.stApp {
    background-color: white !important;
    color: #0b3c5d !important;
}
body {
    background-color: white !important;
    font-family: 'Inter', sans-serif !important;
    color: #0b3c5d;
}
.block-container {
    padding-top: 0rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
}

/* Override Streamlit button for download visibility */
div.stButton > button:first-child {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background: #fff;
    color: #fff !important;
    font-weight: bold;
    border-radius: 6px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: 0.3s;
}
div.stButton > button:first-child:hover {
    background: #fff;
    color: #58a648 !important;
}

/* Navbar from scraper.html */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 5%;
    background: #ffffff;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 15px;
}

/* Footer from scraper.html */
footer {
    background: #003055;
    color: #cbd5e1;
    padding: 4rem 5% 2rem;
    margin-top: 0;
    margin-bottom: 0;
    font-family: 'Inter', sans-serif;
}
.footer-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr 1.5fr;
    gap: 2rem;
    margin-bottom: 3rem;
}
.footer-col h4 {
    color: #fff;
    margin-bottom: 1.5rem;
}
.footer-col ul {
    list-style: none;
    padding: 0;
    margin: 0;
}
.footer-col li {
    margin-bottom: 0.75rem;
}
.footer-col a {
    color: #cbd5e1;
    text-decoration: none;
    transition: 0.3s;
}
.footer-col a:hover {
    color: #58a648;
}
.donate-box {
    background: rgba(255,255,255,0.1);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
}
.footer-bottom {
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 2rem;
    text-align: center;
    font-size: 0.9rem;
}

/* Hero from original app.py */
.hero {
    background: #083a5c;
    text-align: center;
    padding: 60px 10px;
    color: white;
    font-family: 'Inter', sans-serif;
}

/* Content styling to match centered website layout */
.content {
    padding: 3rem 5% 0 5%;
    font-family: 'Inter', sans-serif;
    max-width: 1200px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# NAVBAR from scraper.html (without buttons)
# ------------------------------------------------------
st.markdown(f"""
<nav class="navbar">
    <div class="logo-container">
        <a href="index.html"><img src="data:image/png;base64,{logo_base64}" alt="TMI Logo"></a>
    </div>
    <div class="nav-right">
    </div>
</nav>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# HERO HEADER
# ------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>ImpactStream</h1>
    <p>We find the funding. You do the work.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# CONTENT SECTION
# ------------------------------------------------------
st.markdown('<div class="content">', unsafe_allow_html=True)

st.title("Job Scraper Dashboard")
st.markdown("Download the latest consolidated job listings collected from multiple sources.")

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

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# FOOTER from scraper.html (without donate button)
# ------------------------------------------------------
st.markdown(f"""
<footer>
    <div class="footer-grid">
        <div class="footer-col">
            <img src="data:image/png;base64,{logo_base64}" style="height:50px; margin-bottom:1rem;">
            <p>The Metropolitan Institute is a think-and-do tank dedicated to building aspirational and resilient regions.</p>
        </div>
        <div class="footer-col">
            <h4>Quick Links</h4>
            <ul>
                <li><a href="about.html">About Us</a></li>
                <li><a href="research.html">Our Research</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </div>
        <div class="footer-col">
            <h4>Connect</h4>
            <ul>
                <li><a href="https://x.com/TheMetroInst" target="_blank">Twitter / X</a></li>
                <li><a href="https://www.linkedin.com/company/the-metropolitan-institute" target="_blank">LinkedIn</a></li>
                <li><a href="https://www.instagram.com/themetropolitaninstitute" target="_blank">Instagram</a></li>
            </ul>
        </div>
        <div class="footer-col">
            <div class="donate-box">
                <h4>Support Our Mission</h4>
                <p>Help us bridge the gap between policy and people.</p>
            </div>
        </div>
    </div>
    <div class="footer-bottom">
        © 2025 The Metropolitan Institute. All Rights Reserved.
    </div>
</footer>
""", unsafe_allow_html=True)
