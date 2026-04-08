import time
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


URLS = {
    "Grants": "https://onepurpos.in/openings/grants",
    "RFPs": "https://onepurpos.in/openings/rfps"
}


KEYWORDS = {
    "Governance": ["governance", "policy", "capacity", "government", "data"],
    "Learning": ["education", "training", "skill", "learning"],
    "Safety": ["safety", "gender", "health", "protection"],
    "Climate": ["climate", "environment", "sustainability", "energy"]
}


def get_matched_vertical(text):
    text = text.lower()
    for vertical, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return vertical
    return None


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# 🔥 NO TAB VERSION (FAST)
def get_description(driver, link):
    try:
        driver.get(link)
        time.sleep(2)

        return driver.find_element(
            By.CSS_SELECTOR,
            "div.details-card-body div.editor-content-main"
        ).text.strip()

    except:
        return ""


def scrape_onepurpose_jobs():
    driver = init_driver()
    all_rows = []

    try:
        for _, url in URLS.items():
            driver.get(url)
            time.sleep(4)

            # scroll
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            cards = driver.find_elements(By.CSS_SELECTOR, "a.card-link")

            for card in cards[:20]:  # 🔥 LIMIT (IMPORTANT for speed)
                try:
                    link = card.get_attribute("href")
                    title = card.find_element(By.CSS_SELECTOR, "p.large-card-title").text
                    deadline = card.find_element(By.CSS_SELECTOR, "p.large-card-date-text").text

                    description = get_description(driver, link)

                    combined = f"{title} {description}"
                    vertical = get_matched_vertical(combined)

                    if vertical:
                        all_rows.append({
                            "Title": title,
                            "Description": description,
                            "Matched_Vertical": vertical,
                            "Deadline": deadline,
                            "Apply_Link": link
                        })

                    driver.back()
                    time.sleep(1)

                except:
                    continue

    finally:
        driver.quit()

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)

    df['Deadline_Date'] = pd.to_datetime(df['Deadline'], errors='coerce')
    today = pd.Timestamp(datetime.today().date())
    df = df[df['Deadline_Date'] >= today]

    df = df.sort_values("Deadline_Date")

    return df[["Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"]]
