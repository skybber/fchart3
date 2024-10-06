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

from enum import Enum
import math


class ProjectionType(Enum):
    ORTHOGRAPHIC = 1
    STEREOGRAPHIC = 2


class ProjectionInterface:
    def __init__(self):
        self.fieldcentre = None
        self.scale_x = None
        self.scale_y = None

    def set_fieldcentre(self, fieldcentre):
        """
        Set the center of the projection, typically in celestial coordinates (RA, Dec).
        """
        self.fieldcentre = fieldcentre

    def set_scale(self, scale_x, scale_y):
        """
        Set the scaling factors for the projection along the x and y axes.
        """
        self.scale_x = scale_x
        self.scale_y = scale_y

    def is_zoptim(self):
        pass

    def radec_to_xy(self, ra, dec):
        """
        Convert right ascension (RA) and declination (Dec) to 2D Cartesian coordinates (x, y) for the current projection.

        Returns:
        tuple: (x, y) coordinates in the projected 2D plane.
        """
        pass

    def radec_to_xyz(self, ra, dec):
        """
        Convert right ascension (RA) and declination (Dec) to 3D Cartesian coordinates (x, y, z).

        Returns:
        tuple: (x, y, z) coordinates in 3D space.
        """
        pass

    def np_radec_to_xy(self, ra, dec):
        """
        Convert right ascension (RA) and declination (Dec) relative to the north pole to 2D Cartesian coordinates (x, y).
        This is often used in polar or other specialized projections.

        Returns:
        tuple: (x, y) coordinates in the projected 2D plane relative to the north pole.
        """
        pass

    def np_radec_to_xyz(self, ra, dec):
        """
        Convert right ascension (RA) and declination (Dec) relative to the north pole to 3D Cartesian coordinates (x, y, z).
        Useful for polar projections or north pole-centric coordinate systems.

        Returns:
        tuple: (x, y, z) coordinates in 3D space relative to the north pole.
        """
        pass

    def direction_ddec(self, ra, dec):
        """
        Determine the direction of the change in declination (dDec) for a celestial object at a given right ascension (RA) and declination (Dec).
        This is useful for determining gradients or the direction of motion in sky charts.

        Returns:
        float: The direction or angle of the declination change.
        """
        pass

    def pos_angle(self, ra1, dec1, ra2, dec2):
        """
        Calculate the position angle between two celestial points (ra1, dec1) and (ra2, dec2),
        using their projected Cartesian coordinates.

        Returns:
        float
            Position angle in radians, measured counterclockwise from the north (positive y-axis).
        """
        dr = ra2 - ra1
        pos_angle = math.atan2(math.sin(dr), math.cos(dec1) * math.tan(dec2) - math.sin(dec1) * math.cos(dr))
        pos_angle += math.pi

        x, y = self.radec_to_xy(ra1, dec1)

        x_north, y_north = self.radec_to_xy(0, math.pi / 2)  # Dec = +90° (π/2 radians)

        dx = x_north - x
        dy = y_north - y

        angle_to_north = math.atan2(dx, dy)

        return pos_angle + angle_to_north - math.pi / 2
