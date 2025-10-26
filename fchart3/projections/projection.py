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

from enum import Enum


class ProjectionType(Enum):
    ORTHOGRAPHIC = 1
    STEREOGRAPHIC = 2


class ProjectionInterface:
    def __init__(self):
        self.field_center = None
        self.scale_x = None
        self.scale_y = None

    def set_field_center(self, field_center):
        """
        Set the center of the projection, typically in celestial coordinates (RA, Dec).
        """
        self.field_center = field_center

    def set_r_obs(self, r_obs):
        """
        Sets rotation matrix of observer
        :param r_obs: observer's rotation matrix
        """
        pass

    def set_scale(self, scale_x, scale_y):
        """
        Set the scaling factors for the projection along the x and y axes.
        """
        self.scale_x = scale_x
        self.scale_y = scale_y

    def is_zoptim(self):
        pass

    def celestial_to_xy(self, phi, theta):
        """
        Convert celestial coordinates to 2D Cartesian coordinates (x, y) for the current projection.

        Returns:
        tuple: (x, y) coordinates in the projected 2D plane.
        """
        pass

    def celestial_to_xyz(self, phi, theta):
        """
        Convert celestial coordinates to 3D Cartesian coordinates (x, y, z).

        Returns:
        tuple: (x, y, z) coordinates in 3D space.
        """
        pass

    def np_celestial_to_xy(self, phi, theta):
        """
        Numpy version of celestial coordinates conversion to 2D Cartesian coordinates (x, y).

        Returns:
        tuple: (x, y) coordinates in the projected 2D plane
        """
        pass

    def np_celestial_to_xyz(self, phi, theta):
        """
        Numpy version of celestial coordinates conversion to 3D Cartesian coordinates (x, y, z).

        Returns:
        tuple: (x, y, z) coordinates in 3D space
        """
        pass

    def direction_dtheta(self, phi, theta):
        """
        Determine the direction of the change in theta for a celestial object at a given phi, theta

        Returns:
        float: The direction or angle of the declination change.
        """
        pass

    def np_unit3d_to_xy_matrix(self, points_3d):
        """
        Converts a 3D unit vector to its corresponding 2D projection in the XY-plane.
        :rtype: numpy.ndarray
        """
        pass

    def np_unit3d_to_xy(self, points_3d):
        """
        Convert 3D points in unit space to 2D points on the XY plane.

        This method processes an array of 3D points and transforms them
        to 2D points lying on the XY plane. It can be used in scenarios
        where data is represented in three-dimensional space and a projection
        to two dimensions is required for further processing or visualization.

        :param points_3d: A numpy array containing the 3D coordinates
            to be transformed. Each row represents a 3D point, typically
            with shape (n, 3).
        :return: A numpy array containing the 2D projected points limited
            to the XY plane, typically with shape (n, 2).
        """
        pass
