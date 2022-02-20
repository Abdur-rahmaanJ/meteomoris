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
except Exception as e:
    pass

import sys




# def __download_file(url, path):
#     r = requests.get(url, allow_redirects=True)
#     open(path, 'wb').write(r.content)
console = Console()

def internet_present(exit=False):
    
    domains = [
        'https://google.com',
        'https://yahoo.com',
        'https://bing.com',
        'https://www.ecosia.org',
        'https://www.wikipedia.org'
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
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5', 
    'Accept-Encoding' : 'gzip', 
    'DNT' : '1', # Do Not Track Request Header 
    'Connection' : 'close',
    'Sec-GPC': '1',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
    
    
    @classmethod
    def check_internet(cls):
        if cls.CHECK_INTERNET:
            if not internet_present():
                print('No internet')
                if cls.EXIT_ON_NO_INTERNET:
                    sys.exit()
    @classmethod
    def get_weekforecast(cls, day=None):
        cls.check_internet()


        URL = 'http://metservice.intnet.mu'
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        w_forecast = soup.find(attrs={'class': 'daysforecast'})

        week_forcecast = w_forecast.find_all(attrs={'class': 'forecast'})

        week = []

        for i, _day in enumerate(week_forcecast):
            fulldate = _day.find(attrs={'class': 'fday'})
            fdate = fulldate.text.split(',')
            date_day = fdate[0]
            date_date = fdate[1].strip()
            
            return_dict = {}

            return_dict['day'] = date_day
            return_dict['date'] = date_date

            condition = _day.find(attrs={'class': 'fcondition'})
            return_dict['condition'] = condition.text

            temp = _day.find_all(attrs={'class': 'ftemp'})
            min_temp = temp[0].text
            max_temp = temp[1].text
            return_dict['min'] = min_temp
            return_dict['max'] = max_temp

            fgrey = _day.find_all(attrs={'class': 'fgrey'})
            wind = fgrey[0].text
            sea_condition = fgrey[1].text
            return_dict['wind'] = wind
            return_dict['sea condition'] = sea_condition

            prob = _day.find_all(attrs={'class': 'fgrey1'})
            probability = prob[0].text
            return_dict['probability'] = probability
            
            week.append(return_dict)

        return_data = {}

        if day is None:
            return_data = week
        else:
            return_data = week[day]

        return return_data

    @classmethod
    def get_cityforecast(cls, day=None):
        cls.check_internet()
        # for city of PL

        URL = 'http://metservice.intnet.mu'
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        w_forecast = soup.find(attrs={'class': 'city_forecast'})
        week_forcecast = w_forecast.find_all(attrs={'class': 'block'})

        week = []

        for i, _day in enumerate(week_forcecast):
            date_day = _day.find(attrs={'class': 'cday'})
            return_dict = {}
            return_dict['day'] = date_day.text[:-1]

            date_date = _day.find(attrs={'class': 'cdate'})
            return_dict['date'] = date_date.text

            condition = _day.find(attrs={'class': 'fcondition'})
            return_dict['condition'] = condition.text

            min_temp = _day.find(attrs={'class': 'ctemp'})
            return_dict['min'] = min_temp.text

            max_temp = _day.find(attrs={'class': 'ctemp1'})
            return_dict['max'] = max_temp.text

            wind = _day.find(attrs={'class': 'cwind1'})
            return_dict['wind'] = wind.text


            week.append(return_dict)

        return_data = {}

        if day is None:
            return_data = week
        else:
            return_data = week[day]

        return return_data

    @classmethod
    def get_moonphase(cls, month=None):
        cls.check_internet()
        # should we give time as 12:34?
        moonphase_url = 'http://metservice.intnet.mu/sun-moon-and-tides-moon-phase.php'
        moon_r = requests.get(moonphase_url, headers=cls.headers).content
        moon_soup = BeautifulSoup(moon_r, 'html.parser')
        table = moon_soup.find('table')
        rows = table.find_all('tr')
        months = rows[0].find_all('p')
        month1 = months[0].text.strip()
        month2 = months[1].text.strip()

        moon_phase = {
            month1: {},
            month2: {}
        }

        data_rows = rows[2:]

        def assign(key):
            moon_phase[month1][key] = {}
            moon_phase[month1][key]['date'] = info[1]
            moon_phase[month1][key]['hour'] = info[2]
            moon_phase[month1][key]['minute'] = info[3]

            moon_phase[month2][key] = {}
            moon_phase[month2][key]['date'] = info[5]
            moon_phase[month2][key]['hour'] = info[6]
            moon_phase[month2][key]['minute'] = info[7]

        for i, row in enumerate(data_rows):
            info = row.find_all('p')
            info = [i.text for i in info]
            if i == 0:
                assign('new moon')
            elif i == 1:
                assign('first quarter')
            elif i == 2:
                assign('full moon')
            elif i == 3:
                assign('last quarter')

        if month is None:
            return moon_phase
        else:
            return moon_phase[month]

    @classmethod
    def get_main_message(cls):
        """
        Get the main message of website
        """
        cls.check_internet()
        URL = 'http://metservice.intnet.mu'
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        message = soup.find('div', attrs={'class': 'warning'})
        return message.text.strip()

    @classmethod
    def get_eclipse_text(cls):
        '''small function to scrape the eclipse data from a website'''
        
        url = 'http://metservice.intnet.mu/sun-moon-and-tides-info-eclipses.php'
        r = requests.get(url, headers=cls.headers)
        page_soup = BeautifulSoup(r.text, "html.parser")
        page_container = page_soup.find("div", {"class":"left_content"}).findAll("p")
        page_container = page_container[1:-1]

        eclipse_text = ''
        for line in page_container:
            eclipse_text += line.text + '\n'

        return eclipse_text


    @classmethod
    def test(cls):
        print('test ok')


    @classmethod
    def get_sunrisemu(cls):
        cls.check_internet()
        URL = 'http://metservice.intnet.mu/sun-moon-and-tides-sunrise-sunset-mauritius.php'
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        table = soup.find('table')
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        data = dict()
        for i, row in enumerate(rows):
            cols = row.find_all('td')

            cols = [ele.text.strip() for ele in cols]

            if i == 0:
                month1 = cols[1].lower()
                month2 = cols[2].lower()
                data = {
                    month1: {},
                    month2: {}
                }

            elif i > 1:
                date = int(cols[0])
                m1_rise = cols[1]
                m1_set = cols[2]
                m2_rise = cols[3]
                m2_set = cols[4]

                if (m1_rise and m1_set):
                    data[month1][date] = {'rise': m1_rise, 'set': m1_set}
                if (m2_rise and m2_set):
                    data[month2][date] = {'rise': m2_rise, 'set': m2_set}

        return data


    @classmethod
    def get_sunriserodr(cls):
        cls.check_internet()
        URL = 'http://metservice.intnet.mu/sun-moon-and-tides-sunrise-sunset-rodrigues.php'
        r = requests.get(URL, headers=cls.headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        table = soup.find('table')
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        data = dict()
        for i, row in enumerate(rows):
            cols = row.find_all('td')

            cols = [ele.text.strip() for ele in cols]

            if i == 0:
                month1 = cols[1].lower()
                month2 = cols[2].lower()
                data = {
                    month1: {},
                    month2: {}
                }

            elif i > 1:
                date = int(cols[0])
                m1_rise = cols[1]
                m1_set = cols[2]
                m2_rise = cols[3]
                m2_set = cols[4]

                if (m1_rise and m1_set):
                    data[month1][date] = {'rise': m1_rise, 'set': m1_set}
                if (m2_rise and m2_set):
                    data[month2][date] = {'rise': m2_rise, 'set': m2_set}

        return data