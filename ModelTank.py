"""
Model tank component, represented as a GL_WIREFRAME object

Daniel Scrivener 08/2022
"""

from Displayable import Displayable
from Component import Component
from GLBuffer import VAO, VBO, lineEBO
import numpy as np
import ColorType
from collada import *

class Tank(Component):

    def __init__(self, position, shaderProg, scale):
        self.species_id = -1
        self.default_color = ColorType.PINK
        self.mesh = DisplayableTank(shaderProg, scale, color=ColorType.PINK)
        super(Tank, self).__init__(position, self.mesh)

class DisplayableTank(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    vertices = None  # array to store vertices information
    indices = None  # stores triangle indices to vertices
    vCenter = None # the "center" of the mesh, approximated as the average vertex

    defaultColor = None

    def __init__(self, shaderProg, scale, color=ColorType.PINK):
        super(DisplayableTank, self).__init__()
        assert(len(scale) == 3)

        self.defaultColor = np.array(color.getRGB())

        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = lineEBO()

        # construct vertex list
        
        self.vertices = np.array([
            -scale[0] / 2, -scale[1] / 2, -scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
            -scale[0] / 2, -scale[1] / 2, scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
            -scale[0] / 2, scale[1] / 2, -scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
            -scale[0] / 2, scale[1] / 2, scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
            scale[0] / 2, -scale[1] / 2, -scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
            scale[0] / 2, -scale[1] / 2, scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
            scale[0] / 2, scale[1] / 2, -scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
            scale[0] / 2, scale[1] / 2, scale[2] / 2, 0, 0, 0, *self.defaultColor, 0, 0,
        ])

        
        # construct indices
        self.indices = np.array([
            0, 1,
            0, 2,
            0, 4,
            1, 5,
            1, 3,
            2, 3,
            2, 6,
            3, 7,
            4, 5,
            4, 6,
            5, 7,
            6, 7
        ])

        # self.vertices should be an n x 11 array, where n is the number of mesh vertices
        # self.indices should be a flat array of length n*2

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems that don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)
        
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexTexture"),
                                  stride=11, offset=9, attribSize=2)


        self.vao.unbind()


