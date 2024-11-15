"""https://kwork.ru/projects scraper functions."""
from __future__ import annotations

import asyncio
import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from db import add_last_orders, get_last_orders


def create_driver(mode: str = "desktop") -> Chrome:
    """Create chrome driver object.

    Args:
        mode (str, optional): "headless" for server and "desktop" or not specify for debug with graphical interface
    Returns:
        Chrome: chrome driver object

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
        ]
    elif mode == "desktop":
        options_list = [
            "--ignore-certificate-errors-spki-list",
            "--log-level=3",
        ]

    for option in options_list:
        options.add_argument(option)

    return Chrome(options=options)



async def get_data_from_kwork(url: str = "https://kwork.ru/projects?c=41") -> set:
    """Receives latest orders from Kwork project exchange.

    Returns:
        set: set of tuples with information about orders

    """
    last_orders = await get_last_orders(url)
    new_orders = []

    driver = create_driver(mode="headless")
    logging.debug("Driver created")
    driver.get(url)
    orders = driver.find_elements(By.CLASS_NAME, "want-card")

    logging.debug("Page received")
    for order in orders:
        logging.debug("Order handled")
        order_header = order.find_element(By.CLASS_NAME, "wants-card__header-title")
        order_url = order_header.find_element(By.TAG_NAME, "a").get_attribute("href")
        order_name = order_header.text.strip()

        # If an order was already processed the last time, iteration stops.
        if order_url in last_orders:
            logging.debug("aborted")
            break

        order_price = order.find_element(By.CLASS_NAME, "wants-card__price").find_element(By.CLASS_NAME, "d-inline").text.strip()

        # To get full description, click on the button. If description is short, there may not be button.
        description = order.find_element(By.CLASS_NAME, "wants-card__description-text")
        try:
            description.find_element(By.CLASS_NAME, "kw-link-dashed").click()
            await asyncio.sleep(0.5)
            order_description = description.find_elements(By.CLASS_NAME, "d-inline")[1].text
        except NoSuchElementException:
            order_description = description.text

        order_info = order.find_element(By.CLASS_NAME, "want-card__informers-row").find_elements(By.TAG_NAME, "span")
        order_date = order_info[0].text.strip()
        order_responses = f"{order_info[1].text.split(": ")[1]} откликов"

        # If the last processed order was not found on the page, all orders from it will be returned
        new_orders.append((
            order_url,
            order_name,
            order_date,
            order_description,
            order_price,
            order_responses,
        ))

    # If there are new orders, we get their URLs and add last three new orders to db.
    if new_orders:
        order_urls = [order[0] for order in new_orders]
        all_links = order_urls + list(last_orders)
        await add_last_orders(url, *all_links[:3])
        logging.debug("New orders added to database")

    # If there were no orders before, the function returns empty list. Otherwise, it gives new orders.
    driver.close()
    return new_orders[::-1] if last_orders else []
