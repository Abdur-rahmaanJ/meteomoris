# meteomoris

get info about the weather in mauritius!

```
pip install meteomoris
```

Venv explanations at footer.

# Ubuntu

```
sudo add-apt-repository ppa:abdur-rahmaanj/meteomoris-ppa
sudo apt update
sudo apt-get install meteomoris
```

# Important changes

- year output removed from tides, added a meta label for year and month

# Examples

NOTE: Add `print=True` to get a tabular representation

```python
>>> from meteomoris import *

>>> get_main_message()
"A Strong Wind Warning and High Wave Warning for Mauritius | Aucun avertissement de cyclone n'est en vigueur a Maurice | Avertissement de fortes houles pour Rodrigues"
>>> get_main_message(links=True)
[
   ('The Mauritius Meteorological Services (Warnings) Regulations 2023', 'http://metservice.intnet.mu/about-us/legislations/'), 
   ('Heavy Rain warning Bulletin for Mauritius issued at 0500 hours on Thursday 19 January 2023, valid until 0500 hours  Friday 20 January 2023.', 'http://metservice.intnet.mu/warning-bulletin-special-weather.php')
]
>>> get_special_whether_bulletin()
Special Weather Bulletin
Thu, Jan 19, 2023Heavy Rain warning Bulletin for Mauritius issued at 0500 hours on Thursday 19 January 2023, valid until 0500 hours  Friday 20 January 2023. 
 
Heavy rain warning is in force in Mauritius
Active clouds coming from the North-East are influencing the local weather.
Moderate to heavy showers with thunderstorms are expected over the island.
 
The public is advised to:
1. Remain in safe places and avoid open areas, hikings, sea ventures and sheltering under trees during thunderstorms.
2. Avoid places prone to water accumulation, river banks and other water courses which are flooded and certain mountain slopes prone to landslide
3. Be very cautious on the roads due to reduced visibility resulting from heavy rains and fog patches

...
>>> get_weekforecast()
[
 {
   'condition': 'Few showers highgrounds',
   'date': 'Apr 22',
   'day': 'Mon',
   'max': '32�',
   'min': '21�',
   'probability': 'High',
   'sea condition': 'rough',
   'wind': 'E25G50'
 },
 {
...
 }
]
>>> get_weekforecast(print=True)
                                                     Week forecast                                                     
┏━━━━━┳━━━━━━━━┳━━━━━┳━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Day ┃ Date   ┃ Min ┃ Max ┃ Condition                                                     ┃ Sea condition ┃ Wind     ┃
┡━━━━━╇━━━━━━━━╇━━━━━╇━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Thu │ Jan 19 │ 19° │ 30° │ Moderate to locally heavy showers with isolated thunderstorms │ rough         │ ENE25G50 │
│ Fri │ Jan 20 │ 20° │ 30° │ Moderate to locally heavy showers with isolated thunderstorms │ rough         │ NE20     │
│ Sat │ Jan 21 │ 20° │ 30° │ Moderate showers with isolated thunderstorms                  │ moderate      │ NE20     │
│ Sun │ Jan 22 │ 20° │ 30° │ Moderate showers with isolated thunderstorms                  │ moderate      │ N15      │
│ Mon │ Jan 23 │ 20° │ 30° │ Moderate to heavy thundery showers                            │ rough         │ N15      │
│ Tue │ Jan 24 │ 20° │ 30° │ Moderate to heavy thundery showers                            │ rough         │ N20      │
│ Wed │ Jan 25 │ 20° │ 30° │ Moderate to heavy thundery showers                            │ rough         │ N25      │
└─────┴────────┴─────┴─────┴───────────────────────────────────────────────────────────────┴───────────────┴──────────┘
>>> get_weekforecast(day=3)
{'condition': 'Few passing showers',
 'date': 'Apr 25',
 'day': 'Thu',
 'max': '31�',
 'min': '20�',
 'probability': 'Medium',
 'sea condition': 'moderate',
 'wind': 'SE20'}

>>> get_weekforecast(day=3)['condition']
'Few passing showers'

>>> get_cityforecast()
[
 {'condition': 'Partly cloudy',
     'date': 'Apr 22',
     'day': 'Mon',
     'max': '31�',
     'min': '26�',
     'wind': 'E25G50'},
 {'condition': ...}
]


>>> get_moonphase()
{'April 2019': {
                'first quarter': {'date': '12', 'hour': '23', 'minute': '06'},
                'full moon': {'date': '19', 'hour': '15', 'minute': '12'},
                'last quarter': {'date': '27', 'hour': '02', 'minute': '18'},
                'new moon': {'date': '05', 'hour': '12', 'minute': '50'}
                },
 'May 2019': {'first quarter': {'date': '12', 'hour': '05', 'minute': '12'},
...

>>> may = get_moonphase(month='May 2019')
>>> may['new moon']['date']
'05'

>>> get_sunrisemu()
{
 'february': {
                1: {'rise': '05:53', 'set': '18:53'},
                ...
                28: {'rise': '06:07', 'set': '18:37'}
            },
 'march': {
            1: {'rise': '06:07', 'set': '18:36'},
            2: {'rise': '06:07', 'set': '18:36'},
            ...
            31: {'rise': '06:16', 'set': '18:11'}
        }
}

>>> get_sunriserodr()

>>> get_sunrisemu().keys()
dict_keys(['february', 'march'])

>>> get_eclipses()
[
 {
    'end': {'date': 1, 'hour': 2, 'minute': 37, 'month': 'may'},
    'info': 'The eclipse will not be visible in Mauritius, Rodrigues, St. Brandon and Agalega.',
    'start': {'date': 30, 'hour': 22, 'minute': 45, 'month': 'april'},
    'status': 'partial',
    'type': 'sun',
    'title': ''
 },
 ...
 {
    'end': {'date': 8, 'hour': 17, 'minute': 56, 'month': 'november'},
    'info': 'The eclipse will not be visible in Mauritius, Rodrigues, St. Brandon and Agalega.',
    'start': {'date': 8, 'hour': 12, 'minute': 2, 'month': 'november'},
    'status': 'total',
    'type': 'moon',
    'title': ''
 }
]

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
]
>>> get_tides()
{
    'months': {
        'january': {
            1: ['09:27', '59', '23:37', '58', '03:27', '41', '16:55', '30'],
            ...
        },
        'february': {
            1: ['00:36', '63', '10:49', '58', '06:12', '49', '18:21', '28'],
            ...
        }
    },
    'month_format': {
        'date': [
            '1st High Tide (Time (Local))',
            '1st High Tide (Height (cm))',
            '2nd High Tide (Time (Local))',
            '2nd High Tide (Height (cm))',
            '1st Low Tide (Time (Local))',
            '1st Low Tide (Height (cm))',
            '2nd Low Tide (Time (Local))',
            '2nd Low Tide (Height (cm))'
        ]
    },
    'meta': {'months': [['january', '2023'], ['feruary', '2023']]}
}
>>> get_latest()
{
    'rainfall24h': {
        'info': 'Rainfall in (mm) from 28 January 2023 10 PM  to 29 January 2023 10 PM',
        'data': {
            'Albion': '',
            ...
            'Vacoas': '2.3'
        }
    },
    'rainfall3hrs': {
        'info': 'Last 3hrs Rainfall in (mm) on 29 January 2023 10 PM.',
        'data': {
            'Albion': '',
            ...
            'Vacoas': '0.5'
        }
    },
    'wind': {
        'info': 'Maximum wind speed (km/h) for the last 24 hours until 29 January 2023',
        'data': {
            'Albion': '',
            ...
            'Vacoas': '24'
        }
    },
    'humidity': {
        'info': 'Humidity at 10 AM on 29 January 2023',
        'data': {
            'Albion': '',
            ...
            'Vacoas': '72'
        }
    },
    'minmaxtemp': {
        'info': 'Maximum and minimum temperatures for the last 24 hours until 29 January 2023',
        'data': {
            'Albion': {'min': '', 'max': ''},
            ...
            'Vacoas': {'min': '22', 'max': '29'}
        }
    }
}
>>> get_uvindex()
{
    'vacoas': 'Extreme', 
    'port-louis': 'Extreme', 
    'plaisance': 'Low'
}
>>> get_today_moonphase() # {} if nothing today
{
    'title': 'first quarter', 
    'hour': 22, 
    'minute': 39
}
>>> get_today_eclipse() # {} if nothing today
{
    'start': eclispe_json,
    'end': eclipse_json
}
>>> get_today_sunrise("mu")
{
    'rise': '05:53', 
    'set': '18:53'
}
>>> get_today_forecast()
{
 'condition': 'Few passing showers',
 'date': 'Apr 25',
 'day': 'Thu',
 'max': '31�',
 'min': '20�',
 'probability': 'Medium',
 'sea condition': 'moderate',
 'wind': 'SE20'
}
>>> get_today_tides()
['09:27', '59', '23:37', '58', '03:27', '41', '16:55', '30']
```

