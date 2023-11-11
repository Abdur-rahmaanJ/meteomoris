import meteomoris


# integration tests todo
# this one just a dirty scheme for me
def test_weekforecast():
    assert isinstance(meteomoris.get_weekforecast(), list)


def test_moonphase():
    assert isinstance(meteomoris.get_moonphase(), dict)


def test_cityforecast():
    assert isinstance(meteomoris.get_cityforecast(), list)
    assert isinstance(meteomoris.get_cityforecast(day=1), dict)


def test_main_message():
    assert isinstance(meteomoris.get_main_message(), str)


def test_sunrisemu():
    assert isinstance(meteomoris.get_sunrisemu(), dict)


def test_sunriserodr():
    assert isinstance(meteomoris.get_sunriserodr(), dict)


def test_eclipses():
    assert isinstance(meteomoris.get_eclipses(), list)


def test_equinoxes():
    assert isinstance(meteomoris.get_equinoxes(), list)


def test_solstices():
    assert isinstance(meteomoris.get_solstices(), list)


def test_tides():
    assert isinstance(meteomoris.get_tides(), dict)


def test_latest():
    assert isinstance(meteomoris.get_latest(), dict)


def test_uvindex():
    assert isinstance(meteomoris.get_uvindex(), dict)
