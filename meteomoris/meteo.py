try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except Exception:
    pass

import sys
import datetime
import calendar
import os


def cache_path():
    return os.path.join(".", "meteomoris_cache.json")


def _to_dict(obj):
    from .model.entities import Result
    if isinstance(obj, Result):
        if not obj.success and obj.data is None:
            return None
        obj = obj.data
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, list):
        return [_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj


def _sun_dict(data, month, day):
    entry = data.get(month, {}).get(str(day))
    if entry is None:
        entry = data.get(month, {}).get(day)
    if entry:
        return _to_dict(entry)
    return {}


class Meteo:
    ALREADY_CHECKED_INTERNET = False
    EXIT_ON_NO_INTERNET = True
    CHECK_INTERNET = True
    DEBUG = False
    CACHE_PERMS = True
    CACHE_PATH = cache_path()
    MAX_RETRIES = 3
    FETCH_TIMEOUT = 30
    ABORT_ON_NO_INTERNET = False

    today = str(datetime.date.today())

    try:
        console = Console()
        print = console.print
    except:
        pass

    @classmethod
    def _dispatch(cls, *args, **kwargs):
        from .fsm.dispatch import FSMDispatch
        return FSMDispatch()

    @classmethod
    def verify_cache_exists(cls):
        from .behavior.cache import Cache
        c = Cache()
        cls.CACHE_PERMS = c.enabled

    @classmethod
    def get_cache_data(cls):
        from .behavior.cache import Cache
        c = Cache()
        return c._get_cache_data()

    @classmethod
    def get_from_cache(cls, key):
        from .behavior.cache import Cache
        c = Cache()
        return c.get(key)

    @classmethod
    def add_to_cache(cls, key, data):
        from .behavior.cache import Cache
        c = Cache()
        c.set(key, data)

    @classmethod
    def internet_present(cls):
        from .behavior.fetcher import InternetChecker
        ic = InternetChecker()
        return ic.internet_present()

    @classmethod
    def check_internet(cls):
        from .behavior.fetcher import InternetChecker
        ic = InternetChecker(
            check_internet=cls.CHECK_INTERNET,
            exit_on_no_internet=cls.EXIT_ON_NO_INTERNET,
        )
        return ic.is_online()

    @classmethod
    def get_weekforecast(cls, day=None, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("weekforecast", print_output=print, day=day)
        result = _to_dict(data)
        if day is not None and isinstance(result, list) and len(result) > day:
            return result[day]
        return result

    @classmethod
    def get_cityforecast(cls, print=False, day=None):
        dispatch = cls._dispatch()
        data = dispatch.execute("cityforecast", print_output=print, day=day)
        result = _to_dict(data)
        if day is not None and isinstance(result, list) and len(result) > day:
            return result[day]
        return result

    @classmethod
    def get_moonphase(cls, print=False, month=None):
        dispatch = cls._dispatch()
        data = dispatch.execute("moonphase", print_output=print, month=month)
        result = _to_dict(data)
        if month is not None:
            return result.get(month, result)
        return result

    @classmethod
    def get_main_message(cls, print_=False, links=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("main_message", print_output=print_, links=links)
        result = _to_dict(data)
        if isinstance(result, dict):
            if links:
                return result.get("links", [])
            return result.get("text", "")
        return result

    @classmethod
    def get_special_weather_bulletin(cls, print=False):
        dispatch = cls._dispatch()
        return dispatch.execute("special_bulletin", print_output=print)

    @classmethod
    def get_eclipse_text(cls):
        dispatch = cls._dispatch()
        return dispatch.execute("eclipse_text")

    @classmethod
    def test(cls):
        print("test ok")

    @classmethod
    def get_sunrisemu(cls, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("sunrisemu", print_output=print)
        return _to_dict(data)

    @classmethod
    def get_sunriserodr(cls, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("sunriserodr", print_output=print)
        return _to_dict(data)

    @classmethod
    def get_moonrisemu(cls, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("moonrisemu", print_output=print)
        return _to_dict(data)

    @classmethod
    def get_moonriserodr(cls, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("moonriserodr", print_output=print)
        return _to_dict(data)

    @classmethod
    def get_eclipses(cls):
        dispatch = cls._dispatch()
        data = dispatch.execute("eclipses")
        return _to_dict(data)

    @classmethod
    def get_eclipse_html(cls):
        from .behavior.cache import Cache
        c = Cache()
        cached = c.get("eclipse_html")
        if cached:
            return cached
        from .behavior.fetcher import Fetcher
        f = Fetcher()
        response = f.fetch(
            "http://metservice.intnet.mu/sun-moon-and-tides-info-eclipses.php"
        )
        if response is not None:
            return response.text
        return None

    @classmethod
    def parse_time_string(cls, time_str):
        from .behavior.parser import Parser
        return Parser.parse_time_string(time_str)

    @classmethod
    def get_equinoxes(cls):
        dispatch = cls._dispatch()
        data = dispatch.execute("equinoxes")
        return _to_dict(data)

    @classmethod
    def get_solstices(cls):
        dispatch = cls._dispatch()
        data = dispatch.execute("solstices")
        return _to_dict(data)

    @classmethod
    def get_today_moonphase(cls):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        year = datetime.datetime.now().year

        try:
            dispatch = cls._dispatch()
            moonphase = dispatch.execute("moonphase")
            moonphase = _to_dict(moonphase)
            moonphase = moonphase.get("{} {}".format(month, year), {})
        except Exception:
            return {}

        for phase in moonphase:
            entry = moonphase[phase]
            if isinstance(entry, dict) and entry.get("date") == day:
                return {
                    "title": phase,
                    "hour": entry.get("hour"),
                    "minute": entry.get("minute"),
                }
        return {}

    @classmethod
    def get_today_eclipse(cls):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        info = {}
        eclipses = cls.get_eclipses()
        if not isinstance(eclipses, list):
            return info
        for eclipse in eclipses:
            start = eclipse.get("start") if isinstance(eclipse, dict) else {}
            end = eclipse.get("end") if isinstance(eclipse, dict) else {}
            if start and start.get("date") == day and start.get("month") == month:
                info["start"] = eclipse
            if end and end.get("date") == day and end.get("month") == month:
                info["end"] = eclipse
        return info

    @classmethod
    def get_today_solstice(cls):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        for solstice in cls.get_solstices():
            if isinstance(solstice, dict):
                if solstice.get("day") == day and solstice.get("month") == month:
                    return solstice
        return {}

    @classmethod
    def get_today_equinox(cls):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        for equinox in cls.get_equinoxes():
            if isinstance(equinox, dict):
                if equinox.get("day") == day and equinox.get("month") == month:
                    return equinox
        return {}

    @classmethod
    def get_today_sunrise(cls, country):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        if country == "mu":
            sunrise = cls.get_sunrisemu()
        elif country == "rodr":
            sunrise = cls.get_sunriserodr()
        else:
            raise ValueError("Unexpected country: {}".format(country))
        result = _sun_dict(sunrise, month, day)
        if not result:
            result = _sun_dict(sunrise, month, str(day))
        return result

    @classmethod
    def get_today_forecast(cls):
        return cls.get_weekforecast(day=0)

    @classmethod
    def get_today_tides(cls):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        tides_all = _to_dict(cls.get_tides())
        month_data = tides_all.get("months", {}).get(month, {})
        if str(day) in month_data:
            return month_data[str(day)]
        if day in month_data:
            return month_data[day]
        return []

    @classmethod
    def print_today(cls, country="mu"):
        if cls.EXIT_ON_NO_INTERNET and cls.CHECK_INTERNET:
            if not cls.internet_present():
                cls.print("[red]No internet connection[/red]")
                return
        with cls.console.status("fetching", spinner="aesthetic"):
            if country not in ["mu", "rodr"]:
                cls.print("[red]Country should be mu or rodr[/red]")
                return

            day = datetime.datetime.now().day
            month = calendar.month_name[datetime.datetime.now().month].casefold()
            year = datetime.datetime.now().year

            forecast = cls.get_today_forecast()
            sun = cls.get_today_sunrise(country)
            today_moonphase = cls.get_today_moonphase()
            eclipse_today = cls.get_today_eclipse()
            equinox = cls.get_today_equinox()
            solstice = cls.get_today_solstice()
            uv_data = _to_dict(cls.get_uvindex())
            tides = cls.get_today_tides()
            latest = cls.get_latest()
            message_links = cls.get_main_message(links=True)

            moonphase_string = ""
            if today_moonphase:
                moonphase_string = "{} today at [green]{}:{}[/green]".format(
                    today_moonphase.get("title", "").title(),
                    today_moonphase.get("hour", ""),
                    today_moonphase.get("minute", ""),
                )

            eclipse_elements = []
            if eclipse_today:
                if "start" in eclipse_today:
                    es = eclipse_today["start"]
                    eclipse_elements.extend([
                        es.get("title", ""),
                        "starts today at",
                        "[green]{}:{}[/green]".format(
                            es.get("start", {}).get("hour", ""),
                            es.get("start", {}).get("minute", ""),
                        ),
                        es.get("info", ""),
                    ])
                if "end" in eclipse_today:
                    ee = eclipse_today["end"]
                    eclipse_elements.extend([
                        "\n",
                        ee.get("title", ""),
                        "ends today at",
                        "[green]{}:{}[/green]".format(
                            ee.get("end", {}).get("hour", ""),
                            ee.get("end", {}).get("minute", ""),
                        ),
                        ee.get("info", ""),
                    ])
            eclipse_string = " ".join(eclipse_elements).replace("\n ", "\n")

            equinox_string = ""
            if equinox:
                equinox_string = "Equinox today at [green]{}:{}[/green]".format(
                    equinox.get("hour", ""), equinox.get("minute", "")
                )

            solstice_string = ""
            if solstice:
                solstice_string = "Solstice today at [green]{}:{}[/green]".format(
                    solstice.get("hour", ""), solstice.get("minute", "")
                )

            uv_string = ""
            if isinstance(uv_data, dict):
                for region, status in uv_data.items():
                    region_display = region.replace("-", " ").capitalize()
                    if status.lower() == "extreme":
                        status_display = "[blink]:fire: [red]{}[/red][/blink]".format(status)
                    elif status.lower() == "very high":
                        status_display = "[red]{}[/red]".format(status)
                    elif status.lower() == "high":
                        status_display = "[dark_orange3]{}[/dark_orange3]".format(status)
                    elif status.lower() in ("medium", "moderate"):
                        status_display = "[gold3]{}[/gold3]".format(status)
                    elif status.lower() == "low":
                        status_display = "[green]{}[/green]".format(status)
                    else:
                        status_display = status
                    uv_string += "[magenta]{}[/magenta]: {}\n".format(region_display, status_display)
            uv_string = uv_string.strip("\n")

            temp_str = "Min: {}C [b]\tMax: {}C[/b]".format(
                forecast.get("min", ""), forecast.get("max", "")
            )
            temp_panel = Panel(temp_str, expand=True, title="Temperature")
            wind_panel = Panel(forecast.get("wind", ""), expand=True, title="Wind")
            sea_panel = Panel(forecast.get("sea condition", ""), expand=True, title="Sea condition")
            solstice_panel = Panel(solstice_string, expand=True, title="Solstice")
            equinox_panel = Panel(equinox_string, expand=True, title="Equinox")
            eclipse_panel = Panel(eclipse_string, expand=True, title="Eclipse")
            uv_panel = Panel(uv_string, expand=True, title="UV Index")
            moonphase_panel = Panel(moonphase_string, expand=True, title="Moon phase")
            condition_panel = Panel(forecast.get("condition", ""), expand=True, title="Condition")
            sun_panel = Panel(
                "[gold3]Sunrise: {}[/gold3]\t[red]Sunset: {}[/red]".format(
                    sun.get("rise", ""), sun.get("set", "")
                ),
                expand=True,
                title="Sun",
            )

            messages = ["[bold]{}[/bold]  {}".format(l[0], l[1]) for l in message_links]
            message_panel = Panel("\n".join(messages), expand=True, title="Message")

            tidetable = Table()
            tidetable.add_column("Tide", justify="left", style="slate_blue3", no_wrap=True)
            tidetable.add_column("Time", justify="left", style="gold3", no_wrap=True)
            tidetable.add_column("Height (cm)", style="dark_cyan")
            if isinstance(tides, list) and len(tides) >= 8:
                tidetable.add_row("1st high", tides[0], tides[1])
                tidetable.add_row("2nd high", tides[2], tides[3])
                tidetable.add_row("1st low", tides[4], tides[5])
                tidetable.add_row("2nd low", tides[6], tides[7])
            tides_panel = Panel(tidetable, expand=True, title="Tides")

            latest_dict = _to_dict(latest) if hasattr(latest, 'to_dict') else (latest or {})
            rainfall = latest_dict.get("rainfall24h", {})
            rtable = Table()
            rtable.add_column("Region", justify="left", style="slate_blue3")
            rtable.add_column("Rain 24hr", style="dark_cyan")
            rtable.add_column("Rain 3hrs", style="dark_cyan")
            rtable.add_column("Wind", style="dark_cyan")
            rtable.add_column("Humidity", style="dark_cyan")
            rtable.add_column("Min Max temp", style="dark_cyan")
            rainfall3hrs = latest_dict.get("rainfall3hrs", {}).get("data", {})
            wind_data = latest_dict.get("wind", {}).get("data", {})
            humidity_data = latest_dict.get("humidity", {}).get("data", {})
            minmaxtemp_data = latest_dict.get("minmaxtemp", {}).get("data", {})
            for r, a in rainfall.get("data", {}).items():
                mmt = minmaxtemp_data.get(r, {})
                if mmt.get("min") or mmt.get("max"):
                    minmaxtemp_str = "{} to {}".format(mmt.get("min", ""), mmt.get("max", ""))
                else:
                    minmaxtemp_str = ""
                rtable.add_row(
                    r, a, rainfall3hrs.get(r, ""), wind_data.get(r, ""),
                    humidity_data.get(r, ""), minmaxtemp_str,
                )
            titles_str = "".join(["- {}\n".format(v.get("info", "")) for v in latest_dict.values()])
            rtable.title = titles_str
            latest_panel = Panel(rtable, expand=True, title="Latest data")

            grid = Table.grid()
            grid.add_column()
            grid.add_column()

            def add_row(grid, elements):
                try:
                    grid.add_row(*elements)
                except Exception:
                    pass

            ltable = Table(box=None, show_header=False)
            ltable.add_column()
            ltable.add_row(temp_panel)
            ltable.add_row(wind_panel)
            ltable.add_row(sea_panel)
            ltable.add_row(sun_panel)
            ltable.add_row(uv_panel)
            ltable.add_row(tides_panel)
            ltable.add_row(moonphase_panel)

            rtable_inner = Table(box=None, show_header=False)
            rtable_inner.add_column()
            rtable_inner.add_row(message_panel)
            rtable_inner.add_row(condition_panel)
            rtable_inner.add_row(latest_panel)
            rtable_inner.add_row(equinox_panel)
            rtable_inner.add_row(solstice_panel)
            rtable_inner.add_row(eclipse_panel)

            add_row(grid, [ltable, rtable_inner])
            cls.print(Panel(grid, expand=True, title="Today"))

    @classmethod
    def get_tides(cls, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("tides", print_output=print)
        return _to_dict(data)

    @classmethod
    def get_rainfall(cls, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("rainfall", print_output=print)
        return _to_dict(data)

    @classmethod
    def get_latest(cls, print=False):
        dispatch = cls._dispatch()
        data = dispatch.execute("latest", print_output=print)
        return _to_dict(data)

    @classmethod
    def get_uvindex(cls, print=False):
        from .behavior.cache import Cache
        from .behavior.fetcher import Fetcher
        from .behavior.parser import Parser
        from .behavior.renderer import Renderer

        regions = [
            "vacoas", "port-louis", "plaisance", "triolet",
            "camp-diable", "centre-de-flacq", "flic-en-flac",
            "tamarin", "rodrigues",
        ]

        cache = Cache()
        cached = cache.get("uvindex")
        if cached is not None:
            data = cached
        else:
            fetcher = Fetcher()
            parser = Parser()
            htmls = {}
            for region in regions:
                url = "https://en.tutiempo.net/ultraviolet-index/{}.html".format(region)
                html = fetcher.fetch_html(url)
                if html:
                    htmls[region] = html
            parsed = parser.parse_uvindex(htmls)
            data = parsed.to_dict()
            cache.set("uvindex", data)

        if print:
            renderer = Renderer()
            renderer.render_uvindex(data)
            return
        return data
