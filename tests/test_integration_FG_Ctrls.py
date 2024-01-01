import pytest

from flightgear_python.fg_if import CtrlsConnection


pytestmark = pytest.mark.fg_integration
ctrls_version = 27  # FlightGear-2020.3.19-x86_64.AppImage


def test_ctrls_rx_and_tx_integration():
    def rx_cb(ctrls_data, event_pipe):
        (run_idx,) = event_pipe.child_recv()
        child_callback_version = ctrls_data['version']
        event_pipe.child_send(
            (
                run_idx,
                child_callback_version,
            )
        )
        return ctrls_data

    ctrls_c = CtrlsConnection(ctrls_version)
    ctrls_c.connect_rx('localhost', 5503, rx_cb)
    ctrls_c.connect_tx('localhost', 5504)

    for i in range(10):
        ctrls_c.event_pipe.parent_send((i,))
        # manually call the process instead of having the process spawn
        ctrls_c._fg_packet_roundtrip()
        run_idx, parent_callback_version = ctrls_c.event_pipe.parent_recv()
        assert run_idx == i
        assert parent_callback_version == ctrls_version

    # Prevent 'ResourceWarning: unclosed' warning
    ctrls_c.fg_rx_sock.close()
    ctrls_c.fg_tx_sock.close()
