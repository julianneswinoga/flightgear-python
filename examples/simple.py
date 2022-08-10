#!/usr/bin/python3
import time
from flightgear_python.fg_if import FDMConnection

def fdm_callback(fdm_data, event_pipe):
    phi_rad, = event_pipe.child_recv()  # unpack tuple
    fdm_data.phi_rad = phi_rad  # set only the data that we need to
    fdm_data.alt_m = fdm_data.alt_m + 0.5
    return fdm_data  # return the whole structure

"""
Start FlightGear with `--native-fdm=socket,out,30,,5501,udp --native-fdm=socket,in,,,5502,udp`
(you probably also want `--fdm=null` and `--max-fps=30` to stop the simulation fighting with these external commands)
May need to change fdm_version from 24
"""
fdm_conn = FDMConnection(fdm_version=24)
fdm_event_pipe = fdm_conn.connect_rx('localhost', 5501, fdm_callback)
fdm_conn.connect_tx('localhost', 5502)
fdm_conn.start()  # Start the FDM RX/TX loop

phi_rad = 0.0
while True:
    phi_rad += 0.02
    # could also do `fdm_conn.event_pipe.parent_send` so you just need to pass around `fdm_conn`
    fdm_event_pipe.parent_send((phi_rad, ))  # send tuple
    time.sleep(0.01)
