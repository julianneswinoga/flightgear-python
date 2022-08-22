from flightgear_python.fdm_v24 import fdm_struct as fdm24_struct
from flightgear_python.fdm_v25 import fdm_struct as fdm25_struct

from construct import Struct


def test_v24_length():
    s = Struct(**fdm24_struct)
    assert s.sizeof() == 408


def test_v25_length():
    s = Struct(**fdm25_struct)
    assert s.sizeof() == 552
