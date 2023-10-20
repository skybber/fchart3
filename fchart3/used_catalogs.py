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

import gettext
import os

uilanguage=os.environ.get('fchart3lang')
try:
    lang = gettext.translation( 'messages',localedir='locale', languages=[uilanguage])
    lang.install()
    _ = lang.gettext
except:                  
    _ = gettext.gettext
    
import numpy as np

from .astrocalc import sphere_to_rect
from .constellation import ConstellationCatalog
from .geodesic_star_catalog import GeodesicStarCatalog
from .deepsky_catalog import DeepskyCatalog
from .hnsky_deepsky import import_hnsky_deepsky, import_hnsky_supplement
from .pgc_deepsky import import_pgc_deepsky
from .outlines_deepsky import import_outlines_catgen
from .milkyway import import_milky_way
from .milkyway_enhanced import EnhancedMilkyWay
from .vic import import_vic
from . import deepsky_object as deepsky



class UsedCatalogs:
    def __init__(self, data_dir, extra_data_dir, supplements=None, limit_magnitude_deepsky=10.0, force_messier=False,
                 force_asterisms=False, force_unknown=False, show_catalogs=None, use_pgc_catalog=False,
                 enhanced_mw_optim_max_col_diff=None):
        # Read basic catalogs
        self._constellcatalog = ConstellationCatalog(data_dir+os.sep + 'bsc5.dat',
                                               data_dir+os.sep + 'constellationship_western.fab',
                                               data_dir+os.sep + 'constbndJ2000.dat',
                                               data_dir+os.sep + 'cross-id.dat')
        self._starcatalog = GeodesicStarCatalog(data_dir, extra_data_dir, self._constellcatalog.bsc_hip_map)
        self._deeplist, self._unknown_nebulas = self._get_deepsky_list(data_dir, show_catalogs, use_pgc_catalog, supplements)

        # Apply magnitude selection to deepsky list, build Messier list
        self._reduced_deeplist = []
        self._messierlist=[]
        for dso in self._deeplist:
            dso.x, dso.y, dso.z = sphere_to_rect(dso.ra, dso.dec)
            if dso.messier > 0:
                self._messierlist.append(dso)
            if force_messier and dso.messier > 0:
                self._reduced_deeplist.append(dso)
            elif dso.mag <= limit_magnitude_deepsky and \
                    dso.master_object is None and \
                    dso.type != deepsky.GALCL and \
                    (dso.type != deepsky.STARS or force_asterisms or (dso.messier > 0 and dso.type == deepsky.STARS)) and \
                    (dso.type != deepsky.PG or force_unknown or dso.type == deepsky.PG and dso.mag > -5.0):
                self._reduced_deeplist.append(dso)

        self._messierlist.sort(key=lambda x: x.messier)
        self._deepskycatalog = DeepskyCatalog(self._reduced_deeplist, force_messier)
        self._milky_way = import_milky_way(os.path.join(data_dir, 'milkyway.dat'))
        self._enhanced_milky_way = EnhancedMilkyWay(os.path.join(data_dir, 'milkyway_enhanced2.dat'), enhanced_mw_optim_max_col_diff)

    def free_mem(self):
        self._starcatalog.free_mem()

    @property
    def messierlist(self):
        return self._messierlist

    @property
    def starcatalog(self):
        return self._starcatalog

    @property
    def constellcatalog(self):
        return self._constellcatalog

    @property
    def deepskycatalog(self):
        return self._deepskycatalog

    @property
    def deeplist(self):
        return self._deeplist

    @property
    def reduced_deeplist(self):
        return self._reduced_deeplist

    @property
    def unknown_nebulas(self):
        return self._unknown_nebulas

    @property
    def milky_way(self):
        return self._milky_way

    @property
    def enhanced_milky_way(self):
        return self._enhanced_milky_way

    def lookup_dso(self, dso_name):
        index = 0
        cat = ''
        if dso_name[0:3] == 'Sh2':
            cat = 'Sh2'
            index = 4
        elif dso_name[0:2].upper() == '3C':
            cat = '3C'
            index = 2
        else:
            for i in range(len(dso_name)):
                ch = dso_name[i]
                if ch.isalpha():
                    cat += ch
                else:
                    index = i
                    break
            # special handling for Minkowski
            if cat == 'M' and i+1<len(dso_name) and (dso_name[i+1] == '-' or dso_name[i+1] == '_') :
                cat = 'Mi'
            if cat.upper() == 'N' or cat == '' or cat.upper == 'NGC':
                cat = 'NGC'

            if cat.upper() == 'I' or cat.upper() == 'IC':
                cat = 'IC'

        name = dso_name[index:].upper().rstrip().lstrip()

        # determine ra, dec of fieldcentre
        found_dso = None
        cat_upper = cat.upper()
        if cat_upper != 'M':
            for dso in self.deeplist:
                if dso.cat.upper() == cat_upper:
                    if name.upper() in dso.all_names:
                        cat = dso.cat
                        found_dso = dso
                        break
                for syn_dso in dso.synonyms:
                    if syn_dso[0].upper() == cat_upper and name.upper() == syn_dso[1]:
                        cat = dso.cat
                        found_dso = dso
                        break
                if found_dso:
                    break
        else:
            cat = 'M'
            for mdso in self.messierlist:
                if mdso.messier == int(name):
                    name = str(mdso.messier)
                    found_dso = mdso
                    break

        return found_dso, cat, name

    def _get_dso_dict(sell, deeplist):
        dso_dict = {}
        for dso in deeplist:
            if dso.cat == 'Sh2':
                name = dso.cat + '-' + dso.name
            else:
                name = dso.cat + dso.name
            dso_dict[name] = dso
            for syn in dso.synonyms:
                dso_dict[syn[0] + syn[1]] = dso
        return dso_dict

    def _norm_dso_name(self, dso_name):
        end_cat, start_num = -1, -1
        for j, c in enumerate(dso_name):
            if c.isdigit():
                if end_cat == -1:
                    end_cat = j
                if c != '0':
                    start_num = j
                    break
        if end_cat != -1 and start_num != -1:
            dso_name = dso_name[:end_cat] + dso_name[start_num:]
        return dso_name

    def _convert_outlines_to_np_arr(self, outlines):
        arr_x = []
        arr_y = []
        for v in outlines:
            arr_x.append(v[0])
            arr_y.append(v[1])
        return (np.array(arr_x), np.array(arr_y))

    def _get_deepsky_list(self, data_dir, show_catalogs, use_pgc_catalog, supplements):
        all_dsos = {}
        print( _('Reading Hnsky...'), flush=True)
        hnskylist = import_hnsky_deepsky(os.path.join(data_dir, 'deep_sky.hnd'), show_catalogs, all_dsos)
        if use_pgc_catalog:
            print(_('Reading PGC/UGC...'), flush=True)
            pgclist = import_pgc_deepsky(os.path.join(data_dir, 'PGC.dat'), os.path.join(data_dir, 'PGC_update.dat'), show_catalogs, all_dsos)
        else:
            pgclist = []
        print(_('Reading VIC...'), flush=True)
        viclist = import_vic(os.path.join(data_dir, 'vic.txt'))
        deeplist = hnskylist + pgclist + viclist
        if supplements:
            for supplement in supplements:
                print(_('Reading hnsky supplement {} ...'.format(supplement)), flush=True)
                suppl_dsos = import_hnsky_supplement(supplement, all_dsos)
                deeplist += suppl_dsos
        deeplist.sort(key=deepsky.cmp_to_key(deepsky.cmp_name))
        print(_('Reading DSO outlines...'), flush=True)
        dso_dict = self._get_dso_dict(deeplist)

        all_lvl_outlines = import_outlines_catgen(os.path.join(data_dir, 'outlines_catgen.dat'))

        unknown_nebulas = []
        unknown_nebula_map = {}

        for i in range(3):
            for name in all_lvl_outlines[i]:
                dso = dso_dict.get(self._norm_dso_name(name))
                outlines_ar = all_lvl_outlines[i][name]
                if dso:
                    if dso.outlines is None:
                        dso.outlines = [[], [], []]
                    for outlines in outlines_ar:
                        dso.outlines[i].append(self._convert_outlines_to_np_arr(outlines))
                else:
                    if name in ['Orion', 'Scorpion']: #Hack
                        uneb = unknown_nebula_map.get(name)
                        if not uneb:
                            uneb = deepsky.UnknownNebula()
                            unknown_nebula_map[name] = uneb
                            unknown_nebulas.append(uneb)
                        for outlines in outlines_ar:
                            uneb.add_outlines(i, self._convert_outlines_to_np_arr(outlines))

        return deeplist, unknown_nebulas
