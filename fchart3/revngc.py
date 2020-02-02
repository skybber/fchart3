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

from numpy import *

from fchart3 import deepsky_object as deepsky

def _parse_rev_ngcic_line(line, catalog='NGC'):
    object = deepsky.DeepskyObject()
    object.cat = catalog
    typechar = line[11]
    # only continue filling in rest if the type of object is known
    if typechar != ' ':
        object.name = line[0:5].lstrip().rstrip()
        object.all_names = [object.name]
        compchar = line[5]
        if compchar != ' ':
            object.component = int(compchar)

        object.type = int(typechar)
        if object.type == deepsky.N and line[78:81] == 'SNR':
            object.type = deepsky.SNR
        object.constellation = line[15:18].upper()

        ra = pi*(float(line[20:22])+float(line[23:25])/60.0 + float(line[26:28])/3600.0)/12.0
        dec = pi*(float(line[32:34]) + float(line[35:37])/60.0 + float(line[38:40])/3600.0)/180.0
        if line[31] == '-':
            dec *= -1.0
        object.ra = ra
        object.dec = dec

        magtext= line[50:54].rstrip()
        if magtext != '':
            object.mag = float(magtext)
        else:
            magtext = line[43:47].rstrip()
            if magtext != '':
                object.mag = float(magtext)


        rlongtext = line[61:67].rstrip()
        if rlongtext != '':
            object.rlong = float(rlongtext)/60.0*pi/180.0/2.0

        rshorttext = line[68:73].rstrip()
        if rshorttext != '':
            object.rshort = float(rshorttext)/60.0*pi/180.0/2.0

        if object.rshort < 0.0:
            object.rshort = object.rlong

        posangletext = line[74:77].rstrip()
        if posangletext != '':
            object.position_angle = float(posangletext)*pi/180.0

        ID1text = line[96:111].strip()
        if ID1text != '':
            if ID1text[0:2] == 'M ':
                object.messier = int(ID1text[1:])
            elif ID1text.split()[0].strip() == catalog:
                object.all_names.append(ID1text.split()[1].split('-')[0].strip())


        ID2text = line[112:127].strip()
        if ID2text != '':
            if ID2text.split()[0].strip() == catalog:
                object.all_names.append(ID2text.split()[1].split('-')[0].strip())

    return object


def import_revised_ngcic(filename, ngcic='NGC'):# or 'IC'
    """
    Reads data from the revised NGC/IC project. Returns a list
    of DeepskyObjects()
    """
    ngcfile = open(filename, 'r', encoding='ISO-8859-1')
    lines   = ngcfile.readlines()[2:]
    ngcfile.close()

    ngclist_single = []
    ngclist_multiple = []
    for line in lines:
        if len(line) >= 170:
            ngcobject = _parse_rev_ngcic_line(line, ngcic)

            # Do not include ICs that are also NGCs. DO include NGCs or
            # ICs that have already been mentioned in their "own" catalog.
            if ngcobject.type != deepsky.UNKNOWN and \
                   ngcobject.type != deepsky.NOTFOUND and \
                   ngcobject.type != deepsky.ALREADY_LISTED_2 and \
                   ngcobject.type != deepsky.ALREADY_LISTED_1:
                if len(ngcobject.all_names) == 1:
                    ngclist_single.append(ngcobject)
                else:
                    ngclist_multiple.append(ngcobject)

    return ngclist_single, ngclist_multiple


if __name__=='__main__':
    print(__file__)
    ngclist = import_revised_ngcic('data/revngc.txt', 'NGC')
    iclist  = import_revised_ngcic('data/revic.txt', 'IC')

    print(len(ngclist), len(iclist))

    deeplist = ngclist+iclist

    winterlist = []
    for object in deeplist:
        if object.ra >= pi/12.0 and object.ra < 9*pi/12.0 and object.dec > -35*pi/180 and object.mag < 12.5 and object.mag > -5.0:
            winterlist.append(object)

    def magsort(x,y):
        r = 0
        if x.mag < y.mag:
            r = -1
        if x.mag > y.mag:
            r = 1
        return r

    winterlist.sort(magsort)
    for i in winterlist:
        if i.messier > 0:
            print(('M '+str(i.messier)).ljust(10)+' '+str(i.mag).rjust(4)+' '+deepsky.TYPENAME[i.type])
        else:
            print((i.cat+' '+i.name).ljust(10)+' '+str(i.mag).rjust(4)+' '+deepsky.TYPENAME[i.type])


    mlist = []
    mnumbers=[]
    for object in deeplist:
        if object.messier > 0:
            mlist.append(object)
            mnumbers.append(object.messier)
    print(len(mlist))
    print(sort(mnumbers))


__all__ = ['import_revised_ngcic']
