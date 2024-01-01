from flightgear_python.fg_if import CtrlsConnection
from flightgear_python.fg_util import FGConnectionError
from testing_common import supported_ctrls_versions

import pytest


def test_ctrls_wrong_version_on_create():
    with pytest.raises(NotImplementedError):
        CtrlsConnection(ctrls_version=1)


@pytest.mark.parametrize('ctrls_version', supported_ctrls_versions)
def test_ctrls_bad_port(mocker, ctrls_version):
    def mock_bind(addr):
        # Binding to port 1 should usually fail with Should fail with `[Errno 13] Permission denied`
        # but this is more reliable
        raise PermissionError('Mock permission fail')

    mocker.patch('socket.socket.bind', mock_bind)

    ctrls_c = CtrlsConnection(ctrls_version)
    with pytest.raises(FGConnectionError):
        # Should fail with [Errno 13] Permission denied
        ctrls_c.connect_rx('localhost', 1, lambda data, pipe: data)
