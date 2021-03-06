import pygame
from pygame.locals import *
from config import *
from clickManager import *
from transitionFunctions import *


# hover over an object and set it to a specified color
def hoverColor(obj, menu, event, color = None):
    if color is not None:
        obj.setColor(color)


# hover over the object and add a hover animation
def hoverOver(obj, menu, event, speed = 1, x = 110, color = Color("white")):
    if hoverOverAnimation not in obj.getAnimations():
        obj.addAnimation(hoverOverAnimation, 'onMouseOver', speed = speed, x = x)
    obj.setColor(color)


# remove the hover over animation on mouse out
def hoverOut(obj, menu, event, speed = 1, x = 100, color = BLACK):
    if hoverOverAnimation in obj.getAnimations():
        obj.removeAnimation(hoverOverAnimation)
    obj.addAnimation(hoverOutAnimation, 'onMouseOut', speed = speed, x = x)
    obj.setColor(color)


# close and clear the menu
def clearMenu(obj, menu):
    menu.close()
    menu.main()