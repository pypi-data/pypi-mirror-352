import math
import time

from pyrogram.types import Message

from aylak.tools.human import HumanTools


async def progress_bar(
    current: int,
    total: int,
    message: Message,
    start: float,
    title: str = None,
    download_or_upload: str = "download",
):
    """Mevcut ilerlemeyi ve yüzdeyi içeren bir ilerleme çubuğu mesajı düzenler.

    Args:
        current (int): Mevcut ilerleme.
        total (int): Toplam ilerleme.
        message (Message): İlerleme çubuğu mesajı.
        start (float): İlerleme çubuğunun başlangıç zamanı.
        title (str): İlerleme çubuğunun başlığı.
        download_or_upload (str, optional): İndirme veya yükleme durumu. Defaults to "download".
    """
    now = time.time()
    diff = now - start
    human = HumanTools()
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = human.TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = human.TimeFormatter(milliseconds=estimated_total_time)

        progress = "__**İlerleme :**__ `[{0}{1}] {2}%`\n".format(
            "".join(["●" for i in range(math.floor(percentage / 5))]),
            "".join([" " for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )

        tmp = (
            progress
            + "__**{d_or_u} :**__ {current} / {total}\n__**Hız :**__ {speed}/s\n__**ETA :**__ {eta}\n".format(
                d_or_u="İndirme" if download_or_upload == "download" else "Yükleme",
                current=human.humanbytes(current, precision=3),
                total=human.humanbytes(total, precision=3),
                speed=human.humanbytes(speed, precision=3),
                # elapsed_time if elapsed_time != '' else "0 s",
                eta=estimated_total_time if estimated_total_time != "" else "0 s",
            )
        )
        try:
            await message.edit(
                text=(
                    f"__**Dosya {'indiriliyor' if download_or_upload == 'download' else 'yükleniyor'} :**__ __{title}__\n"
                    if title
                    else ""
                )
                + f"{tmp}"
            )
        except:
            pass
