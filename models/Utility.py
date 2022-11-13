from typing import Union, List, Tuple

import numpy as np

from Component import Component
from GLProgram import GLProgram
from Shapes import *
import ColorType as Ct


# define all the colors
CodHeadColor = Ct.ColorType(155 / 255, 140 / 255, 114 / 255)
CodBodyColor = Ct.ColorType(129 / 255, 104 / 255, 84 / 255)
CodFin1Color = Ct.ColorType(84 / 255, 72 / 255, 53 / 255)
CodFin2Color = Ct.ColorType(165 / 255, 147 / 255, 120 / 255)
CodTail1Color = Ct.ColorType(142 / 255, 126 / 255, 106 / 255)
CodTail2Color = Ct.ColorType(165 / 255, 147 / 255, 120 / 255)
SalmonHeadColor = Ct.ColorType(85 / 255, 111 / 255, 81 / 255)
SalmonEyeColor = Ct.ColorType(39 / 255, 66 / 255, 42 / 255)
SalmonPupilColor = Ct.ColorType(27 / 255, 33 / 255, 28 / 255)
SalmonBodyColor = Ct.ColorType(128 / 255, 51 / 255, 49 / 255)
SalmonFin1Color = Ct.ColorType(69 / 255, 58 / 255, 29 / 255)
SalmonFin2Color = Ct.ColorType(151 / 255, 159 / 255, 63 / 255)
SalmonTail1Color = Ct.ColorType(147 / 255, 116 / 255, 78 / 255)
SalmonTail2Color = Ct.ColorType(125 / 255, 90 / 255, 55 / 255)


def createFin(nums: int, shaderProg: GLProgram,
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
