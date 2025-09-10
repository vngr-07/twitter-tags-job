import os
import time
import json
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]
WAIT_TIME = 12
SCREENSHOT_DIR = "screenshots"

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def _sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

def _inject_cookie_list(driver, cookies):
    added = 0
    for c in cookies:
        cookie = {"name": c["name"], "value": c["value"], "path": c.get("path", "/")}
        if "expiry" in c: cookie["expiry"] = c["expiry"]
        if "secure" in c: cookie["secure"] = c["secure"]
        if "httpOnly" in c: cookie["httpOnly"] = c["httpOnly"]
        try:
            driver.add_cookie(cookie)
            added += 1
        except:
            pass
    print(f"✅ Injected {added} cookies on this domain")

def _parse_cookie_header(header):
    out = []
    for seg in header.split(";"):
        seg = seg.strip()
        if "=" in seg:
            name, value = seg.split("=", 1)
            out.append({"name": name, "value": value, "path": "/"})
    return out

def login_with_cookies(driver):
    cj = os.getenv("COOKIES_JSON")
    ch = os.getenv("COOKIE_HEADER")
    if not cj and not ch:
        raise RuntimeError("Provide COOKIES_JSON or COOKIE_HEADER as an env var.")

    if cj:
        cookies = json.loads(cj)
        for c in cookies:
            c.pop("sameSite", None)
        for host in ("https://twitter.com/", "https://x.com/"):
            driver.get(host)
            time.sleep(2)
            _inject_cookie_list(driver, cookies)
    else:
        header_cookies = _parse_cookie_header(ch)
        driver.get("https://twitter.com/")
        time.sleep(2)
        _inject_cookie_list(driver, header_cookies)
        driver.get("https://x.com/")
        time.sleep(2)
        _inject_cookie_list(driver, header_cookies)

    driver.get("https://x.com/home")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    print("✅ Logged in via cookies")

def take_screenshot(driver, tag):
    filename = os.path.join(SCREENSHOT_DIR, f"{_sanitize_filename(tag)}.png")
    driver.save_screenshot(filename)
    print(f"📸 Screenshot saved: {filename}")

def human_scroll(driver, times=3):
    actions = ActionChains(driver)
    for _ in range(times):
        actions.scroll_by_amount(0, 800).perform()
        time.sleep(2)

def search_and_retweet(driver):
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag} …")

        success = False
        for attempt in range(2):  # Try twice per hashtag
            driver.get(f"https://x.com/search?q={tag}&f=live")
            time.sleep(3)  # Give time for JS to start loading tweets

            try:
                WebDriverWait(driver, 40).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]'))
                )
                success = True
                break
            except:
                print(f"⚠️ Tweets for {tag} didn't load, retrying...")
                take_screenshot(driver, tag)
                human_scroll(driver, times=5)
                time.sleep(5)

        if not success:
            print(f"⏭️ Skipping {tag}, no tweets found.")
            continue

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"✅ Found {len(tweets)} tweets for {tag}")

        retweeted = 0
        for tweet in tweets:
            if retweeted >= 3:
                break
            try:
                rt_button = tweet.find_element(By.XPATH, './/*[@data-testid="retweet"]')
                rt_button.click()
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@data-testid="retweetConfirm"]'))
                ).click()
                print(f"🔁 Retweeted one for {tag}")
                retweeted += 1
                time.sleep(WAIT_TIME)
            except:
                print("⚠️ Skipping already retweeted tweet")
                continue

def main():
    opts = uc.ChromeOptions()
    opts.headless = False  # ⬅️ Running with a visible browser now
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")

    driver = uc.Chrome(options=opts)
    try:
        login_with_cookies(driver)
        search_and_retweet(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
