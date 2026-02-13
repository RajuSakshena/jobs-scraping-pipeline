import streamlit as st
import os
import base64

# ------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------
st.set_page_config(
    page_title="Job Scraper Dashboard",
    layout="wide"
)

# ------------------------------------------------------
# Image Loading
# ------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(APP_DIR, "TMI.png")
logo_base64 = ""
try:
    with open(logo_path, 'rb') as f:
        logo_base64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    pass

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
    padding-top: 1rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    padding-bottom: 0rem !important;
}

/* Override Streamlit button for download visibility */
div.stDownloadButton > button:first-child {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background: #fff;
    color: #000 !important;
    font-weight: bold;
    border-radius: 6px;
    text-decoration: none;
    border: 1px solid #000;
    cursor: pointer;
    transition: 0.3s;
}
div.stDownloadButton > button:first-child:hover {
    background: #000;
    color: #fff !important;
    border: 1px solid #000;
}

/* Navbar from scraper.html */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 5% 0.5rem 5%;
    background: #ffffff;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 15px;
}
.logo-container {
    width: 150px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 5px;
    box-sizing: border-box;
}
.logo-container img {
    max-height: 40px;
    width: auto;
    object-fit: contain;
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
    padding: 4rem 5% 4rem 5%;
    font-family: 'Inter', sans-serif;
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}
.content > * {
    margin-bottom: 2rem;
}
.content h1, .content h3, .content p {
    text-align: center;
}
.content .stAlert {
    margin: 0 auto;
    width: fit-content;
}
.content .stDownloadButton {
    display: flex;
    justify-content: center;
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

st.markdown('<h1 style="text-align: center;">Job Scraper Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;">Download the latest consolidated job listings collected from multiple sources.</p>', unsafe_allow_html=True)

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
st.markdown('<h3 style="text-align: center;">Available Download</h3>', unsafe_allow_html=True)

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
