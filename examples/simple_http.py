#!/usr/bin/python3
"""
Simple http example that makes the altitude increase.

Before running the script, start FlightGear with `--httpd=5050`
"""
import time
from pprint import pprint

from flightgear_python.fg_if import HTTPConnection

props_conn = HTTPConnection("localhost", 5050)
pprint(
    props_conn.list_props("/", recurse_limit=0)
)  # List the top-level properties, no recursion
while True:
    alt_ft = props_conn.get_prop("/position/altitude-ft")
    print(f"Altitude: {alt_ft:.1f}ft")
    props_conn.set_prop("/position/altitude-ft", alt_ft + 20.0)
    time.sleep(0.1)
