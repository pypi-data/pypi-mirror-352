import time
from gtts import gTTS
import random
import asyncio

import speech_recognition as sp
import traceback
import speech_recognition as sp

from urllib.parse import urlencode
import json

from speech_recognition import UnknownValueError, RequestError
import aiohttp, asyncio
from aylak.voice.convert import Convert


class Speech:
    def __init__(self):
        self.recognizer = sp.Recognizer()
        # self.recognizer.recognize_google = recognize_google  # Async function
        self.converter = Convert()
        pass

    async def tts(
        self,
        tts_text: str,
        file_name: str = None,
        lang: str = "tr",
    ) -> str:
        """Verilen metni ses dosyasına çevirir ve dosya adını döndürür.

        Args:
            tts_text (`str`): Ses dosyasına çevrilecek metin.
            file_name (`str`, optional): Ses dosyasının adı. Defaults to None.
            lang (`str`, optional): Ses dosyasının dili. Defaults to "tr".

        Returns:
            str: Ses dosyasının adı.
        """

        def _tts(tts_text: str, file_name: str = None, lang: str = "tr"):
            tts = gTTS(tts_text, lang=lang)
            rand = random.randint(1, 10000)
            file = (
                "audio-" + str(rand) + ".mp3"
                if file_name is None
                else (file_name if file_name.endswith(".mp3") else file_name + ".mp3")
            )
            tts.save(file)
            return file

        return await asyncio.to_thread(_tts, tts_text, file_name, lang)

    async def stt(
        self,
        audio_file: str,
        lang: str = "tr-TR",
        force_convert: bool = True,
        record_interval: bool = False,
    ) -> str:
        """Verilen ses dosyasındaki metni döndürür.

        Args:
            audio_file (`str`): Ses dosyasının adı.
            lang (`str`, optional): Ses dosyasının dili. Defaults to "tr".

        Returns:
            str: Ses dosyasındaki metin.
        """
        # eğer ses dosyası WAV formatında değilse, WAV formatına dönüştürülür.
        if record_interval:
            start_time = time.time()

        format = audio_file.split(".")[-1]
        if format != "wav" and format.upper() not in self.converter.formats:
            raise ValueError(f"{format} formatı desteklenmiyor.")

        elif format != "wav" and force_convert:
            audio_file = await self.converter.convert(
                audio_file, audio_file.replace(format, "wav")
            )

        with sp.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio, language=lang)
            trace = None
        except sp.UnknownValueError:
            text = None
            trace = traceback.format_exc()

        except sp.RequestError as e:
            text = e
            trace = traceback.format_exc()

        except Exception as e:
            text = e
            trace = traceback.format_exc()

        if record_interval:
            end_time = time.time()
            print(f"Recording time: {end_time - start_time}")

        return text, trace


async def recognize_google(
    audio_data,
    key=None,
    language="tr-TR",
    pfilter=0,
    show_all=False,
    with_confidence=False,
):
    assert isinstance(
        audio_data, sp.audio.AudioData
    ), "``audio_data`` must be audio data"
    assert key is None or isinstance(key, str), "``key`` must be ``None`` or a string"
    assert isinstance(language, str), "``language`` must be a string"

    flac_data = audio_data.get_flac_data(
        convert_rate=(
            None if audio_data.sample_rate >= 8000 else 8000
        ),  # audio samples must be at least 8 kHz
        convert_width=2,  # audio samples must be 16-bit
    )
    if key is None:
        key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
    url = "http://www.google.com/speech-api/v2/recognize?{}".format(
        urlencode(
            {"client": "chromium", "lang": language, "key": key, "pFilter": pfilter}
        )
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=flac_data,
                headers={
                    "Content-Type": "audio/x-flac; rate={}".format(
                        audio_data.sample_rate
                    )
                },
            ) as response:
                response_text = await response.text()
    except Exception as e:
        raise RequestError("recognition connection failed: {}".format(e))

    # ignore any blank blocks
    actual_result = []
    for line in response_text.split("\n"):
        if not line:
            continue
        result = json.loads(line)["result"]
        if len(result) != 0:
            actual_result = result[0]
            break

    # return results
    if show_all:
        return actual_result

    if (
        not isinstance(actual_result, dict)
        or len(actual_result.get("alternative", [])) == 0
    ):
        raise UnknownValueError()

    if "confidence" in actual_result["alternative"]:
        # return alternative with highest confidence score
        best_hypothesis = max(
            actual_result["alternative"],
            key=lambda alternative: alternative["confidence"],
        )
    else:
        # Güven olmadığında, ilk hipotezi keyfi olarak seçeriz.
        best_hypothesis = actual_result["alternative"][0]
    if "transcript" not in best_hypothesis:
        raise UnknownValueError()
    confidence = best_hypothesis.get("confidence", 0.5)
    if with_confidence:
        return best_hypothesis["transcript"], confidence
    return best_hypothesis["transcript"]
