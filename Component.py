"""
Define a class to easy manipulate Displayable Object
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1

Modified by Daniel Scrivener 07/2022
"""
import copy
import math
import os
from typing import *
from typing import Union

import numpy as np
from PIL import Image

import GLBuffer
from EnvironmentObject import EnvironmentObject
from GLProgram import GLProgram
from Point import Point
from ColorType import ColorType
from Displayable import Displayable
from Quaternion import Quaternion
from GLUtility import GLUtility
from GLBuffer import Texture

try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")


class Component:
    children = None  # list

    # the homogeneous transformation matrix for the current joint
    transformationMat = None

    # a instance of class which inherit from Displayable
    # if this class is used as skeleton, then keep this empty
    displayObj = None

    default_color = None  # ColorType
    current_color = None  # ColorType
    defaultPos = None  # Point
    currentPos = None  # Point

    uAxis = None  # list<float>(3): local basis u
    vAxis = None  # list<float>(3): local basis v
    wAxis = None  # list<float>(3): local basis w
    default_uAngle = 0.0
    uAngle = 0.0
    uRange = None  # list<float>(2)
    default_vAngle = 0.0
    vAngle = 0.0
    vRange = None  # list<float>(2)
    default_wAngle = 0.0
    wAngle = 0.0
    wRange = None  # list<float>(2)
    axisBucket = None

    defaultScaling = None
    currentScaling = None

    preRotationMat = None
    postRotationMat = None

    texture = None
    textureOn = False

    glUtility = None

    quat = None

    def __init__(self, position, display_obj=None):
        """
        Init Component

        :param position: This component's relative translation from the parent's origin to its origin
        :type position: Point
        :param display_obj: The displayable object to be assigned to this component. If no Displayable object is given, then this Component has nothing to draw
        :type display_obj: Displayable
        :rtype: None
        """
        # list variable initialization should be done here. Otherwise list variable in different instances will share
        # the same list
        self.children = []
        self.uAxis = Point([1, 0, 0])
        self.vAxis = Point([0, 1, 0])
        self.wAxis = Point([0, 0, 1])
        self.uRange = [-360, 360]
        self.vRange = [-360, 360]
        self.wRange = [-360, 360]
        self.axisBucket = [self.uAxis, self.vAxis, self.wAxis]
        self.glUtility = GLUtility()

        # Type Checking
        if not isinstance(position, Point):
            raise TypeError("Incorrect Position, it should be Point type")
        if not (isinstance(display_obj, Displayable) or isinstance(display_obj, type(None))):
            raise TypeError("displayObj can only accept None or Displayable object")

        # init some default values
        if not isinstance(display_obj, type(None)):
            self.default_color = display_obj.defaultColor
            self.current_color = display_obj.defaultColor
        else:
            self.default_color = np.array([1., 1., 1.])
            self.current_color = np.array([1., 1., 1.])
        self.defaultPos = position.copy()
        self.currentPos = position.copy()
        self.displayObj = display_obj
        self.defaultScaling = [1, 1, 1]
        self.currentScaling = [1, 1, 1]
        self.preRotationMat = np.identity(4)
        self.postRotationMat = np.identity(4)
        self.inRotation = np.identity(4)
        self.outRotation = np.identity(4)
        self.texture = Texture()

    def addChild(self, child):
        """
        Add a child to this Component child list.

        :param child: The child Component to be added
        :type child: Component
        :return: None
        """
        # Basic TypeChecking
        if not isinstance(child, Component):
            raise TypeError("Children of a Component can only be Component")
        # prevent the duplicate child to be added to the self.children
        if child not in self.children:
            self.children.append(child)

    def clear(self):
        """
        remove all children and destroy them
        """
        for c in self.children:
            c.clear()
            self.children.remove(c)
            del c

    def initialize(self):
        """
        Initialize this component and all its children
        This method is required if there is any parameter changed in the Component's Displayable objects

        :return: None
        """
        if isinstance(self.displayObj, Displayable):
            self.displayObj.initialize()

        for c in self.children:
            c.initialize()

        # use init value to generate transformation matrix for all children
        self.update()

    def draw(self, shaderProg: GLProgram):
        shaderProg.setMat4("modelMat", self.transformationMat.transpose())
        shaderProg.setVec3("currentColor", self.current_color)
        if isinstance(self.displayObj, Displayable):
            if self.textureOn:
                shaderProg.use()
                self.texture.bind(shaderProg.getUniformLocation("textureImage"))
            else:
                shaderProg.use()
                self.texture.unbind(shaderProg.getUniformLocation("textureImage"))
            self.displayObj.draw()

        for c in self.children:
            c.draw(shaderProg)

    def update(self, parentTransformationMat=None):
        """
        Apply translation, rotation and scaling to this component and all its children
        all matrix are stored in column-major order
        Must be called after any changes made to the instance

        :return: None
        """
        if parentTransformationMat is None:
            parentTransformationMat = np.identity(4)

        translationMat = self.glUtility.translate(*self.currentPos.getCoords(), False)

        # if self.quat is set, use the quaternion as your rotation matrix.
        # otherwise, use Euler angles with rotation extents, etc.
        # this means that quaternions will always override the settings for Euler angles

        if self.quat != None:
            rotationMatU = self.quat.toMatrix().transpose()
            rotationMatV = np.identity(4)
            rotationMatW = np.identity(4)
        else:
            rotationMatU = self.glUtility.rotate(self.uAngle, self.uAxis, False)
            rotationMatV = self.glUtility.rotate(self.vAngle, self.vAxis, False)
            rotationMatW = self.glUtility.rotate(self.wAngle, self.wAxis, False)
        scalingMat = self.glUtility.scale(*self.currentScaling, False)

        self.transformationMat = parentTransformationMat @ translationMat @ self.postRotationMat @ self.outRotation @ rotationMatU @ rotationMatV @ \
                                 rotationMatW @ self.inRotation @ self.preRotationMat @ scalingMat

        for c in self.children:
            c.update(self.transformationMat)

    def rotate(self, degree, axis):
        """
        rotate along axis. axis should be one of this object's uAxis, vAxis, wAxis

        :param degree: rotate degree, in degs
        :type degree: float
        :param axis: rotation axis. Axis must be uAxis, vAxis, or wAxis
        :type axis: enum(self.uAxis, self.vAxis, self.wAxis)
        :return: None
        """
        if axis not in self.axisBucket:
            raise TypeError("unknown axis for rotation")
        index = self.axisBucket.index(axis)
        if index == 0:
            self.uAngle = max(min(degree + self.uAngle, self.uRange[1]), self.uRange[0])
            # print(self.uAngle)
        elif index == 1:
            self.vAngle = max(min(degree + self.vAngle, self.vRange[1]), self.vRange[0])
            # print(self.vAngle)
        else:
            self.wAngle = max(min(degree + self.wAngle, self.wRange[1]), self.wRange[0])
            # print(self.wAngle)

    def reset(self, mode="all"):
        """
        Reset to default settings
        mode should be "color", "position", "angle", "scale", or "all"
        If mode is "all", then reset everything to default value.

        :param mode: the thing you want to reset
        :type mode: string
        """
        if mode in ["angle", "all"]:
            self.uAngle = self.default_uAngle
            self.vAngle = self.default_vAngle
            self.wAngle = self.default_wAngle
        if mode in ["position", "all"]:
            self.currentPos = self.defaultPos
        if mode in ["scale", "all"]:
            self.setCurrentScale(self.defaultScaling, check=False)
        if mode in ["rotationAxis", "all"]:
            self.setPreRotation(np.identity(4, dtype=np.double))
            self.setU([1, 0, 0])
            self.setV([0, 1, 0])
            self.setW([0, 0, 1])

    def setRotateExtents(self, uMin, uMax, vMin, vMax, wMin, wMax):
        """
        Factory function to set all the rotation extents
        """
        self.setRotateExtent(self.uAxis, uMin, uMax)
        self.setRotateExtent(self.vAxis, vMin, vMax)
        self.setRotateExtent(self.wAxis, wMin, wMax)

    def setRotateExtent(self, axis, minDeg=None, maxDeg=None):
        """
        set rotate extent range for axis rotation

        :param axis: rotation axis. Axis must be uAxis, vAxis, or wAxis
        :param minDeg: rotation's lower limit
        :param maxDeg: rotation's upper limit
        :return: None
        """
        if axis not in self.axisBucket:
            raise TypeError("unknown axis for rotation extent setting")
        # Find out which axis to set
        index = self.axisBucket.index(axis)
        if index == 0:
            r = self.uRange
        elif index == 1:
            r = self.vRange
        else:
            r = self.wRange

        # Update range if any value given
        if not isinstance(minDeg, type(None)):
            iD = minDeg
        else:
            iD = r[0]
        if not isinstance(maxDeg, type(None)):
            aD = maxDeg
        else:
            aD = r[1]
        if iD > aD:
            print("Warning: You shouldn't see this. This means you set minDeg greater than maxDeg. ")
            print("At axis: ", ["u", "v", "w"][index], "   min & max Deg given: ", iD, aD)
            t = iD
            iD = aD
            aD = t
        r[0] = iD
        r[1] = aD

    @staticmethod
    def clamp(v, low_bound, up_bound):
        result = v
        if not isinstance(up_bound, type(None)):
            result = min(result, up_bound)
        if not isinstance(low_bound, type(None)):
            result = max(result, low_bound)
        return result

    def setTexture(self, shaderProg: GLProgram, imgFilePath, textureOn=True):
        # apply texturek
        if not os.path.isfile(imgFilePath):
            raise TypeError("Image File doesn't exist")

        shaderProg.use()
        texture_image = Image.open(imgFilePath).convert("RGB")
        texture_image = np.array(texture_image, dtype=np.uint8)
        self.texture.setTextureImage(texture_image)
        self.textureOn = textureOn

    def setCurrentAngle(self, angle, axis):
        if axis not in self.axisBucket:
            raise TypeError("unknown axis for rotation")
        index = self.axisBucket.index(axis)

        if index == 0:
            self.uAngle = self.clamp(angle, self.uRange[0], self.uRange[1])
        elif index == 1:
            self.vAngle = self.clamp(angle, self.vRange[0], self.vRange[1])
        else:
            self.wAngle = self.clamp(angle, self.wRange[0], self.wRange[1])
        self.update()

    def setDefaultAngle(self, angle, axis):
        """
        Set default angle for rotation along every axis
        :param axis: rotation axis. Axis must be uAxis, vAxis, or wAxis
        :param angle: the default deg
        :return: None
        """
        if axis not in self.axisBucket:
            raise TypeError("unknown axis for rotation")
        index = self.axisBucket.index(axis)
        if index == 0:
            self.default_uAngle = angle
            self.uAngle = angle
        elif index == 1:
            self.default_vAngle = angle
            self.vAngle = angle
        else:
            self.default_wAngle = angle
            self.wAngle = angle

    def setDefaultPosition(self, pos):
        """
        Set default relative translation from parent
        :param pos: default relative translation from parent to this component
        :type pos: Point
        :return:
        """
        if not isinstance(pos, Point):
            raise TypeError("pos should have type Point")
        self.defaultPos = pos.copy()
        self.currentPos = copy.deepcopy(self.defaultPos)

    def setDefaultScale(self, scale):
        """
        Set default scaling along three axes
        :param scale: default scaling along three axes
        :return: None
        """
        if not isinstance(scale, list) and not isinstance(scale, tuple) and not isinstance(scale, np.ndarray):
            raise TypeError("default scale should be list or tuple or np.ndarray")
        if isinstance(scale, np.ndarray):
            if len(scale.shape) != 1 or scale.shape[0] != 3:
                raise TypeError("default scale should consists of scaling on 3 axis")
            scale = scale.tolist()
        elif len(scale) != 3:
            raise TypeError("default scale should consists of scaling on 3 axis")
        self.defaultScaling = copy.deepcopy(scale)
        self.setCurrentScale(self.defaultScaling, check=False)

    def setDefaultColor(self, color):
        """
        Default color for this component
        :param color: color for this component
        :type color: ColorType
        :return: None
        """
        if not isinstance(color, ColorType):
            raise TypeError("color should have type ColorType")
        self.default_color = np.array(color.copy().getRGB())
        self.current_color = copy.deepcopy(self.default_color)

    def setCurrentPosition(self, pos):
        """
        Set relative translation from parent
        :param pos: relative translation from parent to this component
        :type pos: Point
        :return:
        """
        if not isinstance(pos, Point):
            raise TypeError("pos should have type Point")
        self.currentPos = pos.copy()
        self.update()

    def setCurrentColor(self, color):
        """
        color for this component
        :param color: color for this component
        :type color: ColorType
        :return: None
        """
        if isinstance(color, ColorType):
            self.current_color = np.array(color.copy().getRGB())
        elif (isinstance(color, tuple) or isinstance(color, list)) and len(color) == 3:
            self.current_color = np.array(color)
        elif (isinstance(color, np.ndarray)):
            self.current_color = color
        else:
            raise TypeError(f"color should have type ColorType, Tuple, or list, not {type(color)}")

    def setCurrentScale(self, scale, check: bool = True):
        """
        Set scaling along three axes
        :param check:
        :param scale: scaling along three axes
        :return: None
        """
        if check:
            if not isinstance(scale, list) and not isinstance(scale, tuple):
                raise TypeError("current scale should be list or tuple")
            if len(scale) != 3:
                raise TypeError("current scale should consists of scaling on 3 axis")
            if min(scale) != max(scale):
                raise ValueError("Component only accept uniform scaling")
        self.currentScaling = copy.deepcopy(scale)
        self.update()

    def setPreRotation(self, rotation_matrix=None):
        """
        If you want the component to start with a different facing direction before all the following transformation,
        then set a pre-rotation matrix

        :param rotation_matrix: a 4x4 homogenuous transformation matrix
        :type rotation_matrix: numpy.ndarray
        """
        if isinstance(rotation_matrix, np.ndarray):
            self.preRotationMat = rotation_matrix

    def setPostRotation(self, rotation_matrix=None):
        """
        Set transform to be applied after rotation

        :param rotation_matrix: a 4x4 homogenuous transformation matrix
        :type rotation_matrix: numpy.ndarray
        """
        if isinstance(rotation_matrix, np.ndarray):
            self.postRotationMat = rotation_matrix

    def u(self):
        return self.uAxis.copy()

    def v(self):
        return self.vAxis.copy()

    def w(self):
        return self.wAxis.copy()

    def setU(self, u):
        if len(u) != len(self.uAxis):
            raise TypeError("axis should have the same size as the current one")
        for i in range(len(u)):
            self.uAxis[i] = u[i]

    def setV(self, v):
        if len(v) != len(self.vAxis):
            raise TypeError("axis should have the same size as the current one")
        for i in range(len(v)):
            self.vAxis[i] = v[i]

    def setW(self, w):
        if len(w) != len(self.wAxis):
            raise TypeError("axis should have the same size as the current one")
        for i in range(len(w)):
            self.wAxis[i] = w[i]

    def setQuaternion(self, q):
        """ sets a quaternion for rotation """
        if not isinstance(q, Quaternion):
            raise TypeError("q must be of type Quaternion")
        self.quat = q

    def clearQuaternion(self):
        """ clears the existing quaternion """
        self.quat = None


