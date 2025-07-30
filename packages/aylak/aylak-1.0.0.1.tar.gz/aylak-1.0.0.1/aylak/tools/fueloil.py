import requests, asyncio
from bs4 import BeautifulSoup

from ._static import Static


class FuelOil(Static):
    def __init__(self):
        self.url = "https://www.haberler.com/finans/akaryakit/"
        self.identity = super().identity
        self.fuel_data = None

    async def prices(self):
        def __prices():
            response = requests.get(self.url, headers=self.identity)
            soup = BeautifulSoup(response.content, "lxml")

            last_updated = soup.select(
                "div.hbTableContent.piyasa > table > tbody > tr:nth-child(1) > td:nth-child(2)"
            )[0].text
            table = soup.find("div", class_="hbTableContent piyasa")

            fuel_data = {
                "source": "haberler.com",
                "last_updated": last_updated,
                "data": [],
            }

            for row in table.findAll("tr")[1:]:
                fuel_type = row.find("td", {"width": "50%"}).text.replace(" TL", " - ₺")
                price = row.find("td", {"width": "16%"}).text

                fuel_data["data"].append({"type": fuel_type, "price": price})

            self.fuel_data = fuel_data if fuel_data["data"] != [] else None
            self.custom_json = self.fuel_data
            return self.fuel_data

        return await asyncio.get_event_loop().run_in_executor(None, __prices)
