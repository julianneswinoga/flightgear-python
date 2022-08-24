#!/usr/bin/python3
"""
Simple example that makes the altitude increase and the plane roll in the air.
"""
import time
from flightgear_python.fg_if import PropsConnection

"""
Start FlightGear with `--telnet=socket,bi,,localhost,5500,tcp`
"""
props_conn = PropsConnection('localhost', 5500)
props_conn.connect()

sim_props = props_conn.list_props('/', recurse_limit=1)
print(sim_props)
while True:
    alt_ft = props_conn.get_prop('/position/altitude-ft')
    print(f'Altitude: {alt_ft}')
    props_conn.set_prop('/position/altitude-ft', alt_ft + 50.0)
    time.sleep(0.2)
