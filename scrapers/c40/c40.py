import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright
# FIX: Import changed to just 'stealth'
from playwright_stealth import stealth_async, stealth_sync 

# ... (KEYWORDS aur match_verticals logic same rahega) ...

def scrape_c40_jobs():
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()
        
        # 🔥 FIX: Correct way to call stealth
        stealth_sync(page) 

        print("🔍 Opening C40 page with Stealth...")
        try:
            page.goto(C40_RFP_URL, timeout=90000, wait_until="networkidle")
            
            # Wait for Cloudflare to settle
            time.sleep(10) 
            
            # Check for verification page
            if "Perform security verification" in page.content():
                print("⚠ Stuck on Cloudflare. Trying to wait longer...")
                time.sleep(15)

            # Wait for content
            page.wait_for_selector("a.link-cards-item", timeout=30000)
            
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

        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="debug_screenshot.png")
        
        browser.close()

    return pd.DataFrame(data)
