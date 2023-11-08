import math
import tempfile
import time
from pathlib import Path
from typing import List, NamedTuple

import jsbsim

from tests.testing_common import fill_xml_template, m_to_ft


class Waypoint(NamedTuple):
    lat_deg: float
    lon_deg: float
    alt_m: float  # relative to sea-level


class FlightGearUdpOutput(NamedTuple):
    ip_addr: str
    port: int
    rate_hz: int
    fg_version: int = 24


class JsbConfig(NamedTuple):
    # required
    waypoints: List[Waypoint]
    # Must be at least 1 FlightGear output (it'll be the internal one to the python script)
    flightgear_outputs: List[FlightGearUdpOutput]
    # optional
    vehicle_str: str = "c310"
    wp_distance_thresh: float = 500.0  # I think this is feet?
    end_time: float = 60 * 60 * 24  # Default 24 hours
    time_step: float = 1.0 / 50.0  # Default 50Hz


def fix_jsb_latitude(lat_deg: float) -> float:
    """
    import tempfile
    import jsbsim
    import simplekml
    from jsbsim_wrapper import build_wp_xml, fix_jsb_latitude
    from helpers import fill_xml_template
    def test_jsb_over_world():
        frange = lambda start, stop, step: [(x * step) for x in range(int(start / step), int(stop / step), 1)]
        kml = simplekml.Kml()
        lat_diffs = []
        lon_diffs = []
        idx = 0
        for requested_lat in frange(-90, 90, 5):
            for requested_lon in frange(0, 1, 1):
                jsbfdm = jsbsim.FGFDMExec(None)  # Use JSBSim default aircraft data
                jsbfdm.set_debug_level(0)
                init_script_xml = fill_xml_template('jsbsim_wrapper/xml_templates/jsb_initialize_vehicle.xml', lat_deg=fix_jsb_latitude(requested_lat), lon_deg=requested_lon, alt_m=1000)
                wp_xml = build_wp_xml([], 100)
                with tempfile.NamedTemporaryFile('w', suffix='.xml') as initialize_fp:
                    initialize_fp.write(init_script_xml)
                    initialize_fp.flush()
                    veh_script_xml = fill_xml_template(
                        'jsbsim_wrapper/xml_templates/jsb_vehicle_script.xml',
                        init_script_path=initialize_fp.name,
                        vehicle='c310',
                        wp_xml=wp_xml,
                        end_time=5000,
                        time_step=(1/50),
                    )
                    with tempfile.NamedTemporaryFile('w', suffix='.xml') as script_fp:
                        script_fp.write(veh_script_xml)
                        script_fp.flush()
                        jsbfdm.load_script(script_fp.name)
                jsbfdm.run_ic()  # setup initial conditions
                jsbfdm.run()
                actual_lat = jsbfdm.get_property_value('position/lat-geod-deg')
                actual_lon = jsbfdm.get_property_value('position/long-gc-deg')

                # KML points are lon,lat,hgt
                from_loc = [requested_lon, requested_lat, 1000]
                to_loc = [actual_lon, actual_lat, 1000]

                kml.newpoint(name=f'{idx}a', coords=[from_loc], altitudemode=simplekml.AltitudeMode.clamptoground)
                kml.newpoint(name=f'{idx}b', coords=[to_loc], altitudemode=simplekml.AltitudeMode.clamptoground)
                kml.newlinestring(name=str(idx), coords=[from_loc, to_loc], altitudemode=simplekml.AltitudeMode.clamptoground)

                lat_diffs.append(requested_lat - actual_lat)
                lon_diffs.append(requested_lon - actual_lon)
                print(f'{requested_lat} {actual_lat:.6f}')
                idx += 1
        print(f'min: {min(lat_diffs)} {min(lon_diffs)}')
        print(f'max: {max(lat_diffs)} {max(lon_diffs)}')
        print(f'avg: {sum(lat_diffs)/len(lat_diffs)} {sum(lon_diffs)/len(lat_diffs)}')
        kml.save('./JSB_geo_diff.kml', format=False)
    """
    # These constants fit to the error sort of well. Still 20m error at worst case
    a = -0.192465694889549
    b = 2.00002985781682
    fixed_lat_deg = lat_deg + (a * math.sin(math.radians(lat_deg) * b))
    return fixed_lat_deg


