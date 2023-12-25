from meteomoris import *
from pilmoji import Pilmoji
from PIL import Image  
from PIL import ImageDraw
from PIL import ImageFont
width = 800
height = 1000

img  = Image.new( mode = "RGB", size = (width, height), color = (255, 255, 255) )
font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 30, encoding="unic")

padding = 30
line_between = 25
y = 30
buffer = []
special = get_special_weather_bulletin()
main_msg = get_main_message()

with Pilmoji(img) as pilmoji:
    today_forecast = get_today_forecast()
    pilmoji.text((padding, y), f'{today_forecast["day"]} {today_forecast["date"]}', (0,0,0), font=font)
    y += (line_between * 2)
    for k,v in today_forecast.items():
        if k.casefold() not in ["date", "day"]:
            if k in ["condition"]:
                pilmoji.text((padding, y), f'{v}', (0,0,0), font=font)
            else:
                pilmoji.text((padding, y), f'{k}:{v}', (0,0,0), font=font)
            y += line_between

    for k,v in get_today_sunrise("mu").items():
        pilmoji.text((padding, y), f'{k}:{v}', (0,0,0), font=font)
        y += line_between

    y += line_between


    item = get_today_tides()
    print(item)
    pilmoji.text((padding, y), f'Tides', (0,0,0),
            font=font)
    y += line_between
    pilmoji.text((padding, y), f'{item[0]} {item[1]}mm', (0,0,0),
            font=font)
    y += line_between
    pilmoji.text((padding, y), f'{item[2]} {item[3]}mm ', (0,0,0),
            font=font)
    y += line_between
    pilmoji.text((padding, y), f'{item[4]} {item[5]}mm', (0,0,0),
            font=font)
    y += line_between
    pilmoji.text((padding, y), f'{item[6]} {item[7]}mm', (0,0,0),
            font=font)
    y += line_between


    y+= line_between

    #pilmoji.text((padding, y), main_msg, (0, 0, 0), font)
    #y += line_between 

    # font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 20, encoding="unic")
    
    for c in main_msg:
        if len(buffer) >= 20:
            buffer_str = "".join(buffer)
            print(buffer_str)
            pilmoji.text((padding, y), buffer_str, (0, 0, 0), font)
            buffer = []
            y += line_between
            buffer.append(c)
        else:
            buffer.append(c)
            print(buffer)
    buffer_str = "".join(buffer)
    pilmoji.text((padding, y), buffer_str, (0, 0, 0), font)
img.show()


