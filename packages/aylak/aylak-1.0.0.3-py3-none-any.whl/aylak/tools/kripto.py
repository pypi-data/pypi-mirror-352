from typing import Literal

import aiohttp

from ._static import Static


class Kripto(Static):
    def __init__(self):
        self.source = "api.binance.com"

    async def kripto(
        self,
        symbol: str,
        interval: Literal[
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ] = None,
    ):
        interval_url = f"https://{self.source}/api/v3/klines?symbol={symbol.upper()}&interval={interval}"
        today_url = f"https://{self.source}/api/v3/ticker/24hr?symbol={symbol.upper()}"
        url = interval_url if interval else today_url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200 and not interval:
                    data: dict | None = await response.json()
                    data = {
                        "sembol": data.get("symbol"),
                        "fiyat_degisimi": data.get("priceChange"),
                        "fiyat_degisim_yuzdesi": data.get("priceChangePercent"),
                        "agirlikli_ortalama_fiyat": data.get("weightedAvgPrice"),
                        "onceki_kapanis_fiyati": data.get("prevClosePrice"),
                        "son_fiyat": data.get("lastPrice"),
                        "son_miktar": data.get("lastQty"),
                        "alim_fiyati": data.get("bidPrice"),
                        "alim_miktari": data.get("bidQty"),
                        "satim_fiyati": data.get("askPrice"),
                        "satim_miktari": data.get("askQty"),
                        "acilis_fiyati": data.get("openPrice"),
                        "en_yuksek_fiyat": data.get("highPrice"),
                        "en_dusuk_fiyat": data.get("lowPrice"),
                        "hacim": data.get("volume"),
                        "alim_satim_hacmi": data.get("quoteVolume"),
                        "acilis_zamani": data.get("openTime"),
                        "kapanis_zamani": data.get("closeTime"),
                        "islem_sayisi": data.get("count"),
                    }
                    custom_json = {"source": self.source, "data": data}
                    self.custom_json = custom_json
                    return custom_json if custom_json["data"] != [] else None

                elif response.status == 200 and interval:
                    data = [
                        {
                            "acilis_zamani": data[0],
                            "acilis_fiyati": veri[1],
                            "en_yuksek_fiyat": veri[2],
                            "en_dusuk_fiyat": veri[3],
                            "onceki_kapanis_fiyati": veri[4],
                            "hacim": veri[5],
                            "kapanis_zamani": veri[6],
                            "teklif_varlik_hacmi": veri[7],
                            "islem_sayisi": veri[8],
                            "satin_alma_temel_varlik_hacmi": veri[9],
                            "satın_alma_teklifi_varlik_hacmi": veri[10],
                        }
                        for veri in await response.json()
                    ]
                    custom_json = {"source": self.source, "data": data}
                    self.custom_json = (
                        custom_json if custom_json["data"] != [] else None
                    )
                    return custom_json if custom_json["data"] != [] else None

                elif response.status != 200:
                    data = {
                        "hata": await response.json()["msg"],
                        "kod": await response.json()["code"],
                        "cozum": "Çıkan hata kodunu burda aratın:  https://github.com/binance/binance-spot-api-docs/blob/master/errors.md",
                    }
                    custom_json = {"source": self.source, "data": data}
                    self.custom_json = custom_json
                    return custom_json if custom_json["data"] != [] else None
