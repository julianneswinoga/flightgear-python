import requests_mock
import pytest

from flightgear_python.fg_if import HTTPConnection

# Excerpt from https://wiki.flightgear.org/Json_Properties#Example
preset_values = [
    {
        'path': '/sim/time/cur-time-override',
        'name': 'cur-time-override',
        'value': '0',
        'type': 'long',
        'index': 0,
        'nChildren': 0,
    },
    {
        'path': '/sim/time/local-offset',
        'name': 'local-offset',
        'value': '3600',
        'type': 'int',
        'index': 0,
        'nChildren': 0,
    },
    {
        'path': '/sim/time/gmt',
        'name': 'gmt',
        'value': '2014-03-27T13:25:10',
        'type': 'string',
        'index': 0,
        'nChildren': 0,
    },
    {
        'path': '/sim/time/sun-angle-rad',
        'name': 'sun-angle-rad',
        'value': '0.9883239645',
        'type': 'double',
        'index': 0,
        'nChildren': 0,
    },
]


@pytest.mark.parametrize('preset_value', preset_values)
def test_http_get_prop(preset_value):
    h_con = HTTPConnection('localhost', 55555)
    with requests_mock.Mocker() as m:
        prop_path = preset_value['path']
        # Set the mock value
        m.get(h_con.url + prop_path, json=preset_value)
        # Check the code result
        resp = h_con.get_prop(prop_path)
        # Instead of comparing the converted value, just convert the converted value to a string and compare that
        assert str(resp) == preset_value['value']


@pytest.mark.parametrize('preset_value', preset_values)
def test_http_set_prop(preset_value):
    h_con = HTTPConnection('localhost', 55555)
    with requests_mock.Mocker() as m:
        prop_path = preset_value['path']
        # Set the mock value
        m.get(h_con.url + prop_path, json=preset_value)
        m.post(h_con.url + prop_path)
        # Check the code doesn't break (nothing to assert)
        h_con.set_prop(prop_path, 'test value')
