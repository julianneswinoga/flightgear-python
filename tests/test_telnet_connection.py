import pytest

from flightgear_python.fg_if import TelnetConnection


def setup_props_mock(mocker, cmd_str):
    # this is mocking what flightgear will send
    def mock_socket_recv(buflen):
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


def test_telnet_round_trip(mocker):
    cmd = 'test123'
    setup_props_mock(mocker, cmd)
    t_con = TelnetConnection('localhost', 55554)
    resp = t_con._send_cmd_get_resp(cmd)
    assert ('A' * 512) in resp
    # Prevent 'ResourceWarning: unclosed' warning
    t_con.sock.close()


def test_telnet_get_prop_must_be_absolute(mocker):
    cmd = 'test123'
    setup_props_mock(mocker, cmd)
    t_con = TelnetConnection('localhost', 55554)
    with pytest.raises(ValueError):
        t_con.get_prop('non_absolute/path')


def test_telnet_set_prop_must_be_absolute(mocker):
    cmd = 'test123'
    setup_props_mock(mocker, cmd)
    t_con = TelnetConnection('localhost', 55554)
    with pytest.raises(ValueError):
        t_con.set_prop('non_absolute/path', 'test value')


def test_telnet_deprecated_name_still_works():
    from flightgear_python.fg_if import PropsConnection

    with pytest.deprecated_call():
        t_con = PropsConnection('localhost', 55554)
    # Prevent 'ResourceWarning: unclosed' warning
    t_con.sock.close()


# ---------------------------------------------------------------------------
# run_nasal tests
# ---------------------------------------------------------------------------


def test_telnet_run_nasal_sends_correct_payload(mocker):
    sent = []

    def mock_sendall(self, data):
        sent.append(data)

    def mock_recv(buflen):
        return b'/> '

    mocker.patch('socket.socket.sendall', mock_sendall)
    mocker.patch('socket.socket.recv', side_effect=mock_recv)

    t_con = TelnetConnection('localhost', 55554)
    code = 'print("hello");'
    t_con.run_nasal(code)

    assert sent == [f'nasal\r\n{code}\r\n##EOF##\r\n\r\n'.encode()]
    t_con.sock.close()


def test_telnet_run_nasal_returns_output(mocker):
    chunks = [b'hello from FG\r\n/> ']

    def mock_recv(buflen):
        return chunks.pop(0) if chunks else b'/> '

    mocker.patch('socket.socket.sendall')
    mocker.patch('socket.socket.recv', side_effect=mock_recv)

    t_con = TelnetConnection('localhost', 55554)
    assert t_con.run_nasal('print("hello from FG");') == 'hello from FG'
    t_con.sock.close()
