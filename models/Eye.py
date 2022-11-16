from Component import Component
from CS680PA3 import CS680PA3
from GLProgram import GLProgram
from Point import Point
import typing
import ColorType as Ct
from Shapes import Sphere


class Eye(Component):
    def __init__(self,
                 parent: Component,
                 position: Point,
                 shaderProg: GLProgram,
                 scale: typing.Optional[typing.Iterator] = None,
                 eyeColor: Ct.ColorType = Ct.WHITE,
                 pupilColor: Ct.ColorType = Ct.BLACK):
        super().__init__(position)

        eye_radius = 1
        eye_thickness = eye_radius * 0.75
        # width, height, depth
        eye_size = [eye_radius, eye_radius, eye_thickness]
        eye = Sphere(position, shaderProg, eye_size, eyeColor, lowPoly=False)

        ball_radius = eye_radius * 0.5
        ball_thickness = eye_thickness / 3
        ball_size = [ball_radius, ball_radius, ball_thickness]
        pupil = Sphere(Point((0, 0, eye_thickness - ball_thickness)), shaderProg, ball_size, pupilColor, lowPoly=False)

        pupil.setRotateExtent(pupil.uAxis, -30, 54)
        pupil.setRotateExtent(pupil.vAxis, 0, 0)
        pupil.setRotateExtent(pupil.wAxis, -44, 47)

        self.addChild(eye)
        eye.addChild(pupil)

        if scale is not None:
            self.setDefaultScale(scale)
