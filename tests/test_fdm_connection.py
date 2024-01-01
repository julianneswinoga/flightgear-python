from flightgear_python.fg_if import FDMConnection
from flightgear_python.fg_util import FGConnectionError
from testing_common import supported_fdm_versions

import pytest


@pytest.mark.parametrize('fdm_version', supported_fdm_versions)
def test_fdm_length(mocker, fdm_version):
    fdm_length = {
        24: 408,
        25: 552,
    }.get(fdm_version, None)
    if fdm_length is None:
        raise NotImplementedError(f'FDM version {fdm_version} length not tested')
    assert FDMConnection(fdm_version).fg_net_struct.sizeof() == fdm_length


def setup_fdm_mock(mocker, version: int, struct_length: int):
    # this is mocking what flightgear will send
    def mock_socket_recvfrom(self, buflen):
        # big endian
        data = bytes([0, 0, 0, version])
        while len(data) < struct_length:
            data += b'\0'
        ret_addr = ('localhost', 12345)
        return data, ret_addr

    # this is mocking what flightgear will receive
    def mock_socket_sendto(self, tx_bytes, addr):
        assert tx_bytes[0:4] == bytes([0, 0, 0, version])

    def mock_socket_bind(self, addr):
        pass

    mocker.patch('socket.socket.recvfrom', mock_socket_recvfrom)
    mocker.patch('socket.socket.sendto', mock_socket_sendto)
    mocker.patch('socket.socket.bind', mock_socket_bind)


@pytest.mark.parametrize('fdm_version', supported_fdm_versions)
def test_fdm_rx_and_tx(mocker, fdm_version):
    def rx_cb(fdm_data, event_pipe):
        (run_idx,) = event_pipe.child_recv()
        callback_version = fdm_data['version']
        event_pipe.child_send(
            (
                run_idx,
                callback_version,
            )
        )
        return fdm_data

    fdm_c = FDMConnection(fdm_version)

    setup_fdm_mock(mocker, fdm_version, fdm_c.fg_net_struct.sizeof())

    fdm_c.connect_rx('localhost', 55550, rx_cb)
    fdm_c.connect_tx('localhost', 55551)

    for i in range(100):
        fdm_c.event_pipe.parent_send((i,))
        # manually call the process instead of having the process spawn
        fdm_c._fg_packet_roundtrip()
        run_idx, callback_version = fdm_c.event_pipe.parent_recv()
        assert run_idx == i
        assert callback_version == fdm_version

    # Prevent 'ResourceWarning: unclosed' warning
    fdm_c.fg_rx_sock.close()
    fdm_c.fg_tx_sock.close()


@pytest.mark.parametrize('fdm_version', supported_fdm_versions)
def test_fdm_only_rx(mocker, fdm_version):
    def rx_cb(fdm_data, event_pipe):
        callback_version = fdm_data['version']
        event_pipe.child_send((callback_version,))

    fdm_c = FDMConnection(fdm_version)

    setup_fdm_mock(mocker, fdm_version, fdm_c.fg_net_struct.sizeof())

    fdm_c.connect_rx('localhost', 55550, rx_cb)

    for i in range(5):
        # manually call the process instead of having the process spawn
        fdm_c._fg_packet_roundtrip()
        (callback_version,) = fdm_c.event_pipe.parent_recv()
        assert callback_version == fdm_version

    # Prevent 'ResourceWarning: unclosed' warning
    fdm_c.fg_rx_sock.close()


def test_fdm_wrong_version_on_create():
    with pytest.raises(NotImplementedError):
        FDMConnection(fdm_version=1)


@pytest.mark.parametrize('fdm_version', supported_fdm_versions)
def test_fdm_bad_port(mocker, fdm_version):
    def mock_bind(addr):
        # Binding to port 1 should usually fail with Should fail with `[Errno 13] Permission denied`
        # but this is more reliable
        raise PermissionError('Mock permission fail')

    mocker.patch('socket.socket.bind', mock_bind)

    fdm_c = FDMConnection(fdm_version)
    with pytest.raises(FGConnectionError):
        fdm_c.connect_rx('localhost', 1, lambda data, pipe: data)
