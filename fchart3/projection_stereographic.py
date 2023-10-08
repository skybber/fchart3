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

import math
import numpy as np

from .projection import ProjectionInterface

class ProjectionStereographic(ProjectionInterface):
    def __init__(self):
        ProjectionInterface.__init__(self)
        self.sin_dec0 = None
        self.cos_dec0 = None

    def set_fieldcentre(self, fieldcentre):
        ProjectionInterface.set_fieldcentre(self, fieldcentre)
        self.sin_dec0 = math.sin(fieldcentre[1])
        self.cos_dec0 = math.cos(fieldcentre[1])

    def is_zoptim(self):
        return False

    def radec_to_xy(self, ra, dec):
        ra0, dec0 = self.fieldcentre
        delta_ra = ra - ra0

        sin_dec = math.sin(dec)
        cos_dec = math.cos(dec)
        cos_delta_ra = math.cos(delta_ra)

        sin_dec0, cos_dec0 = self.sin_dec0, self.cos_dec0

        k = 2 / (1 + sin_dec0 * sin_dec + cos_dec0 * cos_dec * cos_delta_ra)
        x = -k * cos_dec * math.sin(delta_ra) * self.scale_x
        y = k * (sin_dec*cos_dec0 - cos_dec*cos_delta_ra*sin_dec0) * self.scale_y
        return x, y

    def radec_to_xyz(self, ra, dec):
        ra0, dec0 = self.fieldcentre
        delta_ra = ra - ra0

        sin_dec = math.sin(dec)
        cos_dec = math.cos(dec)
        cos_delta_ra = math.cos(delta_ra)

        sin_dec0, cos_dec0 = self.sin_dec0, self.cos_dec0

        denom = 1 + sin_dec0 * sin_dec + cos_dec0 * cos_dec * cos_delta_ra

        if denom == 0:
            x, y, z = 0, 0, -1
        else:
            z = (cos_dec * cos_dec0 * math.cos(delta_ra) + sin_dec * sin_dec0) / denom
            x = -(2 * cos_dec * math.sin(delta_ra)) / denom * self.scale_x
            y = (2 * (cos_dec0 * sin_dec - sin_dec0 * cos_dec * cos_delta_ra)) / denom * self.scale_y

        return x, y, z

    def np_radec_to_xy(self, ra, dec):
        ra0, dec0 = self.fieldcentre
        delta_ra = ra - ra0

        sin_dec = np.sin(dec)
        cos_dec = np.cos(dec)
        cos_delta_ra = np.cos(delta_ra)

        sin_dec0, cos_dec0 = self.sin_dec0, self.cos_dec0

        k = 2 / (1 + sin_dec0 * sin_dec + cos_dec0 * cos_dec * cos_delta_ra)

        x = -k * cos_dec*np.sin(delta_ra)*self.scale_x
        y = k * (sin_dec*cos_dec0 - cos_dec*cos_delta_ra*sin_dec0)*self.scale_y
        return x, y

    def np_radec_to_xyz(self, ra, dec):
        ra0, dec0 = self.fieldcentre
        delta_ra = ra - ra0

        sin_dec = np.sin(dec)
        cos_dec = np.cos(dec)
        cos_delta_ra = np.cos(delta_ra)

        sin_dec0, cos_dec0 = self.sin_dec0, self.cos_dec0

        denom = 1 + sin_dec0 * sin_dec + cos_dec0 * cos_dec * cos_delta_ra

        z = (cos_dec * cos_dec0 * np.cos(delta_ra) + sin_dec * sin_dec0) / denom
        x = -(2 * cos_dec * np.sin(delta_ra)) / denom * self.scale_x
        y = (2 * (cos_dec0 * sin_dec - sin_dec0 * cos_dec * cos_delta_ra)) / denom * self.scale_y
        return x,y,z

    def direction_ddec(self, ra, dec):
        ra0, dec0 = self.fieldcentre
        sin_dec0, cos_dec0 = self.sin_dec0, self.cos_dec0
        angle = math.atan2(-math.sin(dec)*math.sin(ra-ra0), math.cos(dec)*cos_dec0 + math.sin(dec)*sin_dec0*math.cos(ra-ra0))
        return angle
