# meteomoris

get info about the weather in mauritius!

# examples

```python
>>> from meteomoris import meteo

>>> print(meteo.get_weekforecast())
{0: {'condition': 'Few showers highgrounds',
     'date': 'Apr 22',
     'day': 'Mon',
     'max': '32�',
     'min': '21�',
     'probability': 'High',
     'sea condition': 'rough',
     'wind': 'E25G50'},
 1: {...
}

>>> print(meteo.get_weekforecast(day=3))
{'condition': 'Few passing showers',
 'date': 'Apr 25',
 'day': 'Thu',
 'max': '31�',
 'min': '20�',
 'probability': 'Medium',
 'sea condition': 'moderate',
 'wind': 'SE20'}

>>> print(meteo.get_weekforecast(day=3)['condition'])
'Few passing showers'

>>> print(get_cityforecast())
{0: {'condition': 'Partly cloudy',
     'date': 'Apr 22',
     'day': 'Mon',
     'max': '31�',
     'min': '26�',
     'wind': 'E25G50'},
 1: {'condition': ...
}
```
