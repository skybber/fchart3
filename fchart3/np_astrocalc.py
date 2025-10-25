#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2024 fchart authors
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import numpy as np


def np_angular_distance(position1, position2):
    """
    Compute angular distance between start and end point.
    These points are tuples (ra,dec) in radians. Result is also in radians.
    """
    if position1[0] == position2[0] and position1[0] == position2[0]:
        return 0.0
    (start_ra, start_dec) = position1
    (end_ra, end_dec)     = position2
    a = start_ra-end_ra
    arg = np.sin(start_dec)*np.sin(end_dec) + np.cos(start_dec)*np.cos(end_dec)*np.cos(a)
    return np.arccos(arg)


def np_lm_to_radec(lm, field_center):
    """
    Inverse of SIN projection. Converts lm (l, m) with respect to
    a field_center (alpha0, delta0) to equatorial coordinates (alpha,
    delta). All units are in radians. lm is a tuple:
    (l,m). Fieldcenter is a tuple (alpha0, delta0). The routine
    returns a tuple (alpha, delta). The formulae are taken from
    Greisen 1983: AIPS Memo 27, 'Non-linear Coordinate Systems in
    AIPS'
    """
    (l,m) = lm
    (alpha0, delta0) = field_center
    alpha = alpha0 + np.arctan2(l,(np.cos(delta0)*np.sqrt(1-l*l -m*m) - m*np.sin(delta0)))
    delta = np.asin((m*np.cos(delta0) + np.sin(delta0)*np.sqrt(1-l*l - m*m)))
    return (alpha, delta)


def np_radec_to_lm(radec, field_center):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a field_center (alpha0, delta0) to direction cosines (l, m). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcenter
    is a tuple (alpha0, delta0). The routine returns a tuple (l,m).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra, dec) = radec
    (ra0, dec0) = field_center
    delta_ra = ra - ra0
    l = np.cos(dec)*np.sin(delta_ra)
    m = np.sin(dec)*np.cos(dec0) - np.cos(dec)*np.cos(delta_ra)*np.sin(dec0)
    return (l,m)


def np_radec_to_lmz(ra, dec, field_center):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a field_center (alpha0, delta0) to direction cosines (l, m, z). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcenter
    is a tuple (alpha0, delta0). The routine returns a tuple (l,m,z).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra0, dec0) = field_center
    delta_ra = ra - ra0

    sin_dec = np.sin(dec)
    cos_dec = np.cos(dec)
    cos_dec0 = np.cos(dec0)
    sin_dec0 = np.sin(dec0)
    cos_delta_ra = np.cos(delta_ra)

    z = sin_dec*sin_dec0 + cos_dec*cos_dec0*cos_delta_ra
    l = np.where(z>0,cos_dec*np.sin(delta_ra),0)
    m = np.where(z>0,sin_dec*cos_dec0 - cos_dec*cos_delta_ra*sin_dec0,0)
    return (l,m,z)


def np_radec_to_xyz(ra, dec, field_center, scale, fc_sincos_dec):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a field_center (alpha0, delta0) to coordinates (x, y, z). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcenter
    is a tuple (alpha0, delta0). The routine returns a tuple (x,y,z).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra0, dec0) = field_center
    delta_ra = ra - ra0

    sin_dec = np.sin(dec)
    cos_dec = np.cos(dec)
    cos_dec0 = fc_sincos_dec[1] # np.cos(dec0)
    sin_dec0 = fc_sincos_dec[0] # np.sin(dec0)
    cos_delta_ra = np.cos(delta_ra)

    z = sin_dec*sin_dec0 + cos_dec*cos_dec0*cos_delta_ra
    x = np.where(z>0,-cos_dec*np.sin(delta_ra)*scale,0)
    y = np.where(z>0,(sin_dec*cos_dec0 - cos_dec*cos_delta_ra*sin_dec0)*scale,0)
    return (x,y,z)


def np_radec_to_xy(ra, dec, field_center, scale, fc_sincos_dec):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a field_center (alpha0, delta0) to coordinates (x, y, z). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcenter
    is a tuple (alpha0, delta0). The routine returns a tuple (x,y,z).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra0, dec0) = field_center
    delta_ra = ra - ra0

    sin_dec = np.sin(dec)
    cos_dec = np.cos(dec)
    cos_dec0 = fc_sincos_dec[1] # np.cos(dec0)
    sin_dec0 = fc_sincos_dec[0] # np.sin(dec0)
    cos_delta_ra = np.cos(delta_ra)

    x = -cos_dec*np.sin(delta_ra)*scale
    y = (sin_dec*cos_dec0 - cos_dec*cos_delta_ra*sin_dec0)*scale
    return (x,y)


def np_direction_ddec(radec, field_center, fc_sincos_dec):
    """
    Gives the angle between true north and map north on any
    location in a SIN projection. Positive means that the true north
    is pointing east of the map north.

    ra, dec , ra0 and dec0 are in radians
    """

    (ra0, dec0) = field_center
    (ra, dec)   = radec

    cos_dec0 = fc_sincos_dec[1] # np.cos(dec0)
    sin_dec0 = fc_sincos_dec[0] # np.sin(dec0)

    angle = np.arctan2(-np.sin(dec)*np.sin(ra-ra0), np.cos(dec)*cos_dec0 + np.sin(dec)*sin_dec0*np.cos(ra-ra0))
    return angle


