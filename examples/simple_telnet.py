#!/usr/bin/python3
"""
Simple telnet example that makes the altitude increase.

Before running the script, start FlightGear with
`--telnet=socket,bi,60,localhost,5500,tcp`

Note: according to the documentation [1] and the underlying source
code [2], only the rate and port parameters are used. Moreover,
increasing the rate does help FlightGear process the commands faster,
although I found diminishing returns after 120-150 Hz (depending on the
system used).

[1]: https://wiki.flightgear.org/Telnet_usage#:~:text=Use%20HZ%20to,call%20something%20like%3A
[2]: https://gitlab.com/flightgear/flightgear/-/blob/next/src/Network/propsProtocol.cxx?ref_type=heads#L717-743
"""
import time
from pprint import pprint

from flightgear_python.fg_if import PropsConnection

props_conn = PropsConnection("localhost", 5500)
props_conn.connect()  # Make an actual connection
pprint(
    props_conn.list_props("/", recurse_limit=0)
)  # List the top-level properties, no recursion
while True:
    alt_ft = props_conn.get_prop("/position/altitude-ft")
    print(f"Altitude: {alt_ft:.1f}ft")
    props_conn.set_prop("/position/altitude-ft", alt_ft + 20.0)
    time.sleep(0.1)
