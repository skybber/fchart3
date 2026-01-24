#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2026 fchart3 authors
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

import math
import numpy as np

from .projection import ProjectionInterface
from ..astro.np_astrocalc import np_build_rotation_matrix_equatorial


class ProjectionOrthographic(ProjectionInterface):
    def __init__(self):
        super().__init__()
        self.sin_theta0 = None
        self.cos_theta0 = None
        self._R = None
        self._R_obs = None

    def set_field_center(self, field_center):
        super().set_field_center(field_center)
        self.sin_theta0 = math.sin(field_center[1])
        self.cos_theta0 = math.cos(field_center[1])
        self.update_matrix_transform()

    def set_r_obs(self, r_obs):
        self._R_obs = r_obs
        self.update_matrix_transform()

    def set_scale(self, scale_x, scale_y):
        super().set_scale(scale_x, scale_y)
        self.update_matrix_transform()

    def is_zoptim(self):
        return True

    def celestial_to_xy(self, phi, theta):
        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        cos_delta_phi = math.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0

        x = -cos_theta*math.sin(delta_phi)*self.scale_x
        y = (sin_theta*cos_theta0 - cos_theta*cos_delta_phi*sin_theta0)*self.scale_y
        return x, y

    def celestial_to_xyz(self, phi, theta):
        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        cos_delta_phi = math.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0

        z = sin_theta*sin_theta0 + cos_theta*cos_theta0*cos_delta_phi
        x = -cos_theta*math.sin(delta_phi)*self.scale_x if z>0 else 0
        y = (sin_theta*cos_theta0 - cos_theta*cos_delta_phi*sin_theta0)*self.scale_y if z>0 else 0
        return x, y, z

    def np_celestial_to_xy(self, phi, theta):
        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        cos_delta_phi = np.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0

        x = -cos_theta*np.sin(delta_phi)*self.scale_x
        y = (sin_theta*cos_theta0 - cos_theta*cos_delta_phi*sin_theta0)*self.scale_y
        return x, y

    def np_celestial_to_xyz(self, phi, theta):
        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        cos_delta_phi = np.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0

        z = sin_theta*sin_theta0 + cos_theta*cos_theta0*cos_delta_phi
        x = np.where(z>0, -cos_theta*np.sin(delta_phi)*self.scale_x, 0)
        y = np.where(z>0, (sin_theta*cos_theta0 - cos_theta*cos_delta_phi*sin_theta0)*self.scale_y, 0)
        return x,y,z

    def direction_dtheta(self, phi, theta):
        phi0, theta0 = self.field_center
        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0
        angle = math.atan2(-math.sin(theta) * math.sin(phi - phi0), math.cos(theta) * cos_theta0 + math.sin(theta) * sin_theta0 * math.cos(phi - phi0))
        return angle

    def update_matrix_transform(self):
        phi0, theta0 = self.field_center
        if phi0 is None or theta0 is None:
            self._R = None
            return

        r_equat = np_build_rotation_matrix_equatorial(phi0, theta0)
        self._R = self._R_obs @ r_equat if self._R_obs is not None else r_equat

    def np_unit3d_to_xy(self, points_3d):
        if self._R is None:
            self.update_matrix_transform()

        rotated = points_3d @ self._R.T

        xprime = -rotated[:, 0]
        yprime = rotated[:, 1]
        zprime = rotated[:, 2]

        x2d = xprime * self.scale_x
        y2d = yprime * self.scale_y

        return x2d, y2d, zprime
