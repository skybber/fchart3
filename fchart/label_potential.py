from numpy import *


class LabelPotential:
    def __init__(self, fieldradius, deepskylist):
        """
        fieldradius in mm
        deepskylist [(x,y,size), (x,y,size),...]
        x,y, size in mm
        """
        self.fieldradius  = fieldradius
        self.positions = zeros((len(deepskylist), 2))*0.0
        self.sizes = zeros(len(deepskylist))*0.0
        for i in range(len(deepskylist)):
            x,y,s = deepskylist[i]
            if s <= 0:
                s = 1
            self.sizes[i] = s**0.5
            self.positions[i,0] = x
            self.positions[i,1] = y


    def add_position(self,x,y,size):
        N = len(self.sizes)
        newpos = zeros((N+1,2))*0.0
        newpos[0:N,:] = self.positions
        newpos[N,:] = [x,y]

        newsize = zeros(N+1)*0.0
        newsize[0:N] = self.sizes
        newsize[N] = size**0.5

        self.positions = newpos
        self.sizes = newsize

    def compute_potential(self,x,y):
        """
        x,y in mm
        """
        value = 0.0
        ss = sum(self.sizes)
        rf = ((x**2+y**2)**0.5 - self.fieldradius)**-3

        r2 = (self.positions[:,0]-x)**2 + (self.positions[:,1]-y)**2
        sr = (r2+0.1)**(-1)
        p = self.sizes*sr
        value = sum(p) + ss*rf
        return value


__all__ = ['LabelPotential']
