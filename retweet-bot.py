import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ==========================
# Configurações
# ==========================
USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")
HASHTAGS = ["#Python", "#Selenium"]  # personalize as hashtags
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def save_html(driver, name):
    """Salva HTML da página para debug."""
    with open(f"{SCREENSHOT_DIR}/{name}", "w", encoding="utf-8") as f:
        f.write(driver.page_source)


def login(driver):
    """Realiza login no X/Twitter."""
    driver.get("https://x.com/")
    time.sleep(4)

    # 1. Clica no botão inicial de login (se existir)
    try:
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="loginButton"]'))
        )
        login_button.click()
        print("🔑 Clicked login button")
        time.sleep(2)
    except TimeoutException:
        print("⚠️ Login button not found, maybe already on login page")

    # 2. Preenche username
    try:
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.clear()
        username_input.send_keys(USERNAME)
        print("👤 Entered username")
        time.sleep(1)

        # Clica no primeiro botão ativo (ignora texto)
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[@role="button" and not(@disabled)][1]'
            ))
        )
        next_button.click()
        print("➡️ Clicked generic next button")
        time.sleep(2)

    except TimeoutException:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/username_input_failed.png")
        save_html(driver, "username_input_failed.html")
        raise RuntimeError("❌ Couldn't find username input or next button")

    # 3. Preenche senha
    try:
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.clear()
        password_input.send_keys(PASSWORD)
        print("🔒 Entered password")
        time.sleep(1)

        # Clica no primeiro botão ativo (ignora texto)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[@role="button" and not(@disabled)][1]'
            ))
        )
        login_button.click()
        print("✅ Clicked generic login button")
        time.sleep(5)

    except TimeoutException:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/password_input_failed.png")
        save_html(driver, "password_input_failed.html")
        raise RuntimeError("❌ Couldn't find password input or login button")

    # 4. Verifica se login funcionou
    if "login" in driver.current_url or "signin" in driver.current_url:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/login_failed.png")
        save_html(driver, "login_failed.html")
        raise RuntimeError("❌ Login failed. Please check credentials")

    print("✅ Successfully logged in")


def search_and_retweet(driver, hashtag):
    """Procura tweets por hashtag e dá RT."""
    print(f"🔍 Searching for {hashtag}")
    driver.get(f"https://x.com/search?q={hashtag}&src=typed_query&f=live")
    time.sleep(5)

    try:
        tweets = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]'))
        )
        print(f"📝 Found {len(tweets)} tweets for {hashtag}")

        for tweet in tweets[:3]:  # só 3 primeiros para evitar spam
            try:
                rt_button = tweet.find_element(By.XPATH, './/button[@data-testid="retweet"]')
                rt_button.click()
                time.sleep(1)

                confirm = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="retweetConfirm"]'))
                )
                confirm.click()
                print(f"🔁 Retweeted {hashtag}")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Error retweeting: {e}")
    except TimeoutException:
        print(f"⚠️ No tweets found for {hashtag}")


def main():
    print("🚀 Starting retweet bot...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        login(driver)
        for tag in HASHTAGS:
            search_and_retweet(driver, tag)
    finally:
        driver.quit()
        print("🏁 Bot finished successfully")


if __name__ == "__main__":
    main()
