import math

import pytest

from flightgear_python.fg_if import HTTPConnection, PropsConnection


pytestmark = pytest.mark.fg_integration


@pytest.mark.parametrize('recurse_limit', [0, 1, None])
def test_comparison_list_props(recurse_limit):
    h_con = HTTPConnection('localhost', 8080)
    t_con = PropsConnection('localhost', 5500)
    t_con.connect()

    http_sun_prop_dict_immediate = h_con.list_props('/ephemeris/sun', recurse_limit=recurse_limit)
    telnet_sun_prop_dict_immediate = t_con.list_props('/ephemeris/sun', recurse_limit=recurse_limit)

    assert http_sun_prop_dict_immediate['directories'] == telnet_sun_prop_dict_immediate['directories']
    assert http_sun_prop_dict_immediate['properties'].keys() == telnet_sun_prop_dict_immediate['properties'].keys()
    # After we've verified the keys are identical we can check the values
    for prop_full_path in http_sun_prop_dict_immediate['properties'].keys():
        http_value = http_sun_prop_dict_immediate['properties'][prop_full_path]
        telnet_value = telnet_sun_prop_dict_immediate['properties'][prop_full_path]
        # We can't compare actual values (could be minute changes) but we can compare types
        assert type(http_value) == type(telnet_value), f'value path is {prop_full_path}'


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
