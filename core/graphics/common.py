from OpenGL.GL import *

from graphic import Graphic

class Repeated:
    def __init__(self,dim,offset,graphic):
        self.object = glGenLists(1)
        glNewList(self.object, GL_COMPILE)
        glPushMatrix()
        for y in xrange(dim[1]):
            glPushMatrix()
            for x in xrange(dim[0]):
                graphic.draw()
                glTranslate(offset[0],offset[1],0)
            glPopMatrix()
            glTranslate(-offset[0],offset[1],0)
        glPopMatrix()
        glEndList()

    def draw(self):
        glCallList(self.object)
