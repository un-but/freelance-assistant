"""Functions for getting all orders from Habr Freelance in search request."""

import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import database


async def get_data_from_habr() -> None:
    """Main function, adding info from all pages to database."""
    async_tasks = []
    async with aiohttp.ClientSession() as session:
        p = 1
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "user-agent": UserAgent().random
        }
        while True:
            url = f"https://freelance.habr.com/tasks?categories=development_bots&page={p}"

            async with session.get(url=url, headers=headers) as res:
                src = await res.text()

            soup = BeautifulSoup(src, "lxml")

            if soup.find(class_="empty-block__title"):
                break

            orders = soup.find_all(class_="task__title")
            for order in orders:
                order_url = "https://freelance.habr.com" + order.find("a")["href"]
                async_tasks.append(
                    asyncio.create_task(get_data_from_habr_order_page(order_url, session))
                )

            p += 1

        await asyncio.gather(*async_tasks)


async def get_data_from_habr_order_page(order_url: str, session: aiohttp.ClientSession) -> None:
    """Functions for getting info from one page

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


    database.add_order_to_db(
        order_url,
        order_name,
        order_date,
        order_description,
        order_price,
        order_responses
    )



if __name__ == "__main__":
    asyncio.run(get_data_from_habr())
