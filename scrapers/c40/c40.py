import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync  # Added Stealth

# ======================================================
# CONFIG
# ======================================================
C40_RFP_URL = "https://www.c40.org/work-with-c40/"

# ======================================================
# KEYWORDS (Same as yours)
# ======================================================
KEYWORDS = {
    "Governance": ["governance", "policy", "capacity building", "municipal", "m&e", "monitoring and evaluation", "social audits", "fundraising", "management", "consulting", "consultancy", "administration", "public", "government", "capacity", "impact", "evaluation", "dashboard", "data", "strategy", "framework", "tool", "technology", "knowledge", "csr", "philanthropy", "business", "entrepreneurship", "entrepreneurs", "shg", "development", "urban", "infrastructure", "city", "housing", "parks", "planning", "guidelines", "implementation", "technical assistance", "project", "program", "scheme"],
    "Learning": ["education", "skill", "skills", "training", "life skills", "tvet", "student", "learning by doing", "teaching", "curriculum", "schools", "colleges", "educational institutes", "ai", "skilling", "digital learning", "edtech"],
    "Safety": ["gender", "women", "equity", "safety", "mobility", "sexual", "health", "security", "protection", "child", "children", "lgbtq", "wellbeing", "wash"],
    "Climate": ["climate", "resilience", "environment", "disaster", "sustainability", "green", "renewable", "energy", "pollution", "waste", "sanitation", "flood", "heat"]
}

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
# MAIN SCRAPER WITH STEALTH & CAPTCHA HANDLING
# ======================================================
def scrape_c40_jobs():
    data = []

    with sync_playwright() as p:
        # Important: Launching with specific args to bypass detection
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        # Setting a realistic User Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()
        
        # 🔥 APPLY STEALTH
        stealth_sync(page)

        print("🔍 Opening C40 page with Stealth...")
        try:
            # Increase timeout for slow GitHub runners
            page.goto(C40_RFP_URL, timeout=90000, wait_until="networkidle")
            
            # --- CLOUDFLARE TURNSTILE HANDLING ---
            # Agar captcha box aata hai, toh 5-10 second wait karo, 
            # Stealth mode mein Turnstile aksar khud pass ho jata hai.
            time.sleep(10) 
            
            # Check if we are stuck on verification
            if "Perform security verification" in page.content():
                print("⚠ Stuck on Cloudflare. Trying to wait longer...")
                time.sleep(15)

            # --- DATA EXTRACTION ---
            # Wait for the card element
            page.wait_for_selector("a.link-cards-item", timeout=30000)
            
            # Scroll to trigger any lazy loading
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                time.sleep(1)

            cards = page.locator("a.link-cards-item")
            count = cards.count()
            print(f"✅ Found {count} RFPs")

            for i in range(count):
                card = cards.nth(i)
                title = card.locator("h3").inner_text() if card.locator("h3").count() > 0 else "N/A"
                deadline = card.locator("h4").inner_text() if card.locator("h4").count() > 0 else "N/A"
                link = card.get_attribute("href")

                if link and link.startswith("/"):
                    link = "https://www.c40.org" + link

                description = f"{title} {deadline}"
                matched_vertical = match_verticals(title, description)

                if matched_vertical != "N/A":
                    data.append({
                        "Title": title,
                        "Description": description,
                        "Matched_Vertical": matched_vertical,
                        "Deadline": deadline,
                        "Apply_Link": link
                    })
                    print(f"✔️ Matched: {title}")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            # Screenshot save karein debug ke liye (GitHub Artifacts mein dekh sakte ho)
            page.screenshot(path="debug_screenshot.png")
        
        browser.close()

    df = pd.DataFrame(data)
    if df.empty:
        print("❌ No relevant data found or blocked by Cloudflare")
    else:
        print(f"✅ Final records: {len(df)}")
    return df

if __name__ == "__main__":
    df = scrape_c40_jobs()
    if not df.empty:
        df.to_excel("c40_output.xlsx", index=False)
