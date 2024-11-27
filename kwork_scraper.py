"""https://kwork.ru/projects scraper functions."""
from __future__ import annotations

import logging

from playwright._impl._errors import TimeoutError
from playwright.async_api import Browser, Playwright, async_playwright, expect

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
            "--ignore-certificate-errors-spki-list",
            "--log-level=3",
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
        ]

    return await pw.chromium.launch(
        headless=headless_mode,
        args=options_list,
    )



async def get_data_from_kwork(url: str) -> set:
    """Receives latest orders from Kwork project exchange.

    Returns:
        set: set of tuples with information about orders

    """
    last_orders = await get_last_orders(url)
    new_orders = []

    async with async_playwright() as pw:
        browser = await create_driver(pw=pw, headless_mode=True)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        try:
            await page.goto(url, timeout=5000)
        except TimeoutError:
            await page.reload()

        orders_locator = page.locator("div.want-card")
        await expect(orders_locator.last).to_be_visible()
        orders = await orders_locator.all()

        for order in orders:
            order_header = order.locator("h1.wants-card__header-title")
            order_url = "https://kwork.ru" + await order_header.locator("a").get_attribute("href")
            order_name = (await order_header.inner_text()).strip()

            # If an order was already processed the last time, iteration stops.
            if order_url in last_orders:
                logging.info("aborted")
                break

            order_price = (await order.locator("div.wants-card__price").locator("div.d-inline").inner_text()).strip()

            # To get full description, click on the button. If description is short, there may not be button.
            order_description = (await order.locator("div.wants-card__description-text > div").last.inner_text()).split("Скрыть")[0].strip()

            order_info = await order.locator("div.want-card__informers-row > span").all_inner_texts()
            order_date = order_info[0].strip()
            order_responses = f"Откликов: {
                order_info[1].split(":")[1].strip()
            }"

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

        # If there were no orders before, the function returns empty list. Otherwise, it gives new orders.
        await context.clear_cookies()
        await browser.close()
        return new_orders[::-1] if last_orders else []


if __name__ == "__main__":
    # UPDATE orders SET first_order = 'zov', second_order = 'zov', third_order = 'zov' WHERE page_url = 'https://kwork.ru/projects?c=41&attr=211'
    import asyncio
    from database import init_db
    asyncio.run(init_db())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(get_data_from_kwork("https://kwork.ru/projects?c=41&attr=211"))
