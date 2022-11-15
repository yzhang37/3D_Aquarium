"""
All creatures should be added to Vivarium. Some help functions to add/remove creature are defined here.
Created on 20181028

:author: micou(Zezhou Sun)
:version: 2021.1.1

modified by Daniel Scrivener
"""
import typing

import numpy as np
from Point import Point
from Component import Component, CS680PA3
from ModelTank import Tank
from EnvironmentObject import EnvironmentObject
from models import Shark, Salmon, Cod, Food


class Vivarium(Component):
    """
    The Vivarium for our animation
    """
    components = None  # List
    parent = None  # class that have current context
    tank = None
    tank_dimensions = None

    ## BONUS 5(for CS680 Students): Feed your creature
    # Requirements:
    #   Add chunks of food to the vivarium which can be eaten by your creatures.
    #     * When ‘f’ is pressed, have a food particle be generated at random within the vivarium.
    #     * Be sure to draw the food on the screen with an additional model. It should drop slowly to the bottom of
    #     the vivarium and remain there within the tank until eaten.
    #     * The food should disappear once it has been eaten. Food is eaten by the first creature that touches it.

    _fish_size = np.ones(3) * 0.1
    _food_size = np.ones(3) * 0.07

    def __init__(self, parent, shaderProg):
        self.parent = parent
        self.shaderProg = shaderProg

        self.tank_dimensions = [4, 4, 4]
        tank = Tank(Point((0, 0, 0)), shaderProg, self.tank_dimensions)
        super(Vivarium, self).__init__(Point((0, 0, 0)))

        # Build relationship
        self.addChild(tank)
        self.tank = tank

        # Store all components in one list, for us to access them later
        self.components = [tank]

        # add one shark as the predator
        shark_size = np.array([1, 1, 1]) * 0.25
        self.addNewObjInTank(Shark(self, Point((0, 0, 0)), shaderProg, shark_size))
        # add 4 fishes
        for _ in range(2):
            self.addFish()

    @staticmethod
    def init_fish_pos():
        return np.random.uniform(low=-1.5, high=1.5, size=(3,))

    @staticmethod
    def init_fish_food_pos():
        return np.array([
            np.random.uniform(low=-1.2, high=1.2),
            np.random.uniform(low=1, high=1.8),
            np.random.uniform(low=-1.2, high=1.2)
        ])

    def addFish(self):
        salmon = Salmon(self, Point(self.init_fish_pos()), self.shaderProg, self._fish_size)
        salmon.initialize()
        self.addNewObjInTank(salmon)
        cod = Cod(self, Point(self.init_fish_pos()), self.shaderProg, self._fish_size)
        cod.initialize()
        self.addNewObjInTank(cod)

    def addFood(self):
        food = Food(self, Point(self.init_fish_food_pos()), self.shaderProg, self._food_size)
        food.initialize()
        self.addNewObjInTank(food)

    def animationUpdate(self):
        """
        Update all creatures in vivarium
        """
        update_list = []
        removed_item = set()

        # first iterate all the objects
        for c in self.components:
            if isinstance(c, EnvironmentObject) and c not in removed_item:
                step, rem_list = c.stepForward(self.components, self.tank_dimensions, self)
                update_list.append((c, step))
                if rem_list is not None:
                    removed_item.update(rem_list)

        # then update and remove the objects
        for (c, step) in update_list:
            if c in removed_item:
                self.delObjInTank(c)
                continue
            c.animationUpdate()
            c.currentPos += step
            c.rotateDirection()

        self.update()

    def delObjInTank(self, obj):
        if isinstance(obj, Component):
            self.tank.children.remove(obj)
            self.components.remove(obj)
            del obj

    def _sort_cs680(self, component: Component) -> int:
        if isinstance(component, CS680PA3):
            return -component.food_chain_level
        else:
            return 1000000

    def addNewObjInTank(self, newComponent):
        if isinstance(newComponent, Component):
            self.tank.addChild(newComponent)
            self.components.append(newComponent)

            # sort the components each time when a new one is added
            self.components.sort(key=self._sort_cs680)
        if isinstance(newComponent, EnvironmentObject):
            # add environment components list reference to this new object's
            newComponent.env_obj_list = self.components
