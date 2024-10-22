"""https://kwork.ru/projects scraper functions."""
from __future__ import annotations

import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from utils import create_driver, add_last_orders, get_last_orders, check_page_for_processing, init_db


async def get_data_from_kwork(url: str = "https://kwork.ru/projects?c=41") -> set:
    """Receives latest orders from Kwork project exchange.

    Returns:
        set: set of tuples with information about orders

    """
    new_orders = set()

    driver = create_driver(mode="headless")
    driver.get(url)
    orders = driver.find_elements(By.CLASS_NAME, "want-card")

    for order in orders:
        order_header = order.find_element(By.CLASS_NAME, "wants-card__header-title")
        order_url = order_header.find_element(By.TAG_NAME, "a").get_attribute("href")
        order_name = order_header.text.strip()

        # If an order was already done during the last time, iteration stops.
        if order_url in json_file["kwork"]:
            break

        order_price = order.find_element(By.CLASS_NAME, "wants-card__price").find_element(By.CLASS_NAME, "d-inline").text.strip()

        # To get full description, click on the button. If description is short, there may not be button.
        description = order.find_element(By.CLASS_NAME, "wants-card__description-text")
        try:
            description.find_element(By.CLASS_NAME, "kw-link-dashed").click()
            time.sleep(0.5)
            order_description = description.find_elements(By.CLASS_NAME, "d-inline")[1].text
        except NoSuchElementException:
            order_description = description.text

        order_info = order.find_element(By.CLASS_NAME, "want-card__informers-row").find_elements(By.TAG_NAME, "span")
        order_date = order_info[0].text.strip()
        order_responses = f"{order_info[1].text.split(": ")[1]} откликов"

        # If the last processed order was not found on the page, all orders from it will be returned
        new_orders.add((
            order_url,
            order_name,
            order_date,
            order_description,
            order_price,
            order_responses,
        ))

    # If there are new orders, we get their URLs.
    if new_orders:
        order_urls = [order[0] for order in new_orders]
        # If there were no orders before, the function returns empty list. Otherwise, it gives new orders.
        new_orders = set() if not json_file["kwork"] else set(new_orders)
        # The last three orders are checked to find new orders at the next function call.
        json_file["kwork"] = (order_urls + json_file["kwork"])[:3]
        await json_dump(json_file)

    driver.close()
    return new_orders
