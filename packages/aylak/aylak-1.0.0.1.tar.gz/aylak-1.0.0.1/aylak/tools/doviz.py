import asyncio
from contextlib import suppress
from json import loads
from warnings import simplefilter

from bs4 import BeautifulSoup
from pandas import read_html
from requests import get

from ._static import Static

with suppress(ImportError):
    from pandas.core.common import SettingWithCopyWarning

    simplefilter(action="ignore", category=SettingWithCopyWarning)


class Doviz(Static):

    def __init__(self) -> None:
        self.source = "altinkaynak.com"

    async def doviz(self):
        def _doviz():
            istek = get(f"http://www.{self.source}/Doviz/Kur/Guncel")
            corba = BeautifulSoup(istek.content, "lxml")
            tablo = corba.find("table", class_="table")

            panda_data = (
                read_html(str(tablo))[0]
                .rename(
                    columns={
                        "Unnamed: 0": "birim",
                        "Alış": "alis",
                        "Satış": "satis",
                        "Unnamed: 1": "sil",
                        "Unnamed: 5": "sil",
                        "₺ ₺": "sil",
                    }
                )
                .drop(columns="sil")
                .dropna()
                .reset_index(drop=True)
            )
            for say in range(len(panda_data["birim"])):
                panda_data["birim"][say] = panda_data["birim"][say][-3:]
            json_data = loads(panda_data.to_json(orient="records"))
            custom_json = {"source": self.source, "data": json_data}
            self.custom_json = custom_json if custom_json["data"] != [] else None
            return self.custom_json

        return await asyncio.get_event_loop().run_in_executor(None, _doviz)
