import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re

BASE_URL = "https://www.developmentaid.org"
URL = "https://www.developmentaid.org/tenders/search?locations=147"

KEYWORDS = {
    "Governance": ["governance","policy","municipal","consulting","consultant","management","public","government","strategy","data"],
    "Learning": ["education","skill","skills","training","learning","schools","ai"],
    "Safety": ["gender","safety","health","security","women","child","hygiene"],
    "Climate": ["climate","environment","energy","green","waste","resilience"]
}

NORMALIZED = {k: [w.lower() for w in v] for k, v in KEYWORDS.items()}


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def detect_categories(text):
    text = text.lower()
    matched = set()
    for cat, words in NORMALIZED.items():
        for w in words:
            if re.search(r"\b" + re.escape(w) + r"\b", text):
                matched.add(cat)
                break
    return ", ".join(matched)


def scrape_jobs():
    driver = get_driver()
    wait = WebDriverWait(driver, 30)
    rows = []
    seen_links = set()

    try:
        driver.get(URL)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "da-tender-content-card")))
        time.sleep(3)

        cards = driver.find_elements(By.CSS_SELECTOR, "da-tender-content-card")
        print(f"Total cards found: {len(cards)}")

        for card in cards:
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "a.search-card__title")
                title = title_elem.get_attribute("title").strip()

                # 🔎 Detect vertical
                matched_vertical = detect_categories(title)

                # ❗ Skip if no match
                if not matched_vertical:
                    continue

                href = title_elem.get_attribute("href")
                link = href if href.startswith("http") else BASE_URL + href

                if link in seen_links:
                    continue
                seen_links.add(link)

                # Deadline extraction
                try:
                    deadline_elem = card.find_element(
                        By.CSS_SELECTOR,
                        "div.tender-deadline span:nth-of-type(2)"
                    )
                    deadline = deadline_elem.text.strip()
                except:
                    deadline = ""

                rows.append({
                    "Source": "DevelopmentAid",
                    "Title": title,
                    "Description": "",
                    "Category": matched_vertical,
                    "Deadline": deadline,
                    "Apply_Link": link
                })

            except Exception:
                continue

    except TimeoutException:
        print("Page load timeout")

    driver.quit()
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = scrape_jobs()
    print(df.head())
    print("Total matched tenders:", len(df))
