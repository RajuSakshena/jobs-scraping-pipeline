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
# FETCH HTML — curl_cffi Chrome impersonation
# ======================================================
def fetch_html(url):

    # ✅ METHOD 1: curl_cffi — Chrome TLS fingerprint mimic (best for Cloudflare)
    if CURL_CFFI_AVAILABLE:
        print("🔑 Using curl_cffi Chrome impersonation...")
        try:
            session = cf_requests.Session(impersonate="chrome120")

            # Hit homepage first to get cookies
            session.get("https://www.c40.org/", timeout=30)
            time.sleep(2)

            resp = session.get(url, timeout=30)

            if resp.status_code == 200 and "Just a moment" not in resp.text:
                print("✅ curl_cffi fetch successful!")
                return resp.text
            else:
                print(f"⚠ curl_cffi got status {resp.status_code} or Cloudflare page")
        except Exception as e:
            print(f"⚠ curl_cffi error: {e}")

    # ✅ METHOD 2: Plain requests fallback (works locally if cookies cached)
    print("🔄 Trying plain requests fallback...")
    try:
        import requests as req
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        session2 = req.Session()
        session2.get("https://www.c40.org/", headers=headers, timeout=30)
        time.sleep(2)
        resp2 = session2.get(url, headers=headers, timeout=30)
        if resp2.status_code == 200 and "Just a moment" not in resp2.text:
            print("✅ Plain requests fetch successful")
            return resp2.text
        else:
            print(f"⚠ Plain requests also blocked ({resp2.status_code})")
    except Exception as e:
        print(f"⚠ Plain requests error: {e}")

    return None


# ======================================================
# PARSE CARDS FROM HTML
# ======================================================
def parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    # Try selectors one by one
    cards = soup.find_all("a", class_=lambda c: c and "link-cards-item" in c)

    if not cards:
        cards = soup.find_all(
            "a", class_=lambda c: c and "card" in " ".join(c).lower() if c else False
        )

    if not cards:
        main = soup.find("main") or soup.find("body")
        if main:
            cards = [
                a for a in main.find_all("a", href=True)
                if len(a.get_text(strip=True)) > 20
            ]

    print(f"📦 Found {len(cards)} cards to parse")

    for card in cards:
        try:
            h3 = card.find("h3") or card.find("h2") or card.find("h4")
            title = h3.get_text(strip=True) if h3 else card.get_text(strip=True)[:120]
            if not title:
                continue

            all_h4 = card.find_all("h4")
            deadline = all_h4[0].get_text(strip=True) if all_h4 else "N/A"

            link = card.get("href") or ""
            if link.startswith("/"):
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
            print(f"✔️ {title[:80]} → {matched_vertical}")

        except Exception as e:
            print(f"⚠ Parse error: {e}")

    return data


# ======================================================
# MAIN SCRAPER
# ======================================================
def scrape_c40_jobs():
    print("🔍 Opening C40 page...")

    if not CURL_CFFI_AVAILABLE:
        print("⚠ curl_cffi not installed — install it: pip install curl_cffi")

    html = fetch_html(C40_RFP_URL)

    if not html:
        print("❌ Could not fetch C40 page")
        return pd.DataFrame(columns=["Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"])

    if "Just a moment" in html:
        print("❌ Cloudflare still blocking — curl_cffi may need update")
        return pd.DataFrame(columns=["Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"])

    data = parse_cards(html)

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
        df.to_excel("c40_output.xlsx", index=False)
        print("📁 Saved to c40_output.xlsx")
