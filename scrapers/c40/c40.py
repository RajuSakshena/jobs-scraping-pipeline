import pandas as pd
import time
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ======================================================
# CONFIG
# ======================================================
C40_RFP_URL = "https://www.c40.org/work-with-c40/"

# ======================================================
# KEYWORDS
# ======================================================
KEYWORDS = {
    "Governance": ["governance", "policy", "consultant", "project", "data"],
    "Learning": ["education", "training", "skill", "learning"],
    "Safety": ["gender", "women", "safety", "health"],
    "Climate": ["climate", "environment", "energy", "sustainability"]
}

# ======================================================
# MATCHING
# ======================================================
def match_verticals(text):
    text = text.lower()
    matched = []

    for vertical, words in KEYWORDS.items():
        for w in words:
            if w in text:
                matched.append(vertical)
                break

    return ", ".join(matched) if matched else "N/A"

# ======================================================
# FETCH USING PLAYWRIGHT
# ======================================================
def fetch_html():

    print("🌐 Launching browser (Playwright)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # GitHub compatible
        page = browser.new_page()

        page.goto(C40_RFP_URL, timeout=60000)

        # wait for content load
        page.wait_for_timeout(8000)

        html = page.content()

        browser.close()

        return html

# ======================================================
# PARSE
# ======================================================
def parse_cards(html):

    soup = BeautifulSoup(html, "html.parser")
    data = []
    seen = set()

    cards = soup.find_all("a")

    print(f"📦 Total elements found: {len(cards)}")

    for card in cards:
        try:
            title_tag = card.find(["h2", "h3", "h4"])
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            if len(title) < 10:
                continue

            link = card.get("href", "")
            if not link:
                continue

            if link.startswith("/"):
                link = "https://www.c40.org" + link

            if link in seen:
                continue
            seen.add(link)

            description = card.get_text(" ", strip=True)[:300]

            # deadline
            deadline = "N/A"
            h4s = card.find_all("h4")
            if h4s:
                deadline = h4s[0].get_text(strip=True)

            matched_vertical = match_verticals(description)

            data.append({
                "Title": title,
                "Description": description,
                "Matched_Vertical": matched_vertical,
                "Deadline": deadline,
                "Apply_Link": link
            })

            print(f"✔ {title[:60]} → {matched_vertical}")

        except Exception as e:
            print(f"⚠ Error: {e}")

    return data

# ======================================================
# MAIN
# ======================================================
def scrape_c40_jobs():

    print("🔍 Scraping C40 using browser...")

    html = fetch_html()

    if not html:
        print("❌ Failed to load page")
        return pd.DataFrame()

    data = parse_cards(html)

    if not data:
        print("❌ No data extracted")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    print(f"✅ Total records: {len(df)}")

    return df

# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":

    df = scrape_c40_jobs()

    if not df.empty:
        import os
        os.makedirs("output", exist_ok=True)

        df.to_excel("output/c40_output.xlsx", index=False)
        print("📁 Saved: output/c40_output.xlsx")
