import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright

# ======================================================
# CONFIG
# ======================================================
C40_RFP_URL = "https://www.c40.org/work-with-c40/"

# ======================================================
# KEYWORDS
# ======================================================
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
# MATCHING LOGIC
# ======================================================
def match_verticals(title, description):
    text = f"{title} {description}".lower()
    matched = []

    for vertical, words in KEYWORDS.items():
        for w in set(words):
            if re.search(rf"\b{re.escape(w.lower())}\b", text):
                matched.append(vertical)
                break

    return ", ".join(matched) if matched else "N/A"


# ======================================================
# MAIN SCRAPER
# ======================================================
def scrape_c40_jobs():
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        print("🔍 Opening C40 page...")
        page.goto(C40_RFP_URL, timeout=60000, wait_until="networkidle")

        # ✅ Extra wait for JS render
        time.sleep(5)

        # ✅ Scroll to load all cards (important for GitHub Actions)
        for i in range(8):
            page.mouse.wheel(0, 6000)
            time.sleep(2)

        # ✅ Ensure elements are loaded
        try:
            page.wait_for_selector("a.link-cards-item", timeout=20000)
        except:
            print("⚠ Selector not found — retrying after delay...")
            time.sleep(5)

        # ======================================================
        # 🔥 MAIN EXTRACTION
        # ======================================================
        cards = page.locator("a.link-cards-item")
        count = cards.count()

        print(f"📦 Total cards found: {count}")

        for i in range(count):
            try:
                card = cards.nth(i)

                # ✅ Title
                title = (
                    card.locator("h3").inner_text().strip()
                    if card.locator("h3").count() > 0
                    else "N/A"
                )

                # ✅ Deadline
                deadline = (
                    card.locator("h4").inner_text().strip()
                    if card.locator("h4").count() > 0
                    else "N/A"
                )

                # ✅ Link
                link = card.get_attribute("href")

                if link and link.startswith("/"):
                    link = "https://www.c40.org" + link

                description = f"{title} {deadline}"

                # ✅ Keyword match
                matched_vertical = match_verticals(title, description)

                if matched_vertical == "N/A":
                    continue

                data.append({
                    "Title": title,
                    "Description": description,
                    "Matched_Vertical": matched_vertical,
                    "Deadline": deadline,
                    "Apply_Link": link,
                    "Source": "C40"
                })

                print(f"✔️ {title} → {matched_vertical}")

            except Exception as e:
                print(f"⚠ Error in card {i}: {e}")

        browser.close()

    # ======================================================
    # REMOVE DUPLICATES
    # ======================================================
    unique_data = {item["Apply_Link"]: item for item in data if item["Apply_Link"]}
    final_data = list(unique_data.values())

    # ======================================================
    # DATAFRAME
    # ======================================================
    if not final_data:
        print("❌ No relevant data found")
        return pd.DataFrame(columns=[
            "Title", "Description", "Matched_Vertical",
            "Deadline", "Apply_Link", "Source"
        ])

    df = pd.DataFrame(final_data)

    print(f"✅ Final records after filtering: {len(df)}")
    return df


# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    df = scrape_c40_jobs()

    if not df.empty:
        file_path = "c40_output.xlsx"
        df.to_excel(file_path, index=False)
        print(f"📁 Saved to {file_path}")
