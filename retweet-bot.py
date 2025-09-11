import os
import time
import random
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==========================
# CONFIGURAÇÕES
# ==========================
USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")
HASHTAGS = ["#ลูกหมีซอนญ่า", "#LMSY", "#HarmonySecret"]
SCREENSHOT_DIR = "screenshots"
HTML_DIR = "html_snapshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)


# ==========================
# FUNÇÃO PARA SALVAR HTML
# ==========================
def save_html(driver, name):
    path = os.path.join(HTML_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"📄 HTML snapshot saved: {path}")


# ==========================
# LOGIN
# ==========================
def login(driver):
    driver.get("https://x.com/")
    time.sleep(4)

    # 1. Clica no botão inicial "Entrar" se existir
    try:
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="loginButton"]'))
        )
        login_button.click()
        print("🔑 Clicked login button")
        time.sleep(2)
    except TimeoutException:
        print("⚠️ Login button not found, maybe already on login page")

    # 2. Preenche o username/email
    try:
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.clear()
        username_input.send_keys(USERNAME)
        print("👤 Entered username")
        time.sleep(1)
    except TimeoutException:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/username_input_failed.png")
        save_html(driver, "username_input_failed.html")
        raise RuntimeError("❌ Couldn't find username input")

    # 3. Tenta clicar no botão correto dinamicamente
    buttons_texts = ["Avançar", "Next", "Entrar", "Log in"]
    clicked = False
    for text in buttons_texts:
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f'//div[@role="button" and .//span[contains(text(),"{text}")]]'
                ))
            )
            btn.click()
            print(f"➡️ Clicked '{text}'")
            clicked = True
            time.sleep(2)
            break
        except TimeoutException:
            continue

    if not clicked:
        # Fallback genérico
        try:
            fallback_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(('xpath', '//div[@role="button" and not(@disabled)]'))
            )
            fallback_button.click()
            print("🟢 Clicked fallback button")
            time.sleep(2)
        except TimeoutException:
            driver.save_screenshot(f"{SCREENSHOT_DIR}/next_button_failed.png")
            save_html(driver, "next_button_failed.html")
            raise RuntimeError("❌ Couldn't find any button after username")

    # 4. Preenche a senha
    try:
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.clear()
        password_input.send_keys(PASSWORD)
        print("🔒 Entered password")
        time.sleep(1)

        # Tenta clicar no botão final
        final_buttons = ["Entrar", "Log in", "Login"]
        clicked_final = False
        for text in final_buttons:
            try:
                final_login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f'//div[@role="button" and .//span[contains(text(),"{text}")]] | //button[contains(text(),"{text}")]'
                    ))
                )
                final_login_button.click()
                print(f"✅ Clicked final '{text}'")
                clicked_final = True
                break
            except TimeoutException:
                continue

        if not clicked_final:
            driver.save_screenshot(f"{SCREENSHOT_DIR}/password_input_failed.png")
            save_html(driver, "password_input_failed.html")
            raise RuntimeError("❌ Couldn't click final login button")

    except TimeoutException:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/password_input_failed.png")
        save_html(driver, "password_input_failed.html")
        raise RuntimeError("❌ Couldn't find password input")

    # 5. Confirma se login foi bem-sucedido
    time.sleep(5)
    if "login" in driver.current_url or "signin" in driver.current_url:
        driver.save_screenshot(f"{SCREENSHOT_DIR}/login_failed.png")
        save_html(driver, "login_failed.html")
        raise RuntimeError("❌ Login failed. Please check username/password")

    print("✅ Successfully logged in")


# ==========================
# PESQUISA E RETWEET
# ==========================
def search_and_retweet(driver):
    for tag in HASHTAGS:
        print(f"🔍 Searching for {tag} …")
        driver.get(f"https://x.com/search?q={tag}&f=live")
        time.sleep(3)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]'))
            )
        except TimeoutException:
            driver.save_screenshot(f"{SCREENSHOT_DIR}/{re.sub('[^a-zA-Z0-9]', '_', tag)}_notweets.png")
            save_html(driver, f"{re.sub('[^a-zA-Z0-9]', '_', tag)}_notweets.html")
            print(f"⚠️ No tweets found for {tag}")
            continue

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"✅ Found {len(tweets)} tweets for {tag}")

        # Limita a retweetar até 3 por hashtag
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


# ==========================
# MAIN
# ==========================
def main():
    options = uc.ChromeOptions()
    # Roda headless mas de forma mais compatível
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
