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

from math import pi

from fchart3.graphics_interface import INCH, DPMM, POINT, GraphicsInterface, DrawMode

DPI_IMG = 100.0
DPMM_IMG = DPI_IMG/INCH
PONT_IMG = 1.0/DPMM_IMG

A4_WIDTH_POINTS = 594
A4_HEIGHT_POINTS = 842

GREEK_TO_LATEX = {
    "α":"$\\alpha$",
    "β":"$\\beta$",
    "γ":"$\\gamma$",
    "δ":"$\\delta$",
    "ε":"$\\epsilon$",
    "ζ":"$\\zeta$",
    "η":"$\\eta$",
    "θ":"$\\theta$",
    "ι":"$\\iota$",
    "κ":"$\\kappa$",
    "λ":"$\\lambda$",
    "μ":"$\\mu$",
    "ν":"$\\nu$",
    "ξ":"$\\xi$",
    "ο":"$[omicron]$",
    "π":"$\\pi$",
    "ρ":"$\\rho$",
    "σ":"$\\sigma$",
    "ς":"$\\sigma$",
    "τ":"$\\tau$",
    "υ":"$\\upsilon$",
    "φ":"$\\phi$",
    "χ":"$\\chi$",
    "ψ":"$\\psi$",
    "ω":"$\\omega$"
}



class TikZDrawing(GraphicsInterface):
    """
    A CairoTikZ - implement Graphics interface using TikZ
    """
    def __init__(self, fobj, width, height, landscape=False):
        """
        :param fobj: file object
        :param width: width in mm
        :param height: height in mm
        :param landscape: True if orientation of page is landscape
        """
        GraphicsInterface.__init__(self, width , height)

        print('WH {} {}'.format(self.gi_width, self.gi_height))

        if isinstance(fobj, str):
            self.close_fobj = True
            self.fobj = open(fobj, 'w')
        else:
            self.fobj = fobj
            self.close_fobj = False
        self.landscape = landscape
        self.context = None
        self.sfc_width = None
        self.sfc_height = None
        self.set_origin(self.gi_width/2.0, self.gi_height/2.0)

    def new(self):
        self.set_font('Times-Roman', 12*POINT)
        self.set_linewidth(10)
        self.fobj.write('\\begin{tikzpicture}\n')
        w2 = self.gi_width/2
        h2 = self.gi_height/2
        self.fobj.write('\\clip ({:.3f}mm,{:.3f}mm) rectangle ({:.3f}mm,{:.3f}mm);\n'.format(-w2, -h2, w2, h2))
        self.fobj.write('\\tikzstyle {mydashed} = [dashed, dash pattern = on 2 mm off 2 mm]\n')

    def clear(self):
        pass

    def save(self):
        GraphicsInterface.save(self)

    def restore(self):
        GraphicsInterface.restore(self)

    def set_font(self, font='Arial', fontsize=12*POINT):
        GraphicsInterface.set_font(self, font, fontsize)

    def set_linewidth(self, linewidth):
        GraphicsInterface.set_linewidth(self,linewidth)

    def set_solid_line(self):
        GraphicsInterface.set_solid_line(self)

    def set_dashed_line(self, on, off, start=0.0):
        GraphicsInterface.set_dashed_line(self, on, off, start)

    def line(self, x1, y1, x2, y2):
        c1 = self._cohen_sutherland_encode(x1, y1)
        c2 = self._cohen_sutherland_encode(x2, y2)
        if (c1 | c2) == 0 or (c1 & c2) == 0:
            if self.gi_dash_style is None:
                self.fobj.write('\\draw ({:.3f}mm,{:.3f}mm)--({:.3f}mm,{:.3f}mm);\n'.format(x1, y1, x2, y2))
            else:
                self.fobj.write('\\draw[mydashed] ({:.3f}mm,{:.3f}mm)--({:.3f}mm,{:.3f}mm);\n'.format(x1, y1, x2, y2))

    def rectangle(self, x, y, width, height, mode=DrawMode.BORDER):
        pass

    def circle(self, x, y, r, mode=DrawMode.BORDER):
        if mode == DrawMode.BORDER:
            if  self.gi_dash_style is None:
                self.fobj.write('\\draw ({:.3f}mm,{:.3f}mm) circle ({:.3f}mm);\n'.format(x, y, r))
            else:
                self.fobj.write('\\draw[mydashed] ({:.3f}mm,{:.3f}mm) circle ({:.3f}mm);\n'.format(x, y, r))
        elif mode == DrawMode.FILL:
            self.fobj.write('\\filldraw[black]({:.3f}mm, {:.3f}mm) circle({:.3f}mm);\n'.format(x, y, r))

    def polygon(self, vertices, mode=DrawMode.BORDER):
        pass

    def ellipse(self, x, y, rlong, rshort, posangle, mode=DrawMode.BORDER):
        pass

    def _draw_element(self, mode):
        if mode == DrawMode.BORDER:
            pass
        elif mode == DrawMode.FILL:
            pass
        else:
            pass

    def text_right(self, x, y, text):
        self.fobj.write('\\node[right] at ({:.3f}mm, {:.3f}mm) {{{}}};\n'.format(x, y, self._to_latex(text)))

    def text_left(self, x, y, text):
        self.fobj.write('\\node at ({:.3f}mm, {:.3f}mm) {{{}}};\n'.format(x, y, self._to_latex(text)))

    def text_centred(self, x, y, text):
        self.fobj.write('\\node[left] at ({:.3f}mm, {:.3f}mm) {{{}}};\n'.format(x, y, self._to_latex(text)))

    def text_width(self, text):
        return 20.0

    def _moveto(self, x, y):
        pass

    def translate(self, dx, dy):
        pass

    def rotate(self, angle):
        pass

    def clip_path(self, path):
        pass

    def reset_clip(self):
        pass

    def finish(self):
        self.fobj.write('\\end{tikzpicture}\n')
        if self.close_fobj:
            self.fobj.close()

    def on_screen(self, x, y):
        return x > -self.gi_width/2.0 and x < self.gi_width/2.0 and y > -self.gi_height/2.0  and y < self.gi_height/2.0

    def to_pixel(self, x, y):
        return int(x * DPMM_IMG + self.sfc_width/2), int(y * DPMM_IMG + self.sfc_height/2)

    def _cohen_sutherland_encode(self, x, y):
        code = 0
        if x < -self.gi_width/2:
            code |= 1
        if x > self.gi_width/2:
            code |= 2
        if y > self.gi_height/2:
            code |= 4
        if y < -self.gi_height/2:
            code |= 8
        return code

    def _to_latex(self, t):
        latex = [GREEK_TO_LATEX.get(c, c) for c in t]
        return ''.join(latex)
