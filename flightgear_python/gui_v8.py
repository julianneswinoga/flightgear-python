"""
FlightGear GUI Network interface, version 8

See https://github.com/FlightGear/flightgear/blob/a756ad0f430c7d2d992f6987d256675042e4e7d4/src/Network/net_gui.hxx
"""

from construct import Struct, Array, Const, Bytes, Int32ul, Float64l, Float32l

# FG_MAX_ENGINES = 4  #: Constant value from enum TODO: Unused?
# FG_MAX_WHEELS = 3  #: Constant value from enum. TODO: Unused?
FG_MAX_TANKS = 4  #: Constant value from enum

# Little endian TODO: Why is this the only little endian interface
#: GUI v8 structure
gui_struct = Struct(
    'version' / Const(8, Int32ul),
    '_padding0' / Bytes(4),
    'lon_rad' / Float64l,  # geodetic
    'lat_rad' / Float64l,  # geodetic
    'alt_m' / Float32l,  # above sea level
    'agl_m' / Float32l,  # above ground level
    'phi_rad' / Float32l,  # roll
    'theta_rad' / Float32l,  # pitch
    'psi_rad' / Float32l,  # yaw or true heading
    'vcas' / Float32l,  # calibrated airspeed
    'climb_rate_ft_per_s' / Float32l,
    'num_tanks' / Int32ul,  # Max number of fuel tanks
    'fuel_quantity' / Array(FG_MAX_TANKS, Float32l),
    'cur_time_s' / Int32ul,  # current unix time
    'warp_s' / Int32ul,  # offset in seconds to unix time TODO: why is this unsigned?
    'ground_elev_m' / Float32l,  # ground elev (meters)
    'tuned_freq_MHz' / Float32l,  # currently tuned frequency TODO: Verify this is MHz
    'nav_radial' / Float32l,  # target nav radial
    'in_range' / Int32ul,  # tuned navaid is in range?
    'dist_nm' / Float32l,  # distance to tuned navaid in nautical miles
    'course_deviation_deg' / Float32l,  # degrees off target course
    'gs_deviation_deg' / Float32l,  # degrees off target glide slope
)
