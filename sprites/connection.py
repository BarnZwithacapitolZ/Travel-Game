import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math
from enum import Enum
vec = pygame.math.Vector2

class Connection:
    class Direction(Enum):
        FORWARDS = 0
        BACKWARDS = 1

    def __init__(self, spriteRenderer, connectionType, fromNode, toNode, direction):
        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.connectionType = connectionType
        self.fromNode = fromNode
        self.toNode = toNode
        self.direction = direction #0 forwards, 1 backwards
        self.sideColor = TRUEBLACK

        self.setColor()
        self.setLength()

        self.mouseOver = False


    #### Getters ####
    
    # Return the colour of the connection
    def getColor(self):
        return self.color


    # Return the side colour of the connection
    def getSideColor(self):
        return self.sideColor


    # Return the node which the connection connects from
    def getFrom(self):
        return self.fromNode


    # Return the node which the connection connects to
    def getTo(self):
        return self.toNode


    # Return the length (as a vector) from point A to B
    def getLength(self):
        return self.length


    # Return the distance (as a float) from point A to B
    def getDistance(self):
        return self.distance


    # Return the type of connection
    def getType(self):
        return self.connectionType


    # Return the direction of the connection
    def getDirection(self):
        return self.direction


    def getConnectionType(self):
        return self.connectionType


    #### Setters ####

    # Set the colour of the connection depending on the type 
    def setColor(self):
        if self.connectionType == 1 or self.connectionType == "layer 1":
            self.color = RED
        elif self.connectionType == 2 or self.connectionType == "layer 2":
            self.color = GREY
        elif self.connectionType == 3 or self.connectionType == "layer 3":
            self.color = GREEN


    # Set the length and distance of the connection from point A (from) to B (to)
    def setLength(self):
        if self.fromNode is None or self.toNode is None:
            return

        self.length = ((self.fromNode.pos - self.fromNode.offset) - (self.toNode.pos - self.toNode.offset))
        self.distance = self.length.length()
        

    # Set point A (from)
    def setFromNode(self, fromNode):
        self.fromNode = fromNode


    # Set point B (to)
    def setToNode(self, toNode):
        self.toNode = toNode


    def update(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]

        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
        buffer = 1
        d1 = ((vec(mx, my) - vec(10,10) * scale) - (self.fromNode.pos - self.fromNode.offset) * scale).length()
        d2 = ((vec(mx, my) - vec(10, 10) * scale) - (self.toNode.pos - self.toNode.offset) * scale).length()

        if d1 + d2 >= self.distance * scale - buffer and d1 + d2 <= self.distance * scale + buffer and self.game.clickManager.getClicked():
            self.game.mapEditor.getClickManager().deleteConnection(self)
            self.game.clickManager.setClicked(False)

        elif d1 + d2 >= self.distance * scale - buffer and d1 + d2 <= self.distance * scale + buffer and not self.mouseOver:
            self.color = YELLOW
            self.mouseOver = True
        
        elif not (d1 + d2 >= self.distance * scale - buffer and d1 + d2 <= self.distance * scale + buffer) and self.mouseOver:
            self.mouseOver = False
            self.setColor()


