"""
FlightGear Flight Dynamics Model Network interface, version 25

See https://github.com/FlightGear/flightgear/blob/4049acd84e6ce391184716d1020c456d389f919e/src/Network/net_fdm.hxx
"""

from construct import Struct, Array, Enum, Const, Bytes, Int32ub, Int32sb, Float64b, Float32b

FG_MAX_ENGINES = 4  #: Constant value from enum
FG_MAX_WHEELS = 3  #: Constant value from enum
FG_MAX_TANKS = 4  #: Constant value from enum

# Big endian
#: FDM v25 structure
fdm_struct = Struct(
    'version' / Const(25, Int32ub),
    '_padding' / Bytes(4),
    'lon_rad' / Float64b,
    'lat_rad' / Float64b,
    'alt_m' / Float64b,
    'agl_m' / Float32b,
    'phi_rad' / Float32b,
    'theta_rad' / Float32b,
    'psi_rad' / Float32b,
    'alpha_rad' / Float32b,
    'beta_rad' / Float32b,
    'phidot_rad_per_s' / Float32b,
    'thetadot_rad_per_s' / Float32b,
    'psidot_rad_per_s' / Float32b,
    'vcas' / Float32b,  # calibrated airspeed
    'climb_rate_ft_per_s' / Float32b,
    'v_north_ft_per_s' / Float32b,
    'v_east_ft_per_s' / Float32b,
    'v_down_ft_per_s' / Float32b,
    'v_body_u' / Float32b,  # ECEF velocity in body frame
    'v_body_v' / Float32b,  # ECEF velocity in body frame
    'v_body_w' / Float32b,  # ECEF velocity in body frame
    'A_X_pilot_ft_per_s_per_s' / Float32b,
    'A_Y_pilot_ft_per_s_per_s' / Float32b,
    'A_Z_pilot_ft_per_s_per_s' / Float32b,
    'stall_warning' / Float32b,  # 0.0 - 1.0 indicating the amount of stall
    'slip_deg' / Float32b,  # slip ball deflection
    'num_engines' / Int32ub,
    'eng_state' / Array(FG_MAX_ENGINES, Enum(Int32ub, off=0, cranking=1, running=2)),  # Engine state
    'rpm' / Array(FG_MAX_ENGINES, Float32b),
    'fuel_flow_gal_per_hr' / Array(FG_MAX_ENGINES, Float32b),
    'fuel_px_psi' / Array(FG_MAX_ENGINES, Float32b),
    'egt_deg_F' / Array(FG_MAX_ENGINES, Float32b),
    'cht_deg_F' / Array(FG_MAX_ENGINES, Float32b),
    'mp_osi' / Array(FG_MAX_ENGINES, Float32b),  # Manifold pressure
    'tit' / Array(FG_MAX_ENGINES, Float32b),  # Turbine Inlet Temperature
    'oil_temp_deg_F' / Array(FG_MAX_ENGINES, Float32b),
    'oil_px_psi' / Array(FG_MAX_ENGINES, Float32b),
    'num_tanks' / Int32ub,  # Max number of fuel tanks
    'fuel_quantity' / Array(FG_MAX_TANKS, Float32b),
    # v24->v25 changes
    'tank_selected' / Array(FG_MAX_TANKS, Int32ub),
    'capacity_m3' / Array(FG_MAX_TANKS, Float64b),
    'unusable_m3' / Array(FG_MAX_TANKS, Float64b),
    'density_kgpm3' / Array(FG_MAX_TANKS, Float64b),
    'level_m3' / Array(FG_MAX_TANKS, Float64b),
    # end changes
    'num_wheels' / Int32ub,
    'wow' / Array(FG_MAX_WHEELS, Int32ub),
    'gear_pos' / Array(FG_MAX_WHEELS, Float32b),
    'gear_steer' / Array(FG_MAX_WHEELS, Float32b),
    'gear_compression' / Array(FG_MAX_WHEELS, Float32b),
    'cur_time_s' / Int32ub,  # current unix time
    'warp_s' / Int32sb,  # offset in seconds to unix time
    'visibility_m' / Float32b,
    'elevator' / Float32b,
    'elevator_trim_tab' / Float32b,
    'left_flap' / Float32b,
    'right_flap' / Float32b,
    'left_aileron' / Float32b,
    'right_aileron' / Float32b,
    'rudder' / Float32b,
    'nose_wheel' / Float32b,
    'speedbrake' / Float32b,
    'spoilers' / Float32b,
)
