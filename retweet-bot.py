import os
import time
import random
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# utilitário para salvar debug
def save_debug(driver, name="debug"):
    os.makedirs("html_snapshots", exist_ok=True)
    with open(f"html_snapshots/{name}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot(f"html_snapshots/{name}.png")
    print(f"📄 HTML e screenshot salvos: {name}")


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


def login(driver):
    print("🔑 Abrindo login...")
    driver.get("https://twitter.com/i/flow/login")

    # espera o input de username
    try:
        username_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.send_keys(os.environ["TWITTER_USERNAME"])
        print("👤 Entered username")
    except Exception:
        save_debug(driver, "username_failed")
        raise RuntimeError("❌ Não achou input de username")

    # agora tenta encontrar o botão "next"
    try:
        next_button = None

        # 1ª tentativa: botão com data-testid
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="ocfEnterTextNextButton"]'))
            )
        except Exception:
            pass

        # 2ª tentativa: botão visível com texto
        if not next_button:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]//span[contains(text(),"Avançar") or contains(text(),"Next")]'))
                )
            except Exception:
                pass

        # 3ª tentativa: botão de login direto
        if not next_button:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]'))
                )
            except Exception:
                pass

        # 4ª tentativa: o botão que você encontrou (button[2])
        if not next_button:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '(//button[@type="button" and not(@disabled)])[2]'))
                )
            except Exception:
                pass

        # 5ª tentativa: botão genérico logo após o input
        if not next_button:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@name="text"]/ancestor::div[1]/following::button[1]'))
                )
            except Exception:
                pass

        if not next_button:
            save_debug(driver, "next_button_failed")
            raise RuntimeError("❌ Couldn't find username input or next button")

        next_button.click()
        print("👉 Clicked Next button")

    except Exception:
        save_debug(driver, "next_button_exception")
        traceback.print_exc()
        raise


def main():
    print("🚀 Starting retweet bot...")
    driver = create_driver()
    try:
        login(driver)
        print("✅ Login flow completo (até username).")
        # aqui você pode continuar com senha e depois retweetar
    finally:
        driver.quit()
        print("🏁 Bot finished successfully")


if __name__ == "__main__":
    main()
