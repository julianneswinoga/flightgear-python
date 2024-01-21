"""
FlightGear Controls Network interface, version 27

See https://github.com/FlightGear/flightgear/blob/619226e9d069d2a3e8ebf8658fb5441ca8a2c233/src/Network/net_ctrls.hxx
"""

from construct import Struct, Array, Enum, Const, Bytes, Int32ub, Float64b, BitStruct, Bit, BitsInteger

RESERVED_SPACE = 25  #: Constant value from define

FG_MAX_ENGINES = 4  #: Constant value from enum
# FG_MAX_WHEELS = 16  #: Constant value from enum. TODO: Unused?
FG_MAX_TANKS = 8  #: Constant value from enum

# Big endian
#: Ctrls v27 structure
ctrls_struct = Struct(
    'version' / Const(27, Int32ub),
    '_padding0' / Bytes(4),  # TODO: Not documented, probably due to struct packing
    'aileron' / Float64b,  # -1 ... 1
    'elevator' / Float64b,  # -1 ... 1
    'rudder' / Float64b,  # -1 ... 1
    'aileron_trim' / Float64b,  # -1 ... 1
    'elevator_trim' / Float64b,  # -1 ... 1
    'rudder_trim' / Float64b,  # -1 ... 1
    'flaps' / Float64b,  # 0 ... 1
    'spoilers' / Float64b,
    'speedbrake' / Float64b,
    'flaps_power' / Enum(Int32ub, unavailable=0, available=1),
    'flap_motor_ok' / Int32ub,
    'num_engines' / Int32ub,
    'master_bat' / Array(FG_MAX_ENGINES, Enum(Int32ub, off=0, on=1)),
    'master_alt' / Array(FG_MAX_ENGINES, Enum(Int32ub, off=0, on=1)),
    'magnetos' / Array(FG_MAX_ENGINES, Int32ub),
    'starter_power' / Array(FG_MAX_ENGINES, Enum(Int32ub, off=0, on=1)),
    # throttle needs to be moved forward 1 double?
    '_padding3' / Bytes(4),  # TODO: Not documented, probably due to struct packing
    'throttle' / Array(FG_MAX_ENGINES, Float64b),  # 0 ... 1
    'mixture' / Array(FG_MAX_ENGINES, Float64b),  # 0 ... 1
    'condition' / Array(FG_MAX_ENGINES, Float64b),  # 0 ... 1
    'fuel_pump_power' / Array(FG_MAX_ENGINES, Enum(Int32ub, off=0, on=1)),
    'prop_advance' / Array(FG_MAX_ENGINES, Float64b),  # 0 ... 1
    'feed_tank_to' / Array(4, Int32ub),
    'reverse' / Array(4, Int32ub),
    'engine_ok' / Array(FG_MAX_ENGINES, Int32ub),
    'mag_left_ok' / Array(FG_MAX_ENGINES, Int32ub),
    'mag_right_ok' / Array(FG_MAX_ENGINES, Int32ub),
    'spark_plugs_ok' / Array(FG_MAX_ENGINES, Enum(Int32ub, fouled=0, ok=1)),
    'oil_press_status' / Array(FG_MAX_ENGINES, Enum(Int32ub, normal=0, low=1, full_fail=2)),
    'fuel_pump_ok' / Array(FG_MAX_ENGINES, Int32ub),
    'num_tanks' / Int32ub,
    'fuel_selector' / Array(FG_MAX_TANKS, Enum(Int32ub, off=0, on=1)),
    'xfer_pump' / Array(5, Int32ub),  # specifies transfer from array value tank to tank specified by int value
    'cross_feed' / Enum(Int32ub, off=0, on=1),
    '_padding4' / Bytes(4),  # TODO: Not documented, probably due to struct packing
    'brake_left' / Float64b,
    'brake_right' / Float64b,
    'copilot_brake_left' / Float64b,
    'copilot_brake_right' / Float64b,
    'brake_parking' / Float64b,
    'gear_handle' / Enum(Int32ub, up=0, down=1),
    'master_avionics' / Enum(Int32ub, off=0, on=1),
    'comm_1_MHz' / Float64b,  # TODO: Frequencies are all screwed up. Garbage data
    'comm_2_MHz' / Float64b,
    'nav_1_MHz' / Float64b,
    'nav_2_MHz' / Float64b,
    'wind_speed_kt' / Float64b,
    'wind_dir_deg' / Float64b,
    'turbulence_norm' / Float64b,
    'temp_c' / Float64b,
    'press_inhg' / Float64b,
    'hground_m' / Float64b,  # ground elevation
    'magvar_deg' / Float64b,  # local magnetic variation
    'icing' / Int32ub,
    'speedup' / Int32ub,  # integer speedup multiplier
    'freeze'
    / BitStruct(  # Default is big-endian
        other=BitsInteger((Int32ub.sizeof() * 8) - 3),  # Rest of uint32 minus the 3 flags
        fuel=Bit,
        position=Bit,
        master=Bit,
    ),
    '_reserved' / Bytes(Int32ub.length * RESERVED_SPACE),
)
