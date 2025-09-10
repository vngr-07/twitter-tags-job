import os
import time
import random
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")
HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def login(driver):
    driver.get("https://x.com/")
    time.sleep(4)

    try:
        # Click the "Entrar" button on the homepage
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="loginButton"]'))
        )
        login_button.click()
        print("🔑 Clicked login button")
        time.sleep(3)
    except TimeoutException:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/login_button_failed.png")
        raise RuntimeError("❌ Couldn't find the login button")

    try:
        # Fill username or email
        username_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.send_keys(USERNAME)
        print("👤 Entered username")
        time.sleep(1)

        # Click "Avançar"
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//span[contains(text(),"Avançar")]/ancestor::div[@role="button"]'
            ))
        )
        next_button.click()
        print("➡️ Clicked 'Avançar'")
        time.sleep(3)
    except TimeoutException:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/username_input_failed.png")
        raise RuntimeError("❌ Couldn't enter username or click Avançar")

    try:
        # Fill password
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(PASSWORD)
        print("🔒 Entered password")
        time.sleep(1)

        # Click final "Entrar" button
        final_login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="LoginForm_Login_Button"]'))
        )
        final_login_button.click()
        print("✅ Logged in successfully")
        time.sleep(6)
    except TimeoutException:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/password_input_failed.png")
        raise RuntimeError("❌ Couldn't enter password or click final login")

    if "login" in driver.current_url or "signin" in driver.current_url:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/login_failed.png")
        raise RuntimeError("❌ Login failed. Check username/password")

def search_and_retweet(driver):
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag} …")
        driver.get(f"https://x.com/search?q={tag}&f=live")
        time.sleep(3)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]'))
            )
        except TimeoutException:
            driver.save_screenshot(f"{SCREENSHOT_DIR}/{re.sub('[^a-zA-Z0-9]', '_', tag)}_notweets.png")
            print(f"⚠️ No tweets found for {tag}")
            continue

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"✅ Found {len(tweets)} tweets for {tag}")

        to_retweet = random.sample(tweets, min(len(tweets), 3))
        for idx, tweet in enumerate(to_retweet, 1):
            try:
                rt_btn = tweet.find_element(By.XPATH, './/*[@data-testid="retweet"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", rt_btn)
                time.sleep(1)
                rt_btn.click()

                confirm = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="retweetConfirm"]'))
                )
                confirm.click()

                print(f"🔁 Retweeted {idx}/{len(to_retweet)} for {tag}")
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                print(f"⚠️ Failed to retweet tweet {idx}: {e}")

def main():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    driver.set_window_size(1400, 900)

    try:
        login(driver)
        search_and_retweet(driver)
    finally:
        driver.quit()
        print("🏁 Bot finished successfully")

if __name__ == "__main__":
    main()
