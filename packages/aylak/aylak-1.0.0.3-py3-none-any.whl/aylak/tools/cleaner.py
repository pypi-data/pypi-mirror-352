# İsmi ve türü verilen (klasör/dosya)yı ana alt klasörden ve alt klasörlerinden siler.

import os
import shutil
from typing import List, Tuple, Union

from ._static import Static


class Cleaner(Static):
    def __init__(self) -> None:
        self.deleted = []
        self.failed = []
        pass

    async def clean(
        self,
        path: str = os.getcwd(),
        name: str = "__pycache__",
        type: str = "folder",
        print_it: bool = True,
    ) -> Union[Tuple[List[str], None], Tuple[List[str], List[Tuple[str, Exception]]]]:
        """_summary_

        Args:
            path (`str`, optional): Temizlik yapılacak klasör. Varsayılan olarak mevcut path değerine (*os.getcwd()*) eşittir.
            name (`str`, optional): Silinecek klasör/dosyanın ismi. Varsayılan olarak *__pycache__* klasörünü siler.
            type (`str`, optional): Silinecek verinin türü. (`folder`/`file`) Varsayılan olarak *folder* değerine eşittir.
            print_it (`bool`, optional): Silme işlemi sırasında çıktı alınsın mı? Varsayılan olarak *True* değerine eşittir.

        Returns:
            deleteds (`List[str]`): Silinen klasör/dosya isimleri.
            faileds (`List[Tuple[str, Exception]]` | `None`): Silinmeyen klasör/dosya isimleri ve hatalar. Eğer hiçbir hata oluşmamışsa *None* döner.
        """

        if type == "folder":
            for folder in os.listdir(path):
                if folder == name:
                    try:
                        shutil.rmtree(os.path.join(path, folder))
                        if print_it:
                            print(f"{folder} klasörü başarıyla silindi!")
                        else:
                            self.deleted.append(os.path.join(path, folder))
                    except Exception as error:
                        if print_it:
                            print(f"{folder} klasörü silinemedi!\nHata: {error}")
                        else:
                            self.failed.append((os.path.join(path, folder), error))

            for folder in os.listdir(path):
                if os.path.isdir(os.path.join(path, folder)):
                    await self.clean(os.path.join(path, folder), name, type, print_it)

        elif type == "file":
            for file in os.listdir(path):
                if file == name:
                    try:
                        os.remove(os.path.join(path, file))
                        if print_it:
                            print(f"{file} dosyası başarıyla silindi!")
                        else:
                            self.deleted.append(file)
                    except Exception as error:
                        if print_it:
                            print(f"{file} dosyası silinemedi!\nHata: {error}")
                        else:
                            self.failed.append((file, error))

            for folder in os.listdir(path):
                if os.path.isdir(os.path.join(path, folder)):
                    await self.clean(os.path.join(path, folder), name, type, print_it)
        else:
            raise ValueError("type argümanı 'folder' veya 'file' olmalıdır!")

        if len(self.failed) == 0:
            return self.deleted, None
        self.custom_json = {
            "source": "cleaner",
            "path": path,
            "name": name,
            "type": type,
            "data": [self.deleted, self.failed],
        }
        return self.deleted, self.failed

 