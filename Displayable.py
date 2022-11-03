'''
Created on 20181021

@author: Zezhou Sun
@description: Define displayable interface at here. Object inherit from Displayable can be displayed on screen use draw method. And shape of it should be defined at initialize method. 
'''


class Displayable:
    """
    Interface for displayable object
    """
    callListHandle = 0
    parent = None  # parent class, used for SetCurrent

    def __init__(self):
        pass

    def draw(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError
