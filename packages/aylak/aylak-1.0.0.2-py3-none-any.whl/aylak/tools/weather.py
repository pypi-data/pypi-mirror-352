import aiohttp
from typing import List, Union, Dict, Any, Literal

""" c    Hava Durumu,
    C    Hava Durumu Metin Adı,
    x    Hava durumu, düz metin sembolü,
    h    Nem,
    t    Sıcaklık (gerçek),
    f    Sıcaklık (Hissediyor),
    w    Rüzgâr,
    l    Konum,
    m    Ay evreleri 🌑🌒🌓🌔🌕🌖🌗🌘,
    M    Ay Günü,
    p    Yağış (mm/3 saat),
    P    Basınç (HPA),
    u    UV endeksi (1-12),

    D    Şafak*,
    S    gündoğumu*,
    z    Zirvi*,
    s    Gün batımı*,
    d    Alacakaranlıkta*,
    T    Şimdiki zaman*,
    Z    Yerel saat dilimi.

(*times are shown in the local timezone)"""


class Weather:
    def __init__(self):
        self.MAIN_URL = "https://wttr.in/{city}?"
        self.turkish_chars = {
            "ç": "c",
            "ğ": "g",
            "ı": "i",
            "i̇": "i",
            "ö": "o",
            "ş": "s",
            "ü": "u",
        }
        self.formats = {
            "%c": "HavaDurumu",
            "%C": "HavaDurumuMetin",
            "%x": "HavaDurumuSembol",
            "%h": "Nem",
            "%t": "Sıcaklık",
            "%f": "HissedilenSıcaklık",
            "%w": "Rüzgar",
            "%l": "Konum",
            "%m": "AyEvreleri",
            "%M": "AyGünü",
            "%p": "Yağış",
            "%P": "Basınç",
            "%u": "UV",
            "%D": "Şafak",
            "%S": "Gündoğumu",
            "%z": "Zirvi",
            "%s": "Günbatımı",
            "%d": "Alacakaranlık",
            "%T": "ŞimdikiZaman",
            "%Z": "SaatDilimi",
        }
        ["%c", "%t", "%w", "%h", "%C"],

    async def weather(
        self,
        city: str,
        formats: List[str] = [
            "HavaDurumu",
            "Sıcaklık",
            "Rüzgar",
            "Nem",
            "HavaDurumuMetin",
        ],
        response_type: Union[
            str,
            Literal[
                "json",
                "text",
            ],
        ] = "text",
    ) -> Union[Dict[str, Any], str]:
        """Belirtilen şehir için hava durumu bilgilerini alır.

        Args:
            city (str): Hava durumu bilgisi alınacak şehir.
            formats (List[str], optional): Hava durumu bilgilerinin formatı. Defaults to ["HavaDurumu", "Sıcaklık", "Rüzgar", "Nem", "HavaDurumuMetin"].
            response_type (Union[str, Literal["json", "text"]], optional): Hava durumu bilgilerinin tipi. Defaults to "text".

        Returns:
            Union[Dict[str, Any], str]: Hava durumu bilgileri.
        """
        city = city.lower().replace(" ", "+")
        for char in self.turkish_chars:
            city = city.replace(char, self.turkish_chars[char])
        url = self.MAIN_URL.format(city=city)

        for format in formats:
            if format not in self.formats.values():
                raise ValueError(f"{format} formatı desteklenmiyor!")

        url += "&format=%s" % "".join(
            [
                f"%{list(self.formats.keys())[list(self.formats.values()).index(format)]}"
                for format in formats
            ]
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response_type == "json":
                    return await response.json()
                return await response.text()
