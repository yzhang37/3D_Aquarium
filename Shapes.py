"""
Implements four geometric primitives (Sphere, Cube, Cone, Cylinder) using the DisplayableMesh class

Modified by Daniel Scrivener 07/2022
"""

from time import time_ns
from typing import Union, List, Tuple

from collada import *
from DisplayableMesh import DisplayableMesh
from Component import Component
import GLUtility
import ColorType
import numpy as np

from GLProgram import GLProgram
from Point import Point


def getVertexData(filename):

    colladaData = Collada(filename)

    # generate vertices from model data
    # also generate indices

    geo = colladaData.geometries[0]
    tridata = geo.primitives[0]
    trilist = list(tridata)

    # construct vertex list
    vertices = np.array([])
    
    for vert in tridata.vertex:
        vert = np.concatenate((vert, [0.,0.,0.]), axis=0) # empty normals
        vert = np.concatenate((vert, [0.,0.,0.]), axis=0) # color
        vert = np.concatenate((vert, [0.,0.]), axis=0) # empty UV
        vertices = np.append(vertices, vert)

    # construct indices
    indices = np.array([])

    for tri in trilist:
        indices = np.append(indices, tri.indices)

    return (vertices, indices)


class Shape(Component):
    vertexData = None
    indexData = None
    mesh = None

    def __init__(self,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: Union[List[float], Tuple[float, float, float], np.ndarray],
                 vertexData,
                 indexData,
                 color: ColorType.ColorType = ColorType.YELLOW):
        """
        :param position: location of the object
        :type position: Point
        :param shaderProg: compiled shader program
        :type shaderProg: GLProgram
        :param scale: set of three scale factors to be applied to each vertex
        :type scale: list or tuple
        :param pathname: .dae file to import
        :type pathname: string
        :param color: vertex color to be applied uniformly
        :type color: ColorType
        :param limb: sets the rotation behavior of the object. if true, rotations happen "at the joint" \
            rather than the object's center
        :type limb: boolean
        """
        self.mesh = DisplayableMesh(shaderProg, scale, vertexData, indexData, color)
        super(Shape, self).__init__(position, self.mesh)


class Cone(Shape):

    pathname = "assets/cone0.dae"
    pathnameLP = "assets/coneLP.dae"
    data = getVertexData(pathname)
    dataLP = getVertexData(pathnameLP)
    vertices = data[0]
    verticesLP = dataLP[0]
    indices = data[1]
    indicesLP = dataLP[1]

    def __init__(self,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: Union[List[float], Tuple[float, float, float], np.ndarray],
                 color: ColorType.ColorType = ColorType.YELLOW,
                 lowPoly=True):
        """
        :param position: location of the object
        :type position: Point
        :param shaderProg: compiled shader program
        :type shaderProg: GLProgram
        :param scale: set of three scale factors to be applied to each vertex
        :type scale: list or tuple
        :param color: vertex color to be applied uniformly
        :type color: ColorType
        """
        if lowPoly:
            super(Cone, self).__init__(position, shaderProg, scale, self.verticesLP.copy(), self.indicesLP.copy(), color)
        else:
            super(Cone, self).__init__(position, shaderProg, scale, self.vertices.copy(), self.indices.copy(), color)

        # translate object by -z extent of the new component so that rotations occur @ the joint
        # rather than around the object's true center
        glutility = GLUtility.GLUtility()
        tIn = glutility.translate(0, 0, scale[2], False)
        tOut = glutility.translate(0, 0, -scale[2], False)
        self.inRotation = tIn
        self.outRotation = tOut


