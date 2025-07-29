import undetected_chromedriver as uc
import time


def main():
    # Initialize Chrome options
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument('--headless')  # Uncomment this to run in headless mode
    chrome_options.add_argument('--disable-gpu')  # Disable GPU usage for compatibility
    chrome_options.add_argument('--no-sandbox')  # Disable sandboxing for compatibility

    # Initialize the undetected ChromeDriver
    driver = uc.Chrome(options=chrome_options)

    try:
        # Navigate to a webpage
        driver.get('https://ozon.ru')

        # Wait for a few seconds to allow the page to load
        time.sleep(5)

        # Print the contents of the page
        print(driver.page_source)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()