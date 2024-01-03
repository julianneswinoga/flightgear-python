#!/usr/bin/python3
"""
Simple telnet example that makes the altitude increase.
"""
import time
from pprint import pprint
from flightgear_python.fg_if import TelnetConnection

"""
Start FlightGear with `--telnet=socket,bi,60,localhost,5500,tcp`
"""
telnet_conn = TelnetConnection('localhost', 5500)
telnet_conn.connect()  # Make an actual connection
telnet_props = telnet_conn.list_props('/', recurse_limit=0)
pprint(telnet_props)  # List the top-level properties, no recursion

while True:
    alt_ft = telnet_conn.get_prop('/position/altitude-ft')
    print(f'Altitude: {alt_ft:.1f}ft')
    telnet_conn.set_prop('/position/altitude-ft', alt_ft + 20.0)
    time.sleep(0.1)
