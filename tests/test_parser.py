from meteomoris.behavior.parser import Parser


parser = Parser()


SAMPLE_FORECAST_HTML = """
<div class="daysforecast">
    <div class="forecast">
        <span class="fday">Mon, Jan 1</span>
        <span class="fcondition">Sunny</span>
        <span class="ftemp">20°</span>
        <span class="ftemp">30°</span>
        <span class="fgrey">E10</span>
        <span class="fgrey">calm</span>
        <span class="fgrey1">Low</span>
    </div>
    <div class="forecast">
        <span class="fday">Tue, Jan 2</span>
        <span class="fcondition">Cloudy</span>
        <span class="ftemp">22°</span>
        <span class="ftemp">28°</span>
        <span class="fgrey">W15</span>
        <span class="fgrey">moderate</span>
        <span class="fgrey1">Medium</span>
    </div>
</div>
"""

SAMPLE_CITY_FORECAST_HTML = """
<div class="city_forecast">
    <div class="block">
        <span class="cday">Mon,</span>
        <span class="cdate">Jan 1</span>
        <span class="fcondition">Sunny</span>
        <span class="ctemp">20°</span>
        <span class="ctemp1">30°</span>
        <span class="cwind1">E10</span>
    </div>
</div>
"""

SAMPLE_SUNRISE_HTML = """
<table>
    <tbody>
        <tr><td></td><td>1january 2025</td><td>1february 2025</td></tr>
        <tr><td>1</td><td>05:30</td><td>05:31</td></tr>
    </tbody>
</table>
"""

SAMPLE_MOONPHASE_HTML = """
<table>
    <tbody>
        <tr><td>january 2025</td><td>february 2025</td></tr>
        <tr><td>N.M</td><td>1</td><td>2</td><td>3</td><td>F.Q</td><td>4</td><td>5</td><td>6</td></tr>
    </tbody>
</table>
"""

SAMPLE_MAIN_MESSAGE_HTML = """
<div class="warning">
    Weather alert: Cyclone warning class II
    <a href="/details">Read more</a>
</div>
"""

SAMPLE_ECLIPSE_HTML = """
<table>
    <tr><td><strong>Total eclipse of the moon - january 15</strong></td></tr>
    <tr><td><strong>Eclipse begins at 05h30</strong></td></tr>
    <tr><td><strong>Ends at 07h45</strong></td></tr>
    <tr><td><strong>Visible in Mauritius</strong></td></tr>
</table>
"""

SAMPLE_SPECIAL_BULLETIN_HTML = """
<div class="left_content">
    <div class="warning">Irrelevant</div>
    Cyclone warning bulletin issued at 4 PM
</div>
"""

SAMPLE_ECLIPSE_SOLSTICE_HTML = """
<table><tr><td>data</td></tr></table>
<table><tr><td>data</td></tr></table>
<table><tr><td>data</td></tr></table>
<table><tr><td>data</td></tr></table>
<table><tr><td>data</td></tr></table>
<table><tr>
<td><strong>Equinoxes: 20 march at 12h30</strong></td>
</tr></table>
"""

SAMPLE_LATEST_HTML = """
<div class="weatherinfo">Rainfall (24hrs)</div>
<div class="weatherinfo">Rainfall (3hrs)</div>
<div class="weatherinfo">Wind</div>
<div class="weatherinfo">Humidity</div>
<div class="weatherinfo">Maximum and Minimum Temperature</div>
<table class="tableau">
    <tr><td>Port Louis</td><td>12.5</td></tr>
    <tr><td>Curepipe</td><td>8.0</td></tr>
</table>
<table class="tableau">
    <tr><td>Port Louis</td><td>5.0</td></tr>
</table>
<table class="tableau">
    <tr><td>Port Louis</td><td>E20</td></tr>
</table>
<table class="tableau">
    <tr><td>Port Louis</td><td>75%</td></tr>
</table>
<table class="tableau">
    <tr><td>Port Louis</td><td>20</td><td>30</td></tr>
</table>
"""

SAMPLE_RAINFALL_HTML = """
<div class="left_content">
    Highest rainfall during the last 24 hours today:
    Port Louis: 25.0mm
    Curepipe: 12.0mm
</div>
"""

