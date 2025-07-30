from .bimaktuel import BimAktuel
from .cleaner import Cleaner
from .doviz import Doviz
from .fueloil import FuelOil
from .havadurumu import HavaDurumu
from .human import HumanTools
from .kripto import Kripto
from .masal import Masal
from .nobetcieczane import NobetciEczane
from .paste import Paste
from .qrcode import QRCode
from .sondepremler import SonDepremler
from .udemy import Udemy
from .weather import Weather
from .youtube import YouTube


class Tools(
    BimAktuel,
    Cleaner,
    Doviz,
    FuelOil,
    HavaDurumu,
    HumanTools,
    Kripto,
    Masal,
    NobetciEczane,
    Paste,
    SonDepremler,
    Udemy,
    Weather,
    YouTube,
):
    pass
