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


# 🔹 Keywords
KEYWORDS = {
    "Governance": [
        "governance", "policy", "capacity building", "municipal", "M&E", "fiscal",
        "monitoring and evaluation", "social audits", "fundraising", "management",
        "consulting", "administration", "public", "government", "capacity",
        "impact", "evaluation", "dashboard", "data"
    ],
    "Learning": [
        "education", "skill", "training", "life skills", "TVET", "student",
        "learning by doing", "contextualized learning", "teaching", "development",
        "curriculum", "schools", "colleges", "educational institutes", "AI",
        "skilling"
    ],
    "Safety": [
        "gender", "safety", "equity", "mobility", "transport", "sexual", "health",
        "responsive", "institutional safety", "SAFER", "security", "protection",
        "wellbeing", "wellness", "happiness", "access", "accessibility", "child",
        "children", "LGBTQ", "queer", "sexuality education", "personal",
        "empowerment", "design"
    ],
    "Climate": [
        "climate", "resilience", "environment", "disaster", "sustainability", "green",
        "climate adaptation", "ecology", "conservation",
        "renewable", "pollution", "energy", "climate mitigation",
        "disaster management", "flood", "heat"
    ]
}


def get_matched_vertical(text):
    text = text.lower()
    for vertical, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return vertical
    return None


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def get_description(driver, link):
    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

        driver.get(link)
        time.sleep(3)

        desc = driver.find_element(
            By.CSS_SELECTOR,
            "div.details-card-body div.editor-content-main"
        ).text.strip()

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return desc

    except:
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return ""


def scrape_onepurpose_jobs():
    driver = init_driver()
    all_rows = []

    try:
        for source_type, url in URLS.items():
            driver.get(url)
            time.sleep(5)

            # scroll
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            cards = driver.find_elements(By.CSS_SELECTOR, "a.card-link")

            for card in cards:
                try:
                    link = card.get_attribute("href")
                    title = card.find_element(By.CSS_SELECTOR, "p.large-card-title").text
                    deadline = card.find_element(By.CSS_SELECTOR, "p.large-card-date-text").text

                    description = get_description(driver, link)

                    combined_text = f"{title} {description}"
                    matched_vertical = get_matched_vertical(combined_text)

                    if matched_vertical:
                        all_rows.append({
                            "Title": title,
                            "Description": description,
                            "Matched_Vertical": matched_vertical,
                            "Deadline": deadline,
                            "Apply_Link": link
                        })

                except:
                    continue

    finally:
        driver.quit()

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)

    # 🔹 Deadline filter
    df['Deadline_Date'] = pd.to_datetime(df['Deadline'], errors='coerce')
    today = pd.Timestamp(datetime.today().date())
    df = df[df['Deadline_Date'] >= today]

    df = df.sort_values("Deadline_Date")

    df = df[["Title", "Description", "Matched_Vertical", "Deadline", "Apply_Link"]]

    print(f"✅ OnePurpose rows: {len(df)}")

    return df