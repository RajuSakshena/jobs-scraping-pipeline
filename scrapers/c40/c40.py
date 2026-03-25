import re
import time
import pandas as pd
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as cf_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    import requests

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
# FETCH HTML — curl_cffi
# ======================================================
def fetch_html(url):

    if CURL_CFFI_AVAILABLE:
        print("🔑 Using curl_cffi (Cloudflare bypass)...")
        try:
            session = cf_requests.Session(impersonate="chrome124")

            # Get cookies first
            session.get("https://www.c40.org/", timeout=30)
            time.sleep(2)

            # Retry logic
            for attempt in range(3):
                try:
                    resp = session.get(url, timeout=30)

                    if resp.status_code == 200 and "Just a moment" not in resp.text:
                        print(f"✅ Success on attempt {attempt+1}")
                        return resp.text
                    else:
                        print(f"⚠ Attempt {attempt+1} blocked")

                except Exception as e:
                    print(f"⚠ Attempt {attempt+1} error: {e}")

                time.sleep(3)

        except Exception as e:
            print(f"⚠ curl_cffi error: {e}")

    # Fallback
    print("🔄 Trying fallback requests...")
    try:
        import requests as req
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        resp = req.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"⚠ fallback error: {e}")

    return None


# ======================================================
# PARSE
# ======================================================
def parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    data = []
    seen_links = set()

    cards = soup.find_all("a", class_=lambda c: c and "link-cards-item" in c)

    if not cards:
        cards = soup.find_all("a")

    print(f"📦 Found {len(cards)} elements")

    for card in cards:
        try:
            title_tag = card.find(["h2", "h3", "h4"])
            title = title_tag.get_text(strip=True) if title_tag else None

            if not title or len(title) < 10:
                continue

            link = card.get("href", "")
            if not link:
                continue

            if link.startswith("/"):
                link = "https://www.c40.org" + link

            if link in seen_links:
                continue
            seen_links.add(link)

            # Better description
            desc_text = card.get_text(" ", strip=True)
            description = desc_text[:300]

            # Deadline extract
            deadline = "N/A"
            h4s = card.find_all("h4")
            if h4s:
                deadline = h4s[0].get_text(strip=True)

            matched_vertical = match_verticals(title, description)

            data.append({
                "Title": title,
                "Description": description,
                "Matched_Vertical": matched_vertical,
                "Deadline": deadline,
                "Apply_Link": link
            })

            print(f"✔ {title[:60]} → {matched_vertical}")

        except Exception as e:
            print(f"⚠ Parse error: {e}")

    return data


# ======================================================
# MAIN
# ======================================================
def scrape_c40_jobs():
    print("🔍 Scraping C40...")

    html = fetch_html(C40_RFP_URL)

    if not html:
        print("❌ Failed to fetch page")
        return pd.DataFrame()

    if "Just a moment" in html:
        print("❌ Still blocked by Cloudflare")
        return pd.DataFrame()

    data = parse_cards(html)

    if not data:
        print("❌ No data found")
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