def build_wp_xml(wp_list: List[Waypoint], wp_distance_thresh: float) -> str:
    wp_xml = ""
    for wp_idx, waypoint_data in enumerate(wp_list, start=1):
        prev_wp_idx = len(wp_list) if wp_idx == 1 else wp_idx - 1
        conditions = f"""
<condition logic="AND">
    ap/active-waypoint eq {prev_wp_idx}
    guidance/wp-distance lt {wp_distance_thresh}
</condition>
"""
        if wp_idx == 1:
            # Add in the first condition: if active waypoint is 0 (not set), start going to 1
            conditions = f"""
<condition logic="OR">
    ap/active-waypoint eq 0
    {conditions}
</condition>
"""
        wp_xml += fill_xml_template(
            "jsbsim_wrapper/xml_templates/jsb_single_wp.xml",
            wp_idx=wp_idx,
            conditions=conditions,
            lat_rad=math.radians(waypoint_data.lat_deg),
            lon_rad=math.radians(waypoint_data.lon_deg),
            alt_ft=m_to_ft(waypoint_data.alt_m),
        )
    return wp_xml


def build_initialize_xml(jsb_config: JsbConfig) -> str:
    # Take the starting location from the last waypoint
    start_lat_deg, start_lon_deg, start_alt_m = jsb_config.waypoints[-1]
    init_script_xml = fill_xml_template(
        "jsbsim_wrapper/xml_templates/jsb_initialize_vehicle.xml",
        lat_deg=start_lat_deg,
        lon_deg=start_lon_deg,
        alt_m=start_alt_m,
    )
    return init_script_xml


def build_vehicle_xml(jsb_config: JsbConfig, init_script_path: str) -> str:
    wp_xml = build_wp_xml(jsb_config.waypoints, jsb_config.wp_distance_thresh)

    outputs_config_xml = ""
    for fg_output in jsb_config.flightgear_outputs:
        output_config_xml = fill_xml_template(
            "jsbsim_wrapper/xml_templates/jsb_output_config_flightgear.xml",
            flightgear_ip=fg_output.ip_addr,
            flightgear_port=fg_output.port,
            flightgear_version=fg_output.fg_version,
            flightgear_rate=fg_output.rate_hz,
        )
        outputs_config_xml += output_config_xml

    veh_script_xml = fill_xml_template(
        "jsbsim_wrapper/xml_templates/jsb_vehicle_script.xml",
        init_script_path=init_script_path,  # Vehicle script references the initialize script path
        vehicle=jsb_config.vehicle_str,
        wp_xml=wp_xml,
        end_time=jsb_config.end_time,
        time_step=jsb_config.time_step,
        outputs_xml=outputs_config_xml,
    )
    return veh_script_xml


def make_and_load_jsb_scripts(jsbfdm: jsbsim.FGFDMExec, jsb_config: JsbConfig):
    # Create initialize script
    init_script_fp = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False)
    init_script_path = init_script_fp.name
    init_script_xml = build_initialize_xml(jsb_config)
    init_script_fp.write(init_script_xml)
    init_script_fp.flush()
    init_script_fp.close()

    # Create vehicle script
    veh_script_fp = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False)
    veh_script_path = veh_script_fp.name
    veh_script_xml = build_vehicle_xml(jsb_config, init_script_path)
    print(f"Full vehicle script @ {veh_script_path}:\n{veh_script_xml}")
    veh_script_fp.write(veh_script_xml)
    veh_script_fp.flush()
    veh_script_fp.close()  # Need to close file before it can be read. Windows issue :/

    # Tell JSB to load the vehicle script
    script_loaded = jsbfdm.load_script(veh_script_path)
    if not script_loaded:
        raise FileNotFoundError(f"JSB failed to load script: {veh_script_path}")

    # cleanup
    # Can't use missing_ok, introduced in 3.8
    if Path(init_script_path).is_file():
        Path(init_script_path).unlink()
    if Path(veh_script_path).is_file():
        Path(veh_script_path).unlink()


def setup_jsbsim(jsb_config: JsbConfig) -> jsbsim.FGFDMExec:
    # Before we do anything, go through and fix the waypoints to be correct :/
    fixed_waypoints = []
    for waypoint in jsb_config.waypoints:
        fixed_wp = Waypoint(
            fix_jsb_latitude(waypoint.lat_deg), waypoint.lon_deg, waypoint.alt_m
        )
        fixed_waypoints.append(fixed_wp)
    jsb_config = jsb_config._replace(waypoints=fixed_waypoints)

    jsbfdm = jsbsim.FGFDMExec(None)  # Use JSBSim default aircraft data
    default_dbg_level = jsbfdm.get_debug_level()

    jsbfdm.set_debug_level(0)  # initial output is too noisy
    make_and_load_jsb_scripts(jsbfdm, jsb_config)
    jsbfdm.run_ic()  # setup initial conditions

    jsbfdm.set_debug_level(default_dbg_level)

    return jsbfdm
