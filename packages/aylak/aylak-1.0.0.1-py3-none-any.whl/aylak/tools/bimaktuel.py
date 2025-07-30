import requests, asyncio
from bs4 import BeautifulSoup

from ._static import Static


class BimAktuel(Static):
    def __init__(self) -> None:
        self.url = "https://www.bim.com.tr/"
        self.identity = super().identity
        self.veri = None

    async def aktuel(self):
        def _aktuel():
            response = requests.get(self.url, headers=self.identity)
            soup = BeautifulSoup(response.content, "lxml")
            date = soup.find("a", class_="active subButton").text.strip()
            urun_alani = soup.find("div", class_="productArea")

            urun_rerero = []
            for urun in urun_alani.findAll("div", class_="inner"):
                try:
                    urun_basligi = urun.find("h2", class_="title").text.strip()
                    urun_linki = f"{self.url}{urun.a['href']}"
                    urun_gorseli = f"{self.url}{urun.img['src'].replace(' ', '%20')}"
                    urun_fiyati = urun.find("a", class_="gButton triangle").text.strip()

                    urun_rerero.append(
                        {
                            "urun_baslik": urun_basligi,
                            "urun_link": urun_linki,
                            "urun_gorsel": urun_gorseli,
                            "urun_fiyat": urun_fiyati,
                        }
                    )
                except (AttributeError, KeyError):
                    continue

            custom_json = {"source": self.url, "date": date, "data": urun_rerero}

            self.custom_json = custom_json if custom_json["data"] != [] else None
            return self.custom_json

        self.veri = await asyncio.get_event_loop().run_in_executor(None, _aktuel)
        return self.veri
