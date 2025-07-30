# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

import aiohttp
from parsel import Selector

from ._static import Static


class Masal(Static):

    def __init__(self) -> None:
        self.url = "https://www.masaloku.net"
        self.identity = super().identity
        self.custom_json = {}

    async def masallar(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.identity) as response:
                secici = Selector(await response.text())

        custom_json = {"kaynak": self.url, "data": []}

        for masal in secici.xpath(
            "//ul[@id='posts-container']/li[contains(@class, 'post-item')]"
        ):
            adi = masal.xpath(".//h2/a/text()").get()
            linki = masal.xpath(".//h2/a/@href").get()

            custom_json["data"].append(
                {
                    "ad": adi,
                    "link": linki,
                    "icerik": "\n".join(
                        Selector(
                            await (
                                await session.get(linki, headers=self.identity)
                            ).text()
                        )
                        .xpath("//div[contains(@class, 'entry-content')]/p/text()")
                        .getall()[1:]
                    ),
                }
            )

        self.custom_json = custom_json if custom_json["data"] != [] else None
        return self.custom_json

 