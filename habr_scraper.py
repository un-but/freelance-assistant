"""Functions for getting all orders from Habr Freelance in search request."""
from __future__ import annotations

import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from utils import json_dump, json_load


async def get_data_from_habr() -> set:
    """Main function, adding info from all pages to database."""
    async_tasks = []
    result = []
    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",  # noqa: E501
            "user-agent": UserAgent().random,
        }
        url = "https://freelance.habr.com/tasks?categories=development_bots"

        async with session.get(url=url, headers=headers) as res:
            src = await res.text()

        soup = BeautifulSoup(src, "lxml")
        order_urls = ["https://freelance.habr.com" + order_url.find("a")["href"] for order_url in soup.find_all(class_="task__title")]
        json_file = await json_load()

        if json_file["habr"]:
            for order_url in order_urls:
                if order_url in json_file["habr"]:
                    break
                async_tasks.append(
                    asyncio.create_task(get_data_from_habr_order_page(order_url, session)),
                )
            result = await asyncio.gather(*async_tasks)

        json_file["habr"] = order_urls[:3]
        await json_dump(json_file)
        return set(result)


async def get_data_from_habr_order_page(order_url: str, session: aiohttp.ClientSession) -> None:
    """Return info from order page

    Args:
        order_url (str): link to order page
        session (aiohttp.ClientSession): aiohttp session for requests to order pages
    """
    headers = {"user-agent": UserAgent().random}

    async with session.get(url=order_url, headers=headers, timeout=1000) as res:
        src = await res.text()

    order_soup = BeautifulSoup(src, "lxml")
    order_name = order_soup.find(class_="task__title").get_text(" ", strip=True)
    order_description = order_soup.find(class_="task__description").get_text("\n", strip=True)
    order_price = order_soup.find(class_="task__finance").get_text(strip=True)

    order_meta = order_soup.find(class_="task__meta").get_text(" ", strip=True).split("\n • ")
    order_date = f"{order_meta[0]}/нет информации"
    order_responses = order_meta[1]

    return (
        order_url,
        order_name,
        order_date,
        order_description,
        order_price,
        order_responses,
    )
