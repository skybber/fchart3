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

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Any
import numpy as np


class DsoType(Enum):
    UNKNOWN = 0               # unknown
    G = 1                     # galaxy
    N = 2                     # Galactic nebula
    PN = 3                    # Planetary nebula
    OC = 4                    # Open cluster
    GC = 5                    # Globular cluster
    PG = 6                    # Part of galaxy (star cloud, HII region)
    ALREADY_LISTED_1 = 7      # already elsewhere in NGC or IC
    ALREADY_LISTED_2 = 8      # IC object already in NGC
    STARS = 9                 # Star(s)
    NOTFOUND = 10             # Not found
    SNR = 11                  # Supernova remnant
    QSO = 12                  # Quasar
    GALCL = 13                # Galaxy cluster


TYPENAME = ['Unknown', 'G', 'N', 'PN', 'OC', 'GC', 'PG', 'xxx', 'xxx', 'AST', 'xxx', 'SNR', 'QSO', 'GALCL']


@dataclass(slots=True, eq=False)
class DeepskyObject:
    """
    This class has the following fields:

    - cat            name of catalog ('NGC', 'IC', 'MEL',...). Not 'M'.
                     If the object is also in the Messier list, the
                     messier field is larger than 0
    - name           primary name of object in that catalog ('891',
                     '3683A',...)
    - all_names      all names of the object in this catalog.
    - synonyms       all object synonyms
    - type           integer indicating the type of the object. There
                     are constants defined in this module to help
                     interpret this field:
                     UNKNOWN         = 0      unknown type
                     G               = 1      galaxy
                     N               = 2      diffuse nebula
                     PN              = 3      planetary nebula
                     OC              = 4      open cluster
                     GC              = 5      globular cluster
                     PG              = 6      part of other galaxy
                     ALREADY_LISTED_1= 7      already in catalog
                     ALREADY_LISTED_2= 8      already in catalog
                     STARS           = 9      asterism
                     NOTFOUND        =10      not found in reality/error
                     SNR             =11      supernova remnant
    - ra             right ascension in radians (J2000)
    - dec            declination in radians (J2000)
    - mag            magnitude
    - rlong          long dimension of object in radians (-1 if unknown)
    - rshort         short dimension of object in radians (-1 if unknown)
    - position_angle position angle (N through E) in radians
                     (default: 0.5np.pi)
    - messier        number in messier list (default: -1)
    - visible        True if object is visible on the map
    """
    cat: str = 'NGC'
    name: str = ''

    all_names: List[str] = field(default_factory=list)
    synonyms: List[Tuple[str, str]] = field(default_factory=list)

    type: DsoType = DsoType.UNKNOWN

    ra: float = -1.0
    dec: float = 0.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    mag: float = -100.0
    rlong: float = -1.0
    rshort: float = -1.0
    position_angle: float = float(np.pi * 0.5)

    messier: int = -1
    master_object: Optional["DeepskyObject"] = None
    visible: bool = True
    outlines: Any = None
    __hash__ = object.__hash__

    def add_name(self, n: str) -> None:
        self.all_names.append(n)

    def add_synonym(self, cat_name_tuple: Tuple[str, str]) -> None:
        self.synonyms.append(cat_name_tuple)

    def set_names_sorted(self) -> None:
        self.all_names.sort()

    def _typename(self) -> str:
        idx = self.type.value
        return TYPENAME[idx] if 0 <= idx < len(TYPENAME) else TYPENAME[DsoType.UNKNOWN.value]

    def label(self) -> str:
        if self.messier > 0:
            return f'M {self.messier}'
        if self.cat == 'NGC':
            return '-'.join(sorted(self.all_names) or [self.name])
        if self.cat == 'Abell':
            return f'{self.cat} {self.name}'
        if self.cat == 'Sh2':
            return f'{self.cat}-' + '-'.join(sorted(self.all_names) or [self.name])
        return f'{self.cat} ' + '-'.join(sorted(self.all_names) or [self.name])

    def primary_label(self) -> str:
        if self.messier > 0:
            return f'M {self.messier}'
        if self.cat == 'Sh2':
            return f'Sh2-{self.name}'
        return f'{self.cat} {self.name}'

    def __str__(self) -> str:
        return f"{self.primary_label()} {self._typename()}"


# One outline is typically: (ra_list, dec_list) where each list contains floats (radians).
Outline = Tuple[List[float], List[float]]


@dataclass(slots=True)
class UnknownNebula:
    outlines: List[Optional[List[Outline]]] = field(default_factory=lambda: [None, None, None])

    ra_min: Optional[float] = None
    ra_max: Optional[float] = None
    dec_min: Optional[float] = None
    dec_max: Optional[float] = None

    def _update_bounds(self, ras: List[float], decs: List[float]) -> None:
        for ra in ras:
            if self.ra_min is None or ra < self.ra_min:
                self.ra_min = ra
            if self.ra_max is None or ra > self.ra_max:
                self.ra_max = ra

        for dec in decs:
            if self.dec_min is None or dec < self.dec_min:
                self.dec_min = dec
            if self.dec_max is None or dec > self.dec_max:
                self.dec_max = dec

    def add_outlines(self, level: int, outline: Outline) -> None:
        if level < 0 or level >= len(self.outlines):
            raise ValueError(f"Invalid outline level {level}. Expected 0..{len(self.outlines)-1}.")

        ras, decs = outline
        self._update_bounds(ras, decs)

        if self.outlines[level] is None:
            self.outlines[level] = []

        self.outlines[level].append(outline)


def cmp_ra(x, y):
    r = 0
    if x.ra > y.ra:
        r = 1
    if x.ra < y.ra:
        r = -1
    return r


def cmp_dec(x, y):
    r = 0
    if x.dec > y.dec:
        r = 1
    if x.dec < y.dec:
        r = -1
    return r


def cmp_name(x,y):
    xn = x.label()
    yn = y.label()
    r = 0
    if xn > yn:
        r = 1
    if xn < yn:
        r = -1
    return r


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
