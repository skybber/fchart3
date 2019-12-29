from math import pi

class MirroringGraphics:
    """
    A Graphics used for mirroring in X and Y axises
    """
    def __init__(self, graphics, mirror_x, mirror_y):
        self.graphics = graphics
        self.mirror_x = mirror_x
        self.mirror_y = mirror_y
        self.mul_x = -1 if mirror_x else 1
        self.mul_y = -1 if mirror_y else 1


    def translate(self, dx, dy):
        self.graphics.translate(self.mul_x * dx, self.mul_y * dy)


    def rotate(self, angle):
        if self.mirror_x:
            angle += pi
        if self.mirror_y:
            angle = -angle
        self.graphics.rotate(angle)


    def line(self, x1, y1, x2, y2):
        self.graphics.line(self.mul_x*x1, self.mul_y*y1, self.mul_x*x2, self.mul_y*y2)


    def circle(self, x, y, r, mode='P'):
        self.graphics.circle(self.mul_x*x, self.mul_y*y, r, mode)


    def ellipse(self, x, y, rlong, rshort, position_angle, mode='P'):
        self.graphics.ellipse(self.mul_x*x, self.mul_y*y, rlong, rshort, position_angle, mode)


    def text(self, text):
        self.graphics.text(text)

    def text_right(self, x, y, text):
        if self.mirror_x:
            self.graphics.text_left(-x, self.mul_y*y, text)
        else:
            self.graphics.text_right(x, self.mul_y*y, text)


    def text_left(self, x, y, text):
        if self.mirror_x:
            self.graphics.text_right(-x, self.mul_y*y, text)
        else:
            self.graphics.text_left(x, self.mul_y*y, text)


    def text_centred(self, x, y, text):
        self.graphics.text_centred(self.mul_x*x, self.mul_y*y, text)
