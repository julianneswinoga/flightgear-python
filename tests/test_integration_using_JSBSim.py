import math

import pytest

# from testing_common import supported_fdm_versions
from jsbsim_wrapper.jsbsim_wrapper import (
    FlightGearUdpOutput,
    JsbConfig,
    Waypoint,
    setup_jsbsim,
)

from flightgear_python.fg_if import FDMConnection

# TODO: JSBSim 1.1.11 doesn't support FDM v25
#  Once we drop 3.6 we can fully test v25
supported_fdm_versions = [24]


def fdm_callback(fdm_data, event_pipe):
    child_data = (
        fdm_data["lat_rad"],
        fdm_data["lon_rad"],
        fdm_data["alt_m"],
    )
    print("Callback!", child_data)
    event_pipe.child_send(child_data)


@pytest.mark.parametrize("fdm_version", supported_fdm_versions)
def test_jsbsim_integration(fdm_version, capsys):
    fg_to_py_port = 5000 + fdm_version  # So that tests can run parallel
    fdm_conn = FDMConnection(fdm_version=fdm_version)
    fdm_conn.connect_rx("localhost", fg_to_py_port, fdm_callback)

    update_rate = 60
    jsb_time_step = 1 / update_rate
    jsb_config = JsbConfig(
        waypoints=[
            Waypoint(46.667094, 7.827569, 2500),
            Waypoint(46.646220, 7.649860, 3000),
            Waypoint(46.765000, 7.626200, 3500),
        ],
        flightgear_outputs=[
            FlightGearUdpOutput(
                "localhost", fg_to_py_port, update_rate, fg_version=fdm_version
            ),
        ],
        time_step=jsb_time_step,
    )
    fdm_conn.start()

    jsbfdm = setup_jsbsim(jsb_config)

    total_sim_steps = int(1e4)
    pos_history = []
    for sim_step_idx in range(total_sim_steps):
        if not jsbfdm.run():
            print(f"Test ended early {fdm_version}, {sim_step_idx}")
            assert False

        assert fdm_conn.rx_proc.is_alive()

        if fdm_conn.event_pipe.parent_poll(timeout=jsb_time_step):
            lat_rad, lon_rad, alt_m = fdm_conn.event_pipe.parent_recv()
            lat_deg = math.degrees(lat_rad)
            lon_deg = math.degrees(lon_rad)
            pos_history.append((sim_step_idx, lat_deg, lon_deg, alt_m))

    fdm_conn.stop()

    # Make sure we got at least half of the updates
    total_updates = len(pos_history)
    assert total_updates > (total_sim_steps / 2)
    sim_step_idx, lat_deg, lon_deg, alt_m = pos_history[-1]
    # Check the end location
    assert 46.6 < lat_deg < 46.8
    assert 7.6 < lon_deg < 7.9
    assert 2000 < alt_m < 4000

    with capsys.disabled():
        print(
            f"\nLast update (got {total_updates}/{total_sim_steps}) @ {sim_step_idx}: {lat_deg},{lon_deg},{alt_m}"
        )
