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

from collections import namedtuple
import struct
import os

DataElement = namedtuple('DataElement' , 'name size type scale')
DATAELEMENT_FMT = '10sbBi'
DATA_ELEMT_SIZE = struct.calcsize(DATAELEMENT_FMT)

def _swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]


def _swap16(i):
    return struct.unpack("<H", struct.pack(">H", i))[0]


def _read_exactly(file, size):
    bytes = file.read(size)
    if len(bytes) < size:
        raise IOError("Failed to read enough data")
    return bytes


class HtmBinFileReader:
    """
    Read KStars HTM bin file header. There are 3 KStars HTM files:
    - unnamedstars.dat
    - deepstars.dat based on Tycho2 catalog
    - USNO-NOMAD-1e8.dat containing ~100 million stars
    """
    def __init__(self):
        self._file = None
        self._byteswap = False
        self._data_offset = None
        self.header_text = ''
        self.version_number = None
        self.preamble_updated = None
        self.nfields = 0
        self.record_size = None
        self.itable_offset = 0
        self.index_size = 0
        self._record_count = 0
        self.fd_updated = False
        self.index_updated = False
        self.fields = []
        self.index_offset = []
        self.index_count = []


    @property
    def data_offset(self):
        return self._data_offset


    @property
    def byteswap(self):
        return self._byteswap


    @property
    def record_count(self):
        return self._record_count


    @property
    def file(self):
        return self._file


    @property
    def guess_record_size(self):
        return self.record_size if self.record_size else None


    def get_record_count(self, index):
        return self.index_count[index]


    def get_offset(self, index):
        return self.index_offset[index]


    def open_file(self, file_name):
        self._file = None
        if os.path.isfile(file_name):
            self._file = open(file_name, 'rb')
        return self._file


    def close_file(self):
        if self._file:
            self._file.close()
            self._file = None


    def read_header(self):
        # Read the first 124 bytes of the binary file which contains a general text about the binary data.
        # e.g. "KStars Star Data v1.0. To be read using the 32-bit StarData structure only"
        self.header_text  = _read_exactly(self._file, 124).decode("ascii")

        # Find out endianess from reading "KS" 0x4B53 in the binary file which was encoded on a little endian machine
        # Therefore, in the binary file it is written as 53 4B (little endian as least significant byte is stored first),
        # and when read on a little endian machine then it results in 0x4B53 (least significant byte is stored first in memory),
        # whereas a big endian machine would read it as 0x534B (most significant byte is stored first in memory).
        endian_id = struct.unpack('h', self._file.read(2))[0]
        self._byteswap = (endian_id != 0x4B53)
        self.version_number = struct.unpack('b', self._file.read(1))[0]

        self.preamble_updated = True
        # Read the field descriptor table
        self.nfields = struct.unpack('h', self._file.read(2))[0]
        if self._byteswap:
            self.nfields = _swap16(self.nfields)

        for i in range(self.nfields):
            # Read 16 byte dataElement that describe each field (name[8], size[1], type[1], scale[4])
            de = DataElement._make(struct.unpack(DATAELEMENT_FMT, self._file.read(DATA_ELEMT_SIZE)))
            if self._byteswap:
                de.scale = _swap32(de.scale)
            self.fields.append(de)

        if not self.record_size:
            self.record_size = sum(fld.size for fld in self.fields)

        self.fd_updated = True

        # Read the index table
        self.index_size = struct.unpack('i', self._file.read(4))[0]
        if self._byteswap:
            self.index_size = _swap32(self.index_size)

        # Find out current offset so far in the binary file (how many bytes we read so far)
        self.itable_offset = self._file.tell()

        self._record_count = 0

        prev_offset = 0
        prev_nrecs  = 0

        if self.index_size == 0:
            raise ValueError("Zero index size!")

        # We read each 12-byte index entry (ID[4], Offset[4] within file in bytes, nrec[4] # of Records).
        # After reading all the indexes, we are (itable_offset + indexSize * 12) bytes within the file
        # indexSize is usually the size of the HTM level (eg. HTM level 3 --> 512)
        for j in range(self.index_size):
            ID = struct.unpack('I', self._file.read(4))[0]

            if self._byteswap:
                ID = _swap32(ID)

            if ID >= self.index_size:
                raise IndexError("ID {} is greater than the expected number of expected entries ({})".format(ID, self.index_size))

            if ID != j:
                raise ValueError("Found ID {}, at the location where ID {} was expected".format(ID, j))

            offset = struct.unpack('I', self._file.read(4))[0]

            if self._byteswap:
                offset = _swap32(offset)

            nrecs = struct.unpack('I', self._file.read(4))[0]

            if self._byteswap:
                nrecs = _swap32(nrecs)

            if prev_offset != 0 and prev_nrecs != (offset - prev_offset) / self.record_size:
                raise ValueError("Expected {}  = ({} - {}) / {} records, but found {}, in index entry {}",
                                    (offset - prev_offset) / self.record_size,
                                    offset,
                                    prev_offset,
                                    self.record_size,
                                    prev_nrecs,
                                     j - 1)

            self.index_offset.append(offset)
            self.index_count.append(nrecs)

            self._record_count += nrecs
            prev_offset = offset
            prev_nrecs  = nrecs

        self._data_offset = self._file.tell()

        self.index_updated = True


if __name__ == '__main__':
    fname = './data/catalogs/deepstars.dat'
    file = open(fname, 'rb')
    reader = HtmBinFileReader(file)
    reader.read_header()
    print("Done")
