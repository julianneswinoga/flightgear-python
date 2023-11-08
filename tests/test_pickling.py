"""
We don't care about pickling per-say, but multiprocess uses the dill library
to spin up new processes. This only seems to be a problem on Windows, but we need
to support the weird way Windows implements fork().
"""
import dill
import pytest
from _pytest.outcomes import Failed
from testing_common import (
    supported_ctrls_versions,
    supported_fdm_versions,
    supported_gui_versions,
)

from flightgear_python.fg_if import CtrlsConnection, FDMConnection, GuiConnection


@pytest.mark.parametrize("fdm_version", supported_fdm_versions)
def test_pickle_fdm(fdm_version):
    fdm_c = FDMConnection(fdm_version)
    try:
        dill.dumps(fdm_c.fg_net_struct)
    except dill.PicklingError as e:
        raise Failed(f"Failed to pickle FDM fg_net_struct: {e}") from None


@pytest.mark.parametrize("ctrls_version", supported_ctrls_versions)
def test_pickle_ctrls(ctrls_version):
    ctrls_c = CtrlsConnection(ctrls_version)
    try:
        dill.dumps(ctrls_c.fg_net_struct)
    except dill.PicklingError as e:
        raise Failed(f"Failed to pickle Ctrls fg_net_struct: {e}") from None


@pytest.mark.parametrize("gui_version", supported_gui_versions)
def test_pickle_gui(gui_version):
    gui_c = GuiConnection(gui_version)
    try:
        dill.dumps(gui_c.fg_net_struct)
    except dill.PicklingError as e:
        raise Failed(f"Failed to pickle Gui fg_net_struct: {e}") from None
