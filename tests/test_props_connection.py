from flightgear_python.fg_if import PropsConnection


def setup_props_mock(mocker, cmd_str):
    # this is mocking what flightgear will send
    def mock_socket_recv(buflen):
        print('CALL')
        if socket_recv_magic_mock.call_count < 5:
            data = ('A' * buflen).encode()
        else:
            data = b'/> '
        return data

    # this is mocking what flightgear will receive
    def mock_socket_sendall(self, tx_bytes):
        assert cmd_str.encode() in tx_bytes

    def mock_socket_connect(self, addr):
        pass

    socket_recv_magic_mock = mocker.patch('socket.socket.recv', side_effect=mock_socket_recv)
    mocker.patch('socket.socket.sendall', mock_socket_sendall)
    mocker.patch('socket.socket.connect', mock_socket_connect)


def test_props_round_trip(mocker):
    cmd = 'test123'
    setup_props_mock(mocker, cmd)
    p_con = PropsConnection('localhost', 55554)
    resp = p_con._send_cmd_get_resp(cmd)
    assert ('A' * 512) in resp
