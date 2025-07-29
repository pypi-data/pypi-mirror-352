from playwright.sync_api import sync_playwright
import ssh_config


def open_rover_web_interface():
    url = f"http://{ssh_config.HOSTNAME}/"
    print(f"Открываем веб-интерфейс: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            print("Веб-интерфейс открыт в браузере Playwright.")
            input("Нажмите Enter для закрытия браузера...")
            browser.close()
    except Exception as e:
        print(f"Не удалось открыть браузер автоматически: {e}")
        print(f"Попробуйте скопировать URL: {url}")

if __name__ == "__main__":
    open_rover_web_interface()
