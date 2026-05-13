from meteomoris.behavior.renderer import Renderer


renderer = Renderer()


class TestRendererWeekForecast:
    def test_render_weekforecast_all_days(self):
        data = [
            {"day": "Mon", "date": "Jan 1", "min": "20", "max": "30",
             "condition": "Sunny", "sea condition": "calm", "wind": "E10",
             "probability": "Low"},
            {"day": "Tue", "date": "Jan 2", "min": "22", "max": "28",
             "condition": "Cloudy", "sea condition": "moderate", "wind": "W15",
             "probability": "Medium"},
        ]
        renderer.render_weekforecast(data)

    def test_render_weekforecast_single_day(self):
        data = [
            {"day": "Mon", "date": "Jan 1", "min": "20", "max": "30",
             "condition": "Sunny", "sea condition": "calm", "wind": "E10",
             "probability": "Low"},
        ]
        renderer.render_weekforecast(data, day=0)


class TestRendererCityForecast:
    def test_render_cityforecast_all(self):
        data = [
            {"day": "Mon", "date": "Jan 1", "min": "20", "max": "30",
             "condition": "Sunny", "wind": "E10"},
        ]
        renderer.render_cityforecast(data)

    def test_render_cityforecast_single(self):
        data = [
            {"day": "Mon", "date": "Jan 1", "min": "20", "max": "30",
             "condition": "Sunny", "wind": "E10"},
        ]
        renderer.render_cityforecast(data, day=0)


class TestRendererSunrise:
    def test_render_sunrise(self):
        data = {
            "january": {"1": {"rise": "05:30", "set": "18:45"}},
            "february": {"1": {"rise": "05:45", "set": "18:30"}},
        }
        renderer.render_sunrise(data)


class TestRendererMoonrise:
    def test_render_moonrise(self):
        data = {
            "january": {"1": {"rise": "18:30", "set": "06:00"}},
        }
        renderer.render_moonrise(data)


class TestRendererMoonPhase:
    def test_render_moonphase_all(self):
        data = {
            "january": {
                "new moon": {"date": 15, "hour": 3, "minute": 30},
            },
        }
        renderer.render_moonphase(data)

    def test_render_moonphase_single(self):
        data = {
            "january": {
                "new moon": {"date": 15, "hour": 3, "minute": 30},
            },
        }
        renderer.render_moonphase(data, month="january")


class TestRendererUVIndex:
    def test_render_uvindex(self):
        data = {"port-louis": "High", "vacoas": "Low"}
        renderer.render_uvindex(data)

    def test_render_uvindex_extreme(self):
        data = {"port-louis": "Extreme"}
        renderer.render_uvindex(data)


class TestRendererMainMessage:
    def test_render_main_message_no_links(self):
        data = {"text": "Cyclone warning", "links": []}
        renderer.render_main_message(data, links=False)


class TestRendererSpecialBulletin:
    def test_render_special_bulletin(self):
        renderer.render_special_bulletin("Bulletin text")


class TestRendererLatest:
    def test_render_latest(self):
        data = {
            "rainfall24h": {"info": "Last 24h", "data": {"PL": "10mm"}},
            "rainfall3hrs": {"info": "Last 3h", "data": {"PL": "2mm"}},
            "wind": {"info": "Wind", "data": {"PL": "E20"}},
            "humidity": {"info": "Humidity", "data": {"PL": "75%"}},
            "minmaxtemp": {"info": "Temp", "data": {"PL": {"min": "20", "max": "30"}}},
        }
        renderer.render_latest(data)
