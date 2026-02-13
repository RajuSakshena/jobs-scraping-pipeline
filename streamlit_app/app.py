```python
import streamlit as st
import os

# ------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------
st.set_page_config(
    page_title="Job Scraper Dashboard",
    layout="wide"
)

# ------------------------------------------------------
# GLOBAL CSS (Navbar + Footer Styling)
# ------------------------------------------------------
st.markdown("""
<style>

/* Remove default padding */
.block-container {
    padding-top: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
}

/* NAVBAR */
.navbar {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:14px 40px;
    background:#ffffff;
    border-bottom:1px solid #eaeaea;
    font-family: sans-serif;
}
.nav-right a{
    padding:6px 18px;
    margin-left:12px;
    border-radius:6px;
    text-decoration:none;
    font-weight:600;
}
.login-btn{
    background:#58a648;
    color:white;
}
.donate-btn{
    background:#0b3c5d;
    color:white;
}

/* HERO HEADER */
.hero {
    background:#083a5c;
    text-align:center;
    padding:60px 10px;
    color:white;
    font-family:sans-serif;
}

/* MAIN CONTENT */
.content {
    padding:40px;
    text-align:center;
    font-family:sans-serif;
}

/* FOOTER */
.footer {
    background:#003055;
    color:#cbd5e1;
    padding:50px 40px;
    margin-top:60px;
    font-family:sans-serif;
}
.footer a {
    color:#cbd5e1;
    text-decoration:none;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# NAVBAR
# ------------------------------------------------------
st.markdown("""
<div class="navbar">
    <div>
        <img src="https://via.placeholder.com/90x40" height="40">
    </div>
    <div class="nav-right">
        <a class="login-btn">Login</a>
        <a class="donate-btn">Donate</a>
    </div>
</div>
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
# FOOTER
# ------------------------------------------------------
st.markdown("""
<div class="footer">
    <p><b>The Metropolitan Institute</b></p>
    <p>
    The Metropolitan Institute is a think-and-do tank dedicated to building aspirational 
    and resilient regions.
    </p>

    <br>

    <p><b>Quick Links</b></p>
    <p>About Us | Our Research | Contact</p>

    <br>

    <p>© 2025 The Metropolitan Institute. All Rights Reserved.</p>
</div>
""", unsafe_allow_html=True)
```
