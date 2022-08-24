#!/usr/bin/python3
"""
Simple telnet example that makes the altitude increase.
"""
import time
from pprint import pprint
from flightgear_python.fg_if import PropsConnection

"""
Start FlightGear with `--telnet=socket,bi,60,localhost,5500,tcp`
"""
props_conn = PropsConnection('localhost', 5500)
props_conn.connect()  # Make an actual connection
pprint(props_conn.list_props('/', recurse_limit=0))  # List the top-level properties, no recursion
while True:
    alt_ft = props_conn.get_prop('/position/altitude-ft')
    print(f'Altitude: {alt_ft:.1f}ft')
    props_conn.set_prop('/position/altitude-ft', alt_ft + 20.0)
    time.sleep(0.1)
