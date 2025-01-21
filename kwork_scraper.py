"""https://kwork.ru/projects scraper functions."""
from __future__ import annotations

from playwright._impl._errors import TimeoutError
from playwright.async_api import Browser, Locator, Playwright, expect

from database import add_last_orders, get_last_orders


async def create_driver(pw: Playwright, headless_mode: bool = True) -> Browser:
    """Create chrome driver object.

    Args:
        pw (Playwright): async playwright session
        headless_mode (bool, optional): True for server and False or not specify for debug with graphical interface
    Returns:
        Browser: driver object

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


async def get_data_from_kwork(url: str, browser: Browser) -> list:
    """Receives latest orders from Kwork project exchange.

    Args:
        url (str): page_url for scraping
        browser (Browser): driver object

    Returns:
        list: list of tuples with information about orders

    """
    new_orders = []
    last_orders = await get_last_orders(url)

    context = await browser.new_context(no_viewport=True)
    page = await context.new_page()

    while True:
        try:
            await page.goto(url, timeout=5000)
            break
        except TimeoutError:
            return new_orders

    try:
        orders_locator = page.locator("div.want-card")
        await expect(orders_locator.last).to_be_visible()
        orders = await orders_locator.all()
    except:
        return new_orders

    for order in orders:
        # If the last processed order was not found on the page, all orders from it will be returned
        if order_info := await get_info_from_order(order, last_orders):
            new_orders.append(order_info)
        else:
            break

    # If there are new orders, we get their URLs and add last three new orders to db.
    if new_orders:
        order_urls = [order[0] for order in new_orders]
        all_links = order_urls + list(last_orders)
        await add_last_orders(url, *all_links[:3])

    # If there were no orders before, the function returns empty list. Otherwise, it gives new orders.
    await context.close()
    return new_orders[::-1] if last_orders else []


async def get_info_from_order(order: Locator, last_orders: list[str]) -> tuple[str] | None:
    """Return info from kwork order.

    Args:
        order (Locator): kwork order locator
        last_orders (list[str]): list of handled orders

    Returns:
        tuple[str] | None: info tuple or None if order was handled in previous time

    """
    order_header = order.locator("h1.wants-card__header-title")
    order_url = "https://kwork.ru" + await order_header.locator("a").get_attribute("href")
    order_name = (await order_header.inner_text()).strip()

    # If an order was already processed the last time, iteration stops.
    if order_url in last_orders:
        return None

    order_price = (await order.locator("div.wants-card__price").locator("div.d-inline").inner_text()).strip()
    order_description = (await order.locator("div.wants-card__description-text > div").last.inner_text()).split("Скрыть")[0].strip()

    order_info = await order.locator("div.want-card__informers-row > span").all_inner_texts()
    order_date = order_info[0].strip()
    order_responses = f"Откликов: {
        order_info[1].split(":")[1].strip()
    }"

    # If the last processed order was not found on the page, all orders from it will be returned
    return [
        order_url,
        order_name,
        order_date,
        order_description,
        order_price,
        order_responses,
    ]