# Cli

```
Usage: meteomoris [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  forecast     Week forecast
  message      Message of the day
  moonphase    Moonphase
  special      Special weather bulletin
  sunrisemu    Sunrise (Mauritius)
  sunriserodr  Sunrise (Rodrigues)
  today        Today's info
  uvindex      Ultra Violet Index

```

# Global settings

```python
from meteomoris import Meteo
from meteomoris import get_main_message

Meteo.CHECK_INTERNET = True # Will check if there is internet
Meteo.EXIT_ON_NO_INTERNET = True # Will exit if no internet
Meteo.ALREADY_CHECKED_INTERNET = False
Meteo.DEBUG = False # used during development
Meteo.CACHE_PERMS = True # used internally, modify to refelct if cache file can be created
Meteo.CACHE_PATH = "." # If cache path can be customized, default to  site-packages

Meteo.today = "2023-11-10" # If you want to override cache data
Meteo.headers = {
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
     } # Redefine default headers here
print(get_main_message())
```
# Installing

Create and activate env

Linux 

```
python3.9 -m venv venv
. venv/bin/activate
```

Windows

```
py -3.9 -m venv venv
venv\Scripts\activate.bat :: for command prompt
venv\Scripts\Activate.ps1 :: for powershell
```

# Local dev

In env

