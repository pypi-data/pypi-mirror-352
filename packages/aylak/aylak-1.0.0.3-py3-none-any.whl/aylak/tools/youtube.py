from pytube import YouTube as PyTube
import asyncio
from ._static import Static
from aylak.tools import HumanTools


class YouTube(Static):
    def __init__(self):
        self.source = "Youtube.com"
        self.human = HumanTools()

    async def youtube(self, yt_url: str):
        def _youtube():
            yt = PyTube(yt_url)
            video = yt.streams.get_highest_resolution()

            data = {
                "sahip": yt.author,
                "baslik": yt.title,
                "sure": self.human.TimeFormatter(yt.length * 1000),
                "tarih": str(yt.publish_date.strftime("%d-%m-%Y")),
                "izlenme": yt.views,
                "resim": yt.thumbnail_url,
                "aciklama": yt.description,
                "kalite": video.resolution if video else None,
                "boyut": self.human.humanbytes(video.filesize) if video else None,
                "url": video.url if video else None,
            }

            custom_json = {"source": self.source, "data": [data]}

            self.custom_json = custom_json if custom_json["data"] != [] else None
            return self.custom_json

        return await asyncio.get_event_loop().run_in_executor(None, _youtube)
