"""
FlightGear-specific utility functionality
"""
import math

from construct import Container


class FGConnectionError(Exception):
    """
    Error type generated when there is an error connecting to FlightGear
    """

    pass


class FGCommunicationError(Exception):
    """
    Error type generated when there is an error talking to FlightGear
    """

    pass


def offset_fg_radian(in_rad: float) -> float:
    """
    Even when echoing back literally what FG sends over the Net FDM connection,
    (i.e. UDP bytes in -> UDP bytes out) the latitude/longitude shown in FG
    appear to decrease. After plotting the offsets at a couple different lat/lons
    it appears to be a linear relationship and identical in anything that is
    represented in radians. The coefficient was chosen through trial-and-error.
    sphinx-no-autodoc

    :param in_rad: Input property, in radians
    :return: Offset that needs to be applied to the input, in radians
    """
    coeff = 1.09349403e-9
    return math.degrees(in_rad) * coeff


def fix_fg_radian_parsing(s: Container) -> Container:
    """
    Helper for all the radian values in the FDM
    sphinx-no-autodoc
    """
    s.lon_rad += offset_fg_radian(s.lon_rad)
    s.lat_rad += offset_fg_radian(s.lat_rad)
    s.phi_rad += offset_fg_radian(s.phi_rad)
    s.theta_rad += offset_fg_radian(s.theta_rad)
    s.psi_rad += offset_fg_radian(s.psi_rad)
    s.alpha_rad += offset_fg_radian(s.alpha_rad)
    s.beta_rad += offset_fg_radian(s.beta_rad)
    s.phidot_rad_per_s += offset_fg_radian(s.phidot_rad_per_s)
    s.thetadot_rad_per_s += offset_fg_radian(s.thetadot_rad_per_s)
    s.psidot_rad_per_s += offset_fg_radian(s.psidot_rad_per_s)
    return s
