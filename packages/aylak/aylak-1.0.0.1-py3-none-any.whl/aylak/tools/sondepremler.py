# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

import asyncio, aiohttp
from json import loads, dumps

import pandas as pd
import asyncio

from ._static import Static
from typing import Union, Dict, Any, List, Literal, Optional, Tuple, Type


class SonDepremler(Static):
    def __init__(self) -> None:
        self.source = "basicbots.pw:3000"
        self.identity = super().identity

    async def son_depremler(
        self,
        min: float = None,
        max: float = None,
        tarih: str = None,
        minsaat: str = None,
        maxsaat: str = None,
        sehir: str = None,
        minderinlik: float = None,
        maxderinlik: float = None,
        minenlem: float = None,
        maxenlem: float = None,
        minboylam: float = None,
        maxboylam: float = None,
        baslangic: str = None,
        bitis: str = None,
    ) -> Union[Dict[str, Any], Exception]:
        """Son depremleri getirir.

        Args:
            min (`float`, `optional`): Minimum büyüklük. Defaults to None.
            max (`float`, `optional`): Maksimum büyüklük. Defaults to None.
            tarih (`str`, `optional`): Tarih. Defaults to None.
            minsaat (`str`, `optional`): Minimum saat. Defaults to None.
            maxsaat (`str`, `optional`): Maksimum saat. Defaults to None.
            sehir (`str`, `optional`): Şehir. Defaults to None.
            minderinlik (`float`, `optional`): Minimum derinlik. Defaults to None.
            maxderinlik (`float`, `optional`): Maksimum derinlik. Defaults to None.
            minenlem (`float`, `optional`): Minimum enlem. Defaults to None.
            maxenlem (`float`, `optional`): Maksimum enlem. Defaults to None.
            minboylam (`float`, `optional`): Minimum boylam. Defaults to None.
            maxboylam (`float`, `optional`): Maksimum boylam. Defaults to None.
            baslangic (`str`, `optional`): Başlangıç. Defaults to None.
            bitis (`str`, `optional`): Bitiş. Defaults to None.

        Returns:
            Union[Dict[`str`, Any], Exception]: Son depremler.

        Example:
            .. code-block:: python
                deprem = SonDepremler()
                deprem.son_depremler(min=4.2, max=5.0)
                deprem.son_depremler(tarih="2020.01.26")
                deprem.son_depremler(minsaat="16:48:00", maxsaat="17:55:00")
                deprem.son_depremler(sehir="BALIKESIR")
                deprem.son_depremler(minderinlik=12.5, maxderinlik=15)
                deprem.son_depremler(minenlem=36.14, maxenlem=38.68)
                deprem.son_depremler(minboylam=36.14, maxboylam=38.68)
                deprem.son_depremler(baslangic="2020.01.26", bitis="2020.01.27")
        """

        params = {
            "min": min,
            "max": max,
            "tarih": tarih,
            "minsaat": minsaat,
            "maxsaat": maxsaat,
            "sehir": sehir,
            "minderinlik": minderinlik,
            "maxderinlik": maxderinlik,
            "minenlem": minenlem,
            "maxenlem": maxenlem,
            "minboylam": minboylam,
            "maxboylam": maxboylam,
            "baslangic": baslangic,
            "bitis": bitis,
        }

        """Api Kullanım
        Api Adres	Açıklama
        /api	Türkiye'de gerçekleşen son 500 deprem bilgisini getirir.
        /api?min=4.2&max=5.0	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz mininum ve maximum büyüklüğe göre depremleri getirir.
        /api?tarih=2020.01.26	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz tarihte gerçekleşen depremleri getirir.
        /api?minsaat=16:48:00&maxsaat=17:55:00	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz başlangıç ve bitiş saatlerine göre depremleri getirir
        /api?sehir=(BALIKESIR)	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz şehre göre depremleri getirir.
        /api?minderinlik=12.5&maxderinlik=15	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz mininum ve maximum derinliğe göre depremleri getirir.
        /api?minenlem=36.14&maxenlem=38.68	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz enlem aralığına göre depremleri getirir.
        /api?minboylam=36.14&boylam=38.68	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz boylam aralığına göre depremleri getirir.
        /api?baslangic=2020.01.26&bitis=2020.01.27	Türkiye'de gerçekleşen son 500 deprem bilgisini arasından istemiş olduğunuz iki tarih arasına göre depremleri getirir."""

        try:
            URL = f"http://{self.source}/api?"
            # add to url
            for key, value in params.items():
                if value:
                    URL += f"&{key}={value}"

            async with aiohttp.ClientSession() as session:
                async with session.get(URL, headers=self.identity) as response:
                    data = await response.json()
                    custom_json = {"source": self.source, "data": data}
                    self.custom_json = custom_json
                    return custom_json if custom_json["data"] != [] else None
        except Exception as e:
            custom_json = {"source": self.source, "data": [{"error": str(e)}]}
            self.custom_json = custom_json
            return e
