import pytest

from flightgear_python.fg_if import GuiConnection


pytestmark = pytest.mark.fg_integration
gui_version = 8  # FlightGear-2020.3.19-x86_64.AppImage


def test_gui_rx_and_tx_integration():
    def rx_cb(gui_data, event_pipe):
        (run_idx,) = event_pipe.child_recv()
        child_callback_version = gui_data['version']
        event_pipe.child_send(
            (
                run_idx,
                child_callback_version,
            )
        )
        return gui_data

    gui_c = GuiConnection(gui_version)
    gui_c.connect_rx('localhost', 5505, rx_cb)
    gui_c.connect_tx('localhost', 5506)

    for i in range(10):
        gui_c.event_pipe.parent_send((i,))
        # manually call the process instead of having the process spawn
        gui_c._fg_packet_roundtrip()
        run_idx, parent_callback_version = gui_c.event_pipe.parent_recv()
        assert run_idx == i
        assert parent_callback_version == gui_version

    # Prevent 'ResourceWarning: unclosed' warning
    gui_c.fg_rx_sock.close()
    gui_c.fg_tx_sock.close()
