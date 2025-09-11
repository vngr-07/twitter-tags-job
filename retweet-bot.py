import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========= CONFIG =========
HASHTAGS = ["#LMSY", "#ลูกหมีซอนญ่า", "#harmonysecret"]
RETWEET_LIMIT_PER_HASHTAG = 3
# coloque TWITTER_USERNAME e TWITTER_PASSWORD nos secrets do GitHub Actions

# ========= DRIVER =========
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# ========= DEBUG =========
def save_debug(driver, name):
    ts = str(int(time.time()))
    try:
        driver.save_screenshot(f"{name}_{ts}.png")
        with open(f"{name}_{ts}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception:
        pass

# ========= LOGIN =========
def login(driver):
    print("🔑 Abrindo login...")
    driver.get("https://twitter.com/i/flow/login")

    # === USERNAME ===
    username_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    username_input.send_keys(os.environ["TWITTER_USERNAME"])
    print("👤 Entered username")

    # Botão Next
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//input[@name="text"]/ancestor::div[1]/following::button[1]')
        )
    )
    next_button.click()
    print("👉 Clicked Next button")

    # === PASSWORD ===
    try:
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(os.environ["TWITTER_PASSWORD"])
        print("🔒 Entered password")

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]'))
        )
        login_button.click()
        print("🚪 Clicked Login button")
    except Exception:
        save_debug(driver, "password_failed")
        raise RuntimeError("❌ Não achou o input de senha")

    # esperar a home carregar
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href="/home"]'))
    )
    print("✅ Login concluído")

# ========= RETWEET =========
def retweet_hashtag(driver, hashtag, limit=RETWEET_LIMIT_PER_HASHTAG):
    print(f"🔍 Procurando tweets com {hashtag}...")

    driver.get(f"https://twitter.com/search?q={hashtag}&src=typed_query&f=live")
    time.sleep(5)  # esperar carregar tweets

    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    count = 0

    for tweet in tweets:
        try:
            retweet_btn = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]')
            retweet_btn.click()
            time.sleep(1)
            confirm_btn = driver.find_element(By.XPATH, '//div[@data-testid="retweetConfirm"]')
            confirm_btn.click()
            count += 1
            print(f"✅ Retweet feito para {hashtag} ({count}/{limit})")
            time.sleep(random.randint(5, 10))  # delay natural
        except Exception:
            print(f"⚠️ Não conseguiu retweetar um tweet em {hashtag}")
        if count >= limit:
            break

# ========= MAIN =========
def main():
    print("🚀 Starting retweet bot...")
    driver = create_driver()
    try:
        login(driver)
        for tag in HASHTAGS:
            retweet_hashtag(driver, tag)
    finally:
        driver.quit()
        print("🏁 Bot finished successfully")

if __name__ == "__main__":
    main()
