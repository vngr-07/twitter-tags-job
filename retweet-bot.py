import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# =======================
# CONFIGURATION
# =======================
USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")
HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]
WAIT_TIME = 15  # seconds between actions

# =======================
# LOGIN TO TWITTER/X
# =======================
def login_to_twitter(driver):
    driver.get("https://twitter.com/login")
    time.sleep(5)

    # Step 1: Enter username/email
    username_input = driver.find_element(By.NAME, "text")
    username_input.send_keys(USERNAME)
    username_input.send_keys(Keys.RETURN)
    time.sleep(4)

    # Step 2: Handle potential extra verification step
    try:
        alt_input = driver.find_element(By.NAME, "text")
        if alt_input:
            print("🔒 X is asking for email/phone confirmation...")
            alt_input.send_keys(USERNAME)
            alt_input.send_keys(Keys.RETURN)
            time.sleep(3)
    except:
        pass  # No extra step needed

    # Step 3: Enter password safely
    try:
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(6)
        print("✅ Logged into X successfully")
    except:
        print("❌ Could not find password input. Login failed.")
        driver.save_screenshot("login_error.png")
        raise

# =======================
# SEARCH AND RETWEET
# =======================
def search_and_retweet(driver):
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag}...")
        driver.get(f"https://twitter.com/search?q={tag}&f=live")
        time.sleep(5)

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"Found {len(tweets)} tweets for {tag}")

        retweeted = 0
        for tweet in tweets:
            if retweeted >= 3:  # Limit to avoid spam
                break
            try:
                rt_button = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]')
                rt_button.click()
                time.sleep(1)

                confirm = driver.find_element(By.XPATH, '//div[@data-testid="retweetConfirm"]')
                confirm.click()
                print(f"🔁 Retweeted a tweet with {tag}")
                retweeted += 1
                time.sleep(WAIT_TIME)
            except:
                print("⚠️ Skipping already retweeted tweet")
                continue

# =======================
# MAIN FUNCTION
# =======================
def main():
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)

    try:
        login_to_twitter(driver)
        search_and_retweet(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