def f(x: np.ndarray) -> np.ndarray:
    return 1 / np.exp(x ** 2)


def d_f(x: np.ndarray) -> np.ndarray:
    return -2 * x * np.exp(-x ** 2)


def unit_v(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


class CS680PA3(Component, EnvironmentObject):
    class RotWrap:
        comp: Component = None
        rotation_speed: Union[List[float], Tuple[float, float, float]] = None

        def __init__(self,
                     comp: Component,
                     rotation_speed: Union[List[float], Tuple[float, float, float]]):
            self.comp = comp
            self.rotation_speed = rotation_speed

    componentDict: Dict[str, Component] = None
    # Rotation handling registry to record information about
    # each part and the speed at which it needs to be rotated.
    rotationRegistry: List[RotWrap] = None

    # define the relative boundary of each component
    basic_boundary_radius: float = 1.0

    # define the center within the boundary of each component
    basic_boundary_center: Point = None

    # define the speed of the creature
    basic_speed: float = 0.5

    # define the current step orientation of the creature
    step_vector: Point = None

    # define the food chain level, the smaller number represents the higher level
    food_chain_level: int = 0

    __cur_max_scale: float = 1.0
    __boundary_center: Point = None

    def __init__(self, position):
        Component.__init__(self, position)
        self.componentDict = {}
        self.rotationRegistry = []
        self.basic_boundary_center = Point((0, 0, 0))
        self.__boundary_center = self.basic_boundary_center
        self.step_vector = Point(np.random.normal(0, 1, 3)).normalize()

    def setCurrentScale(self, scale, check: bool = True):
        super().setCurrentScale(scale, check)
        self.__cur_max_scale = max(scale)
        self.__boundary_center = Point(self.basic_boundary_center.coords * scale)

    @property
    def boundary_radius(self) -> float:
        return self.basic_boundary_radius * self.__cur_max_scale

    @property
    def speed(self) -> float:
        return self.basic_speed * self.__cur_max_scale

    @property
    def boundary_center(self) -> Point:
        return self.__boundary_center

    def animationUpdate(self):
        for i, wrap in enumerate(self.rotationRegistry):
            comp = wrap.comp
            speed = wrap.rotation_speed
            comp.rotate(speed[0], comp.uAxis)
            comp.rotate(speed[1], comp.vAxis)
            comp.rotate(speed[2], comp.wAxis)
            # rotation reached the limit
            if comp.uAngle in comp.uRange:
                speed[0] *= -1
            if comp.vAngle in comp.vRange:
                speed[1] *= -1
            if comp.wAngle in comp.wRange:
                speed[2] *= -1
        self.update()

    def stepForward(self,
                    components: List[Component],
                    tank_dimensions: List[float],
                    vivarium: Component):
        # reflect when the object is near hit the tank.
        # this is the highest priority. If hit, we no longer do any more test.
        tank_dimensions = np.array(tank_dimensions)
        hit = False
        hit_test_pos = self.currentPos + self.boundary_center + self.step_vector * self.speed
        for dim in range(3):
            if hit_test_pos.coords[dim] > tank_dimensions[dim] / 2 - self.boundary_radius or \
                    hit_test_pos.coords[dim] < -tank_dimensions[dim] / 2 + self.boundary_radius:
                self.step_vector.coords[dim] *= -1
                hit = True
        if hit:
            # when actually do translation, we should not add the boundary_center inside it!
            return self.step_vector * self.speed

        overall_velocity = np.zeros(3)
        # we add the potential functions for the walls, to avoid objects run towards the tank walls
        wall_drv_step = d_f(tank_dimensions / 2 - hit_test_pos.coords) + d_f(tank_dimensions / 2 + hit_test_pos.coords)
        overall_velocity -= wall_drv_step * 0.002

        # now compute the potential functions between objects
        for comp in components:
            if comp is not self and isinstance(comp, CS680PA3):
                # this is another creature
                new_object_test_pos = comp.currentPos + comp.boundary_center + comp.step_vector * comp.speed

                # chasing and escaping
                if self.food_chain_level < comp.food_chain_level:
                    # chasing
                    overall_velocity += d_f(hit_test_pos.coords - new_object_test_pos.coords) * 0.02
                elif self.food_chain_level > comp.food_chain_level:
                    # escaping
                    overall_velocity -= d_f(hit_test_pos.coords - new_object_test_pos.coords) * 0.02

        self.step_vector += Point(overall_velocity)
        self.step_vector = self.step_vector.normalize()

        # the object will move towards its own step_vector
        return self.step_vector * self.speed
