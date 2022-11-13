import typing


import ColorType as Ct
from Component import CS680PA3
from EnvironmentObject import EnvironmentObject
from Shapes import *
from models.Eye import Eye
import models.Utility


_headColor = Ct.PURPLE
_bodyColor = Ct.RED
_fin1Color = Ct.BLUE
_fin2Color = Ct.GREEN
_tail1Color = Ct.CYAN
_tail2Color = Ct.YELLOW


class Cod(Component, EnvironmentObject, CS680PA3):
    def __init__(self,
                 parent: Component,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: typing.Optional[typing.Iterator] = None,
                 headColor: Ct.ColorType = _headColor,
                 bodyColor: Ct.ColorType = _bodyColor,
                 fin1Color: Ct.ColorType = _fin1Color,
                 fin2Color: Ct.ColorType = _fin2Color,
                 tail1Color: Ct.ColorType = _tail1Color,
                 tail2Color: Ct.ColorType = _tail2Color):
        Component.__init__(self, position)
        CS680PA3.__init__(self)

        # define the head
        head_size = np.array([0.6, 0.9, 0.8])
        head = Cube(Point((0, 0, 0)), shaderProg, head_size, headColor)
        head.setRotateExtents(0, 0, -8, 8, 0, 0)
        self.rotationRegistry.append(CS680PA3.RotWrap(head, [0, 0.6, 0]))
        self.addChild(head)

        # define the body
        conn_size = np.array([0.01, 0.01, 0.01])
        conn1 = Cube(Point((0, 0, -head_size[2] / 2)), shaderProg, conn_size, headColor)
        head.addChild(conn1)
        conn1.setRotateExtents(0, 0, -4, 4, 0, 0)
        self.rotationRegistry.append(CS680PA3.RotWrap(conn1, [0, 0.2, 0]))

        body_size = np.array([0.6, 1, 1.9])
        body_pos = np.array([0, -0.1 / 2, -1.9 / 2])
        body = Cube(Point(body_pos), shaderProg, body_size, bodyColor)
        conn1.addChild(body)

        # define the eye
        eye_size = np.array([0.22, 0.22, 0.22])
        eye1 = Eye(self, Point(((head_size[0] - 0.15) / 2, 0, 0)), shaderProg, eye_size)
        eye1.setDefaultAngle(90, eye1.vAxis)
        head.addChild(eye1)
        eye2 = Eye(self, Point((-(head_size[0] - 0.15) / 2, 0, 0)), shaderProg, eye_size)
        eye2.setDefaultAngle(-90, eye2.vAxis)
        head.addChild(eye2)

        # Define the Pectoral Fin
        pec_fin1 = models.Utility.createFin(12, shaderProg, [1, 0.4, 0.4], fin2Color)
        pec_fin1.setDefaultPosition(Point((
            body_size[0] / 2, -0.2, (body_size[2] - 0.4) / 2,
        )))
        pec_fin1.setDefaultAngle(-135, pec_fin1.wAxis)
        pec_fin1.setRotateExtent(pec_fin1.wAxis, -150, -120)
        self.rotationRegistry.append(CS680PA3.RotWrap(pec_fin1, [0, 0, -1]))
        body.addChild(pec_fin1)
        pec_fin2 = models.Utility.createFin(12, shaderProg, [1, 0.4, 0.4], fin2Color)
        pec_fin2.setDefaultPosition(Point((
            -body_size[0] / 2, -0.2, (body_size[2] - 0.4) / 2,
        )))
        pec_fin2.setDefaultAngle(135, pec_fin2.wAxis)
        pec_fin2.setRotateExtent(pec_fin1.wAxis, 120, 150)
        self.rotationRegistry.append(CS680PA3.RotWrap(pec_fin2, [0, 0, 1]))
        body.addChild(pec_fin2)

        # Define the Dorsal Fins
        fin1_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.7]
        fin1 = Cube(Point((0, body_size[1] / 2, -0.1)), shaderProg, fin1_size, fin1Color)
        body.addChild(fin1)

        fin2_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.4]
        fin2 = Cube(Point((0, body_size[1] / 2, (body_size[2] - fin2_size[2]) / 2)), shaderProg, fin2_size, fin1Color)
        body.addChild(fin2)

        # Define the Anal Fins
        fin3_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.4]
        fin3 = Cube(Point((0, -body_size[1] / 2, -0.1)), shaderProg, fin3_size, fin1Color)
        body.addChild(fin3)

        # Define the Tails
        tail_conn = Cube(Point((0, 0, -body_size[2] / 2)), shaderProg, conn_size, bodyColor)
        body.addChild(tail_conn)
        tail_conn.setRotateExtents(0, 0, -36, 36, 0, 0)
        self.rotationRegistry.append(CS680PA3.RotWrap(tail_conn, [0, -2.7, 0]))
        tail_upper_conn = Sphere(Point((0, 0, 0)), shaderProg, conn_size, tail1Color, limb=True)
        tail_lower_conn = Sphere(Point((0, 0, 0)), shaderProg, conn_size, tail1Color, limb=True)
        tail_conn.addChild(tail_upper_conn)
        tail_conn.addChild(tail_lower_conn)
        tail_upper_conn.setDefaultAngle(24, tail_upper_conn.uAxis)
        tail_lower_conn.setDefaultAngle(-24, tail_lower_conn.uAxis)

        tail_size1 = body_size * [0.12, 0.25, 0.45]
        tail_size2 = body_size * [0.1, 0.25, 0.45]
        tail_upper = Cube(Point((0, 0, -tail_size1[2] / 2)), shaderProg, tail_size1, tail1Color)
        tail_upper_conn.addChild(tail_upper)
        tail_upper = Cube(Point((0, 0, -tail_size1[2] / 2)), shaderProg, tail_size2, tail2Color)
        tail_lower_conn.addChild(tail_upper)

    def animationUpdate(self):
        CS680PA3.animationUpdate(self)
        self.update()

    def stepForward(self,
                    components,
                    tank_dimensions,
                    vivarium):
        pass


