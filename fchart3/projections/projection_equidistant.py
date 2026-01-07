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
from ..np_astrocalc import np_build_rotation_matrix_equatorial


class ProjectionFisheyeEquidistant(ProjectionInterface):
    """
    Fisheye / Azimuthal Equidistant projection:
      - r = c, where c is the central angle from the field center (in radians)
      - projects the full sphere (no horizon clipping)
      - good for very wide FoV, all-sky charts, etc.
    """
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
        # Not a "simple" z-based visibility optimization like orthographic.
        return False

    def celestial_to_xy(self, phi, theta):
        """
        Scalar version based on spherical trig:
          cos(c) = sinθ0 sinθ + cosθ0 cosθ cosΔφ
          x = - r * cosθ sinΔφ / sin(c)
          y =   r * (sinθ cosθ0 - cosθ cosΔφ sinθ0) / sin(c)
        with r = c
        """
        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        cos_delta_phi = math.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0

        cos_c = sin_theta0 * sin_theta + cos_theta0 * cos_theta * cos_delta_phi
        # Clamp for numerical stability.
        cos_c = max(-1.0, min(1.0, cos_c))

        # Use atan2 for stable angle:
        # sin(c) can be computed from the "azimuthal" numerator length as well,
        # but the generic relation is stable enough:
        c = math.acos(cos_c)
        # sin(c) (avoid catastrophic cancellation near 0 using sqrt(max(0,...)))
        sin_c = math.sqrt(max(0.0, 1.0 - cos_c * cos_c))

        if sin_c < 1e-12:
            # At the center of the projection.
            return 0.0, 0.0

        r = c  # equidistant fisheye

        x = -r * (cos_theta * math.sin(delta_phi)) / sin_c * self.scale_x
        y =  r * (sin_theta * cos_theta0 - cos_theta * cos_delta_phi * sin_theta0) / sin_c * self.scale_y
        return x, y

    def celestial_to_xyz(self, phi, theta):
        """
        Returns (x, y, z) where:
          - (x, y) are the fisheye-projected coords (scaled)
          - z is cos(c) (useful diagnostic: +1 center, -1 opposite side)
        """
        x, y = self.celestial_to_xy(phi, theta)

        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        cos_delta_phi = math.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0
        z = sin_theta0 * sin_theta + cos_theta0 * cos_theta * cos_delta_phi  # cos(c)
        return x, y, z

    def np_celestial_to_xy(self, phi, theta):
        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        cos_delta_phi = np.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0

        cos_c = sin_theta0 * sin_theta + cos_theta0 * cos_theta * cos_delta_phi
        cos_c = np.clip(cos_c, -1.0, 1.0)

        c = np.arccos(cos_c)
        sin_c = np.sqrt(np.maximum(0.0, 1.0 - cos_c * cos_c))

        eps = 1e-12
        sin_c_safe = np.where(sin_c < eps, 1.0, sin_c)  # avoid division by 0

        r = c  # equidistant fisheye

        x = -r * (cos_theta * np.sin(delta_phi)) / sin_c_safe * self.scale_x
        y =  r * (sin_theta * cos_theta0 - cos_theta * cos_delta_phi * sin_theta0) / sin_c_safe * self.scale_y

        # Exact center -> (0,0)
        x = np.where(sin_c < eps, 0.0, x)
        y = np.where(sin_c < eps, 0.0, y)
        return x, y

    def np_celestial_to_xyz(self, phi, theta):
        x, y = self.np_celestial_to_xy(phi, theta)

        phi0, theta0 = self.field_center
        delta_phi = phi - phi0

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        cos_delta_phi = np.cos(delta_phi)

        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0
        z = sin_theta0 * sin_theta + cos_theta0 * cos_theta * cos_delta_phi  # cos(c)
        return x, y, z

    def direction_dtheta(self, phi, theta):
        # Same helper as others: direction of +theta in projected plane.
        phi0, theta0 = self.field_center
        sin_theta0, cos_theta0 = self.sin_theta0, self.cos_theta0
        angle = math.atan2(
            -math.sin(theta) * math.sin(phi - phi0),
            math.cos(theta) * cos_theta0 + math.sin(theta) * sin_theta0 * math.cos(phi - phi0)
        )
        return angle

    def update_matrix_transform(self):
        phi0, theta0 = self.field_center
        if phi0 is None or theta0 is None:
            self._R = None
            return

        r_equat = np_build_rotation_matrix_equatorial(phi0, theta0)
        # Keep the same convention as ProjectionOrthographic (observer rotation applied on the left)
        self._R = (self._R_obs @ r_equat) if self._R_obs is not None else r_equat

    def np_unit3d_to_xy(self, points_3d):
        """
        Fast path: rotate 3D unit vectors so that field center becomes +Z,
        then apply fisheye equidistant:
          c = atan2(sin_c, z)
          r = c
          x = r * (x / sin_c)
          y = r * (y / sin_c)
        Uses the same sign convention as Orthographic for x/y axes.
        """
        if self._R is None:
            self.update_matrix_transform()

        rotated = points_3d @ self._R.T

        # Match Orthographic sign convention:
        xdir = -rotated[:, 0]
        ydir =  rotated[:, 1]
        z    =  rotated[:, 2]

        # sin(c) is the radial length in the tangent plane before projection.
        sin_c = np.sqrt(xdir * xdir + ydir * ydir)

        # Stable central angle:
        c = np.arctan2(sin_c, z)  # in [0..pi]

        eps = 1e-12
        sin_c_safe = np.where(sin_c < eps, 1.0, sin_c)

        r = c  # equidistant fisheye

        x2d = (r * (xdir / sin_c_safe)) * self.scale_x
        y2d = (r * (ydir / sin_c_safe)) * self.scale_y

        # Exact center -> (0,0)
        x2d = np.where(sin_c < eps, 0.0, x2d)
        y2d = np.where(sin_c < eps, 0.0, y2d)

        return x2d, y2d, z
