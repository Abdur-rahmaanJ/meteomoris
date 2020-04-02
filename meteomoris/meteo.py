import requests
from bs4 import BeautifulSoup
from pprint import pprint

URL = 'http://metservice.intnet.mu'

r = requests.get(URL)

soup = BeautifulSoup(r.content, 'html.parser')

def __download_file(url, path):
    r = requests.get(url, allow_redirects=True)
    open(path, 'wb').write(r.content)

def get_weekforecast(day=None):
    w_forecast = soup.find(attrs={'class': 'daysforecast'})
    week_forcecast = w_forecast.find_all(attrs={'class': 'forecast'})

    week = {
        0: {},
        1: {},
        2: {},
        3: {},
        4: {},
        5: {},
        6: {}
    }

    for i, _day in enumerate(week_forcecast):
        fulldate = _day.find(attrs={'class': 'fday'})
        fdate = fulldate.text.split(',')
        date_day = fdate[0]
        date_date = fdate[1].strip()
        week[i]['day'] = date_day
        week[i]['date'] = date_date

        condition = _day.find(attrs={'class': 'fcondition'})
        week[i]['condition'] = condition.text

        temp = _day.find_all(attrs={'class': 'ftemp'})
        min_temp = temp[0].text
        max_temp = temp[1].text
        week[i]['min'] = min_temp
        week[i]['max'] = max_temp

        fgrey = _day.find_all(attrs={'class': 'fgrey'})
        wind = fgrey[0].text
        sea_condition = fgrey[1].text
        week[i]['wind'] = wind
        week[i]['sea condition'] = sea_condition

        prob = _day.find_all(attrs={'class': 'fgrey1'})
        probability = prob[0].text
        week[i]['probability'] = probability
    # pprint(week)

    return_data = {}

    if day is None:
        return_data = week
    else:
        return_data = week[day]

    return return_data

# pprint(get_weekforecast()[0])

def get_cityforecast(day=None):
    # for city of PL
    w_forecast = soup.find(attrs={'class': 'city_forecast'})
    week_forcecast = w_forecast.find_all(attrs={'class': 'block'})

    week = {
        0: {},
        1: {},
        2: {},
        3: {},
        4: {}
    }

    for i, _day in enumerate(week_forcecast):
        date_day = _day.find(attrs={'class': 'cday'})
        week[i]['day'] = date_day.text[:-1]

        date_date = _day.find(attrs={'class': 'cdate'})
        week[i]['date'] = date_date.text

        condition = _day.find(attrs={'class': 'fcondition'})
        week[i]['condition'] = condition.text

        min_temp = _day.find(attrs={'class': 'ctemp'})
        week[i]['min'] = min_temp.text

        max_temp = _day.find(attrs={'class': 'ctemp1'})
        week[i]['max'] = max_temp.text

        wind = _day.find(attrs={'class': 'cwind1'})
        week[i]['wind'] = wind.text

    return_data = {}

    if day is None:
        return_data = week
    else:
        return_data = week[day]

    return return_data


def get_moonphase(month=None):
    # should we give time as 12:34?
    moonphase_url = 'http://metservice.intnet.mu/sun-moon-and-tides-moon-phase.php'
    moon_r = requests.get(moonphase_url).content
    moon_soup = BeautifulSoup(moon_r, 'html.parser')
    table = moon_soup.find('table')
    rows = table.find_all('tr')
    months = rows[0].find_all('p')
    month1 = months[0].text
    month2 = months[1].text

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

def get_main_message():
    """
    Get the main message of website
    """
    message = soup.find('div', attrs={'class': 'warning'})
    return message.text.strip()

#this will return the relevant eclipse information as a string

def get_eclipse_text():
    '''small function to scrape the eclipse data from a website'''
    
    url = 'http://metservice.intnet.mu/sun-moon-and-tides-info-eclipses.php'
    r = requests.get(url)
    page_soup = BeautifulSoup(r.text, "html.parser")
    page_container = page_soup.find("div", {"class":"left_content"}).findAll("p")
    page_container = page_container[1:-1]

    eclipse_text = ''
    for line in page_container:
        eclipse_text += line.text + '\n'

    return eclipse_text

def get_cyclone_text():
    '''small function to scrape the cyclone data from a website'''
    #getting the request info
    r = requests.get("http://metservice.intnet.mu/current-cyclone.php")
    s = BeautifulSoup(r.content, "html.parser")
    #getting the info tag text
    info = s.find("div", attrs={"style" : "width: 20%; float:right"}).text.strip()
    if(info==''):
        return ">NO CYCLONES NOW<"
    else:
        return info

# TODO
#def download_moonphase_pdf(path):
#    url = 'http://metservice.intnet.mu/mmsimages/Phases%20of%20the%20Moon2019.pdf'
#    __download_file(url, path)
#    print('downloaded moonphase pdf')
