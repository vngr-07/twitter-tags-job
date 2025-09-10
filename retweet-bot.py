from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time

# --- Load cookies from secrets ---
COOKIES_JSON = os.getenv("COOKIES_JSON")

HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # ✅ Use new headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1200, 800)
    return driver

def inject_cookies(driver):
    cookies = json.loads(COOKIES_JSON)
    driver.get("https://twitter.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

def search_and_retweet(driver):
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag} …")
        driver.get(f"https://twitter.com/search?q={tag}&src=typed_query&f=live")
        time.sleep(5)

        try:
            tweets = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-testid='tweet']"))
            )
            if not tweets:
                print(f"⚠️ No tweets found for {tag}")
                continue

            for tweet in tweets[:2]:  # ✅ Retweet at most 2 per run
                try:
                    retweet_button = tweet.find_element(By.XPATH, ".//div[@data-testid='retweet']")
                    retweet_button.click()
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='retweetConfirm']"))
                    ).click()
                    print(f"✅ Retweeted: {tag}")
                    time.sleep(3)
                except Exception as e:
                    print(f"⚠️ Skipping one tweet for {tag}: {e}")
        except:
            print(f"⚠️ Could not load tweets for {tag}")

def main():
    driver = create_driver()
    inject_cookies(driver)
    print("✅ Logged in via cookies")
    search_and_retweet(driver)
    driver.quit()

if __name__ == "__main__":
    main()
