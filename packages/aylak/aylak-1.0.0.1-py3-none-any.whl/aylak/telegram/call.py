from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.exceptions import *
from pytgcalls.types import ChatUpdate, MediaStream, Update

from aylak.telegram.keys import get_keys


class PrivateCall:
    def __init__(self, client: Client = None, session_string: str = None):
        api_id, api_hash = get_keys()
        self.client = client or Client(
            "py-tgcalls",
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
        )
        self.call_py = PyTgCalls(self.client)

    async def call(self, user_id: int, stream: str) -> str | Exception:
        """Telegram üzerinden pyrogram client ile özelden arama yapar.

        Args:
            user_id (int): Aranacak kullanıcının ID'si.
            stream (str): Çalınacak ses dosyasının URL'si ya da yolu.

        Raises:
            CallDeclined: Arama reddedildiğinde.

        Notes:
            İki tarafında birbiri için P2P gizlilik ayarlarını açmış olması gerekir.
            (Eşler arası gizlilik ayarları: Her iki tarafında birbirlerini aramasına izin vermelidir.)

        Returns:
            str | Exception: Arama sonucu.

        Examples:
            .. code-block:: python

                async def main():
                    call = PrivateCall()
                    await call.call(123456789, test_stream="http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4")

                asyncio.run(main())
        """
        try:
            await self.call_py.play(
                user_id,
                MediaStream(
                    stream,
                ),
            )
        except CallDeclined:
            return "Arama reddedildi."

        except CallDiscarded:
            return "Arama iptal edildi."

        except NotInCallError:
            return "Userbot Aramada değil."

        except ClientNotStarted:
            return "Userbot başlatılmadı."

        except Exception as e:
            return e

    async def hangup(self, user_id: int):
        """Özelden yapılan aramayı sonlandırır.

        Args:
            user_id (int): Aranan kullanıcının ID'si.
        """
        try:
            await self.call_py.leave_call(user_id)
        except NotInCallError:
            return "Userbot Aramada değil."

        except ClientNotStarted:
            return "Userbot başlatılmadı."

        except Exception as e:
            return e
