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
