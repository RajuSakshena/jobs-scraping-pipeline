from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

# ======================================================
# URLS
# ======================================================
BASE_URL = "https://www.developmentaid.org"
URL = "https://www.developmentaid.org/tenders/search?locations=147"

# ======================================================
# KEYWORDS
# ======================================================
KEYWORDS = {
    "Governance": [
        "governance", "policy", "capacity building", "municipal", "m&e", "fiscal",
        "monitoring and evaluation", "social audits", "fundraising", "management",
        "consulting", "consultant", "consultancy", "administration", "public",
        "government", "capacity", "impact", "evaluation", "dashboard", "data",
        "knowledge", "technology", "tool", "framework", "strategy",
        "csr", "philanthropy", "business", "entrepreneurship", "entrepreneurs",
        "shg"
    ],
    "Learning": [
        "education", "skill", "skills", "training", "life skills", "tvet",
        "student", "learning", "teaching", "development", "curriculum",
        "schools", "colleges", "educational", "ai", "skilling"
    ],
    "Safety": [
        "gender", "safety", "equity", "mobility", "transport", "sexual",
        "health", "public health", "security", "protection", "wellbeing",
        "wellness", "child", "children", "lgbtq", "queer", "women",
        "wash", "hygiene", "empowerment"
    ],
    "Climate": [
        "climate", "resilience", "environment", "disaster", "sustainability",
        "green", "ecology", "conservation", "renewable", "pollution",
        "energy", "waste", "flood", "heat", "green buildings"
    ]
}

NORMALIZED = {k: [w.lower() for w in v] for k, v in KEYWORDS.items()}

# ======================================================
# DRIVER
# ======================================================
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

# ======================================================
# CATEGORY DETECTION
# ======================================================
def detect_categories(text):
    text = text.lower()
    matched = []
    for cat, words in NORMALIZED.items():
        for w in words:
            if re.search(r"\b" + re.escape(w) + r"\b", text):
                matched.append(cat)
                break
    return ", ".join(matched)

# ======================================================
# SCRAPER (ROBUST PAGINATION)
# ======================================================
def scrape_jobs(max_pages=10):
    driver = get_driver()
    wait = WebDriverWait(driver, 30)
    driver.get(URL)

    all_rows = []
    seen_links = set()

    for page in range(1, max_pages + 1):
        print(f"⏳ Scraping page {page} ...")

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.search-card__title")
        ))

        time.sleep(2)

        cards = driver.find_elements(By.CSS_SELECTOR, "a.search-card__title")
        print(f"✅ Found {len(cards)} tenders on page {page}")

        for card in cards:
            title = card.get_attribute("title").strip()
            href = card.get_attribute("href")

            if href.startswith("http"):
                link = href
            else:
                link = BASE_URL + href

            if link in seen_links:
                continue
            seen_links.add(link)

            category = detect_categories(title)
            if not category:
                continue

            all_rows.append({
                "Source": "DevelopmentAid",
                "Title": title,
                "Category": category,
                "Description": "",
                "Apply_Link": link
            })

        # ---- CLICK NEXT PAGE BUTTON SAFELY ----
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f'//button[normalize-space()="{page + 1}"]')
                )
            )

            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            driver.execute_script("arguments[0].click();", next_btn)

            time.sleep(3)

        except:
            print("⚠️ Pagination ended at page", page)
            break

    driver.quit()
    return pd.DataFrame(all_rows)

# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    df = scrape_jobs(max_pages=10)
    print(df.head())
    print("Total tenders scraped:", len(df))
