# print('meteomoris ~')

from .meteo import Meteo

get_weekforecast = Meteo.get_weekforecast
get_cityforecast = Meteo.get_cityforecast
get_moonphase = Meteo.get_moonphase
get_main_message = Meteo.get_main_message
get_eclipse_text = Meteo.get_eclipse_text
test = Meteo.test
get_sunrisemu = Meteo.get_sunrisemu
get_sunriserodr = Meteo.get_sunriserodr

__version__ = '2.0.0'