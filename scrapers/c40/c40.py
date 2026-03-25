import os
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ======================================================
# CONFIG
# ======================================================
C40_RFP_URL = "https://www.c40.org/work-with-c40/"

# ✅ UPDATED KEYWORDS (Development + Govt included)
KEYWORDS = {
    "Governance": [
        "governance", "policy", "capacity building", "municipal", "m&e",
        "monitoring and evaluation", "social audits", "fundraising",
        "management", "consulting", "consultant", "consultancy",
        "administration", "public", "government", "capacity",
        "impact", "evaluation", "dashboard", "data",
        "strategy", "framework", "tool", "technology",
        "knowledge", "csr", "philanthropy", "business",
        "entrepreneurship", "entrepreneurs", "shg",

        # ✅ DEVELOPMENT + GOVT RELATED
        "development", "urban", "infrastructure", "city",
        "housing", "parks", "planning", "guidelines",
        "implementation", "technical assistance",
        "project", "program", "scheme"
    ],

    "Learning": [
        "education", "skill", "skills", "training", "life skills",
        "tvet", "student", "learning by doing",
        "teaching", "curriculum", "schools", "colleges",
        "educational institutes", "ai", "skilling",
        "digital learning", "edtech"
    ],

    "Safety": [
        "gender", "women", "equity", "safety", "mobility",
        "sexual", "health", "security", "protection",
        "child", "children", "lgbtq", "wellbeing", "wash"
    ],

    "Climate": [
        "climate", "resilience", "environment", "disaster",
        "sustainability", "green", "renewable", "energy",
        "pollution", "waste", "sanitation", "flood", "heat"
    ]
}

# ======================================================
# 🔥 MATCHING LOGIC (ONLY 1 KEYWORD NEEDED)
# ======================================================
def match_verticals(title, description):
    text = f"{title} {description}".lower()
    matched = []

    for vertical, words in KEYWORDS.items():
        for w in set(words):
            if re.search(rf"\b{re.escape(w.lower())}\b", text):
                matched.append(vertical)
                break  # ✅ 1 match enough → break

    return ", ".join(matched) if matched else "N/A"


# ======================================================
# MAIN SCRAPER
# ======================================================
def scrape_c40_jobs():
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # ✅ browser UI band rahega
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

        print("🔍 Opening C40 page...")
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

                description = f"{title} {deadline}"

                matched_vertical = match_verticals(title, description)

                # ✅ Only include if at least 1 keyword matched
                if matched_vertical == "N/A":
                    continue

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
    # DATAFRAME
    # ======================================================
    if not data:
        print("❌ No relevant data found")
        return pd.DataFrame(columns=[
            "Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"
        ])

    df = pd.DataFrame(data)

    print(f"✅ Final records: {len(df)}")
    return df


# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    df = scrape_c40_jobs()

    # ✅ save output
    if not df.empty:
        file_path = "c40_output.xlsx"
        df.to_excel(file_path, index=False)
        print(f"📁 Saved to {file_path}")
