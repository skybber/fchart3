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

from .graphics_interface import INCH, DPMM, POINT, GraphicsInterface, DrawMode, FontStyle

DPI_IMG = 100.0
DPMM_IMG = DPI_IMG/INCH
PONT_IMG = 1.0/DPMM_IMG

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
    "ο":"o",
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


def _cm(v):
    return v / 10.0


def _to_latex_text(t):
    latex = [GREEK_TO_LATEX.get(c, c) for c in t]
    return ''.join(latex)


def _to_tikz_color(rgb):
    return '{{ rgb,1:red,{:.3f};green,{:.3f};blue,{:.3f} }}'.format(rgb[0], rgb[1], rgb[2])


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

        if isinstance(fobj, str):
            self.close_fobj = True
            self.fobj = open(fobj, 'w')
        else:
            self.fobj = fobj
            self.close_fobj = False
        self.landscape = landscape
        self.set_origin(self.gi_width/2.0, self.gi_height/2.0)
        self.scope_stack = []

    def new(self):
        self.set_font('Times-Roman', 12*POINT)
        self.set_linewidth(10)
        self.fobj.write('\\begin{tikzpicture}\n')
        w2 = self.gi_width/2
        h2 = self.gi_height/2
        self.fobj.write('\\clip ({:.3f},{:.3f}) rectangle ({:.3f},{:.3f});\n'.format(_cm(-w2), _cm(-h2), _cm(w2), _cm(h2)))
        self.fobj.write('\\tikzset {every node}=[font=\\scriptsize]\n')

    def clear(self):
        pass

    def save(self):
        GraphicsInterface.save(self)
        self.scope_stack.append({'shift':[0,0], 'rotate':0, 'flushed':False})

    def restore(self):
        GraphicsInterface.restore(self)
        last = self.scope_stack.pop()
        if last['flushed']:
            self.fobj.write('\end{scope}\n')


    def set_font(self, font='Arial', font_size=12*POINT, font_style=FontStyle.NORMAL):
        GraphicsInterface.set_font(self, font, font_size, font_style)

    def set_linewidth(self, linewidth):
        GraphicsInterface.set_linewidth(self, linewidth)

    def set_solid_line(self):
        GraphicsInterface.set_solid_line(self)

    def set_dashed_line(self, on, off, start=0.0):
        GraphicsInterface.set_dashed_line(self, on, off, start)
        self.fobj.write('\\tikzstyle {{mydashed}} = [dashed, dash pattern = on {}mm off {}mm]\n'.format(on, off))

    def line(self, x1, y1, x2, y2):
        self._flush_scope()
        c1 = self.cohen_sutherland_encode(x1, y1)
        c2 = self.cohen_sutherland_encode(x2, y2)
        if (c1 | c2) == 0 or (c1 & c2) == 0:
            color = _to_tikz_color(self.gi_pen_rgb)
            if self.gi_dash_style is None:
                self.fobj.write('\\draw[line width={:.3f}mm,color={}] ({:.3f},{:.3f})--({:.3f},{:.3f});\n'.format(self.gi_linewidth, color, _cm(x1), _cm(y1), _cm(x2), _cm(y2)))
            else:
                self.fobj.write('\\draw[line width={:.3f}mm,mydashed,color={}] ({:.3f},{:.3f})--({:.3f},{:.3f});\n'.format(self.gi_linewidth, color, _cm(x1), _cm(y1), _cm(x2), _cm(y2)))

    def rectangle(self, x, y, width, height, mode=DrawMode.BORDER):
        self._flush_scope()
        pass

    def circle(self, x, y, r, mode=DrawMode.BORDER):
        self._flush_scope()
        if mode == DrawMode.BORDER:
            color = _to_tikz_color(self.gi_pen_rgb)
            if  self.gi_dash_style is None:
                self.fobj.write('\\draw[line width={:.3f}mm,color={}] ({:.3f},{:.3f}) circle ({:.3f});\n'.format(self.gi_linewidth, color, _cm(x), _cm(y), _cm(r)))
            else:
                self.fobj.write('\\draw[line width={:.3f}mm,mydashed,color={}] ({:.3f},{:.3f}) circle ({:.3f});\n'.format(self.gi_linewidth, color, _cm(x), _cm(y), _cm(r)))
        elif mode == DrawMode.FILL:
            self.fobj.write('\\definecolor{{fcolor}}{{rgb}}{{ {:.3f},{:.3f},{:.3f} }};\n'.format(self.gi_fill_rgb[0], self.gi_fill_rgb[1], self.gi_fill_rgb[2]))
            self.fobj.write('\\filldraw[color=fcolor,fill=fcolor]({:.3f}, {:.3f}) circle({:.3f});\n'.format(_cm(x), _cm(y), _cm(r)))

    def polygon(self, vertices, mode=DrawMode.BORDER):
        self._flush_scope()
        tikz_vertices = ['({:.3f},{:.3f})'.format(_cm(v[0]), _cm(v[1])) for v in vertices]
        tikz_vertices = ' -- '.join(tikz_vertices)
        if mode == DrawMode.BORDER:
            color = _to_tikz_color(self.gi_pen_rgb)
            if  self.gi_dash_style is None:
                self.fobj.write('\\draw[color={}] {} -- cycle;\n'.format(color, tikz_vertices))
            else:
                self.fobj.write('\\draw[mydashed,color={}] {} -- cycle;\n'.format(color, tikz_vertices))
        elif mode == DrawMode.FILL:
            self.fobj.write('\\definecolor{{fcolor}}{{rgb}}{{ {:.3f},{:.3f},{:.3f} }};\n'.format(self.gi_fill_rgb[0], self.gi_fill_rgb[1], self.gi_fill_rgb[2]))
            self.fobj.write('\\draw[color=fcolor,fill=fcolor] {} -- cycle;\n'.format(tikz_vertices))
        else:
            color_fill = _to_tikz_color(self.gi_fill_rgb)
            color_pen = _to_tikz_color(self.gi_pen_rgb)
            self.fobj.write('\\draw[color={},fill={}] {} -- cycle;\n'.format(color_pen, color_fill, tikz_vertices))

    def polyline(self, vertices):
        self._flush_scope()
        tikz_vertices = ['({:.3f},{:.3f})'.format(_cm(v[0]), _cm(v[1])) for v in vertices]
        tikz_vertices = ' -- '.join(tikz_vertices)
        color = _to_tikz_color(self.gi_pen_rgb)
        if  self.gi_dash_style is None:
            self.fobj.write('\\draw[line width={:.3f}mm,color={}] {};\n'.format(self.gi_linewidth, color, tikz_vertices))
        else:
            self.fobj.write('\\draw[line width={:.3f}mm,mydashed,color={}] {};\n'.format(self.gi_linewidth, color, tikz_vertices))

    def ellipse(self, x, y, rlong, rshort, posangle, mode=DrawMode.BORDER):
        self.save()
        self.translate(x, y)
        self.rotate(posangle)
        self._flush_scope()
        if mode == DrawMode.BORDER:
            color = _to_tikz_color(self.gi_pen_rgb)
            if  self.gi_dash_style is None:
                self.fobj.write('\\draw[line width={:.3f}mm,color={}] (0, 0) ellipse ({:.3f} and {:.3f});\n'.format(self.gi_linewidth, color, _cm(rlong), _cm(rshort)))
            else:
                self.fobj.write('\\draw[line width={:.3f}mm,mydashed,color={}] (0, 0) ellipse ({:.3f} and {:.3f});\n'.format(self.gi_linewidth, color, _cm(rlong), _cm(rshort)))
        elif mode == DrawMode.FILL:
            self.fobj.write('\\definecolor{{fcolor}}{{rgb}}{{ {:.3f},{:.3f},{:.3f} }};\n'.format(self.gi_fill_rgb[0], self.gi_fill_rgb[1], self.gi_fill_rgb[2]))
            self.fobj.write('\\filldraw[color=fcolor,fill=fcolor] (0, 0) ellipse ({:.3f} and {:.3f});\n'.format(_cm(rlong), _cm(rshort)))
        self.restore()

    def text_right(self, x, y, text):
        self._flush_scope()
        latex_fs = self._get_latex_font_style()
        scale = self._get_font_scale()
        tr_shape = ',transform shape' if self._is_active_scope() else ''
        self.fobj.write('\\node[scale={:.3f},font=\sffamily{},inner sep=0,anchor=base west{}] at ({:.3f}, {:.3f}) {{{}}};\n'.format(scale, latex_fs, tr_shape, _cm(x), _cm(y), _to_latex_text(text)))

    def text_left(self, x, y, text):
        self._flush_scope()
        latex_fs = self._get_latex_font_style()
        scale = self._get_font_scale()
        tr_shape = ',transform shape' if self._is_active_scope() else ''
        self.fobj.write('\\node[scale={:.3f},font=\sffamily{},inner sep=0,anchor=base east{}] at ({:.3f}, {:.3f}) {{{}}};\n'.format(scale, latex_fs, tr_shape, _cm(x), _cm(y), _to_latex_text(text)))

    def text_centred(self, x, y, text):
        self._flush_scope()
        latex_fs = self._get_latex_font_style()
        scale = self._get_font_scale()
        tr_shape = ',transform shape' if self._is_active_scope() else ''
        self.fobj.write('\\node[scale={:.3f},font=\sffamily{},inner sep=0,anchor=base{}] at ({:.3f}, {:.3f}) {{{}}};\n'.format(scale, latex_fs, tr_shape, _cm(x), _cm(y), _to_latex_text(text)))

    def text_width(self, text):
        return 10.0

    def translate(self, dx, dy):
        scope = self.scope_stack[-1]
        scope['shift'] = [dx, dy]

    def rotate(self, angle):
        scope = self.scope_stack[-1]
        scope['rotate'] = 180.0*angle/pi

    def clip_path(self, path):
        tikz_vertices = ['({:.3f},{:.3f})'.format(_cm(v[0]), _cm(v[1])) for v in path]
        tikz_vertices = ' -- '.join(tikz_vertices)
        self.fobj.write('\\begin {{scope}};\n'.format(tikz_vertices))
        self.fobj.write('\\clip {}--cycle;\n'.format(tikz_vertices))

    def reset_clip(self):
        self.fobj.write('\\end {scope}\n')

    def finish(self):
        self.fobj.write('\\end{tikzpicture}\n')
        if self.close_fobj:
            self.fobj.close()

    def on_screen(self, x, y):
        return x > -self.gi_width/2.0 and x < self.gi_width/2.0 and y > -self.gi_height/2.0  and y < self.gi_height/2.0

    def _flush_scope(self):
        if len(self.scope_stack)>0:
            scope = self.scope_stack[-1]
            if not scope['flushed']:
                shift = scope['shift']
                rotate = scope['rotate']
                if shift[0] != 0 or shift[1] != 0 or rotate != 0:
                    self.fobj.write('\\begin{{scope}}[shift={{({:.3f},{:.3f})}},rotate={:.3f}]\n'.format(_cm(shift[0]), _cm(shift[1]), rotate))
                    scope['flushed'] = True

    def _is_active_scope(self):
        return len(self.scope_stack)>0 and self.scope_stack[-1]['flushed']

    def _get_latex_font_style(self):
        if self.gi_font_style == FontStyle.ITALIC:
            return '\\itshape'
        if self.gi_font_style == FontStyle.BOLD:
            return '\\bfseries'
        if self.gi_font_style == FontStyle.ITALIC_BOLD:
            return '\\itshape\\bfseries'
        return ''

    def _get_font_scale(self):
        return self.gi_font_size / self.gi_default_font_size