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
# SELECTOR ATTEMPTS — tries multiple known selectors
# ======================================================
SELECTORS_TO_TRY = [
    "a.link-cards-item",
    "a[class*='link-cards']",
    "a[class*='card']",
    ".rfp-item a",
    "article a",
    "a[href*='work-with-c40']",
    "[class*='cards'] a",
    "[class*='listing'] a",
    "[class*='rfp'] a",
    "main a[href]",
]


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
                "--disable-gpu",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            ignore_https_errors=True,
            # Mimic real browser headers
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

        page = context.new_page()

        # ✅ Mask webdriver property to avoid bot detection
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        """)

        print("🔍 Opening C40 page...")

        try:
            page.goto(C40_RFP_URL, timeout=60000, wait_until="networkidle")
        except Exception as e:
            print(f"⚠ networkidle timed out, trying domcontentloaded... ({e})")
            try:
                page.goto(C40_RFP_URL, timeout=60000, wait_until="domcontentloaded")
            except Exception as e2:
                print(f"❌ Page load failed: {e2}")
                browser.close()
                return pd.DataFrame(columns=["Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"])

        # ✅ Multi-stage scroll to trigger lazy loading
        print("📜 Scrolling to trigger lazy loading...")
        for _ in range(8):
            page.mouse.wheel(0, 3000)
            time.sleep(1.5)

        # Scroll back up then down (mimics real user)
        page.mouse.wheel(0, -10000)
        time.sleep(1)
        for _ in range(8):
            page.mouse.wheel(0, 3000)
            time.sleep(1)

        time.sleep(3)

        # ======================================================
        # 🔥 DEBUG: Print page HTML snippet to see what loaded
        # ======================================================
        html_snippet = page.content()[:3000]
        print("🔎 Page HTML snippet (first 3000 chars):")
        print(html_snippet)
        print("--- END SNIPPET ---")

        # ======================================================
        # 🔥 TRY MULTIPLE SELECTORS
        # ======================================================
        cards = None
        matched_selector = None

        for selector in SELECTORS_TO_TRY:
            try:
                count = page.locator(selector).count()
                print(f"   Selector '{selector}' → {count} elements")
                if count > 0:
                    cards = page.locator(selector)
                    matched_selector = selector
                    break
            except Exception as e:
                print(f"   ⚠ Selector '{selector}' error: {e}")

        if cards is None or cards.count() == 0:
            print("❌ No cards found with any selector")
            # ✅ Dump all <a> tags as last resort debug
            all_links = page.locator("a[href]").all()
            print(f"🔗 Total <a> tags found on page: {len(all_links)}")
            for a in all_links[:20]:
                try:
                    href = a.get_attribute("href")
                    txt = a.inner_text().strip()[:80]
                    print(f"   → {txt} | {href}")
                except:
                    pass

            browser.close()
            return pd.DataFrame(columns=["Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"])

        count = cards.count()
        print(f"✅ Found {count} cards using selector: '{matched_selector}'")

        # ======================================================
        # EXTRACT DATA FROM CARDS
        # ======================================================
        for i in range(count):
            try:
                card = cards.nth(i)

                # Try h3 for title, fallback to full text
                if card.locator("h3").count() > 0:
                    title = card.locator("h3").inner_text().strip()
                elif card.locator("h2").count() > 0:
                    title = card.locator("h2").inner_text().strip()
                else:
                    title = card.inner_text().strip()[:120]

                if not title or title == "N/A":
                    continue

                # Try h4 for deadline
                deadline = card.locator("h4").inner_text().strip() if card.locator("h4").count() > 0 else "N/A"

                # Get link
                link = card.get_attribute("href") or ""
                if link.startswith("/"):
                    link = "https://www.c40.org" + link

                description = f"{title} {deadline}"
                matched_vertical = match_verticals(title, description)

                if matched_vertical == "N/A":
                    print(f"   ⏭ Skipped (no vertical match): {title[:60]}")
                    continue

                data.append({
                    "Title": title,
                    "Description": description,
                    "Matched_Vertical": matched_vertical,
                    "Deadline": deadline,
                    "Apply_Link": link
                })

                print(f"✔️ {title[:80]} → {matched_vertical}")

            except Exception as e:
                print(f"⚠ Error on card {i}: {e}")

        browser.close()

    # ======================================================
    # DATAFRAME
    # ======================================================
    if not data:
        print("❌ No relevant data found after matching")
        return pd.DataFrame(columns=["Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"])

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