def np_sphere_to_rect(ra, dec):
    """
    Convert from spherical coordinates to Rectangular direction.
    """
    cos_dec = np.cos(dec);
    return (np.cos(ra) * cos_dec, np.sin(ra) * cos_dec, np.sin(dec));


def np_rect_to_sphere(x1, x2, x3):
    """
    Convert from Rectangular direction to spherical coordinate components.
    """
    r = np.sqrt(x1*x1 + x2*x2 + x3*x3)
    ra = np.arctan2(x2, x1);
    dec = np.arcsin(x3/r);
    return (ra, dec)


def np_radec_to_horizontal(lst, sincos_lat, ra, dec):
    """
    Convert Equatorial coordinates (ra, dec) to Horizontal coordinates (Alt, Az).
    :param lst: Local Sidereal Time in radians (scalar or array)
    :param sincos_lat: precomputed array of sin+cos of observer's latitude [sin_lat, cos_lat]
    :param ra: Right Ascension in radians (array)
    :param dec: Declination in radians (array)
    :return: (Alt, Az) in radians (arrays)
    """
    hour_angle = (lst - ra) % (2 * np.pi)

    sin_lat = sincos_lat[0]
    cos_lat = sincos_lat[1]

    sin_dec = np.sin(dec)
    cos_dec = np.cos(dec)
    sin_ha = np.sin(hour_angle)
    cos_ha = np.cos(hour_angle)

    sin_alt = sin_dec * sin_lat + cos_dec * cos_lat * cos_ha
    alt = np.arcsin(sin_alt)

    cos_alt = np.sqrt(np.maximum(0.0, 1.0 - sin_alt ** 2))
    cos_alt = np.where(np.abs(cos_alt) < 1e-15, np.cos(alt), cos_alt)

    arg = (sin_dec - sin_lat * sin_alt) / (cos_lat * cos_alt)

    az = np.where(arg <= -1.0, np.pi, np.where(arg >= 1.0, 0.0, np.arccos(arg)))

    az = np.where((sin_ha > 0.0) & (np.abs(az) > 1e-15), 2.0 * np.pi - az, az)

    az = (2 * np.pi - az) % (2 * np.pi)

    return alt, az


def np_build_rotation_matrix_equatorial(phi0, theta0):
    """
    Builds a rotation matrix based on equatorial spherical coordinates (phi0, theta0).
    The matrix is constructed from the given angles, representing a rotation that aligns
    the z-axis with a unit vector defined by the spherical angles. The function ensures that
    an appropriate orthonormal basis is created with well-defined x, y, and z axes.

    :param phi0: Longitude angle in radians. Specifies the azimuthal position.
    :type phi0: float
    :param theta0: Latitude angle in radians. Specifies the altitude position.
    :type theta0: float
    :return: A 3x3 rotation matrix where each row represents the orthonormal basis vectors.
    :rtype: numpy.ndarray
    """
    cos_t0 = np.cos(theta0)
    sin_t0 = np.sin(theta0)
    cos_p0 = np.cos(phi0)
    sin_p0 = np.sin(phi0)

    center = np.array([
        cos_t0 * cos_p0,
        cos_t0 * sin_p0,
        sin_t0
    ], dtype=float)

    x_temp = np.array([0, 0, 1], dtype=float)

    ex = np.cross(x_temp, center)
    ex /= np.linalg.norm(ex)

    ey = np.cross(center, ex)

    R = np.vstack([ex, ey, center])
    return R


def np_build_rotation_matrix_obs(lst, lat):
    """
    Build a 3x3 rotation matrix that transforms a 3D vector in the
    (RA,Dec) equatorial frame into the local horizontal frame,
    given the observer's local sidereal time (lst) and latitude.

    Convention (for this example):
      - +z = up (zenith),
      - +x = north,
      - +y = east.  (Az increases toward the east from north.)

    Steps (applied right-to-left to a column vector v):
      1) Rz(LST): rotate around z-axis by +LST,
      2) Ry(lat - π/2): rotate around y-axis by (lat - 90 deg).

    So the final transform is  R_obs = Ry(lat - π/2) @ Rz(LST).
    """
    st_corr = -lst + np.pi
    cos_l = np.cos(st_corr)
    sin_l = np.sin(st_corr)
    Rz = np.array([
        [cos_l, -sin_l, 0],
        [sin_l, cos_l, 0],
        [0, 0, 1]
    ])

    alpha = (np.pi / 2) - lat
    cos_a = np.cos(alpha)
    sin_a = np.sin(alpha)
    Ry = np.array([
        [cos_a, 0, sin_a],
        [0, 1, 0],
        [-sin_a, 0, cos_a]
    ])

    return Ry @ Rz

__all__ = ['np_angular_distance',
           'np_lm_to_radec', 'np_radec_to_lm', 'np_radec_to_lmz',
           'np_radec_to_xyz', 'np_radec_to_xy', 'np_direction_ddec',
           'np_sphere_to_rect', 'np_rect_to_sphere',
           'np_radec_to_horizontal', 'np_build_rotation_matrix_equatorial'
           ]
