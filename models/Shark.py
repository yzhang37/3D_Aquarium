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
    - [ ] TODO: Mouth
    - [ ] TODO: Eye
    - [x] TODO: Body
    - [ ] TODO: First dorsal fin
    - [ ] TODO: Pectoral fin
    - [x] TODO: Tail
        - [ ] TODO: Caudal fin
        - [ ] TODO: Other parts
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

        if scale is not None:
            self.setDefaultScale(scale)

    def animationUpdate(self):
        # TODO: Animation
        pass

    def stepForward(self, components, tank_dimensions, vivarium):
        pass
