#!/usr/bin/python3
"""
Simple GUI example TODO: Docs
"""
import time
from flightgear_python.fg_if import GuiConnection

def gui_callback(gui_data, event_pipe):
    print(gui_data)
    return gui_data

"""
Start FlightGear with `--native-gui=socket,out,30,localhost,5504,udp --native-gui=socket,in,30,localhost,5505,udp`
"""
if __name__ == '__main__':  # NOTE: This is REQUIRED on Windows!
    gui_conn = GuiConnection(gui_version=8)
    ctrls_event_pipe = gui_conn.connect_rx('localhost', 5504, gui_callback)
    gui_conn.connect_tx('localhost', 5505)
    gui_conn.start()  # Start the GUI RX/TX loop

    time.sleep(2)
    while True:
        # could also do `gui_conn.event_pipe.parent_send` so you just need to pass around `gui_conn`
        # ctrls_event_pipe.parent_send((gear_down_parent,))  # send tuple
        # gear_down_parent = not gear_down_parent  # Flip gear state
        time.sleep(10)
