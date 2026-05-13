from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class Renderer:
    def __init__(self):
        self.console = Console()
        self.print = self.console.print

    def render_weekforecast(self, data, day=None, **kwargs):
        table = Table(title="Week forecast" if day is None else "Day forecast")
        table.add_column("Day", justify="left", style="magenta", no_wrap=True)
        table.add_column("Date", justify="left", no_wrap=True)
        table.add_column("Min", justify="left", no_wrap=True)
        table.add_column("Max", justify="left", no_wrap=True)
        table.add_column("Condition", justify="left")
        table.add_column("Sea condition", justify="left")
        table.add_column("Wind", justify="left", no_wrap=True)
        table.add_column("Probability", justify="left")
        if day is None:
            for d in data:
                table.add_row(
                    d["day"] if isinstance(d, dict) else d.day,
                    d["date"] if isinstance(d, dict) else d.date,
                    d["min"] if isinstance(d, dict) else d.min,
                    d["max"] if isinstance(d, dict) else d.max,
                    d["condition"] if isinstance(d, dict) else d.condition,
                    d["sea condition"] if isinstance(d, dict) else d.sea_condition,
                    d["wind"] if isinstance(d, dict) else d.wind,
                    d["probability"] if isinstance(d, dict) else d.probability,
                )
        else:
            d = data[day] if isinstance(data, list) else data
            d = d if isinstance(d, dict) else d.to_dict()
            table.add_row(
                d["day"], d["date"], d["min"], d["max"],
                d["condition"], d["sea condition"], d["wind"], d["probability"],
            )
        self.console.print(table)

    def render_cityforecast(self, data, day=None, **kwargs):
        table = Table(title="Week forecast" if day is None else "Day forecast")
        table.add_column("Day", justify="left", style="magenta", no_wrap=True)
        table.add_column("Date", justify="left", no_wrap=True)
        table.add_column("Min", justify="left", no_wrap=True)
        table.add_column("Max", justify="left", no_wrap=True)
        table.add_column("Condition", justify="left")
        table.add_column("Wind", justify="left", no_wrap=True)
        if day is None:
            for d in data:
                d_dict = d if isinstance(d, dict) else d.to_dict()
                table.add_row(
                    d_dict["day"], d_dict["date"], d_dict["min"],
                    d_dict["max"], d_dict["condition"], d_dict["wind"],
                )
        else:
            d = data[day] if isinstance(data, list) else data
            d_dict = d if isinstance(d, dict) else d.to_dict()
            table.add_row(
                d_dict["day"], d_dict["date"], d_dict["min"],
                d_dict["max"], d_dict["condition"], d_dict["wind"],
            )
        self.console.print(table)

    def render_sunrise(self, data, **kwargs):
        months = list(data.keys())
        table = Table(title="Sunrise")
        table.add_column("", justify="left", no_wrap=True)
        for m in months:
            table.add_column(m, justify="left", no_wrap=True)
        for i in range(1, 32):
            def get_sun_info(month, date):
                d = str(date)
                entry = data.get(month, {}).get(d)
                if entry:
                    entry_dict = entry if isinstance(entry, dict) else entry.to_dict()
                    return "{} - {}".format(entry_dict["rise"], entry_dict["set"])
                return ""
            month1_data = get_sun_info(months[0], i)
            month2_data = get_sun_info(months[1], i) if len(months) > 1 else ""
            table.add_row(str(i).zfill(2), month1_data, month2_data)
        self.console.print(table)

    def render_moonrise(self, data, **kwargs):
        months = list(data.keys())
        table = Table(title="Moonrise")
        table.add_column("", justify="left", no_wrap=True)
        for m in months:
            table.add_column(m, justify="left", no_wrap=True)
        for i in range(1, 32):
            def get_moon_info(month, date):
                d = str(date)
                entry = data.get(month, {}).get(d)
                if entry:
                    entry_dict = entry if isinstance(entry, dict) else entry.to_dict()
                    return "{} - {}".format(entry_dict["rise"], entry_dict["set"])
                return ""
            month1_data = get_moon_info(months[0], i)
            month2_data = get_moon_info(months[1], i) if len(months) > 1 else ""
            table.add_row(str(i).zfill(2), month1_data, month2_data)
        self.console.print(table)

    def render_moonphase(self, data, month=None, **kwargs):
        table = Table(title="Moon Phase")
        table.add_column("Month", justify="left", style="magenta", no_wrap=True)
        table.add_column("New Moon", justify="left", style="magenta", no_wrap=True)
        table.add_column("First Quarter", justify="left", style="magenta", no_wrap=True)
        table.add_column("Full Moon", justify="left", style="magenta", no_wrap=True)
        table.add_column("Last Quarter", justify="left", style="magenta", no_wrap=True)

        def get_moon_str(d, key):
            try:
                entry = d[key]
                entry_dict = entry if isinstance(entry, dict) else entry.to_dict()
                return "{} at {}:{}".format(
                    entry_dict["date"],
                    str(entry_dict["hour"]).zfill(2),
                    str(entry_dict["minute"]).zfill(2),
                )
            except KeyError:
                return ""

        if month is None:
            data_dict = data if isinstance(data, dict) else data
            for k, d in data_dict.items():
                nm = get_moon_str(d, "new moon")
                fq = get_moon_str(d, "first quarter")
                fm = get_moon_str(d, "full moon")
                lq = get_moon_str(d, "last quarter")
                table.add_row(k, nm, fq, fm, lq)
        else:
            d = data[month]
            nm = get_moon_str(d, "new moon")
            fq = get_moon_str(d, "first quarter")
            fm = get_moon_str(d, "full moon")
            lq = get_moon_str(d, "last quarter")
            table.add_row(month, nm, fq, fm, lq)
        self.console.print(table)

    def render_eclipses(self, data, **kwargs):
        self.console.print(data)

    def render_equinoxes(self, data, **kwargs):
        self.console.print(data)

    def render_solstices(self, data, **kwargs):
        self.console.print(data)

    def render_tides(self, data, **kwargs):
        self.console.print(data)

    def render_uvindex(self, data, **kwargs):
        data_dict = data if isinstance(data, dict) else data.to_dict()
        uv_string = ""
        for region, status in data_dict.items():
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
            uv_string += "[magenta]{}[/magenta]: {}\n".format(
                region_display, status_display
            )
        uv_string = uv_string.strip("\n")
        self.console.print(Panel(uv_string, expand=True, title="UV Index"))

    def render_latest(self, data, **kwargs):
        data_dict = data if isinstance(data, dict) else data.to_dict()
        rainfall = data_dict.get("rainfall24h", {})
        rainfall_info_str = "{}".format(rainfall.get("info", ""))
        rtable = Table()
        rtable.add_column("Region", justify="left", style="slate_blue3")
        rtable.add_column("Rain 24hr", style="dark_cyan")
        rtable.add_column("Rain 3hrs", style="dark_cyan")
        rtable.add_column("Wind", style="dark_cyan")
        rtable.add_column("Humidity", style="dark_cyan")
        rtable.add_column("Min Max temp", style="dark_cyan")
        rainfall3hrs = data_dict.get("rainfall3hrs", {}).get("data", {})
        wind = data_dict.get("wind", {}).get("data", {})
        humidity = data_dict.get("humidity", {}).get("data", {})
        minmaxtemp = data_dict.get("minmaxtemp", {}).get("data", {})
        for r, a in rainfall.get("data", {}).items():
            mmt = minmaxtemp.get(r, {})
            if mmt.get("min") or mmt.get("max"):
                minmaxtemp_str = "{} to {}".format(mmt.get("min", ""), mmt.get("max", ""))
            else:
                minmaxtemp_str = ""
            rtable.add_row(
                r, a, rainfall3hrs.get(r, ""), wind.get(r, ""),
                humidity.get(r, ""), minmaxtemp_str,
            )
        titles_str = "".join(["- {}\n".format(v.get("info", "")) for v in data_dict.values()])
        rtable.title = titles_str
        self.console.print(Panel(rtable, expand=True, title="Latest data"))

    def render_main_message(self, data, links=False, **kwargs):
        data_dict = data if isinstance(data, dict) else data.to_dict() if hasattr(data, 'to_dict') else data
        if isinstance(data_dict, dict) and "links" in data_dict:
            if links:
                message_links = data_dict.get("links", [])
                table = Table(title="Info")
                table.add_column("Message")
                table.add_column("Link")
                for l in message_links:
                    table.add_row(l[0], l[1])
                self.console.print(table)
            else:
                self.console.print(
                    Panel(data_dict.get("text", ""), title="Meteo message")
                )
        else:
            if links:
                self.console.print(data)
            else:
                self.console.print(Panel(str(data), title="Meteo message"))

    def render_special_bulletin(self, data, **kwargs):
        self.console.print(Panel(data))

    def render_today(self, **kwargs):
        pass
