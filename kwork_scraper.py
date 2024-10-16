"""https://kwork.ru/projects scraper functions."""
from __future__ import annotations

import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from utils import create_driver, json_dump, json_load


async def get_data_from_kwork() -> set:
    """Receives latest orders from Kwork project exchange.

    Returns:
        set: set of tuples with information about orders

    """
    driver = create_driver()
    url = "https://kwork.ru/projects?c=41"
    result = []
    driver.get(url)
    json_file = await json_load()

    orders = driver.find_elements(By.CLASS_NAME, "want-card")
    for order in orders:
        order_header = order.find_element(By.CLASS_NAME, "wants-card__header-title")
        order_url = order_header.find_element(By.TAG_NAME, "a").get_attribute("href")
        order_name = order_header.text.strip()

        if order_url in json_file["kwork"]:
            break

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

        result.append((
            order_url,
            order_name,
            order_date,
            order_description,
            order_price,
            order_responses,
        ))

    if result:
        order_urls = [order[0] for order in result]
        result = None if not json_file["kwork"] else set(result)
        json_file["kwork"] = (order_urls + json_file["kwork"])[:3]
        await json_dump(json_file)

    driver.close()
    return set(result)
