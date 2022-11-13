import typing

import numpy as np

import ColorType as Ct
from Component import Component, CS680
from EnvironmentObject import EnvironmentObject
from GLProgram import GLProgram
from Point import Point
from Shapes import *
from models.Eye import Eye


class Cod(Component, EnvironmentObject, CS680):
    def __init__(self,
                 parent: Component,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: typing.Optional[typing.Iterator] = None,
                 headColor: Ct.ColorType = Ct.PURPLE,
                 bodyColor: Ct.ColorType = Ct.RED,
                 finColor: Ct.ColorType = Ct.BLUE,
                 tailColor: Ct.ColorType = Ct.CYAN):
        Component.__init__(self, position)
        CS680.__init__(self)

        # define the head
        head_size = np.array([0.6, 0.9, 0.8])
        head = Cube(Point((0, 0, 0)), shaderProg, head_size, headColor)
        head.setRotateExtents(0, 0, -8, 8, 0, 0)
        self.rotationRegistry.append(CS680.RotWrap(head, [0, 0.6, 0]))
        self.addChild(head)

        # define the body
        conn_size = np.array([0.01, 0.01, 0.01])
        conn1 = Cube(Point((0, 0, -head_size[2] / 2)), shaderProg, conn_size, headColor)
        head.addChild(conn1)
        conn1.setRotateExtents(0, 0, -4, 4, 0, 0)
        self.rotationRegistry.append(CS680.RotWrap(conn1, [0, 0.2, 0]))

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

        # TODO: Define the Pectoral Fin

        # Define the Dorsal Fins
        fin1_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.7]
        fin1 = Cube(Point((0, body_size[1] / 2, -0.1)), shaderProg, fin1_size, finColor)
        body.addChild(fin1)

        fin2_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.4]
        fin2 = Cube(Point((0, body_size[1] / 2, (body_size[2] - fin2_size[2]) / 2)), shaderProg, fin2_size, finColor)
        body.addChild(fin2)

        # Define the Anal Fins
        fin3_size = body_size * [0.1, 0, 0] + [0, 0.45, 0.4]
        fin3 = Cube(Point((0, -body_size[1] / 2, -0.1)), shaderProg, fin3_size, finColor)
        body.addChild(fin3)

        # Define the Tails
        tail_conn = Cube(Point((0, 0, -body_size[2] / 2)), shaderProg, conn_size, bodyColor)
        body.addChild(tail_conn)
        tail_conn.setRotateExtents(0, 0, -36, 36, 0, 0)
        self.rotationRegistry.append(CS680.RotWrap(tail_conn, [0, -2.7, 0]))
        tail_upper_conn = Sphere(Point((0, 0, 0)), shaderProg, conn_size, tailColor, limb=True)
        tail_lower_conn = Sphere(Point((0, 0, 0)), shaderProg, conn_size, tailColor, limb=True)
        tail_conn.addChild(tail_upper_conn)
        tail_conn.addChild(tail_lower_conn)
        tail_upper_conn.setDefaultAngle(24, tail_upper_conn.uAxis)
        tail_lower_conn.setDefaultAngle(-24, tail_lower_conn.uAxis)

        tail_size = body_size * [0.1, 0.25, 0.45]
        tail_upper = Cube(Point((0, 0, -tail_size[2] / 2)), shaderProg, tail_size, tailColor)
        tail_upper_conn.addChild(tail_upper)
        tail_upper = Cube(Point((0, 0, -tail_size[2] / 2)), shaderProg, tail_size, tailColor)
        tail_lower_conn.addChild(tail_upper)

    def animationUpdate(self):
        doRotation = True
        if not doRotation:
            return

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

        # rotate animation
        self.update()

    def stepForward(self,
                    components,
                    tank_dimensions,
                    vivarium):
        pass


class Salmon:
    pass
