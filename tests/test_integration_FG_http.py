import time

import pytest

from flightgear_python.fg_if import HTTPConnection


pytestmark = pytest.mark.fg_integration


def test_http_list_props():
    h_con = HTTPConnection('localhost', 8080)

    sun_prop_dict_immediate = h_con.list_props('/ephemeris/sun', recurse_limit=0)
    assert len(sun_prop_dict_immediate['directories']) != 0
    assert len(sun_prop_dict_immediate['properties']) != 0

    sun_prop_dict_all = h_con.list_props('/ephemeris/sun', recurse_limit=None)
    assert len(sun_prop_dict_all['directories']) == 0
    assert len(sun_prop_dict_all['properties']) != 0


def test_http_get_prop():
    h_con = HTTPConnection('localhost', 8080)

    sim_time_1 = h_con.get_prop('/sim/time/steady-clock-sec')
    time.sleep(1)
    sim_time_2 = h_con.get_prop('/sim/time/steady-clock-sec')
    assert sim_time_2 > sim_time_1


def test_http_set_prop():
    h_con = HTTPConnection('localhost', 8080)

    h_con.set_prop('/controls/flight/aileron', 0.5)
    aileron_value = h_con.get_prop('/controls/flight/aileron')
    assert aileron_value == 0.5

    h_con.set_prop('/controls/flight/aileron', -0.5)
    aileron_value = h_con.get_prop('/controls/flight/aileron')
    assert aileron_value == -0.5
