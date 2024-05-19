#!/usr/bin/python3
"""
Simple Controls example that sweeps the control surfaces and periodically puts the gear up/down
"""
import time
import math
from flightgear_python.fg_if import CtrlsConnection

gear_down_child_state = True
def ctrls_callback(ctrls_data, event_pipe):
    global gear_down_child_state
    if event_pipe.child_poll():
        gear_down_child, = event_pipe.child_recv()  # unpack tuple
        # TODO: FG sometimes ignores "once" updates? i.e. if we set `ctrls_data.gear_handle`
        #  the next callback will still have the old value of `ctrls_data.gear_handle`, not
        #  the one that we set. To fix this we can just keep our own state of what the value
        #  should be and set it every time. I still need to figure out a clean way to fix
        #  this on the backend
        gear_down_child_state = gear_down_child
    ctrls_data.gear_handle = 'down' if gear_down_child_state else 'up'
    # set only the data that we need to
    ctrls_data.aileron = math.sin(time.time())
    ctrls_data.elevator = math.sin(time.time())
    ctrls_data.rudder = math.sin(time.time())
    ctrls_data.throttle[0] = (math.sin(time.time()) / 2) + 0.5
    ctrls_data.throttle[1] = (-math.sin(time.time()) / 2) + 0.5
    return ctrls_data  # return the whole structure

"""
Start FlightGear with `--native-ctrls=socket,out,30,localhost,5503,udp --native-ctrls=socket,in,30,localhost,5504,udp`
"""
if __name__ == '__main__':  # NOTE: This is REQUIRED on Windows!
    ctrls_conn = CtrlsConnection()
    ctrls_event_pipe = ctrls_conn.connect_rx('localhost', 5503, ctrls_callback)
    ctrls_conn.connect_tx('localhost', 5504)
    ctrls_conn.start()  # Start the Ctrls RX/TX loop

    gear_down_parent = True
    time.sleep(2)
    while True:
        # could also do `ctrls_conn.event_pipe.parent_send` so you just need to pass around `ctrls_conn`
        ctrls_event_pipe.parent_send((gear_down_parent,))  # send tuple
        gear_down_parent = not gear_down_parent  # Flip gear state
        time.sleep(10)
