#!/usr/bin/python3
"""
Simple GUI example that prints the latitude and longitude of the aircraft
"""
import time
import math
from flightgear_python.fg_if import GuiConnection

def gui_callback(gui_data, event_pipe):
    lat_deg = math.degrees(gui_data['lat_rad'])
    lon_deg = math.degrees(gui_data['lon_rad'])
    child_data = (lat_deg, lon_deg)
    event_pipe.child_send(child_data)

"""
Start FlightGear with `--native-gui=socket,out,30,localhost,5504,udp --native-gui=socket,in,30,localhost,5505,udp`
"""
if __name__ == '__main__':  # NOTE: This is REQUIRED on Windows!
    gui_conn = GuiConnection()
    gui_event_pipe = gui_conn.connect_rx('localhost', 5504, gui_callback)
    # Note: I couldn't get FlightGear to do anything with the returned data on this interface
    # I think it's just ignoring everything. Technically you can send data back though.
    # gui_conn.connect_tx('localhost', 5505)
    gui_conn.start()  # Start the GUI RX loop

    while True:
        # could also do `gui_conn.event_pipe.parent_recv` so you just need to pass around `gui_conn`
        pipe_data = gui_event_pipe.parent_recv()  # receive tuple
        lat_deg, lon_deg = pipe_data
        print(f'Lat: {lat_deg:.6f} Lon: {lon_deg:.6f}')
        time.sleep(0.01)
