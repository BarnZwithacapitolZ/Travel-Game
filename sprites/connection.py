import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math

class Connection:
    def __init__(self, game, connectionType, fromNode, toNode, direction):
        self.game = game
        self.connectionType = connectionType
        self.fromNode = fromNode
        self.toNode = toNode
        self.direction = direction #0 forwards, 1 backwards
        self.sideColor = BLACK

        self.setColor()
        self.setLength()


    def setColor(self):
        if self.connectionType == 1 or self.connectionType == "layer 1":
            self.color = RED
        elif self.connectionType == 2 or self.connectionType == "layer 2":
            self.color = GREY
        elif self.connectionType == 3 or self.connectionType == "layer 3":
            self.color = GREEN


    def setLength(self):
        if self.fromNode is None or self.toNode is None:
            return

        self.length = ((self.fromNode.pos - self.fromNode.offset) - (self.toNode.pos - self.toNode.offset))
        self.distance = self.length.length()
        

    def setFromNode(self, fromNode):
        self.fromNode = fromNode


    def setToNode(self, toNode):
        self.toNode = toNode

    
    def getColor(self):
        return self.color


    def getSideColor(self):
        return self.sideColor


    def getFrom(self):
        return self.fromNode


    def getTo(self):
        return self.toNode


    def getLength(self):
        return self.length

    def getDistance(self):
        return self.distance


    def getType(self):
        return self.connectionType


    def getDirection(self):
        return self.direction
