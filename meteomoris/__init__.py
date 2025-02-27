# print('meteomoris ~')

from .meteo import Meteo

get_weekforecast = Meteo.get_weekforecast
get_cityforecast = Meteo.get_cityforecast
get_moonphase = Meteo.get_moonphase
get_main_message = Meteo.get_main_message
get_special_weather_bulletin = Meteo.get_special_weather_bulletin
get_eclipse_text = Meteo.get_eclipse_text
test = Meteo.test
get_sunrisemu = Meteo.get_sunrisemu
get_sunriserodr = Meteo.get_sunriserodr
get_eclipses = Meteo.get_eclipses
get_equinoxes = Meteo.get_equinoxes
get_solstices = Meteo.get_solstices
get_tides = Meteo.get_tides
get_latest = Meteo.get_latest
get_uvindex = Meteo.get_uvindex

get_today_forecast = Meteo.get_today_forecast
get_today_sunrise = Meteo.get_today_sunrise
get_today_eclipse = Meteo.get_today_eclipse
get_today_moonphase = Meteo.get_today_moonphase
get_today_solstice = Meteo.get_today_solstice
get_today_equinox = Meteo.get_today_equinox
get_today_tides = Meteo.get_today_tides

__version__ = "2.12.3"
