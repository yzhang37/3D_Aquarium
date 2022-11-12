import typing
from typing import List, Tuple, Union, Optional
from Component import Component, CS680
from EnvironmentObject import EnvironmentObject
from Point import Point
from Shapes import *
import ColorType as Ct
import numpy as np

from models.Eye import Eye


class Shark(Component, EnvironmentObject, CS680):
    """
    Define how the shark model is written.
    - [x] Head
    - [x] Mouth
    - [x] Eye
    - [x] Body
    - [x] First dorsal fin
    - [x] Pectoral fin
    - [x] Lower Part
        - [x] Tail
        - [x] Caudal fin
    """

    def __init__(self,
                 parent: Component,
                 position: Point,
                 shaderProg,
                 scale: typing.Optional[typing.Iterator] = None):
        Component.__init__(self, position)
        CS680.__init__(self)

        # define the colors
        SHARK_GREY = Ct.ColorType(0.243, 0.275, 0.376)
        SHARK_LIGHTGREY = Ct.ColorType(0.302, 0.345, 0.470)

        # define the body of the shark

        # width, height, length
        body_size = np.array([0.9, 1.1, 1.4])
        body = Cube(Point((0, 0, 0)), shaderProg, body_size, SHARK_GREY)
        self.addChild(body)

        connect_part_size = [0.01, 0.01, 0.01]

        # body lower part
        # tails_part = []
        cur_size = body_size
        cur_par = body
        for i in range(3):
            new_size = cur_size * [0.8, 0.7, 0.6]
            new_pos = cur_size * [0, 0.1 / 2, -(1 + 0.6 - 0.1) / 2]

            conn_part = Cube(Point(new_pos), shaderProg, connect_part_size, SHARK_GREY)
            conn_part.setRotateExtent(conn_part.uAxis, 0, 0)
            conn_part.setRotateExtent(conn_part.vAxis, -20, 20)
            conn_part.setRotateExtent(conn_part.wAxis, 0, 0)

            new_tail = Cube(Point((0, 0, 0)), shaderProg, new_size, SHARK_GREY)

            self.rotationRegistry.append(CS680.RotWrap(conn_part, [0, 0.5, 0]))
            cur_par.addChild(conn_part)
            conn_part.addChild(new_tail)
            # tails_part.append(new_tail)

            cur_par = new_tail
            cur_size = new_size

        # define the Pectoral fin
        pectoral_fin_size = cur_size * [0.7, 0.7, 1.5]
        pectoral_fin_pos = cur_size * [0, 0, -(1 + 1.5) / 2]
        pectoral_fin = Cube(Point(pectoral_fin_pos), shaderProg, pectoral_fin_size, SHARK_GREY)
        cur_par.addChild(pectoral_fin)

        # define The Caudal fin
        caudal_fin1_size = pectoral_fin_size * [0.2, 0.6, 1.1]
        caudal_fin1_pos = pectoral_fin_size * [0, 0, 0.7]
        caudal_fin1 = Cone(Point(caudal_fin1_pos), shaderProg, caudal_fin1_size, SHARK_GREY)
        caudal_fin1.setCurrentAngle(180, caudal_fin1.vAxis)
        caudal_fin1.setCurrentAngle(30, caudal_fin1.uAxis)
        pectoral_fin.addChild(caudal_fin1)

        caudal_fin2_size = pectoral_fin_size * [0.2, 0.6, 0.8]
        caudal_fin2_pos = pectoral_fin_size * [0, 0, 0.7]
        caudal_fin2 = Cone(Point(caudal_fin2_pos), shaderProg, caudal_fin2_size, SHARK_LIGHTGREY)
        caudal_fin2.setCurrentAngle(180, caudal_fin2.vAxis)
        caudal_fin2.setCurrentAngle(-50, caudal_fin2.uAxis)
        pectoral_fin.addChild(caudal_fin2)

        # define the neck part of the shark
        neck_size = body_size * [0.8, 0.7, 0.5]
        neck_pos = body_size * [0, 0.1 / 2, (1 + 0.5 - 0.1) / 2]
        neck = Cube(Point(neck_pos), shaderProg, neck_size, SHARK_GREY)
        body.addChild(neck)

        # define the head and mouth
        head_size = neck_size * [0.8, 0.6, 1]
        head_pos = neck_size * [0, 0.1, (1 + 1 - 0.1) / 2]
        head = Cube(Point(head_pos), shaderProg, head_size, SHARK_GREY)
        neck.addChild(head)

        mouth_size = neck_size * [0.65, 0.15, 0.7]
        mouth_pos = neck_size * [0, -0.25, (1 + 0.7 - 0.1) / 2]
        mouth = Cube(Point(mouth_pos), shaderProg, mouth_size, SHARK_LIGHTGREY)
        mouth.setCurrentAngle(0, mouth.uAxis)
        mouth.setRotateExtent(mouth.uAxis, 0, 20)
        self.rotationRegistry.append(CS680.RotWrap(mouth, [0.1, 0, 0]))
        neck.addChild(mouth)

        # define the first dorsal
        first_dorsal = Shark.createFin(12, shaderProg, [1, 1.2, 1.2], SHARK_LIGHTGREY)
        first_dorsal.setDefaultPosition(Point((0, 0.5 - 0.1, 0)))
        body.addChild(first_dorsal)

        # define two Pectoral fin
        pectoral_1 = Shark.createFin(12, shaderProg, [1, 1, 0.6], SHARK_LIGHTGREY)
        pectoral_1.setDefaultPosition(Point((
            -(body_size[0] - 0.1) / 2,
            -(body_size[1] - 0.1) / 2,
            0))
        )
        pectoral_1.setDefaultAngle(140, pectoral_1.wAxis)
        pectoral_1.setRotateExtent(pectoral_1.wAxis, 120, 160)
        self.rotationRegistry.append(CS680.RotWrap(pectoral_1, [0, 0, 0.2]))
        body.addChild(pectoral_1)

        pectoral_2 = Shark.createFin(12, shaderProg, [1, 1, 0.6], SHARK_LIGHTGREY)
        pectoral_2.setDefaultPosition(Point((
            +(body_size[0] - 0.1) / 2,
            -(body_size[1] - 0.1) / 2,
            0))
        )
        pectoral_2.setDefaultAngle(-140, pectoral_2.wAxis)
        pectoral_2.setRotateExtent(pectoral_2.wAxis, -160, -120)
        self.rotationRegistry.append(CS680.RotWrap(pectoral_2, [0, 0, -0.2]))
        body.addChild(pectoral_2)

        # add the eye
        eye1 = Eye(self, Point((head_size[0] / 2, 0, 0)), shaderProg, [0.15, 0.15, 0.15])
        eye1.setDefaultAngle(90, eye1.vAxis)
        head.addChild(eye1)
        eye2 = Eye(self, Point((-head_size[0] / 2, 0, 0)), shaderProg, [0.15, 0.15, 0.15])
        eye2.setDefaultAngle(-90, eye2.vAxis)
        head.addChild(eye2)

        if scale is not None:
            self.setDefaultScale(scale)

    @staticmethod
    def createFin(nums: int, shaderProg,
                  scale: Union[List[float], Tuple[float, float, float], np.ndarray, None] = None,
                  color: Ct.ColorType = Ct.RED) -> Component:
        """
        Create a fin with the given number of segments.
        :param color: the color
        :param nums: Number of segments.
        :param shaderProg: Shader program to use.
        :param scale: Scale of the fin.
        :return: The fin.
        """
        fin_size = np.array([0.08, 0.12, 0.6])
        base_fin = Cube(Point((0, 0, 0)), shaderProg, fin_size, color)

        parent = base_fin
        for _ in range(nums - 1):
            new_fin = Cube(Point((0, 0, 0)), shaderProg, fin_size, color)
            new_fin.setCurrentAngle(-10, new_fin.uAxis)
            parent.addChild(new_fin)
            parent = new_fin

        if scale is not None:
            base_fin.setDefaultScale(scale)
        return base_fin

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

        # rotate animation
        # self.vAngle = (self.vAngle + 5) % 360
        # self.setCurrentPosition(self.defaultPos + Point((0, 0.5 * np.sin(self.vAngle / 180 * np.pi), 0)))

    def stepForward(self, components, tank_dimensions, vivarium):
        pass
