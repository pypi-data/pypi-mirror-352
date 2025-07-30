import asyncio, traceback

import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
import qrcode.constants

from ._static import Static
from qrcode.main import QRCode as PyQRCode, GenericImage


class QRCode(Static):
    def __init__(self):
        self.source = "pyzbar"

    async def encode(
        self,
        data: str,
        save_path: str = "qrcode.png",
        box_size: int = 10,
        border: int = 4,
        version: int = None,
        fill_color: str = "black",
        back_color: str = "white",
    ):
        """QRCode oluşturur ve kaydeder.

        Args:
            data (str): Kodlanacak veri.
            save_path (str): Kaydedilecek dosya yolu.
            box_size (int, optional): Kare boyutu. Defaults to 10.
            border (int, optional): Kenarlık. Defaults to 4.
            version (int, optional): Versiyon. Defaults to None.
            fill_color (str, optional): Dolgu rengi. Defaults to "black".
            back_color (str, optional): Arkaplan rengi. Defaults to "white".
        """

        def _qrcode():
            qr = PyQRCode(
                version=version,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=box_size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img: GenericImage = qr.make_image(
                fill_color=fill_color, back_color=back_color
            )
            img.save(save_path)

        return await asyncio.get_event_loop().run_in_executor(None, _qrcode)

    async def decode(self, image_path: str):
        def _qrcode():
            try:
                image = Image.open(image_path)
                decoded = decode(image)
                data = decoded[0].data.decode("utf-8")

                custom_json = {"source": self.source, "data": [data]}
                self.custom_json = custom_json if custom_json["data"] != [] else None
                return self.custom_json
            except Exception as e:
                trace = traceback.format_exc()
                custom_json = {
                    "source": self.source,
                    "data": [{"error": str(e), "trace": trace}],
                }
                self.custom_json = custom_json if custom_json["data"] != [] else None

        return await asyncio.get_event_loop().run_in_executor(None, _qrcode)
