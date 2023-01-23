# print('meteomoris ~')

from .meteo import Meteo

get_weekforecast = Meteo.get_weekforecast
get_cityforecast = Meteo.get_cityforecast
get_moonphase = Meteo.get_moonphase
get_main_message = Meteo.get_main_message
get_special_whether_bulletin = Meteo.get_special_whether_bulletin
get_eclipse_text = Meteo.get_eclipse_text
test = Meteo.test
get_sunrisemu = Meteo.get_sunrisemu
get_sunriserodr = Meteo.get_sunriserodr
get_eclipses_raw = Meteo.get_eclipses_raw
get_eclipses = Meteo.get_eclipses
get_equinoxes = Meteo.get_equinoxes
get_solstices = Meteo.get_solstices

__version__ = "2.3.3"
