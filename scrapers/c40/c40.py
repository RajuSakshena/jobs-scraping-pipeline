import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright

C40_RFP_URL = "https://www.c40.org/work-with-c40/"

KEYWORDS = {
    "Governance": [
        "governance","policy","capacity","government","development",
        "urban","infrastructure","city","planning","implementation",
        "project","program","scheme","technical assistance"
    ],
    "Learning": ["education","training","skills","learning"],
    "Safety": ["gender","women","safety","health","security"],
    "Climate": ["climate","environment","sustainability","energy"]
}

def match_verticals(title, description):
    text = f"{title} {description}".lower()
    matched = []

    for vertical, words in KEYWORDS.items():
        for w in words:
            if re.search(rf"\b{re.escape(w)}\b", text):
                matched.append(vertical)
                break

    return ", ".join(matched) if matched else "N/A"


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
            user_agent="Mozilla/5.0",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        print("🔍 Opening C40 page...")
        page.goto(C40_RFP_URL, timeout=60000, wait_until="networkidle")

        # ✅ HARD WAIT (GitHub ke liye important)
        page.wait_for_timeout(5000)

        # ======================================================
        # 🔥 RETRY LOOP (KEY FIX)
        # ======================================================
        cards = None
        for attempt in range(5):
            print(f"🔄 Attempt {attempt+1} to load cards...")

            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(3000)

            cards = page.locator("a.link-cards-item")
            count = cards.count()

            print(f"👉 Found {count} cards")

            if count > 0:
                break

        if not cards or cards.count() == 0:
            print("❌ No cards found after retries")
            browser.close()
            return pd.DataFrame(columns=[
                "Title","Description","Matched_Vertical","Deadline","Apply_Link"
            ])

        print(f"✅ Final Found {cards.count()} RFPs")

        # ======================================================
        # EXTRACT DATA
        # ======================================================
        for i in range(cards.count()):
            try:
                card = cards.nth(i)

                title = card.locator("h3").inner_text(timeout=5000)
                deadline = card.locator("h4").inner_text(timeout=5000)
                link = card.get_attribute("href")

                if link and link.startswith("/"):
                    link = "https://www.c40.org" + link

                description = f"{title} {deadline}"
                matched_vertical = match_verticals(title, description)

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

    if not data:
        print("❌ No relevant data found")
        return pd.DataFrame(columns=[
            "Title","Description","Matched_Vertical","Deadline","Apply_Link"
        ])

    df = pd.DataFrame(data)
    print(f"✅ Final records: {len(df)}")

    return df


if __name__ == "__main__":
    df = scrape_c40_jobs()

    if not df.empty:
        df.to_excel("c40_output.xlsx", index=False)
        print("📁 Saved to c40_output.xlsx")
