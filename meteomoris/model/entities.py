from collections import namedtuple

Region = namedtuple("Region", ["name", "display_name"])


class Result:
    def __init__(self, success, data=None, error=None, errors=None,
                 from_stale_cache=False, warnings=None):
        self.success = success
        self.data = data
        self.error = error
        self.errors = errors or []
        self.from_stale_cache = from_stale_cache
        self.warnings = warnings or []

    def to_dict(self):
        return self.data


class Forecast:
    def __init__(self, day, date, condition, min_temp, max_temp, wind,
                 sea_condition="", probability=""):
        self.day = day
        self.date = date
        self.condition = condition
        self.min = min_temp
        self.max = max_temp
        self.wind = wind
        self.sea_condition = sea_condition
        self.probability = probability

    def to_dict(self):
        return {
            "day": self.day,
            "date": self.date,
            "condition": self.condition,
            "min": self.min,
            "max": self.max,
            "wind": self.wind,
            "sea condition": self.sea_condition,
            "probability": self.probability,
        }


class CityForecast:
    def __init__(self, day, date, condition, min_temp, max_temp, wind):
        self.day = day
        self.date = date
        self.condition = condition
        self.min = min_temp
        self.max = max_temp
        self.wind = wind

    def to_dict(self):
        return {
            "day": self.day,
            "date": self.date,
            "condition": self.condition,
            "min": self.min,
            "max": self.max,
            "wind": self.wind,
        }


class SunInfo:
    def __init__(self, rise, set):
        self.rise = rise
        self.set = set

    def to_dict(self):
        return {"rise": self.rise, "set": self.set}


class MoonInfo:
    def __init__(self, rise, set):
        self.rise = rise
        self.set = set

    def to_dict(self):
        return {"rise": self.rise, "set": self.set}


class MoonPhaseEntry:
    def __init__(self, date, hour, minute):
        self.date = date
        self.hour = hour
        self.minute = minute

    def to_dict(self):
        return {"date": self.date, "hour": self.hour, "minute": self.minute}


class Eclipse:
    def __init__(self, status, type, start, end, info, title):
        self.status = status
        self.type = type
        self.start = start
        self.end = end
        self.info = info
        self.title = title

    def to_dict(self):
        return {
            "status": self.status,
            "type": self.type,
            "start": self.start,
            "end": self.end,
            "info": self.info,
            "title": self.title,
        }


class Equinox:
    def __init__(self, day, month, year, hour, minute):
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute

    def to_dict(self):
        return {"day": self.day, "month": self.month, "year": self.year,
                "hour": self.hour, "minute": self.minute}


class Solstice:
    def __init__(self, day, month, year, hour, minute):
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute

    def to_dict(self):
        return {"day": self.day, "month": self.month, "year": self.year,
                "hour": self.hour, "minute": self.minute}


class TideData:
    def __init__(self, months, month_format, meta):
        self.months = months
        self.month_format = month_format
        self.meta = meta

    def to_dict(self):
        return {
            "months": self.months,
            "month_format": self.month_format,
            "meta": self.meta,
        }


class UVIndexData:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return dict(self.data)


class LatestData:
    def __init__(self, rainfall24h, rainfall3hrs, wind, humidity, minmaxtemp):
        self.rainfall24h = rainfall24h
        self.rainfall3hrs = rainfall3hrs
        self.wind = wind
        self.humidity = humidity
        self.minmaxtemp = minmaxtemp

    def to_dict(self):
        return {
            "rainfall24h": self.rainfall24h,
            "rainfall3hrs": self.rainfall3hrs,
            "wind": self.wind,
            "humidity": self.humidity,
            "minmaxtemp": self.minmaxtemp,
        }


class Rainfall:
    def __init__(self, info, data):
        self.info = info
        self.data = data

    def to_dict(self):
        return {"info": self.info, "data": self.data}


class MainMessage:
    def __init__(self, text, links=None):
        self.text = text
        self.links = links or []

    def to_dict(self):
        return {"text": self.text, "links": self.links}
