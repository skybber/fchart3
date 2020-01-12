#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-202 fchart authors0
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
import os
import sys
from fchart3.astrocalc import *

class IndexRecord:
    def __init__(self, first_record, num_records, ra_min, dec_min, ra_max, dec_max):
        """
        Angles are in radians
        """
        self.centre       = ((ra_max+ra_min)/2.0, (dec_max+dec_min)/2.0)
        self.first_record = first_record
        self.num_records  = num_records
        self.max_angular_distance = angular_distance(self.centre,
                                                     (ra_min, dec_min))
        d    = angular_distance(self.centre, (ra_min, dec_max))
        if d > self.max_angular_distance:
            self.max_angular_distance = d


class TychoIndex:
    def __init__(self, filename):
        self.records_in_main = 2539913
        self.records_in_supl1= 17588
        self.records_in_supl2= 1146
        self.index_list = []
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()


        for i in range(len(lines)):
            l = lines[i]
            linesplit = l.split('|')
            start = int(linesplit[0])
            ra_min = float(linesplit[2])*np.pi/180
            ra_max = float(linesplit[3])*np.pi/180
            dec_min = float(linesplit[4])*np.pi/180
            dec_max = float(linesplit[5])*np.pi/180
            end = start
            if i != (len(lines)-1):
                end = int(lines[i+1].split('|')[0])
                num_records = end - start
                start -= 1
                self.index_list.append(IndexRecord(start, num_records, ra_min, dec_min, ra_max, dec_max))
        N = len(self.index_list)
        self.ra           = np.zeros(N)*0.0
        self.dec          = np.zeros(N)*0.0
        self.max_radius   = np.zeros(N)*0.0
        self.first_record = np.zeros(N)

        for i in range(N):
            self.ra[i], self.dec[i] = self.index_list[i].centre
            self.max_radius[i]      = self.index_list[i].max_angular_distance
            self.first_record[i]    = self.index_list[i].first_record


#====================>>>  StarCatalog  <<<====================

class StarCatalog:

    def __init__(self, filename='', indexfilename=''):
        self.catalog = np.zeros((0,3), dtype=np.float32)

        if filename != '':
            print(str(self.read_catalog(filename))+' stars loaded.')

        self.index = TychoIndex(indexfilename)


    def read_catalog(self, filename):
        """
        Reads a starcatalog from disc. Format: binary file. One record
        contains:

        32 bit float: ra in radians
        32 bit float: dec in radians
        32 bit float: magnitude

        These floats should be stored most significant byte first (big-endian)

        """
        num_bytes    = os.path.getsize(filename)
        num_records  = num_bytes//12 # 4 bytes times 3 floats
        # read from file using numarray function
        self.catalog = np.fromfile(filename, np.float32).reshape((num_records, 3))
        if sys.byteorder == 'little':
            self.catalog.byteswap()
        return num_records


    def select_stars(self, fieldcentre, radius, lm_stars):
        """
        return an array containing [[ra, dec, mag], [ra, dec, mag]]
        etc... for all stars in the field centred around fieldcentre
        with radius 'radius'

        fieldcentre is a tuple (ra, dec) in radians. radius is also in
        radians
        """
        fieldsize = angular_distance(fieldcentre, (fieldcentre[0] - radius, fieldcentre[1] - radius))
        d = angular_distance(fieldcentre, (fieldcentre[0] - radius, fieldcentre[1] + radius))
        if d > fieldsize:
            fieldsize = d

        ang_dist = angular_distance(fieldcentre, (self.index.ra, self.index.dec))
        select_regions = (ang_dist - fieldsize - self.index.max_radius) <= 0.0
        first_records = self.index.first_record[select_regions]

        # end records are start of next region...
        select_regions = np.roll(select_regions, 1)
        select_regions[0] = False
        end_records = self.index.first_record[select_regions]

        selected_regions = np.array([], dtype=np.float32).reshape(0, 3)
        for i in range(len(first_records)):
            selected_regions = np.concatenate((selected_regions, self.catalog[int(first_records[i]):int(end_records[i])]), axis=0)
        selected_regions = np.concatenate((selected_regions, self.catalog[self.index.records_in_main:]), axis=0)

        ra = selected_regions[:,0]
        dec = selected_regions[:,1]

        ra_sep = abs(ra-fieldcentre[0])
        toosmall = ra_sep < np.pi
        norm_ra_sep = toosmall * ra_sep + np.logical_not(toosmall) * (2*np.pi-ra_sep)
        star_in_field = np.logical_and(norm_ra_sep*np.cos(dec) < radius, abs(dec-fieldcentre[1]) < radius)

        position_selection = selected_regions[star_in_field]

        # select on magnitude
        mag = position_selection[:,2]
        bright_enough = mag <= lm_stars

        selection = position_selection[bright_enough]

        return selection


__all__ =['StarCatalog']
