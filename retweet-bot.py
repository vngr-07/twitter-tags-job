import os, time, json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]
WAIT_TIME = 12  # seconds between actions

def _inject_cookie_list(driver, cookies):
    # assumes we're already on the right domain
    added = 0
    for c in cookies:
        # keep only fields Selenium accepts
        cookie = {"name": c["name"], "value": c["value"], "path": c.get("path", "/")}
        # don't set domain explicitly to avoid domain-mismatch errors
        if "expiry" in c: cookie["expiry"] = c["expiry"]
        if "secure" in c: cookie["secure"] = c["secure"]
        if "httpOnly" in c: cookie["httpOnly"] = c["httpOnly"]
        try:
            driver.add_cookie(cookie)
            added += 1
        except Exception:
            pass
    print(f"✅ Injected {added} cookies on this domain")

def _parse_cookie_header(header):
    # header: "name=value; other=value; ..."
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

    # Go to twitter.com then x.com and inject on both (X uses both hosts)
    if cj:
        cookies = json.loads(cj)
        # remove properties that can break headless setCookie
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

    # Final check: page should show logged-in UI
    driver.get("https://x.com/home")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    print("✅ Logged in via cookies")

def search_and_retweet(driver):
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag} …")
        driver.get(f"https://x.com/search?q={tag}&f=live")
        WebDriverWait(driver, 12).until(
            EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]'))
        )
        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

        retweeted = 0
        for tweet in tweets:
            if retweeted >= 3:  # courteous limit per run
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
            except Exception:
                # skip if already retweeted or UI differs
                continue

def main():
    opts = uc.ChromeOptions()
    opts.headless = True
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=opts)
    try:
        login_with_cookies(driver)
        search_and_retweet(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
