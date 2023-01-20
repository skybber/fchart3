#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2023 fchart authors
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


def np_lm_to_radec(lm, fieldcentre):
    """
    Inverse of SIN projection. Converts lm (l, m) with respect to
    a fieldcentre (alpha0, delta0) to equatorial coordinates (alpha,
    delta). All units are in radians. lm is a tuple:
    (l,m). Fieldcentre is a tuple (alpha0, delta0). The routine
    returns a tuple (alpha, delta). The formulae are taken from
    Greisen 1983: AIPS Memo 27, 'Non-linear Coordinate Systems in
    AIPS'
    """
    (l,m) = lm
    (alpha0, delta0) = fieldcentre
    alpha = alpha0 + np.arctan2(l,(np.cos(delta0)*np.sqrt(1-l*l -m*m) - m*np.sin(delta0)))
    delta = np.asin((m*np.cos(delta0) + np.sin(delta0)*np.sqrt(1-l*l - m*m)))
    return (alpha, delta)


def np_radec_to_lm(radec, fieldcentre):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a fieldcentre (alpha0, delta0) to direction cosines (l, m). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcentre
    is a tuple (alpha0, delta0). The routine returns a tuple (l,m).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra, dec) = radec
    (ra0, dec0) = fieldcentre
    delta_ra = ra - ra0
    l = np.cos(dec)*np.sin(delta_ra)
    m = np.sin(dec)*np.cos(dec0) - np.cos(dec)*np.cos(delta_ra)*np.sin(dec0)
    return (l,m)


def np_radec_to_lmz(ra, dec, fieldcentre):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a fieldcentre (alpha0, delta0) to direction cosines (l, m, z). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcentre
    is a tuple (alpha0, delta0). The routine returns a tuple (l,m,z).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra0, dec0) = fieldcentre
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


def np_radec_to_xyz(ra, dec, fieldcentre, scale, fc_sincos_dec):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a fieldcentre (alpha0, delta0) to coordinates (x, y, z). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcentre
    is a tuple (alpha0, delta0). The routine returns a tuple (x,y,z).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra0, dec0) = fieldcentre
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


def np_radec_to_xy(ra, dec, fieldcentre, scale, fc_sincos_dec):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a fieldcentre (alpha0, delta0) to coordinates (x, y, z). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcentre
    is a tuple (alpha0, delta0). The routine returns a tuple (x,y,z).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (ra0, dec0) = fieldcentre
    delta_ra = ra - ra0

    sin_dec = np.sin(dec)
    cos_dec = np.cos(dec)
    cos_dec0 = fc_sincos_dec[1] # np.cos(dec0)
    sin_dec0 = fc_sincos_dec[0] # np.sin(dec0)
    cos_delta_ra = np.cos(delta_ra)

    x = -cos_dec*np.sin(delta_ra)*scale
    y = (sin_dec*cos_dec0 - cos_dec*cos_delta_ra*sin_dec0)*scale
    return (x,y)


def np_direction_ddec(radec, fieldcentre, fc_sincos_dec):
    """
    Gives the angle between true north and map north on any
    location in a SIN projection. Positive means that the true north
    is pointing east of the map north.

    ra, dec , ra0 and dec0 are in radians
    """

    (ra0, dec0) = fieldcentre
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


__all__ = ['np_angular_distance',
           'np_lm_to_radec', 'np_radec_to_lm', 'np_radec_to_lmz',
           'np_radec_to_xyz', 'np_radec_to_xy', 'np_direction_ddec',
           'np_sphere_to_rect', 'np_rect_to_sphere'
           ]
