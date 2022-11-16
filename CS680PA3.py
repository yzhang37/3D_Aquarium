from typing import Union, List, Tuple, Dict

import numpy as np

from Component import Component
from EnvironmentObject import EnvironmentObject
from Point import Point
from Quaternion import Quaternion


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

    # define the current orientation of the creature
    orientation: Point = None

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
        self.orientation = Point((0, 0, 1))
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
        hit_test_pos = self.currentPos + self.boundary_center + self.step_vector * self.speed
        tank_dimensions = np.array(tank_dimensions)

        hit = False
        for dim in range(3):
            if hit_test_pos.coords[dim] > tank_dimensions[dim] / 2 - self.boundary_radius or \
                    hit_test_pos.coords[dim] < -tank_dimensions[dim] / 2 + self.boundary_radius:
                self.step_vector.coords[dim] *= -1
                hit = True
        if hit:
            # when actually do translation, we should not add the boundary_center inside it!
            return self.step_vector * self.speed, None

        overall_velocity = np.zeros(3)
        # we add the potential functions for the walls, to avoid objects run towards the tank walls
        wall_drv_step = d_upper_bound(30, 3.4012, hit_test_pos.coords - tank_dimensions / 2.162)
        wall_drv_step += d_lower_bound(30, 3.4012, hit_test_pos.coords + tank_dimensions / 2.162)
        overall_velocity -= wall_drv_step * 0.09

        # now compute the potential functions between objects
        most_junior_level = float('-inf')
        item_to_delete = []

        for comp in components:
            if comp is not self and isinstance(comp, CS680PA3):
                most_junior_level = max(most_junior_level, comp.food_chain_level)

                # this is another creature
                new_object_test_pos = comp.currentPos + comp.boundary_center + comp.step_vector * comp.speed
                dist_vec = new_object_test_pos - hit_test_pos
                dist = np.sqrt(np.sum(dist_vec.coords ** 2))

                # Collision
                if dist < self.boundary_radius + comp.boundary_radius:
                    # if the food chain level is equal:
                    if self.food_chain_level == comp.food_chain_level:
                        overall_velocity += self.step_vector.reflect(dist_vec.normalize()).coords * 0.3
                    elif self.food_chain_level < comp.food_chain_level == most_junior_level:
                        # only can kill the creature when the food is the least level
                        # each time it can only kill one creature
                        item_to_delete.append(comp)

                # boids movement
                if self.food_chain_level == comp.food_chain_level:
                    # mimic universal gravity
                    overall_velocity -= d_gravity(
                        0.5 * 3 * self.boundary_radius, 0.5,
                        hit_test_pos.coords - new_object_test_pos.coords) * 0.01
                elif self.food_chain_level < comp.food_chain_level:
                    # chasing
                    if comp.food_chain_level == most_junior_level:
                        overall_velocity += d_dist(hit_test_pos.coords - new_object_test_pos.coords) * 0.05
                elif self.food_chain_level > comp.food_chain_level:
                    # escaping
                    overall_velocity -= d_dist(hit_test_pos.coords - new_object_test_pos.coords) * 0.04

        self.step_vector += Point(overall_velocity)
        self.step_vector = self.step_vector.normalize()

        # the object will move towards its own step_vector
        return self.step_vector * self.speed, item_to_delete

    def rotateDirection(self):
        """
        change this environment object's orientation from v1 to v2.
        """
        v1 = self.orientation
        v2 = self.step_vector
        rotate_axis = v1.cross3d(v2)
        rotate_angle = v1.angleWith(v2)
        rotate_q = Quaternion.axisAngleToQuaternion(rotate_axis, rotate_angle)
        self.setPostRotation(rotate_q.toMatrix())


def unit_v(vector: np.ndarray, tol: float = 1E-6) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0 or norm < abs(norm - 1.0) <= tol:
        return vector
    else:
        return vector / norm


def d_lower_bound(n: float, log_n: float, x: np.ndarray) -> np.ndarray:
    # compute the lower bound gradient descent function
    # n: the number of exponent
    # log_n: log(n), precomputed for reduced computation
    # x: the input vector
    # y = np.pow(n, -x)
    return -log_n * (n ** -x)


def d_upper_bound(n: float, log_n: float, x: np.ndarray) -> np.ndarray:
    # y = np.pow(n, x)
    return log_n * (n ** x)


def d_gravity(a: float, b: float, x: np.ndarray) -> np.ndarray:
    # potential functions for mimic gravity boids.
    # df(x) = - a / x + b
    # b: limit point
    # a / b should be the place you want to cross the 0
    sign_x = np.sign(x)
    result = b - a / np.abs(x)
    result *= sign_x
    return result


def d_dist(x: np.ndarray) -> np.ndarray:
    # y = 1 / np.exp(x ** 2)
    return -2 * x * np.exp(-x ** 2)
