import runpy
import multiprocess as mp
from pathlib import Path

import pytest
import _pytest.outcomes

pytestmark = pytest.mark.fg_integration


@pytest.mark.timeout(10)  # Examples have infinite loops
@pytest.mark.parametrize('example_script_path', Path(__file__, '..', '..', 'examples').resolve().glob('*.py'))
def test_gui_rx_and_tx_integration(example_script_path: Path):
    try:
        runpy.run_path(str(example_script_path), run_name='__main__')
    except _pytest.outcomes.Failed as py_fail:
        # Timeout is expected, otherwise it's a real error
        if 'timeout' not in py_fail.msg.lower():
            raise py_fail
    # With rx_proc.daemon this isn't strictly necessary, but without manually
    # calling terminate the callback process still seem to be running. So this
    # is still a good thing to do.
    for mp_child in mp.active_children():
        mp_child.terminate()
