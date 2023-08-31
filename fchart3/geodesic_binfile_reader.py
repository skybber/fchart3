#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2023 fchart3 authors
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

import struct
import os

from .geodesic_grid import *

FILE_MAGIC_OTHER_ENDIAN = 0x0a045f83
FILE_MAGIC = 0x835f040a
FILE_MAGIC_NATIVE = 0x835f040b


def _swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]


def _swap16(i):
    return struct.unpack("<H", struct.pack(">H", i))[0]


class GeodesicBinFileReader:
    """
    Stellarium bin file reader. Reads data organized into geodesic grid.
    """
    def __init__(self):
        self.byteswap = False
        self.level = None
        self.file = None
        self.file_type = None
        self.nr_of_stars = 0
        self._magic = None
        self._major = None
        self._minor = None
        self._mag_min = None
        self._mag_range = None
        self._mag_steps = None
        self._mag_table = None
        self._index_offset = None
        self._index_count = None

    @property
    def mag_min_mag(self):
        return self._mag_min / 1000.0

    def get_star_rec_size(self):
        if self.file_type == 2:
            return 6    # Star2
        if self.file_type == 1:
            return 10   # Star1
        return 28       # Star0

    def open_file(self, file_name):
        self.file = None
        if os.path.isfile(file_name):
            self.file = open(file_name, 'rb')
        return self.file

    def close_file(self):
        if self.file:
            self.file.close()
            self.file = None

    def get_record_count(self, index):
        return self._index_count[index]

    def get_offset(self, index):
        return self._index_offset[index]

    def get_mag_table(self):
        if self._mag_table is None:
            mag_table = []
            mag_min = 0.001 * self._mag_min
            k = 0.001 * self._mag_range / self._mag_steps
            for i in range(4096):
                mag_table.append(mag_min+k*i)
            self._mag_table = np.array(mag_table)
        return self._mag_table

    def read_header(self):
        self._magic = struct.unpack('I', self.file.read(4))[0]
        self.file_type = struct.unpack('I', self.file.read(4))[0]
        self._major = struct.unpack('I', self.file.read(4))[0]
        self._minor = struct.unpack('I', self.file.read(4))[0]
        self.level = struct.unpack('I', self.file.read(4))[0]
        self._mag_min = struct.unpack('i', self.file.read(4))[0]
        self._mag_range = struct.unpack('I', self.file.read(4))[0]
        self._mag_steps = struct.unpack('I', self.file.read(4))[0]

        self._byte_swap = (self._magic == FILE_MAGIC_OTHER_ENDIAN)

        if self._byte_swap:
            self.file_type = _swap32(self.file_type)
            self._major = _swap32(self._major)
            self._minor = _swap32(self._minor)
            self.level = _swap32(self.level)
            self._mag_min = _swap32(self._mag_min)
            self._mag_range = _swap32(self._mag_range)
            self._mag_steps = _swap32(self._mag_steps)
        elif self._magic != FILE_MAGIC and self._magic != FILE_MAGIC_NATIVE:
            raise ValueError("Invalid file magic=0x{:02X}!".format(self._magic))

        if self.file_type not in range(3):
            raise ValueError("Invalid file type={}!".format(hex(self.file_type)))

        nr_of_zones = GeodesicGrid.nr_of_zones(self.level)

        self.nr_of_stars = 0

        index_offset_start = self.file.tell() + nr_of_zones * 4

        self._index_count = [None] * nr_of_zones
        self._index_offset = [None] * nr_of_zones

        star_rec_size = self.get_star_rec_size()

        for i in range(nr_of_zones):
            nrecs = struct.unpack('I', self.file.read(4))[0]

            if self.byteswap:
                nrecs = _swap32(nrecs)

            self._index_count[i] = nrecs
            self._index_offset[i] = index_offset_start + self.nr_of_stars * star_rec_size
            self.nr_of_stars += nrecs


if __name__ == '__main__':
    fname = './data/catalogs/stars_0_0v0_8.cat'
    reader = GeodesicBinFileReader()
    reader.open_file(fname)
    reader.read_header()
    print("Done")

