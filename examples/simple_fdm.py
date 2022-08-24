#!/usr/bin/python3
"""
Simple Flight Dynamics Model (FDM) example that makes the altitude increase and the plane roll in the air.
"""
import time
from flightgear_python.fg_if import FDMConnection

def fdm_callback(fdm_data, event_pipe):
    phi_rad_child, = event_pipe.child_recv()  # unpack tuple
    # set only the data that we need to
    fdm_data['phi_rad'] = phi_rad_child  # we can force our own values
    fdm_data.alt_m = fdm_data.alt_m + 0.5  # or just make a relative change
    return fdm_data  # return the whole structure

"""
Start FlightGear with `--native-fdm=socket,out,30,,5501,udp --native-fdm=socket,in,30,,5502,udp`
(you probably also want `--fdm=null` and `--max-fps=30` to stop the simulation fighting with
these external commands)
"""
fdm_conn = FDMConnection(fdm_version=24)  # May need to change version from 24
fdm_event_pipe = fdm_conn.connect_rx('localhost', 5501, fdm_callback)
fdm_conn.connect_tx('localhost', 5502)
fdm_conn.start()  # Start the FDM RX/TX loop

phi_rad_parent = 0.0
while True:
    phi_rad_parent += 0.02
    # could also do `fdm_conn.event_pipe.parent_send` so you just need to pass around `fdm_conn`
    fdm_event_pipe.parent_send((phi_rad_parent,))  # send tuple
    time.sleep(0.01)
