import traceback
from typing import Any, Dict, Union

import aiohttp

from ._static import Static


class Paste(Static):
    def __init__(self):
        self.paste_url = "http://basicbots.pw:7070/create_paste/"
        self.get_paste_url = "http://basicbots.pw:7070/get_paste/"
        self.headers = {"Content-Type": "application/json"}

    async def paste(
        self,
        content: str,
        language: str = "python",
        paste_by: str = "",
        title: str = "",
        return_url: bool = True,
        trace: bool = False,
    ) -> Union[str, None, Exception]:
        payload = {
            "content": content,
            "language": language,
            "paste_by": paste_by,
            "title": title,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.paste_url, json=payload, headers=self.headers
                ) as response:
                    paste_id = (await response.json())["paste_id"]
                    payload["id"] = paste_id
                    self.custom_json = {"source": self.paste_url, "data": [payload]}
                    if return_url:
                        return f"http://basicbots.pw:7070/get_paste/{paste_id}"
                    return paste_id
        except Exception as e:
            trace = traceback.format_exc()
            self.custom_json = {
                "source": self.paste_url,
                "data": [{"error": str(e), "trace": trace}],
            }
            if trace:
                return trace
            return e

    async def get_paste(
        self, paste_id: str, trace: bool = False
    ) -> Union[Dict[str, Any], None, Exception]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.get_paste_url}{paste_id}") as response:
                    data = await response.json()
                    data["id"] = paste_id
                    self.custom_json = {"source": self.get_paste_url, "data": [data]}
                    return data
        except Exception as e:
            trace = traceback.format_exc()
            self.custom_json = {
                "source": self.get_paste_url,
                "data": [{"error": str(e), "trace": trace}],
            }
            if trace:
                return trace
            return e
