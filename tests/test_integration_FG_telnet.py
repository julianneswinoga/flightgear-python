import time

import pytest

from flightgear_python.fg_if import TelnetConnection
from flightgear_python.fg_util import FGConnectionError, FGCommunicationError


pytestmark = pytest.mark.fg_integration


def test_telnet_list_props():
    t_con = TelnetConnection('localhost', 5500)
    t_con.connect()

    sun_prop_dict_immediate = t_con.list_props('/ephemeris/sun', recurse_limit=0)
    assert len(sun_prop_dict_immediate['directories']) != 0
    assert len(sun_prop_dict_immediate['properties']) != 0

    sun_prop_dict_all = t_con.list_props('/ephemeris/sun', recurse_limit=None)
    assert len(sun_prop_dict_all['directories']) == 0
    assert len(sun_prop_dict_all['properties']) != 0


def test_telnet_get_prop():
    t_con = TelnetConnection('localhost', 5500)
    t_con.connect()

    sim_time_1 = t_con.get_prop('/sim/time/steady-clock-sec')
    time.sleep(1)
    sim_time_2 = t_con.get_prop('/sim/time/steady-clock-sec')
    assert sim_time_2 > sim_time_1


def test_telnet_set_prop():
    t_con = TelnetConnection('localhost', 5500)
    t_con.connect()

    t_con.set_prop('/controls/flight/rudder', 0.5)
    aileron_value = t_con.get_prop('/controls/flight/rudder')
    assert aileron_value == 0.5

    t_con.set_prop('/controls/flight/rudder', -0.5)
    aileron_value = t_con.get_prop('/controls/flight/rudder')
    assert aileron_value == -0.5


def test_telnet_wrong_port():
    t_con = TelnetConnection('localhost', 123)
    with pytest.raises(FGConnectionError):
        t_con.connect()


def test_telnet_no_connect():
    t_con = TelnetConnection('localhost', 5500)
    with pytest.raises(FGCommunicationError):
        t_con.get_prop('/controls/flight/rudder')


def test_telnet_bad_path_cmd():
    t_con = TelnetConnection('localhost', 5500)
    t_con.connect()
    with pytest.raises(FGCommunicationError):
        t_con.list_props('/aaa/bbb/ccc')


def test_telnet_bad_internal_cmd():
    t_con = TelnetConnection('localhost', 5500)
    t_con.connect()
    with pytest.raises(FGCommunicationError):
        t_con._send_cmd_get_resp('what a bad command')
