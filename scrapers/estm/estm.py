from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time

# ======================================================
# PATH SETUP
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "estm_jobs.xlsx")

URL = (
    "https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs"
    "?location=India&locationId=300000000440677&locationLevel=country&mode=location"
)


def safe_text(parent, by, value):
    try:
        return parent.find_element(by, value).text.strip()
    except:
        return ""


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def scrape_jobs():
    driver = get_driver()
    wait = WebDriverWait(driver, 30)

    driver.get(URL)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.job-grid-item__content")
        )
    )

    time.sleep(3)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.job-grid-item__content")
    print(f"✅ Found {len(cards)} ESTM jobs")

    jobs = []

    for card in cards:
        title = safe_text(card, By.CSS_SELECTOR, "span.job-tile__title")
        location = safe_text(card, By.CSS_SELECTOR, "span[data-bind*='primaryLocation']")
        posting_date = safe_text(
            card,
            By.XPATH,
            ".//div[contains(text(),'Posting Date')]/following::div[1]"
        )

        try:
            apply_link = card.find_element(
                By.XPATH,
                "ancestor::div[contains(@class,'job-grid-item__link')]/preceding-sibling::a"
            ).get_attribute("href")
        except:
            apply_link = ""

        if title or apply_link:
            jobs.append({
                "Source": "ESTM",
                "Title": title,
                "Location": location,
                "Posting_Date": posting_date,
                "Apply_Link": apply_link
            })

    driver.quit()
    return pd.DataFrame(jobs)


def save_to_excel(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if df.empty:
        df = pd.DataFrame(columns=[
            "Source", "Title", "Location", "Posting_Date", "Apply_Link"
        ])

    df["Apply_Link"] = df["Apply_Link"].apply(
        lambda x: f'=HYPERLINK("{x}", "Apply")' if x else ""
    )

    df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
    print(f"✅ ESTM Excel created: {OUTPUT_FILE}")


def main():
    df = scrape_jobs()
    save_to_excel(df)


if __name__ == "__main__":
    main()
