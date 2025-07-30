import asyncio
from contextlib import suppress

from bs4 import BeautifulSoup
from requests import get

from ._static import Static


class NobetciEczane(Static):
    def __init__(self):
        self.identity = super().identity
        self.source = "eczaneler.gen.tr"

    async def eczane(self, il: str, ilce: str):
        def _eczane(il: str, ilce: str):
            il = il.replace("İ", "i").lower()
            ilce = ilce.lower()

            tr2eng = str.maketrans(" .,-*/+-ıİüÜöÖçÇşŞğĞ", "________iIuUoOcCsSgG")
            il = il.translate(tr2eng)
            ilce = ilce.translate(tr2eng)

            istek = get(
                f"https://www.{self.source}/nobetci-{il}-{ilce}", headers=self.kimlik
            )

            corba = BeautifulSoup(istek.content, "lxml")
            bugun = corba.find("div", id="nav-bugun")

            custom_json = {"source": self.source, "data": []}

            with suppress(AttributeError):
                for bak in bugun.findAll("tr")[1:]:
                    ad = bak.find("span", class_="isim").text
                    mah = (
                        None
                        if bak.find("div", class_="my-2") is None
                        else bak.find("div", class_="my-2").text
                    )
                    adres = bak.find("div", class_="col-lg-6").text.split("(")[0]
                    tarif = (
                        None
                        if bak.find("span", class_="text-secondary font-italic") is None
                        else bak.find("span", class_="text-secondary font-italic").text
                    )
                    telf = bak.find("div", class_="col-lg-3 py-lg-2").text

                    custom_json["data"].append(
                        {
                            "ad": ad,
                            "mahalle": mah,
                            "adres": adres,
                            "tarif": tarif,
                            "telefon": telf,
                        }
                    )

            self.custom_json = custom_json if custom_json["data"] != [] else None
            return self.custom_json

        return await asyncio.get_event_loop().run_in_executor(None, _eczane, il, ilce)

 