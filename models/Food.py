import typing
import random

from Component import CS680PA3
from Shapes import *
import ColorType as Ct
import numpy as np

import models.Utility as Utility
from models.Eye import Eye


class Food(CS680PA3):
    def __init__(self,
                 parent: Component,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: typing.Optional[typing.Iterator] = None):
        CS680PA3.__init__(self, position)

        self.basic_boundary_radius = 1
        self.basic_boundary_center = Point((0, 0, 0))
        self.basic_speed = 0.2
        self.food_chain_level = 1000
        self.step_vector = Point((0, -1, 0))

        food = Sphere(Point((0, 0, 0)), shaderProg, [1, 1, 1], random.choice([
            Utility.FishFood1Color, Utility.FishFood2Color, Utility.FishFood3Color, Utility.FishFood4Color
        ]), lowPoly=False)
        self.addChild(food)

        if scale is not None:
            self.setDefaultScale(scale)

    def stepForward(self,
                    components: List[Component],
                    tank_dimensions: List[float],
                    vivarium: Component):
        # if sink to the bottom, then remove it
        hit_test_pos = self.currentPos + self.boundary_center + self.step_vector * self.speed
        tank_height = tank_dimensions[1]
        if hit_test_pos.coords[1] < -tank_height / 2.162 + self.boundary_radius:
            return Point((0, 0, 0)), None
        else:
            return self.step_vector * self.speed, None
