#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2020 fchart authors
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

def angular_distance(position1, position2):
    """
    Compute angular distance between start and end point.
    These points are tuples (ra,dec) in radians. Result is also in radians.
    """

    (start_ra, start_dec) = position1
    (end_ra, end_dec)     = position2
    a = start_ra-end_ra
    arg = np.sin(start_dec)*np.sin(end_dec) + np.cos(start_dec)*np.cos(end_dec)*np.cos(a)
    return np.arccos(arg)



def justify_angle(angle, lower_bound, upper_bound):
    """
    Justifies angle to interval lower_bound <= angle <
    upper_bound. The routine assumes periodic boundary conditions.

    Usage:
       justify_angle(371, 0, 360)      => 11
       justify_angle(-0.5*pi, 0, 2*pi) => 1.5*pi
    """

    step = upper_bound - lower_bound

    k = int((angle-lower_bound)/step)
    if angle < lower_bound:
        angle += (k+1)*step
    else:
        if angle >= upper_bound:
            angle -= k*step
    return angle


def rad2hms_t(angle):
    sign = 1
    if angle < 0:
        sign = -1
    p2 = 2.0*np.pi
    h  = (sign*angle/p2)*24.0
    h_int = int(h + 1e-8)
    m  = (h - h_int)*60.0
    m_int = int(m + 1e-8)
    s  = (m - m_int)*60.0

    if s <= 1e-6:
        s = 0
        #if fabs(s*100 - int(s*100)) < 1e-4:
    s = int(100*s + 0.5)/100.0
    return(h_int, m_int, s, sign)


def rad2dms_t(angle):
    sign = 1
    if angle < 0:
        sign = -1
    p2 = 2.0*np.pi
    d  = (sign*angle/p2)*360.0
    d_int = int(d + 1e-8)
    m  = (d - d_int)*60.0
    m_int = int(m + 1e-8)
    s  = (m - m_int)*60.0

    if s <= 1e-6:
        s = 0
    s = int(100*s + 0.5)/100.0
    return (d_int, m_int, s, sign)


def rad2hms(angle):
    """
    Converts an angle in radians to a string in a 24-hour, hour,
    minute, seconds format. 0 <= angle < 2np.pi.

    Usage:
        rad2hms(0.345) => '1h19m4.09054368322'
    """
    h_int,m_int,s,sign = rad2hms_t(angle)

    return str(sign*h_int) + 'h' + str(m_int) + 'm' + str(s)


def rad2dms(angle):
    """
    Converts an angle in radians to a string in a 360 degree, degree,
    minute, seconds format. 0 <= angle < 2np.pi.

    Usage:
        rad2dms(0.345) => '19d46m1.35815524824'
    """
    d_int, m_int,s,sign = rad2dms_t(angle)
    return str(sign*d_int)+'d'+str(m_int)+'m'+str(s)


def dms2rad(d,m=0,s=0, sign=1):
    """
    Converts an angle in degrees(d), minutes(m) and seconds(s) into
    radians. The parameters d, m and s MUST be positive. If a negative
    angle needs to be converted, then sign must be set to -1.
    """
    return sign*(d + m/60.0 + s/3600.0)*np.pi/180.0


def hms2rad(h,m=0,s=0, sign=1):
    """
    Converts an angle in hours(h), minutes(m) and seconds(s) into
    radians. If a negative angle needs to be converted, then sign must
    be set to -1.

    """
    return (sign*(h + m/60.0 + s/3600.0)*np.pi/12.0)


def lm_to_radec(lm, fieldcentre):
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


def radec_to_lm(radec, fieldcentre):
    """
    SIN projection. Converts radec (alpha, delta) with respect to
    a fieldcentre (alpha0, delta0) to direction cosines (l, m). All
    units are in radians. radec is a tuple (alpha, delta), Fieldcentre
    is a tuple (alpha0, delta0). The routine returns a tuple (l,m).
    The formulae are taken from Greisen 1983: AIPS Memo 27,
    'Non-linear Coordinate Systems in AIPS'
    """
    (alpha, delta) = radec
    (alpha0, delta0) = fieldcentre
    dalpha = alpha - alpha0
    l = np.cos(delta)*np.sin(dalpha)
    m = np.sin(delta)*np.cos(delta0) - np.cos(delta)*np.sin(delta0)*np.cos(dalpha)
    return (l,m)


def direction_ddec(radec, fieldcentre):
    """
    Gives the angle between true north and map north on any
    location in a SIN projection. Positive means that the true north
    is pointing east of the map north.

    ra, dec , ra0 and dec0 are in radians
    """

    (ra0, dec0) = fieldcentre
    (ra, dec)   = radec

    angle = np.arctan2(-np.sin(dec)*np.sin(ra -ra0), np.cos(dec)*np.cos(dec0) + np.sin(dec)*np.sin(dec0)*np.cos(ra-ra0))
    return angle


__all__ = ['angular_distance', 'justify_angle', 'rad2hms_t','rad2dms_t',
           'rad2dms', 'rad2hms',
           'hms2rad', 'dms2rad', 'lm_to_radec', 'radec_to_lm',
           'direction_ddec']
