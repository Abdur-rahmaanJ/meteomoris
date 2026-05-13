import re
import datetime
import calendar

from bs4 import BeautifulSoup

from ..model.entities import (
    Forecast, CityForecast, SunInfo, MoonInfo, MoonPhaseEntry,
    Eclipse, Equinox, Solstice, TideData, UVIndexData,
    LatestData, Rainfall, MainMessage
)


class Parser:
    @staticmethod
    def parse_time_string(time_str):
        match = re.match(r"(\d{1,2})h(\d{2})", time_str)
        if match:
            return {"hour": int(match.group(1)), "minute": int(match.group(2))}
        return None

    def parse_weekforecast(self, html):
        soup = BeautifulSoup(html, "html.parser")
        w_forecast = soup.find(attrs={"class": "daysforecast"})
        if w_forecast is None:
            return None
        week_forcecast = w_forecast.find_all(attrs={"class": "forecast"})
        week = []
        for _day in week_forcecast:
            fulldate = _day.find(attrs={"class": "fday"})
            if fulldate is None:
                continue
            fdate = fulldate.text.split(",")
            date_day = fdate[0]
            date_date = fdate[1].strip() if len(fdate) > 1 else ""
            condition = _day.find(attrs={"class": "fcondition"})
            temp = _day.find_all(attrs={"class": "ftemp"})
            if len(temp) < 2:
                continue
            fgrey = _day.find_all(attrs={"class": "fgrey"})
            prob = _day.find_all(attrs={"class": "fgrey1"})
            week.append(Forecast(
                day=date_day,
                date=date_date,
                condition=condition.text if condition else "",
                min_temp=temp[0].text,
                max_temp=temp[1].text,
                wind=fgrey[0].text if len(fgrey) > 0 else "",
                sea_condition=fgrey[1].text if len(fgrey) > 1 else "",
                probability=prob[0].text if len(prob) > 0 else "",
            ))
        return week

    def parse_cityforecast(self, html):
        soup = BeautifulSoup(html, "html.parser")
        w_forecast = soup.find(attrs={"class": "city_forecast"})
        if w_forecast is None:
            return None
        week_forcecast = w_forecast.find_all(attrs={"class": "block"})
        week = []
        for _day in week_forcecast:
            date_day = _day.find(attrs={"class": "cday"})
            date_date = _day.find(attrs={"class": "cdate"})
            condition = _day.find(attrs={"class": "fcondition"})
            min_temp = _day.find(attrs={"class": "ctemp"})
            max_temp = _day.find(attrs={"class": "ctemp1"})
            wind = _day.find(attrs={"class": "cwind1"})
            week.append(CityForecast(
                day=date_day.text[:-1] if date_day else "",
                date=date_date.text if date_date else "",
                condition=condition.text if condition else "",
                min_temp=min_temp.text if min_temp else "",
                max_temp=max_temp.text if max_temp else "",
                wind=wind.text if wind else "",
            ))
        return week

    def parse_sunrise_table(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table is None:
            return None
        table_body = table.find("tbody")
        if table_body is None:
            return None
        rows = table_body.find_all("tr")
        data = {}
        for i, row in enumerate(rows):
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            if i == 0:
                if len(cols) < 3:
                    continue
                month1 = re.sub("\\d+", "", cols[1].lower()).strip()
                month2 = re.sub("\\d+", "", cols[2].lower()).strip()
                data = {month1: {}, month2: {}}
            elif i > 1 and len(cols) >= 5:
                try:
                    date = int(cols[0])
                except (ValueError, IndexError):
                    continue
                m1_rise = cols[1]
                m1_set = cols[2]
                m2_rise = cols[3]
                m2_set = cols[4]
                if m1_rise and m1_set:
                    data[month1][str(date)] = SunInfo(rise=m1_rise, set=m1_set)
                if m2_rise and m2_set:
                    data[month2][str(date)] = SunInfo(rise=m2_rise, set=m2_set)
        return data

    def parse_moonrise_table(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table is None:
            return None
        table_body = table.find("tbody")
        if table_body is None:
            return None
        rows = table_body.find_all("tr")
        data = {}
        for i, row in enumerate(rows):
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            if i == 0:
                if len(cols) < 3:
                    continue
                month1 = re.sub("\\d+", "", cols[1].lower()).strip()
                month2 = re.sub("\\d+", "", cols[2].lower()).strip()
                data = {month1: {}, month2: {}}
            elif i > 2 and len(cols) >= 7:
                try:
                    date = int(cols[0])
                except (ValueError, IndexError):
                    continue
                m1_rise = cols[2] if len(cols) > 2 else ""
                m1_set = cols[3] if len(cols) > 3 else ""
                m2_rise = cols[5] if len(cols) > 5 else ""
                m2_set = cols[6] if len(cols) > 6 else ""
                if m1_rise and m1_set and m1_rise != "-":
                    data[month1][str(date)] = MoonInfo(rise=m1_rise, set=m1_set)
                if m2_rise and m2_set and m2_rise != "-":
                    data[month2][str(date)] = MoonInfo(rise=m2_rise, set=m2_set)
        return data

    def parse_moonphase(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table is None:
            return None
        table_body = table.find("tbody")
        if table_body is None:
            return None
        rows = table_body.find_all("tr")
        data = {}
        for i, row in enumerate(rows):
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            if i == 0 and len(cols) >= 2:
                month1 = " ".join(cols[0].lower().split())
                month2 = " ".join(cols[1].lower().split())
                data = {month1.casefold(): {}, month2.casefold(): {}}
            elif 1 < i < 6 and len(cols) >= 8:
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
                phase1 = code_lookup.get(m1_phase)
                phase2 = code_lookup.get(m2_phase)
                if phase1:
                    data[month1][phase1] = MoonPhaseEntry(m1_date, m1_hour, m1_min)
                if phase2:
                    data[month2][phase2] = MoonPhaseEntry(m2_date, m2_hour, m2_min)
        return data

    def parse_eclipses(self, html):
        soup = BeautifulSoup(html, "html.parser")
        eclipses = []
        for table in soup.find_all("table"):
            strong_tags = table.find_all("strong")
            if not strong_tags:
                continue
            title_tag = strong_tags[0].get_text(strip=True).lower()
            if "eclipse of the" not in title_tag:
                continue
            match = re.search(
                r"(total|partial) eclipse of the (moon|sun) - (\w+) (\d{1,2})",
                title_tag,
            )
            if not match:
                continue
            status, ecl_type, month, date = match.groups()
            date = int(date)
            ecl_type = ecl_type.lower()
            start, end, info = None, None, ""
            for tag in strong_tags:
                text = tag.get_text(strip=True).lower()
                if "eclipse begins at" in text:
                    start_match = re.search(
                        r"eclipse begins at (\d{1,2}h\d{2})", text
                    )
                    if start_match:
                        start = self.parse_time_string(start_match.group(1))
                        if start:
                            start["month"], start["date"] = month, date
                if "ends at" in text:
                    end_match = re.search(r"ends at (\d{1,2}h\d{2})", text)
                    if end_match:
                        end = self.parse_time_string(end_match.group(1))
                        if end:
                            end["month"], end["date"] = month, date + (
                                1 if "on" in text else 0
                            )
                if "visible" in text or "not visible" in text:
                    info = tag.get_text(strip=True)
            eclipses.append(Eclipse(
                status=status,
                type=ecl_type,
                start=start,
                end=end,
                info=info,
                title=title_tag,
            ))
        return eclipses

    def parse_eclipse_text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        page_container = soup.find("div", {"class": "left_content"})
        if page_container is None:
            return None
        page_container = page_container.findAll("p")[1:-1]
        eclipse_text = ""
        for line in page_container:
            eclipse_text += line.text + "\n"
        return eclipse_text

    def parse_equinoxes(self, html):
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")
        if len(tables) < 6:
            return None
        soup_table = tables[5]
        equinoxes = []
        for strong_tag in soup_table.find_all("tr"):
            text = strong_tag.get_text(strip=True).lower()
            if "equinoxes:" in text.lower():
                matches = re.findall(
                    r"(\d{1,2}) (\w+) at (\d{1,2}h\d{2})", text
                )
                for day, month, time_str in matches:
                    time_data = self.parse_time_string(time_str)
                    if time_data:
                        equinoxes.append(Equinox(
                            day=int(day),
                            month=month,
                            year=datetime.datetime.now().year,
                            **time_data,
                        ))
        return equinoxes

    def parse_solstices(self, html):
        soup = BeautifulSoup(html, "html.parser")
        solstices = []
        for strong_tag in soup.find_all("strong"):
            text = strong_tag.get_text(strip=True).lower()
            if "solstice" in text:
                matches = re.findall(
                    r"(\d{1,2}) (\w+) at (\d{1,2}h\d{2})", text
                )
                for day, month, time_str in matches:
                    time_data = self.parse_time_string(time_str)
                    if time_data:
                        solstices.append(Solstice(
                            day=int(day),
                            month=month,
                            year=datetime.datetime.now().year,
                            **time_data,
                        ))
        return solstices

    def parse_tides(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.text.strip().split("\n")
        text = [t for t in text if t.strip()]
        months = [calendar.month_name[i].casefold() for i in range(1, 13)]
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
        try:
            i = 0
            while i < len(text):
                line = text[i]
                try:
                    words = line.split(" ")
                    if words[0].casefold() in months:
                        words[0] = words[0].casefold()
                        words[1] = int(words[1])
                        tide_info["meta"]["months"].append([words[0], words[1]])
                        tide_info["months"][words[0]] = {}
                except (IndexError, ValueError):
                    pass
                if tide_info["meta"]["months"]:
                    if re.findall("^\\d{1,2}$", line):
                        target_month_index = (
                            len(tide_info["meta"]["months"]) - 1
                        )
                        target_month = tide_info["meta"]["months"][
                            target_month_index
                        ][0]
                        tide_info["months"][target_month][int(line)] = []
                        for j in range(1, 9):
                            if i + j < len(text):
                                tide_info["months"][target_month][
                                    int(line)
                                ].append(text[i + j])
                        i += 9
                        continue
                i += 1
        except Exception:
            pass
        return TideData(
            months=tide_info["months"],
            month_format=tide_info["month_format"],
            meta=tide_info["meta"],
        )

    def parse_rainfall(self, html):
        soup = BeautifulSoup(html, "html.parser")
        content = soup.find("div", attrs={"class": "left_content"})
        if content is None:
            return None
        content = [c for c in content.text.strip().split("\n") if c.strip()]
        info = None
        data = {}
        for line in content:
            if "highest rainfall" in line.casefold():
                try:
                    info = line.split("during the")[1].strip()[: -len(" today:")]
                except (IndexError, ValueError):
                    info = line
            if ("mm" in line) and (":" in line):
                try:
                    region = line.strip().split(":")[0].strip()
                    rain = line.strip().split(":")[1].strip()
                    data[region] = rain
                except (IndexError, ValueError):
                    pass
        return Rainfall(info=info, data=data)

    def parse_latest(self, html):
        soup = BeautifulSoup(html, "html.parser")
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
                            if key == "minmaxtemp" and itd + 2 < len(tds):
                                infos[key]["data"][td.text.strip()] = {
                                    "min": tds[itd + 1].text.strip(),
                                    "max": tds[itd + 2].text.strip(),
                                }
                            elif itd + 1 < len(tds):
                                infos[key]["data"][td.text.strip()] = tds[
                                    itd + 1
                                ].text.strip()
                        except Exception:
                            pass
        return LatestData(**infos)

    def parse_uvindex(self, html_by_region):
        data = {}
        for region, html in html_by_region.items():
            soup = BeautifulSoup(html, "html.parser")
            try:
                soup = soup.find_all(class_="diauv")[0]
                uv_description = soup.select_one(".tvtd").text.strip()
                data[region] = uv_description
            except (IndexError, AttributeError):
                data[region] = "---"
        return UVIndexData(data)

    def parse_main_message(self, html):
        soup = BeautifulSoup(html, "html.parser")
        message = soup.find("div", attrs={"class": "warning"})
        if message is None:
            return MainMessage(text="", links=[])
        text = message.text.strip()
        links = [
            (link.text.strip(), link.get("href"))
            for link in message.find_all("a")
        ]
        return MainMessage(text=text, links=links)

    def parse_special_bulletin(self, html):
        soup = BeautifulSoup(html, "html.parser")
        message = soup.find("div", attrs={"class": "left_content"})
        if message is None:
            return ""
        unwanted = message.find("div", attrs={"class": "warning"})
        if unwanted:
            unwanted.extract()
        return message.text.strip()
