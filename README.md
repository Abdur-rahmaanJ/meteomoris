# meteomoris

get info about the weather in mauritius!

```
pip install meteomoris
```

# examples

```python
>>> from meteomoris import meteo

>>> meteo.get_weekforecast()
{0: {'condition': 'Few showers highgrounds',
     'date': 'Apr 22',
     'day': 'Mon',
     'max': '32�',
     'min': '21�',
     'probability': 'High',
     'sea condition': 'rough',
     'wind': 'E25G50'},
 1: {
...
}

>>> meteo.get_weekforecast(day=3)
{'condition': 'Few passing showers',
 'date': 'Apr 25',
 'day': 'Thu',
 'max': '31�',
 'min': '20�',
 'probability': 'Medium',
 'sea condition': 'moderate',
 'wind': 'SE20'}

>>> meteo.get_weekforecast(day=3)['condition']
'Few passing showers'

>>> meteo.get_cityforecast()
{0: {'condition': 'Partly cloudy',
     'date': 'Apr 22',
     'day': 'Mon',
     'max': '31�',
     'min': '26�',
     'wind': 'E25G50'},
 1: {'condition': ...
}

>>> meteo.get_moonphase()
{'April 2019': {'first quarter': {'date': '12', 'hour': '23', 'minute': '06'},
                'full moon': {'date': '19', 'hour': '15', 'minute': '12'},
                'last quarter': {'date': '27', 'hour': '02', 'minute': '18'},
                'new moon': {'date': '05', 'hour': '12', 'minute': '50'}},
 'May 2019': {'first quarter': {'date': '12', 'hour': '05', 'minute': '12'},
...

>>> may = meteo.get_moonphase(month='May 2019')
>>> may['new moon']['date']
'05'
```

# Local test

```
git clone https://github.com/Abdur-rahmaanJ/meteomoris.git
```

```
python -m pip install <path-to-package>/meteomoris
```