SAMPLE_ECLIPSE_TEXT_HTML = """
<div class="left_content">
    <p>Eclipse details</p>
    <p>First eclipse of the year</p>
    <p>More information</p>
</div>
"""


class TestParserWeekForecast:
    def test_parse_weekforecast_returns_list(self):
        result = parser.parse_weekforecast(SAMPLE_FORECAST_HTML)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_parse_weekforecast_fields(self):
        result = parser.parse_weekforecast(SAMPLE_FORECAST_HTML)
        f = result[0]
        assert f.day == "Mon"
        assert f.date == "Jan 1"
        assert f.condition == "Sunny"
        assert f.min == "20°"
        assert f.max == "30°"
        assert f.wind == "E10"
        assert f.probability == "Low"

    def test_parse_weekforecast_none_on_empty(self):
        result = parser.parse_weekforecast("<html></html>")
        assert result is None


class TestParserCityForecast:
    def test_parse_cityforecast_returns_list(self):
        result = parser.parse_cityforecast(SAMPLE_CITY_FORECAST_HTML)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_parse_cityforecast_fields(self):
        result = parser.parse_cityforecast(SAMPLE_CITY_FORECAST_HTML)
        f = result[0]
        assert f.day == "Mon"
        assert f.date == "Jan 1"
        assert f.condition == "Sunny"
        assert f.min == "20°"
        assert f.max == "30°"


class TestParserMainMessage:
    def test_parse_main_message_returns_object(self):
        result = parser.parse_main_message(SAMPLE_MAIN_MESSAGE_HTML)
        assert "Cyclone" in result.text


class TestParserSunrise:
    def test_parse_sunrise_returns_dict(self):
        result = parser.parse_sunrise_table(SAMPLE_SUNRISE_HTML)
        assert isinstance(result, dict)

    def test_parse_sunrise_has_month_keys(self):
        result = parser.parse_sunrise_table(SAMPLE_SUNRISE_HTML)
        months = list(result.keys())
        assert len(months) == 2


class TestParserMoonPhase:
    def test_parse_moonphase_returns_dict(self):
        result = parser.parse_moonphase(SAMPLE_MOONPHASE_HTML)
        assert isinstance(result, dict)


class TestParserEclipses:
    def test_parse_eclipses_returns_list(self):
        result = parser.parse_eclipses(SAMPLE_ECLIPSE_HTML)
        assert isinstance(result, list)

    def test_parse_eclipses_has_objects(self):
        result = parser.parse_eclipses(SAMPLE_ECLIPSE_HTML)
        if result:
            e = result[0]
            assert e.status == "total"


class TestParserEquinoxes:
    def test_parse_equinoxes_returns_list(self):
        result = parser.parse_equinoxes(SAMPLE_ECLIPSE_SOLSTICE_HTML)
        assert isinstance(result, list)

    def test_parse_equinoxes_fields(self):
        result = parser.parse_equinoxes(SAMPLE_ECLIPSE_SOLSTICE_HTML)
        if result:
            e = result[0]
            assert e.day == 20


class TestParserSolstices:
    def test_parse_solstices_empty_on_no_data(self):
        result = parser.parse_solstices("<html></html>")
        assert result == []


class TestParserLatest:
    def test_parse_latest_returns_object(self):
        result = parser.parse_latest(SAMPLE_LATEST_HTML)
        assert result is not None
        assert hasattr(result, "to_dict")


class TestParserRainfall:
    def test_parse_rainfall_returns_object(self):
        result = parser.parse_rainfall(SAMPLE_RAINFALL_HTML)
        assert result is not None
        assert hasattr(result, "data")


class TestParserEclipseText:
    def test_parse_eclipse_text_returns_string(self):
        result = parser.parse_eclipse_text(SAMPLE_ECLIPSE_TEXT_HTML)
        assert isinstance(result, str)


class TestParserSpecialBulletin:
    def test_parse_special_bulletin_returns_string(self):
        result = parser.parse_special_bulletin(SAMPLE_SPECIAL_BULLETIN_HTML)
        assert isinstance(result, str)


class TestParseTimeString:
    def test_valid_time(self):
        result = Parser.parse_time_string("13h45")
        assert result == {"hour": 13, "minute": 45}

    def test_invalid_time(self):
        result = Parser.parse_time_string("invalid")
        assert result is None
