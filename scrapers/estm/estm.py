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

URL = (
    "https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs"
    "?location=India&locationId=300000000440677&locationLevel=country&mode=location"
)

# ======================================================
# DRIVER
# ======================================================
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# ======================================================
# SCRAPER
# ======================================================
def scrape_jobs():
    driver = get_driver()
    wait = WebDriverWait(driver, 30)

    driver.get(URL)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.job-grid-item")
        )
    )

    time.sleep(3)

    job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-grid-item")
    print(f"✅ Found {len(job_cards)} jobs")

    jobs = []

    for card in job_cards:
        try:
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            continue

        try:
            title = card.find_element(By.CSS_SELECTOR, "span.job-tile__title").text.strip()
        except:
            title = ""

        try:
            location = card.find_element(
                By.CSS_SELECTOR,
                "span[data-bind*='primaryLocation']"
            ).text.strip()
        except:
            location = ""

        # ================= OPEN DETAIL PAGE =================
        driver.execute_script("window.open(arguments[0]);", link)
        driver.switch_to.window(driver.window_handles[1])

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.job-details__info-section")
            )
        )

        time.sleep(2)

        # ================= EXTRACT DEADLINE =================
        try:
            deadline = driver.find_element(
                By.XPATH,
                "//span[text()='Apply Before']/following-sibling::span"
            ).text.strip()
        except:
            deadline = ""

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        jobs.append({
            "Source": "ESTM",
            "Title": title,
            "Location": location,
            "Deadline": deadline,
            "Apply_Link": link
        })

    driver.quit()
    return pd.DataFrame(jobs)

# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    df = scrape_jobs()
    print(df)
