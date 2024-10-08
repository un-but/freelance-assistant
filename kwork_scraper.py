"""Functions for getting all orders from Kwork in search request."""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import db

def create_driver(mode="headless") -> webdriver.Chrome:
    """Create chrome driver object.

    Args:
        mode (str, optional): "headless" for server or "desktop" for debug. Defaults to "headless".

    Returns:
        webdriver.Chrome
    """
    options = Options()

    if mode == "headless":
        options_list = [
            "--no-sandbox", 
            "--disable-gpu", 
            "--disable-dev-shm-usage", 
            "--headless", 
            "--ignore-certificate-errors-spki-list", 
            "--log-level=3",
            "--start-maximized"
        ]
        # options.add_argument('--start-maximized')
    elif mode == "desktop":
        # Добавить функции для отображения браузера
        pass

    for option in options_list:
        options.add_argument(option)

    return webdriver.Chrome(options=options)


def save_kwork_orders_info(driver: webdriver.Chrome) -> None:
    """Add to db all orders info from category page.

    Args:
        driver (webdriver.Chrome): chrome driver for selenium
    """
    orders = driver.find_elements(By.CLASS_NAME, "want-card")
    for order in orders:
        order_header = order.find_element(By.CLASS_NAME, "wants-card__header-title")
        order_url = order_header.get_attribute("href")
        order_name = order_header.text.strip()

        order_price = order.find_element(By.CLASS_NAME, "wants-card__price").find_element(By.CLASS_NAME, "d-inline").text.strip()

        description = order.find_element(By.CLASS_NAME, "wants-card__description-text")
        try:
            description.find_element(By.CLASS_NAME, "kw-link-dashed").click()
            time.sleep(0.5)
            order_description = description.find_elements(By.CLASS_NAME, "d-inline")[1].text
        except NoSuchElementException:
            order_description = description.text

        order_info = order.find_element(By.CLASS_NAME, "want-card__informers-row").find_elements(By.CLASS_NAME, "mr8")
        order_date = order_info[0].text.strip()
        order_responses = f"{order_info[1].text.split(": ")[1]} откликов"

        db.add_order_to_db(
            order_url,
            order_name,
            order_date,
            order_description,
            order_price,
            order_responses
        )


def get_data_from_kwork() -> None:
    """Main function, retrieves all orders tags."""
    driver = create_driver()
    current_page = 1
    last_page = 1
    while current_page <= last_page:
        url = f"https://kwork.ru/projects?c=41&page={current_page}"
        driver.get(url)
        time.sleep(3)

        save_kwork_orders_info(driver)

        if current_page == 1:
            last_page = int(driver.find_elements(By.CLASS_NAME, "pagination__item")[-2].text)

        current_page += 1

    driver.close()


if __name__ == "__main__":
    get_data_from_kwork()
