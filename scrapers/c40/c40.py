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
# MATCHING LOGIC (1 keyword enough)
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
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        print("🔍 Opening C40 page...")

        # ✅ FIXED: NO networkidle
        page.goto(C40_RFP_URL, timeout=60000, wait_until="domcontentloaded")

        # ✅ wait for JS rendering
        page.wait_for_timeout(8000)

        # ======================================================
        # 🔥 RETRY + SCROLL (CRITICAL FOR GITHUB)
        # ======================================================
        cards = None

        for attempt in range(6):
            print(f"🔄 Attempt {attempt + 1}")

            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)

            cards = page.locator("a.link-cards-item")
            count = cards.count()

            print(f"👉 Found {count} cards")

            if count > 0:
                break

        # ❌ if still nothing
        if not cards or cards.count() == 0:
            print("❌ No cards found after retries")
            browser.close()
            return pd.DataFrame(columns=[
                "Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"
            ])

        print(f"✅ Final Found {cards.count()} RFPs")

        # ======================================================
        # EXTRACT DATA
        # ======================================================
        for i in range(cards.count()):
            try:
                card = cards.nth(i)

                title = card.locator("h3").inner_text(timeout=5000) if card.locator("h3").count() > 0 else "N/A"
                deadline = card.locator("h4").inner_text(timeout=5000) if card.locator("h4").count() > 0 else "N/A"
                link = card.get_attribute("href")

                # fix relative links
                if link and link.startswith("/"):
                    link = "https://www.c40.org" + link

                description = f"{title} {deadline}"

                matched_vertical = match_verticals(title, description)

                # ✅ skip if no keyword match
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
                print(f"⚠ Error: {e}")

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

    if not df.empty:
        file_path = "c40_output.xlsx"
        df.to_excel(file_path, index=False)
        print(f"📁 Saved to {file_path}")
