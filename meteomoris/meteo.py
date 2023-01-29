try:
    # Poor solution for calling pure python codes
    # when the packaging system is installing the
    # package. Due to a poorly designed user experience
    # from the PyPA, i'll let it like this until things
    # have settled
    import requests
    from bs4 import BeautifulSoup
    from pprint import pprint
    from rich.console import Console
    from rich.columns import Columns
    from rich.table import Table
    from rich.panel import Panel
    import datetime
    import calendar
except Exception as e:
    pass

import sys


# def __download_file(url, path):
#     r = requests.get(url, allow_redirects=True)
#     open(path, 'wb').write(r.content)



def internet_present(exit=False):
    console = Console()
    domains = [
        "https://google.com",
        "https://yahoo.com",
        "https://bing.com",
        "https://www.ecosia.org",
        "https://www.wikipedia.org",
    ]
    results = []
    with console.status("Checking internet ...", spinner="material"):
        for domain in domains:
            try:
                requests.get(domain)
                results.append(1)
            except Exception as e:
                results.append(0)

    if not any(results):
        # print('No internet connection')
        if exit:
            sys.exit()
        return False
    else:
        return True


class Meteo:

    EXIT_ON_NO_INTERNET = False
    CHECK_INTERNET = False
    DEBUG = False

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

    @classmethod
    def check_internet(cls):
        if cls.CHECK_INTERNET:
            if not internet_present():
                print("No internet")
                if cls.EXIT_ON_NO_INTERNET:
                    sys.exit()

    @classmethod
    def get_weekforecast(cls, day=None, print=False):
        print_ = print
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

        return_data = {}

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
            return_data = week

            if print_:
                table.title = 'Week forecast'
                for d in return_data:
                    table.add_row(d['day'], d['date'], d['min'], d['max'], d['condition'], d['sea condition'], d['wind'], d['probability'])
                console.print(table)
                return
        else:
            return_data = week[day]

            if print_:
                table.title = 'Day forecast'
                d = return_data
                table.add_row(d['day'], d['date'], d['min'], d['max'], d['condition'], d['sea condition'], d['wind'], d['probability'])
                console.print(table)
                return

        return return_data

    @classmethod
    def get_cityforecast(cls, print=False, day=None):
        print_ = print
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


        if print_:
            console = Console()
            table = Table()
            table.add_column("Day", justify="left", style="magenta", no_wrap=True)
            table.add_column("Date", justify="left", no_wrap=True)
            table.add_column("Min", justify="left", no_wrap=True)
            table.add_column("Max", justify="left", no_wrap=True)
            table.add_column("Condition", justify="left")
            table.add_column("Wind", justify="left", no_wrap=True)

        return_data = {}

        if day is None:
            return_data = week

            if print_:
                table.title = 'Week forecast'
                for d in return_data:
                    table.add_row(d['day'], d['date'], d['min'], d['max'], d['condition'], d['wind'])
                console.print(table)
                return
        else:
            return_data = week[day]

            if print_:
                table.title = 'Day forecast'
                d = return_data
                
                table.add_row(d['day'], d['date'], d['min'], d['max'], d['condition'], d['wind'])
                console.print(table)
                return
            

        return return_data

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


            if i == 0: # first row
                month1 = cols[0].lower()
                month2 = cols[1].lower()
                data = {month1.casefold(): {}, month2.casefold(): {}}

            elif (1 < i < 6): # 3rd row and above
                m1_phase = cols[0]
                m1_date = int(cols[1])
                m1_hour = int(cols[2])
                m1_min = int(cols[3])

                m2_phase = cols[4]
                m2_date = int(cols[5])
                m2_hour = int(cols[6])
                m2_min = int(cols[7])

                code_lookup = {
                    'N.M': 'new moon',
                    'F.Q': 'first quarter',
                    'F.M': 'full moon',
                    'L.Q': 'last quarter'
                }

                phase1 = code_lookup[m1_phase]
                data[month1][phase1] = {
                    "date": m1_date, 
                    "hour": m1_hour,
                    "minute": m1_min
                    }

                phase2 = code_lookup[m2_phase]
                data[month2][phase2] = {
                    "date": m2_date, 
                    "hour": m2_hour,
                    "minute": m2_min
                    }


        if print_:
            console = Console()
            table = Table(title='Moon Phase')
            table.add_column('Month', justify="left", style="magenta", no_wrap=True)
            table.add_column('New Moon', justify="left", style="magenta", no_wrap=True)
            table.add_column('First Quarter', justify="left", style="magenta", no_wrap=True)
            table.add_column('Full Moon', justify="left", style="magenta", no_wrap=True)
            table.add_column('Last Quarter', justify="left", style="magenta", no_wrap=True)

        def get_moon_str(d, key):
            try:
                return '{} at {}:{}'.format(d[key]['date'], str(d[key]['hour']).zfill(2), str(d[key]['minute']).zfill(2))
            except KeyError:
                return ''
        if month is None:
            
            if print_:
                for k, d in data.items():
                    nm = get_moon_str(d, 'new moon')
                    fq = get_moon_str(d, 'first quarter')
                    fm = get_moon_str(d, 'full moon')
                    lq = get_moon_str(d, 'last quarter')
                    table.add_row(k, nm, fq, fm, lq)

                console.print(table)
                return

            return data
        else:
            if print_:
                d = data[month]
                nm = get_moon_str(d, 'new moon')
                fq = get_moon_str(d, 'first quarter')
                fm = get_moon_str(d, 'full moon')
                lq = get_moon_str(d, 'last quarter')
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
            message_links = [(link.text.strip(), link.get('href')) for link in message.find_all('a')]
            if print_:
                console = Console()
                table = Table(title='Info')
                table.add_column('Message')
                table.add_column('Link')
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
        unwanted = message.find('div', attrs={"class": "warning"})
        unwanted.extract()

        data = message.text.strip()

        if print_:
            cls.print(
                Panel(data)
                )
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

        def get_sun_info(data, month, date, point):
            try:
                return '{}'.format(data[month][date][point])
            except:
                return ''
        if print_:
            console = Console()
            table = Table(title='Sunrise (Mauritius)')

            table.add_column('', justify="left", no_wrap=True)
            months = list(data.keys())
            for m in months:
                table.add_column(m, justify="left", no_wrap=True)

            for i in range(1, 32):
                table.add_row(str(i).zfill(2), get_sun_info(data, months[0], i, 'rise'), get_sun_info(data, months[1], i, 'set'))

            console.print(table)
            return 
        return data

    @classmethod
    def get_sunriserodr(cls, print=False):
        print_ = print
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
        def get_sun_info(data, month, date, point):
            try:
                return '{}'.format(data[month][date][point])
            except:
                return ''
        if print_:
            console = Console()
            table = Table(title='Sunrise (Rodrigues)')

            table.add_column('', justify="left", no_wrap=True)
            months = list(data.keys())
            for m in months:
                table.add_column(m, justify="left", no_wrap=True)

            for i in range(1, 32):
                table.add_row(str(i).zfill(2), get_sun_info(data, months[0], i, 'rise'), get_sun_info(data, months[1], i, 'set'))

            console.print(table)
            return 

        return data


    @classmethod
    def get_eclipses_raw(cls):
        cls.check_internet()
        URL = "http://metservice.intnet.mu/sun-moon-and-tides-info-eclipses.php"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")

        tables = soup.find_all("table")

        len_tables = len(tables)
        data = {'eclipses':[]}
        year = None
        eclipse_info = {}
        all_tables = []
        equinoxes = []
        # cls.print(str(len(tables)))
        for table_index, table in enumerate(tables):
            current_list = table.text.strip().split('\n')
            current_list = [e for e in current_list if bool(e.strip())]
            if table_index == 0:
                pass 

            elif table_index == len(tables)-1:
                equinoxes = current_list
            else:
                
                all_tables += current_list
        '''
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
        '''
        eclipse_info = []
        
        if cls.DEBUG:
            cls.print(all_tables)
        '''
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
        '''
        for table_index, row in enumerate(all_tables):
            info = {}
            if (
                ('eclipse of the' in row.casefold()) and
                ('-' in row.casefold())
                ):
                info['title'] = row.split(' - ')[0].strip()
                info['info'] = all_tables[table_index+2]
                if 'sun' in info['title'].casefold():
                    info['type'] = 'sun'
                elif 'moon' in info['title'].casefold():
                    info['type'] = 'moon'
                info['status'] = info['title'].casefold().split()[0].strip()

                # info['date'] = row.split(' - ')[1].strip()

                next_row = all_tables[table_index+1]

                next_row_words = next_row.split()
                for i, word in enumerate(next_row_words):
                    if word == 'begins':
                        if next_row_words[i+1] == 'on':
                            info['start'] = {}
                            info['start']['date'] = int(next_row_words[i+2])
                            info['start']['month'] = next_row_words[i+3].casefold()
                            info['start']['hour'] = int(next_row_words[i+5].split('h')[0].strip('.'))
                            info['start']['minute'] = int(next_row_words[i+5].split('h')[1].strip('.'))
                    if word == 'ends':
                        if next_row_words[i+1] == 'on':
                            info['end'] = {}
                            info['end']['date'] = int(next_row_words[i+2])
                            info['end']['month'] = next_row_words[i+3].casefold()
                            info['end']['hour'] = int(next_row_words[i+5].split('h')[0].strip('.'))
                            info['end']['minute'] = int(next_row_words[i+5].split('h')[1].strip('.'))
                        elif next_row_words[i+1] == 'at':
                            info['end'] = {}
                            info['end']['date'] = int(info['start']['date'])
                            info['end']['month'] = info['start']['month'].casefold()
                            info['end']['hour'] = int(next_row_words[i+2].split('h')[0].strip('.'))
                            info['end']['minute'] = int(next_row_words[i+2].split('h')[1].strip('.'))

                eclipse_info.append(info)

        if cls.DEBUG:
            cls.print(equinoxes)
        '''
        [
            'EQUINOXES and SOLSTICES - 2023',
            'Equinoxes\xa0\xa0\xa0 :\xa0 \xa0March 21 at 01h24 and September 23 at 10h50.',
            'Solstices\xa0\xa0\xa0 :\xa0 \xa0June 21 at 18h57 and December 22 at 07h27.'
        ]
        '''
        equinox = [e.strip().casefold().strip('.') for e in equinoxes[1].split()]
        solstice = [e.strip().casefold().strip('.') for e in equinoxes[2].split()]
        year = equinoxes[0].split(' - ')[1].strip().casefold()
        year = int(year)
        '''

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
        ]'''
        equinox_info = None
        for i, e in enumerate(equinox):
            if e == 'and':
                equinox_info = [
                {
                    'day': int(equinox[i-3]),
                    'month': equinox[i-4],
                    'year': year,
                    'hour': int(equinox[i-1].split('h')[0]),
                    'minute': int(equinox[i-1].split('h')[1]),
                },
                {
                    'day': int(equinox[i+2]),
                    'month': equinox[i+1],
                    'year': year,
                    'hour': int(equinox[i+4].split('h')[0]),
                    'minute': int(equinox[i+4].split('h')[1]),
                },
                ] 


        solstice_info = None
        for i, e in enumerate(equinox):
            if e == 'and':
                solstice_info = [
                {
                    'day': int(solstice[i-3]),
                    'month': solstice[i-4],
                    'year': year,
                    'hour': int(solstice[i-1].split('h')[0]),
                    'minute': int(solstice[i-1].split('h')[1]),
                },
                {
                    'day': int(solstice[i+2]),
                    'month': solstice[i+1],
                    'year': year,
                    'hour': int(solstice[i+4].split('h')[0]),
                    'minute': int(solstice[i+4].split('h')[1]),
                },
                ] 

        return {
            'eclipses': eclipse_info,
            'equinoxes': equinox_info,
            'solstices': solstice_info
        }

    @classmethod
    def get_eclipses(cls):
        return cls.get_eclipses_raw()['eclipses']


    @classmethod
    def get_equinoxes(cls):
        return cls.get_eclipses_raw()['equinoxes']


    @classmethod
    def get_solstices(cls):
        return cls.get_eclipses_raw()['solstices']


    @classmethod
    def print_today(cls, country='mu'):
        '''
        All info for today

        Check week forecast from today
        Check moonphase info
        Check solstice, eclipse and equinox
        Print sunrise and sunset
        '''
        if country not in ['mu', 'rodr']:
            cls.print('[red]Country should be mu or rodr[/red]')

        day = datetime.datetime.now().day
        month = calendar.month_name[datetime.datetime.now().month].casefold()
        year = datetime.datetime.now().year
        # cls.print(day)
        # cls.print(year)
        # cls.print(month)

        forecast = cls.get_weekforecast(day=0)
        moonphase = cls.get_moonphase()['{} {}'.format(month, year)]
        if country == 'mu':
            sun = cls.get_sunrisemu()[month][day]
        else:
            sun = cls.get_sunriserodr()[month][day]
        

        # cls.print(forecast)

        # day_ = 22
        # month_ = 'january'

        # day = day_ 
        # month = month_

        col_elems = []


        for phase in moonphase:
            if moonphase[phase]['date'] == day:
                elements = []
                elements.extend([
                phase.title(), 'today at', 
                    '[green]{}:{}[/green]'.format(
                        moonphase[phase]['hour'], moonphase[phase]['minute'])
                    ])

                moonphase_string = ' '.join(elements)
                break

            else:
                moonphase_string = ''


        eclipse_elements = []
        for eclipse in cls.get_eclipses():
            

            if (
                eclipse['start']['date'] == day and
                eclipse['start']['month'] == month):
                
                eclipse_elements.extend([eclipse['title'], 'starts today at', 
                    '[green]{}:{}[/green]'.format(eclipse['start']['hour'], eclipse['start']['minute']),
                    eclipse['info']])



            if (
                eclipse['end']['date'] == day and
                eclipse['end']['month'] == month):

                eclipse_elements.extend([
                    '\n',
                    eclipse['title'], 'ends today at', 
                    '[green]{}:{}[/green]'.format(eclipse['end']['hour'], eclipse['end']['minute']),
                    eclipse['info']
                    ]) 


        eclipse_string = ' '.join(eclipse_elements).replace('\n ', '\n')
            # col_elems.append(Panel(string, expand=True, title="Eclipse"))


        for equinox in cls.get_equinoxes():
            if (
                equinox['day'] == day and 
                equinox['month'] == month 
                ):
                elements = []
                elements.extend([
                'Equinox today at', '[green]{}:{}[/green]'.format(equinox['hour'], equinox['minute'])
                ])

                equinox_string = ' '.join(elements)
            else:
                equinox_string = ''    

        for solstice in cls.get_solstices():
            if (
                solstice['day'] == day and 
                solstice['month'] == month 
                ):
                elements = []
                elements.extend([
                    'Solstice today at', '[green]{}:{}[/green]'.format(solstice['hour'], solstice['minute'])
                    ])


                solstice_string = ' '.join(elements)
            else:
                solstice_string = ''
  
        
        grid = Table.grid()
        grid.add_column()
        grid.add_column()
        grid.add_column()
        temp_str = '[b]{}-{}[/]'.format(forecast["min"], forecast["max"])
        temp_panel = Panel(temp_str, expand=True, title="Temperature")

        wind_panel = Panel(forecast["wind"], expand=True, title="Wind")
        sea_panel = Panel(forecast["sea condition"], expand=True, title="Sea condition")

        solstice_panel = Panel(solstice_string, expand=True, title="Solstice")
        equinox_panel = Panel(equinox_string, expand=True, title="Equinox")
        eclipse_panel = Panel(eclipse_string, expand=True, title="Eclipse")
        moonphase_panel = Panel(moonphase_string, expand=True, title="Moon phase")
        condition_panel = Panel(forecast["condition"], expand=True, title="Contition")
        
        sun_panel = Panel('rises at {}\nsets at {}'.format(sun['rise'], sun['set']), expand=True, title="Sun")
        
        messages = ['[bold]{}[/bold]  {}'.format(l[0], l[1]) for l in cls.get_main_message(links=True)]
        message_panel = Panel('\n'.join(messages), expand=True, title='Message')

        ###
        #
        # Tides
        #
        ###

        tides_all = cls.get_tides()

        tides = tides_all['months'][month][day]
        tidetable = Table()

        tidetable.add_column("Tide", justify="left", style="slate_blue3", no_wrap=True)
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


        tidetable.add_row('1st high', tides[0], tides[1])
        tidetable.add_row('2nd high', tides[2], tides[3])
        tidetable.add_row('1st low', tides[4], tides[5])
        tidetable.add_row('2nd low', tides[6], tides[7])
        tides_panel = Panel(tidetable, expand=True, title='Tides')


        ###
        #
        # Rainfall
        #
        ###

        latest = cls.get_latest()

        rainfall = latest['rainfall24h']

        rainfall_info_str = '{}'.format(rainfall['info'])

        rtable = Table()

        rtable.add_column("Region", justify="left", style="slate_blue3")
        rtable.add_column("Rain 24hr", style="dark_cyan")
        rtable.add_column("Rain 3hrs", style="dark_cyan")
        rtable.add_column("Wind", style="dark_cyan")
        rtable.add_column("Humidity", style="dark_cyan")
        rtable.add_column("Min Max temp", style="dark_cyan")

        for r, a in rainfall['data'].items():
            if (latest['minmaxtemp']['data'][r]['min'] or latest['minmaxtemp']['data'][r]['max']):
                minmaxtemp_str = '{} to {}'.format(latest['minmaxtemp']['data'][r]['min'], latest['minmaxtemp']['data'][r]['max'])
            else:
                minmaxtemp_str = ''
            rtable.add_row(r, a, 
                latest['rainfall3hrs']['data'][r],
                latest['wind']['data'][r],
                latest['humidity']['data'][r],
                minmaxtemp_str
                )

        latest_panel = Panel(rtable, expand=True, title="Latest data")
        titles = ['- {}\n'.format(v['info']) for k, v in latest.items()]
        titles_str = ''.join(titles)
        
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
        
        grid.add_row('', message_panel,'')
        grid.add_row(temp_panel, wind_panel, sea_panel)
        grid.add_row(moonphase_panel, condition_panel, sun_panel)
        grid.add_row(solstice_panel, latest_panel, tides_panel)
        grid.add_row(equinox_panel, eclipse_panel, '')
        

        cls.print(
            Panel(
            grid,
            expand=True,
            title="Today"
            )
            )

    @classmethod
    def get_tides(cls, print=False):
        print_ = print

        URL = "http://metservice.intnet.mu/sun-moon-and-tides-tides-mauritius.php"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")
        h2s = soup.find_all("h2")
        tables = soup.find_all("table")

        tide_info = None

        month1 = tables[0]
        month2 = tables[1]
        
        month1 = [e.strip() for e in month1.text.strip().split('\n') if e.strip()]
        month1 = month1[13:]

        month2 = [e.strip() for e in month2.text.strip().split('\n') if e.strip()]
        month2 = month2[14:]

        h2txts = [h2.text for h2 in h2s]
        h2txt = ' '.join(h2txts)

        month1_name = h2txt.casefold().split(' for ')[1].split()[0]
        month2_name = h2txt.casefold().split(' for ')[1].split()[2]
        year = int(h2txt.casefold().split(' for ')[1].split()[3])

        tide_info = {
            'months': {
                month1_name: {},
                month2_name: {}
            },
            'year': year,
            'month_format': {
                'date': [
                '1st High Tide (Time (Local))', 
                '1st High Tide (Height (cm))',
                '2nd High Tide (Time (Local))', 
                '2nd High Tide (Height (cm))',
                '1st Low Tide (Time (Local))', 
                '1st Low Tide (Height (cm))',
                '2nd Low Tide (Time (Local))', 
                '2nd Low Tide (Height (cm))',
                ]
            }
        }

        # cls.print(tide_info)
        for i, e in enumerate(month1):
            if ((i) % 9) == 0:
                tide_info['months'][month1_name][int(e)] = month1[i+1:i+9]

        for i, e in enumerate(month2):
            if ((i) % 9) == 0:
                tide_info['months'][month2_name][int(e)] = month2[i+1:i+9]

        return tide_info


    @classmethod
    def get_rainfall(cls, print=False):
        print_ = print

        URL = "http://metservice.intnet.mu/forecast-bulletin-english-mauritius.php"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")

        content = soup.find("div", attrs={'class': 'left_content'})

        content = [c for c in content.text.strip().split('\n') if c.strip()]

        info = None
        data = {}
        for line in content:
            if 'highest rainfall' in line.casefold():
                info = line.split('during the')[1].strip()[:-len(' today:')]
            if (
                ('mm' in line) and
                (':' in line) 
                ):
                region = line.strip().split(':')[0].strip()
                rain = line.strip().split(':')[1].strip()
                data[region] = rain

        rainfall_data = {
            'info': info,
            'rain': data
        }

        return rainfall_data


    @classmethod
    def get_latest(cls, print=False):
        print_ = print

        URL = "http://metservice.intnet.mu/latest-weather-data.php"
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, "html.parser")


        weather_info = soup.find_all('div', attrs={'class': 'weatherinfo'})
        weather_info = [w.text.strip() for w in weather_info]

        tables = soup.find_all("table", attrs={'class': 'tableau'})


        infos = {
            "rainfall24h": {},
            "rainfall3hrs": {},
            "wind": {},
            "humidity": {},
            "minmaxtemp": {}
        }

        for i, table in enumerate(tables):
            title = weather_info[i].replace('\r', '').replace('\n', '')
            if 'humidity' in title.casefold():
                key = 'humidity'
            elif 'wind' in title.casefold():
                key = 'wind'
            elif 'maximum and minimum' in title.casefold():
                key = 'minmaxtemp'
            elif '3hrs' in title.casefold():
                key = 'rainfall3hrs'
            else:
                key = 'rainfall24h'
            infos[key] = {
                'info': title,
                'data': {}
            }
            trs = table.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                for itd, td in enumerate(tds):
                    if td.text.strip().replace(' ', '').isalpha():
                        try:
                            # infos.append(td.text.strip())
                            # infos.append(tds[itd+1].text.strip())
                            if key == 'minmaxtemp':
                                #cls.print(tds)
                                infos[key]['data'][td.text.strip()] = {}
                                infos[key]['data'][td.text.strip()]['min'] = tds[itd+1].text.strip()
                                infos[key]['data'][td.text.strip()]['max'] = tds[itd+2].text.strip()
                                
                            else:
                                infos[key]['data'][td.text.strip()] = tds[itd+1].text.strip()

                        except Exception as e:
                            #cls.print(e)
                            pass
        return infos
