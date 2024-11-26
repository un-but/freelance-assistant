"""https://kwork.ru/projects scraper functions."""
from __future__ import annotations

import asyncio
import logging

from playwright._impl._errors import TimeoutError
from playwright.async_api import Browser, Playwright, async_playwright

from database import add_last_orders, get_last_orders


async def create_driver(pw: Playwright, headless_mode: bool = True) -> Browser:
    """Create chrome driver object.

    Args:
        headless_mode (bool, optional): True for server and False or not specify for debug with graphical interface
    Returns:
        Chrome: chrome driver object

    """
    if headless_mode:
        options_list = [
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--headless",
            "--ignore-certificate-errors-spki-list",
            "--log-level=3",
            "--disable-blink-features=AutomationControlled",
            "--disable-software-rasterizer",
            "--start-maximized",
        ]
    else:
        options_list = [
            # "--ignore-certificate-errors-spki-list",
            # "--log-level=3",
            # "--disable-blink-features=AutomationControlled",
            # "--start-maximized",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--ignore-certificate-errors-spki-list",
            "--log-level=3",
            "--disable-blink-features=AutomationControlled",
            "--disable-software-rasterizer",
            "--start-maximized",
        ]

    return await pw.chromium.launch(
        headless=headless_mode,
        args=options_list,
    )



async def get_data_from_kwork(url: str = "https://kwork.ru/projects?c=41") -> set:
    """Receives latest orders from Kwork project exchange.

    Returns:
        set: set of tuples with information about orders

    """
    last_orders = await get_last_orders(url)
    new_orders = []

    async with async_playwright() as pw:
        browser = await create_driver(pw=pw, headless_mode=False)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()
        try:
            await page.goto(url, timeout=5000)
        except TimeoutError:
            await page.reload()
        logging.info("Driver created")
        await asyncio.sleep(2)
        orders = await page.locator("div.want-card").all()

        logging.info("Page received")
        print(orders)
        for order in orders:
            order_header = order.locator("h1.wants-card__header-title")
            order_url = await order_header.locator("a").get_attribute("href")
            order_name = (await order_header.text_content()).strip()
            print("страница")

            # If an order was already processed the last time, iteration stops.
            if order_url in last_orders:
                logging.info("aborted")
                break

            order_price = (await order.locator("div.wants-card__price").locator("div.d-inline").text_content()).strip()

            # To get full description, click on the button. If description is short, there may not be button.
            description = order.locator("div.wants-card__description-text")
            try:
                await description.locator("div.kw-link-dashed").first.click(timeout=2000)
                order_description = (await description.locator("div.d-inline").nth(1).text_content()).strip()
            except TimeoutError:
                order_description = (await description.text_content()).strip()

            order_info = order.locator("div.want-card__informers-row > span")
            order_date = (await order_info.nth(0).text_content()).strip()
            order_responses = f"{
                (await order_info.nth(0).text_content()).split(": ")[1].strip()
            } откликов"

            # If the last processed order was not found on the page, all orders from it will be returned
            print(
                order_url,
                order_name,
                order_date,
                order_price,
                order_responses,
                "\n\n",
                order_description,
                "\n\n\n\n",
            )
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
            logging.info("New orders added to database")

        # If there were no orders before, the function returns empty list. Otherwise, it gives new orders.
        await context.clear_cookies()
        await browser.close()
        return new_orders[::-1] if last_orders else []


if __name__ == "__main__":
    from database import init_db
    asyncio.run(init_db())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(get_data_from_kwork())
