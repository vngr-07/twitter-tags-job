import os
import json
import time
import random
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ==============================
# CONFIGURATION
# ==============================
HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]
BASE_URL = "https://twitter.com/search?q={}&src=typed_query&f=live"
COOKIES_JSON = os.getenv("COOKIES_JSON")
SCREENSHOT_DIR = Path("screenshots")
HTML_DIR = Path("html_snapshots")

# Create folders if missing
SCREENSHOT_DIR.mkdir(exist_ok=True)
HTML_DIR.mkdir(exist_ok=True)


# ==============================
# UTILS
# ==============================
def inject_cookies(driver):
    """Injects saved cookies into the Twitter session."""
    cookies = json.loads(COOKIES_JSON)
    driver.get("https://twitter.com/")  # Load domain first

    valid_cookies = []
    for cookie in cookies:
        # Sanitize SameSite attribute
        if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
            cookie.pop("sameSite")

        # Remove extra fields Chrome stores but Selenium hates
        for field in ["size", "priority", "hostOnly", "session"]:
            cookie.pop(field, None)

        try:
            driver.add_cookie(cookie)
            valid_cookies.append(cookie)
        except Exception as e:
            print(f"⚠️ Skipped cookie '{cookie.get('name')}' → {e}")

    driver.refresh()
    print(f"✅ Injected {len(valid_cookies)} cookies successfully")


def save_debug_data(driver, hashtag, attempt):
    """Saves a screenshot and HTML snapshot for debugging."""
    sanitized_tag = hashtag.replace("#", "")
    screenshot_path = SCREENSHOT_DIR / f"{sanitized_tag}_try{attempt}.png"
    html_path = HTML_DIR / f"{sanitized_tag}_try{attempt}.html"

    driver.save_screenshot(str(screenshot_path))
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    print(f"📸 Saved screenshot: {screenshot_path}")
    print(f"📝 Saved HTML snapshot: {html_path}")


def search_and_retweet(driver):
    """Searches for tweets with given hashtags and retweets them."""
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag} …")
        search_url = BASE_URL.format(tag.replace("#", "%23"))
        driver.get(search_url)

        # Wait for tweets to load
        tweets_loaded = False
        for attempt in range(1, 3):  # Two attempts max
            try:
                WebDriverWait(driver, 12).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//article[@data-testid="tweet"]')
                    )
                )
                tweets_loaded = True
                break
            except TimeoutException:
                print(f"⚠️ Tweets for {tag} didn't load, retrying ({attempt}/2)...")
                save_debug_data(driver, tag, attempt)

        if not tweets_loaded:
            print(f"⏭️ Skipping {tag}, no tweets found.")
            continue

        # Grab tweets
        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"✅ Found {len(tweets)} tweets for {tag}")

        # Retweet up to 3 random tweets per tag
        to_retweet = random.sample(tweets, min(len(tweets), 3))
        for idx, tweet in enumerate(to_retweet, 1):
            try:
                retweet_btn = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", retweet_btn)
                time.sleep(1)
                retweet_btn.click()

                confirm_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="retweetConfirm"]'))
                )
                confirm_btn.click()

                print(f"🔁 Retweeted tweet {idx}/{len(to_retweet)} for {tag}")
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                print(f"⚠️ Failed to retweet tweet {idx}: {e}")


def main():
    opts = uc.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=opts)
    driver.set_window_size(1400, 900)

    print("✅ Browser launched successfully")
    inject_cookies(driver)
    print("✅ Logged in via cookies")

    search_and_retweet(driver)
    driver.quit()
    print("🏁 Bot finished successfully")


if __name__ == "__main__":
    main()
