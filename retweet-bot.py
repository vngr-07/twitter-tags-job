import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# =======================
# CONFIGURATION
# =======================
USERNAME = os.getenv("TWITTER_USERNAME")  # Set in GitHub Secrets or Replit
PASSWORD = os.getenv("TWITTER_PASSWORD")
HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]
WAIT_TIME = 15  # seconds between actions

# =======================
# LOGIN TO X (TWITTER)
# =======================
def login_to_twitter(driver):
    driver.get("https://twitter.com/login")
    time.sleep(5)

    # Enter username
    username_input = driver.find_element(By.NAME, "text")
    username_input.send_keys(USERNAME)
    username_input.send_keys(Keys.RETURN)
    time.sleep(3)

    # Enter password
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)
    print("✅ Logged into Twitter")

# =======================
# SEARCH AND RETWEET
# =======================
def search_and_retweet(driver):
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag}...")
        driver.get(f"https://twitter.com/search?q={tag}&f=live")
        time.sleep(5)

        # Find tweets
        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"Found {len(tweets)} tweets for {tag}")

        for tweet in tweets[:3]:  # Limit to avoid spam
            try:
                # Find retweet button
                rt_button = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]')
                rt_button.click()
                time.sleep(1)

                # Confirm retweet
                confirm = driver.find_element(By.XPATH, '//div[@data-testid="retweetConfirm"]')
                confirm.click()
                print(f"🔁 Retweeted a tweet with {tag}")
                time.sleep(WAIT_TIME)
            except:
                print("⚠️ Skipping already retweeted tweet")
                continue

# =======================
# MAIN SCRIPT
# =======================
def main():
    options = uc.ChromeOptions()
    options.headless = True
    driver = uc.Chrome(options=options)

    try:
        login_to_twitter(driver)
        search_and_retweet(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
