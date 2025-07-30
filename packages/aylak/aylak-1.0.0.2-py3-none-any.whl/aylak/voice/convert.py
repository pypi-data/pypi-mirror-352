from aylak.run import Run
import os

from typing import Optional, Union, Any, Dict, List, Tuple


class Convert:
    def __init__(self):
        self.run = Run()
        self.formats = ["WAV", "OGG", "MP3", "AAC", "FLAC"]

    async def check_ffmpeg(self):
        try:
            result, err, _ = await self.run.py.run_command("ffmpeg -version")
            if result and "ffmpeg version" in result:
                return True
            else:
                return False
        except Exception as e:
            return False

    async def convert(
        self,
        input_file: str,
        output_file: str,
        delete_input: bool = False,
    ) -> Union[str, Exception]:
        """Verilen ses dosyasını belirtilen formata dönüştürür.

        Args:
            input_file (str): Giriş ses dosyasının adı.
            output_file (str): Çıkış ses dosyasının adı.
            delete_input (bool, optional): Giriş dosyasını siler. Defaults to False.

        Raises:
            FileNotFoundError: Eğer giriş dosyası bulunamazsa.
            ValueError: Eğer dönüştürme işlemi desteklenmiyorsa.

        Returns:
            Union[str, Exception]: Dönüştürülen dosyanın adı.

        Examples:
            .. code-block:: python

                async def main():
                    output = await convert("input.wav", "output.mp3", delete_input=True)
                    print(output)

                asyncio.run(main())
        """
        #! FFMPEG
        if not await self.check_ffmpeg():
            raise Exception("FFMPEG is not installed.")

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"{input_file} not found.")

        input_format = input_file.split(".")[-1]
        output_format = output_file.split(".")[-1]

        commands = {
            "WAV": {
                "OGG": f"ffmpeg -i {input_file}.{input_format} {output_file}.ogg",
                "MP3": f"ffmpeg -i {input_file}.{input_format} -c:a mp3 {output_file}.mp3",
                "AAC": f"ffmpeg -i {input_file}.{input_format} -c:a aac {output_file}.aac",
                "FLAC": f"ffmpeg -i {input_file}.{input_format} {output_file}.flac",
            },
            "OGG": {
                "WAV": f"ffmpeg -i {input_file}.{input_format} {output_file}.wav",
                "MP3": f"ffmpeg -i {input_file}.{input_format} -c:a mp3 {output_file}.mp3",
                "AAC": f"ffmpeg -i {input_file}.{input_format} -c:a aac {output_file}.aac",
                "FLAC": f"ffmpeg -i {input_file}.{input_format} {output_file}.flac",
            },
            "MP3": {
                "WAV": f"ffmpeg -i {input_file}.{input_format} {output_file}.wav",
                "OGG": f"ffmpeg -i {input_file}.{input_format} -c:a libvorbis {output_file}.ogg",
                "AAC": f"ffmpeg -i {input_file}.{input_format} -c:a aac {output_file}.aac",
                "FLAC": f"ffmpeg -i {input_file}.{input_format} {output_file}.flac",
            },
            "AAC": {
                "WAV": f"ffmpeg -i {input_file}.{input_format} {output_file}.wav",
                "OGG": f"ffmpeg -i {input_file}.{input_format} -c:a libvorbis {output_file}.ogg",
                "MP3": f"ffmpeg -i {input_file}.{input_format} -c:a mp3 {output_file}.mp3",
                "FLAC": f"ffmpeg -i {input_file}.{input_format} {output_file}.flac",
            },
            "FLAC": {
                "WAV": f"ffmpeg -i {input_file}.{input_format} {output_file}.wav",
                "OGG": f"ffmpeg -i {input_file}.{input_format} {output_file}.ogg",
                "MP3": f"ffmpeg -i {input_file}.{input_format} -c:a mp3 {output_file}.mp3",
                "AAC": f"ffmpeg -i {input_file}.{input_format} -c:a aac {output_file}.aac",
            },
        }

        if (
            input_format.upper() in commands
            and output_format.upper() in commands[input_format.upper()]
        ):
            try:
                result, err, _ = await self.run.py.run_command(
                    commands[input_format.upper()][output_format.upper()]
                )
                if delete_input:
                    os.remove(input_file)
                return output_file
            except Exception as e:
                return e
        else:
            raise ValueError(
                f"Unsupported conversion from {input_format} to {output_format}."
            )
