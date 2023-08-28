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

import numpy as np


class WidgetCoords:

    def __init__(self, language, color=(0, 0, 0)):
        self.language = language
        self.color = color

    def draw(self, graphics, left, bottom, ra, dec, legend_only):
        """
        left,bottom are coordinates of the lower left corner of the textbox
        """
        rah = int(ra*12/np.pi)
        ram = int((ra*12/np.pi -rah)*60)
        ras = int(((ra*12/np.pi -rah)*60 - ram)*60+0.5)
        if ras == 60:
            ram +=1
            ras = 0
        if ram == 60:
            rah += 1
            ram = 0
        if rah == 24:
            rah = 0

        decsign = '+'
        if dec < 0.0:
            decsign = '-'
        decd = int(abs(dec)*180/np.pi)
        decm = int((abs(dec)*180/np.pi-decd)*60)
        decs = int( ((abs(dec)*180/np.pi-decd)*60 -decm)*60 + 0.5)

        if decs == 60:
            decm += 1
            decs = 0
        if decm == 60:
            decm = 0

        text = str(rah).rjust(2) + self.language['h'] + str(ram) + self.language['m'] + str(ras) + self.language['s'] + \
             ' ' + decsign + str(decd) + '°' + str(decm) + '\'' + str(decs) + '"'

        graphics.text_left(left, bottom, text)
