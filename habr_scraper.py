"""https://freelance.habr.com scraper functions."""
from __future__ import annotations

import asyncio
import logging

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from database import add_last_orders, get_last_orders


async def get_data_from_habr(url: str = "https://freelance.habr.com/tasks?categories=development_bots") -> set:
    """Receives latest orders from Habr Freelance.

    Args:
        url (str): main page or category URL for finding new orders.

    Returns:
        set: set of tuples with information about orders

    """
    async_tasks = []
    last_orders = await get_last_orders(url)
    new_orders = []
    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "user-agent": UserAgent().random,
        }

        async with session.get(url=url, headers=headers) as res:
            src = await res.text()
            logging.debug("Page received")

        soup = BeautifulSoup(src, "lxml")
        order_urls = ["https://freelance.habr.com" + order_url.find("a")["href"] for order_url in soup.find_all(class_="task__title")]

        # If the last processed orders have already been saved, then add all new ones to the list for mailing
        if last_orders:
            for order_url in order_urls:
                if order_url in last_orders:
                    break
                async_tasks.append(
                    asyncio.create_task(get_data_from_habr_order_page(order_url, session)),
                )

            # If the last processed order was not found on the page, all orders from it will be returned
            new_orders = await asyncio.gather(*async_tasks)
            logging.debug("New orders collected")

        # Overwriting the last 3 orders
        await add_last_orders(url, *order_urls[:3])
        return new_orders


async def get_data_from_habr_order_page(order_url: str, session: aiohttp.ClientSession) -> tuple:
    """Collect order info from order page.

    Args:
        order_url (str): order page URL
        session (aiohttp.ClientSession): aiohttp client session for requests

    Returns:
        tuple: order info

    """
    headers = {"user-agent": UserAgent().random}

    async with session.get(url=order_url, headers=headers, timeout=1000) as res:
        src = await res.text()

    order_soup = BeautifulSoup(src, "lxml")

    order_name = order_soup.find(class_="task__title").get_text(" ", strip=True)
    order_description = order_soup.find(class_="task__description").get_text("\n", strip=True)
    order_price = order_soup.find(class_="task__finance").get_text(strip=True)

    order_meta = order_soup.find(class_="task__meta").get_text(" ", strip=True).split("\n • ")
    order_date = f"{order_meta[0]}"
    order_responses = order_meta[1]

    return (
        order_url,
        order_name,
        order_date,
        order_description,
        order_price,
        order_responses,
    )
