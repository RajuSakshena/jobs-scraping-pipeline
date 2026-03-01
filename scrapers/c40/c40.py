import os
import time
import json
import re
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ======================================================
# PATH SETUP
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYWORDS_FILE = os.path.join(BASE_DIR, "keywords.json")

CAREERS_URL = "https://c40.bamboohr.com/careers"
BASE_URL = "https://c40.bamboohr.com"


# ======================================================
# HELPERS
# ======================================================
def load_keywords():
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def match_verticals(title, description, keywords):
    text = f"{title} {description}".lower()
    matched = []
    for vertical, words in keywords.items():
        for w in words:
            if re.search(rf"\b{re.escape(w.lower())}\b", text):
                matched.append(vertical)
                break
    return ", ".join(matched) if matched else "N/A"


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


# ======================================================
# DEADLINE EXTRACTOR (STRUCTURE BASED)
# ======================================================
def extract_application_process(desc_container):
    """
    Extract full paragraph immediately after
    'Application Process:' heading.
    """
    deadline_text = ""

    app_span = desc_container.find(
        "span",
        string=lambda x: x and "Application Process" in x
    )

    if app_span:
        parent_p = app_span.find_parent("p")

        if parent_p:
            next_p = parent_p.find_next_sibling("p")
            if next_p:
                deadline_text = next_p.get_text(separator=" ", strip=True)

    return deadline_text


# ======================================================
# MAIN SCRAPER
# ======================================================
def scrape_c40_jobs():
    keywords = load_keywords()
    jobs = []

    driver = get_driver()
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(CAREERS_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        job_links = []

        for a in soup.select("a[href^='/careers/']"):
            href = a.get("href")
            title = a.get_text(strip=True)

            if href and title:
                job_links.append((BASE_URL + href, title))

        job_links = list(dict.fromkeys(job_links))

        for job_url, fallback_title in job_links:
            driver.get(job_url)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)

            job_soup = BeautifulSoup(driver.page_source, "html.parser")

            title_tag = job_soup.find("h3")
            title = title_tag.get_text(strip=True) if title_tag else fallback_title

            desc_container = job_soup.find("div", class_="BambooRichText")

            if not desc_container:
                continue

            description = desc_container.get_text(separator="\n", strip=True)
            deadline = extract_application_process(desc_container)

            matched_vertical = match_verticals(title, description, keywords)

            jobs.append({
                "Title": title,
                "Description": description,
                "Matched_Vertical": matched_vertical,
                "Deadline": deadline,
                "Apply_Link": job_url
            })

    finally:
        driver.quit()

    if not jobs:
        print("❌ No C40 jobs extracted")
        return pd.DataFrame(columns=[
            "Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"
        ])

    df = pd.DataFrame(jobs)

    print(f"✅ C40 scraping completed, {len(df)} jobs found")
    return df
