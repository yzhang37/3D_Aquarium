import typing
from Component import Component
from EnvironmentObject import EnvironmentObject
from Point import Point
from Shapes import *
import ColorType as Ct
import numpy as np


class Shark(Component, EnvironmentObject):
    """
    Define how the shark model is written.
    - [ ] TODO: Head
    - [ ] TODO: Mouth
    - [ ] TODO: Eye
    - [x] TODO: Body
    - [ ] TODO: First dorsal fin
    - [x] TODO: Tail
        - [x] TODO: Pectoral fin
        - [x] TODO: Caudal fin
        - [x] TODO: Other parts
    """

    def __init__(self,
                 parent: Component,
                 position: Point,
                 shaderProg,
                 scale: typing.Optional[typing.Iterator] = None):
        super().__init__(position)

        # define the colors
        SHARK_GREY = Ct.ColorType(0.243, 0.275, 0.376)

        # define the body of the shark

        # width, height, length
        body_size = np.array([0.9, 1.1, 1.4])
        body = Cube(Point((0, 0, 0)), shaderProg, body_size, SHARK_GREY)
        self.addChild(body)

        tails_part = []
        cur_size = body_size
        cur_par = body
        for i in range(3):
            new_size = cur_size * [0.8, 0.7, 0.6]
            new_pos = cur_size * [0, 0.1 / 2, -(1 + 0.6 - 0.1) / 2]
            new_tail = Cube(Point(new_pos), shaderProg, new_size, SHARK_GREY)
            cur_par.addChild(new_tail)
            tails_part.append(new_tail)
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
        caudal_fin2 = Cone(Point(caudal_fin2_pos), shaderProg, caudal_fin2_size, SHARK_GREY)
        caudal_fin2.setCurrentAngle(180, caudal_fin2.vAxis)
        caudal_fin2.setCurrentAngle(-50, caudal_fin2.uAxis)
        pectoral_fin.addChild(caudal_fin2)

        if scale is not None:
            self.setDefaultScale(scale)

    def animationUpdate(self):
        # TODO: Animation
        pass

    def stepForward(self, components, tank_dimensions, vivarium):
        pass
