"""
Defines Buff class to store canvas data. For a buff with size Width x Height, each entry will store a pixel color.
Each pixel color will be represented in (R, G, B) format, where R, G, B are unsigned char in range [0, 255].
This Buff class has a method to export all data to byte string to feed into graphic card.

First version Created on 09/27/2018

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

import numpy as np
from typing import Union

from Point import Point
from ColorType import ColorType


class Buff:
    """
    Buff class to store canvas color information
    """
    buff = None
    buffPointArray = None
    size = None
    width = None
    height = None
    background_color = None

    def __init__(self, width=0, height=0, color=None):
        """
        Use Width and Height to define a buff which has default black color at all entry.
        This default color can be replaced by setting a color as input argument.
        
        :param width: the buff width
        :type width: int
        :param height: the buff height
        :type height: int
        :param color: the default color you want to set the buff to
        :type color: ColorType
        :rtype: None
        """
        # Create a new Buff
        # Some Assertions to check input
        if (not isinstance(width, int)) or (not isinstance(height, int)):
            raise TypeError("width and height used to create Buff must be integer")
        if width < 0 or height < 0:
            raise TypeError("width and height of buff should be larger than 0")
        if width == 0:
            # If window is too small width might set to 0. To avoid number be divided by 0
            width = 1
        if height == 0:
            # If window is too small height might set to 0. To avoid number be divided by 0
            height = 1

        self.width = width
        self.height = height
        self.size = (width, height)
        self.buff = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        if isinstance(color, ColorType):
            self.background_color = ColorType(*color.getRGB())
            self.clear()
        else:
            self.background_color = ColorType(0, 0, 0)
            self.clear()

    def __repr__(self):
        return str(self.buff)

    def clear(self):
        """
        Clear buff to background color

        :rtype: None
        """
        r, g, b = self.background_color.getRGB_8bit()
        self.buff[:, :, 0] = r
        self.buff[:, :, 1] = g
        self.buff[:, :, 2] = b

    def resize(self, width: int, height: int):
        """
        Resize current buff to new size, data in buff will be kept as much as possible

        :param width: the buff width
        :type width: int
        :param height: the buff height
        :type height: int
        """
        w_min = min(self.width, width)
        h_min = min(self.height, height)

        # keep as much common pixels as possible, clip pixels outside canvas
        tempbuff = self.buff
        newbuff = np.zeros((width, height, 3), dtype=np.uint8)
        newbuff[:w_min, :h_min, :] = tempbuff[:w_min, :h_min, :]

        self.buff = newbuff
        self.size = (width, height)
        self.width = width
        self.height = height

    def setBackground(self, color: ColorType) -> None:
        """
        set background color for buff

        :param color: The background color you want to set to
        :type color: ColorType
        :rtype: None
        """
        if not isinstance(color, ColorType):
            raise TypeError("setBackground only accept color in ColorType")
        self.background_color = color.copy()

    def setPoint(self, point: Point) -> bool:
        """
        Do the same thing as setPixel, more convenient to pass all arguments by Point

        :param point: the point to set on buff
        :type point: Point
        :rtype: bool
        """
        return self.setPixel(*point.coords, *point.color.getRGB_8bit())

    def setPixel(self, x: int, y: int, r: int, g: int, b: int) -> bool:
        """
        Ignore out of Bound points and return False if point cannot be set on buff

        :param x: coordinate x value
        :type x: int
        :param y: coordinate y value
        :type y: int
        :param r: point's red value in [0, 255]
        :type r: int
        :param g: point's green value in [0, 255]
        :type g: int
        :param b: point's blue value in [0, 255]
        :type b: int
        :rtype: bool
        """
        if (x < 0) or (x >= self.width) or (y < 0) or (y >= self.height):
            # Out of Bound, ignore this point and return False
            return False
        self.buff[x, y, 0] = r
        self.buff[x, y, 1] = g
        self.buff[x, y, 2] = b
        return True

    def getPoint(self, x: int, y: int) -> Union[bool, Point]:
        """
        Get pixel information and return result in Point format

        :param x: the x coordinate to query
        :type x: int
        :param y: the y coordinate to query
        :type y: int
        :rtype: Point
        """
        if (x < 0) or (x > self.width) or (y < 0) or (y > self.height):
            # Out of Bound, return False
            return False
        return Point(coords=(x, y), color=ColorType(*(self.getPixel(x, y) / 255)))

    def getPixel(self, x, y):
        """
        Get Pixel color in position

        :param x: queried x coordinate
        :type x: int
        :param y: queried y coordiante
        :type y: int
        :rtype: numpy.array[type=uint8]
        """
        return self.buff[x, y, :]

    def setStaticBuffArray(self, buffArray):
        """
        :param buffArray: a array to load into buff array
        :type buffArray: numpy.array(dtype=uint8)
        """
        self._setBuffArray(buffArray)
        self.generatePointArray()

    def generatePointArray(self):
        """
        use current buff to generate a Point array, which can speed up the point retrieval.
        This point array won't update with buff. If buff updated, then this function need to be called again
        This is only recommended to texture buff
        """
        self.buffPointArray = [[Point() for _ in range(self.height)] for _ in range(self.width)]
        for i in range(self.width):
            for j in range(self.height):
                self.buffPointArray[i][j].setCoords((i, j))
                self.buffPointArray[i][j].setColor(ColorType(*(self.getPixel(i, j) / 255)))

    def getPointFromPointArray(self, x: int, y: int) -> Point:
        """
        Retrieve point from Point array. If Point array not prepared, then generatePointArray will be called.
        This is used to speed up texture buff query. Remember to call generatePointArray if buff changed.

        :param x: Query point x coordinate
        :type x: int
        :param y: Query point y coordinate
        :type y: int
        :rtype: Point
        """
        if self.buffPointArray is None:
            self.generatePointArray()
        return self.buffPointArray[x][y]

    def _setBuffArray(self, buffarray):
        """
        In class usage only
        """
        if not isinstance(buffarray, np.ndarray):
            raise TypeError("buffarray can be ndarray only")
        if self.width * self.height * 3 != buffarray.size:
            raise TypeError("You are copying buffarray with incorrect shape to this buff")
        self.buff = buffarray.reshape((self.width, self.height, 3)).copy()

    def getBytes(self):
        """
        Turn buff to bytes, which is a copy of raw data memory content in C-order, to feed into graphic card.

        :rtype: bytes
        """
        # flip width and height to generate bytes correctly
        return np.transpose(self.buff, (1, 0, 2)).tobytes()

    def copy(self):
        """
        A deep copy of current buff object

        :rtype: Buff
        """
        newBuff = Buff(self.width, self.height, self.background_color)
        newBuff._setBuffArray(self.buff)
        return newBuff


if __name__ == "__main__":
    a = Buff(100, 100)
    a.setPixel(5, 5, 255, 255, 255)

    p1 = a.getPoint(5, 5)
    print(p1)
    p1.setCoords((6, 4))
    a.setPoint(p1)
    p2 = a.getPoint(6, 5)
    print(p2)
    p_default = a.getPoint(50, 50)
    print(p_default)

    b = Buff(5, 5, ColorType(0.3, 0., 0.4))
    print(b.getBytes())
    print(b.getPoint(2, 2))
    print(b.getPoint(50, 50))

    c = b
    d = b.copy()
    print("c (reference of b): ", c.getBytes())
    print("d (copy of b)     :", d.getBytes())
    b.setBackground(ColorType(0.1, 0.2, 0.3))
    b.clear()
    b.setPixel(2, 2, 2, 0, 0)
    print("change b's background and set pixel at (2, 2)")
    print("c (reference of b): ", c.getBytes())
    print("d (copy of b)     :", d.getBytes())

    e = Buff(3, 3, ColorType(0, 0, 0))
    e.setPixel(0, 0, 1, 1, 1)
    e.setPixel(0, 1, 2, 2, 2)
    e.setPixel(0, 2, 3, 3, 3)
    e.setPixel(1, 0, 4, 4, 4)
    e.setPixel(1, 1, 5, 5, 5)
    print(e)
    print(e.getBytes())
    e.resize(2, 4)
    print(e)
    print(e.getBytes())
    e.resize(5, 3)
    print(e)
    print(e.getBytes())
    e.resize(6, 6)
    print(e)
    print(e.getBytes())
    e.resize(2, 2)
    print(e)
    print(e.getBytes())
