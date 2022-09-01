from flightgear_python.fg_if import FDMConnection

import pytest

supported_fdm_versions = [24, 25, ]


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
def test_fdm_happypath(mocker, fdm_version):
    rx_cb = lambda s, e_p: s

    fdm_c = FDMConnection(fdm_version)

    setup_fdm_mock(mocker, fdm_version, fdm_c.fg_net_struct.sizeof())

    fdm_c.connect_rx('localhost', 55550, rx_cb)
    fdm_c.connect_tx('localhost', 55551)

    for i in range(500):
        # manually call the process instead of having the process spawn
        fdm_c._fg_packet_roundtrip()
