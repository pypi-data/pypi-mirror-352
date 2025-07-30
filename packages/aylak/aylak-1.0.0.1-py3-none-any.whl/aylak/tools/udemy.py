import requests, asyncio
from bs4 import BeautifulSoup
from ._static import Static


class Udemy(Static):

    def __init__(self):
        self.source = "discudemy.com"

    async def kurslar(self, category: str):
        def _kurslar():
            response = requests.get(
                f"https://www.{self.source}/s-r/{category}.jsf",
                headers=self.kimlik,
                allow_redirects=True,
            )
            soup = BeautifulSoup(response.content, "lxml")

            udemy = []
            for one in soup.findAll("section", class_="card"):
                language = one.find("label", class_="ui green disc-fee label")
                if language.text.lower() == "ads":
                    continue
                title = one.find("div", class_="header")
                disc_response = requests.get(
                    f"https://www.{self.source}/go/{title.a['href'].split('/')[-1]}"
                )
                disc_coup = BeautifulSoup(disc_response.content, "lxml")

                try:
                    url = disc_coup.select(
                        "body > div.ui.container.mt10 > div:nth-child(3) > div > a"
                    )[0]["href"]
                except IndexError:
                    continue

                udemy.append(
                    {
                        "language": language.text,
                        "title": title.text.strip(),
                        "url": url,
                    }
                )
            custom_json = {"source": self.source, "data": udemy}
            self.custom_json = custom_json if custom_json["data"] != [] else None
            return self.custom_json

        return await asyncio.get_event_loop().run_in_executor(None, _kurslar)
