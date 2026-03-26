import os
import time
import json
import re
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ======================================================
# PATH SETUP
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYWORDS_FILE = os.path.join(BASE_DIR, "keywords.json")

C40_RFP_URL = "https://www.c40.org/work-with-c40/"


# ======================================================
# HELPERS
# ======================================================
def load_keywords():
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# 🔥 STRICT MATCHING LOGIC
def match_verticals(title, description, keywords):
    text = f"{title} {description}".lower()
    matched = []

    for vertical, words in keywords.items():
        count = 0
        unique_words = set(words)

        for w in unique_words:
            if re.search(rf"\b{re.escape(w.lower())}\b", text):
                count += 1

        # ✅ STRICT CONDITION (minimum 2 keyword match)
        if count >= 2:
            matched.append(vertical)

    return ", ".join(matched) if matched else "N/A"


# ======================================================
# MAIN SCRAPER (RFP VERSION)
# ======================================================
def scrape_c40_jobs():
    keywords = load_keywords()
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        # stealth
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        print("🔍 Opening C40 RFP page...")
        page.goto(C40_RFP_URL, timeout=60000)

        time.sleep(5)
        page.mouse.wheel(0, 3000)
        time.sleep(3)

        soup = BeautifulSoup(page.content(), "html.parser")

        rfp_cards = soup.select("a.link-cards-item")
        print(f"✅ Found {len(rfp_cards)} RFPs")

        for card in rfp_cards:
            try:
                title_tag = card.select_one("h3.link-cards-item__heading")
                deadline_tag = card.select_one("h4.link-cards-item__subheading")
                link = card.get("href")

                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                deadline = deadline_tag.get_text(strip=True) if deadline_tag else "N/A"

                description = f"{title}\n{deadline}"

                matched_vertical = match_verticals(title, description, keywords)

                data.append({
                    "Title": title,
                    "Description": description,
                    "Matched_Vertical": matched_vertical,
                    "Deadline": deadline,
                    "Apply_Link": link
                })

                print(f"✔️ {title} → {matched_vertical}")

            except Exception as e:
                print(f"⚠️ Error: {e}")

        browser.close()

    # ======================================================
    # RETURN DATAFRAME
    # ======================================================
    if not data:
        print("❌ No C40 RFP extracted")
        return pd.DataFrame(columns=[
            "Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"
        ])

    df = pd.DataFrame(data)

    print(f"✅ C40 RFP scraping completed, {len(df)} records found")
    return df
