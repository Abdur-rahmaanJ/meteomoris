try:
    # Poor solution for calling pure python codes
    # when the packaging system is installing the
    # package. Due to a poorly designed user experience
    # from the PyPA, i'll let it like this until things
    # have settled
    import requests
    from bs4 import BeautifulSoup
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except Exception:
    pass

import sys
import datetime
import calendar
import re
import site
import os
import http.client as httplib
import json


# def __download_file(url, path):
#     r = requests.get(url, allow_redirects=True)
#     open(path, 'wb').write(r.content)


def cache_path():
    return os.path.join(".", "meteomoris_cache.json")


class Meteo:
    ALREADY_CHECKED_INTERNET = False
    EXIT_ON_NO_INTERNET = True
    CHECK_INTERNET = True
    DEBUG = False
    CACHE_PERMS = True
    CACHE_PATH = cache_path()

    today = str(datetime.date.today())  # Decoupled for tests

    try:
        # thanks pypa for broken tricks like this
        console = Console()
        print = console.print
    except:
        pass

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip",
        "DNT": "1",  # Do Not Track Request Header
        "Connection": "close",
        "Sec-GPC": "1",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # --- Utilities ---
    @classmethod
    def verify_cache_exists(cls):
        if cls.DEBUG:
            cls.print("Verifying if cache exists")
        if not os.path.exists(cls.CACHE_PATH):
            try:
                if cls.DEBUG:
                    cls.print(
                        f"Not exists, trying to create empty file at {cls.CACHE_PATH}"
                    )
                with open(cls.CACHE_PATH, "w+") as f:
                    json.dump({}, f)
                cls.CACHE_PERMS = True
            except PermissionError:
                if cls.DEBUG:
                    cls.print("Could not: permission error")
                cls.CACHE_PERMS = False

    @classmethod
    def get_cache_data(cls):
        cls.verify_cache_exists()

        if cls.DEBUG:
            cls.print("Fetching cache data")
        data = None
        try:
            with open(cls.CACHE_PATH) as f:
                data = json.load(f)
            cls.CACHE_PERMS = True
            if cls.DEBUG:
                cls.print(f"Successful: {data}")
        except FileNotFoundError:
            if cls.DEBUG:
                cls.print("File not found, perms set to false")
            cls.CACHE_PERMS = False
        return data

    @classmethod
    def get_from_cache(cls, key):
        """
        keep cache day only per day for now
        until we add functionalities to clear
        the cache for all
        """
        if cls.DEBUG:
            cls.print(f"Loading key {key} from cache")
        cache_data = cls.get_cache_data()
        if cls.today not in cache_data:
            if cls.DEBUG:
                cls.print("Today not in cache, adding")
            cache_data = {}  # clear cache
            cache_data[str(cls.today)] = {}
            if cls.DEBUG:
                cls.print(f"Added {cache_data}, dumping data")
            try:
                with open(cls.CACHE_PATH, "w+") as f:
                    json.dump(cache_data, f)
                cls.CACHE_PERMS = True
                if cls.DEBUG:
                    cls.print("Dumped!")
            except PermissionError:
                cls.CACHE_PERMS = False
                if cls.DEBUG:
                    cls.print("Could not dump, perms error")
            return False
        if key not in cache_data[cls.today]:
            if cls.DEBUG:
                cls.print(f"Key {key} not in {cache_data[cls.today]}")
            return False

        data = cache_data[cls.today][key]
        if cls.DEBUG:
            cls.print(f"Returning {data}")
        return data

    @classmethod
    def add_to_cache(cls, key, data):
        if cls.DEBUG:
            cls.print(f"Trying to add key {key} and {data}")

        try:
            cache_data = cls.get_cache_data()
            cache_data[cls.today][key] = data
            with open(cls.CACHE_PATH, "w+") as f:
                json.dump(cache_data, f)
            cls.CACHE_PERMS = True
            if cls.DEBUG:
                cls.print(f"Successfully added key {key} and data {data}")
        except TypeError:
            cls.CACHE_PERMS = False
            if cls.DEBUG:
                cls.print(
                    f"Could not add key {key} and data {data}: Did not receive data"
                )
        except PermissionError:
            cls.CACHE_PERMS = False
            if cls.DEBUG:
                cls.print(f"Could not add key {key} and data {data}: Perms error")

    @classmethod
    def internet_present(cls):
        console = Console()

        with console.status("Checking internet ...", spinner="aesthetic"):
            conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
            try:
                conn.request("HEAD", "/")
                return True
            except Exception:
                return False
            finally:
                cls.ALREADY_CHECKED_INTERNET = True
                conn.close()

    @classmethod
    def check_internet(cls):
        if cls.CHECK_INTERNET:
            if not cls.ALREADY_CHECKED_INTERNET:
                if not cls.internet_present():
                    print("No internet")
                    if cls.EXIT_ON_NO_INTERNET:
                        sys.exit()

    # --- Data ---
    @classmethod
    def get_weekforecast(cls, day=None, print=False):
        print_ = print

        return_data = None
        try:
            cache = cls.get_from_cache("weekforecast")
        except:
            # TODO Add debug if permm error cache
            cache = False

        if not cls.CACHE_PERMS:
            cache = False

        if cache:
            return_data = cache
        else:
            cls.check_internet()

            URL = "http://metservice.intnet.mu"
            r = requests.get(URL, headers=cls.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            w_forecast = soup.find(attrs={"class": "daysforecast"})

            week_forcecast = w_forecast.find_all(attrs={"class": "forecast"})

            week = []

            for i, _day in enumerate(week_forcecast):
                fulldate = _day.find(attrs={"class": "fday"})
                fdate = fulldate.text.split(",")
                date_day = fdate[0]
                date_date = fdate[1].strip()

                return_dict = {}

                return_dict["day"] = date_day
                return_dict["date"] = date_date

                condition = _day.find(attrs={"class": "fcondition"})
                return_dict["condition"] = condition.text

                temp = _day.find_all(attrs={"class": "ftemp"})
                min_temp = temp[0].text
                max_temp = temp[1].text
                return_dict["min"] = min_temp
                return_dict["max"] = max_temp

                fgrey = _day.find_all(attrs={"class": "fgrey"})
                wind = fgrey[0].text
                sea_condition = fgrey[1].text
                return_dict["wind"] = wind
                return_dict["sea condition"] = sea_condition

                prob = _day.find_all(attrs={"class": "fgrey1"})
                probability = prob[0].text
                return_dict["probability"] = probability

                week.append(return_dict)

            return_data = week

            try:
                cls.add_to_cache("weekforecast", return_data)
            except Exception as e:
                if cls.DEBUG:
                    cls.print(f"Could not add week forecast to cache: {e}")

        if print_:
            console = Console()
            table = Table()
            table.add_column("Day", justify="left", style="magenta", no_wrap=True)
            table.add_column("Date", justify="left", no_wrap=True)
            table.add_column("Min", justify="left", no_wrap=True)
            table.add_column("Max", justify="left", no_wrap=True)
            table.add_column("Condition", justify="left")
            table.add_column("Sea condition", justify="left")
            table.add_column("Wind", justify="left", no_wrap=True)
            table.add_column("Probability", justify="left")
            if day is None:
                table.title = "Week forecast"
                for d in return_data:
                    table.add_row(
                        d["day"],
                        d["date"],
                        d["min"],
                        d["max"],
                        d["condition"],
                        d["sea condition"],
                        d["wind"],
                        d["probability"],
                    )
                console.print(table)

            else:
                return_data = return_data[day]
                table.title = "Day forecast"
                d = return_data
                table.add_row(
                    d["day"],
                    d["date"],
                    d["min"],
                    d["max"],
                    d["condition"],
                    d["sea condition"],
                    d["wind"],
                    d["probability"],
                )
                console.print(table)
                return

        if day is None:
            return return_data
        else:
            return return_data[day]

    @classmethod
    def get_cityforecast(cls, print=False, day=None):
        print_ = print

        if cls.DEBUG:
            cls.print("Fetching city forecast")

        return_data = None
        try:
            cache = cls.get_from_cache("cityforecast")
        except:
            # TODO Add debug if permm error cache
            cache = False

        if not cls.CACHE_PERMS:
            cache = False

        if cache:
            if cls.DEBUG:
                cls.print("Found in cache")
            return_data = cache
        else:
            if cls.DEBUG:
                cls.print("Not found in cache")
            cls.check_internet()
            # for city of PL

            URL = "http://metservice.intnet.mu"
            r = requests.get(URL, headers=cls.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            w_forecast = soup.find(attrs={"class": "city_forecast"})
            week_forcecast = w_forecast.find_all(attrs={"class": "block"})

            week = []

            for i, _day in enumerate(week_forcecast):
                date_day = _day.find(attrs={"class": "cday"})
                return_dict = {}
                return_dict["day"] = date_day.text[:-1]

                date_date = _day.find(attrs={"class": "cdate"})
                return_dict["date"] = date_date.text

                condition = _day.find(attrs={"class": "fcondition"})
                return_dict["condition"] = condition.text

                min_temp = _day.find(attrs={"class": "ctemp"})
                return_dict["min"] = min_temp.text

                max_temp = _day.find(attrs={"class": "ctemp1"})
                return_dict["max"] = max_temp.text

                wind = _day.find(attrs={"class": "cwind1"})
                return_dict["wind"] = wind.text

                week.append(return_dict)

            return_data = week

            try:
                cls.add_to_cache("cityforecast", return_data)
            except Exception as e:
                if cls.DEBUG:
                    cls.print(f"Could not add week forecast to cache: {e}")

        if print_:
            console = Console()
            table = Table()
            table.add_column("Day", justify="left", style="magenta", no_wrap=True)
            table.add_column("Date", justify="left", no_wrap=True)
            table.add_column("Min", justify="left", no_wrap=True)
            table.add_column("Max", justify="left", no_wrap=True)
            table.add_column("Condition", justify="left")
            table.add_column("Wind", justify="left", no_wrap=True)

            if day is None:
                return_data = week
                table.title = "Week forecast"
                for d in return_data:
                    table.add_row(
                        d["day"],
                        d["date"],
                        d["min"],
                        d["max"],
                        d["condition"],
                        d["wind"],
                    )
                console.print(table)
                return
            else:
                return_data = week[day]
                table.title = "Day forecast"
                d = return_data

                table.add_row(
                    d["day"], d["date"], d["min"], d["max"], d["condition"], d["wind"]
                )
                console.print(table)
                return

        if day is None:
            return return_data
        else:
            return return_data[day]

    @classmethod
    def get_moonphase(cls, print=False, month=None):
        print_ = print
        cls.check_internet()
        URL = "http://metservice.intnet.mu/sun-moon-and-tides-moon-phase.php"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")

        table = soup.find("table")
        table_body = table.find("tbody")

        rows = table_body.find_all("tr")
        data = dict()

        for i, row in enumerate(rows):
            cols = row.find_all("td")

            cols = [ele.text.strip() for ele in cols]

            if i == 0:  # first row
                month1 = " ".join(cols[0].lower().split())
                month2 = " ".join(cols[1].lower().split())
                data = {month1.casefold(): {}, month2.casefold(): {}}

            elif 1 < i < 6:  # 3rd row and above
                m1_phase = cols[0]
                m1_date = int(cols[1])
                m1_hour = int(cols[2])
                m1_min = int(cols[3])

                m2_phase = cols[4]
                m2_date = int(cols[5])
                m2_hour = int(cols[6])
                m2_min = int(cols[7])

                code_lookup = {
                    "N.M": "new moon",
                    "F.Q": "first quarter",
                    "F.M": "full moon",
                    "L.Q": "last quarter",
                }

                phase1 = code_lookup[m1_phase]
                data[month1][phase1] = {
                    "date": m1_date,
                    "hour": m1_hour,
                    "minute": m1_min,
                }

                phase2 = code_lookup[m2_phase]
                data[month2][phase2] = {
                    "date": m2_date,
                    "hour": m2_hour,
                    "minute": m2_min,
                }

        if print_:
            console = Console()
            table = Table(title="Moon Phase")
            table.add_column("Month", justify="left", style="magenta", no_wrap=True)
            table.add_column("New Moon", justify="left", style="magenta", no_wrap=True)
            table.add_column(
                "First Quarter", justify="left", style="magenta", no_wrap=True
            )
            table.add_column("Full Moon", justify="left", style="magenta", no_wrap=True)
            table.add_column(
                "Last Quarter", justify="left", style="magenta", no_wrap=True
            )

        def get_moon_str(d, key):
            try:
                return "{} at {}:{}".format(
                    d[key]["date"],
                    str(d[key]["hour"]).zfill(2),
                    str(d[key]["minute"]).zfill(2),
                )
            except KeyError:
                return ""

        if month is None:
            if print_:
                for k, d in data.items():
                    nm = get_moon_str(d, "new moon")
                    fq = get_moon_str(d, "first quarter")
                    fm = get_moon_str(d, "full moon")
                    lq = get_moon_str(d, "last quarter")
                    table.add_row(k, nm, fq, fm, lq)

                console.print(table)
                return

            return data
        else:
            if print_:
                d = data[month]
                nm = get_moon_str(d, "new moon")
                fq = get_moon_str(d, "first quarter")
                fm = get_moon_str(d, "full moon")
                lq = get_moon_str(d, "last quarter")
                table.add_row(month, nm, fq, fm, lq)

                console.print(table)
                return
            return data[month]

    @classmethod
    def get_main_message(cls, print_=False, links=False):
        """
        Get the main message of website
        """
        print_ = print_
        cls.check_internet()
        URL = "http://metservice.intnet.mu"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")

        message = soup.find("div", attrs={"class": "warning"})

        if links:
            message_links = [
                (link.text.strip(), link.get("href")) for link in message.find_all("a")
            ]
            if print_:
                console = Console()
                table = Table(title="Info")
                table.add_column("Message")
                table.add_column("Link")
                for l in message_links:
                    table.add_row(l[0], l[1])
                console.print(table)
            return message_links

        if print_:
            console = Console()
            console.print(Panel(message.text.strip(), title="Meteo message"))
            return
        return message.text.strip()

    @classmethod
    def get_special_weather_bulletin(cls, print=False):
        print_ = print
        cls.check_internet()

        URL = "http://metservice.intnet.mu/warning-bulletin-special-weather.php"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")

        message = soup.find("div", attrs={"class": "left_content"})
        unwanted = message.find("div", attrs={"class": "warning"})
        unwanted.extract()

        data = message.text.strip()

        if print_:
            cls.print(Panel(data))
            return
        return data

    @classmethod
    def get_eclipse_text(cls):
        """small function to scrape the eclipse data from a website"""

        url = "http://metservice.intnet.mu/sun-moon-and-tides-info-eclipses.php"
        r = requests.get(url, headers=cls.headers)
        page_soup = BeautifulSoup(r.text, "html.parser")
        page_container = page_soup.find("div", {"class": "left_content"}).findAll("p")
        page_container = page_container[1:-1]

        eclipse_text = ""
        for line in page_container:
            eclipse_text += line.text + "\n"

        return eclipse_text

    @classmethod
    def test(cls):
        print("test ok")

    @classmethod
    def get_sunrisemu(cls, print=False):
        print_ = print

        data = None
        try:
            cache = cls.get_from_cache("sunrisemu")
        except:
            # TODO Add debug if permm error cache
            cache = False
        if not cls.CACHE_PERMS:
            cache = False
        if cache:
            data = cache
        else:
            cls.check_internet()

            URL = "http://metservice.intnet.mu/sun-moon-and-tides-sunrise-sunset-mauritius.php"
            r = requests.get(URL, headers=cls.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            table = soup.find("table")
            table_body = table.find("tbody")

            rows = table_body.find_all("tr")
            data = dict()
            for i, row in enumerate(rows):
                cols = row.find_all("td")

                cols = [ele.text.strip() for ele in cols]

                if i == 0:
                    month1 = re.sub("\d+", "", cols[1].lower()).strip()
                    month2 = re.sub("\d+", "", cols[2].lower()).strip()
                    data = {month1: {}, month2: {}}

                elif i > 1:
                    date = int(cols[0])
                    m1_rise = cols[1]
                    m1_set = cols[2]
                    m2_rise = cols[3]
                    m2_set = cols[4]

                    if m1_rise and m1_set:
                        data[month1][date] = {"rise": m1_rise, "set": m1_set}
                    if m2_rise and m2_set:
                        data[month2][date] = {"rise": m2_rise, "set": m2_set}
            try:
                cls.add_to_cache("sunrisemu", data)
            except:
                pass

        def get_sun_info(data, month, date, point):
            try:
                return "{}".format(data[month][date][point])
            except:
                return ""

        if print_:
            console = Console()
            table = Table(title="Sunrise (Mauritius)")

            table.add_column("", justify="left", no_wrap=True)
            months = list(data.keys())
            for m in months:
                table.add_column(m, justify="left", no_wrap=True)

            for i in range(1, 32):
                table.add_row(
                    str(i).zfill(2),
                    get_sun_info(data, months[0], i, "rise"),
                    get_sun_info(data, months[1], i, "set"),
                )

            console.print(table)
            return
        return data

    @classmethod
    def get_sunriserodr(cls, print=False):
        print_ = print
        data = None
        try:
            cache = cls.get_from_cache("sunriserodr")
        except:
            # TODO Add debug if permm error cache
            cache = False
        if not cls.CACHE_PERMS:
            cache = False
        if cache:
            data = cache
        else:
            cls.check_internet()
            URL = "http://metservice.intnet.mu/sun-moon-and-tides-sunrise-sunset-rodrigues.php"
            r = requests.get(URL, headers=cls.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            table = soup.find("table")
            table_body = table.find("tbody")

            rows = table_body.find_all("tr")
            data = dict()
            for i, row in enumerate(rows):
                cols = row.find_all("td")

                cols = [ele.text.strip() for ele in cols]

                if i == 0:
                    month1 = cols[1].lower()
                    month2 = cols[2].lower()
                    data = {month1: {}, month2: {}}

                elif i > 1:
                    date = int(cols[0])
                    m1_rise = cols[1]
                    m1_set = cols[2]
                    m2_rise = cols[3]
                    m2_set = cols[4]

                    if m1_rise and m1_set:
                        data[month1][date] = {"rise": m1_rise, "set": m1_set}
                    if m2_rise and m2_set:
                        data[month2][date] = {"rise": m2_rise, "set": m2_set}
            try:
                cls.add_to_cache("sunriserodr", data)
            except:
                pass

        def get_sun_info(data, month, date, point):
            try:
                return "{}".format(data[month][date][point])
            except:
                return ""

        if print_:
            console = Console()
            table = Table(title="Sunrise (Rodrigues)")

            table.add_column("", justify="left", no_wrap=True)
            months = list(data.keys())
            for m in months:
                table.add_column(m, justify="left", no_wrap=True)

            for i in range(1, 32):
                table.add_row(
                    str(i).zfill(2),
                    get_sun_info(data, months[0], i, "rise"),
                    get_sun_info(data, months[1], i, "set"),
                )

            console.print(table)
            return

        return data

    @classmethod
    def get_eclipses_raw(cls):
        eclipses_data = None

        try:
            cache = cls.get_from_cache("eclipses_raw")
        except:
            # TODO Add debug if permm error cache
            cache = False
        if not cls.CACHE_PERMS:
            cache = False
        if cache:
            eclipses_data = cache
        else:
            cls.check_internet()
            URL = "http://metservice.intnet.mu/sun-moon-and-tides-info-eclipses.php"
            r = requests.get(URL, headers=cls.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            tables = soup.find_all("table")

            len_tables = len(tables)
            data = {"eclipses": []}
            year = None
            eclipse_info = {}
            all_tables = []
            equinoxes = []
            # cls.print(str(len(tables)))
            for table_index, table in enumerate(tables):
                current_list = table.text.strip().split("\n")
                current_list = [e for e in current_list if bool(e.strip())]
                if table_index == 0:
                    pass

                elif table_index == len(tables) - 1:
                    equinoxes = current_list
                else:
                    all_tables += current_list
            """
            [
            {
                'end': {'date': 1, 'hour': 2, 'minute': 37, 'month': 'may'},
                'info': 'The eclipse will not be visible in Mauritius, Rodrigues, St. Brandon and Agalega.',
                'start': {'date': 30, 'hour': 22, 'minute': 45, 'month': 'april'},
                'status': 'partial',
                'type': 'sun'
            },
            ...
            {
                'end': {'date': 8, 'hour': 17, 'minute': 56, 'month': 'november'},
                'info': 'The eclipse will not be visible in Mauritius, Rodrigues, St. Brandon and Agalega.',
                'start': {'date': 8, 'hour': 12, 'minute': 2, 'month': 'november'},
                'status': 'total',
                'type': 'moon'
            }
            ]
            """
            eclipse_info = []

            if cls.DEBUG:
                cls.print(all_tables)
            """
            [
                'Annular-Total eclipse of the Sun - April 20',
                'The eclipse begins on 20 April at 05h34 and ends on 20 April at 10h59.',
                'The penumbral part of the eclipse will be visible in Mauritius, Rodrigues, St. Brandon but will not be visible in 
            Agalega.',
                'Penumbral eclipse of the Moon - May 05',
                'The eclipse begins on 05 May at 19h12 and ends at 23h33.',
                'The eclipse will be visible in Mauritius, Rodrigues, St. Brandon and Agalega.',
                'Annular eclipse of the Sun - October 14-15',
                'The eclipse begins on 14 October at 19h04 and ends on 15 October at 00h55.',
                'The eclipse will not be visible in Mauritius, Rodrigues, St. Brandon and Agalega.',
                'Partial eclipse of the Moon - October 28-29',
                'The eclipse begins on 28 October at 23h34 and ends on 29 October at 02h28.',
                'The eclipse will be visible in Mauritius, Rodrigues, St. Brandon and Agalega.'
            ]
            """
            for table_index, row in enumerate(all_tables):
                info = {}
                if ("eclipse of the" in row.casefold()) and ("-" in row.casefold()):
                    info["title"] = row.split(" - ")[0].strip()
                    info["info"] = all_tables[table_index + 2]
                    if "sun" in info["title"].casefold():
                        info["type"] = "sun"
                    elif "moon" in info["title"].casefold():
                        info["type"] = "moon"
                    info["status"] = info["title"].casefold().split()[0].strip()

                    # info['date'] = row.split(' - ')[1].strip()

                    next_row = all_tables[table_index + 1]

                    next_row_words = next_row.split()
                    for i, word in enumerate(next_row_words):
                        if word == "begins":
                            if next_row_words[i + 1] == "on":
                                info["start"] = {}
                                info["start"]["date"] = int(next_row_words[i + 2])
                                info["start"]["month"] = next_row_words[
                                    i + 3
                                ].casefold()
                                info["start"]["hour"] = int(
                                    next_row_words[i + 5].split("h")[0].strip(".")
                                )
                                info["start"]["minute"] = int(
                                    next_row_words[i + 5].split("h")[1].strip(".")
                                )
                        if word == "ends":
                            if next_row_words[i + 1] == "on":
                                info["end"] = {}
                                info["end"]["date"] = int(next_row_words[i + 2])
                                info["end"]["month"] = next_row_words[i + 3].casefold()
                                info["end"]["hour"] = int(
                                    next_row_words[i + 5].split("h")[0].strip(".")
                                )
                                info["end"]["minute"] = int(
                                    next_row_words[i + 5].split("h")[1].strip(".")
                                )
                            elif next_row_words[i + 1] == "at":
                                info["end"] = {}
                                info["end"]["date"] = int(info["start"]["date"])
                                info["end"]["month"] = info["start"]["month"].casefold()
                                info["end"]["hour"] = int(
                                    next_row_words[i + 2].split("h")[0].strip(".")
                                )
                                info["end"]["minute"] = int(
                                    next_row_words[i + 2].split("h")[1].strip(".")
                                )

                    eclipse_info.append(info)

            if cls.DEBUG:
                cls.print(equinoxes)
            """
            [
                'EQUINOXES and SOLSTICES - 2023',
                'Equinoxes\xa0\xa0\xa0 :\xa0 \xa0March 21 at 01h24 and September 23 at 10h50.',
                'Solstices\xa0\xa0\xa0 :\xa0 \xa0June 21 at 18h57 and December 22 at 07h27.'
            ]
            """
            equinox = [e.strip().casefold().strip(".") for e in equinoxes[1].split()]
            solstice = [e.strip().casefold().strip(".") for e in equinoxes[2].split()]
            year = equinoxes[0].split(" - ")[1].strip().casefold()
            year = int(year)
            """

            >>> get_equinoxes()
            [
            {
                'day': 20, 'hour': 19, 'minute': 33, 'month': 'march', 'year': 2022
            },
            {
            'day': 23, 'hour': 5, 'minute': 3, 'month': 'september', 'year': 2022
            }
            ]

            >>> get_solstices()
            [
            {
                'day': 21, 'hour': 13, 'minute': 13, 'month': 'june', 'year': 2022
            },
            {
                'day': 22, 'hour': 1, 'minute': 48, 'month': 'december', 'year': 2022
            }
            ]"""
            equinox_info = None
            for i, e in enumerate(equinox):
                if e == "and":
                    equinox_info = [
                        {
                            "day": int(equinox[i - 3]),
                            "month": equinox[i - 4],
                            "year": year,
                            "hour": int(equinox[i - 1].split("h")[0]),
                            "minute": int(equinox[i - 1].split("h")[1]),
                        },
                        {
                            "day": int(equinox[i + 2]),
                            "month": equinox[i + 1],
                            "year": year,
                            "hour": int(equinox[i + 4].split("h")[0]),
                            "minute": int(equinox[i + 4].split("h")[1]),
                        },
                    ]

            solstice_info = None
            for i, e in enumerate(equinox):
                if e == "and":
                    solstice_info = [
                        {
                            "day": int(solstice[i - 3]),
                            "month": solstice[i - 4],
                            "year": year,
                            "hour": int(solstice[i - 1].split("h")[0]),
                            "minute": int(solstice[i - 1].split("h")[1]),
                        },
                        {
                            "day": int(solstice[i + 2]),
                            "month": solstice[i + 1],
                            "year": year,
                            "hour": int(solstice[i + 4].split("h")[0]),
                            "minute": int(solstice[i + 4].split("h")[1]),
                        },
                    ]

            eclipses_data = {
                "eclipses": eclipse_info,
                "equinoxes": equinox_info,
                "solstices": solstice_info,
            }

            try:
                cls.add_to_cache("eclipses_raw", eclipses_data)
            except:
                pass

        return eclipses_data

    @classmethod
    def get_eclipses(cls):
        return cls.get_eclipses_raw()["eclipses"]

    @classmethod
    def get_equinoxes(cls):
        return cls.get_eclipses_raw()["equinoxes"]

    @classmethod
    def get_solstices(cls):
        return cls.get_eclipses_raw()["solstices"]


    @classmethod
    def get_today_moonphase(cls):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        year = datetime.datetime.now().year

        skip_moonphase = False
        try:
            moonphase = cls.get_moonphase()["{} {}".format(month, year)]
        except:
            skip_moonphase = True

        info = {}

        if not skip_moonphase:
            for phase in moonphase:
                if moonphase[phase]["date"] == day:

                    info = {
                        "title": phase,
                        "hour": moonphase[phase]["hour"],
                        "minute": moonphase[phase]["minute"]
                    }
                    break

        return info
    
    @classmethod
    def get_today_eclipse(cls):
        day = datetime.datetime.now().day # int 20
        month = calendar.month_name[datetime.datetime.now().month].casefold() # december
        year = datetime.datetime.now().year # int 2023 

        info = {}

        for eclipse in cls.get_eclipses():
            if (
                eclipse["start"]["date"] == day
                and eclipse["start"]["month"] == month
            ):
                info["start"] = eclipse

            if eclipse["end"]["date"] == day and eclipse["end"]["month"] == month:
                info["end"] = eclipse

        return info
    
    @classmethod 
    def get_today_sunrise(cls, country):
        '''
        
            return 
                {'rise': '05:53', 'set': '18:53'}
        '''
        day = datetime.datetime.now().day # int 20
        month = calendar.month_name[datetime.datetime.now().month].casefold() # december
        if country == "mu":
            sunrise = cls.get_sunrisemu()
            try:
                sun = sunrise[month][str(day)]
            except KeyError:
                sun = sunrise[month][int(day)]
        else:
            sunrise = cls.get_sunriserodr()
            try:
                sun = sunrise[month][str(day)]
            except KeyError:
                sun = sunrise[month][int(day)]
        return sun 

    @classmethod
    def get_today_forecast(cls):
        return cls.get_weekforecast(day=0)
    
    @classmethod
    def get_today_tides(cls):
        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        tides_all = cls.get_tides()
        try:
            tides = tides_all["months"][month][str(day)]
        except KeyError:
            tides = tides_all["months"][month][int(day)]
        
        return tides

    @classmethod
    def print_today(cls, country="mu"):
        cls.check_internet()
        """
        All info for today

        Check week forecast from today
        Check moonphase info
        Check solstice, eclipse and equinox
        Print sunrise and sunset
        """
        with cls.console.status("fetching", spinner="aesthetic") as status:
            if country not in ["mu", "rodr"]:
                cls.print("[red]Country should be mu or rodr[/red]")

            day = datetime.datetime.now().day
            month = calendar.month_name[datetime.datetime.now().month].casefold()
            year = datetime.datetime.now().year


            forecast = cls.get_today_forecast()

            sun = cls.get_today_sunrise(country)

            col_elems = []



            today_moonphase = cls.get_today_moonphase()
            if today_moonphase:
                moonphase_title = today_moonphase['title'].title()
                moonphase_hour = today_moonphase['hour']
                moonphase_minute = today_moonphase['minute']
                moonphase_string = f"{moonphase_title} today at [green]{moonphase_hour}:{moonphase_minute}[/green]"
            else:
                moonphase_string = ""


            eclipse_today = cls.get_today_eclipse()
            eclipse_elements = []
            if eclipse_today:
                if "start" in eclipse_today:
                    elipse_today_start = eclipse_today["start"]
                    eclipse_elements.extend(
                        [
                            elipse_today_start["title"],
                            "starts today at",
                            "[green]{}:{}[/green]".format(
                                elipse_today_start["start"]["hour"], elipse_today_start["start"]["minute"]
                            ),
                            elipse_today_start["info"],
                        ]
                    )
                if "end" in eclipse_today:
                    eclipse_today_end = eclipse_today["end"]

                    eclipse_elements.extend(
                        [
                            "\n",
                            eclipse_today_end["title"],
                            "ends today at",
                            "[green]{}:{}[/green]".format(
                                eclipse_today_end["end"]["hour"], eclipse_today_end["end"]["minute"]
                            ),
                            eclipse_today_end["info"],
                        ]
                    )
            eclipse_string = " ".join(eclipse_elements).replace("\n ", "\n")


            for equinox in cls.get_equinoxes():
                if equinox["day"] == day and equinox["month"] == month:
                    elements = []
                    elements.extend(
                        [
                            "Equinox today at",
                            "[green]{}:{}[/green]".format(
                                equinox["hour"], equinox["minute"]
                            ),
                        ]
                    )

                    equinox_string = " ".join(elements)
                else:
                    equinox_string = ""

            for solstice in cls.get_solstices():
                if solstice["day"] == day and solstice["month"] == month:
                    elements = []
                    elements.extend(
                        [
                            "Solstice today at",
                            "[green]{}:{}[/green]".format(
                                solstice["hour"], solstice["minute"]
                            ),
                        ]
                    )

                    solstice_string = " ".join(elements)
                else:
                    solstice_string = ""

            uv_string = ""
            for region, status in cls.get_uvindex().items():
                region = region.replace("-", " ").capitalize()
                if status.lower() == "extreme":
                    status = f"[blink]:fire: [red]{status}[/red][/blink]"
                elif status.lower() == "very high":
                    status = f"[red]{status}[/red]"
                elif status.lower() == "high":
                    status = f"[dark_orange3]{status}[/dark_orange3]"
                elif status.lower() in ["medium", "moderate"]:
                    status = f"[gold3]{status}[/gold3]"
                elif status.lower() == "low":
                    status = f"[green]{status}[/green]"
                uv_string += f"[magenta]{region}[/magenta]: {status}\n"
            uv_string.strip("\n")

            temp_str = "[b]{}-{}[/]".format(forecast["min"], forecast["max"])
            temp_panel = Panel(temp_str, expand=True, title="Temperature")

            wind_panel = Panel(forecast["wind"], expand=True, title="Wind")
            sea_panel = Panel(
                forecast["sea condition"], expand=True, title="Sea condition"
            )

            solstice_panel = Panel(solstice_string, expand=True, title="Solstice")
            equinox_panel = Panel(equinox_string, expand=True, title="Equinox")
            eclipse_panel = Panel(eclipse_string, expand=True, title="Eclipse")
            uv_panel = Panel(uv_string, expand=True, title="Ultra-Violet")

            if today_moonphase:
                moonphase_panel = Panel(
                    moonphase_string, expand=True, title="Moon phase"
                )
            else:
                moonphase_panel = Panel(
                    "Error fetching moonphase", expand=True, title="Moon phase"
                )
            condition_panel = Panel(
                forecast["condition"], expand=True, title="Contition"
            )

            sun_panel = Panel(
                "rises at {}\nsets at {}".format(sun["rise"], sun["set"]),
                expand=True,
                title="Sun",
            )

            messages = [
                "[bold]{}[/bold]  {}".format(l[0], l[1])
                for l in cls.get_main_message(links=True)
            ]
            message_panel = Panel("\n".join(messages), expand=True, title="Message")

            ###
            #
            # Tides
            #
            ###

            tides = cls.get_today_tides()
            
            tidetable = Table()

            tidetable.add_column(
                "Tide", justify="left", style="slate_blue3", no_wrap=True
            )
            tidetable.add_column("Time", justify="left", style="gold3", no_wrap=True)
            tidetable.add_column("Height (mm)", style="dark_cyan")

            # tides_str = '\n'.join([
            #     '{}: {}'.format(tides_all['month_format']['date'][0], tides[0]),
            #     '{}: {}'.format(tides_all['month_format']['date'][1], tides[1]),
            #     '{}: {}'.format(tides_all['month_format']['date'][2], tides[2]),
            #     '{}: {}'.format(tides_all['month_format']['date'][3], tides[3]),
            #     '{}: {}'.format(tides_all['month_format']['date'][4], tides[4]),
            #     '{}: {}'.format(tides_all['month_format']['date'][5], tides[5]),
            #     '{}: {}'.format(tides_all['month_format']['date'][6], tides[6]),
            #     '{}: {}'.format(tides_all['month_format']['date'][7], tides[7]),
            # ])

            tidetable.add_row("1st high", tides[0], tides[1])
            tidetable.add_row("2nd high", tides[2], tides[3])
            tidetable.add_row("1st low", tides[4], tides[5])
            tidetable.add_row("2nd low", tides[6], tides[7])
            tides_panel = Panel(tidetable, expand=True, title="Tides")

            ###
            #
            # Rainfall
            #
            ###

            latest = cls.get_latest()

            rainfall = latest["rainfall24h"]

            rainfall_info_str = "{}".format(rainfall["info"])

            rtable = Table()

            rtable.add_column("Region", justify="left", style="slate_blue3")
            rtable.add_column("Rain 24hr", style="dark_cyan")
            rtable.add_column("Rain 3hrs", style="dark_cyan")
            rtable.add_column("Wind", style="dark_cyan")
            rtable.add_column("Humidity", style="dark_cyan")
            rtable.add_column("Min Max temp", style="dark_cyan")

            for r, a in rainfall["data"].items():
                if (
                    latest["minmaxtemp"]["data"][r]["min"]
                    or latest["minmaxtemp"]["data"][r]["max"]
                ):
                    minmaxtemp_str = "{} to {}".format(
                        latest["minmaxtemp"]["data"][r]["min"],
                        latest["minmaxtemp"]["data"][r]["max"],
                    )
                else:
                    minmaxtemp_str = ""
                rtable.add_row(
                    r,
                    a,
                    latest["rainfall3hrs"]["data"][r],
                    latest["wind"]["data"][r],
                    latest["humidity"]["data"][r],
                    minmaxtemp_str,
                )

            latest_panel = Panel(rtable, expand=True, title="Latest data")
            titles = ["- {}\n".format(v["info"]) for k, v in latest.items()]
            titles_str = "".join(titles)

            rtable.title = titles_str

            # rainfall3hrs = latest['rainfall3hrs']

            # rainfall3hrs_info_str = '{}'.format(rainfall3hrs['info'])

            # r3table = Table(title=rainfall3hrs_info_str)

            # r3table.add_column("Region", justify="left", style="slate_blue3")
            # r3table.add_column("Rain", style="dark_cyan")

            # for r, a in rainfall3hrs['data'].items():
            #     r3table.add_row(r, a)

            # rainfall3hrs_panel = Panel(r3table, expand=True, title="Rainfall 3hrs")

            ###
            #
            # Grid
            #
            ###
            grid = Table.grid()
            grid.add_column()
            grid.add_column()
            def add_row(grid, elements):
                try:
                    grid.add_row(*elements)
                except:
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

            rtable = Table(box=None, show_header=False)
            rtable.add_column()
            rtable.add_row(message_panel)
            rtable.add_row(condition_panel)
            rtable.add_row(latest_panel)
            rtable.add_row(equinox_panel)
            rtable.add_row(solstice_panel)
            rtable.add_row(eclipse_panel)

            add_row(grid, [ltable, rtable])

            cls.print(Panel(grid, expand=True, title="Today"))

    @classmethod
    def get_tides(cls, print=False):
        print_ = print

        tide_info = None

        try:
            cache = cls.get_from_cache("tides")
        except Exception:
            # TODO Add debug if permm error cache
            cache = False

        if not cls.CACHE_PERMS:
            cache = False
        if cache:
            tide_info = cache
        else:
            cls.check_internet()
            URL = "http://metservice.intnet.mu/sun-moon-and-tides-tides-mauritius.php"
            r = requests.get(URL, headers=cls.headers)
            soup = BeautifulSoup(r.content, "html.parser")
            tables = soup.find_all("table")
            # cls.print(len(tables))
            if len(tables) == 1:
                text_arr = tables[0].text.split()
                text_arr_cleaned = []
                months = []
                years = []
                month_names = [m.casefold() for m in calendar.month_name if m]
                for t in text_arr:
                    if t.casefold() in month_names:
                        months.append(t.casefold())
                        text_arr_cleaned.append(t.casefold())
                    elif re.findall("\d\d\d\d", t):
                        text_arr_cleaned.append(t.casefold())
                        years.append(t)
                    elif t.casefold() not in [
                        "date",
                        "1st",
                        "2nd",
                        "(local)",
                        "(height)",
                        "tide",
                        "low",
                        "high",
                        "time",
                        "height",
                        "(cm)",
                    ]:
                        text_arr_cleaned.append(t)

            # cls.print(text_arr_cleaned)
            #     [
            # 'july',
            # '2023',
            # '1',
            # '12:02',
            # '54',
            # '23:11',
            # '57',
            # '05:29',
            # '6',
            # '17:28',
            # '28',
            # '2',
            # cls.print(months)
            # cls.print(years)
            tide_info = {
                "months": {},
                "month_format": {
                    "date": [
                        "1st High Tide (Time (Local))",
                        "1st High Tide (Height (cm))",
                        "2nd High Tide (Time (Local))",
                        "2nd High Tide (Height (cm))",
                        "1st Low Tide (Time (Local))",
                        "1st Low Tide (Height (cm))",
                        "2nd Low Tide (Time (Local))",
                        "2nd Low Tide (Height (cm))",
                    ]
                },
                "meta": {"months": []},
            }
            for i, month in enumerate(months):
                tide_info["meta"]["months"].append([months[i], years[i]])

            tc_i = 0
            current_month = None
            month_pad = 0
            while tc_i < len(text_arr_cleaned):
                text = text_arr_cleaned[tc_i]
                if text in month_names:
                    # current_month = f'{text_arr_cleaned[tc_i]}_{text_arr_cleaned[tc_i+1]}'
                    current_month = f"{text_arr_cleaned[tc_i]}"
                    tide_info["months"][current_month] = {}
                    month_pad += 1
                    tc_i += 2
                    continue
                else:
                    if (tc_i - (2 * month_pad)) % 9 == 0:
                        date = int(text_arr_cleaned[tc_i])
                        tide_info["months"][current_month][date] = text_arr_cleaned[
                            tc_i + 1 : tc_i + 9
                        ]
                        tc_i += 8
                tc_i += 1

            try:
                cls.add_to_cache("tides", tide_info)
            except Exception as e:
                raise e
            # cls.print(tide_info)
        return tide_info

    @classmethod
    def get_rainfall(cls, print=False):
        print_ = print

        try:
            cache = cls.get_from_cache("rainfall")
        except:
            # TODO Add debug if permm error cache
            cache = False
        if not cls.CACHE_PERMS:
            cache = False
        if cache:
            rainfall_data = cache
        else:
            cls.check_internet()

            URL = "http://metservice.intnet.mu/forecast-bulletin-english-mauritius.php"
            r = requests.get(URL, headers=cls.headers)
            soup = BeautifulSoup(r.content, "html.parser")

            content = soup.find("div", attrs={"class": "left_content"})

            content = [c for c in content.text.strip().split("\n") if c.strip()]

            info = None
            data = {}
            for line in content:
                if "highest rainfall" in line.casefold():
                    info = line.split("during the")[1].strip()[: -len(" today:")]
                if ("mm" in line) and (":" in line):
                    region = line.strip().split(":")[0].strip()
                    rain = line.strip().split(":")[1].strip()
                    data[region] = rain

            rainfall_data = {"info": info, "rain": data}
            try:
                cls.add_to_cache("rainfall", rainfall_data)
            except:
                pass

        return rainfall_data

    @classmethod
    def get_latest(cls, print=False):
        print_ = print
        infos = None

        cls.check_internet()

        URL = "http://metservice.intnet.mu/latest-weather-data.php"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")

        weather_info = soup.find_all("div", attrs={"class": "weatherinfo"})
        weather_info = [w.text.strip() for w in weather_info]

        tables = soup.find_all("table", attrs={"class": "tableau"})

        infos = {
            "rainfall24h": {},
            "rainfall3hrs": {},
            "wind": {},
            "humidity": {},
            "minmaxtemp": {},
        }

        for i, table in enumerate(tables):
            title = weather_info[i].replace("\r", "").replace("\n", "")
            if "humidity" in title.casefold():
                key = "humidity"
            elif "wind" in title.casefold():
                key = "wind"
            elif "maximum and minimum" in title.casefold():
                key = "minmaxtemp"
            elif "3hrs" in title.casefold():
                key = "rainfall3hrs"
            else:
                key = "rainfall24h"
            infos[key] = {"info": title, "data": {}}
            trs = table.find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                for itd, td in enumerate(tds):
                    if td.text.strip().replace(" ", "").isalpha():
                        try:
                            # infos.append(td.text.strip())
                            # infos.append(tds[itd+1].text.strip())
                            if key == "minmaxtemp":
                                # cls.print(tds)
                                infos[key]["data"][td.text.strip()] = {}
                                infos[key]["data"][td.text.strip()]["min"] = tds[
                                    itd + 1
                                ].text.strip()
                                infos[key]["data"][td.text.strip()]["max"] = tds[
                                    itd + 2
                                ].text.strip()

                            else:
                                infos[key]["data"][td.text.strip()] = tds[
                                    itd + 1
                                ].text.strip()

                        except Exception:
                            # cls.print(e)
                            pass

        return infos

    @classmethod
    def get_uvindex(cls, print=False):
        print_ = print

        regions = [
            "vacoas",
            "port-louis",
            "plaisance",
            "triolet",
            "camp-diable",
            "centre-de-flacq",
            "flic-en-flac",
            "tamarin",
            "rodrigues",
        ]

        try:
            cache = cls.get_from_cache("uvindex")
        except:
            # TODO Add debug if permm error cache
            cache = False
        if not cls.CACHE_PERMS:
            cache = False
        if cache:
            data = cache
        else:
            cls.check_internet()
            data = {}

            for region in regions:
                URL = f"https://en.tutiempo.net/ultraviolet-index/{region}.html"
                r = requests.get(URL, headers=cls.headers)
                soup = BeautifulSoup(r.content, "html.parser")

                uvindex = soup.find("div", attrs={"class": "UvIndex"})

                today = uvindex.find("h4")

                uv_status = today.text
                data[region] = uv_status
            try:
                cls.add_to_cache("uvindex", data)
            except:
                pass

        if print_:
            uv_string = ""
            for region, status in data.items():
                region = region.replace("-", " ").capitalize()
                if status.lower() == "extreme":
                    status = f"[blink]:fire: [red]{status}[/red][/blink]"
                elif status.lower() == "very high":
                    status = f"[red]{status}[/red]"
                elif status.lower() == "high":
                    status = f"[dark_orange3]{status}[/dark_orange3]"
                elif status.lower() in ["medium", "moderate"]:
                    status = f"[gold3]{status}[/gold3]"
                elif status.lower() == "low":
                    status = f"[green]{status}[/green]"
                uv_string += f"[magenta]{region}[/magenta]: {status}\n"
            uv_string.strip("\n")
            uv_panel = Panel(
                uv_string, expand=True, title="Ultra-Violet index for Mauritius"
            )
            cls.print(uv_panel)
        else:
            return data
