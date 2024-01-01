import pytest

from flightgear_python.fg_if import FDMConnection


pytestmark = pytest.mark.fg_integration
fdm_version = 24  # FlightGear-2020.3.19-x86_64.AppImage


def test_fdm_rx_and_tx_integration():
    def rx_cb(fdm_data, event_pipe):
        (run_idx,) = event_pipe.child_recv()
        child_callback_version = fdm_data['version']
        event_pipe.child_send(
            (
                run_idx,
                child_callback_version,
            )
        )
        return fdm_data

    fdm_c = FDMConnection(fdm_version)
    fdm_c.connect_rx('localhost', 5501, rx_cb)
    fdm_c.connect_tx('localhost', 5502)

    for i in range(10):
        fdm_c.event_pipe.parent_send((i,))
        # manually call the process instead of having the process spawn
        fdm_c._fg_packet_roundtrip()
        run_idx, parent_callback_version = fdm_c.event_pipe.parent_recv()
        assert run_idx == i
        assert parent_callback_version == fdm_version

    # Prevent 'ResourceWarning: unclosed' warning
    fdm_c.fg_rx_sock.close()
    fdm_c.fg_tx_sock.close()
