from flightgear_python.fg_if import GuiConnection
from flightgear_python.fg_util import FGConnectionError
from testing_common import supported_gui_versions

import pytest


def test_gui_wrong_version_on_create():
    with pytest.raises(NotImplementedError):
        GuiConnection(gui_version=1)


@pytest.mark.parametrize('gui_version', supported_gui_versions)
def test_gui_bad_port(mocker, gui_version):
    def mock_bind(addr):
        # Binding to port 1 should usually fail with Should fail with `[Errno 13] Permission denied`
        # but this is more reliable
        raise PermissionError('Mock permission fail')

    mocker.patch('socket.socket.bind', mock_bind)

    gui_c = GuiConnection(gui_version)
    with pytest.raises(FGConnectionError):
        # Should fail with [Errno 13] Permission denied
        gui_c.connect_rx('localhost', 1, lambda data, pipe: data)


@pytest.mark.timeout(3)  # If this fails don't wait a long time
@pytest.mark.parametrize('gui_version', supported_gui_versions)
def test_gui_rx_timeout(mocker, gui_version):
    gui_c = GuiConnection(gui_version, rx_timeout_s=0.1)
    gui_c.connect_rx('localhost', 9999, lambda data, pipe: data)
    with pytest.raises(FGConnectionError, match='[Tt]imeout'):
        gui_c._fg_packet_roundtrip()
