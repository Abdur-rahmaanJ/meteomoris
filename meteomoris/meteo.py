import requests
from bs4 import BeautifulSoup
from pprint import pprint

URL = 'http://metservice.intnet.mu'

r = requests.get(URL)

soup = BeautifulSoup(r.content, 'html.parser')

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

pprint(get_cityforecast())