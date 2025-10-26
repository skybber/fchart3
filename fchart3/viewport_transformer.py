#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2025 fchart3 authors
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

from .astrocalc import radec_to_horizontal, horizontal_to_radec
from .np_astrocalc import np_radec_to_horizontal, np_build_rotation_matrix_obs

import math


class ViewportTransformer:
    def __init__(self, projection):
        self.projection = projection

        self.center_phi = None
        self.center_theta = None

        self.obs_lst = None
        self.obs_lat = None
        self.obs_sincos_lat = None
        self.grid_lst = None
        self.grid_lat = None
        self.grid_sincos_lat = None

    def set_celestial_center(self, phi, theta):
        """
        Set the center of the projection, typically in equatorial coordinates (RA, Dec).
        """
        self.center_phi = phi
        self.center_theta = theta
        self.projection.set_field_center((phi, theta))

    def get_equatorial_center(self):
        return horizontal_to_radec(self.obs_lst, self.obs_sincos_lat, self.center_theta, self.center_phi)

    def set_observer(self, lst, lat):
        """
        Sets the observer's location and time parameters (lst, lat)
        """
        if lst is not None and lat is not None:
            self.obs_lst = lst
            self.obs_lat = lat
            self.obs_sincos_lat = (math.sin(lat), math.cos(lat))
            r_obs = np_build_rotation_matrix_obs(lst, lat)
            self.projection.set_r_obs(r_obs)
        else:
            self.obs_lst = None
            self.obs_sincos_lat = None
            self.projection.set_r_obs(None)

    def set_grid_observer(self, lst, lat):
        """
        Sets the observer's location and time parameters (lst, lat) for grid transformation
        """
        if lst is not None and lat is not None:
            self.grid_lst = lst
            self.grid_lat = lat
            self.grid_sincos_lat = (math.sin(lat), math.cos(lat))
        else:
            self.grid_lst = None
            self.grid_lat = None
            self.grid_sincos_lat = None

    def set_scale(self, scale_x, scale_y):
        """
        Set the scaling factors for the projection along the x and y axes.
        """
        self.projection.set_scale(scale_x, scale_y)

    def is_zoptim(self):
        return self.projection.is_zoptim()

    def equatorial_to_xy(self, phi, theta):
        """
        Convert equatorial coordinates to 2D Cartesian coordinates (x, y) for the current projection.

        Returns:
        tuple: (x, y) coordinates in the projected 2D plane.
        """
        if self.obs_lst is not None:
            theta, phi = radec_to_horizontal(self.obs_lst, self.obs_sincos_lat, phi, theta)
        return self.projection.celestial_to_xy(phi, theta)

    def equatorial_to_xyz(self, phi, theta):
        """
        Convert equatorial coordinates to 3D Cartesian coordinates (x, y, z).

        Returns:
        tuple: (x, y, z) coordinates in 3D space.
        """
        if self.obs_lst is not None:
            theta, phi = radec_to_horizontal(self.obs_lst, self.obs_sincos_lat, phi, theta)
        return self.projection.celestial_to_xyz(phi, theta)

    def np_equatorial_to_xy(self, phi, theta):
        """
        Numpy version of equatorial coordinates conversion to 2D Cartesian coordinates (x, y).

        Returns:
        tuple: (x, y) coordinates in the projected 2D plane
        """
        if self.obs_lst is not None:
            theta, phi = np_radec_to_horizontal(self.obs_lst, self.obs_sincos_lat, phi, theta)
        return self.projection.np_celestial_to_xy(phi, theta)

    def np_equatorial_to_xyz(self, phi, theta):
        """
        Numpy version of equatorial coordinates conversion to 3D Cartesian coordinates (x, y, z).

        Returns:
        tuple: (x, y, z) coordinates in 3D space
        """
        if self.obs_lst is not None:
            theta, phi = np_radec_to_horizontal(self.obs_lst, self.obs_sincos_lat, phi, theta)
        return self.projection.np_celestial_to_xyz(phi, theta)

    def direction_dtheta(self, phi, theta):
        """
        Determine the direction of the change in theta for a equatorial object at a given phi, theta

        Returns:
        float: The direction or angle of the declination change.
        """
        if self.obs_lst is not None:
            theta, phi = np_radec_to_horizontal(self.obs_lst, self.obs_sincos_lat, phi, theta)
        return self.projection.direction_dtheta(phi, theta)

    def horizontal_to_xyz(self, az, alt):
        """
        Convert horizontal coordinates to 3D Cartesian coordinates (x, y, z).

        Returns:
        tuple: (x, y, z) coordinates in 3D space.
        """
        return self.projection.celestial_to_xyz(az, alt)

    def np_unit3d_to_xy(self, points_3d):
        return self.projection.np_unit3d_to_xy(points_3d)

    def grid_equatorial_to_horizontal(self, ra, dec):
        """
        Convert equatorial coordinates (RA, Dec) to horizontal coordinates (az, alt)
        using the dedicated grid observer.
        """
        alt, az = radec_to_horizontal(self.grid_lst, self.grid_sincos_lat, ra, dec)
        return az, alt

    def grid_horizontal_to_equatorial(self, az, alt):
        """
        Convert horizontal coordinates (az, alt) to equatorial coordinates (RA, Dec)
        using the dedicated grid observer.
        """
        ra, dec = horizontal_to_radec(self.grid_lst, self.grid_sincos_lat, alt, az)
        return ra, dec

