import math

import pytest

from flightgear_python.fg_if import HTTPConnection, PropsConnection


pytestmark = pytest.mark.fg_integration


def test_comparison_list_props():
    h_con = HTTPConnection('localhost', 8080)
    t_con = PropsConnection('localhost', 5500)
    t_con.connect()

    http_sun_prop_dict_immediate = h_con.list_props('/ephemeris/sun', recurse_limit=0)
    telnet_sun_prop_dict_immediate = t_con.list_props('/ephemeris/sun', recurse_limit=0)
    assert http_sun_prop_dict_immediate['directories'] == telnet_sun_prop_dict_immediate['directories']
    assert http_sun_prop_dict_immediate['properties'].keys() == telnet_sun_prop_dict_immediate['properties'].keys()

    http_sun_prop_dict_all = h_con.list_props('/ephemeris/sun', recurse_limit=None)
    telnet_sun_prop_dict_all = t_con.list_props('/ephemeris/sun', recurse_limit=None)
    assert http_sun_prop_dict_all['directories'] == telnet_sun_prop_dict_all['directories']
    assert http_sun_prop_dict_all['properties'].keys() == telnet_sun_prop_dict_all['properties'].keys()


def test_comparison_get_prop():
    h_con = HTTPConnection('localhost', 8080)
    t_con = PropsConnection('localhost', 5500)
    t_con.connect()

    http_sim_time = h_con.get_prop('/sim/time/steady-clock-sec')
    telnet_sim_time = t_con.get_prop('/sim/time/steady-clock-sec')
    assert math.isclose(http_sim_time, telnet_sim_time, abs_tol=1e-1)


def test_comparison_set_prop():
    h_con = HTTPConnection('localhost', 8080)
    t_con = PropsConnection('localhost', 5500)
    t_con.connect()

    h_con.set_prop('/controls/flight/aileron', 0.5)
    aileron_value = t_con.get_prop('/controls/flight/aileron')
    assert aileron_value == 0.5

    t_con.set_prop('/controls/flight/aileron', -0.5)
    aileron_value = h_con.get_prop('/controls/flight/aileron')
    assert aileron_value == -0.5
