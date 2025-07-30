import asyncio

from bs4 import BeautifulSoup
from requests import get

from ._static import Static


class HavaDurumu(Static):
    def __init__(self, il: str, ilce: str):
        self.source = "google.com"

    async def hava_durumu(self, il: str, ilce: str):
        def _hava_durumu():
            istek = get(
                f"https://www.{self.source}/search?&q={il}+{ilce}+hava+durumu&lr=lang_tr&hl=tr"
            )
            soup = BeautifulSoup(istek.text, "lxml")
            gun_durum = soup.findAll("div", class_="BNeawe")
            gun, durum = gun_durum[3].text.strip().split("\n")
            derece = soup.find("div", class_="BNeawe").text
            custom_json = {
                "source": self.source,
                "data": [
                    {
                        "day": gun,
                        "location": f"{il.capitalize()} {ilce.capitalize()}",
                        "degree": f"{durum} {derece}",
                    }
                ],
            }
            self.custom_json = custom_json if custom_json["data"] != [] else None
            return self.custom_json

        return await asyncio.get_event_loop().run_in_executor(None, _hava_durumu)