class Cube(Shape):

    pathname = "assets/cube0.dae"
    data = getVertexData(pathname)
    vertices = data[0]
    indices = data[1]

    def __init__(self,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: Union[List[float], Tuple[float, float, float], np.ndarray],
                 color: ColorType.ColorType = ColorType.RED):
        """
        :param position: location of the object
        :type position: Point
        :param shaderProg: compiled shader program
        :type shaderProg: GLProgram
        :param scale: set of three scale factors to be applied to each vertex
        :type scale: list or tuple
        :param color: vertex color to be applied uniformly
        :type color: ColorType
        """
        super(Cube, self).__init__(position, shaderProg, scale, self.vertices.copy(), self.indices.copy(), color)
        # translate object by -z extent of the new component so that rotations occur @ the joint
        # rather than around the object's true center
        glutility = GLUtility.GLUtility()
        tIn = glutility.translate(0, 0, scale[2] / 2, False)
        tOut = glutility.translate(0, 0, -scale[2] / 2, False)
        self.inRotation = tIn
        self.outRotation = tOut


class Cylinder(Shape):

    pathname = "assets/cylinder0.dae"
    pathnameLP = "assets/cylinderLP.dae"
    data = getVertexData(pathname)
    dataLP = getVertexData(pathnameLP)
    vertices = data[0]
    verticesLP = dataLP[0]
    indices = data[1]
    indicesLP = dataLP[1]

    def __init__(self,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: Union[List[float], Tuple[float, float, float], np.ndarray],
                 color: ColorType.ColorType = ColorType.GREEN,
                 lowPoly=True):
        """
        :param position: location of the object
        :type position: Point
        :param shaderProg: compiled shader program
        :type shaderProg: GLProgram
        :param scale: set of three scale factors to be applied to each vertex
        :type scale: list or tuple
        :param color: vertex color to be applied uniformly
        :type color: ColorType
        """
        if lowPoly:
            super(Cylinder, self).__init__(position, shaderProg, scale, self.verticesLP.copy(), self.indicesLP.copy(), color)
        else:
            super(Cylinder, self).__init__(position, shaderProg, scale, self.vertices.copy(), self.indices.copy(), color)
        # translate object by -z extent of the new component so that rotations occur @ the joint
        # rather than around the object's true center
        glutility = GLUtility.GLUtility()
        tIn = glutility.translate(0, 0, scale[2], False)
        tOut = glutility.translate(0, 0, -scale[2], False)
        self.inRotation = tIn
        self.outRotation = tOut


class Sphere(Shape):

    pathname = "assets/sphere0.dae"
    pathnameLP = "assets/sphereLP.dae"
    data = getVertexData(pathname)
    dataLP = getVertexData(pathnameLP)
    vertices = data[0]
    verticesLP = dataLP[0]
    indices = data[1]
    indicesLP = dataLP[1]

    def __init__(self,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: Union[List[float], Tuple[float, float, float], np.ndarray],
                 color: ColorType.ColorType = ColorType.BLUE,
                 limb=True,
                 lowPoly=True):
        """
        :param position: location of the object
        :type position: Point
        :param shaderProg: compiled shader program
        :type shaderProg: GLProgram
        :param scale: set of three scale factors to be applied to each vertex
        :type scale: list or tuple
        :param color: vertex color to be applied uniformly
        :type color: ColorType
        :param limb: sets the rotation behavior of the object. if true, rotations happen "at the joint" \
            rather than the object's center.
            Set this to False for eyes or other ball joints.
        :type limb: boolean
        """
        if lowPoly:
            super(Sphere, self).__init__(position, shaderProg, scale, self.verticesLP.copy(), self.indicesLP.copy(), color)
        else:
            super(Sphere, self).__init__(position, shaderProg, scale, self.vertices.copy(), self.indices.copy(), color)
        # translate object by -z extent of the new component so that rotations occur @ the joint
        # rather than around the object's true center   
        glutility = GLUtility.GLUtility()
        if limb:
            tIn = glutility.translate(0, 0, scale[2], False)
            tOut = glutility.translate(0, 0, -scale[2], False)
        else:
            tIn = np.identity(4)
            tOut = np.identity(4)
        self.inRotation = tIn
        self.outRotation = tOut