class Salmon(Component, EnvironmentObject, CS680PA3):
    def __init__(self,
                 parent: Component,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: typing.Optional[typing.Iterator] = None,
                 headColor: Ct.ColorType = _headColor,
                 bodyColor: Ct.ColorType = _bodyColor,
                 fin1Color: Ct.ColorType = _fin1Color,
                 fin2Color: Ct.ColorType = _fin2Color,
                 tail1Color: Ct.ColorType = _tail1Color,
                 tail2Color: Ct.ColorType = _tail2Color):
        Component.__init__(self, position)
        CS680PA3.__init__(self)

        # define the head
        head_size = np.array([0.6, 0.9, 0.8])
        head = Cube(Point((0, 0, 0)), shaderProg, head_size, headColor)
        head.setRotateExtents(0, 0, -6, 6, 0, 0)
        self.rotationRegistry.append(CS680PA3.RotWrap(head, [0, 0.8, 0]))
        self.addChild(head)

        # define the body
        conn_size = np.array([0.01, 0.01, 0.01])
        body1_conn = Cube(Point((0, 0, -head_size[2] / 2)), shaderProg, conn_size, headColor)
        head.addChild(body1_conn)
        body1_conn.setRotateExtents(0, 0, -4, 4, 0, 0)
        self.rotationRegistry.append(CS680PA3.RotWrap(body1_conn, [0, -0.533, 0]))

        body_size = np.array([0.6, 1, 1.5])
        body1_pos = np.array([0, -0.1 / 2, -1.5 / 2])
        body1 = Cube(Point(body1_pos), shaderProg, body_size, bodyColor)
        body1_conn.addChild(body1)

        body2_conn = Cube(Point((0, 0, -body_size[2] / 2)), shaderProg, conn_size, headColor)
        body1.addChild(body2_conn)
        body2_conn.setRotateExtents(0, 0, -26, 26, 0, 0)
        self.rotationRegistry.append(CS680PA3.RotWrap(body2_conn, [0, 3.466, 0]))
        body2_pos = np.array([0, 0, -1.5 / 2])
        body2 = Cube(Point(body2_pos), shaderProg, body_size, bodyColor)
        body2_conn.addChild(body2)

        # define the eye
        eye_size = np.array([0.22, 0.22, 0.22])
        eye1 = Eye(self, Point(((head_size[0] - 0.15) / 2, 0, 0)), shaderProg, eye_size)
        eye1.setDefaultAngle(90, eye1.vAxis)
        head.addChild(eye1)
        eye2 = Eye(self, Point((-(head_size[0] - 0.15) / 2, 0, 0)), shaderProg, eye_size)
        eye2.setDefaultAngle(-90, eye2.vAxis)
        head.addChild(eye2)

        # Define the Pectoral Fin
        pec_fin1 = models.Utility.createFin(12, shaderProg, [1, 0.4, 0.4], fin2Color)
        pec_fin1.setDefaultPosition(Point((
            body_size[0] / 2, -0.2, (body_size[2] - 0.4) / 2,
        )))
        pec_fin1.setDefaultAngle(-135, pec_fin1.wAxis)
        pec_fin1.setRotateExtent(pec_fin1.wAxis, -150, -120)
        self.rotationRegistry.append(CS680PA3.RotWrap(pec_fin1, [0, 0, -1]))
        body1.addChild(pec_fin1)
        pec_fin2 = models.Utility.createFin(12, shaderProg, [1, 0.4, 0.4], fin2Color)
        pec_fin2.setDefaultPosition(Point((
            -body_size[0] / 2, -0.2, (body_size[2] - 0.4) / 2,
        )))
        pec_fin2.setDefaultAngle(135, pec_fin2.wAxis)
        pec_fin2.setRotateExtent(pec_fin1.wAxis, 120, 150)
        self.rotationRegistry.append(CS680PA3.RotWrap(pec_fin2, [0, 0, 1]))
        body1.addChild(pec_fin2)

        # Define the Dorsal Fins
        fin1_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.35]
        fin1 = Cube(Point((0, body_size[1] / 2, -(body_size[2] - fin1_size[2]) / 2)), shaderProg, fin1_size, fin1Color)
        body1.addChild(fin1)

        fin2_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.5]
        fin2 = Cube(Point((0, body_size[1] / 2, (body_size[2] - fin2_size[2]) / 2)), shaderProg, fin2_size, fin1Color)
        body2.addChild(fin2)

        # Define the Tails
        tail_conn = Cube(Point((0, 0, -body_size[2] / 2)), shaderProg, conn_size, bodyColor)
        body2.addChild(tail_conn)
        tail_conn.setRotateExtents(0, 0, -36, 36, 0, 0)
        self.rotationRegistry.append(CS680PA3.RotWrap(tail_conn, [0, 4.8, 0]))
        tail_upper_conn = Sphere(Point((0, 0, 0)), shaderProg, conn_size, tail1Color, limb=True)
        tail_lower_conn = Sphere(Point((0, 0, 0)), shaderProg, conn_size, tail1Color, limb=True)
        tail_conn.addChild(tail_upper_conn)
        tail_conn.addChild(tail_lower_conn)
        tail_upper_conn.setDefaultAngle(24, tail_upper_conn.uAxis)
        tail_lower_conn.setDefaultAngle(-24, tail_lower_conn.uAxis)

        tail_size1 = body_size * [0.12, 0.25, 0.75]
        tail_size2 = body_size * [0.1, 0.25, 0.75]
        tail_upper = Cube(Point((0, 0, -tail_size1[2] / 2)), shaderProg, tail_size1, tail1Color)
        tail_upper_conn.addChild(tail_upper)
        tail_upper = Cube(Point((0, 0, -tail_size1[2] / 2)), shaderProg, tail_size2, tail2Color)
        tail_lower_conn.addChild(tail_upper)

    def animationUpdate(self):
        CS680PA3.animationUpdate(self)
        self.update()

    def stepForward(self,
                    components,
                    tank_dimensions,
                    vivarium):
        pass