```
pip install -e . 
```

# Local test

In env

Install pytest `pip install pytest`

Run

`python -m pytest tests/`

# Changelog

```
2.11.0
🎉 get_today_sunrise
🎉 get_today_forecast
🎉 get_today_tides

2.10.0
🎉 get_today_moonphase
🎉 get_today_eclipse

2.9.0: 🎉 Add version cli command

2.8.8
🔧 Set cache path to current directory
🖌️ Rearrange display of today command
🔧 Remove latest data from cache as need last 3hrs

2.8.7
🔧 Lots of fixes
🔧 Tests
🎉 Customizable cache path

2.8.3: 🔧 Fix key error
2.8.2: 🔧 Fix imports
2.8.4: ✨ Feat resist cache permission issues
2.8.5: 🔧 Fix cache not found on perms error
2.8.6: 🔧 Fix none error on no cache data
2.8.1: 🔥 Feat cache
2.8.0: 🎉 Add UV index

2.7.8
🔧 Fixes
🛩️ Debian package published

2.7.0
🎉 Add latest data in API
🎉 Add today command

2.6.0
🎉 Add tide
🎉 Add rainfall 

2.4.0: 🎉 Add today info
2.3.3: 🔧 Fix broken install

2.3.0
🔧 Fix get_eclipse_raw bug
✨ Add debug mode

2.2.1: 🔧 Fix get_moonphase bug
2.2.0: 🎉 Add print commands and API

2.1.0
🔧 Fix get_moonphase
🎉 Add get_equinoxes
🎉 Add get_solstices
🎉 Add get_equinoxes

2.0.2: 🔧 Fix broken install

2.0.1
📑 Add venv docs
📑 Add global settings docs

2.0.0
🎉 Add Meteo with classmethod
🎉 Add internet check
🎉 Add global settings
🎉 Add headers change option
🎉 Add get_sunrisemu
🎉 Add get_sunriserodr
🔧 Tests basics
```

# Debian

Example

```
~/code/meteomoris/$ debuild -k"<key id>" -S
~/code/meteomoris/$ cd ..
~/code/$ dput ppa:abdur-rahmaanj/meteomoris-ppa meteomoris_2.7.8_source.changes
```
